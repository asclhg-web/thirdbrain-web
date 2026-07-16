"""이중 안전망 — 1층: 규칙 임계값(고정 문구, LLM 개입 금지) / 2층: AI 추세 관찰(제안 어조)."""
from datetime import datetime

from graph import store
from server import llm
from server.events import record_event

# 1층 임계값 기본표 (성인 기준 — 개인 기준선은 주치의와 조정)
THRESHOLDS = {
    "bp_sys": {"emergency": 180, "warn": 135},
    "bp_dia": {"emergency": 120, "warn": 85},
    "glucose_spikes": {"warn": 3},
}
EMERGENCY_TEXT = "⚠️ 긴급: {person}의 {label}이(가) {value}로 긴급 기준을 넘었습니다. 지금 병원(또는 119)에 연락하세요."
WARN_TEXT = "주의: {person}의 {label} {value} — 가정 기준({limit})을 넘었어요. 기록해 두었으니 진료 시 보여주세요."
LABELS = {"bp_sys": "수축기 혈압", "bp_dia": "이완기 혈압", "glucose_spikes": "혈당 스파이크"}


def check_measurement(person: str, mtype: str, value: float, now: datetime | None = None) -> dict | None:
    """새 측정값에 대한 1층 검사. 위반 시 이벤트 기록 + 알림 딕셔너리 반환."""
    now = now or datetime.now()
    th = THRESHOLDS.get(mtype)
    if not th:
        return None
    label = LABELS.get(mtype, mtype)
    if "emergency" in th and value >= th["emergency"]:
        text = EMERGENCY_TEXT.format(person=person, label=label, value=value)  # 고정 문구 — AI 금지
        record_event(person, "임계초과", f"{mtype}={value} 긴급", now)
        return {"level": "emergency", "text": text}
    if value >= th["warn"]:
        text = WARN_TEXT.format(person=person, label=label, value=value, limit=th["warn"])
        record_event(person, "임계초과", f"{mtype}={value} 주의", now)
        return {"level": "warn", "text": text}
    return None


def daily_observation(person: str, now: datetime | None = None) -> str:
    """2층: 7일 추세를 관찰 어조로 — 단정 대신 관찰, 처방 대신 제안."""
    now = now or datetime.now()
    hv = [m["value"] for m in store.measurements(person, "hrv", 7, now)]
    sl = [a["value"] for a in store.activities(person, "sleep", 7, now)]
    obs = []
    if len(hv) >= 4 and hv[-1] < (sum(hv) / len(hv)) * 0.85:
        obs.append("HRV가 주 평균보다 낮아지고 있어요 — 오늘은 일정을 가볍게 가보는 건 어떨까요?")
    if sl and min(sl) < 5.5:
        obs.append(f"이번 주 가장 짧은 잠이 {min(sl)}시간이었어요. 오늘은 조금 일찍 쉬어요.")
    if not obs:
        obs.append("이번 주 흐름은 안정적이에요. 좋은 리듬입니다!")
    fb = " ".join(obs)
    return llm.compose(llm.LIBRARIAN_SYSTEM,
                       f"다음 관찰을 격려 어조의 한 문장으로 다듬어줘(단정·진단 금지): {fb}", fallback=fb)
