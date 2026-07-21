"""G08-M 검증: 마음 마스터 1단계 — 기록·주간 분포·브리핑의 다정한 질문."""
from datetime import datetime, timedelta

from graph import mind_master as mm
from server.briefing import morning_briefing


def test_record_and_week_distribution(fresh_db):
    now = datetime(2026, 7, 20, 21)
    mm.record_mood("나", "평온", "산책이 좋았다", now - timedelta(days=1))
    mm.record_mood("나", "불안", "", now)
    w = mm.week_moods("나", now)
    assert w["n"] == 2 and w["counts"]["평온"] == 1 and w["counts"]["불안"] == 1
    assert "산책" in fresh_db.events("나", 7, "마음", now)[0]["payload"], "문장이 보존된다"


def test_briefing_asks_gently_only_when_missing(fresh_db):
    now = datetime(2026, 7, 20, 7)
    assert "마음은 어떠세요" in morning_briefing("나", now), "기록 없으면 묻는다"
    mm.record_mood("나", "기쁨", "", now)
    assert "마음은 어떠세요" not in morning_briefing("나", now + timedelta(hours=2)), "기록했으면 묻지 않는다"


def test_home_mood_form(fresh_db):
    from fastapi.testclient import TestClient
    from server.main import app
    c = TestClient(app)
    r = c.post("/mind", data={"person": "나", "mood": "평온", "memo": "테스트"},
               follow_redirects=True)
    assert "평온 1회" in r.text
