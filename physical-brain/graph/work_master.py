"""일 마스터 (G08-W) — 1인 밸류체인: 목표(왜)→과업(무엇)→완료(실행)→산출물(무엇이 남았나).

OKR(Objective+KR) × 칸반(todo/doing/done) × PARA(Deliverable 링크)의 조합.
프로젝트 노드는 삼각 모델의 Project 그대로 — 활동(세션)의 CONTRIBUTES_TO와 이어진다.
일 항목의 원본은 그래프(앱 관리) — 지식(프로젝트 정의)의 원본은 여전히 볼트.
"""
import re
import uuid
from datetime import datetime, timedelta

from graph import store

STATUSES = ["todo", "doing", "done"]


def _slug(name: str) -> str:
    return re.sub(r"\s+", "_", name.strip())


def _ensure_project(name: str, person: str = "나") -> str:
    pid_node = f"project:{_slug(name)}"
    if not store.get_node(pid_node):
        store.upsert_node(pid_node, "Project", {"name": name, "status": "active"})
        p = store.person_id(person)
        if not store.get_node(p):
            store.upsert_node(p, "Person", {"name": person})
        store.upsert_edge(p, "WORKS_ON", pid_node)
    return pid_node


def add_objective(project: str, title: str, kr: str = "", person: str = "나") -> str:
    """목표 등록 — kr(핵심결과)은 측정 가능한 문장으로 (CTQ와 동형)."""
    proj_id = _ensure_project(project, person)
    oid = f"objective:{_slug(project)}:{_slug(title)}"
    store.upsert_node(oid, "Objective", {"name": title, "kr": kr})
    store.upsert_edge(proj_id, "HAS_OBJECTIVE", oid)
    return oid


def add_task(objective_id: str, title: str, now: datetime | None = None) -> str:
    now = now or datetime.now()
    tid = f"task:{uuid.uuid4().hex[:8]}"
    store.upsert_node(tid, "Task", {"name": title, "status": "todo",
                                    "created_at": now.isoformat()})
    store.upsert_edge(objective_id, "HAS_TASK", tid)
    return tid


def move_task(task_id: str, status: str, now: datetime | None = None) -> dict:
    """칸반 이동. done 이동 시 과업완료 이벤트 — 실행이 기록으로 남는다."""
    assert status in STATUSES, f"unknown status {status}"
    now = now or datetime.now()
    n = store.get_node(task_id)
    if not n:
        raise ValueError(f"과업 없음: {task_id}")
    props = dict(n["props"])
    props["status"] = status
    if status == "done":
        props["done_at"] = now.isoformat()
    store.upsert_node(task_id, "Task", props)
    if status == "done":
        from server.events import record_event
        owner = _owner_of(task_id)
        record_event(owner, "과업완료", props.get("name", task_id), now)
    return props


def add_deliverable(task_id: str, name: str, link: str = "") -> str:
    """산출물 — 볼트 파일·문서 링크가 그래프에 남는다 (PARA의 Archive)."""
    did = f"deliverable:{uuid.uuid4().hex[:8]}"
    store.upsert_node(did, "Deliverable", {"name": name, "link": link})
    store.upsert_edge(did, "PRODUCED_BY", task_id)
    return did


def _owner_of(task_id: str) -> str:
    for _r, obj in store.neighbors(task_id, "HAS_TASK", "in"):
        for _r2, proj in store.neighbors(obj["id"], "HAS_OBJECTIVE", "in"):
            for _r3, person in store.neighbors(proj["id"], "WORKS_ON", "in"):
                return person["props"].get("name", "나")
    return "나"


def board(person: str | None = None) -> list[dict]:
    """프로젝트별 보드: 목표→과업(칸반)·진도·산출물."""
    out = []
    for proj in store.nodes_by_type("Project"):
        if person:
            owners = [p["props"].get("name") for _r, p in store.neighbors(proj["id"], "WORKS_ON", "in")]
            if owners and person not in owners:
                continue
        objectives = []
        for _r, obj in store.neighbors(proj["id"], "HAS_OBJECTIVE"):
            tasks = [dict(id=t["id"], **t["props"]) for _r2, t in store.neighbors(obj["id"], "HAS_TASK")]
            done = sum(1 for t in tasks if t.get("status") == "done")
            delivs = []
            for t in tasks:
                for _r3, d in store.neighbors(t["id"], "PRODUCED_BY", "in"):
                    delivs.append(d["props"])
            objectives.append({"id": obj["id"], "name": obj["props"].get("name", ""),
                               "kr": obj["props"].get("kr", ""), "tasks": tasks,
                               "done": done, "total": len(tasks), "deliverables": delivs})
        out.append({"id": proj["id"], "name": proj["props"].get("name", ""),
                    "status": proj["props"].get("status", ""), "objectives": objectives})
    return out


def weekly_done(person: str, now: datetime | None = None) -> int:
    """최근 7일 완료 과업 수 — 주간 관리도 재료."""
    now = now or datetime.now()
    since = (now - timedelta(days=7)).isoformat()
    cnt = 0
    for proj in board(person):
        for obj in proj["objectives"]:
            cnt += sum(1 for t in obj["tasks"]
                       if t.get("status") == "done" and since <= t.get("done_at", "") <= now.isoformat())
    return cnt
