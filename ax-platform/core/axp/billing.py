"""P6-1 과금 — 구독 상태·청구 이력·미납 잠금 (6단계 실행계획서 6-B).

설계 원칙:
- 인스턴스(테넌트) 하나 = 구독 하나. 결제 대행(PG) 연동 전에는 수납을
  사람이 확인하고 '수납 처리'로 기록한다 — 자동 출금은 6-B 결제 수단
  확정(A4) 이후의 일이며, 이 모듈은 그때 상태 기계를 그대로 재사용한다.
- 잠금은 데이터를 지우지 않는다 — 로그인만 막고(관리자는 예외) 수납
  즉시 원상복구. 원장·백업·복제는 잠금과 무관하게 계속 돈다.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

from . import common, db

DDL = """
CREATE TABLE IF NOT EXISTS axp_subscription (
  sub_id INTEGER PRIMARY KEY CHECK (sub_id = 1),   -- 인스턴스당 1행
  plan TEXT NOT NULL CHECK (plan IN ('trial','standard','pilot')),
  monthly_fee INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'active'
         CHECK (status IN ('active','past_due','locked')),
  started_at TEXT, updated_by TEXT, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS axp_invoices (
  invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
  period TEXT NOT NULL UNIQUE,                     -- 'YYYY-MM' 월 1건
  amount INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'issued'
         CHECK (status IN ('issued','paid','overdue')),
  issued_at TEXT, due_date TEXT, paid_at TEXT, paid_by TEXT
);
"""

GRACE_DAYS = 14        # 발행→납기
LOCK_AFTER_DAYS = 14   # 납기 경과→잠금 (합계 4주 유예)


def init() -> None:
    db.executescript(DDL)


def get() -> dict | None:
    init()
    return db.one("SELECT * FROM axp_subscription WHERE sub_id=1")


def set_plan(plan: str, monthly_fee: int, by: str) -> dict:
    init()
    if plan not in ("trial", "standard", "pilot"):
        raise ValueError(f"알 수 없는 플랜: {plan}")
    now = common.now_iso()
    db.execute(
        "INSERT INTO axp_subscription (sub_id, plan, monthly_fee, status, started_at, updated_by, updated_at) "
        "VALUES (1,?,?,'active',?,?,?) "
        "ON CONFLICT(sub_id) DO UPDATE SET plan=excluded.plan, "
        "monthly_fee=excluded.monthly_fee, updated_by=excluded.updated_by, "
        "updated_at=excluded.updated_at",
        (plan, int(monthly_fee), now, by, now))
    common.alert("info", "billing", f"플랜 설정: {plan} · 월 {monthly_fee:,}원 (by {by})")
    return get()


def issue(period: str | None = None, today: str | None = None) -> dict | None:
    """해당 월 청구 발행 — 멱등(이미 있으면 그대로). trial(0원)은 발행 없음."""
    init()
    sub = get()
    if not sub or sub["monthly_fee"] <= 0:
        return None
    tday = today or date.today().isoformat()
    period = period or tday[:7]
    row = db.one("SELECT * FROM axp_invoices WHERE period=?", (period,))
    if row:
        return row
    due = (date.fromisoformat(tday) + timedelta(days=GRACE_DAYS)).isoformat()
    db.execute(
        "INSERT INTO axp_invoices (period, amount, issued_at, due_date) VALUES (?,?,?,?)",
        (period, sub["monthly_fee"], common.now_iso(), due))
    common.alert("info", "billing", f"청구 발행: {period} · {sub['monthly_fee']:,}원 · 납기 {due}")
    return db.one("SELECT * FROM axp_invoices WHERE period=?", (period,))


def mark_paid(invoice_id: int, by: str) -> None:
    init()
    row = db.one("SELECT * FROM axp_invoices WHERE invoice_id=?", (invoice_id,))
    if not row:
        raise ValueError(f"청구 {invoice_id} 없음")
    db.execute("UPDATE axp_invoices SET status='paid', paid_at=?, paid_by=? WHERE invoice_id=?",
               (common.now_iso(), by, invoice_id))
    if not db.scalar("SELECT COUNT(*) FROM axp_invoices WHERE status='overdue'"):
        db.execute("UPDATE axp_subscription SET status='active' WHERE sub_id=1")
    common.alert("info", "billing", f"수납 처리: 청구 {invoice_id}({row['period']}) by {by}")


def check_overdue(today: str | None = None) -> dict:
    """야간 배치 — 납기 경과 청구를 overdue로, 구독을 past_due/locked로.

    잠금은 납기+LOCK_AFTER_DAYS 경과 시에만(총 4주 유예) — crit 1회."""
    init()
    sub = get()
    if not sub:
        return {"status": None, "overdue": 0}
    tday = today or date.today().isoformat()
    db.execute("UPDATE axp_invoices SET status='overdue' "
               "WHERE status='issued' AND due_date < ?", (tday,))
    overdue = db.query("SELECT * FROM axp_invoices WHERE status='overdue' ORDER BY due_date")
    new_status = "active"
    if overdue:
        lock_at = (date.fromisoformat(overdue[0]["due_date"])
                   + timedelta(days=LOCK_AFTER_DAYS)).isoformat()
        new_status = "locked" if tday >= lock_at else "past_due"
    if new_status != sub["status"]:
        db.execute("UPDATE axp_subscription SET status=? WHERE sub_id=1", (new_status,))
        level = "crit" if new_status == "locked" else ("warn" if new_status == "past_due" else "info")
        label = {"locked": "미납 잠금", "past_due": "납기 경과", "active": "정상 복귀"}[new_status]
        common.alert(level, "billing",
                     f"구독 상태 변경: {sub['status']} → {new_status} ({label}, 미납 {len(overdue)}건)")
    return {"status": new_status, "overdue": len(overdue)}


def unlock(by: str) -> None:
    """관리자 수동 해제 — 수납 확인 후. 미납 청구는 남는다(정직한 이력)."""
    init()
    db.execute("UPDATE axp_subscription SET status='active' WHERE sub_id=1")
    common.alert("info", "billing", f"잠금 해제 by {by}")


def is_locked() -> bool:
    try:
        sub = get()
    except Exception:  # noqa: BLE001 — 과금 미구성 인스턴스는 잠그지 않는다
        return False
    return bool(sub and sub["status"] == "locked")


def invoices(limit: int = 24) -> list[dict]:
    init()
    return db.query("SELECT * FROM axp_invoices ORDER BY period DESC LIMIT ?", (limit,))
