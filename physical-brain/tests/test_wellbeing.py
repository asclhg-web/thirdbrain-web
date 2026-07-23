"""H02+H03 검증: 일반 측정 입력(체중)·웰빙 주간 카드(결과+습관 한 장)."""
from datetime import datetime

from server.wellbeing import week_card

NOW = datetime(2026, 7, 23, 10)


def test_measure_form_records_weight(fresh_db):
    from fastapi.testclient import TestClient
    from server.main import app
    c = TestClient(app)
    r = c.post("/measure", data={"person": "나", "mtype": "weight", "value": 72.5},
               follow_redirects=False)
    assert r.status_code == 303
    from datetime import timedelta
    ms = fresh_db.measurements("나", "weight", 1, datetime.now() + timedelta(minutes=1))
    assert ms and ms[-1]["value"] == 72.5 and ms[-1]["unit"] == "kg"


def test_unknown_type_is_ignored(fresh_db):
    from fastapi.testclient import TestClient
    from server.main import app
    c = TestClient(app)
    c.post("/measure", data={"person": "나", "mtype": "없는유형", "value": 1})
    from graph_core import store as cs
    assert not [n for n in cs.nodes_by_type("Measurement")
                if n["props"].get("type") == "없는유형"], "사전에 없는 유형은 기록하지 않는다"


def test_week_card_combines_body_and_habits(fresh_db):
    from graph import learning_master as lm
    from graph import store
    lm.seed_curriculum()
    # 몸: 수면·체중 / 습관: 학습 확인 1회·마음 기록 1일
    pid = store.person_id("나")
    store.upsert_node(f"measurement:나:weight:{NOW.isoformat()}", "Measurement",
                      {"type": "weight", "value": 72.0, "unit": "kg",
                       "measured_at": NOW.isoformat()})
    store.upsert_edge(pid, "MEASURED", f"measurement:나:weight:{NOW.isoformat()}")
    lm.record_quiz("나", "concept:자연수의_사칙연산", True, NOW)
    from graph.mind_master import record_mood
    record_mood("나", "평온", "", NOW)
    w = week_card("나", NOW)
    assert w["body"]["weight"] == 72.0
    assert w["habits"]["learn_checks"] == 1
    assert w["habits"]["mind_days"] == 1
    assert set(w["habits"]) == {"adherence", "learn_checks", "tasks_done", "mind_days"}


def test_briefing_praises_habits_only(fresh_db):
    """H04: 브리핑은 잘한 습관만 짚는다 — 못한 것은 꾸짖지 않는다(격려 기조)."""
    from server.briefing import morning_briefing
    text0 = morning_briefing("나", NOW)
    assert "이번 주 습관" not in text0, "습관 기록이 없으면 조용히"
    from graph import learning_master as lm
    lm.seed_curriculum()
    lm.record_quiz("나", "concept:자연수의_사칙연산", True, NOW)
    text = morning_briefing("나", NOW)
    assert "학습 확인 1회" in text and "좋은 리듬" in text


def test_home_shows_wellbeing_card(fresh_db):
    from fastapi.testclient import TestClient
    from server.main import app
    page = TestClient(app).get("/").text
    assert "웰빙 주간 카드" in page and "습관 (선행)" in page
    assert "체중" in page, "일반 측정 입력에 체중 노출 (H02)"
