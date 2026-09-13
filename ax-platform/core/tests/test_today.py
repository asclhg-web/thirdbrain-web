"""P8-1·P8-2 — 4허브 내비·역할별 홈·'오늘' 화면."""
from axp import db, projects
from tests.test_webapp import _client, _login


def test_login_redirects_by_role(tmp_db):
    """P8-1: 역할이 홈을 결정 — 대표(viewer)=성과, 승인자=판단, 실무=데이터, admin=오늘."""
    import axp.webapp as w
    w.ensure_users()
    for user, home in (("admin", "/today"), ("steward", "/upload"), ("approver", "/inbox")):
        c = _client()
        db.execute("UPDATE axp_users SET must_change=0 WHERE username=?", (user,))
        r = c.post("/login", data={"username": user, "password": "change-me!"})
        assert r.status_code == 303 and r.headers["location"] == home, (user, r.headers)


def test_root_redirects_to_role_home(tmp_db):
    c = _client()
    _login(c, "approver")
    r = c.get("/")
    assert r.status_code == 303 and r.headers["location"] == "/inbox"


def test_admin_hub_hidden_from_non_admin(tmp_db):
    """관리 허브(계정·체험 신청)는 admin에게만 보인다 — 접근은 종전대로 라우트가 강제."""
    c = _client()
    _login(c, "approver")
    body = c.get("/inbox").text
    assert ">관리<" not in body
    c2 = _client()
    _login(c2, "admin")
    assert ">관리<" in c2.get("/inbox").text


def test_today_lists_todos_and_links(tmp_db):
    """P8-2: 승인 대기·확인할 이름·미달 KPI가 할 일 카드로 모인다."""
    from axp.dataset import codemap
    from axp.judge import cards as jcards
    db.executescript(jcards.DDL)
    db.execute(
        "INSERT INTO judgment_cards (kind, agent, proposal, narrative, values_json, "
        "range_json, evidence_json, alternatives_json, approver, status, created_at) "
        "VALUES ('demand_forecast','a','t','n','[]','{}','[]','[]','x','proposed','2026-09-13')")
    codemap.init()
    db.execute(
        "INSERT INTO quarantine_queue (domain, alias, context, n_rows, status, created_at) "
        "VALUES ('product','새과자','excel',3,'pending','2026-09-13')")
    from axp.dataset import transform
    transform.apply_schema()
    with db.conn() as c0:
        c0.execute("PRAGMA foreign_keys=OFF")
        c0.execute("INSERT INTO fact_production (mo_ref, date_key, shift, product_id, qty_planned, qty_done) "
                   "VALUES ('MO1','2026-09-01','미상','P',100,50)")
        c0.execute("PRAGMA foreign_keys=ON")
    p = projects.create("오늘 홈", "", "admin", ["production"])
    adh = next(k for k in p["kpis"] if k["kpi_code"] == "plan_adherence")
    projects.set_target(adh["kpi_id"], 99.0, "admin")     # 50% 실적 → 확실한 미달
    projects.measure_all(p["project_id"])
    c = _client()
    _login(c, "admin")
    body = c.get("/today").text
    assert "승인 대기 카드 1건" in body and "/inbox" in body
    assert "확인할 이름 1건" in body
    assert "목표 미달 KPI" in body and f"/projects/{p['project_id']}" in body
    assert "무엇이든 물어보세요" in body


def test_today_empty_state(tmp_db):
    c = _client()
    _login(c, "approver")
    body = c.get("/today").text
    assert "오늘 처리할 일이 없습니다" in body
