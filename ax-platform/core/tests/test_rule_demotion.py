"""P2-C4 — 규칙 반증 강등: 효과 소멸 2회 연속 → 강등, 재확인 시 리셋."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from axp import db  # noqa: E402
from axp.graph import confidence, store  # noqa: E402


def _seed(effect: bool):
    db.executescript(
        "CREATE TABLE IF NOT EXISTS fact_defect (date_key TEXT, shift TEXT, "
        "product_id TEXT, line_id TEXT, worker_id TEXT, equipment_id TEXT, "
        "material_lot_id TEXT, sop_id TEXT, defect_type TEXT, qty_defect REAL, "
        "qty_produced REAL, memo TEXT, mo_ref TEXT);"
        "CREATE TABLE IF NOT EXISTS dim_material_lot (lot_id TEXT, vendor_id TEXT);"
        "DELETE FROM fact_defect;")
    db.execute("INSERT INTO dim_material_lot VALUES ('L1','V2')")
    import datetime as dt
    rows = []
    for i in range(28):
        d = (dt.date(2026, 8, 14) + dt.timedelta(days=i)).isoformat()
        bad = 30 if effect else 10   # 조합 불량 수량
        rows.append((d, "D", "P-1", "L1", "W1", "OVEN-2", "L1", "S", "탄화", bad, 1000, "", "MO"))
        rows.append((d, "D", "P-1", "L1", "W1", "OVEN-1", "L9", "S", "탄화", 10, 1000, "", "MO"))
    db.executemany("INSERT INTO fact_defect VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)


def _promoted_candidate():
    confidence.db.executescript(confidence.DDL)
    store.init()
    confidence._ensure_demoted_status()
    db.execute(
        "INSERT INTO causal_candidates (dims, confidence, confirmations, "
        "status, rule_id, updated_at) VALUES (?,?,?,?,?,?)",
        (json.dumps({"equipment_id": "OVEN-2", "vendor": "V2"}), 0.88,
         "[]", "promoted", "RULE-0001", "2026-08-01"))
    store.upsert_node("Rule", "RULE-0001", {"kind": "rule", "text": "t", "confidence": 0.88})
    return db.scalar("SELECT MAX(cc_id) FROM causal_candidates")


def test_refute_twice_then_demote(tmp_db):
    _seed(effect=False)          # 효과 소멸 상태
    cc = _promoted_candidate()
    r1 = confidence.review_promoted("2026-09-10")
    assert r1 and r1[0]["action"] == "refute"
    r2 = confidence.review_promoted("2026-09-10")
    assert r2 and r2[0]["action"] == "demoted"
    assert db.one("SELECT status FROM causal_candidates WHERE cc_id=?", (cc,))["status"] == "demoted"
    node = store.node(store.nid("Rule", "RULE-0001"))
    assert node["props"].get("status") == "demoted"


def test_effect_alive_keeps_rule(tmp_db):
    _seed(effect=True)           # 효과 유지(3배 높음)
    _promoted_candidate()
    assert confidence.review_promoted("2026-09-10") == []
