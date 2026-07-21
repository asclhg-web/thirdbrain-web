"""에이전트 빌더 (G12) — 확정된 지식에서 시나리오(YAML 규칙) 초안을 만든다.

원리: 몸 마스터에 주의 임계값(warn)이 있는데 대응 규칙이 없는 측정 유형
→ '넘으면 부드럽게 알려주는' 규칙 초안을 자동 생성 → 승인 큐(G05) 제안
→ 사람이 승인하면 그때 rules 디렉토리에 YAML이 생기고 다음 틱부터 가동.

초안의 문장은 고정 템플릿(권유 어조) — 진단·처방 없음(AI 4대 금지).
"""
import os
import re

import yaml

from graph.body_master import measure_types
from graph_core import approvals
from server import orchestrator

SAY_TEMPLATE = "💡 {label}이(가) {{value}}로 기준({gte})을 넘었어요 — 무리하지 말고, 기록해 두었으니 흐름을 함께 지켜봐요."


def _rules_measurements() -> set[str]:
    """기존 규칙들이 이미 다루는 측정 키."""
    keys = set()
    for fn in os.listdir(orchestrator.RULES_DIR):
        if not fn.endswith(".yaml"):
            continue
        with open(os.path.join(orchestrator.RULES_DIR, fn), encoding="utf-8") as f:
            r = yaml.safe_load(f) or {}
        t = r.get("trigger", {})
        if t.get("type") == "measurement" and t.get("measurement"):
            keys.add(t["measurement"])
    return keys


def suggest_rules(person: str = "나") -> list[dict]:
    """임계값은 있는데 규칙이 없는 측정 유형 → 규칙 초안 목록."""
    covered = _rules_measurements()
    drafts = []
    for key, mt in measure_types().items():
        if "warn" not in mt or key in covered:
            continue
        label = mt.get("label", key)
        rule = {
            "name": f"{label} 주의 알림 (자동 초안)",
            "enabled": True,
            "trigger": {"type": "measurement", "person": person,
                        "measurement": key, "gte": mt["warn"]},
            "cooldown_hours": 4,
            "actions": [{"type": "say", "person": person,
                         "text": SAY_TEMPLATE.format(label=label, gte=mt["warn"])}],
        }
        safe_key = re.sub(r"[^\w]", "_", key)
        drafts.append({"key": key, "label": label, "warn": mt["warn"],
                       "filename": f"auto_{safe_key}.yaml", "rule": rule})
    return drafts


def propose_rule(draft: dict, now=None) -> int:
    """초안을 승인 큐에 제안 — 활성화는 사람의 승인 후."""
    return approvals.propose(
        "activate_rule", f"규칙 초안: {draft['rule']['name']}",
        {"filename": draft["filename"], "rule": draft["rule"],
         "action": "activate_rule", "title": draft["rule"]["name"]},
        proposed_by="에이전트빌더", now=now)


def _exec_activate_rule(detail: dict) -> str:
    """승인 후 실행: rules 디렉토리에 YAML 생성 → 다음 틱부터 오케스트레이터가 가동."""
    path = os.path.join(orchestrator.RULES_DIR, detail["filename"])
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(detail["rule"], f, allow_unicode=True, sort_keys=False)
    return f"규칙 활성화: {detail['filename']}"


approvals.register_executor("activate_rule", _exec_activate_rule)
