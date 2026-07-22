"""R02+R08 검증: 로봇 프로필(L1×L2×L3 한 장) + 로봇 대화 API(음성의 입구)."""
from datetime import datetime

from robot_lms import domain, exam, profile
from server.librarian import answer

NOW = datetime(2026, 7, 22, 10)


def _perfect(question: str) -> str:
    for _id, _lv, _sj, q, keys in exam.BANK:
        if q == question:
            return ("모르겠습니다. 존재하지 않는 정보입니다." if keys is None
                    else f"정답은 {keys[0]} 입니다.")
    return "모르겠습니다."


def test_profile_before_any_training(fresh_db):
    p = profile.robot_profile()
    assert p["l1"]["certified"] is False and p["l1"]["exams"] == 0
    assert p["l2"]["total"] == 0 and p["open_domains"] == []
    assert p["l3"]["nodes"] > 0, "L3(주인그래프)는 볼트 동기화로 이미 자라고 있다"
    assert set(p["l3"]["masters"]) == {"몸", "학습", "일", "마음"}
    assert p["can_general"] is False


def test_profile_after_l1_and_l2(fresh_db):
    exam.run_exam(_perfect, NOW, model="fake")
    domain.create_pack("건강 돌봄", "care")
    domain.self_test(1, lambda q: answer(q, NOW), NOW)
    p = profile.robot_profile()
    assert p["l1"]["certified"] is True and p["l1"]["hallucination"] == 0
    assert p["l2"]["certified"] == 1 and p["open_domains"] == ["건강 돌봄"]
    assert p["can_general"] is True


def test_robot_page_shows_profile(fresh_db):
    from fastapi.testclient import TestClient
    from server.main import app
    page = TestClient(app).get("/robot").text
    assert "로봇 프로필" in page and "피지컬브레인 1호" in page
    assert "L1" in page and "주인지능" in page


def test_robot_chat_api_for_voice(fresh_db):
    """R08: 음성 클라이언트가 붙는 API — 게이트가 그대로 적용된다."""
    from fastapi.testclient import TestClient
    c = TestClient(__import__("server.main", fromlist=["app"]).app)
    domain.create_pack("건강 돌봄", "care")
    r = c.post("/api/robot/chat", json={"question": "오늘 나의 약 일정 알려줘"}).json()
    assert r["mode"] == "studying" and "오메가3" not in r["answer"]
    domain.self_test(1, lambda q: answer(q, NOW), NOW)
    r2 = c.post("/api/robot/chat", json={"question": "오늘 나의 약 일정 알려줘"}).json()
    assert r2["mode"] == "domain" and "오메가3" in r2["answer"]
    assert len(r2["evidence"]) > 0, "음성으로 나갈 답에도 근거가 붙는다"
