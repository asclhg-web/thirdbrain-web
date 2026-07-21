"""학습 마스터 (G08-L) — 지식의 BOM: 커리큘럼 온톨로지 + 숙달 판정.

구조: Subject(과목) ← Topic(영역) ← Concept(개념), Concept 간 PREREQUISITE_OF.
숙달 판정은 PTGDA의 이식: 확인(퀴즈 정답)이 누적되어 임계(3회·70%)를 넘는 순간
'학습중(wave)' → '숙달(particle)'로 입자화된다. 본 것과 아는 것을 구분한다.

스타터 커리큘럼은 Frame(공통 지식 지도)의 씨앗 — 국가 교육과정 전체 이식은
확장 단계에서 JSON으로 교체/증분한다. 개인 특화 주제는 기존 Skill 노드를 쓴다.
"""
from datetime import datetime

from graph import store

MASTER_MIN_CONFIRM = 3
MASTER_MIN_RATE = 0.7

# (과목, 영역, 개념, 선수개념(같은 리스트 내 이름) 리스트, 확인 질문)
CURRICULUM = [
    ("수학", "수와 연산", "자연수의 사칙연산", [], "자연수 사칙연산(덧셈~나눗셈)을 설명할 수 있나요?"),
    ("수학", "수와 연산", "분수와 소수", ["자연수의 사칙연산"], "분수를 소수로 바꾸는 법을 설명할 수 있나요?"),
    ("수학", "문자와 식", "일차방정식", ["분수와 소수"], "일차방정식 2x+3=7을 풀 수 있나요?"),
    ("수학", "함수", "함수의 개념", ["일차방정식"], "함수가 무엇인지 예를 들어 설명할 수 있나요?"),
    ("수학", "확률과 통계", "평균과 표준편차", ["분수와 소수"], "평균과 표준편차의 차이를 설명할 수 있나요?"),
    ("과학", "생명", "세포와 기관", [], "세포-조직-기관의 관계를 설명할 수 있나요?"),
    ("과학", "생명", "혈압과 순환", ["세포와 기관"], "수축기/이완기 혈압이 무엇인지 설명할 수 있나요?"),
    ("AI 활용", "기초", "생성형 AI란", [], "챗GPT·제미나이가 무엇을 하는 도구인지 설명할 수 있나요?"),
    ("AI 활용", "기초", "프롬프트 쓰기", ["생성형 AI란"], "원하는 결과를 얻는 질문(프롬프트)을 만들 수 있나요?"),
    ("AI 활용", "실전", "AI로 요리 레시피 찾기", ["프롬프트 쓰기"], "AI에게 재료 기반 레시피를 요청할 수 있나요?"),
    ("AI 활용", "안전", "개인정보 지키며 쓰기", ["생성형 AI란"], "AI에 넣으면 안 되는 정보를 구분할 수 있나요?"),
]


def _cid(name: str) -> str:
    return f"concept:{name.replace(' ', '_')}"


def seed_curriculum() -> dict:
    """스타터 커리큘럼을 그래프에 심는다(멱등). Frame의 씨앗."""
    made = 0
    for subject, topic, concept, prereqs, question in CURRICULUM:
        sid, tid, cid = f"subject:{subject}", f"topic:{subject}:{topic}", _cid(concept)
        store.upsert_node(sid, "Subject", {"name": subject, "source": "curriculum"})
        store.upsert_node(tid, "Topic", {"name": topic, "source": "curriculum"})
        store.upsert_node(cid, "Concept", {"name": concept, "question": question,
                                           "source": "curriculum"})
        store.upsert_edge(tid, "PART_OF", sid)
        store.upsert_edge(cid, "PART_OF", tid)
        for p in prereqs:
            store.upsert_edge(_cid(p), "PREREQUISITE_OF", cid)
        made += 1
    return {"concepts": made}


def mastery_of(person: str, concept_id: str) -> dict:
    """wave/particle 이중 표현: {confirm, total, rate, status}."""
    e = store.get_edge(store.person_id(person), "MASTERS", concept_id) or {}
    confirm, total = int(e.get("confirm", 0)), int(e.get("total", 0))
    rate = confirm / total if total else 0.0
    status = "mastered" if (total >= MASTER_MIN_CONFIRM and rate >= MASTER_MIN_RATE) \
        else ("learning" if total else "unseen")
    return {"confirm": confirm, "total": total, "rate": round(rate * 100), "status": status}


def record_quiz(person: str, concept_id: str, correct: bool,
                now: datetime | None = None) -> dict:
    """확인 1회 누적 — 임계를 넘는 순간 숙달로 입자화 (기록은 이벤트로도 남긴다)."""
    now = now or datetime.now()
    pid = store.person_id(person)
    if not store.get_node(pid):
        store.upsert_node(pid, "Person", {"name": person})
    e = store.get_edge(pid, "MASTERS", concept_id) or {"confirm": 0, "total": 0}
    e["total"] = int(e["total"]) + 1
    e["confirm"] = int(e["confirm"]) + (1 if correct else 0)
    e["last_at"] = now.isoformat()
    store.upsert_edge(pid, "MASTERS", concept_id, e)
    m = mastery_of(person, concept_id)
    if m["status"] == "mastered" and e["total"] == MASTER_MIN_CONFIRM + (0 if correct else 1):
        from server.events import record_event
        c = store.get_node(concept_id)
        record_event(person, "개념숙달", c["props"].get("name", concept_id), now)
    return m


def _prereqs_met(person: str, concept_id: str) -> bool:
    for _r, pre in store.neighbors(concept_id, "PREREQUISITE_OF", "in"):
        if mastery_of(person, pre["id"])["status"] != "mastered":
            return False
    return True


def quiz_candidates(person: str, n: int = 20) -> list[dict]:
    """진단/학습 퀴즈 대상 — 선수개념이 충족된 미숙달 개념 (지식의 지도 위 '다음 걸음')."""
    out = []
    for c in store.nodes_by_type("Concept"):
        m = mastery_of(person, c["id"])
        if m["status"] == "mastered":
            continue
        if _prereqs_met(person, c["id"]):
            out.append({"id": c["id"], "name": c["props"].get("name", ""),
                        "question": c["props"].get("question", ""), **m})
    return out[:n]


def progress(person: str) -> list[dict]:
    """과목별 진행: 숙달/전체 — 학습 마스터의 관리도 재료."""
    subs = {}
    for c in store.nodes_by_type("Concept"):
        topic = next((t for _r, t in store.neighbors(c["id"], "PART_OF")), None)
        subject = next((s for _r, s in store.neighbors(topic["id"], "PART_OF")), None) if topic else None
        sname = subject["props"]["name"] if subject else "기타"
        d = subs.setdefault(sname, {"subject": sname, "total": 0, "mastered": 0, "learning": 0})
        d["total"] += 1
        st = mastery_of(person, c["id"])["status"]
        if st == "mastered":
            d["mastered"] += 1
        elif st == "learning":
            d["learning"] += 1
    return sorted(subs.values(), key=lambda d: d["subject"])
