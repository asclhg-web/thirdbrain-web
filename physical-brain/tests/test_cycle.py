"""G04 검증: KG-DMAIC 사이클 엔진 — Define→Measure(근거 기반 판정)→갭 보드."""
from datetime import datetime

from graph_core import cycle
from server.librarian import answer


def test_define_and_measure_with_librarian(fresh_db):
    now = datetime(2026, 7, 20, 10)
    cid = cycle.create_cycle(
        "건강 1차", "나와 아버지의 건강을 지키기 위해",
        ["오늘 나의 약 뭐야?",            # 규칙 있음 → 근거 있는 답 ✅
         "오메가3는 누가 먹고 있어?",      # GraphRAG 폴백 ✅
         "이번 주 나의 혈압 어때?",        # 측정 데이터 없음 → ❌ (정직)
         "김철수의 재산은?"],              # 그래프 밖 → ❌
        [{"name": "CQ 응답률", "target": "80%"}], now)
    r = cycle.measure(cid, lambda q: answer(q, now), now)
    assert r["total"] == 4 and r["answerable"] == 2 and r["rate"] == 50

    b = cycle.board(cid)
    assert b["cycle"]["phase"] == "measure"
    assert b["cq_rate"] == 50 and len(b["gaps"]) == 2
    reasons = {g["question"]: g["gap_reason"] for g in b["gaps"]}
    assert "기록 없음" in reasons["이번 주 나의 혈압 어때?"], "데이터 부재로 분류"
    assert "부재" in reasons["김철수의 재산은?"]


def test_measure_improves_after_data_added(fresh_db):
    """개선 후 재측정 — 갭이 닫히는 것을 사이클이 증명한다 (I→C의 심장)."""
    now = datetime(2026, 7, 20, 10)
    cid = cycle.create_cycle("c", "p", ["이번 주 나의 혈압 어때?"], [], now)
    assert cycle.measure(cid, lambda q: answer(q, now), now)["rate"] == 0
    fresh_db.upsert_node(f"measurement:나:bp_sys:{now.isoformat()}", "Measurement",
                         {"type": "bp_sys", "value": 128.0, "unit": "mmHg",
                          "measured_at": now.isoformat()})
    fresh_db.upsert_edge("person:나", "MEASURED", f"measurement:나:bp_sys:{now.isoformat()}")
    assert cycle.measure(cid, lambda q: answer(q, now), now)["rate"] == 100


def test_cycle_page_renders(fresh_db):
    from fastapi.testclient import TestClient
    from server.main import app
    c = TestClient(app)
    assert "새 사이클" in c.get("/cycle").text  # 사이클 없으면 Define 위저드
    r = c.post("/cycle/create", data={"name": "테스트", "purpose": "목적",
                                      "cqs": "오늘 나의 약 뭐야?", "ctq1": "CQ 응답률",
                                      "ctq1_target": "80%"}, follow_redirects=True)
    assert "테스트" in r.text and "미측정" in r.text


def test_control_chart_history_accumulates(fresh_db):
    """G07 관리도: 측정할 때마다 이력이 쌓여 추이가 남는다."""
    from datetime import datetime
    from graph_core import cycle
    from server.librarian import answer
    now = datetime(2026, 7, 20, 10)
    cid = cycle.create_cycle("c", "p", ["오늘 나의 약 뭐야?"], [], now)
    cycle.measure(cid, lambda q: answer(q, now), now)
    cycle.measure(cid, lambda q: answer(q, now), now)
    b = cycle.board(cid)
    assert len(b["history"]) == 2 and all(h["rate"] == 100 for h in b["history"])
