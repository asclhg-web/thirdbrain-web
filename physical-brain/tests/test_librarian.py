"""T09~T12 검증: 사서 정답, 금지영역, 안전망, 브리핑."""
from datetime import datetime

NOW = datetime(2026, 7, 15, 12, 0)


def _mock(fresh_db):
    from pipelines.mock_health import generate
    generate(days=14, end=NOW, seed=7)


def test_librarian_bp_trend(fresh_db):
    _mock(fresh_db)
    from server.librarian import answer
    r = answer("이번 주 아버지 혈압 어때?", NOW)
    assert r["intent"] == "bp_trend" and r["person"] == "아버지"
    assert r["data"]["avg_sys"] and 120 < r["data"]["avg_sys"] < 160
    assert str(r["data"]["avg_sys"]) in r["answer"]  # 수치는 조회값만


def test_librarian_meds_today(fresh_db):
    from server.librarian import answer
    r = answer("오늘 아버지 약 뭐야?", NOW)
    assert "혈압약" in r["answer"] and "자몽" in r["answer"]


def test_librarian_forbidden(fresh_db):
    from server.librarian import answer
    r = answer("아버지 무슨 병이야? 약 끊어도 돼?", NOW)
    assert r["intent"] == "forbidden"
    assert "의사" in r["answer"] or "진료" in r["answer"]  # 병원 안내로 응답


def test_safety_layers(fresh_db):
    from server.safety import check_measurement
    assert check_measurement("아버지", "bp_sys", 185, NOW)["level"] == "emergency"
    assert check_measurement("아버지", "bp_sys", 142, NOW)["level"] == "warn"
    assert check_measurement("아버지", "bp_sys", 120, NOW) is None
    evs = fresh_db.events("아버지", 1, "임계초과", NOW)
    assert len(evs) == 2  # 긴급+주의 모두 기록


def test_briefing(fresh_db):
    _mock(fresh_db)
    from server.briefing import morning_briefing
    text = morning_briefing("아버지", NOW)
    assert "아버지" in text and "혈압약" in text
    assert fresh_db.events("아버지", 1, "브리핑", NOW)
