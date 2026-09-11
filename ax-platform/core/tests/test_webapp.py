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


def _client():
    return TestClient(webapp.app, follow_redirects=False)


def _login(c, user):
    r = c.post("/login", data={"username": user, "password": "change-me!"})
    assert r.status_code == 303, r.text
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
