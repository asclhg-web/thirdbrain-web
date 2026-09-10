"""M7-3 승급 절차 — 저위험 카드의 자동 실행: 조건 검사 → 신청 → 승인 → 감시 → 강등.

조건(기본): 금액 상한 + 해당 kind 카드의 최근 승인율 기준. 위반 시 자동 강등.
"""
from __future__ import annotations

import json

from .. import common, db

DDL = """
CREATE TABLE IF NOT EXISTS promotions (
  promo_id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,
  amount_cap REAL NOT NULL,
  min_approval_rate REAL NOT NULL,
  status TEXT NOT NULL DEFAULT 'requested'
         CHECK (status IN ('requested','active','denied','demoted')),
  requested_by TEXT, approved_by TEXT,
  requested_at TEXT, decided_at TEXT, demoted_at TEXT, demote_reason TEXT
);
"""


def approval_rate(kind: str, last_n: int = 20) -> float:
    rows = db.query(
        "SELECT status FROM judgment_cards WHERE kind=? AND status IN "
        "('approved','rejected','executed') ORDER BY card_id DESC LIMIT ?",
        (kind, last_n))
    if not rows:
        return 0.0
    ok = sum(1 for r in rows if r["status"] in ("approved", "executed"))
    return ok / len(rows)


def request(kind: str, amount_cap: float, min_approval_rate: float,
            by: str) -> dict:
    """승급 신청 — 조건 자동 검사 후 신청 기록(불충족이면 즉시 반려)."""
    db.executescript(DDL)
    rate = approval_rate(kind)
    ok = rate >= min_approval_rate
    status = "requested" if ok else "denied"
    with db.conn() as c:
        cur = c.execute(
            "INSERT INTO promotions (kind, amount_cap, min_approval_rate, status, "
            "requested_by, requested_at) VALUES (?,?,?,?,?,?)",
            (kind, amount_cap, min_approval_rate, status, by, common.now_iso()))
        pid = cur.lastrowid
    return {"promo_id": pid, "status": status, "current_approval_rate": round(rate, 3),
            "note": "" if ok else f"승인율 {rate:.0%} < 기준 {min_approval_rate:.0%} — 자동 반려"}


def decide(promo_id: int, approver: str, approve: bool) -> dict:
    db.executescript(DDL)
    status = "active" if approve else "denied"
    db.execute("UPDATE promotions SET status=?, approved_by=?, decided_at=? "
               "WHERE promo_id=? AND status='requested'",
               (status, approver, common.now_iso(), promo_id))
    return db.one("SELECT * FROM promotions WHERE promo_id=?", (promo_id,))


def active_for(kind: str) -> dict | None:
    db.executescript(DDL)
    return db.one("SELECT * FROM promotions WHERE kind=? AND status='active'", (kind,))


def can_auto_execute(card: dict) -> bool:
    """카드의 자동 실행 가능 여부 — 활성 승급 + 금액 상한 이내."""
    p = active_for(card["kind"])
    if p is None:
        return False
    amount = max((abs(v["value"]) for v in card.get("values", [])), default=0)
    return amount <= p["amount_cap"]


def monitor_and_demote() -> list[dict]:
    """감시 — 활성 승급의 kind 승인율이 기준 아래로 떨어지면 자동 강등."""
    db.executescript(DDL)
    demoted = []
    for p in db.query("SELECT * FROM promotions WHERE status='active'"):
        rate = approval_rate(p["kind"])
        if rate < p["min_approval_rate"]:
            db.execute("UPDATE promotions SET status='demoted', demoted_at=?, "
                       "demote_reason=? WHERE promo_id=?",
                       (common.now_iso(),
                        f"승인율 {rate:.0%} < 기준 {p['min_approval_rate']:.0%}",
                        p["promo_id"]))
            common.alert("warn", "M7-3",
                         f"자동 실행 강등: {p['kind']} — 승인율 {rate:.0%}")
            demoted.append({"promo_id": p["promo_id"], "kind": p["kind"],
                            "rate": round(rate, 3)})
    return demoted
