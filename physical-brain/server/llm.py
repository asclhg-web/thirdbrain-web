"""LLM 연결 계층 — Ollama 래퍼 + 규칙 기반 폴백.

2차 이관: LLM_BASE_URL 만 GPU 서버 주소로 바꾸면 된다 (코드 변경 없음).
LLM_MODEL 이 비어 있거나 서버 불가 시 → 규칙 기반 문장 생성 폴백(오프라인 원칙).
"""
import os

import httpx

LIBRARIAN_SYSTEM = (
    "너는 개인 건강 데이터의 '사서'다. 반드시 지켜라: "
    "1) 진단하지 않는다 — 병명을 단정하지 말고, 기준 초과 시 '진료 시 이 기록을 보여주세요'라고 안내한다. "
    "2) 처방하지 않는다 — 약의 추가·중단·용량 변경을 제안하지 않는다. "
    "3) 응급을 판단하지 않는다. "
    "4) 불안을 조장하지 않는다 — 기본 어조는 격려다. "
    "5) 상관과 인과를 구분한다 — n=1 데이터에서 인과를 단정하지 않는다. "
    "6) 주어진 데이터에 없는 수치를 지어내지 않는다."
)


def available() -> bool:
    if not os.environ.get("LLM_MODEL"):
        return False
    try:
        base = os.environ.get("LLM_BASE_URL", "http://localhost:11434")
        r = httpx.get(f"{base}/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def chat(system: str, user: str, timeout: float = 60) -> str:
    """LLM 호출. 불가 시 RuntimeError — 호출부가 폴백을 책임진다."""
    base = os.environ.get("LLM_BASE_URL", "http://localhost:11434")
    model = os.environ.get("LLM_MODEL", "")
    if not model:
        raise RuntimeError("LLM_MODEL 미설정")
    r = httpx.post(f"{base}/api/chat", json={
        "model": model, "stream": False,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }, timeout=timeout)
    r.raise_for_status()
    return r.json()["message"]["content"]


def compose(system: str, user: str, fallback: str) -> str:
    """LLM이 있으면 다듬은 문장, 없으면 규칙 기반 폴백 문장 그대로."""
    try:
        if available():
            return chat(system, user)
    except Exception:
        pass
    return fallback
