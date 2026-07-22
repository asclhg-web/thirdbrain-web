"""R03+R04 검증: 분야팩 인제스트·자기시험 — 정답+근거 이중 채점, 인증 게이트."""
from datetime import datetime

from robot_lms import domain
from server.librarian import answer


def test_care_pack_builds_items_from_graph(fresh_db):
    """그래프(볼트의 거울)에서 문항이 자동 생성된다 — 규칙·주의사항·복용자 관계."""
    p = domain.create_pack("건강 돌봄", "care")
    items = domain.build_items(p)
    assert len(items) >= 4
    assert all(i["question"] and i["keys"] for i in items)
    qs = " ".join(i["question"] for i in items)
    assert "약 일정" in qs and "누가 먹고" in qs
    assert not any("혈압약" in i["question"] for i in items
                   if "누가" in i["question"]), "사서 의도와 충돌하는 약 이름은 관계 문항 제외"


def test_self_test_with_librarian_certifies(fresh_db):
    """실제 사서 파이프라인(규칙 기반, 오프라인)이 응시 → 전 문항 근거와 함께 통과."""
    p = domain.create_pack("건강 돌봄", "care")
    r = domain.self_test(p["id"], lambda q: answer(q, datetime(2026, 7, 22, 10)),
                         datetime(2026, 7, 22, 10))
    assert r["rate"] == 100 and r["evidence_rate"] == 100
    assert r["certified"] is True
    assert domain.open_domains() == ["건강 돌봄"], "인증된 분야만 대화가 열린다"


def test_correct_without_evidence_is_not_certified(fresh_db):
    """근거 없는 정답은 인정하지 않는다 — 지어낸 정답과 구분할 수 없기 때문(헌장 제2원칙)."""
    p = domain.create_pack("건강 돌봄", "care")

    def echo_no_evidence(q):
        keys = [k for i in domain.build_items(p) if i["question"] == q for k in i["keys"]]
        return {"answer": "정답은 " + ", ".join(keys) + " 입니다.", "evidence": []}

    r = domain.self_test(p["id"], echo_no_evidence, datetime(2026, 7, 22, 10))
    assert r["rate"] == 0, "근거 없으면 정답이어도 통과가 아니다"
    assert r["evidence_rate"] == 0 and r["certified"] is False
    assert domain.open_domains() == []
    d = domain.latest_test_detail()
    assert all(i["status"] == "no_evidence" for i in d["items"])


def test_failing_robot_stays_studying(fresh_db):
    """오답 로봇은 '공부 중' — 재시험으로 이력이 쌓이고 인증 상태가 갱신된다."""
    p = domain.create_pack("건강 돌봄", "care")
    domain.self_test(p["id"], lambda q: {"answer": "모르겠습니다.", "evidence": []},
                     datetime(2026, 7, 22, 9))
    assert domain.packs()[0]["certified"] == 0
    domain.self_test(p["id"], lambda q: answer(q, datetime(2026, 7, 22, 10)),
                     datetime(2026, 7, 22, 10))
    assert domain.packs()[0]["certified"] == 1, "통과하면 개방 상태로 갱신"


def test_robot_page_shows_packs(fresh_db):
    from fastapi.testclient import TestClient
    from server.main import app
    c = TestClient(app)
    assert "분야팩" in c.get("/robot").text
    c.post("/robot/pack/create", data={"name": "건강 돌봄", "kind": "care"})
    c.post("/robot/pack/1/test")
    page = c.get("/robot").text
    assert "건강 돌봄" in page and "대화 개방" in page and "자기시험 상세" in page
