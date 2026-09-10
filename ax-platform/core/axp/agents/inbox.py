"""M7-1 HITL 승인함 — 검토·수정·승인/반려, 승인 시에만 환류, 전 건 감사 로그.

prod: Odoo 화면 내장 모듈(같은 테이블). demo: 이 API + CLI/웹.
권한: 승인/반려는 card_approver 역할만(M0-2 분리). 반려 사유는 구조화 —
재학습 재료가 된다.
"""
from __future__ import annotations

import json

from .. import common, db
from ..judge import cards

REJECT_REASONS = ["수치 의문", "근거 부족", "시점 부적절", "현장 사정", "대안 선호", "기타"]

DDL = """
CREATE TABLE IF NOT EXISTS audit_log (
  log_id INTEGER PRIMARY KEY AUTOINCREMENT,
  card_id INTEGER, action TEXT, actor TEXT, role TEXT,
  before_json TEXT, after_json TEXT, note TEXT, at TEXT
);
CREATE TABLE IF NOT EXISTS odoo_params (
  param_key TEXT PRIMARY KEY,     -- 예: forecast_qty:S-MAIN:P-CREAM:2026-08-01..07
  value REAL NOT NULL,
  old_value REAL,
  card_id INTEGER, set_by TEXT, set_at TEXT
);
CREATE TABLE IF NOT EXISTS reject_feedback (
  card_id INTEGER PRIMARY KEY, reason_code TEXT, reason_text TEXT, by_whom TEXT, at TEXT
);
"""


class PermissionError_(Exception):
    pass


def _log(card_id: int, action: str, actor: str, role: str,
         before: dict | None = None, after: dict | None = None, note: str = "") -> None:
    db.executescript(DDL)
    db.execute(
        "INSERT INTO audit_log (card_id, action, actor, role, before_json, after_json, note, at) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (card_id, action, actor, role,
         json.dumps(before or {}, ensure_ascii=False),
         json.dumps(after or {}, ensure_ascii=False), note, common.now_iso()))


def pending(approver: str | None = None) -> list[dict]:
    rows = cards.listing(status="proposed") + cards.listing(status="review")
    if approver:
        rows = [r for r in rows if r["approver"] == approver]
    return rows


def start_review(card_id: int, actor: str, role: str) -> None:
    cards.set_status(card_id, "review", actor)
    _log(card_id, "review", actor, role)


def amend(card_id: int, actor: str, role: str, new_values: dict) -> None:
    """수정 — 승인 전 값 조정(수정 이력은 감사 로그에)."""
    before = cards.get(card_id)
    vals = before["values"]
    for v in vals:
        if v["name"] in new_values:
            v["value"] = new_values[v["name"]]
            v["source"] += " (승인자 수정)"
    db.execute("UPDATE judgment_cards SET values_json=? WHERE card_id=?",
               (json.dumps(vals, ensure_ascii=False), card_id))
    _log(card_id, "amend", actor, role, {"values": before["values"]}, {"values": vals})


def decide(card_id: int, actor: str, role: str, approve: bool,
           reason_code: str = "", reason_text: str = "") -> dict:
    """승인/반려 — card_approver 역할만. 예외 하나: 승급(M7-3)이 활성인 유형의
    상한 이내 카드는 role='auto'로 자동 승인 가능(감사 로그에 승급 근거 명시).
    반려는 사유 필수(구조화)."""
    card = cards.get(card_id)
    if role == "auto":
        from . import promotion
        if not (approve and promotion.can_auto_execute(card)):
            _log(card_id, "decide_denied", actor, role, note="승급 조건 미충족")
            raise PermissionError_("자동 실행 불가 — 활성 승급 없음 또는 상한 초과")
        p = promotion.active_for(card["kind"])
        reason_text = (f"자동 실행(승급 #{p['promo_id']}: 상한 {p['amount_cap']}, "
                       f"승인율 기준 {p['min_approval_rate']:.0%}) " + reason_text)
    elif role != "card_approver":
        _log(card_id, "decide_denied", actor, role, note="권한 없음")
        raise PermissionError_(f"'{role}' 역할은 승인 권한이 없다 — card_approver만")
    if card["status"] not in ("proposed", "review"):
        raise ValueError(f"결정 가능한 상태가 아님: {card['status']}")
    if approve:
        cards.set_status(card_id, "approved", actor)
        _log(card_id, "approve", actor, role, note=reason_text)
        feedback = apply_feedback(card_id, actor)
        return {"card_id": card_id, "status": "approved", "feedback": feedback}
    if not reason_code:
        raise ValueError(f"반려 사유 필수 — {REJECT_REASONS}")
    cards.set_status(card_id, "rejected", actor, note=f"{reason_code}: {reason_text}")
    db.execute("INSERT OR REPLACE INTO reject_feedback VALUES (?,?,?,?,?)",
               (card_id, reason_code, reason_text, actor, common.now_iso()))
    _log(card_id, "reject", actor, role, note=f"{reason_code}: {reason_text}")
    return {"card_id": card_id, "status": "rejected", "reason": reason_code}


def apply_feedback(card_id: int, actor: str) -> dict:
    """환류 — 승인된 카드만 Odoo 파라미터를 쓴다(이전 값 보존, 감사 로그).
    prod: Odoo XML-RPC 어댑터. demo: odoo_params 테이블."""
    db.executescript(DDL)
    card = cards.get(card_id)
    if card["status"] != "approved":
        raise PermissionError_("승인 전 환류 금지 — HITL 기본값")
    written = []
    if card["kind"] == "demand_forecast":
        ev = card["evidence"]
        key = (f"forecast_qty:{ev['store_id']}:{ev['product_id']}:"
               f"{ev['daily'][0]['date_key']}..{ev['daily'][-1]['date_key'][-2:]}")
        val = float(card["range"].get("p50") or card["values"][0]["value"])
        written.append(_set_param(key, val, card_id, actor))
    elif card["kind"] == "replenish":
        pol = card["evidence"]["policy"]
        for k, v in pol.items():
            written.append(_set_param(f"replenish_policy:{k}", float(v), card_id, actor))
    elif card["kind"] == "equip_alert":
        written.append(_set_param(
            f"inspection_flag:{card['evidence'].get('equipment_id','?')}", 1.0,
            card_id, actor))
    elif card["kind"] == "sop_revision":
        written.append(_set_param(
            f"sop_revision:{card['evidence']['sop_id']}:{card['evidence']['rule_key']}",
            1.0, card_id, actor))
    elif card["kind"] == "knowledge":
        from ..graph import confidence
        res = confidence.decide(card["evidence"]["cc_id"], True, actor,
                                f"승인함 카드 {card_id}")
        written.append({"rule": res})
    elif card["kind"] == "production_plan":
        for p in card["evidence"].get("plan", []):
            written.append(_set_param(
                f"prod_plan:{card['evidence']['plan_date']}:{p['product_id']}",
                float(p["qty"]), card_id, actor))
    elif card["kind"] == "allocation":
        for a in card["evidence"].get("allocations", []):
            written.append(_set_param(
                f"alloc_qty:{a['store_id']}:{card['evidence']['product_id']}",
                float(a["qty"]), card_id, actor))
    cards.set_status(card_id, "executed", actor)
    _log(card_id, "feedback", actor, "system", after={"written": written})
    return {"written": written}


def _set_param(key: str, value: float, card_id: int, actor: str) -> dict:
    old = db.scalar("SELECT value FROM odoo_params WHERE param_key=?", (key,))
    db.execute(
        "INSERT INTO odoo_params (param_key, value, old_value, card_id, set_by, set_at) "
        "VALUES (?,?,?,?,?,?) ON CONFLICT(param_key) DO UPDATE SET "
        "old_value=odoo_params.value, value=excluded.value, card_id=excluded.card_id, "
        "set_by=excluded.set_by, set_at=excluded.set_at",
        (key, value, old, card_id, actor, common.now_iso()))
    return {"param": key, "value": value, "old": old}


def audit(card_id: int | None = None) -> list[dict]:
    db.executescript(DDL)
    if card_id:
        return db.query("SELECT * FROM audit_log WHERE card_id=? ORDER BY log_id", (card_id,))
    return db.query("SELECT * FROM audit_log ORDER BY log_id")
