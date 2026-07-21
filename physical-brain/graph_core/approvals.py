"""승인 큐 (G05) — HITL의 코드화: 시스템 값 변경은 사람 승인 없이 실행되지 않는다.

에이전트·어댑터는 propose()로 제안만 할 수 있다. 실행(execute)은
'승인된 제안'에만 허용되며, 이 계약은 테스트로 고정된다.
실행기는 팩이 register_executor(kind, fn)로 주입한다 (Odoo 쓰기, 규칙 활성화 등).
"""
import json
from datetime import datetime

from graph_core import store

store.register_ddl(
    """
    CREATE TABLE IF NOT EXISTS approvals(
      id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT, title TEXT,
      detail TEXT DEFAULT '{}', proposed_by TEXT,
      status TEXT DEFAULT 'pending',   -- pending | approved | rejected
      executed INTEGER DEFAULT 0, result TEXT DEFAULT '',
      created_at TEXT, decided_at TEXT);
    """
)
if store._CONN is not None:
    store.init_tables(store._CONN)

_EXECUTORS: dict[str, callable] = {}


class NotApproved(Exception):
    """승인되지 않은 제안의 실행 시도 — 절대 조용히 지나가지 않는다."""


def register_executor(kind: str, fn) -> None:
    _EXECUTORS[kind] = fn


def propose(kind: str, title: str, detail: dict | None = None,
            proposed_by: str = "agent", now: datetime | None = None) -> int:
    now = now or datetime.now()
    conn = store.get_conn()
    cur = conn.execute(
        "INSERT INTO approvals(kind,title,detail,proposed_by,created_at) VALUES(?,?,?,?,?)",
        (kind, title, json.dumps(detail or {}, ensure_ascii=False), proposed_by, now.isoformat()))
    conn.commit()
    return cur.lastrowid


def pending() -> list[dict]:
    return [dict(r) for r in store.get_conn().execute(
        "SELECT * FROM approvals WHERE status='pending' ORDER BY id").fetchall()]


def history(limit: int = 20) -> list[dict]:
    return [dict(r) for r in store.get_conn().execute(
        "SELECT * FROM approvals WHERE status!='pending' ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]


def decide(approval_id: int, approve: bool, now: datetime | None = None) -> dict:
    """사람의 결정. 승인이면 실행까지 이어진다 — 실행 결과는 기록으로 남는다."""
    now = now or datetime.now()
    conn = store.get_conn()
    row = conn.execute("SELECT * FROM approvals WHERE id=?", (approval_id,)).fetchone()
    if not row or row["status"] != "pending":
        raise ValueError(f"결정 불가: 제안 {approval_id} (없거나 이미 결정됨)")
    status = "approved" if approve else "rejected"
    conn.execute("UPDATE approvals SET status=?, decided_at=? WHERE id=?",
                 (status, now.isoformat(), approval_id))
    conn.commit()
    return execute(approval_id) if approve else {"status": "rejected"}


def execute(approval_id: int) -> dict:
    """승인된 제안만 실행한다. 미승인·기실행은 예외 — HITL 계약의 심장."""
    conn = store.get_conn()
    row = conn.execute("SELECT * FROM approvals WHERE id=?", (approval_id,)).fetchone()
    if not row:
        raise NotApproved(f"제안 {approval_id} 없음")
    if row["status"] != "approved":
        raise NotApproved(f"제안 {approval_id}은(는) 승인되지 않음 (status={row['status']})")
    if row["executed"]:
        raise NotApproved(f"제안 {approval_id}은(는) 이미 실행됨")
    fn = _EXECUTORS.get(row["kind"])
    if fn is None:
        result = f"실행기 없음({row['kind']}) — 기록만 남김"
    else:
        result = str(fn(json.loads(row["detail"])))
    conn.execute("UPDATE approvals SET executed=1, result=? WHERE id=?", (result, approval_id))
    conn.commit()
    return {"status": "approved", "executed": True, "result": result}
