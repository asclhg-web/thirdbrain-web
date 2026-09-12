"""P7-3 KPI 무한 개선 루프 — 측정→미달 카드→승인 환류→피드백→재판정."""
from axp import db, projects
from axp.agents import five, inbox, runtime
from axp.judge import cards as jcards


def _seed(qty_done=70):
    from axp.dataset import transform
    transform.apply_schema()
    with db.conn() as c:
        c.execute("PRAGMA foreign_keys=OFF")
        c.execute("INSERT INTO fact_production (mo_ref, date_key, shift, product_id, qty_planned, qty_done) "
                  f"VALUES ('MO1','2026-09-01','미상','P',100,{qty_done})")
        c.execute("PRAGMA foreign_keys=ON")


def test_full_improvement_loop(tmp_db):
    _seed(qty_done=70)                                    # 준수율 70%
    p = projects.create("루프 검증", "준수율 90%", "admin", ["production"])
    adh = next(k for k in p["kpis"] if k["kpi_code"] == "plan_adherence")
    projects.set_target(adh["kpi_id"], 90.0, "admin", note="목표 90%")
    projects.measure_all(p["project_id"])                 # ① 측정 — 70 < 90 미달

    five.register_all()
    r = runtime.run_agent("kpi_agent", {"run_date": "2026-09-12"}, shadow=True)
    assert r["ok"] and len(r["cards"]) == 1               # ② 미달 카드 생성
    card = jcards.get(r["cards"][0])
    assert card["kind"] == "kpi_improve" and "미달" in card["proposal"]
    assert "계획 준수율" in card["narrative"] and "fact_production" in card["narrative"]

    r2 = runtime.run_agent("kpi_agent", {"run_date": "2026-09-12"}, shadow=True)
    assert len(r2["cards"]) == 0                          # ③ 중복 방지

    inbox.decide(card["card_id"], "승인자", "card_approver", True)   # ④ 승인 → 환류
    fb = db.query("SELECT * FROM axp_kpi_feedback WHERE kpi_id=? AND action='improve'",
                  (adh["kpi_id"],))
    assert len(fb) == 1 and "카드" in fb[0]["note"]

    # P7-I2: 승인 직후(같은 측정) 재실행 — 개선 기록이 있으므로 재제안 없음
    r_after = runtime.run_agent("kpi_agent", {"run_date": "2026-09-12"}, shadow=True)
    assert len(r_after["cards"]) == 0
    # 다음 측정에서도 여전히 미달이면 그때 새 카드가 온다
    projects.measure_all(p["project_id"])
    r_next = runtime.run_agent("kpi_agent", {"run_date": "2026-09-13"}, shadow=True)
    assert len(r_next["cards"]) == 1
    inbox.decide(r_next["cards"][0], "승인자", "card_approver", True)

    # ⑤ 개선이 실적으로 나타난 뒤(90 달성) 재측정 — 카드가 더 안 생긴다
    db.execute("UPDATE fact_production SET qty_done=95 WHERE mo_ref='MO1'")
    projects.measure_all(p["project_id"])
    adh = db.one("SELECT * FROM axp_project_kpis WHERE kpi_id=?", (adh["kpi_id"],))
    assert projects.kpi_status(adh) == "달성"
    r3 = runtime.run_agent("kpi_agent", {"run_date": "2026-09-13"}, shadow=True)
    assert len(r3["cards"]) == 0


def test_no_target_no_card(tmp_db):
    _seed()
    projects.create("목표 없음", "", "admin", ["production"])
    five.register_all()
    r = runtime.run_agent("kpi_agent", {"run_date": "2026-09-12"}, shadow=True)
    assert r["ok"] and len(r["cards"]) == 0               # 목표 미설정은 제안 없음


def test_scheduler_measures_active_projects(tmp_db):
    _seed()
    p = projects.create("배치 측정", "", "admin", ["production"])
    out = projects.measure_active_all()
    assert out["projects"] == 1 and out["measured"] >= 1
    adh = next(k for k in p["kpis"] if k["kpi_code"] == "plan_adherence")
    assert projects.latest(adh["kpi_id"]) is not None
