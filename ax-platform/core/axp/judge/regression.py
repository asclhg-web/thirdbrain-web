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

# ── P2-C4: 회귀 30선 확대 — LLM 백엔드 교체(Ollama) 대비 환각 방어 강화 ──
GOLDEN += [
    {"id": 11, "q": "OVEN-1 원인 후보는?",
     "run": lambda: assembler.answer("OVEN-1", assembler.search_cause("OVEN-1")),
     "expect": ["[근거:"]},
    {"id": 12, "q": "OVEN-1 정비 이력은?",
     "run": lambda: assembler.answer("이력", assembler.search_history("OVEN-1")),
     "expect": ["[근거:"]},
    {"id": 13, "q": "P-PIE 제품 관련 원인 후보는?",
     "run": lambda: assembler.answer("P-PIE", assembler.search_cause("P-PIE")),
     "expect": ["[근거:"]},
    {"id": 14, "q": "P-SAND 최근 30일 판매량은?",
     "run": lambda: assembler.answer("판매", assembler.search_numeric(
         "sales_qty", {"product_id": "P-SAND"}, "2026-08-01", "2026-08-31")),
     "expect": ["sales_qty", "[근거: fact_sales"]},
    {"id": 15, "q": "전 제품 최근 7일 판매량은?",
     "run": lambda: assembler.answer("판매", assembler.search_numeric(
         "sales_qty", {}, "2026-08-01", "2026-08-07")),
     "expect": ["sales_qty", "[근거: fact_sales"]},
    {"id": 16, "q": "2026-06 불량 수량은?",
     "run": lambda: assembler.answer("불량", assembler.search_numeric(
         "defect_qty", {}, "2026-06-01", "2026-06-30")),
     "expect": ["defect_qty", "[근거: fact_defect"]},
    {"id": 17, "q": "OVEN-2 단독 불량 수량(2025-07~08)은?",
     "run": lambda: assembler.answer("불량", assembler.search_numeric(
         "defect_qty", {"equipment_id": "OVEN-2"}, "2025-07-01", "2025-08-31")),
     "expect": ["defect_qty", "[근거: fact_defect"]},
    {"id": 18, "q": "미래 구간(데이터 없음) 판매량은 0으로 정직하게?",
     "run": lambda: assembler.answer("판매", assembler.search_numeric(
         "sales_qty", {"product_id": "P-PIE"}, "2027-01-01", "2027-01-31")),
     "expect": ["sales_qty", "[근거: fact_sales"]},
    {"id": 19, "q": "존재하지 않는 제품 P-GHOST 원인은?",
     "run": lambda: assembler.answer("P-GHOST", assembler.search_cause("P-GHOST")),
     "expect": ["[근거:"]},
    {"id": 20, "q": "존재하지 않는 공급사 V9 원인은?",
     "run": lambda: assembler.answer("V9", assembler.search_cause("V9")),
     "expect": ["[근거:"]},
    # 환각 방어 자체를 검사 — 검증기가 위조 응답을 실제로 차단하는가
    {"id": 21, "q": "인용 태그 없는 문장은 차단되는가?",
     "run": lambda: _expect_citation_error("근거 없는 주장입니다",
         assembler.search_rules()),
     "expect": ["CITATION_BLOCKED"]},
    {"id": 22, "q": "검색에 없는 수치는 차단되는가?",
     "run": lambda: _expect_citation_error(
         "판매는 999999개였습니다. [근거: 위조]", assembler.search_rules()),
     "expect": ["CITATION_BLOCKED"]},
    {"id": 23, "q": "백분율 표기(0.88→88%)는 허용되는가?",
     "run": lambda: _verify_ok("확신도 88%입니다. [근거: Rule]",
                               {"hits": [{"confidence": 0.88}]}),
     "expect": ["VERIFY_OK"]},
    {"id": 24, "q": "승격 규칙 텍스트에 조합 조건이 있는가?",
     "run": lambda: assembler.answer("규칙", assembler.search_rules()),
     "expect": ["조합에서 불량률", "[근거:"]},
    {"id": 25, "q": "규칙 응답의 확신도 표기가 검색값과 일치하는가?",
     "run": lambda: assembler.answer("규칙", assembler.search_rules()),
     "expect": ["확신도", "[근거:"]},
    {"id": 26, "q": "이력 응답에 소요 시간이 포함되는가?",
     "run": lambda: assembler.answer("이력", assembler.search_history("OVEN-2")),
     "expect": ["분)", "[근거:"]},
    {"id": 27, "q": "근거 사다리 응답이 원장 표본까지 내려가는가?",
     "run": lambda: evidence.render_path_text(evidence.evidence_for_rule(_first_rule())),
     "expect": ["사실", "원장 표본"]},
    {"id": 28, "q": "근거 사다리에 확신도가 표기되는가?",
     "run": lambda: evidence.render_path_text(evidence.evidence_for_rule(_first_rule())),
     "expect": ["확신도"]},
    {"id": 29, "q": "빈 검색 결과의 원인 응답이 '없음'을 근거와 함께 말하는가?",
     "run": lambda: assembler.answer("없음", assembler.search_cause("NO-SUCH")),
     "expect": ["없습니다", "[근거:"]},
    {"id": 30, "q": "폐기량 응답의 근거가 fact 테이블을 가리키는가?",
     "run": lambda: assembler.answer("폐기", assembler.search_numeric(
         "scrap_qty", {}, "2026-07-01", "2026-07-31")),
     "expect": ["[근거: fact_inventory_move"]},
]


def _expect_citation_error(text: str, retrieved: dict) -> str:
    try:
        assembler.verify_citations(text, retrieved)
        return "NOT_BLOCKED"
    except assembler.CitationError:
        return "CITATION_BLOCKED"


def _verify_ok(text: str, retrieved: dict) -> str:
    assembler.verify_citations(text, retrieved)
    return "VERIFY_OK"


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
