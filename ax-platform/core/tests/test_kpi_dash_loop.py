"""P7-9 대시보드 루프 상태 표기 — 카드 대기/기록됨/제안 예정."""
from axp import db, projects
from axp.agents import five, inbox, runtime
from tests.test_webapp import _client, _login


def test_dashboard_shows_loop_state(tmp_db):
    from axp.dataset import transform
    transform.apply_schema()
    with db.conn() as c:
        c.execute("PRAGMA foreign_keys=OFF")
        c.execute("INSERT INTO fact_production (mo_ref, date_key, shift, product_id, qty_planned, qty_done) "
                  "VALUES ('MO1','2026-09-01','미상','P',100,70)")
        c.execute("PRAGMA foreign_keys=ON")
    p = projects.create("루프 표기", "", "admin", ["production"])
    adh = next(k for k in p["kpis"] if k["kpi_code"] == "plan_adherence")
    projects.set_target(adh["kpi_id"], 90.0, "admin")
    projects.measure_all(p["project_id"])
    c = _client()
    _login(c, "admin")
    pid = p["project_id"]
    # ① 카드 생성 전 — 제안 예정 안내
    assert "개선 카드가 제안됩니다" in c.get(f"/projects/{pid}").text
    # ② 카드 생성 — 승인 대기 링크
    five.register_all()
    r = runtime.run_agent("kpi_agent", {"run_date": "2026-09-12"}, shadow=True)
    assert "승인 대기" in c.get(f"/projects/{pid}").text
    # ③ 승인 — 개선 기록됨 표시
    inbox.decide(r["cards"][0], "승인자", "card_approver", True)
    assert "개선 활동 기록됨" in c.get(f"/projects/{pid}").text
