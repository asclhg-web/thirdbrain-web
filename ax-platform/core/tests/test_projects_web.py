"""P7-2 프로젝트 화면 — 위저드·대시보드·목표 조정·측정."""
from axp import db, projects
from tests.test_webapp import _client, _login


def _seed_facts():
    from axp.dataset import transform
    transform.apply_schema()
    with db.conn() as c:
        c.execute("PRAGMA foreign_keys=OFF")
        c.execute("INSERT INTO fact_production (mo_ref, date_key, shift, product_id, qty_planned, qty_done) "
                  "VALUES ('MO1','2026-09-01','미상','P',100,90)")
        c.execute("PRAGMA foreign_keys=ON")


def test_wizard_creates_and_dashboard_renders(tmp_db):
    _seed_facts()
    c = _client()
    _login(c, "admin")
    r = c.post("/projects/create", data={"name": "폐기 절감 1차", "goal": "월 폐기 20% 절감",
                                         "areas": ["production", "equipment"]})
    assert r.status_code == 303 and r.headers["location"].startswith("/projects/")
    pid = int(r.headers["location"].rsplit("/", 1)[1])
    r = c.get(f"/projects/{pid}")
    assert r.status_code == 200
    assert "KPI 대시보드" in r.text and "계획 준수율" in r.text
    assert "생산계획·작업지시 지능화" in r.text          # 영역 이름
    assert "측정 전" in r.text                            # 정직 표기(측정 전 KPI)

    # 측정 → 값·차트(svg) 등장
    r = c.post(f"/projects/{pid}/measure")
    assert "측정 완료" in r.text and "<svg" in r.text and "90 %" in r.text

    # 목표 조정 → 달성 판정 + 이력
    adh = db.one("SELECT * FROM axp_project_kpis WHERE kpi_code='plan_adherence'")
    r = c.post(f"/projects/{pid}/target",
               data={"kpi_id": str(adh["kpi_id"]), "target": "85", "note": "1차 목표"})
    assert r.status_code == 303
    r = c.get(f"/projects/{pid}")
    assert "달성" in r.text and "목표 조정" in r.text and "1차 목표" in r.text


def test_viewer_reads_but_cannot_edit(tmp_db):
    projects.create("열람 테스트", "", "admin", ["demand"])
    c = _client()
    _login(c, "approver")
    assert c.get("/projects").status_code == 200
    r = c.post("/projects/create", data={"name": "x", "areas": ["demand"]})
    assert r.status_code == 403                           # 정의는 admin만
    adh = db.one("SELECT kpi_id FROM axp_project_kpis LIMIT 1")
    r = c.post("/projects/1/target", data={"kpi_id": str(adh["kpi_id"]), "target": "1"})
    assert r.status_code == 403                           # 목표 조정도 admin만


def test_create_validation_message(tmp_db):
    c = _client()
    _login(c, "admin")
    r = c.post("/projects/create", data={"name": "", "goal": ""})
    assert r.status_code == 400 and "입력하세요" in r.text
