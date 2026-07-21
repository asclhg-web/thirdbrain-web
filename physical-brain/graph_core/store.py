"""코어 저장소 (G01) — 도메인을 모르는 노드/엣지 SQLite 그래프.

- 검증은 registry(등록된 Frame들의 합집합)에 위임한다.
- 도메인 테이블(복약 tasks 등)은 팩이 register_ddl()로 주입한다.
- Neo4j 승격 대비 동일 인터페이스 (GRAPH_BACKEND — 기존 설계 유지).
"""
import json
import os
import sqlite3
import threading
from datetime import datetime

from graph_core import registry

_LOCK = threading.Lock()
_CONN = None
_EXTRA_DDL: list[str] = []


def register_ddl(sql: str) -> None:
    """도메인 팩의 부속 테이블 DDL 등록 (연결 초기화 시 함께 생성)."""
    if sql not in _EXTRA_DDL:
        _EXTRA_DDL.append(sql)


def db_path() -> str:
    return os.environ.get("PB_DB", os.path.join(os.path.dirname(__file__), "..", "data", "brain.db"))


def get_conn() -> sqlite3.Connection:
    global _CONN
    with _LOCK:
        if _CONN is None:
            path = db_path()
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            _CONN = sqlite3.connect(path, check_same_thread=False)
            _CONN.row_factory = sqlite3.Row
            init_tables(_CONN)
        return _CONN


def reset_conn():
    """테스트용: 연결 캐시 해제 (PB_DB 변경 반영)."""
    global _CONN
    with _LOCK:
        if _CONN is not None:
            _CONN.close()
            _CONN = None


def init_tables(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS nodes(
          id TEXT PRIMARY KEY, type TEXT NOT NULL, props TEXT NOT NULL DEFAULT '{}',
          archived INTEGER NOT NULL DEFAULT 0, updated_at TEXT);
        CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);
        CREATE TABLE IF NOT EXISTS edges(
          src TEXT NOT NULL, rel TEXT NOT NULL, dst TEXT NOT NULL,
          props TEXT NOT NULL DEFAULT '{}',
          PRIMARY KEY (src, rel, dst));
        CREATE INDEX IF NOT EXISTS idx_edges_dst ON edges(dst);
        CREATE TABLE IF NOT EXISTS sync_state(path TEXT PRIMARY KEY, hash TEXT);
        """
    )
    for ddl in _EXTRA_DDL:
        conn.executescript(ddl)
    conn.commit()


def upsert_node(node_id: str, ntype: str, props: dict):
    assert ntype in registry.node_types(), f"unknown node type {ntype}"
    conn = get_conn()
    conn.execute(
        "INSERT INTO nodes(id,type,props,archived,updated_at) VALUES(?,?,?,0,?) "
        "ON CONFLICT(id) DO UPDATE SET type=excluded.type, props=excluded.props, "
        "archived=0, updated_at=excluded.updated_at",
        (node_id, ntype, json.dumps(props, ensure_ascii=False), datetime.now().isoformat()),
    )
    conn.commit()


def upsert_edge(src: str, rel: str, dst: str, props: dict | None = None):
    conn = get_conn()
    s, d = get_node(src), get_node(dst)
    if s and d and not registry.validate_edge(rel, s["type"], d["type"]):
        raise ValueError(f"schema violation: ({s['type']})-[{rel}]->({d['type']})")
    conn.execute(
        "INSERT OR REPLACE INTO edges(src,rel,dst,props) VALUES(?,?,?,?)",
        (src, rel, dst, json.dumps(props or {}, ensure_ascii=False)),
    )
    conn.commit()


def get_node(node_id: str) -> dict | None:
    row = get_conn().execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
    return node_dict(row) if row else None


def archive_node(node_id: str):
    conn = get_conn()
    conn.execute("UPDATE nodes SET archived=1 WHERE id=?", (node_id,))
    conn.commit()


def nodes_by_type(ntype: str, include_archived=False) -> list[dict]:
    q = "SELECT * FROM nodes WHERE type=?" + ("" if include_archived else " AND archived=0")
    return [node_dict(r) for r in get_conn().execute(q, (ntype,)).fetchall()]


def neighbors(node_id: str, rel: str | None = None, direction="out") -> list[tuple[str, dict]]:
    conn = get_conn()
    if direction == "out":
        q, col = "SELECT rel, dst AS other FROM edges WHERE src=?", "other"
    else:
        q, col = "SELECT rel, src AS other FROM edges WHERE dst=?", "other"
    rows = conn.execute(q, (node_id,)).fetchall()
    out = []
    for r in rows:
        if rel and r["rel"] != rel:
            continue
        n = get_node(r[col])
        if n and not n["archived"]:
            out.append((r["rel"], n))
    return out


def counts() -> dict:
    conn = get_conn()
    n = {r["type"]: r["c"] for r in conn.execute(
        "SELECT type, COUNT(*) c FROM nodes WHERE archived=0 GROUP BY type")}
    e = conn.execute("SELECT COUNT(*) c FROM edges").fetchone()["c"]
    return {"nodes": n, "edges": e}


def node_dict(row) -> dict:
    return {"id": row["id"], "type": row["type"], "archived": bool(row["archived"]),
            "props": json.loads(row["props"])}
