"""M6-1 검증 질의 10선 회귀 시험 — 모든 배포의 통과 조건.

각 질의는 기대 조건(expect)을 가진다: 반드시 포함할 참조/문구.
스튜어드와 확정한 목록 — 변경은 레지스트리 PR로.
"""
from __future__ import annotations

from ..graph import confidence, evidence
from . import assembler


def _first_rule() -> str:
    rules = confidence.rules("promoted")
    if not rules:
        raise ValueError("승격 규칙 없음")
    return rules[0]["rule_id"]

GOLDEN = [
    {"id": 1, "q": "OVEN-2 불량의 원인 후보는?",
     "run": lambda: assembler.answer("OVEN-2 원인", assembler.search_cause("OVEN-2")),
     "expect": ["OVEN-2", "[근거:"]},
    {"id": 2, "q": "승격된 규칙 목록은?",
     "run": lambda: assembler.answer("규칙", assembler.search_rules()),
     "expect": ["RULE-", "[근거:"]},
    {"id": 3, "q": "OVEN-2 정비 이력은?",
     "run": lambda: assembler.answer("이력", assembler.search_history("OVEN-2")),
     "expect": ["고장 수리", "[근거:"]},
    {"id": 4, "q": "V2 공급사 관련 원인 후보는?",
     "run": lambda: assembler.answer("V2", assembler.search_cause("V2")),
     "expect": ["V2", "[근거:"]},
    {"id": 5, "q": "2025-07~08 OVEN-2×V2 불량 수량은?",
     "run": lambda: assembler.answer("수량", assembler.search_numeric(
         "defect_qty", {"equipment_id": "OVEN-2", "vendor": "V2"},
         "2025-07-01", "2025-08-31")),
     "expect": ["defect_qty", "[근거: fact_defect"]},
    {"id": 6, "q": "파이만쥬 최근 30일 판매량은?",
     "run": lambda: assembler.answer("판매", assembler.search_numeric(
         "sales_qty", {"product_id": "P-PIE"}, "2026-08-01", "2026-08-31")),
     "expect": ["sales_qty", "[근거: fact_sales"]},
    {"id": 7, "q": "최근 30일 폐기량은?",
     "run": lambda: assembler.answer("폐기", assembler.search_numeric(
         "scrap_qty", {}, "2026-08-01", "2026-08-31")),
     "expect": ["scrap_qty", "[근거: fact_inventory_move"]},
    {"id": 8, "q": "첫 승격 규칙의 근거 경로는?",
     "run": lambda: evidence.render_path_text(evidence.evidence_for_rule(_first_rule())),
     "expect": ["규칙 Rule:RULE-", "원장 표본"]},
    {"id": 9, "q": "존재하지 않는 설비 OVEN-9의 원인은? (근거 없음 처리)",
     "run": lambda: assembler.answer("OVEN-9", assembler.search_cause("OVEN-9")),
     "expect": ["[근거:"]},
    {"id": 10, "q": "W-03 작업자 관련 원인 후보는?",
     "run": lambda: assembler.answer("W-03", assembler.search_cause("W-03")),
     "expect": ["[근거:"]},
]


def run() -> dict:
    results = []
    for g in GOLDEN:
        try:
            out = g["run"]()
            missing = [e for e in g["expect"] if e not in out]
            results.append({"id": g["id"], "q": g["q"], "pass": not missing,
                            "missing": missing, "answer_head": out.splitlines()[0][:80]})
        except Exception as e:  # noqa: BLE001
            results.append({"id": g["id"], "q": g["q"], "pass": False,
                            "missing": [f"예외: {e}"]})
    n_pass = sum(r["pass"] for r in results)
    return {"pass": n_pass == len(GOLDEN), "n_pass": n_pass,
            "n_total": len(GOLDEN), "results": results}
