"""몸 마스터 (G08) — 측정 유형 사전: ERP의 품목 마스터에 해당.

기본 유형은 코드가 제공하고, 사용자는 볼트 노트(type: measure)로
새 유형을 추가하거나 임계값을 조정한다 — 코드 수정 없이 (진실의 원본은 볼트).

노트 예시:
---
type: measure
name: 혈당
key: glucose
unit: mg/dL
warn: 180
emergency: 300
---
"""
from graph import store

DEFAULTS = [
    {"key": "bp_sys", "label": "수축기 혈압", "unit": "mmHg", "warn": 135, "emergency": 180, "chart": True},
    {"key": "bp_dia", "label": "이완기 혈압", "unit": "mmHg", "warn": 85, "emergency": 120, "chart": True},
    {"key": "rhr", "label": "안정 심박", "unit": "bpm", "chart": True},
    {"key": "hrv", "label": "HRV", "unit": "ms", "chart": True},
    {"key": "glucose_spikes", "label": "혈당 스파이크", "unit": "회", "warn": 3, "chart": True},
    {"key": "spo2", "label": "산소포화도", "unit": "%", "chart": True},   # H01 — 낮을수록 나쁨: 임계는 추이 확인 후 볼트로
    {"key": "stress", "label": "스트레스", "unit": "점", "chart": True},  # H01 — 해석 금지, 추이만
    {"key": "weight", "label": "체중", "unit": "kg", "chart": True},      # H02 — 임계 없음(추이가 전부)
]


def measure_types() -> dict[str, dict]:
    """기본 사전 + 볼트 정의(MeasureType 노드) 병합 — 볼트가 기본값을 덮는다."""
    out = {d["key"]: dict(d) for d in DEFAULTS}
    for n in store.nodes_by_type("MeasureType"):
        p = n["props"]
        key = str(p.get("key") or "").strip()
        if not key:
            continue
        mt = out.get(key, {"key": key, "chart": True})
        mt["label"] = str(p.get("name", mt.get("label", key)))
        if p.get("unit"):
            mt["unit"] = str(p["unit"])
        for f in ("warn", "emergency"):
            if p.get(f) not in (None, ""):
                mt[f] = float(p[f])
        if str(p.get("chart", "")).lower() in ("false", "0", "no"):
            mt["chart"] = False
        out[key] = mt
    return out


def chart_types() -> list[tuple[str, str, str]]:
    """신호 페이지용 (key, label, unit) 목록."""
    return [(k, m.get("label", k), m.get("unit", ""))
            for k, m in measure_types().items() if m.get("chart", True)]
