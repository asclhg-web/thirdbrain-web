"""P2-C1 — 통합 웹앱: 인증·역할 강제·격리 undo·카드 결정."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient  # noqa: E402

from axp import db  # noqa: E402
from axp.dataset import codemap  # noqa: E402
import os
os.environ["AXP_BOOTSTRAP_PW"] = "change-me!"   # 테스트는 고정 비밀번호
from axp import webapp  # noqa: E402
webapp.BOOTSTRAP_PW = "change-me!"


class _Client(TestClient):
    """P5-S3: 로그인한 사용자의 CSRF 토큰을 POST에 자동 주입 (실브라우저의 폼 동작 재현)."""
    _user = None

    def post(self, url, data=None, files=None, **kw):
        if self._user and url != "/login" and not kw.pop("no_csrf", False):
            data = dict(data or {})
            data.setdefault("_csrf", webapp._sign("csrf|" + self._user))
        return super().post(url, data=data, files=files, **kw)


def _client():
    return _Client(webapp.app, follow_redirects=False)


def _login(c, user, keep_must_change=False):
    webapp.ensure_users()
    if not keep_must_change:   # 기존 테스트는 초기 비밀번호 강제 변경(P5-S2) 이후 상태로
        db.execute("UPDATE axp_users SET must_change=0 WHERE username=?", (user,))
    r = c.post("/login", data={"username": user, "password": "change-me!"})
    assert r.status_code == 303, r.text
    c._user = user
    return r


def test_login_required(tmp_db):
    c = _client()
    r = c.get("/inbox")
    assert r.status_code == 303 and r.headers["location"] == "/login"


def test_wrong_password_rejected(tmp_db):
    c = _client()
    r = c.post("/login", data={"username": "admin", "password": "nope"})
    assert r.status_code == 401


def test_role_enforced_on_quarantine_confirm(tmp_db):
    c = _client()
    _login(c, "approver")   # 승인자는 격리 확정 불가
    r = c.post("/quarantine/1/confirm", data={"code": "P-X"})
    assert r.status_code == 403


def test_quarantine_confirm_and_undo(tmp_db):
    codemap.init()
    db.execute(
        "INSERT INTO quarantine_queue (domain, alias, context, n_rows, status, created_at) "
        "VALUES ('product','신상품쿠키','excel',7,'pending','2026-09-11')")
    q_id = db.scalar("SELECT MAX(q_id) FROM quarantine_queue")
    c = _client()
    _login(c, "steward")
    r = c.post(f"/quarantine/{q_id}/confirm", data={"code": "P-COOKIE"})
    assert r.status_code == 303
    assert codemap.resolve("product", "신상품쿠키") == "P-COOKIE"
    r = c.post(f"/quarantine/{q_id}/undo")
    assert r.status_code == 303
    assert codemap.resolve("product", "신상품쿠키") is None
    assert db.one("SELECT status FROM quarantine_queue WHERE q_id=?", (q_id,))["status"] == "pending"


def test_reject_requires_reason(tmp_db):
    from axp.judge import cards as jcards
    db.executescript(jcards.DDL)
    db.execute(
        "INSERT INTO judgment_cards (kind, agent, proposal, narrative, values_json, "
        "range_json, evidence_json, alternatives_json, approver, status, created_at) "
        "VALUES ('demand_forecast','a','t','n [근거: x]','[]','{}','[]','[]','카드 승인자','proposed','2026-09-11')")
    cid = db.scalar("SELECT MAX(card_id) FROM judgment_cards")
    c = _client()
    _login(c, "approver")
    r = c.post(f"/cards/{cid}/decide", data={"approve": "0", "reason": ""})
    assert r.status_code == 400


def test_ask_routes_and_answers(tmp_db):
    import json as _json
    from axp.graph import confidence, store
    store.init()
    db.executescript(confidence.DDL)
    db.execute(
        "INSERT INTO causal_candidates (dims, confidence, confirmations, status, rule_id, updated_at) "
        "VALUES (?,?,?,?,?,?)",
        (_json.dumps({"equipment_id": "OVEN-2"}), 0.88, "[]", "promoted", "RULE-0001", "2026-09-01"))
    c = _client()
    _login(c, "approver")
    r = c.post("/ask", data={"q": "승격된 규칙 목록"})
    assert r.status_code == 200
    assert "RULE-0001" in r.text and "근거" in r.text


def test_promotion_request_and_decide(tmp_db):
    from axp.judge import cards as jcards
    db.executescript(jcards.DDL)
    for _ in range(10):   # 승인율 100% 이력
        db.execute(
            "INSERT INTO judgment_cards (kind, agent, proposal, narrative, values_json, "
            "range_json, evidence_json, alternatives_json, approver, status, created_at) "
            "VALUES ('replenish','a','t','n','[]','{}','[]','[]','x','executed','2026-09-01')")
    c = _client()
    _login(c, "approver")
    r = c.post("/promotions/request",
               data={"kind": "replenish", "amount_cap": "1500", "min_rate": "0.8"})
    assert r.status_code == 303
    row = db.one("SELECT * FROM promotions ORDER BY promo_id DESC LIMIT 1")
    assert row["status"] == "requested"
    r = c.post(f"/promotions/{row['promo_id']}/decide", data={"ok": "1"})
    assert db.one("SELECT status FROM promotions WHERE promo_id=?",
                  (row["promo_id"],))["status"] == "active"


def test_asset_register_requires_steward(tmp_db):
    c = _client()
    _login(c, "approver")
    r = c.post("/assets/register", data={"asset_id": "x", "kind": "dataset",
                                         "location": "/tmp", "note": ""})
    assert r.status_code == 403
    c2 = _client()
    _login(c2, "steward")
    r = c2.post("/assets/register", data={"asset_id": "pos-2026", "kind": "dataset",
                                          "location": "inbox/pos.xlsx", "note": "테스트"})
    assert r.status_code == 303
    from axp.custody import ledger
    assert ledger.latest("pos-2026")["location"] == "inbox/pos.xlsx"


def test_login_lockout_after_failures(tmp_db):
    """P4-2: 실패 5회 → 15분 잠금(423), 존재하지 않는 계정도 동일 동작."""
    c = _client()
    for _ in range(5):
        assert c.post("/login", data={"username": "admin", "password": "bad"}).status_code == 401
    r = c.post("/login", data={"username": "admin", "password": "change-me!"})
    assert r.status_code == 423                     # 올바른 비밀번호도 잠금 중엔 거절
    for _ in range(5):
        c.post("/login", data={"username": "ghost", "password": "bad"})
    assert c.post("/login", data={"username": "ghost", "password": "bad"}).status_code == 423


def test_login_success_resets_counter(tmp_db):
    c = _client()
    for _ in range(3):
        c.post("/login", data={"username": "admin", "password": "bad"})
    assert c.post("/login", data={"username": "admin", "password": "change-me!"}).status_code == 303
    row = db.one("SELECT * FROM axp_login_attempts WHERE username='admin'")
    assert row is None                              # 성공 시 카운터 소거


def test_trial_watermark_shown(tmp_db):
    """P4-2: profile.trial=True면 모든 화면에 '체험판 · 합성 데이터' 고지."""
    import json as _json
    from axp import config as _config
    (_config.DATA / "profile.json").write_text(_json.dumps(
        {"profile": "trial-x", "company": "체험 고객사", "trial": True},
        ensure_ascii=False), encoding="utf-8")
    c = _client()
    _login(c, "admin")
    body = c.get("/inbox").text
    assert "체험판 · 합성 데이터" in body and "체험 고객사" in body
    login_page = c.get("/login").text               # 로그인 화면에도 고지
    assert "체험판 · 합성 데이터" in login_page


def test_upload_pos_daily_via_web(tmp_db):
    """P4-3: 웹 업로드 → POS 어댑터 → 스테이징 + 멱등."""
    c = _client()
    _login(c, "steward")
    csv = ("영업일자,매장명,상품코드,판매수량,판매금액\n"
           "2025-09-01,S-CHORYANG,P-PIE,120,144000\n").encode("cp949")
    r = c.post("/upload", data={"kind": "pos_daily"},
               files={"file": ("정산.csv", csv, "text/csv")})
    assert r.status_code == 200 and "반입 완료" in r.text and "1행" in r.text
    assert db.scalar("SELECT COUNT(*) FROM staging_sales WHERE _source='pos_daily'") == 1
    r2 = c.post("/upload", data={"kind": "pos_daily"},
                files={"file": ("정산.csv", csv, "text/csv")})
    assert "이미 반입" in r2.text                      # sha256 멱등


def test_upload_requires_steward(tmp_db):
    c = _client()
    _login(c, "approver")
    r = c.post("/upload", data={"kind": "pos_daily"},
               files={"file": ("x.csv", b"a,b\n", "text/csv")})
    assert r.status_code == 403


def test_upload_unknown_format_asks_mapping(tmp_db):
    c = _client()
    _login(c, "steward")
    r = c.post("/upload", data={"kind": "pos_daily"},
               files={"file": ("mystery.csv", "colA,colB\n1,2\n".encode(), "text/csv")})
    assert "처음 보는 양식" in r.text


def test_health_and_status_public(tmp_db):
    """P4-4: /health·/status 는 로그인 없이 — 하트비트·상태 공개."""
    c = _client()
    r = c.get("/health")
    assert r.status_code == 200 and r.json()["ok"] is True
    r = c.get("/status")
    assert r.status_code == 200
    assert "서비스 상태" in r.text and "정상" in r.text
    # 민감 정보(계정·수치·회사 데이터) 미노출 — 최소 신호만
    assert "admin" not in r.text and "카드" not in r.text


def test_connect_wizard_requires_admin(tmp_db):
    """P4-6: Odoo 연결 마법사는 admin 전용."""
    c = _client()
    _login(c, "steward")
    assert c.get("/connect").status_code == 403


def test_connect_wizard_rejects_bad_host(tmp_db):
    c = _client()
    _login(c, "admin")
    r = c.post("/connect", data={"host": "127.0.0.1", "port": "1",
                                 "dbname": "x", "user": "x", "password": "x"})
    assert r.status_code == 400 and "접속 실패" in r.text


import pytest as _pytest


@_pytest.mark.skipif(os.environ.get("AXP_DB") != "postgres",
                     reason="PG 백엔드에서만 — 실 PG로 비Odoo DB 검사")
def test_connect_wizard_detects_non_odoo_db(tmp_db):
    """플랫폼 PG(axp)는 Odoo가 아니므로 '검사 중 오류'가 떠야 한다."""
    c = _client()
    _login(c, "admin")
    r = c.post("/connect", data={"host": "127.0.0.1", "port": "5432",
                                 "dbname": "axp", "user": "axp", "password": "axp"})
    assert r.status_code == 400 and "Odoo DB가 맞는지" in r.text


def test_setup_wizard_saves_profile_and_seeds_dictionary(tmp_db):
    """P4-9: 온보딩 설정 저장 → profile.json + 코드 사전 반영."""
    import json as _json
    from axp import config as _config
    c = _client()
    _login(c, "steward")
    r = c.post("/setup", data={
        "company": "행복제과",
        "stores": "S-A=본점=retail\nS-B=공항점",
        "products": "P-1=크림빵\nP-2=단팥빵",
        "aliases": "product,크림 빵,P-1\nstore,본  점,S-A"})
    assert r.status_code == 200 and "저장 완료" in r.text
    prof = _json.loads((_config.DATA / "profile.json").read_text(encoding="utf-8"))
    assert prof["company"] == "행복제과"
    assert prof["store_names"] == {"S-A": "본점", "S-B": "공항점"}
    assert prof["store_channels"] == {"S-A": "retail"}
    assert prof["product_names"]["P-2"] == "단팥빵"
    row = db.one("SELECT standard_code FROM code_dictionary WHERE domain='product' AND alias='크림 빵'")
    assert row and row["standard_code"] == "P-1"
    body = c.get("/inbox").text                     # 회사명이 헤더에 반영
    assert "행복제과" in body


def test_setup_wizard_rejects_bad_lines(tmp_db):
    c = _client()
    _login(c, "steward")
    r = c.post("/setup", data={
        "company": "X", "stores": "잘못된줄", "products": "P-1=크림빵",
        "aliases": "unknown,별칭,CODE"})
    assert r.status_code == 400 and "저장하지 않았습니다" in r.text
    assert "매장 1행" in r.text and "별칭 1행" in r.text


def test_setup_requires_steward(tmp_db):
    c = _client()
    _login(c, "approver")
    assert c.get("/setup").status_code == 403


def test_users_admin_only_and_add_reset_unlock(tmp_db):
    """P4-10: 계정 관리 — admin 전용, 추가→임시 비번 로그인→재발급→잠금 해제."""
    import re as _re
    c = _client()
    _login(c, "steward")
    assert c.get("/users").status_code == 403
    c2 = _client()
    _login(c2, "admin")
    # 추가 — 임시 비밀번호가 화면에 한 번 표시
    r = c2.post("/users/add", data={"username": "worker1", "role": "viewer",
                                    "display": "현장 열람"})
    assert r.status_code == 200 and "계정 생성" in r.text
    pw = _re.search(r"<code>([^<]+)</code>", r.text).group(1)
    c3 = _client()
    assert c3.post("/login", data={"username": "worker1", "password": pw}).status_code == 303
    # 재발급 — 이전 비밀번호 무효 + must_change
    r = c2.post("/users/reset", data={"username": "worker1"})
    new_pw = _re.search(r"<code>([^<]+)</code>", r.text).group(1)
    assert new_pw != pw
    c4 = _client()
    assert c4.post("/login", data={"username": "worker1", "password": pw}).status_code == 401
    assert c4.post("/login", data={"username": "worker1", "password": new_pw}).status_code == 303
    assert db.one("SELECT must_change FROM axp_users WHERE username='worker1'")["must_change"] == 1
    # 잠금 → 관리자 해제 → 즉시 로그인
    for _ in range(5):
        c4.post("/login", data={"username": "worker1", "password": "bad"})
    assert c4.post("/login", data={"username": "worker1", "password": new_pw}).status_code == 423
    c2.post("/users/unlock", data={"username": "worker1"})
    assert c4.post("/login", data={"username": "worker1", "password": new_pw}).status_code == 303


def test_users_add_validates(tmp_db):
    c = _client()
    _login(c, "admin")
    assert c.post("/users/add", data={"username": "한글", "role": "viewer",
                                      "display": "x"}).status_code == 400
    assert c.post("/users/add", data={"username": "admin", "role": "viewer",
                                      "display": "중복"}).status_code == 400


def test_upload_shows_preview_summary(tmp_db):
    """P4-11: 반입 성공 시 기간·매장·상품·수량 미리보기."""
    c = _client()
    _login(c, "steward")
    csv = ("영업일자,매장명,상품코드,판매수량,판매금액\n"
           "2025-09-01,S-A,P-1,100,120000\n"
           "2025-09-02,S-B,P-2,50,60000\n").encode("cp949")
    r = c.post("/upload", data={"kind": "pos_daily"},
               files={"file": ("정산2.csv", csv, "text/csv")})
    assert "반입 미리보기" in r.text
    assert "2025-09-01~2025-09-02" in r.text
    assert "매장 2곳" in r.text and "상품 2종" in r.text and "150" in r.text


def test_runs_admin_only_and_lifecycle(tmp_db, monkeypatch):
    """P4-12: 수동 배치 — admin 전용, 실행→완료 기록, 동시 실행 차단."""
    import time as _time
    from axp import scheduler as _sched
    c = _client()
    _login(c, "steward")
    assert c.get("/runs").status_code == 403
    a = _client()
    _login(a, "admin")
    monkeypatch.setattr(_sched, "run_cycle",
                        lambda d, shadow=False: {"transform": "ok"})
    r = a.post("/runs", data={"run_date": "2025-09-03"})
    assert r.status_code == 200 and "시작" in r.text
    for _ in range(50):                      # 백그라운드 완료 대기
        row = db.one("SELECT * FROM batch_runs WHERE run_id=1")
        if row["status"] != "running":
            break
        _time.sleep(0.1)
    assert row["status"] == "done" and "전 단계 정상" in row["summary"]
    # 실패 요약 기록
    monkeypatch.setattr(_sched, "run_cycle",
                        lambda d, shadow=False: {"transform": "error: X"})
    a.post("/runs", data={"run_date": "2025-09-04"})
    for _ in range(50):
        row = db.one("SELECT * FROM batch_runs WHERE run_id=2")
        if row["status"] != "running":
            break
        _time.sleep(0.1)
    assert row["status"] == "failed" and "transform" in row["summary"]
    # 동시 실행 차단 (running 행 수동 삽입)
    db.execute("INSERT INTO batch_runs (run_date, requested_by, started_at, status) "
               "VALUES ('2025-09-05','x','t','running')")
    assert a.post("/runs", data={"run_date": "2025-09-05"}).status_code == 409
    assert a.post("/runs", data={"run_date": "bad-date"}).status_code in (400, 409)


def test_csrf_required_on_posts(tmp_db):
    """P5-S3: 토큰 없는 POST는 403 — 폼 재생·업로드 경로 포함."""
    c = _client()
    _login(c, "admin")
    r = c.post("/runs", data={"run_date": "2025-09-03"}, no_csrf=True)
    assert r.status_code == 403 and "보안 토큰" in r.text
    r = c.post("/upload", data={"kind": "pos_daily"},
               files={"file": ("x.csv", b"a,b\n1,2\n", "text/csv")}, no_csrf=True)
    assert r.status_code == 403
    # 토큰이 있으면 통과(기존 테스트 전체가 증명하지만 명시적으로 한 번)
    assert c.post("/users/unlock", data={"username": "admin"}).status_code == 200


def test_session_expiry_forces_relogin(tmp_db, monkeypatch):
    """P5-S1: 만료 지난 세션 쿠키는 무효 — 재로그인으로 유도."""
    c = _client()
    _login(c, "admin")
    assert c.get("/inbox").status_code == 200
    # 만료를 과거로 조작한 토큰(서명은 유효) — 거절돼야 한다
    import time as _t
    exp = int(_t.time()) - 10
    body = f"admin|{exp}"
    c.cookies.set("axp_session", f"{body}|{webapp._sign(body)}")
    r = c.get("/inbox")
    assert r.status_code == 303 and r.headers["location"] == "/login"


def test_must_change_redirects_until_password_set(tmp_db):
    """P5-S2: 초기 비밀번호 상태면 /password 외 전부 리다이렉트."""
    c = _client()
    _login(c, "admin", keep_must_change=True)
    r = c.get("/inbox")
    assert r.status_code == 303 and r.headers["location"] == "/password"
    assert c.get("/password").status_code == 200          # 변경 화면은 허용
    r = c.post("/password", data={"new_pw": "새로운비밀번호9!"})
    assert r.status_code in (200, 303)
    assert c.get("/inbox").status_code == 200             # 변경 후 정상


def test_security_headers_present(tmp_db):
    c = _client()
    r = c.get("/login")
    assert r.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert "default-src 'self'" in r.headers["Content-Security-Policy"]
