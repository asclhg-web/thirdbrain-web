"""오늘의 작업 목록 — 그래프의 복약규칙을 오늘의 TaskInstance로 전개.

상태 전이: pending → announced → confirmed | unconfirmed
('미확인은 미확인으로': 20분 무응답 → 1회 재알림 → unconfirmed 이벤트)
"""
from datetime import datetime, timedelta

from graph import store
from server.events import record_event

REMIND_AFTER_MIN = 20


def expand_today(now: datetime) -> int:
    """규칙 → 오늘 날짜 태스크 생성(멱등). 지식을 고치면 다음 전개에 반영된다."""
    conn = store.get_conn()
    date = now.date().isoformat()
    created = 0
    for person in [p["props"]["name"] for p in store.nodes_by_type("Person")]:
        for r in store.regimens_for(person):
            cur = conn.execute(
                "INSERT OR IGNORE INTO tasks(date,person,med,time,condition,caution) VALUES(?,?,?,?,?,?)",
                (date, person, r["med"], r.get("time", ""), r.get("condition", ""), r.get("caution", "")))
            created += cur.rowcount
    conn.commit()
    return created


def today(now: datetime) -> list[dict]:
    rows = store.get_conn().execute(
        "SELECT * FROM tasks WHERE date=? ORDER BY time", (now.date().isoformat(),)).fetchall()
    return [dict(r) for r in rows]


def tick(now: datetime) -> list[dict]:
    """스케줄 심장박동: 시간 도래 태스크 announce, 무응답 재알림/미확인 처리.
    반환: 이번 틱에 발생한 액션 목록(알림 발송용)."""
    conn = store.get_conn()
    actions = []
    for t in today(now):
        due = datetime.fromisoformat(f"{t['date']}T{t['time']}:00") if t["time"] else None
        if t["status"] == "pending" and due and now >= due:
            conn.execute("UPDATE tasks SET status='announced', announced_at=? WHERE id=?",
                         (now.isoformat(), t["id"]))
            actions.append({"type": "announce", "task": t})
        elif t["status"] == "announced":
            announced = datetime.fromisoformat(t["announced_at"])
            waited = (now - announced).total_seconds() / 60
            if waited >= REMIND_AFTER_MIN and not t["reminded"]:
                conn.execute("UPDATE tasks SET reminded=1 WHERE id=?", (t["id"],))
                actions.append({"type": "remind", "task": t})
            elif waited >= REMIND_AFTER_MIN * 2 and t["reminded"]:
                conn.execute("UPDATE tasks SET status='unconfirmed' WHERE id=?", (t["id"],))
                record_event(t["person"], "복약미확인", f"{t['med']} {t['time']}", now)
                actions.append({"type": "unconfirmed", "task": t})
    conn.commit()
    return actions


def confirm(person: str, now: datetime, task_id: int | None = None) -> dict | None:
    """'먹었어' — 지정 태스크 또는 가장 최근 announced 태스크를 확인 처리."""
    conn = store.get_conn()
    if task_id:
        row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM tasks WHERE date=? AND person=? AND status='announced' "
            "ORDER BY announced_at DESC LIMIT 1", (now.date().isoformat(), person)).fetchone()
    if not row:
        return None
    conn.execute("UPDATE tasks SET status='confirmed' WHERE id=?", (row["id"],))
    conn.commit()
    record_event(row["person"], "복약완료", f"{row['med']} {row['time']}", now)  # 이벤트는 태스크 소유자에게
    return dict(row)
