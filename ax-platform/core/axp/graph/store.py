"""그래프 저장소 — demo: SQLite 트리플 / prod: Neo4j 어댑터(동일 인터페이스).

노드: DefectEvent(허브)·Worker·Equipment·MaterialLot·SOP·Product·Rule·Vendor·MaintEvent
관계: FACT 계열(자동 적재) · CAUSAL_CANDIDATE(확신도) · RULE 계열(승격)
모든 노드는 원장 참조(ledger_ref)를 보존한다 — 근거 없는 노드는 없다.
"""
from __future__ import annotations

import json

from .. import common, db

NODE_LABELS = ["DefectEvent", "Worker", "Equipment", "MaterialLot", "SOP",
               "Product", "Vendor", "Rule", "MaintEvent"]
FACT_RELS = ["OCCURRED_ON", "WORKED_BY", "ON_EQUIPMENT", "USED_LOT", "PER_SOP",
             "OF_PRODUCT", "SUPPLIED_BY", "MAINTAINED"]

DDL = """
CREATE TABLE IF NOT EXISTS kg_nodes (
  node_id TEXT PRIMARY KEY,        -- 'Label:key'
  label TEXT NOT NULL,
  props TEXT NOT NULL DEFAULT '{}',
  ledger_ref TEXT DEFAULT ''       -- 원장 레코드 참조
);
CREATE TABLE IF NOT EXISTS kg_edges (
  edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
  src TEXT NOT NULL, rel TEXT NOT NULL, dst TEXT NOT NULL,
  props TEXT NOT NULL DEFAULT '{}',
  created_at TEXT,
  UNIQUE (src, rel, dst)
);
CREATE INDEX IF NOT EXISTS idx_edges_src ON kg_edges (src, rel);
CREATE INDEX IF NOT EXISTS idx_edges_dst ON kg_edges (dst, rel);
CREATE INDEX IF NOT EXISTS idx_nodes_label ON kg_nodes (label);
"""


def init() -> None:
    db.executescript(DDL)


def nid(label: str, key: str) -> str:
    return f"{label}:{key}"


def upsert_node(label: str, key: str, props: dict | None = None,
                ledger_ref: str = "") -> str:
    node_id = nid(label, key)
    db.execute(
        "INSERT INTO kg_nodes (node_id, label, props, ledger_ref) VALUES (?,?,?,?) "
        "ON CONFLICT(node_id) DO UPDATE SET props=excluded.props",
        (node_id, label, json.dumps(props or {}, ensure_ascii=False), ledger_ref))
    return node_id


def upsert_edge(src: str, rel: str, dst: str, props: dict | None = None) -> None:
    db.execute(
        "INSERT INTO kg_edges (src, rel, dst, props, created_at) VALUES (?,?,?,?,?) "
        "ON CONFLICT(src, rel, dst) DO UPDATE SET props=excluded.props",
        (src, rel, dst, json.dumps(props or {}, ensure_ascii=False), common.now_iso()))


def bulk_edges(rows: list[tuple[str, str, str, str]]) -> None:
    """rows: (src, rel, dst, props_json)"""
    ts = common.now_iso()
    db.executemany(
        "INSERT OR IGNORE INTO kg_edges (src, rel, dst, props, created_at) "
        "VALUES (?,?,?,?,?)", [(s, r, d, p, ts) for s, r, d, p in rows])


def node(node_id: str) -> dict | None:
    row = db.one("SELECT * FROM kg_nodes WHERE node_id=?", (node_id,))
    if row:
        row["props"] = json.loads(row["props"])
    return row


def neighbors(node_id: str, rel: str | None = None, direction: str = "out") -> list[dict]:
    if direction == "out":
        sql = "SELECT e.rel, e.dst AS other, e.props FROM kg_edges e WHERE e.src=?"
    else:
        sql = "SELECT e.rel, e.src AS other, e.props FROM kg_edges e WHERE e.dst=?"
    params: list = [node_id]
    if rel:
        sql += " AND e.rel=?"
        params.append(rel)
    rows = db.query(sql, params)
    for r in rows:
        r["props"] = json.loads(r["props"])
    return rows


def stats() -> dict:
    init()
    n = {r["label"]: r["c"] for r in db.query(
        "SELECT label, COUNT(*) c FROM kg_nodes GROUP BY label")}
    e = {r["rel"]: r["c"] for r in db.query(
        "SELECT rel, COUNT(*) c FROM kg_edges GROUP BY rel")}
    return {"nodes": n, "edges": e,
            "total_nodes": sum(n.values()), "total_edges": sum(e.values())}


def export_cypher(path: str) -> int:
    """prod 이관 — Neo4j Cypher 스크립트로 내보내기."""
    lines = ["// AX Platform 지식그래프 내보내기 — neo4j-shell/cypher-shell 실행용"]
    for r in db.query("SELECT * FROM kg_nodes"):
        props = json.loads(r["props"])
        props["ledger_ref"] = r["ledger_ref"]
        pj = json.dumps(props, ensure_ascii=False)
        lines.append(f"MERGE (n:{r['label']} {{id: {json.dumps(r['node_id'])}}}) SET n += {pj};")
    for r in db.query("SELECT * FROM kg_edges"):
        pj = r["props"]
        lines.append(
            f"MATCH (a {{id: {json.dumps(r['src'])}}}), (b {{id: {json.dumps(r['dst'])}}}) "
            f"MERGE (a)-[e:{r['rel']}]->(b) SET e += {pj};")
    from pathlib import Path
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    return len(lines) - 1
