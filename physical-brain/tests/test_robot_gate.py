"""R05 검증: 대화 개방 게이트 — 미인증은 정직한 후퇴, 인증 분야만 근거와 함께 대화."""
from datetime import datetime

from robot_lms import domain, exam, gate
from server.librarian import answer

NOW = datetime(2026, 7, 22, 10)


def _perfect(question: str) -> str:
    for _id, _lv, _sj, q, keys in exam.BANK:
        if q == question:
            return ("모르겠습니다. 존재하지 않는 정보입니다." if keys is None
                    else f"정답은 {keys[0]} 입니다.")
    return "모르겠습니다."


def test_uncertified_domain_defers_without_leaking(fresh_db):
    """공부 중인 분야: 물러설 뿐, 사서 답(약 이름 등)을 흘리지 않는다."""
    domain.create_pack("건강 돌봄", "care")
    r = gate.converse("오늘 나의 약 일정 알려줘", NOW)
    assert r["mode"] == "studying" and r["domain"] == "건강 돌봄"
    assert "자기시험을 보기 전" in r["answer"]
    assert "오메가3" not in r["answer"], "미인증 분야에서 데이터가 새면 안 된다"
    domain.self_test(1, lambda q: {"answer": "모르겠습니다.", "evidence": []}, NOW)
    r2 = gate.converse("오늘 나의 약 일정 알려줘", NOW)
    assert "공부 중이에요" in r2["answer"] and "0%" in r2["answer"], "현재 성적을 정직하게 공개"


def test_certified_domain_answers_with_evidence(fresh_db):
    domain.create_pack("건강 돌봄", "care")
    domain.self_test(1, lambda q: answer(q, NOW), NOW)
    r = gate.converse("오늘 나의 약 일정 알려줘", NOW)
    assert r["mode"] == "domain" and r["domain"] == "건강 돌봄"
    assert "오메가3" in r["answer"] and len(r["evidence"]) > 0


def test_l1_gate_for_general_questions(fresh_db):
    """분야 밖 질문: L1 검정 전에는 일반 대화도 열지 않는다."""
    r = gate.converse("아인슈타인의 상대성이론이 뭐야?", NOW)
    assert r["mode"] == "l1_uncertified" and "기반 검정" in r["answer"]
    exam.run_exam(_perfect, NOW, model="fake")
    r2 = gate.converse("아인슈타인의 상대성이론이 뭐야?", NOW)
    assert r2["mode"] == "general", "L1 인증 후에는 일반 대화 개방"
    assert "LLM" in r2["answer"], "오프라인에서는 정직한 폴백 (테스트 환경엔 LLM 없음)"


def test_owner_librarian_stays_ungated(fresh_db):
    """주인의 사서(/api/ask)는 게이트 밖 — 로봇이 공부 중이어도 돌봄은 멈추지 않는다."""
    domain.create_pack("건강 돌봄", "care")  # 미인증 상태
    r = answer("오늘 나의 약 뭐야?", NOW)
    assert "오메가3" in r["answer"], "주인 도구는 항상 동작"


def test_chat_page_renders(fresh_db):
    from fastapi.testclient import TestClient
    from server.main import app
    c = TestClient(app)
    assert "로봇과 대화" in c.get("/robot/chat").text
    domain.create_pack("건강 돌봄", "care")
    page = c.get("/robot/chat", params={"q": "오늘 나의 약 일정 알려줘"}).text
    assert "공부 중인 분야" in page or "자기시험을 보기 전" in page
