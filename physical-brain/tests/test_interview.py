"""G11 검증: 암묵지 인터뷰 — 갭→질문→확인 누적→확정→승인 큐→실행 (전체 루프)."""
from datetime import datetime

from graph import gap_finders  # noqa: F401 — 갭 발견자·실행기 등록
from graph import store, work_master
from graph_core import approvals, interview


def test_gap_becomes_question(fresh_db, tmp_path):
    """규칙 없는 약 → 질문 생성 (규칙 있는 샘플 약들은 질문이 안 됨)."""
    from pipelines.vault_sync import sync_note
    p = tmp_path / "약_새영양제.md"
    p.write_text('---\ntype: medication\nname: 새영양제\nfor: "[[나]]"\n---\n', encoding="utf-8")
    sync_note(str(p))
    assert interview.scan() >= 1
    qs = interview.due(10)
    assert any("새영양제" in q["question"] for q in qs)
    assert not any("오메가3" in q["question"] for q in qs), "규칙 있는 약은 갭이 아님"
    assert interview.scan() == 0, "재스캔은 중복 시드를 만들지 않는다(멱등)"


def test_full_loop_gap_to_execution(fresh_db):
    """끊긴 곳→질문→예 2회→확정→승인 제안→사람 승인→실행(목표 생성) — PTGDA+HITL 완주."""
    now = datetime(2026, 7, 20, 15)
    store.upsert_node("project:책_출간", "Project", {"name": "책 출간", "status": "active"})
    store.upsert_edge("person:나", "WORKS_ON", "project:책_출간")
    interview.scan(now)
    seed = next(q for q in interview.due(10) if q["kind"] == "proj_objective")

    r1 = interview.answer(seed["id"], "yes", now)
    assert r1["status"] == "wave", "1회로는 확정 아님 (파동)"
    r2 = interview.answer(seed["id"], "yes", now)
    assert r2["status"] == "confirmed" and r2["approval_id"], "확정 → 승인 큐 제안"

    assert not store.neighbors("project:책_출간", "HAS_OBJECTIVE"), "승인 전 실행 0건 (HITL)"
    approvals.decide(r2["approval_id"], approve=True, now=now)
    objs = store.neighbors("project:책_출간", "HAS_OBJECTIVE")
    assert objs and "완수" in objs[0][1]["props"]["name"], "승인 후에만 그래프가 바뀐다"


def test_refuted_seed_closes_without_proposal(fresh_db):
    """아니오 2회 → 반박 종결, 승인 큐에 아무것도 올라가지 않는다."""
    now = datetime(2026, 7, 20, 15)
    store.upsert_node("project:임시", "Project", {"name": "임시"})
    store.upsert_edge("person:나", "WORKS_ON", "project:임시")
    interview.scan(now)
    seed = next(q for q in interview.due(10) if "임시" in q["question"])
    interview.answer(seed["id"], "no", now)
    r = interview.answer(seed["id"], "no", now)
    assert r["status"] == "refuted" and not r["approval_id"]
    assert all("임시" not in a["title"] for a in approvals.pending())


def test_interview_page(fresh_db):
    from fastapi.testclient import TestClient
    from server.main import app
    c = TestClient(app)
    store.upsert_node("project:화면용", "Project", {"name": "화면용"})
    store.upsert_edge("person:나", "WORKS_ON", "project:화면용")
    page = c.get("/interview").text
    assert "암묵지 인터뷰" in page and "화면용" in page
