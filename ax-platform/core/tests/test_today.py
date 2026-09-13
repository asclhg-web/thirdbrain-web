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


def test_journey_card_progresses_and_disappears(tmp_db):
    """P8-3: 시작 여정 5단계 — 미완이면 표시, 5단계 완료 후 사라진다."""
    c = _client()
    _login(c, "admin")
    body = c.get("/today").text
    assert "시작 여정" in body and "→ 프로젝트 정의" in body
    import json as _json
    from axp import config as _config
    from axp.dataset import transform
    (_config.DATA / "profile.json").write_text(
        _json.dumps({"company": "여정사"}, ensure_ascii=False), encoding="utf-8")
    transform.apply_schema()
    with db.conn() as c0:
        c0.execute("PRAGMA foreign_keys=OFF")
        c0.execute("INSERT INTO fact_sales VALUES ('2026-09-01','S','P',5,5000,'r',0)")
        c0.execute("INSERT INTO fact_production (mo_ref, date_key, shift, product_id, qty_planned, qty_done) "
                   "VALUES ('MO1','2026-09-01','미상','P',100,90)")
        c0.execute("PRAGMA foreign_keys=ON")
    p = projects.create("여정", "", "admin", ["production"])
    adh = next(k for k in p["kpis"] if k["kpi_code"] == "plan_adherence")
    projects.set_target(adh["kpi_id"], 80.0, "admin")
    projects.measure_all(p["project_id"])
    body = c.get("/today").text
    assert "시작 여정" not in body                       # 완주 → 카드 소멸


def test_upload_pipeline_strip(tmp_db):
    """P8-3: 자료 반입 화면에 파이프라인 진행줄 — 격리 건수·마지막 반영 표시."""
    c = _client()
    _login(c, "steward")
    body = c.get("/upload").text
    assert "① 업로드" in body and "지금 반영" in body and "아직 반영 전" in body


def test_projects_empty_state_guides(tmp_db):
    c = _client()
    _login(c, "admin")
    body = c.get("/projects").text
    assert "아직 프로젝트가 없습니다" in body


def test_tenants_screen_admin_only(tmp_db):
    """P8-5b: 체험 테넌트 화면 — admin 전용, 빈 상태 안내, 없는 테넌트 404."""
    c = _client()
    _login(c, "approver")
    assert c.get("/tenants").status_code == 403
    c2 = _client()
    _login(c2, "admin")
    body = c2.get("/tenants").text
    assert "체험 테넌트" in body and "서버 명령으로만" in body
    r = c2.post("/tenants/ghost/reset")
    assert r.status_code == 404


def test_quarantine_confirm_empty_code_friendly(tmp_db):
    """P8-I1: 코드 칸을 비운 채 확정하면 원시 JSON이 아니라 화면 안내(400)."""
    from axp.dataset import codemap
    codemap.init()
    db.execute(
        "INSERT INTO quarantine_queue (domain, alias, context, n_rows, status, created_at) "
        "VALUES ('product','빈코드','excel',2,'pending','2026-09-13')")
    q_id = db.scalar("SELECT MAX(q_id) FROM quarantine_queue")
    c = _client()
    _login(c, "steward")
    r = c.post(f"/quarantine/{q_id}/confirm", data={"code": ""})
    assert r.status_code == 400 and "표준 코드를 입력" in r.text
    assert "detail" not in r.text[:200]                    # 원시 JSON 아님
    r2 = c.post(f"/quarantine/{q_id}/confirm", data={"code": "P-OK"})
    assert r2.status_code == 303
    assert codemap.resolve("product", "빈코드") == "P-OK"


# ── P9-2: 공개 메인 랜딩 + 데모 서브페이지 ──────────────────────
def test_landing_public_for_anon(tmp_db):
    """익명 방문자는 '/'에서 공개 메인 랜딩(로그인·데모 진입)을 본다."""
    c = _client()
    r = c.get("/", follow_redirects=False)
    assert r.status_code == 200
    body = r.text
    assert "제안은 AI가" in body           # 히어로 카피
    assert 'href="/demo"' in body          # 데모 진입
    assert 'href="/login"' in body         # 로그인 진입


def test_demo_page_public(tmp_db):
    """/demo는 로그인 없이 열리고, 판단 카드·근거 사다리를 보여준다."""
    c = _client()
    r = c.get("/demo")
    assert r.status_code == 200
    assert "판단 카드 승인함" in r.text
    assert "RULE-0001" in r.text            # 근거 사다리
    assert 'href="/login"' in r.text        # 실사용 유도


def test_root_redirects_logged_in(tmp_db):
    """로그인 사용자는 '/'에서 역할 홈으로 이동(랜딩 아님)."""
    c = _client()
    _login(c, "admin")
    r = c.get("/", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] in ("/today", "/inbox", "/upload", "/projects")
