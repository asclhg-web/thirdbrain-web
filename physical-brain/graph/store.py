"""그래프 저장소 — SQLite 구현 (Neo4j 전환 대비 동일 인터페이스).

노드: (id, type, props JSON, archived)  /  엣지: (src, rel, dst, props JSON)
지식 수정의 원본은 볼트(마크다운)이며 이 저장소는 그 거울이다.
"""
import json
import os
import sqlite3
import threading
from datetime import datetime, timedelta

from graph.schema import NODE_TYPES, validate_edge

_LOCK = threading.Lock()
_CONN = None


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
        CREATE TABLE IF NOT EXISTS tasks(
          id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, person TEXT, med TEXT,
          time TEXT, condition TEXT, caution TEXT,
          status TEXT DEFAULT 'pending', announced_at TEXT, reminded INTEGER DEFAULT 0,
          UNIQUE(date, person, med, time));
        """
    )
    conn.commit()


# ---------- 노드/엣지 ----------

def upsert_node(node_id: str, ntype: str, props: dict):
    assert ntype in NODE_TYPES, f"unknown node type {ntype}"
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
    if s and d and not validate_edge(rel, s["type"], d["type"]):
        raise ValueError(f"schema violation: ({s['type']})-[{rel}]->({d['type']})")
    conn.execute(
        "INSERT OR REPLACE INTO edges(src,rel,dst,props) VALUES(?,?,?,?)",
        (src, rel, dst, json.dumps(props or {}, ensure_ascii=False)),
    )
    conn.commit()


def get_node(node_id: str) -> dict | None:
    row = get_conn().execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
    return _node(row) if row else None


def archive_node(node_id: str):
    conn = get_conn()
    conn.execute("UPDATE nodes SET archived=1 WHERE id=?", (node_id,))
    conn.commit()


def nodes_by_type(ntype: str, include_archived=False) -> list[dict]:
    q = "SELECT * FROM nodes WHERE type=?" + ("" if include_archived else " AND archived=0")
    return [_node(r) for r in get_conn().execute(q, (ntype,)).fetchall()]


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


def _node(row) -> dict:
    return {"id": row["id"], "type": row["type"], "archived": bool(row["archived"]),
            **{"props": json.loads(row["props"])}}


# ---------- 도메인 질의 (사서·안전망이 사용하는 'Cypher 템플릿'의 SQLite 판) ----------

def person_id(name: str) -> str:
    return f"person:{name}"


def measurements(person: str, mtype: str, days: int = 7, now: datetime | None = None) -> list[dict]:
    now = now or datetime.now()
    since = (now - timedelta(days=days)).isoformat()
    rows = get_conn().execute(
        "SELECT n.props FROM nodes n JOIN edges e ON e.dst=n.id AND e.rel='MEASURED' "
        "WHERE e.src=? AND n.type='Measurement' AND n.archived=0",
        (person_id(person),),
    ).fetchall()
    out = [json.loads(r["props"]) for r in rows]
    out = [m for m in out if m.get("type") == mtype and m.get("measured_at", "") >= since
           and m.get("measured_at", "") <= now.isoformat()]
    return sorted(out, key=lambda m: m["measured_at"])


def activities(person: str, kind: str, days: int = 7, now: datetime | None = None) -> list[dict]:
    now = now or datetime.now()
    since = (now - timedelta(days=days)).isoformat()
    rows = get_conn().execute(
        "SELECT n.props FROM nodes n JOIN edges e ON e.dst=n.id AND e.rel='PERFORMED' "
        "WHERE e.src=? AND n.type='Activity' AND n.archived=0",
        (person_id(person),),
    ).fetchall()
    out = [json.loads(r["props"]) for r in rows]
    return sorted([a for a in out if a.get("kind") == kind and since <= a.get("at", "") <= now.isoformat()],
                  key=lambda a: a["at"])


def regimens_for(person: str) -> list[dict]:
    """사람 -[TAKES]-> 약 -[HAS_RULE]-> 규칙 전개."""
    out = []
    for _, med in neighbors(person_id(person), "TAKES"):
        for _, rule in neighbors(med["id"], "HAS_RULE"):
            out.append({"person": person, "med": med["props"].get("name", med["id"]),
                        "med_id": med["id"], **rule["props"]})
    return sorted(out, key=lambda r: r.get("time", ""))


def events(person: str, days: int = 7, kind: str | None = None, now: datetime | None = None) -> list[dict]:
    now = now or datetime.now()
    since = (now - timedelta(days=days)).isoformat()
    rows = get_conn().execute(
        "SELECT n.props FROM nodes n JOIN edges e ON e.dst=n.id AND e.rel='OCCURRED' "
        "WHERE e.src=? AND n.type='Event' AND n.archived=0",
        (person_id(person),),
    ).fetchall()
    out = [json.loads(r["props"]) for r in rows]
    out = [ev for ev in out if since <= ev.get("at", "") <= now.isoformat()
           and (kind is None or ev.get("kind") == kind)]
    return sorted(out, key=lambda ev: ev["at"])
