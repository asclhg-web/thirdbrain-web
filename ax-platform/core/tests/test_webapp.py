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
