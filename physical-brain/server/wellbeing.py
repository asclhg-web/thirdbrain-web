"""웰빙 주간 카드 (H03) — 결과(몸)와 습관(선행)을 한 장에.

원칙: 합성 '웰빙 점수'는 만들지 않는다 — 단위가 다른 진실을 하나의 숫자로
뭉개면 거짓이 된다. 각 지표를 각 단위로 나란히 보여주고,
상관은 사람이 본다 (n=1에서 인과 단정 금지).
"""
from datetime import datetime

from graph import store
from server.events import adherence


def _avg(vals: list[float], nd: int = 1) -> float | None:
    return round(sum(vals) / len(vals), nd) if vals else None


def week_card(person: str, now: datetime | None = None) -> dict:
    now = now or datetime.now()

    # ── 결과 지표 (몸) ──
    def m_avg(mtype):
        return _avg([m["value"] for m in store.measurements(person, mtype, 7, now)])

    weights = [m["value"] for m in store.measurements(person, "weight", 7, now)]
    body = {
        "bp": (m_avg("bp_sys"), m_avg("bp_dia")),
        "sleep_avg": _avg([a["value"] for a in store.activities(person, "sleep", 7, now)]),
        "walk_avg": _avg([a["value"] for a in store.activities(person, "walk", 7, now)], 0),
        "stress": m_avg("stress"), "spo2": m_avg("spo2"),
        "weight": weights[-1] if weights else None,
    }

    # ── 습관 지표 (선행) ──
    since = now.toordinal() - 7
    learn_checks = 0
    for _r, c in store.neighbors(store.person_id(person), "MASTERS"):
        e = store.get_edge(store.person_id(person), "MASTERS", c["id"]) or {}
        last = e.get("last_at", "")
        try:
            if last and datetime.fromisoformat(last).toordinal() > since:
                learn_checks += 1
        except ValueError:
            pass
    from graph.work_master import weekly_done
    mind_days = len({e["at"][:10] for e in store.events(person, 7, "마음", now)})
    habits = {
        "adherence": adherence(person, 7, now).get("rate"),
        "learn_checks": learn_checks,
        "tasks_done": weekly_done(person, now),
        "mind_days": mind_days,
    }
    return {"body": body, "habits": habits}
