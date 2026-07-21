"""G08-W 검증: 일 마스터 — OKR·칸반·산출물의 1인 밸류체인."""
from datetime import datetime

from graph import work_master as wm


def test_value_chain_project_to_deliverable(fresh_db):
    """목표→과업→완료→산출물 전 사슬 + 과업완료 이벤트."""
    now = datetime(2026, 7, 20, 14)
    oid = wm.add_objective("라인댄스 발표회", "10월 무대에 서기", "안무 3곡 완주", person="아내")
    t1 = wm.add_task(oid, "1곡 스텝 외우기", now)
    t2 = wm.add_task(oid, "연습 일정 잡기", now)

    wm.move_task(t1, "doing", now)
    wm.move_task(t1, "done", now)
    wm.add_deliverable(t1, "1곡 안무 노트", "볼트/안무1.md")

    b = wm.board("아내")
    proj = next(p for p in b if p["name"] == "라인댄스 발표회")
    obj = proj["objectives"][0]
    assert obj["done"] == 1 and obj["total"] == 2
    assert obj["kr"] == "안무 3곡 완주"
    assert any(d["name"] == "1곡 안무 노트" for d in obj["deliverables"])
    assert fresh_db.events("아내", 1, "과업완료", now), "실행이 이벤트로 남는다"
    assert wm.weekly_done("아내", now) == 1
    assert wm.weekly_done("나", now) == 0, "사람별 격리"
    assert t2  # 미완료 과업은 그대로


def test_project_reuses_triangle_node(fresh_db):
    """일 마스터의 프로젝트 = 삼각 모델의 Project 노드 (중복 생성 없음)."""
    wm.add_objective("발표회", "목표1", person="아내")
    wm.add_objective("발표회", "목표2", person="아내")
    projs = [p for p in fresh_db.nodes_by_type("Project") if p["props"]["name"] == "발표회"]
    assert len(projs) == 1
    assert len(fresh_db.neighbors(projs[0]["id"], "HAS_OBJECTIVE")) == 2


def test_work_page(fresh_db):
    from fastapi.testclient import TestClient
    from server.main import app
    c = TestClient(app)
    r = c.post("/work/objective", data={"project": "책 출간", "title": "원고 완성",
                                        "kr": "300쪽", "person": "나"}, follow_redirects=True)
    assert "책 출간" in r.text and "원고 완성" in r.text and "300쪽" in r.text
