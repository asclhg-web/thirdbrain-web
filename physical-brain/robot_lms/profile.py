"""R02 로봇 프로필 — 로봇의 지능 = L1 × L2 × L3 를 한 장에.

L1 기반지능: 검정고시 성적 (exam)
L2 분야지능: 분야팩 인증 현황 (domain)
L3 주인지능: 브레인그래프 자체 — 마스터별로 쌓인 주인의 기록.
셋 중 하나라도 0이면 지능도 0이라는 곱셈 구조를 숫자 그대로 보여준다.
합성 점수는 만들지 않는다 — 각 층의 진실을 각 층의 단위로 (미확인은 미확인으로).
"""
import os

from graph_core import store
from robot_lms import domain, exam


def robot_profile() -> dict:
    card = exam.report_card()
    latest = card["latest"]
    l1 = {"certified": bool(latest and latest["certified"]),
          "rate": latest["rate"] if latest else None,
          "hallucination": latest["hallucination"] if latest else None,
          "exams": len(card["history"])}

    ps = domain.packs()
    l2 = {"total": len(ps),
          "certified": sum(1 for p in ps if p["certified"]),
          "open": domain.open_domains()}

    c = store.counts()
    n = c["nodes"]
    mind = sum(1 for e in store.nodes_by_type("Event")
               if e["props"].get("kind") == "마음")
    l3 = {"nodes": sum(n.values()), "edges": c["edges"],
          "masters": {"몸": n.get("Measurement", 0),
                      "학습": n.get("Concept", 0),
                      "일": n.get("Objective", 0) + n.get("Task", 0),
                      "마음": mind}}

    return {"name": os.environ.get("PB_ROBOT_NAME", "피지컬브레인 1호"),
            "l1": l1, "l2": l2, "l3": l3,
            "can_general": l1["certified"], "open_domains": l2["open"]}
