"""P6-2 체험 신청·발급 — 승인제 기본·자동 발급 스위치·허니팟·검증."""
import pytest

from axp import db, signup
from tests.test_webapp import _client, _login


def test_submit_validates(tmp_db):
    with pytest.raises(ValueError):
        signup.submit("", "a@b.co")
    with pytest.raises(ValueError):
        signup.submit("회사", "not-an-email")
    row = signup.submit("테스트제과", "ceo@test.co", note="POS 씁니다")
    assert row["status"] == "pending"


def test_default_is_approval_mode(tmp_db, monkeypatch):
    """스위치 없이는 접수만 — 테넌트 생성이 호출되지 않는다(승인제 결정 존중)."""
    monkeypatch.delenv("AXP_AUTO_ISSUE", raising=False)
    c = _client()
    r = c.post("/signup", data={"company": "테스트제과", "email": "a@b.co",
                                "contact": "", "note": "", "website": ""})
    assert r.status_code == 200 and "접수되었습니다" in r.text
    assert db.scalar("SELECT COUNT(*) FROM axp_signup_requests WHERE status='pending'") == 1


def test_honeypot_drops_silently(tmp_db):
    signup.init()
    c = _client()
    r = c.post("/signup", data={"company": "봇", "email": "bot@x.co",
                                "website": "http://spam"})
    assert r.status_code == 200 and "접수되었습니다" in r.text
    assert db.scalar("SELECT COUNT(*) FROM axp_signup_requests") == 0


def test_auto_issue_switch(tmp_db, monkeypatch):
    """AXP_AUTO_ISSUE=1 — 같은 경로로 테넌트가 즉시 발급된다(기록 동일)."""
    monkeypatch.setenv("AXP_AUTO_ISSUE", "1")
    made = {}

    def fake_create(name, company=None, template=None, trial=True):
        made["name"], made["company"] = name, company
        cred = tmp_db / "cred.txt"
        cred.write_text("admin: pw123", encoding="utf-8")
        return {"data_dir": str(tmp_db), "credentials_file": str(cred)}

    from axp import tenant
    monkeypatch.setattr(tenant, "create", fake_create)
    c = _client()
    r = c.post("/signup", data={"company": "자동제과", "email": "auto@b.co",
                                "contact": "", "note": "", "website": ""})
    assert r.status_code == 200 and "발급되었습니다" in r.text and "pw123" in r.text
    assert made["company"] == "자동제과" and made["name"].startswith("trial-")
    assert db.scalar(
        "SELECT status FROM axp_signup_requests ORDER BY req_id DESC LIMIT 1") == "issued"


def test_admin_issue_and_reject(tmp_db, monkeypatch):
    from axp import tenant
    monkeypatch.setattr(tenant, "create", lambda name, company=None, template=None, trial=True: {
        "data_dir": "x", "credentials_file": "y"})
    r1 = signup.submit("갑제과", "a@a.co")
    r2 = signup.submit("을제과", "b@b.co")
    c = _client()
    _login(c, "admin")
    assert "대기 2건" in c.get("/signups").text
    resp = c.post("/signups/issue", data={"req_id": str(r1["req_id"])})
    assert "발급 완료" in resp.text
    c.post("/signups/reject", data={"req_id": str(r2["req_id"])})
    assert db.scalar("SELECT COUNT(*) FROM axp_signup_requests WHERE status='pending'") == 0
    with pytest.raises(ValueError):                    # 재발급 불가(대기 아님)
        signup.issue(r1["req_id"], "again")
