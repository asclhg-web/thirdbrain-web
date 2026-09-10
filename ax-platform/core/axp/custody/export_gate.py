"""반출 게이트 (M0-3) — 신청 → 승인 → 실행 → 로그.

원칙: 승인 없는 반출은 실행되지 않는다. 승인은 사람의 행위이며 여기 기록된다.
prod에서는 n8n 워크플로가 이 테이블을 공유한다(같은 스키마).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from urllib.parse import urlparse

from .. import config, db

DDL = """
CREATE TABLE IF NOT EXISTS export_requests (
  req_id      INTEGER PRIMARY KEY AUTOINCREMENT,
  what        TEXT NOT NULL,          -- 무엇을 (설명 + 내용 해시)
  dest        TEXT NOT NULL,          -- 어디로 (호스트/URL)
  why         TEXT NOT NULL,          -- 왜
  requester   TEXT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'requested'
              CHECK (status IN ('requested','approved','denied','executed')),
  approver    TEXT,
  payload_sha TEXT NOT NULL,
  created_at  TEXT NOT NULL,
  decided_at  TEXT,
  executed_at TEXT
);
"""


class ExportDenied(Exception):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init() -> None:
    db.executescript(DDL)


def request(what: str, dest: str, why: str, requester: str, payload: str) -> int:
    """반출 신청. 반환된 req_id로 승인 후 execute()가 가능해진다."""
    init()
    sha = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    with db.conn() as c:
        cur = c.execute(
            "INSERT INTO export_requests (what, dest, why, requester, payload_sha, created_at) "
            "VALUES (?,?,?,?,?,?)",
            (what, dest, why, requester, sha, _now()),
        )
        return cur.lastrowid


def decide(req_id: int, approver: str, approve: bool) -> dict:
    """승인/거부 — 사람의 결정만 이 함수를 불러야 한다(승인자 이름 필수)."""
    init()
    status = "approved" if approve else "denied"
    db.execute(
        "UPDATE export_requests SET status=?, approver=?, decided_at=? "
        "WHERE req_id=? AND status='requested'",
        (status, approver, _now(), req_id),
    )
    row = db.one("SELECT * FROM export_requests WHERE req_id=?", (req_id,))
    if row is None:
        raise ValueError(f"no such request {req_id}")
    return row


def check_and_mark_executed(req_id: int, payload: str, dest: str) -> dict:
    """실행 직전 최종 검문 — 승인 상태·내용 해시·허용 호스트를 모두 확인한다."""
    init()
    row = db.one("SELECT * FROM export_requests WHERE req_id=?", (req_id,))
    if row is None:
        raise ExportDenied(f"반출 신청 {req_id} 없음")
    if row["status"] != "approved":
        raise ExportDenied(f"반출 {req_id} 미승인 상태({row['status']}) — 실행 불가")
    sha = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    if sha != row["payload_sha"]:
        raise ExportDenied(f"반출 {req_id} 내용이 승인본과 다름 — 재신청 필요")
    host = urlparse(dest if "//" in dest else f"//{dest}").hostname or dest
    if config.EXPORT_ALLOWED_HOSTS and host not in config.EXPORT_ALLOWED_HOSTS:
        raise ExportDenied(f"허용 목록에 없는 목적지 {host}")
    db.execute(
        "UPDATE export_requests SET status='executed', executed_at=? WHERE req_id=?",
        (_now(), req_id),
    )
    return db.one("SELECT * FROM export_requests WHERE req_id=?", (req_id,))


def audit_log() -> list[dict]:
    init()
    return db.query("SELECT * FROM export_requests ORDER BY req_id")


def reconcile() -> dict:
    """수용 기준(커스터디): 반출 로그-승인 일치 검사."""
    init()
    bad = db.query(
        "SELECT req_id FROM export_requests WHERE status='executed' AND approver IS NULL"
    )
    return {"executed_without_approver": [r["req_id"] for r in bad], "ok": not bad}


def summary_json() -> str:
    return json.dumps(audit_log(), ensure_ascii=False, indent=2)
