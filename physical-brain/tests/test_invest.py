"""G13 검증: 투자 팩 — 가치사슬 시드, 충격전파 질의(경로=근거), 사서 자유질문."""
from datetime import datetime

import invest
from server.librarian import answer


def test_frame_and_seed(fresh_db):
    from graph_core import registry
    assert "investment-v1" in registry.frames()
    invest.seed_chain()
    c = fresh_db.counts()["nodes"]
    assert c.get("Company") == 6 and c.get("Sector") == 3
    assert fresh_db.neighbors("company:SK하이닉스", "SUPPLIES")[0][1]["props"]["name"] == "엔비디아"


def test_impact_propagation_with_path_evidence(fresh_db):
    """DRAM 가격 급등 → 직접 영향(메모리사) + 공급망 1홉 전파(엔비디아, 감쇠 0.5) — 경로가 근거."""
    invest.seed_chain()
    now = datetime(2026, 7, 20, 8)
    eid = invest.record_market_event(
        "DRAM 가격 급등", [("삼성전자", "+", 0.8), ("SK하이닉스", "+", 0.9)],
        now, source="삼성증권 주간전략 2026-07")
    r = invest.impact_query(eid)
    by = {x["target"]: x for x in r}
    assert by["SK하이닉스"]["score"] == 0.9 and by["SK하이닉스"]["sign"] == "+"
    assert by["엔비디아"]["score"] == 0.45, "공급망 1홉 감쇠 전파"
    assert "SUPPLIES" in by["엔비디아"]["path"], "전파 경로가 그대로 근거"
    assert r[0]["target"] == "SK하이닉스", "점수 내림차순"


def test_librarian_answers_company_question(fresh_db):
    """사서 자유질문이 투자 그래프도 순회한다 — 팩 통합의 증거."""
    invest.seed_chain()
    r = answer("SK하이닉스는 누구에게 공급해?", datetime(2026, 7, 20))
    assert r["intent"] == "graph"
    assert any("엔비디아" in f for f in r["data"]["facts"])
    assert r["evidence"], "근거 팩 포함"


def test_no_investment_advice(fresh_db):
    """금지영역: 매수/매도 판단은 답하지 않는다... 는 기존 금지 패턴과 별개로,
    impact_query는 점수·경로(사실)만 반환하고 '사라/팔라'류 텍스트가 없다."""
    invest.seed_chain()
    eid = invest.record_market_event("테스트 이벤트", [("삼성전자", "-", 0.5)],
                                     datetime(2026, 7, 20))
    for row in invest.impact_query(eid):
        assert "매수" not in row["path"] and "매도" not in row["path"]
