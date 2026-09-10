"""M6-3 클라우드 폴백 — 반출 게이트(M0-3)를 지나야만 외부 LLM을 쓴다.

기본은 사내 백엔드. 고난도 판별·민감정보 마스킹·승인·캐시·로그가 전부 강제된다.
"""
from __future__ import annotations

import hashlib
import json
import re

from .. import common, db
from ..custody import export_gate

DDL = """
CREATE TABLE IF NOT EXISTS llm_fallback_cache (
  prompt_sha TEXT PRIMARY KEY, response TEXT, req_id INTEGER, created_at TEXT
);
"""

SENSITIVE_PATTERNS = [
    (re.compile(r"\d{6}-\d{7}"), "[주민번호 차단]"),
    (re.compile(r"01[0-9]-\d{3,4}-\d{4}"), "[전화번호 마스킹]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[이메일 마스킹]"),
]


def is_hard_request(question: str, local_confidence: float) -> bool:
    """고난도 판별 — 사내 확신 낮음 또는 장문 종합 요청."""
    return local_confidence < 0.4 or len(question) > 500


def mask(text: str) -> str:
    for pat, repl in SENSITIVE_PATTERNS:
        text = pat.sub(repl, text)
    return text


def request_cloud(question: str, retrieved: dict, requester: str) -> dict:
    """반출 신청 — 승인 전에는 아무것도 나가지 않는다. 반환: req_id 또는 캐시 응답."""
    db.executescript(DDL)
    payload = mask(json.dumps({"q": question, "facts": retrieved}, ensure_ascii=False))
    sha = hashlib.sha256(payload.encode()).hexdigest()
    hit = db.one("SELECT response FROM llm_fallback_cache WHERE prompt_sha=?", (sha,))
    if hit:
        return {"status": "cache_hit", "response": hit["response"]}
    req_id = export_gate.request(
        what=f"LLM 폴백 질의({len(payload)}자, 마스킹 적용)",
        dest="api.anthropic.com", why="사내 모델 확신 부족 — 고난도 종합",
        requester=requester, payload=payload)
    return {"status": "pending_approval", "req_id": req_id, "payload_sha": sha}


def execute_cloud(req_id: int, question: str, retrieved: dict) -> dict:
    """승인 후 실행 — 게이트 최종 검문 통과 시에만. demo: 호출은 스텁."""
    db.executescript(DDL)
    payload = mask(json.dumps({"q": question, "facts": retrieved}, ensure_ascii=False))
    row = export_gate.check_and_mark_executed(req_id, payload, "api.anthropic.com")
    # prod: 여기서 실제 클라우드 API 호출. demo: 결정적 조립기로 대체 응답.
    from . import assembler
    response = assembler.answer(question, retrieved)
    sha = hashlib.sha256(payload.encode()).hexdigest()
    db.execute("INSERT OR REPLACE INTO llm_fallback_cache VALUES (?,?,?,?)",
               (sha, response, req_id, common.now_iso()))
    return {"status": "executed", "req_id": row["req_id"], "response": response}
