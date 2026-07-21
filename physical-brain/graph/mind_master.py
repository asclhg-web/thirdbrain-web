"""마음 마스터 1단계 (G08-M) — 감정의 명시적 기록.

유산 헌장: "기술은 나중에라도 만들 수 있지만, 오늘의 마음은 오늘만 기록할 수 있다."
1단계는 정직하게 '기록'만 한다 — 해석·진단은 하지 않는다(AI 4대 금지).
2단계(수면·HRV 간접 신호 상관)·3단계(EEG)는 로드맵.
"""
from datetime import datetime

from graph import store
from server.events import record_event

MOODS = ["기쁨", "평온", "보통", "불안", "힘듦"]


def record_mood(person: str, mood: str, memo: str = "", now: datetime | None = None) -> dict:
    assert mood in MOODS, f"unknown mood {mood}"
    now = now or datetime.now()
    payload = mood + (f": {memo.strip()}" if memo.strip() else "")
    record_event(person, "마음", payload, now)
    return {"mood": mood, "memo": memo, "at": now.isoformat()}


def week_moods(person: str, now: datetime | None = None) -> dict:
    """최근 7일 감정 분포 + 마지막 기록 — 주간 리포트·홈 카드 재료."""
    now = now or datetime.now()
    evs = store.events(person, 7, "마음", now)
    counts = {m: 0 for m in MOODS}
    for e in evs:
        tag = e["payload"].split(":", 1)[0].strip()
        if tag in counts:
            counts[tag] += 1
    return {"counts": counts, "n": len(evs),
            "last": evs[-1] if evs else None}


def recorded_recently(person: str, now: datetime | None = None) -> bool:
    now = now or datetime.now()
    return bool(store.events(person, 1, "마음", now))
