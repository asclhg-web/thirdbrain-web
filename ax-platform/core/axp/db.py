"""저장 계층 (M0) — demo: SQLite / prod: PostgreSQL(psycopg) 어댑터.

인터페이스 4원칙의 '개방 포맷'을 지킨다: 전 테이블은 표준 SQL, 교환은
SQL 테이블·Parquet·JSON. 특정 모듈이 죽어도 데이터는 읽힌다.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Any, Iterable

import pandas as pd

from . import config


def _connect() -> sqlite3.Connection:
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
        c.execute(sql, tuple(params))


def executemany(sql: str, rows: list[tuple]) -> None:
    if not rows:
        return
    with conn() as c:
        c.executemany(sql, rows)


def executescript(sql: str) -> None:
    with conn() as c:
        c.executescript(sql)


def query(sql: str, params: Iterable[Any] = ()) -> list[dict]:
    with conn() as c:
        cur = c.execute(sql, tuple(params))
        return [dict(r) for r in cur.fetchall()]


def one(sql: str, params: Iterable[Any] = ()) -> dict | None:
    rows = query(sql, params)
    return rows[0] if rows else None


def scalar(sql: str, params: Iterable[Any] = ()) -> Any:
    row = one(sql, params)
    return None if row is None else next(iter(row.values()))


def df(sql: str, params: Iterable[Any] = ()) -> pd.DataFrame:
    with conn() as c:
        return pd.read_sql_query(sql, c, params=tuple(params))


def write_df(frame: pd.DataFrame, table: str, if_exists: str = "append") -> int:
    with conn() as c:
        frame.to_sql(table, c, if_exists=if_exists, index=False)
    return len(frame)


def table_exists(name: str) -> bool:
    return scalar(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ) > 0
