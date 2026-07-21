"""개인 팩 갭 발견자 (G11) — 그래프의 끊긴 곳을 질문으로 바꾼다.

등록 갭 2종 (시작):
① 규칙 없는 약 — 약 노드는 있는데 HAS_RULE이 없다 → 복약 시간을 물어본다
② 목표 없는 프로젝트 — WORKS_ON은 있는데 HAS_OBJECTIVE가 없다 → 목표를 물어본다
   (확정·승인 시 실행기가 기본 목표를 실제로 만들어준다 — 전체 루프의 시범)
"""
from graph import store, work_master
from graph_core import approvals, interview


def meds_without_rule() -> list[dict]:
    out = []
    for med in store.nodes_by_type("Medication"):
        if not store.neighbors(med["id"], "HAS_RULE"):
            name = med["props"].get("name", med["id"])
            out.append({
                "id": f"gap:med_rule:{med['id']}", "kind": "med_rule",
                "question": f"'{name}'은(는) 정해진 시간에 드시는 약인가요? (예라면 볼트 노트에 rule_time을 추가해 주세요)",
                "hypothesis": {"action": "note_hint", "title": f"{name} 복약 규칙을 볼트에 추가",
                               "med": name, "source": med["props"].get("source", "")},
            })
    return out


def projects_without_objective() -> list[dict]:
    out = []
    for proj in store.nodes_by_type("Project"):
        if not store.neighbors(proj["id"], "HAS_OBJECTIVE"):
            name = proj["props"].get("name", proj["id"])
            owners = [p["props"].get("name", "나")
                      for _r, p in store.neighbors(proj["id"], "WORKS_ON", "in")]
            out.append({
                "id": f"gap:proj_obj:{proj['id']}", "kind": "proj_objective",
                "question": f"프로젝트 '{name}'에 목표(왜 하는가)가 없어요. 기본 목표를 세워둘까요?",
                "hypothesis": {"action": "add_objective", "title": f"'{name}' 기본 목표 생성",
                               "project": name, "person": owners[0] if owners else "나"},
            })
    return out


def _exec_add_objective(detail: dict) -> str:
    """승인 후 실행: 프로젝트에 기본 목표 생성 — 그래프가 원본인 영역만 만진다."""
    oid = work_master.add_objective(detail["project"], f"{detail['project']} 완수",
                                    person=detail.get("person", "나"))
    return f"목표 생성: {oid}"


def register() -> None:
    interview.register_gap_finder(meds_without_rule)
    interview.register_gap_finder(projects_without_objective)
    approvals.register_executor("add_objective", _exec_add_objective)
    # note_hint는 실행기 없음 — 승인해도 '기록만' (볼트는 사람이 고친다: 원본 불변 원칙)


register()
