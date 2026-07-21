"""G03 검증: GraphRAG — 시드 탐색, N-hop 서브그래프, 근거 인용 답변."""
from datetime import datetime

from graph_core import graphrag
from server.librarian import answer


def test_find_nodes_robust_to_josa(fresh_db):
    """조사가 붙어도('오메가3는') 이름 노드를 찾는다."""
    hits = graphrag.find_nodes("오메가3는 누가 먹고 있어?")
    assert any(h["props"].get("name") == "오메가3" for h in hits)


def test_subgraph_two_hops(fresh_db):
    """약 시드 → 1홉(복용자·규칙) 관계가 서브그래프에 들어온다."""
    med = graphrag.find_nodes("오메가3")[0]
    sub = graphrag.subgraph([med["id"]], hops=2)
    types = {n["type"] for n in sub["nodes"].values()}
    assert {"Medication", "Person", "Regimen"} <= types
    assert any(rel == "TAKES" for _s, rel, _d in sub["edges"])


def test_free_question_graph_fallback_with_evidence(fresh_db):
    """의도 템플릿 밖 자유 질문 → 그래프 사실 + 근거(출처 노트 포함) 답변."""
    r = answer("오메가3는 누가 먹고 있어?", datetime(2026, 7, 20))
    assert r["intent"] == "graph"
    assert "나" in r["answer"] or any("나" in f for f in r["data"]["facts"])
    assert r["evidence"], "근거 팩이 있어야 한다"
    assert any(e.get("source", "").endswith(".md") for e in r["evidence"]), "볼트 노트 출처 인용"


def test_bp_answer_carries_measurement_evidence(fresh_db):
    """혈압 의도 답변에 측정 근거(id·시각)가 붙는다."""
    from pipelines.mock_health import generate
    now = datetime(2026, 7, 15, 12)
    generate(days=5, end=now, seed=7)
    r = answer("이번 주 아버지 혈압 어때?", now)
    assert r["intent"] == "bp_trend" and r["evidence"]
    assert all(e["id"].startswith("measurement:아버지:bp_sys:") for e in r["evidence"])


def test_unknown_name_still_honest(fresh_db):
    """그래프에 없는 이름 → 지어내지 않고 안내한다."""
    r = answer("김철수의 재산은 얼마야?", datetime(2026, 7, 20))
    assert r["intent"] == "unknown" and r["evidence"] == []
