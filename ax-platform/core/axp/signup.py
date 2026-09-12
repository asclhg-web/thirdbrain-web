"""P6-2 체험 신청·발급 — 승인제 기본, 자동 발급은 스위치(6단계 6-B B2).

결정 존중: 초기 승인제는 접수된 결정이다. AXP_AUTO_ISSUE=1 을 명시로
켜기 전에는 신청이 '대기'로만 쌓이고, 발급은 관리자가 화면에서 한다.
자동 발급을 켜도 같은 기록·같은 테넌트 생성 경로를 지나므로 감사 이력은
동일하다. 이메일 발송(SMTP)은 별도 결선 전까지 수동 — 화면·기록에 명시.
"""
from __future__ import annotations

import os
import re
import secrets

from . import common, db

DDL = """
CREATE TABLE IF NOT EXISTS axp_signup_requests (
  req_id INTEGER PRIMARY KEY AUTOINCREMENT,
  company TEXT NOT NULL, email TEXT NOT NULL, contact TEXT DEFAULT '',
  note TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'pending'
         CHECK (status IN ('pending','issued','rejected')),
  tenant_name TEXT, created_at TEXT, decided_by TEXT, decided_at TEXT
);
"""

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
HOURLY_CAP = 10   # 시간당 신규 신청 상한 — 폭주·봇 완충(승인제와 별개)


def init() -> None:
    db.executescript(DDL)


def auto_issue_enabled() -> bool:
    return os.environ.get("AXP_AUTO_ISSUE", "0") == "1"


def _slug(company: str) -> str:
    base = re.sub(r"[^a-z0-9-]", "", company.lower().replace(" ", "-"))[:16]
    return f"trial-{base or 'co'}-{secrets.token_hex(2)}"


def submit(company: str, email: str, contact: str = "", note: str = "") -> dict:
    """신청 접수 — 검증 통과 시 pending 기록(+정원 완충). 발급은 별도."""
    init()
    company = (company or "").strip()
    email = (email or "").strip()
    if not company or len(company) > 60:
        raise ValueError("회사명을 확인해 주세요(60자 이내).")
    if not _EMAIL_RE.match(email):
        raise ValueError("이메일 주소 형식을 확인해 주세요.")
    hour_ago = common.now_iso()[:13]          # 'YYYY-MM-DDTHH' 프리픽스 비교
    n_recent = db.scalar(
        "SELECT COUNT(*) FROM axp_signup_requests WHERE substr(created_at,1,13)=?",
        (hour_ago,)) or 0
    if n_recent >= HOURLY_CAP:
        raise ValueError("신청이 많아 잠시 접수를 쉬고 있습니다 — 잠시 후 다시 시도해 주세요.")
    with db.conn() as c:
        cur = c.execute(
            "INSERT INTO axp_signup_requests (company, email, contact, note, created_at) "
            "VALUES (?,?,?,?,?)",
            (company, email, contact.strip()[:60], note.strip()[:200], common.now_iso()))
        req_id = cur.lastrowid
    common.alert("info", "signup", f"체험 신청 접수 #{req_id}: {company} <{email}>")
    return db.one("SELECT * FROM axp_signup_requests WHERE req_id=?", (req_id,))


def issue(req_id: int, by: str) -> dict:
    """발급 — 테넌트 생성 + 상태 전환. 승인제(관리자)와 자동 발급이 공용."""
    init()
    row = db.one("SELECT * FROM axp_signup_requests WHERE req_id=?", (req_id,))
    if not row or row["status"] != "pending":
        raise ValueError(f"신청 {req_id}는 대기 상태가 아닙니다")
    from . import tenant
    name = _slug(row["company"])
    r = tenant.create(name, company=row["company"])
    db.execute(
        "UPDATE axp_signup_requests SET status='issued', tenant_name=?, decided_by=?, decided_at=? "
        "WHERE req_id=?", (name, by, common.now_iso(), req_id))
    common.alert("info", "signup",
                 f"체험 발급 #{req_id}: {row['company']} → 테넌트 {name} (by {by})")
    return {"request": db.one("SELECT * FROM axp_signup_requests WHERE req_id=?", (req_id,)),
            "tenant": r}


def reject(req_id: int, by: str, reason: str = "") -> None:
    init()
    row = db.one("SELECT * FROM axp_signup_requests WHERE req_id=?", (req_id,))
    if not row or row["status"] != "pending":
        raise ValueError(f"신청 {req_id}는 대기 상태가 아닙니다")
    db.execute(
        "UPDATE axp_signup_requests SET status='rejected', note=note||?, decided_by=?, decided_at=? "
        "WHERE req_id=?", (f" [반려: {reason}]" if reason else "", by, common.now_iso(), req_id))


def pending() -> list[dict]:
    init()
    return db.query(
        "SELECT * FROM axp_signup_requests WHERE status='pending' ORDER BY req_id")
