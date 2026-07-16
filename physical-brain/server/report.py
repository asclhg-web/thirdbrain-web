"""주간 리포트 — 일요일 저녁, 사람별 + 보호자 공유 버전('전화할 거리' 포함)."""
from datetime import datetime

from graph import store
from server import llm
from server.events import adherence, record_event


def weekly_report(person: str, now: datetime | None = None) -> str:
    now = now or datetime.now()
    ad = adherence(person, 7, now)
    bp = [m["value"] for m in store.measurements(person, "bp_sys", 7, now)]
    bp_prev = [m["value"] for m in store.measurements(person, "bp_sys", 14, now)]
    walk = sum(a["value"] for a in store.activities(person, "walk", 7, now))
    sleep = [a["value"] for a in store.activities(person, "sleep", 7, now)]
    spikes = sum(m["value"] for m in store.measurements(person, "glucose_spikes", 7, now))

    lines = [f"📊 {person}님의 주간 리포트 ({now.date().isoformat()} 기준)"]
    if ad["rate"] is not None:
        lines.append(f"복약 준수율 {ad['rate']}% (완료 {ad['done']} / 미확인 {ad['unconfirmed']} / 누락 {ad['missed']})")
    if bp:
        avg = round(sum(bp) / len(bp), 1)
        prev = round(sum(bp_prev) / len(bp_prev), 1) if bp_prev else avg
        lines.append(f"아침·저녁 수축기 평균 {avg} mmHg (전 2주 평균 {prev})")
    if sleep:
        lines.append(f"수면 평균 {round(sum(sleep)/len(sleep),1)}h · 최단 {min(sleep)}h")
    lines.append(f"걷기 누적 {int(walk):,}보 · 혈당 스파이크 {int(spikes)}회")
    obs = llm.compose(llm.LIBRARIAN_SYSTEM,
                      "다음 주간 수치를 보고 격려 어조의 관찰 3줄을 써줘(진단·처방 금지): " + " / ".join(lines),
                      fallback="이번 주도 기록을 이어가셨어요. 다음 주에는 빠진 날 하루만 줄여봐요. 꾸준함이 답입니다.")
    text = "\n".join(lines) + "\n" + obs
    record_event(person, "주간리포트", text[:120], now)
    return text


def guardian_version(person: str, now: datetime | None = None) -> str:
    base = weekly_report(person, now)
    walk = sum(a["value"] for a in store.activities(person, "walk", 7, now))
    hook = (f"\n💬 전화할 거리: 이번 주 {person}님이 {int(walk):,}보를 걸으셨어요 — 칭찬 전화 어떠세요?")
    return base + hook
