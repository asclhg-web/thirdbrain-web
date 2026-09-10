"""M5-2 원인 후보·확신도 루프 — wave(확신도)에서 particle(Rule)로.

흐름: 마이닝(M3)·모델 중요도(M4) → CAUSAL_CANDIDATE(확신도 초기값)
      → 독립 확인(다른 관측 창) 누적 → 임계(70% 그리고 3회) → 승인 상신
      → 사람 승인 시 Rule 승격(이력 보존) / 반려 시 확신도 감쇠.

독립 확인의 정의: 관측 창(window_end)이 서로 14일 이상 떨어진 확인.
확신도 결합: conf = 1 - Π(1 - s_i), s_i = min(0.5, z_i/40) — 상한 0.95.
"""
from __future__ import annotations

import json

from .. import common, db
from ..studio import mining
from . import store

PROMOTE_CONF = 0.70
PROMOTE_CONFIRMS = 3
INDEPENDENT_GAP_DAYS = 14

DDL = """
CREATE TABLE IF NOT EXISTS causal_candidates (
  cc_id INTEGER PRIMARY KEY AUTOINCREMENT,
  dims TEXT NOT NULL UNIQUE,       -- 정렬된 JSON {차원: 값}
  confidence REAL NOT NULL DEFAULT 0,
  confirmations TEXT NOT NULL DEFAULT '[]',   -- [{window_end, z, source}]
  status TEXT NOT NULL DEFAULT 'watching'
         CHECK (status IN ('watching','submitted','promoted','rejected')),
  rule_id TEXT, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS rule_history (
  hist_id INTEGER PRIMARY KEY AUTOINCREMENT,
  cc_id INTEGER, action TEXT, actor TEXT, note TEXT, at TEXT
);
"""


def _norm_dims(dims: dict) -> str:
    return json.dumps(dict(sorted(dims.items())), ensure_ascii=False)


def _strength(z: float) -> float:
    return min(0.5, max(0.05, z / 40.0))


def _combine(confirms: list[dict]) -> float:
    conf = 1.0
    for c in confirms:
        conf *= 1 - _strength(c.get("z", 4.0))
    return min(0.95, 1 - conf)


def ingest_mining(run_date: str) -> dict:
    """마이닝 후보 수용 — 독립 창이면 확인 1회 추가."""
    db.executescript(DDL)
    store.init()
    added = updated = 0
    cands = mining.new_candidates()
    for c in cands:
        dims_j = _norm_dims(c["dims"])
        row = db.one("SELECT * FROM causal_candidates WHERE dims=?", (dims_j,))
        confirm = {"window_end": c["window_end"], "z": round(c["z"], 2),
                   "source": f"mining {run_date}"}
        if row is None:
            db.execute(
                "INSERT INTO causal_candidates (dims, confidence, confirmations, updated_at) "
                "VALUES (?,?,?,?)",
                (dims_j, _combine([confirm]), json.dumps([confirm]), common.now_iso()))
            added += 1
        else:
            confirms = json.loads(row["confirmations"])
            import datetime as _dt
            last = max((x["window_end"] for x in confirms), default="0000-01-01")
            gap = (_dt.date.fromisoformat(c["window_end"])
                   - _dt.date.fromisoformat(last)).days
            if gap >= INDEPENDENT_GAP_DAYS:
                confirms.append(confirm)
                db.execute(
                    "UPDATE causal_candidates SET confidence=?, confirmations=?, updated_at=? "
                    "WHERE cc_id=?",
                    (_combine(confirms), json.dumps(confirms), common.now_iso(), row["cc_id"]))
                updated += 1
    mining.mark_sent([c["cand_id"] for c in cands])
    _sync_graph()
    return {"added": added, "confirmed": updated, "seen": len(cands)}


def ingest_model_importance(items: list[dict]) -> int:
    """모델 특징 중요도 → 확인 1회로 수용 (source 표시)."""
    db.executescript(DDL)
    n = 0
    for it in items:
        if it.get("importance", 0) <= 0.01:
            continue
        dims_j = _norm_dims(it["dims"])
        row = db.one("SELECT * FROM causal_candidates WHERE dims=?", (dims_j,))
        confirm = {"window_end": common.now_iso()[:10],
                   "z": 8.0 * min(1.0, it["importance"] * 10), "source": it["source"]}
        if row is None:
            db.execute(
                "INSERT INTO causal_candidates (dims, confidence, confirmations, updated_at) "
                "VALUES (?,?,?,?)",
                (dims_j, _combine([confirm]), json.dumps([confirm]), common.now_iso()))
        else:
            confirms = json.loads(row["confirmations"])
            if not any(x["source"] == it["source"] for x in confirms):
                confirms.append(confirm)
                db.execute(
                    "UPDATE causal_candidates SET confidence=?, confirmations=?, updated_at=? "
                    "WHERE cc_id=?",
                    (_combine(confirms), json.dumps(confirms), common.now_iso(), row["cc_id"]))
        n += 1
    _sync_graph()
    return n


def _sync_graph() -> None:
    """후보를 그래프 CAUSAL_CANDIDATE 간선으로 반영 — 차원 노드 → DefectPattern."""
    for row in db.query("SELECT * FROM causal_candidates WHERE status IN ('watching','submitted')"):
        dims = json.loads(row["dims"])
        pat = store.upsert_node("Rule", f"cand-{row['cc_id']}",
                                {"kind": "candidate", "dims": dims,
                                 "confidence": row["confidence"],
                                 "status": row["status"]})
        for d, v in dims.items():
            label = {"worker_id": "Worker", "equipment_id": "Equipment",
                     "material_lot_id": "MaterialLot", "sop_id": "SOP",
                     "product_id": "Product", "vendor": "Vendor",
                     "line_id": "Equipment", "shift": None}.get(d)
            if label:
                store.upsert_edge(store.nid(label, str(v)), "CAUSAL_CANDIDATE", pat,
                                  {"confidence": row["confidence"]})


def check_thresholds() -> list[dict]:
    """임계 도달 후보 → 승인 상신(submitted). 반환: 상신 목록."""
    db.executescript(DDL)
    out = []
    for row in db.query("SELECT * FROM causal_candidates WHERE status='watching'"):
        confirms = json.loads(row["confirmations"])
        if row["confidence"] >= PROMOTE_CONF and len(confirms) >= PROMOTE_CONFIRMS:
            db.execute("UPDATE causal_candidates SET status='submitted', updated_at=? "
                       "WHERE cc_id=?", (common.now_iso(), row["cc_id"]))
            db.execute("INSERT INTO rule_history (cc_id, action, actor, note, at) "
                       "VALUES (?,?,?,?,?)",
                       (row["cc_id"], "submitted", "system",
                        f"conf={row['confidence']:.2f}, confirms={len(confirms)}",
                        common.now_iso()))
            out.append({"cc_id": row["cc_id"], "dims": json.loads(row["dims"]),
                        "confidence": row["confidence"], "confirmations": len(confirms)})
    return out


def decide(cc_id: int, approve: bool, actor: str, note: str = "") -> dict:
    """사람의 승인/반려 — 승격 시 Rule 노드 고정, 반려 시 확신도 반감."""
    db.executescript(DDL)
    row = db.one("SELECT * FROM causal_candidates WHERE cc_id=? AND status='submitted'",
                 (cc_id,))
    if row is None:
        raise ValueError(f"상신 상태의 후보 {cc_id} 없음")
    dims = json.loads(row["dims"])
    if approve:
        rule_id = f"RULE-{cc_id:04d}"
        store.upsert_node("Rule", rule_id,
                          {"kind": "rule", "dims": dims,
                           "confidence": row["confidence"],
                           "text": rule_text(dims), "approved_by": actor})
        for d, v in dims.items():
            label = {"worker_id": "Worker", "equipment_id": "Equipment",
                     "material_lot_id": "MaterialLot", "sop_id": "SOP",
                     "product_id": "Product", "vendor": "Vendor"}.get(d)
            if label:
                store.upsert_edge(store.nid(label, str(v)), "GOVERNED_BY",
                                  store.nid("Rule", rule_id), {})
        db.execute("UPDATE causal_candidates SET status='promoted', rule_id=?, updated_at=? "
                   "WHERE cc_id=?", (rule_id, common.now_iso(), cc_id))
        db.execute("INSERT INTO rule_history (cc_id, action, actor, note, at) VALUES (?,?,?,?,?)",
                   (cc_id, "promoted", actor, note, common.now_iso()))
        return {"cc_id": cc_id, "rule_id": rule_id, "status": "promoted"}
    db.execute("UPDATE causal_candidates SET status='watching', confidence=?, updated_at=? "
               "WHERE cc_id=?", (row["confidence"] * 0.5, common.now_iso(), cc_id))
    db.execute("INSERT INTO rule_history (cc_id, action, actor, note, at) VALUES (?,?,?,?,?)",
               (cc_id, "rejected", actor, note, common.now_iso()))
    return {"cc_id": cc_id, "status": "rejected→watching", "confidence_halved": True}


def rule_text(dims: dict) -> str:
    KOR = {"equipment_id": "설비", "worker_id": "작업자", "vendor": "공급사",
           "material_lot_id": "자재 로트", "sop_id": "표준작업", "shift": "근무조",
           "product_id": "제품", "line_id": "라인"}
    cond = " × ".join(f"{KOR.get(k, k)} {v}" for k, v in dims.items())
    return f"{cond} 조합에서 불량률이 유의하게 높다 — 해당 조합 투입 시 사전 점검"


def rules(status: str = "promoted") -> list[dict]:
    db.executescript(DDL)
    rows = db.query("SELECT * FROM causal_candidates WHERE status=?", (status,))
    for r in rows:
        r["dims"] = json.loads(r["dims"])
        r["confirmations"] = json.loads(r["confirmations"])
    return rows
