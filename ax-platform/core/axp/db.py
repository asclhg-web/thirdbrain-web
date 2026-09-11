"""저장 계층 (M0) — demo: SQLite / prod: PostgreSQL(psycopg) 이중 백엔드.

선택: 환경변수 AXP_DB=sqlite(기본)|postgres, 접속은 AXP_PG_DSN.
코어 모듈은 SQLite 문법으로 쓰고, postgres 백엔드가 호환 변환을 맡는다
(placeholder ?→%s, AUTOINCREMENT→BIGSERIAL, INSERT OR REPLACE/IGNORE→
ON CONFLICT, PRAGMA foreign_keys→session_replication_role).

인터페이스 4원칙의 '개방 포맷'을 지킨다: 전 테이블은 표준 SQL, 교환은
SQL 테이블·Parquet·JSON. 특정 모듈이 죽어도 데이터는 읽힌다.
"""
from __future__ import annotations

import os
import re
import sqlite3
from contextlib import contextmanager
from typing import Any, Iterable

import pandas as pd

from . import config

BACKEND = os.environ.get("AXP_DB", "sqlite")
PG_DSN = os.environ.get(
    "AXP_PG_DSN", "host=127.0.0.1 port=5432 user=axp password=axp dbname=axp")

# ── PostgreSQL 호환 변환 ─────────────────────────────────────────────

_RE_OR_IGNORE = re.compile(r"INSERT\s+OR\s+IGNORE\s+INTO\s+(\w+)", re.I)
_RE_OR_REPLACE = re.compile(r"INSERT\s+OR\s+REPLACE\s+INTO\s+(\w+)\s*(\(([^)]*)\))?", re.I)
_RE_PRAGMA_FK = re.compile(r"^\s*PRAGMA\s+foreign_keys\s*=\s*(ON|OFF)\s*;?\s*$", re.I)
_RE_PRAGMA = re.compile(r"^\s*PRAGMA\b.*$", re.I | re.M)

_pk_cache: dict[str, list[str]] = {}
_col_cache: dict[str, list[str]] = {}


def _pg_meta(raw_con, table: str) -> tuple[list[str], list[str]]:
    """(pk_cols, all_cols) — 카탈로그에서 조회·캐시(스키마별)."""
    with raw_con.cursor() as _c:
        _c.execute("SELECT current_schema()")
        _schema = _c.fetchone()[0]
    t = f"{_schema}.{table.lower()}"
    if t not in _col_cache:
        with raw_con.cursor() as cur:
            cur.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema=current_schema() AND table_name=%s ORDER BY ordinal_position",
                (table.lower(),))
            _col_cache[t] = [r[0] for r in cur.fetchall()]
            cur.execute(
                "SELECT a.attname FROM pg_index i "
                "JOIN pg_attribute a ON a.attrelid=i.indrelid AND a.attnum=ANY(i.indkey) "
                "WHERE i.indrelid=%s::regclass AND i.indisprimary", (table.lower(),))
            pk = [r[0] for r in cur.fetchall()]
            if not pk:  # PK가 없으면 첫 UNIQUE 인덱스 사용 (SQLite OR REPLACE와 동등)
                cur.execute(
                    "SELECT a.attname FROM pg_index i "
                    "JOIN pg_attribute a ON a.attrelid=i.indrelid AND a.attnum=ANY(i.indkey) "
                    "WHERE i.indrelid=%s::regclass AND i.indisunique "
                    "ORDER BY i.indexrelid LIMIT 8", (table.lower(),))
                pk = [r[0] for r in cur.fetchall()]
            _pk_cache[t] = pk
    return _pk_cache[t], _col_cache[t]


def _pg_sql(sql: str, raw_con=None) -> str | None:
    """SQLite 관용구 → PostgreSQL. None이면 실행 생략(no-op PRAGMA)."""
    m = _RE_PRAGMA_FK.match(sql)
    if m:
        mode = "origin" if m.group(1).upper() == "ON" else "replica"
        return f"SET session_replication_role = {mode}"
    if _RE_PRAGMA.match(sql.strip()):
        return None
    sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "BIGSERIAL PRIMARY KEY")

    m = _RE_OR_REPLACE.search(sql)
    if m:
        table = m.group(1)
        cols = [c.strip() for c in (m.group(3) or "").split(",") if c.strip()]
        if raw_con is not None:
            pk, allc = _pg_meta(raw_con, table)
            if not cols:
                cols = allc
            upd = [c for c in cols if c.lower() not in {p.lower() for p in pk}]
            conflict = (f" ON CONFLICT ({', '.join(pk)}) DO UPDATE SET "
                        + ", ".join(f"{c}=EXCLUDED.{c}" for c in upd)
                        ) if pk and upd else (
                        f" ON CONFLICT ({', '.join(pk)}) DO NOTHING" if pk else "")
            head = f"INSERT INTO {table}" + (f" ({', '.join(cols)})" if m.group(2) or not m.group(2) else "")
            head = f"INSERT INTO {table} ({', '.join(cols)})"
            sql = sql[:m.start()] + head + sql[m.end():]
            sql = sql.rstrip().rstrip(";") + conflict
    m2 = _RE_OR_IGNORE.search(sql)
    if m2:
        sql = _RE_OR_IGNORE.sub(lambda mm: f"INSERT INTO {mm.group(1)}", sql)
        sql = sql.rstrip().rstrip(";") + " ON CONFLICT DO NOTHING"

    sql = re.sub(r"%(?![s%(])", "%%", sql)   # 리터럴 %만 이스케이프(%s·%(name)s 보존)
    # SQLite JSON1 → PostgreSQL jsonb: json_extract(col,'$.a')→(col::jsonb->>'a'),
    # 중첩 '$.a.b'는 #>> '{a,b}'
    def _jx(m):
        col, path = m.group(1), m.group(2)
        keys = path.lstrip("$.").split(".")
        if len(keys) == 1:
            return f"({col}::jsonb ->> '{keys[0]}')"
        return f"({col}::jsonb #>> '{{{','.join(keys)}}}')"
    sql = re.sub(r"json_extract\(\s*([\w.]+)\s*,\s*'(\$\.[\w.]+)'\s*\)", _jx, sql)
    sql = sql.replace("?", "%s")
    # sqlite 명명 파라미터(:name) → psycopg %(name)s  ('::' 캐스트는 제외)
    sql = re.sub(r"(?<![:\w']):([a-zA-Z_]\w*)", r"%(\1)s", sql)
    return sql


def _pg_script(sql: str) -> str:
    sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "BIGSERIAL PRIMARY KEY")
    sql = _RE_PRAGMA.sub("", sql)
    return sql


_RE_IS_INSERT = re.compile(r"^\s*INSERT\b", re.I)


class _Row(dict):
    """dict + 위치 인덱스 접근 — sqlite3.Row와 양쪽 호환."""

    def __init__(self, names, values):
        super().__init__(zip(names, values))
        self._values = list(values)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return super().__getitem__(key)


def _axrow(cursor):
    names = [d.name for d in cursor.description] if cursor.description else []

    def make(values):
        return _Row(names, values)

    return make


class _PgCursor:
    """INSERT에 RETURNING을 부여해 sqlite의 lastrowid 의미를 재현."""

    def __init__(self, raw_cur, first_row=None):
        self._cur = raw_cur
        self._first = first_row

    @property
    def lastrowid(self):
        return None if self._first is None else self._first[0]

    @property
    def description(self):
        return self._cur.description

    def fetchall(self):
        return self._cur.fetchall()

    def fetchone(self):
        return self._cur.fetchone()


class _PgConn:
    """psycopg 연결 래퍼 — 모듈이 sqlite 문법으로 execute해도 동작."""

    def __init__(self, raw):
        self.raw = raw

    def execute(self, sql: str, params: Iterable[Any] = ()):  # noqa: A003
        t = _pg_sql(sql, self.raw)
        if t is None:
            return _NullCursor()
        pv = params if isinstance(params, dict) else (tuple(params) if params else None)
        if _RE_IS_INSERT.match(t) and "RETURNING" not in t.upper():
            from psycopg.rows import tuple_row
            with self.raw.cursor(row_factory=tuple_row) as cur:
                cur.execute(t + " RETURNING *", pv)
                row = cur.fetchone()
            return _PgCursor(cur, row)
        return _PgCursor(self.raw.execute(t, pv))

    def executemany(self, sql: str, rows: list[tuple]):
        t = _pg_sql(sql, self.raw)
        if t is None or not rows:
            return
        with self.raw.cursor() as cur:
            cur.executemany(t, rows)

    def commit(self):
        self.raw.commit()

    def rollback(self):
        self.raw.rollback()

    def close(self):
        self.raw.close()

    def cursor(self, *a, **k):
        return self.raw.cursor(*a, **k)


class _NullCursor:
    def fetchall(self):
        return []

    def fetchone(self):
        return None


def _connect():
    if BACKEND == "postgres":
        import hashlib
        import psycopg
        raw = psycopg.connect(PG_DSN, row_factory=_axrow)
        schema = "ax_" + hashlib.md5(str(config.DATA).encode()).hexdigest()[:12]
        raw.execute(f'CREATE SCHEMA IF NOT EXISTS {schema}')
        raw.execute(f'SET search_path = {schema}')
        raw.commit()
        return _PgConn(raw)
    config.ensure_dirs()
    con = sqlite3.connect(config.DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA foreign_keys=ON")
    return con


@contextmanager
def conn():
    con = _connect()
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def execute(sql: str, params: Iterable[Any] = ()) -> None:
    with conn() as c:
        c.execute(sql, params if isinstance(params, dict) else tuple(params))


def executemany(sql: str, rows: list[tuple]) -> None:
    if not rows:
        return
    with conn() as c:
        c.executemany(sql, rows)


def executescript(sql: str) -> None:
    if BACKEND == "postgres":
        with conn() as c:
            c.raw.execute(_pg_script(sql))
        return
    with conn() as c:
        c.executescript(sql)


def query(sql: str, params: Iterable[Any] = ()) -> list[dict]:
    with conn() as c:
        cur = c.execute(sql, params if isinstance(params, dict) else tuple(params))
        return [dict(r) for r in cur.fetchall()]


def one(sql: str, params: Iterable[Any] = ()) -> dict | None:
    rows = query(sql, params)
    return rows[0] if rows else None


def scalar(sql: str, params: Iterable[Any] = ()) -> Any:
    row = one(sql, params)
    return None if row is None else next(iter(row.values()))


def df(sql: str, params: Iterable[Any] = ()) -> pd.DataFrame:
    if BACKEND == "postgres":
        with conn() as c:
            cur = c.execute(sql, tuple(params))
            rows = cur.fetchall()
            cols = [d.name for d in cur.description] if cur.description else []
        return pd.DataFrame(rows, columns=cols or None)
    with conn() as c:
        return pd.read_sql_query(sql, c, params=tuple(params))


def write_df(frame: pd.DataFrame, table: str, if_exists: str = "append") -> int:
    if BACKEND == "postgres":
        with conn() as c:
            if if_exists == "replace":
                c.raw.execute(f"DELETE FROM {table}")
            cols = list(frame.columns)
            with c.raw.cursor() as cur:
                with cur.copy(
                    f"COPY {table} ({', '.join(cols)}) FROM STDIN") as cp:
                    for row in frame.itertuples(index=False, name=None):
                        cp.write_row(row)
        return len(frame)
    with conn() as c:
        frame.to_sql(table, c, if_exists=if_exists, index=False)
    return len(frame)


def load_frame(c, frame: pd.DataFrame, table: str) -> int:
    """열려 있는 conn() 연결 위에 DataFrame 적재 — 백엔드 공통."""
    if BACKEND == "postgres":
        cols = list(frame.columns)
        with c.raw.cursor() as cur:
            with cur.copy(f"COPY {table} ({', '.join(cols)}) FROM STDIN") as cp:
                for row in frame.itertuples(index=False, name=None):
                    cp.write_row(row)
        return len(frame)
    frame.to_sql(table, c, if_exists="append", index=False)
    return len(frame)


def table_exists(name: str) -> bool:
    if BACKEND == "postgres":
        return scalar("SELECT to_regclass(%s) IS NOT NULL", (name,))
    return scalar(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ) > 0
