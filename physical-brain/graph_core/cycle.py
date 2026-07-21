"""KG-DMAIC 사이클 엔진 (G04) — 방법론이 소프트웨어가 되는 지점.

Define(목적·CQ·CTQ 등록) → Measure(CQ를 사서에 던져 기준선 실측) →
Analyze(갭 보드) → Improve(지식·데이터 보강은 볼트에서) → Control(재측정·추이).

원칙: '응답 가능'의 판정은 근거(evidence) 기반 — 근거 없는 답은 답이 아니다.
도메인 무지: 질문에 답하는 함수(ask_fn)는 팩이 주입한다.
"""
import json
from datetime import datetime

from graph_core import store

store.register_ddl(
    """
    CREATE TABLE IF NOT EXISTS cycles(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, purpose TEXT,
      phase TEXT DEFAULT 'define', created_at TEXT);
    CREATE TABLE IF NOT EXISTS cycle_cqs(
      id INTEGER PRIMARY KEY AUTOINCREMENT, cycle_id INTEGER, question TEXT,
      answerable INTEGER, evidence_n INTEGER DEFAULT 0, gap_reason TEXT DEFAULT '',
      last_checked TEXT);
    CREATE TABLE IF NOT EXISTS cycle_ctqs(
      id INTEGER PRIMARY KEY AUTOINCREMENT, cycle_id INTEGER, name TEXT,
      baseline TEXT DEFAULT '미측정', target TEXT, current TEXT DEFAULT '',
      measured_at TEXT);
    """
)

# 이미 열린 연결이 있으면 부속 테이블을 즉시 보강 (임포트 순서 무관성)
if store._CONN is not None:
    store.init_tables(store._CONN)

PHASES = ["define", "measure", "analyze", "improve", "control"]


def create_cycle(name: str, purpose: str, cqs: list[str], ctqs: list[dict],
                 now: datetime | None = None) -> int:
    """Define 단계: 헌장 등록. ctqs: [{name, target, baseline?}]"""
    now = now or datetime.now()
    conn = store.get_conn()
    cur = conn.execute("INSERT INTO cycles(name,purpose,phase,created_at) VALUES(?,?,?,?)",
                       (name, purpose, "define", now.isoformat()))
    cid = cur.lastrowid
    for q in cqs:
        q = q.strip()
        if q:
            conn.execute("INSERT INTO cycle_cqs(cycle_id,question) VALUES(?,?)", (cid, q))
    for c in ctqs:
        if c.get("name"):
            conn.execute("INSERT INTO cycle_ctqs(cycle_id,name,baseline,target) VALUES(?,?,?,?)",
                         (cid, c["name"], c.get("baseline", "미측정"), c.get("target", "")))
    conn.commit()
    return cid


def measure(cycle_id: int, ask_fn, now: datetime | None = None) -> dict:
    """Measure 단계: 모든 CQ를 사서에 실측 — 근거 있는 답만 '응답 가능'."""
    now = now or datetime.now()
    conn = store.get_conn()
    rows = conn.execute("SELECT * FROM cycle_cqs WHERE cycle_id=?", (cycle_id,)).fetchall()
    ok = 0
    for r in rows:
        try:
            a = ask_fn(r["question"])
        except Exception as e:
            a = {"intent": "error", "evidence": [], "data": {}, "answer": str(e)}
        evid = a.get("evidence") or []
        data = a.get("data") or {}
        answerable = bool(evid) or (
            a.get("intent") not in ("unknown", "forbidden", "error")
            and any(v not in (None, [], {}, "", 0) for v in data.values()))
        reason = "" if answerable else (
            "금지영역" if a.get("intent") == "forbidden"
            else "지식/데이터 부재" if a.get("intent") in ("unknown", "error")
            else "기록 없음(데이터 부재)")
        conn.execute(
            "UPDATE cycle_cqs SET answerable=?, evidence_n=?, gap_reason=?, last_checked=? WHERE id=?",
            (int(answerable), len(evid), reason, now.isoformat(), r["id"]))
        ok += int(answerable)
    conn.execute("UPDATE cycles SET phase='measure' WHERE id=? AND phase='define'", (cycle_id,))
    conn.commit()
    return {"total": len(rows), "answerable": ok,
            "rate": round(ok / len(rows) * 100) if rows else None}


def board(cycle_id: int) -> dict:
    """갭 보드 — Analyze의 재료. CQ 응답율·갭 목록·CTQ 현황."""
    conn = store.get_conn()
    c = conn.execute("SELECT * FROM cycles WHERE id=?", (cycle_id,)).fetchone()
    if not c:
        return {}
    cqs = [dict(r) for r in conn.execute(
        "SELECT * FROM cycle_cqs WHERE cycle_id=? ORDER BY id", (cycle_id,)).fetchall()]
    ctqs = [dict(r) for r in conn.execute(
        "SELECT * FROM cycle_ctqs WHERE cycle_id=? ORDER BY id", (cycle_id,)).fetchall()]
    measured = [q for q in cqs if q["last_checked"]]
    ok = sum(1 for q in measured if q["answerable"])
    return {"cycle": dict(c), "cqs": cqs, "ctqs": ctqs,
            "cq_rate": round(ok / len(measured) * 100) if measured else None,
            "gaps": [q for q in measured if not q["answerable"]]}


def cycles() -> list[dict]:
    return [dict(r) for r in store.get_conn().execute(
        "SELECT * FROM cycles ORDER BY id DESC").fetchall()]


def set_phase(cycle_id: int, phase: str) -> None:
    assert phase in PHASES, f"unknown phase {phase}"
    conn = store.get_conn()
    conn.execute("UPDATE cycles SET phase=? WHERE id=?", (phase, cycle_id))
    conn.commit()
