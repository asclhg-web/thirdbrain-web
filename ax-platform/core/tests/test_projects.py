"""P7-1 프로젝트·KPI 센터 — 정의·카탈로그·측정·목표 조정 루프."""
import pytest

from axp import db, projects


def test_create_registers_catalog_kpis(tmp_db):
    p = projects.create("베이커리 지능화 1차", "폐기 20% 절감", "admin",
                        ["demand", "equipment"])
    assert p["status"] == "active" and p["areas"] == ["demand", "equipment"]
    codes = {k["kpi_code"] for k in p["kpis"]}
    assert {"wape", "mttr_min", "defect_rate"} <= codes
    assert all(k["target"] is None for k in p["kpis"])   # 목표는 사람이 정한다
    assert len(p["modules"]) == len(projects.AREAS["demand"]["modules"]) \
        + len(projects.AREAS["equipment"]["modules"])


def test_create_validates(tmp_db):
    with pytest.raises(ValueError):
        projects.create("", "", "a", ["demand"])
    with pytest.raises(ValueError):
        projects.create("x", "", "a", ["없는영역"])
    with pytest.raises(ValueError):
        projects.create("x", "", "a", [])


def test_measure_honest_pending(tmp_db):
    """측정 불가 KPI는 값을 지어내지 않고 pending으로 남는다."""
    from axp.dataset import transform
    transform.apply_schema()
    p = projects.create("측정 테스트", "", "a", ["demand"])
    r = projects.measure_all(p["project_id"])
    assert r["measured"] == 0 and r["pending"] == 2      # 모델 없음·예측 로그 없음
    k = p["kpis"][0]
    assert projects.kpi_status(k) == "측정 전"


def test_measure_from_facts_and_status(tmp_db):
    from axp.dataset import transform
    transform.apply_schema()
    with db.conn() as c:                     # 차원 없이 사실만 심는 시험 픽스처
        c.execute("PRAGMA foreign_keys=OFF")
        c.execute("INSERT INTO fact_production (mo_ref, date_key, shift, product_id, qty_planned, qty_done) "
                  "VALUES ('MO1','2026-09-01','미상','P',100,90)")
        c.execute("PRAGMA foreign_keys=ON")
    with db.conn() as c:
        c.execute("PRAGMA foreign_keys=OFF")
        c.execute("INSERT INTO fact_defect (defect_id, date_key, product_id, defect_type, qty_defect) "
                  "VALUES (1,'2026-09-01','P','scrap',9)")
        c.execute("PRAGMA foreign_keys=ON")
    p = projects.create("실측 테스트", "", "a", ["production", "inventory"])
    r = projects.measure_all(p["project_id"])
    assert r["measured"] >= 2                            # 계획준수율·폐기율
    adh = next(k for k in p["kpis"] if k["kpi_code"] == "plan_adherence")
    m = projects.latest(adh["kpi_id"])
    assert m["value"] == 90.0
    # 목표 조정 루프 — 이력이 남고 판정이 바뀐다
    projects.set_target(adh["kpi_id"], 85.0, "admin", note="1차 목표")
    adh = db.one("SELECT * FROM axp_project_kpis WHERE kpi_id=?", (adh["kpi_id"],))
    assert projects.kpi_status(adh) == "달성"
    projects.set_target(adh["kpi_id"], 95.0, "admin", note="상향 조정")
    adh = db.one("SELECT * FROM axp_project_kpis WHERE kpi_id=?", (adh["kpi_id"],))
    assert projects.kpi_status(adh) == "미달"
    fb = db.query("SELECT * FROM axp_kpi_feedback WHERE kpi_id=? ORDER BY fb_id", (adh["kpi_id"],))
    assert len(fb) == 2 and fb[1]["old_target"] == 85.0 and fb[1]["new_target"] == 95.0


def test_series_accumulates(tmp_db):
    from axp.dataset import transform
    transform.apply_schema()
    with db.conn() as c:                     # 차원 없이 사실만 심는 시험 픽스처
        c.execute("PRAGMA foreign_keys=OFF")
        c.execute("INSERT INTO fact_production (mo_ref, date_key, shift, product_id, qty_planned, qty_done) "
                  "VALUES ('MO1','2026-09-01','미상','P',100,90)")
        c.execute("PRAGMA foreign_keys=ON")
    p = projects.create("시계열", "", "a", ["production"])
    projects.measure_all(p["project_id"])
    projects.measure_all(p["project_id"])
    adh = next(k for k in p["kpis"] if k["kpi_code"] == "plan_adherence")
    assert len(projects.series(adh["kpi_id"])) == 2
