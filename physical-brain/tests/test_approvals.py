"""G05 검증: 승인 큐 — '승인 없는 자동 변경 0건' 계약."""
import pytest

from graph_core import approvals


def test_no_execution_without_approval(fresh_db):
    """HITL의 심장: pending·rejected 제안의 실행은 예외로 막힌다."""
    executed = []
    approvals.register_executor("test_change", lambda d: executed.append(d) or "ok")
    aid = approvals.propose("test_change", "테스트 변경", {"value": 1})

    with pytest.raises(approvals.NotApproved):
        approvals.execute(aid)                       # 승인 전 실행 금지
    assert executed == [], "승인 없는 자동 변경 0건"

    approvals.decide(aid, approve=False)
    with pytest.raises(approvals.NotApproved):
        approvals.execute(aid)                       # 반려 후에도 금지
    assert executed == []


def test_approve_executes_once(fresh_db):
    executed = []
    approvals.register_executor("test_change", lambda d: executed.append(d) or "적용됨")
    aid = approvals.propose("test_change", "안전재고 조정", {"value": 42}, "InventoryAgent")
    r = approvals.decide(aid, approve=True)
    assert r["executed"] and executed == [{"value": 42}]
    with pytest.raises(approvals.NotApproved):
        approvals.execute(aid)                       # 이중 실행 금지
    assert len(executed) == 1
    h = approvals.history()
    assert h[0]["status"] == "approved" and "적용됨" in h[0]["result"]


def test_unknown_executor_records_only(fresh_db):
    """실행기 없는 종류 → 변경 없이 기록만 (조용한 부작용 금지)."""
    aid = approvals.propose("odoo_write", "미래 기능 제안", {})
    r = approvals.decide(aid, approve=True)
    assert "실행기 없음" in r["result"]


def test_approvals_page(fresh_db):
    from fastapi.testclient import TestClient
    from server.main import app
    c = TestClient(app)
    approvals.propose("test_change", "화면 표시 제안", {"x": 1}, "튜닝에이전트")
    page = c.get("/approvals").text
    assert "화면 표시 제안" in page and "승인" in page
    aid = approvals.pending()[0]["id"]
    c.post(f"/approvals/{aid}/decide", data={"approve": 0}, follow_redirects=True)
    assert approvals.pending() == []
