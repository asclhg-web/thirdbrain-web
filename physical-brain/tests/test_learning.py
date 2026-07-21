"""G08-L 검증: 학습 마스터 — 커리큘럼 트리, 선수관계 게이트, PTGDA식 숙달 입자화."""
from datetime import datetime

from graph import learning_master as lm


def test_seed_curriculum_idempotent(fresh_db):
    r1 = lm.seed_curriculum()
    r2 = lm.seed_curriculum()
    assert r1["concepts"] == r2["concepts"]
    assert len(fresh_db.nodes_by_type("Concept")) == r1["concepts"], "중복 생성 없음(멱등)"
    subs = {n["props"]["name"] for n in fresh_db.nodes_by_type("Subject")}
    assert {"수학", "과학", "AI 활용"} <= subs


def test_prerequisite_gates_quiz(fresh_db):
    """선수 미숙달 개념은 '다음 걸음'에 나오지 않는다 — 지식의 지도가 길을 낸다."""
    lm.seed_curriculum()
    names = {q["name"] for q in lm.quiz_candidates("아내", 50)}
    assert "자연수의 사칙연산" in names and "생성형 AI란" in names
    assert "일차방정식" not in names, "분수(선수) 미숙달이면 잠김"
    assert "프롬프트 쓰기" not in names


def test_mastery_particle_after_confirms(fresh_db):
    """확인 3회 정답 → mastered 입자화 + 개념숙달 이벤트, 선수가 풀리며 다음이 열린다."""
    lm.seed_curriculum()
    now = datetime(2026, 7, 20, 10)
    cid = "concept:생성형_AI란"
    assert lm.mastery_of("아내", cid)["status"] == "unseen"
    lm.record_quiz("아내", cid, True, now)
    assert lm.mastery_of("아내", cid)["status"] == "learning", "1회로는 숙달 아님 (wave)"
    lm.record_quiz("아내", cid, True, now)
    m = lm.record_quiz("아내", cid, True, now)
    assert m["status"] == "mastered" and m["rate"] == 100
    assert fresh_db.events("아내", 1, "개념숙달", now)
    assert "프롬프트 쓰기" in {q["name"] for q in lm.quiz_candidates("아내", 50)}, "선수 충족 → 다음 개념 개방"


def test_honest_wrong_answers_do_not_master(fresh_db):
    """오답이 섞이면(정답률<70%) 숙달로 인정하지 않는다 — 정직한 판정."""
    lm.seed_curriculum()
    now = datetime(2026, 7, 20)
    cid = "concept:세포와_기관"
    for ok in (True, False, True, False):
        lm.record_quiz("나", cid, ok, now)
    assert lm.mastery_of("나", cid)["status"] == "learning"


def test_learning_page(fresh_db):
    from fastapi.testclient import TestClient
    from server.main import app
    c = TestClient(app)
    page = c.get("/learning").text
    assert "학습 마스터" in page and "AI 활용" in page and "다음 걸음" in page
