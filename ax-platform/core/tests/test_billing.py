"""P6-1 과금 — 구독 상태 기계·청구 멱등·미납 잠금·로그인 가드."""
from axp import billing, db


def test_plan_issue_idempotent(tmp_db):
    billing.set_plan("standard", 300000, "tester")
    inv1 = billing.issue(today="2026-10-01")
    inv2 = billing.issue(today="2026-10-15")          # 같은 달 — 멱등
    assert inv1["invoice_id"] == inv2["invoice_id"]
    assert inv1["period"] == "2026-10" and inv1["due_date"] == "2026-10-15"
    assert db.scalar("SELECT COUNT(*) FROM axp_invoices") == 1


def test_trial_never_bills(tmp_db):
    billing.set_plan("trial", 0, "tester")
    assert billing.issue(today="2026-10-01") is None
    assert db.scalar("SELECT COUNT(*) FROM axp_invoices") == 0


def test_overdue_state_machine(tmp_db):
    """발행 → 납기 경과(past_due) → 4주 유예 초과(locked) → 수납(active)."""
    billing.set_plan("standard", 300000, "tester")
    inv = billing.issue(today="2026-10-01")           # 납기 10-15
    assert billing.check_overdue("2026-10-10")["status"] == "active"
    r = billing.check_overdue("2026-10-20")           # 납기 경과
    assert r["status"] == "past_due" and r["overdue"] == 1
    assert not billing.is_locked()
    assert billing.check_overdue("2026-10-29")["status"] == "locked"
    assert billing.is_locked()
    billing.mark_paid(inv["invoice_id"], "tester")    # 수납 → 자동 복구
    assert not billing.is_locked()
    assert billing.get()["status"] == "active"


def test_no_subscription_no_lock(tmp_db):
    assert billing.check_overdue("2026-10-01") == {"status": None, "overdue": 0}
    assert not billing.is_locked()


def test_locked_blocks_non_admin_login(tmp_db):
    from tests.test_webapp import _client, _login
    from axp import webapp
    billing.set_plan("standard", 300000, "tester")
    billing.issue(today="2026-10-01")
    billing.check_overdue("2026-11-01")               # 잠금
    c = _client()
    webapp.ensure_users()
    db.execute("UPDATE axp_users SET must_change=0")
    r = c.post("/login", data={"username": "steward", "password": "change-me!"})
    assert r.status_code == 402 and "미납" in r.text
    r = c.post("/login", data={"username": "admin", "password": "change-me!"})
    assert r.status_code == 303                        # 관리자는 들어와서 해제
    c._user = "admin"
    r = c.post("/billing/unlock")
    assert r.status_code == 303
    assert not billing.is_locked()
    r = c.post("/login", data={"username": "steward", "password": "change-me!"})
    assert r.status_code == 303                        # 해제 후 정상
