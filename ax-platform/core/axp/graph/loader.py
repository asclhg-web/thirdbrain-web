"""M5-1 FACT 적재기 — 사실 테이블 → 그래프 (야간 배치·백필, 멱등).

DefectEvent가 허브: 각 불량 이벤트가 4M 노드로 방사한다.
원장 레코드 ID(defect_id·mo_ref)를 속성으로 보존 — 역추적의 사다리.
"""
from __future__ import annotations

import json

from .. import db
from . import store


def load_dimensions() -> dict[str, int]:
    store.init()
    counts = {}
    for label, sql, key, props_cols in [
        ("Worker", "SELECT worker_id AS k, worker_name AS name FROM dim_worker", "k", ["name"]),
        ("Equipment", "SELECT equipment_id AS k, line_id, equipment_type FROM dim_equipment",
         "k", ["line_id", "equipment_type"]),
        ("Product", "SELECT product_id AS k, product_name AS name FROM dim_product", "k", ["name"]),
        ("SOP", "SELECT sop_id AS k, sop_name AS name FROM dim_sop", "k", ["name"]),
        ("Vendor", "SELECT DISTINCT vendor_id AS k FROM dim_material_lot", "k", []),
        ("MaterialLot",
         "SELECT lot_id AS k, material_id, vendor_id, received_date FROM dim_material_lot",
         "k", ["material_id", "vendor_id", "received_date"]),
    ]:
        rows = db.query(sql)
        for r in rows:
            store.upsert_node(label, r["k"], {c: r[c] for c in props_cols})
        counts[label] = len(rows)
    # 로트 → 공급사
    lot_edges = [(store.nid("MaterialLot", r["lot_id"]), "SUPPLIED_BY",
                  store.nid("Vendor", r["vendor_id"]), "{}")
                 for r in db.query("SELECT lot_id, vendor_id FROM dim_material_lot")]
    store.bulk_edges(lot_edges)
    return counts


def backfill_defects(start: str, end: str) -> dict:
    """불량 이벤트 백필 — 멱등(같은 defect_id는 갱신)."""
    store.init()
    rows = db.query(
        "SELECT * FROM fact_defect WHERE date_key BETWEEN ? AND ?", (start, end))
    edges: list[tuple[str, str, str, str]] = []
    for r in rows:
        ev = store.upsert_node(
            "DefectEvent", str(r["defect_id"]),
            {"date": r["date_key"], "shift": r["shift"], "type": r["defect_type"],
             "qty": r["qty_defect"], "memo": r["memo"] or ""},
            ledger_ref=f"fact_defect:{r['defect_id']} mo:{r['mo_ref']}")
        pj = json.dumps({"date": r["date_key"]}, ensure_ascii=False)
        if r["worker_id"]:
            edges.append((ev, "WORKED_BY", store.nid("Worker", r["worker_id"]), pj))
        if r["equipment_id"]:
            edges.append((ev, "ON_EQUIPMENT", store.nid("Equipment", r["equipment_id"]), pj))
        if r["material_lot_id"]:
            edges.append((ev, "USED_LOT", store.nid("MaterialLot", r["material_lot_id"]), pj))
        if r["sop_id"]:
            edges.append((ev, "PER_SOP", store.nid("SOP", r["sop_id"]), pj))
        if r["product_id"]:
            edges.append((ev, "OF_PRODUCT", store.nid("Product", r["product_id"]), pj))
    store.bulk_edges(edges)

    for r in db.query(
            "SELECT * FROM fact_equipment_event WHERE date_key BETWEEN ? AND ?",
            (start, end)):
        ev = store.upsert_node(
            "MaintEvent", str(r["event_id"]),
            {"date": r["date_key"], "type": r["event_type"],
             "duration_min": r["duration_min"], "note": r["note"] or ""},
            ledger_ref=f"fact_equipment_event:{r['event_id']}")
        store.upsert_edge(store.nid("Equipment", r["equipment_id"]), "MAINTAINED", ev,
                          {"date": r["date_key"]})
    return {"defect_events": len(rows), "edges": len(edges)}


def reconcile(start: str, end: str) -> dict:
    """건수 대사 — fact_defect 대비 DefectEvent."""
    fact_n = db.scalar(
        "SELECT COUNT(*) FROM fact_defect WHERE date_key BETWEEN ? AND ?", (start, end))
    node_n = db.scalar(
        "SELECT COUNT(*) FROM kg_nodes WHERE label='DefectEvent' "
        "AND json_extract(props,'$.date') BETWEEN ? AND ?", (start, end))
    return {"fact_defect": fact_n, "graph_events": node_n, "ok": fact_n == node_n}
