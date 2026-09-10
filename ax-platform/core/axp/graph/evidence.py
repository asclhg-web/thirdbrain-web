"""M5-3 근거 API — "왜?"에서 원장 레코드까지의 경로.

경로: Rule/후보 → 지지 DefectEvent 표본 → 원장 레코드 ID(fact_defect·mo_ref).
응답 목표 1초 — 화면 3초 내 표시의 절반 예산.
"""
from __future__ import annotations

import json
import time

from .. import db
from . import confidence, store


def _dims_filter_sql(dims: dict) -> tuple[str, list]:
    conds, params = [], []
    mapping = {"worker_id": "worker_id", "equipment_id": "equipment_id",
               "material_lot_id": "material_lot_id", "sop_id": "sop_id",
               "product_id": "product_id", "shift": "shift", "line_id": "line_id"}
    for d, v in dims.items():
        if d == "vendor":
            conds.append("material_lot_id IN (SELECT lot_id FROM dim_material_lot WHERE vendor_id=?)")
            params.append(v)
        elif d in mapping:
            conds.append(f"{mapping[d]}=?")
            params.append(v)
    return " AND ".join(conds) or "1=1", params


def evidence_for_dims(dims: dict, sample: int = 5) -> dict:
    """조합의 근거 — 지지 사실 요약 + 원장 표본."""
    t0 = time.time()
    where, params = _dims_filter_sql(dims)
    agg = db.one(f"""
        SELECT COUNT(*) n_events, SUM(qty_defect) qty, MIN(date_key) first_seen,
               MAX(date_key) last_seen
        FROM fact_defect WHERE {where}""", params)
    rows = db.query(f"""
        SELECT defect_id, date_key, defect_type, qty_defect, mo_ref
        FROM fact_defect WHERE {where}
        ORDER BY qty_defect DESC LIMIT ?""", params + [sample])
    total = db.one("""
        SELECT SUM(qty_defect)*1.0/NULLIF(SUM(qty_produced),0) r FROM
        (SELECT DISTINCT defect_id, qty_defect, qty_produced FROM fact_defect)""")
    return {
        "dims": dims,
        "support": {"n_events": agg["n_events"], "qty_defect": agg["qty"],
                    "first_seen": agg["first_seen"], "last_seen": agg["last_seen"]},
        "ledger_samples": [
            {"table": "fact_defect", "defect_id": r["defect_id"], "mo_ref": r["mo_ref"],
             "date": r["date_key"], "type": r["defect_type"], "qty": r["qty_defect"]}
            for r in rows],
        "overall_defect_rate": round(total["r"] or 0, 4),
        "elapsed_ms": round((time.time() - t0) * 1000, 1),
    }


def evidence_for_rule(rule_key: str) -> dict:
    """Rule/후보 노드의 근거 경로 — 노드 → 조합 → 사실 → 원장."""
    t0 = time.time()
    n = store.node(store.nid("Rule", rule_key))
    if n is None:
        raise ValueError(f"Rule 노드 없음: {rule_key}")
    dims = n["props"].get("dims", {})
    ev = evidence_for_dims(dims)
    path = [
        {"step": "rule", "node": n["node_id"], "text": n["props"].get("text", ""),
         "confidence": n["props"].get("confidence")},
        {"step": "pattern", "dims": dims},
        {"step": "facts", **ev["support"]},
        {"step": "ledger", "samples": ev["ledger_samples"]},
    ]
    return {"rule": rule_key, "path": path,
            "elapsed_ms": round((time.time() - t0) * 1000, 1)}


def why(card_evidence: dict) -> dict:
    """판단 카드의 '왜?' 버튼 — evidence_path 필드를 받아 경로 전개."""
    kind = card_evidence.get("kind")
    if kind == "rule":
        return evidence_for_rule(card_evidence["rule_key"])
    if kind == "dims":
        return evidence_for_dims(card_evidence["dims"])
    if kind == "forecast":
        # 예측 근거: 모델 카드 + 최근 실적 창
        from ..learn import cards as model_cards
        card = model_cards.get_card("demand_forecast") or {}
        recent = db.query(
            "SELECT date_key, qty FROM fact_sales WHERE store_id=? AND product_id=? "
            "ORDER BY date_key DESC LIMIT 14",
            (card_evidence.get("store_id"), card_evidence.get("product_id")))
        return {"model_card": {k: card.get(k) for k in
                               ("model_id", "version", "metrics", "validation_scheme")},
                "recent_ledger": recent}
    raise ValueError(f"알 수 없는 근거 유형: {kind}")


def render_path_text(res: dict) -> str:
    """역추적 화면용 — 사람이 읽는 문장."""
    lines = []
    for step in res.get("path", []):
        if step["step"] == "rule":
            lines.append(f"규칙 {step['node']} (확신도 {step.get('confidence')}): {step['text']}")
        elif step["step"] == "pattern":
            lines.append("조합: " + ", ".join(f"{k}={v}" for k, v in step["dims"].items()))
        elif step["step"] == "facts":
            lines.append(f"지지 사실: 불량 이벤트 {step['n_events']}건 · 불량 {step['qty_defect']}개 "
                         f"({step['first_seen']} ~ {step['last_seen']})")
        elif step["step"] == "ledger":
            ids = ", ".join(f"#{s['defect_id']}({s['mo_ref']})" for s in step["samples"][:3])
            lines.append(f"원장 표본: {ids} …")
    return "\n".join(lines)
