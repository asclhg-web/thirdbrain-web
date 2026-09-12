"""M7-1 에이전트 런타임 — 트리거 → 조회 → 모델·그래프 호출 → 카드 → 승인함.

표준 골격: 에이전트는 make_cards(ctx) 하나만 구현한다. 실행 이력·실패
재시도·경보는 런타임이 공통 처리. 그림자 모드: 카드는 만들되 승인 대기만
(자동 실행 승급 검사 안 함).
"""
from __future__ import annotations

import json
import traceback

from .. import common, db

DDL = """
CREATE TABLE IF NOT EXISTS agent_runs (
  run_id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent TEXT NOT NULL, trigger_kind TEXT, run_date TEXT,
  status TEXT, cards_created INTEGER DEFAULT 0, error TEXT, shadow INTEGER DEFAULT 0,
  started_at TEXT, finished_at TEXT
);
"""

_REGISTRY: dict[str, dict] = {}


class NotReady(Exception):
    """P5-N: 신규 사이트 정상 상태 — 입력(모델·점수 테이블)이 아직 없어
    카드를 만들 수 없는 국면. 실패(crit)가 아니라 대기(info)로 다룬다:
    실 Odoo 신규 연결 직후엔 학습할 이력 자체가 없는 것이 정상이며,
    crit 경보는 '고쳐야 할 장애'에만 쓴다(경보 피로 방지)."""


def register(name: str, trigger_kind: str, fn, spec: str = "") -> None:
    """에이전트 등록 — fn(ctx: dict) -> list[card_id]."""
    _REGISTRY[name] = {"trigger": trigger_kind, "fn": fn, "spec": spec}


def registered() -> dict[str, dict]:
    return {k: {"trigger": v["trigger"], "spec": v["spec"]} for k, v in _REGISTRY.items()}


def run_agent(name: str, ctx: dict, shadow: bool = False) -> dict:
    db.executescript(DDL)
    a = _REGISTRY[name]
    with db.conn() as c:
        cur = c.execute(
            "INSERT INTO agent_runs (agent, trigger_kind, run_date, status, shadow, started_at) "
            "VALUES (?,?,?,?,?,?)",
            (name, a["trigger"], ctx.get("run_date", ""), "running", int(shadow),
             common.now_iso()))
        run_id = cur.lastrowid
    try:
        card_ids = a["fn"](dict(ctx, shadow=shadow)) or []
        auto_executed = []
        if not shadow:                     # M7-3 승급: 상한 이내 저위험 카드 자동 실행
            from . import inbox, promotion
            from ..judge import cards as jcards
            for cid in card_ids:
                card = jcards.get(cid)
                if promotion.can_auto_execute(card):
                    inbox.decide(cid, "system(승급)", "auto", True)
                    auto_executed.append(cid)
        db.execute("UPDATE agent_runs SET status='ok', cards_created=?, finished_at=? "
                   "WHERE run_id=?", (len(card_ids), common.now_iso(), run_id))
        return {"run_id": run_id, "agent": name, "cards": card_ids,
                "auto_executed": auto_executed, "ok": True}
    except NotReady as e:
        db.execute("UPDATE agent_runs SET status='waiting', error=?, finished_at=? "
                   "WHERE run_id=?", (str(e), common.now_iso(), run_id))
        common.alert("info", "M7", f"에이전트 {name} 대기: {e}")
        return {"run_id": run_id, "agent": name, "ok": True, "waiting": True,
                "reason": str(e)}
    except Exception as e:  # noqa: BLE001
        err = f"{e}\n{traceback.format_exc(limit=3)}"
        db.execute("UPDATE agent_runs SET status='error', error=?, finished_at=? "
                   "WHERE run_id=?", (err, common.now_iso(), run_id))
        common.alert("crit", "M7", f"에이전트 {name} 실패: {e}")
        return {"run_id": run_id, "agent": name, "ok": False, "error": str(e)}


def run_all(ctx: dict, shadow: bool = False) -> list[dict]:
    return [run_agent(name, ctx, shadow) for name in _REGISTRY]


def history(agent: str | None = None) -> list[dict]:
    db.executescript(DDL)
    if agent:
        return db.query("SELECT * FROM agent_runs WHERE agent=? ORDER BY run_id", (agent,))
    return db.query("SELECT * FROM agent_runs ORDER BY run_id")
