"""R05 대화 개방 게이트 — 인증된 분야만 로봇이 대화한다.

동작 (제안서 v2 3장):
- 질문이 분야팩 영역이면: 인증됨 → 사서 파이프라인으로 근거와 함께 답한다.
  미인증 → "아직 공부 중이에요 (자기시험 n%)" 정직한 후퇴. 지어내지 않는다.
- 분야 밖 질문은 기반지능(L1) 영역: L1 인증 후에만 일반 대화를 연다.

적용 범위: 이 게이트는 로봇 페르소나의 대화 표면에만 적용된다.
주인의 데이터 사서(/api/ask·홈 질문)와 안전망·복약 알림은 게이트 밖이다 —
로봇이 공부 중이어도 돌봄은 멈추지 않는다.
"""
import re
from datetime import datetime

from robot_lms import domain, exam

# 팩 종류 → 분야 대화로 분류할 질문 패턴 (팩이 늘면 여기에 추가)
DOMAIN_PATTERNS = {
    "care": r"약|복약|혈압|혈당|수면|잠|HRV|측정|건강|돌봄|준수",
}


def classify(question: str) -> dict | None:
    """질문이 속한 분야팩을 찾는다 — 없으면 기반지능(L1) 영역."""
    for p in domain.packs():
        pat = DOMAIN_PATTERNS.get(p["kind"])
        if pat and re.search(pat, question):
            return p
    return None


def _l1_certified() -> bool:
    card = exam.report_card()
    return bool(card["latest"] and card["latest"]["certified"])


def converse(question: str, now: datetime | None = None) -> dict:
    """로봇 대화 1턴 — {mode, domain, answer, evidence}. 미인증이면 정직하게 물러선다."""
    now = now or datetime.now()
    pack = classify(question)

    if pack:  # ── 분야 대화 (L2) ──
        if pack["certified"]:
            from server import librarian
            r = librarian.answer(question, now)
            return {"mode": "domain", "domain": pack["name"],
                    "answer": r["answer"], "evidence": r.get("evidence", [])}
        if pack["last_rate"] is None:
            text = (f"'{pack['name']}' 분야는 아직 자기시험을 보기 전이에요. "
                    "공부가 끝나고 인증을 통과하면 이 분야 대화를 열게요.")
        else:
            text = (f"'{pack['name']}' 분야는 아직 공부 중이에요 "
                    f"(자기시험 {pack['last_rate']}%, 근거 인용 {pack['last_evidence_rate']}%). "
                    "인증(90% 이상 + 근거 100%)을 통과하면 이 분야 대화를 열게요.")
        return {"mode": "studying", "domain": pack["name"], "answer": text, "evidence": []}

    # ── 기반지능 영역 (L1) ──
    if not _l1_certified():
        return {"mode": "l1_uncertified", "domain": None, "evidence": [],
                "answer": "아직 기반 검정(L1)을 통과하지 못했어요 — 검정부터 볼게요. "
                          "로봇 화면에서 '검정 응시 시작'을 눌러주세요."}
    from server import llm
    fallback = ("일반 지식 대화는 서버의 LLM이 답해요 — 지금은 연결되어 있지 않네요. "
                "분야 질문(예: 오늘 약 일정)은 언제든 물어보세요.")
    text = llm.compose(exam.ROBOT_SYSTEM + " 이제 시험이 아니라 주인과의 일상 대화다. "
                       "친절하고 짧게 답하되, 모르는 것은 모른다고 말하라.",
                       question, fallback=fallback)
    return {"mode": "general", "domain": None, "answer": text, "evidence": []}
