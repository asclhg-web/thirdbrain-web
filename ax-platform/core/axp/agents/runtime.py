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
        db.execute("UPDATE agent_runs SET status='ok', cards_created=?, finished_at=? "
                   "WHERE run_id=?", (len(card_ids), common.now_iso(), run_id))
        return {"run_id": run_id, "agent": name, "cards": card_ids, "ok": True}
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
