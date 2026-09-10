"""M4·M7 — 모델 카드 강제·승인 권한·환류 규율."""
import pytest

from axp.learn import cards as mcards
from axp.learn.simulate import Costs, InventoryTwin, Policy


def test_model_card_missing_fields_rejected(tmp_db):
    with pytest.raises(mcards.CardError):
        mcards.register({"model_id": "m", "problem": "p"})


def test_model_card_promote_requires_registration(tmp_db):
    with pytest.raises(mcards.CardError):
        mcards.promote("ghost", "v9")


def test_twin_conservation():
    """트윈 보존 법칙 — 판매+결품 = 총수요, 폐기≤입고."""
    import numpy as np
    demand = np.array([10, 20, 15, 30, 5], dtype=float)
    twin = InventoryTwin(demand, demand.copy(), Costs())
    r = twin.run(Policy(demand_factor=1.0, safety_days=0.0))
    assert r["service_level"] <= 1.0
    assert r["stockout_qty"] >= 0 and r["scrap_qty"] >= 0
    served = r["service_level"] * r["total_demand"]
    assert abs(served + r["stockout_qty"] - r["total_demand"]) < 1e-6


def test_production_plan_feedback(tmp_db):
    from axp.judge import cards as jcards
    from axp.agents import inbox
    cid = jcards.create({
        "kind": "production_plan", "agent": "t", "proposal": "p",
        "values": [{"name": "생산 P-X", "value": 100, "source": "s"}],
        "evidence": {"kind": "forecast", "store_id": "ALL", "product_id": "ALL",
                     "plan_date": "2026-01-02",
                     "plan": [{"product_id": "P-X", "line_id": "L1", "qty": 100}],
                     "daily": [{"date_key": "2026-01-02"}]},
        "approver": "a"})
    d = inbox.decide(cid, "승인자", "card_approver", True)
    assert d["feedback"]["written"][0]["param"] == "prod_plan:2026-01-02:P-X"


def test_inbox_permission_and_feedback_guard(tmp_db):
    from axp.judge import cards as jcards
    from axp.agents import inbox
    cid = jcards.create({
        "kind": "demand_forecast", "agent": "t", "proposal": "p",
        "values": [{"name": "n", "value": 1, "source": "s"}],
        "evidence": {"kind": "forecast", "store_id": "S", "product_id": "P",
                     "daily": [{"date_key": "2026-01-01"}]},
        "range": {"p50": 1}, "approver": "a"})
    with pytest.raises(inbox.PermissionError_):
        inbox.decide(cid, "누군가", "steward", True)
    with pytest.raises(inbox.PermissionError_):
        inbox.apply_feedback(cid, "누군가")      # 승인 전 환류 금지
    d = inbox.decide(cid, "승인자", "card_approver", True)
    assert d["status"] == "approved" and d["feedback"]["written"]
