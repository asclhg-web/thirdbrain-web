"""아침 브리핑 — 모든 수치는 그래프 조회값만 사용."""
from datetime import datetime

from graph import store
from server import safety
from server.events import record_event
from server.tasks_today import expand_today, today


def morning_briefing(person: str, now: datetime | None = None) -> str:
    now = now or datetime.now()
    expand_today(now)
    parts = [f"좋은 아침입니다, {person}님. ☀️"]

    sleep = store.activities(person, "sleep", 1, now)
    if sleep:
        parts.append(f"어젯밤 수면은 {sleep[-1]['value']}시간이에요.")
    rhr = store.measurements(person, "rhr", 1, now)
    if rhr:
        week = [m["value"] for m in store.measurements(person, "rhr", 7, now)]
        base = round(sum(week) / len(week), 1)
        diff = round(rhr[-1]["value"] - base, 1)
        parts.append(f"기상 심박 {rhr[-1]['value']}bpm (7일 평균 {base} 대비 {'+' if diff >= 0 else ''}{diff}).")
    bp = store.measurements(person, "bp_sys", 1, now)
    if bp:
        dia = store.measurements(person, "bp_dia", 1, now)
        parts.append(f"아침 혈압 {bp[-1]['value']}/{dia[-1]['value'] if dia else '?'} mmHg.")
    else:
        parts.append("아침 혈압은 아직 측정 전이에요 — 약 드시기 전에 재실까요?")

    meds = [t for t in today(now) if t["person"] == person]
    if meds:
        med_lines = [f"{t['time']} {t['med']}" + (f" ({t['condition']})" if t["condition"] else "")
                     + (f" ⚠{t['caution']}" if t["caution"] else "") for t in meds]
        parts.append("오늘의 약: " + " / ".join(med_lines))
    parts.append(safety.daily_observation(person, now))

    text = " ".join(parts)
    record_event(person, "브리핑", text[:120], now)
    return text
