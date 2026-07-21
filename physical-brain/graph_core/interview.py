"""암묵지 인터뷰 (G11) — PTGDA 경량판.

원리(JEDAIX 차용): 그래프의 끊긴 곳(갭)을 질문으로 바꿔 사람에게 묻고,
확인(confirm)이 누적되어 임계를 넘으면 '가설'이 '확정'으로 입자화된다.
확정된 가설은 스스로 실행되지 않는다 — 승인 큐(G05)에 제안될 뿐이다 (HITL).

갭 발견자는 팩이 주입한다: register_gap_finder(fn) → [{id, question, kind, hypothesis}]
"""
import json
from datetime import datetime

from graph_core import approvals, store

CONFIRM_MIN = 2
CONFIRM_RATE = 0.7

store.register_ddl(
    """
    CREATE TABLE IF NOT EXISTS interview_seeds(
      id TEXT PRIMARY KEY, kind TEXT, question TEXT, hypothesis TEXT DEFAULT '{}',
      confirm INTEGER DEFAULT 0, total INTEGER DEFAULT 0,
      status TEXT DEFAULT 'wave',   -- wave | confirmed | refuted
      approval_id INTEGER, last_at TEXT);
    """
)
if store._CONN is not None:
    store.init_tables(store._CONN)

_GAP_FINDERS: list = []


def register_gap_finder(fn) -> None:
    if fn not in _GAP_FINDERS:
        _GAP_FINDERS.append(fn)


def scan(now: datetime | None = None) -> int:
    """갭 스캔 → 새 시드 등록(멱등). 이미 판정 난 시드는 다시 만들지 않는다."""
    now = now or datetime.now()
    conn = store.get_conn()
    new = 0
    for finder in _GAP_FINDERS:
        for g in finder():
            row = conn.execute("SELECT id FROM interview_seeds WHERE id=?", (g["id"],)).fetchone()
            if row:
                continue
            conn.execute(
                "INSERT INTO interview_seeds(id,kind,question,hypothesis,last_at) VALUES(?,?,?,?,?)",
                (g["id"], g["kind"], g["question"],
                 json.dumps(g.get("hypothesis", {}), ensure_ascii=False), now.isoformat()))
            new += 1
    conn.commit()
    return new


def due(n: int = 5) -> list[dict]:
    """물어볼 질문 — 아직 파동(wave) 상태인 시드, 오래된 것부터."""
    rows = store.get_conn().execute(
        "SELECT * FROM interview_seeds WHERE status='wave' ORDER BY last_at LIMIT ?", (n,)).fetchall()
    return [dict(r) for r in rows]


def answer(seed_id: str, response: str, now: datetime | None = None) -> dict:
    """응답 누적: yes(확인)/no(반박)/skip(모름 — 판정에 안 씀).
    확정되는 순간 승인 큐에 제안이 올라간다 — 실행은 여전히 사람의 몫."""
    now = now or datetime.now()
    conn = store.get_conn()
    row = conn.execute("SELECT * FROM interview_seeds WHERE id=?", (seed_id,)).fetchone()
    if not row or row["status"] != "wave":
        raise ValueError(f"응답 불가 시드: {seed_id}")
    confirm, total = row["confirm"], row["total"]
    if response == "yes":
        confirm, total = confirm + 1, total + 1
    elif response == "no":
        total = total + 1
    status, approval_id = "wave", row["approval_id"]
    if total >= CONFIRM_MIN:
        rate = confirm / total
        if confirm >= CONFIRM_MIN and rate >= CONFIRM_RATE:
            status = "confirmed"
            hyp = json.loads(row["hypothesis"])
            approval_id = approvals.propose(
                hyp.get("action", "graph_change"),
                hyp.get("title", row["question"]), hyp,
                proposed_by="암묵지인터뷰", now=now)
        elif (total - confirm) >= CONFIRM_MIN:
            status = "refuted"
    conn.execute("UPDATE interview_seeds SET confirm=?, total=?, status=?, approval_id=?, last_at=? "
                 "WHERE id=?", (confirm, total, status, approval_id, now.isoformat(), seed_id))
    conn.commit()
    return {"id": seed_id, "confirm": confirm, "total": total,
            "status": status, "approval_id": approval_id}
