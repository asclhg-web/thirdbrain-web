"""P7-5 측정 전 KPI 결선 — 결품·편향·질문 활용(+리드타임은 PG/원장 전용)."""
import json

from axp import common, db, projects
from axp.judge import cards as jcards


def test_stockout_days_from_snapshots(tmp_db):
    from axp.dataset import transform
    transform.apply_schema()
    projects.init()
    with db.conn() as c:
        c.execute("PRAGMA foreign_keys=OFF")
        c.execute("INSERT INTO dim_product VALUES ('P-PIE','파이','bakery',1000)")
        c.execute("PRAGMA foreign_keys=ON")
    today = common.now_iso()[:10]
    db.execute("INSERT INTO axp_stock_snapshots VALUES (?, 'P-PIE', 0)", (today,))
    db.execute("INSERT INTO axp_stock_snapshots VALUES ('2026-09-10', 'P-PIE', 12)")
    v, src = projects.measure("stockout_days")
    assert v == 1.0 and "최근 30일" in src               # 오늘만 결품

    db.execute("DELETE FROM axp_stock_snapshots")
    v, src = projects.measure("stockout_days")
    assert v is None and "축적 전" in src                # 원천 없으면 측정 전


def test_forecast_bias_from_cards(tmp_db):
    from axp.dataset import transform
    transform.apply_schema()
    daily = [{"date_key": "2026-09-01", "p50": 80.0},
             {"date_key": "2026-09-02", "p50": 100.0},
             {"date_key": "2026-09-03", "p50": 120.0}]
    jcards.create({
        "kind": "demand_forecast", "agent": "demand_agent",
        "proposal": "테스트", "values": [{"name": "x", "value": 1, "unit": "", "source": "t"}],
        "evidence": {"store_id": "1", "product_id": "P-PIE", "daily": daily},
        "approver": "card_approver"})
    v, src = projects.measure("forecast_bias")
    assert v is None and "표본 부족" in src              # 실판매 대조 전
    with db.conn() as c:
        c.execute("PRAGMA foreign_keys=OFF")
        for dk, actual in (("2026-09-01", 100), ("2026-09-02", 100), ("2026-09-03", 100)):
            c.execute("INSERT INTO fact_sales VALUES (?,?,?,?,?,?,?)",
                      (dk, "1", "P-PIE", actual, actual * 1000, "1", 0))
        c.execute("PRAGMA foreign_keys=ON")
    v, src = projects.measure("forecast_bias")
    # 편향 = mean((100-80)/100, 0, (100-120)/100)% = 0.0
    assert v == 0.0 and "3건" in src


def test_weekly_questions_from_log(tmp_db):
    v, src = projects.measure("weekly_questions")
    assert v is None and "축적 전" in src
    from tests.test_webapp import _client, _login
    c = _client()
    _login(c, "approver")
    c.post("/ask", data={"q": "요즘 어떤가요"})          # 라우팅 불가 질문도 로그는 남는다
    v, src = projects.measure("weekly_questions")
    assert v == 1.0 and "7일" in src
    assert db.scalar("SELECT username FROM question_log") == "approver"


def test_mo_lead_by_backend(tmp_db):
    v, src = projects.measure("mo_lead_days")
    if db.BACKEND == "postgres":
        # 이 클러스터엔 실 Odoo 원장이 복제돼 있어 실측이 나온다(또는 완료 MO 없음)
        assert v is not None or "완료 MO" in src
    else:
        assert v is None and "미복제" in src             # 원장 없음 — 정직한 측정 전
