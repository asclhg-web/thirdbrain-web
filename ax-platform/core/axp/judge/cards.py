"""M6-2 판단 카드 스키마 v1 + 검증기 + 저장.

카드 = {제안, 수치, 구간, 근거 경로, 대안, 승인자, 상태}
카드 3규칙(검증기가 강제):
  ① 수치는 source가 있어야 한다(모델·원장) — LLM 창작 수치 금지
  ② 근거 경로(evidence_path)가 비어 있으면 생성 거부
  ③ 승인 전에는 어떤 값도 실제로 바뀌지 않는다(M7 환류에서만)
"""
from __future__ import annotations

import json

from .. import common, db

STATUS_FLOW = ["proposed", "review", "approved", "rejected", "executed", "feedback"]

DDL = """
CREATE TABLE IF NOT EXISTS judgment_cards (
  card_id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,               -- demand_forecast | replenish | allocation | equip_alert | knowledge
  agent TEXT NOT NULL,
  proposal TEXT NOT NULL,           -- 한 문장 실행 제안
  narrative TEXT DEFAULT '',        -- 조립된 설명 문장(전부 인용 태그 포함)
  values_json TEXT NOT NULL,        -- [{name, value, unit, source}]
  range_json TEXT DEFAULT '{}',     -- {p10, p50, p90} 등
  evidence_json TEXT NOT NULL,      -- 근거 경로 (graph/model/ledger 참조)
  alternatives_json TEXT DEFAULT '[]',
  approver TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'proposed',
  decision_note TEXT DEFAULT '',
  created_at TEXT, decided_at TEXT, decided_by TEXT
);
"""


class CardValidationError(Exception):
    pass


def validate(card: dict) -> None:
    for k in ("kind", "agent", "proposal", "values", "evidence", "approver"):
        if not card.get(k):
            raise CardValidationError(f"카드 필수 필드 비어 있음: {k}")
    for v in card["values"]:
        if not v.get("source"):
            raise CardValidationError(
                f"수치 '{v.get('name')}'에 source 없음 — 모델·원장 값만 인용한다")
        if not isinstance(v.get("value"), (int, float)):
            raise CardValidationError(f"수치 '{v.get('name')}'가 숫자가 아님")
    ev = card["evidence"]
    if not isinstance(ev, (list, dict)) or len(ev) == 0:
        raise CardValidationError("근거 경로 비어 있음 — 카드 생성 거부")


def create(card: dict) -> int:
    """검증 통과 시에만 저장 — 반환: card_id."""
    db.executescript(DDL)
    validate(card)
    with db.conn() as c:
        cur = c.execute(
            "INSERT INTO judgment_cards (kind, agent, proposal, narrative, values_json, "
            "range_json, evidence_json, alternatives_json, approver, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (card["kind"], card["agent"], card["proposal"], card.get("narrative", ""),
             json.dumps(card["values"], ensure_ascii=False),
             json.dumps(card.get("range", {}), ensure_ascii=False),
             json.dumps(card["evidence"], ensure_ascii=False),
             json.dumps(card.get("alternatives", []), ensure_ascii=False),
             card["approver"], common.now_iso()))
        return cur.lastrowid


def get(card_id: int) -> dict:
    db.executescript(DDL)
    row = db.one("SELECT * FROM judgment_cards WHERE card_id=?", (card_id,))
    if row is None:
        raise ValueError(f"카드 {card_id} 없음")
    for k in ("values_json", "range_json", "evidence_json", "alternatives_json"):
        row[k.replace("_json", "")] = json.loads(row.pop(k))
    return row


def listing(status: str | None = None, kind: str | None = None) -> list[dict]:
    db.executescript(DDL)
    sql, params = "SELECT * FROM judgment_cards WHERE 1=1", []
    if status:
        sql += " AND status=?"
        params.append(status)
    if kind:
        sql += " AND kind=?"
        params.append(kind)
    return db.query(sql + " ORDER BY card_id", params)


def set_status(card_id: int, status: str, by: str = "", note: str = "") -> None:
    if status not in STATUS_FLOW:
        raise ValueError(f"알 수 없는 상태 {status}")
    db.execute(
        "UPDATE judgment_cards SET status=?, decided_at=?, decided_by=?, "
        "decision_note=COALESCE(NULLIF(?,'') , decision_note) WHERE card_id=?",
        (status, common.now_iso(), by, note, card_id))
