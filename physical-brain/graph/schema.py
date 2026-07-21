"""서드브레인 표준 개인 온톨로지 v2 — 노드 9종, 관계 9종 (KG-DMAIC v2 삼각 모델).

v2 추가: Skill(배움 주제)·Project(개인 프로젝트) 노드,
LEARNS·WORKS_ON·CONTRIBUTES_TO 관계 — 한 Activity가 여러 영역(몸·학습·프로젝트)에
동시 기여하는 '일석삼조 활동'을 그래프로 표현한다.
"""
from dataclasses import dataclass, field

NODE_TYPES = ["Person", "Medication", "Regimen", "Measurement", "Activity", "Event", "Place",
              "Skill", "Project", "MeasureType",
              "Subject", "Topic", "Concept", "Source",   # G08-L 학습 마스터 (+출처)
              "Objective", "Task", "Deliverable"]        # G08-W 일 마스터 (1인 밸류체인)
REL_TYPES = ["TAKES", "HAS_RULE", "MEASURED", "PERFORMED", "OCCURRED", "RELATES_TO",
             "LEARNS", "WORKS_ON", "CONTRIBUTES_TO",
             "PART_OF", "PREREQUISITE_OF", "MASTERS", "LEARNED_FROM",
             "HAS_OBJECTIVE", "HAS_TASK", "PRODUCED_BY"]

# 관계의 (시작노드, 끝노드) 규약 — RELATES_TO 는 자유. 값이 리스트면 복수 규약 허용
REL_RULES = {
    "TAKES": ("Person", "Medication"),
    "HAS_RULE": ("Medication", "Regimen"),
    "MEASURED": ("Person", "Measurement"),
    "PERFORMED": ("Person", "Activity"),
    "OCCURRED": ("Person", "Event"),
    "LEARNS": ("Person", "Skill"),
    "WORKS_ON": ("Person", "Project"),
    "CONTRIBUTES_TO": [("Activity", "Skill"), ("Activity", "Project"), ("Activity", "Concept")],
    "PART_OF": [("Concept", "Topic"), ("Topic", "Subject")],
    "PREREQUISITE_OF": ("Concept", "Concept"),
    "MASTERS": ("Person", "Concept"),
    "LEARNED_FROM": ("Concept", "Source"),  # 어디서 배웠는가 — 출처의 그래프화
    "HAS_OBJECTIVE": ("Project", "Objective"),   # 왜(OKR)
    "HAS_TASK": ("Objective", "Task"),           # 무엇을(칸반)
    "PRODUCED_BY": ("Deliverable", "Task"),      # 무엇이 남았나(PARA)
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


@dataclass
class Skill:
    """배움 주제 — 예: 요리, AI 활용, 라인댄스 스텝 (삼각의 '학습' 꼭짓점)."""
    name: str
    status: str = "learning"   # learning|paused|done


@dataclass
class Project:
    """개인 프로젝트 — 예: 라인댄스 발표회, 책 출간 (삼각의 '프로젝트' 꼭짓점)."""
    name: str
    status: str = "active"     # active|paused|done
    due: str = ""


# ── G01: 개인 표준 온톨로지를 코어 레지스트리에 Frame으로 등록 ──
from graph_core import registry as _registry

_registry.register_frame("personal-v2", NODE_TYPES, REL_RULES, version="2.4")


def validate_edge(rel: str, src_type: str, dst_type: str) -> bool:
    """하위 호환 파사드 — 검증의 단일 출처는 graph_core.registry."""
    return _registry.validate_edge(rel, src_type, dst_type)
