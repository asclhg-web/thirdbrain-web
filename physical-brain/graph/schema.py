"""서드브레인 표준 개인 온톨로지 v1 — 노드 7종, 관계 6종."""
from dataclasses import dataclass, field

NODE_TYPES = ["Person", "Medication", "Regimen", "Measurement", "Activity", "Event", "Place"]
REL_TYPES = ["TAKES", "HAS_RULE", "MEASURED", "PERFORMED", "OCCURRED", "RELATES_TO"]

# 관계의 (시작노드, 끝노드) 규약 — RELATES_TO 는 자유
REL_RULES = {
    "TAKES": ("Person", "Medication"),
    "HAS_RULE": ("Medication", "Regimen"),
    "MEASURED": ("Person", "Measurement"),
    "PERFORMED": ("Person", "Activity"),
    "OCCURRED": ("Person", "Event"),
}


@dataclass
class Person:
    name: str  # 필수


@dataclass
class Medication:
    name: str
    treats: str = ""       # 무엇을 위한 약인가 (설명 목적 — 진단 아님)
    caution: str = ""


@dataclass
class Regimen:
    time: str              # "07:00"
    condition: str = ""    # "식전 30분"
    caution: str = ""      # "자몽주스 금지"


@dataclass
class Measurement:
    type: str              # bp_sys|bp_dia|rhr|hrv|glucose|sleep_hours|steps
    value: float
    unit: str
    measured_at: str       # ISO8601


@dataclass
class Activity:
    kind: str              # walk|sleep|meditation
    value: float = 0
    unit: str = ""
    at: str = ""


@dataclass
class Event:
    kind: str              # 복약완료|복약미확인|알림발송|임계초과|결측감지|브리핑|하루마감
    at: str = ""
    payload: str = ""


@dataclass
class Place:
    name: str
    x: float = 0
    y: float = 0
    theta: float = 0


def validate_edge(rel: str, src_type: str, dst_type: str) -> bool:
    if rel == "RELATES_TO":
        return True
    rule = REL_RULES.get(rel)
    return bool(rule) and rule == (src_type, dst_type)
