"""OP-5 리스크 5 자동 점검 — 계획서 7.2의 리스크를 관측 지표로 상시 감시.

판정: 녹/황/적. 판정 기준은 코드에 명시(문서와 어긋나면 그것이 부채).
격주 배치가 실행하고, 황·적은 경보 + War Room 안건이 된다.
"""
from __future__ import annotations

import json

from .. import common, db

DDL = """
CREATE TABLE IF NOT EXISTS risk_reports (
  run_at TEXT, risk_id TEXT, level TEXT, metric TEXT, action TEXT
);
"""


def _level(value, yellow, red, higher_is_worse=True):
    if higher_is_worse:
        return "적" if value >= red else ("황" if value >= yellow else "녹")
    return "적" if value <= red else ("황" if value <= yellow else "녹")


def check_all(as_of: str) -> list[dict]:
    db.executescript(DDL)
    out = []

    # R1 엑셀·장표의 무한 다양성 — 격리 큐 적체·신규 양식 유입
    pending = db.scalar(
        "SELECT COALESCE(SUM(n_rows),0) FROM quarantine_queue WHERE status='pending'") or 0
    unmapped = db.scalar(
        "SELECT unmapped_rate FROM quality_reports ORDER BY report_date DESC LIMIT 1") or 0
    lvl = _level(max(pending / 100, unmapped / 0.05), 0.5, 1.0)
    out.append({"risk_id": "R1 양식 다양성", "level": lvl,
                "metric": f"격리 대기 {pending}행 · 미매핑 {unmapped:.1%}",
                "action": "" if lvl == "녹" else "스튜어드 격리 확정 세션 + 표준 폼 전환 독려"})

    # R2 모듈 과설계(플랫폼 병) — 카드로 이어지지 않는 에이전트 실행 비율
    runs = db.scalar("SELECT COUNT(*) FROM agent_runs WHERE status='ok'") or 0
    runs_with_cards = db.scalar(
        "SELECT COUNT(*) FROM agent_runs WHERE status='ok' AND cards_created>0") or 0
    idle_ratio = 1 - (runs_with_cards / runs) if runs else 0
    lvl = _level(idle_ratio, 0.6, 0.85)
    out.append({"risk_id": "R2 과설계", "level": lvl,
                "metric": f"실행 {runs}회 중 카드 산출 {runs_with_cards}회 (무산출 {idle_ratio:.0%})",
                "action": "" if lvl == "녹" else "무산출 에이전트의 요구서 재검토 — 앱 요구 없는 기능 동결"})

    # R3 RL 과속 — Twin 검증 없이 상신된 정책 카드
    twin_cards = db.query(
        "SELECT evidence_json FROM judgment_cards WHERE kind='replenish'")
    unsafe = sum(1 for c in twin_cards
                 if "twin" not in json.loads(c["evidence_json"]).get("kind", ""))
    lvl = "적" if unsafe else "녹"
    out.append({"risk_id": "R3 RL 과속", "level": lvl,
                "metric": f"정책 카드 {len(twin_cards)}건 중 Twin 근거 없음 {unsafe}건",
                "action": "" if lvl == "녹" else "즉시 카드 회수·생성 경로 감사"})

    # R4 LLM 환각 — 회귀 10선 + 인용 차단 로그
    from ..judge import regression
    reg = regression.run()
    lvl = "녹" if reg["pass"] else "적"
    out.append({"risk_id": "R4 환각", "level": lvl,
                "metric": f"회귀 {reg['n_pass']}/{reg['n_total']}",
                "action": "" if lvl == "녹" else "배포 중지 — 실패 질의 원인 분석"})

    # R5 자립 실패 — 스튜어드 단독 수행 실기록(격리 확정·OCR 확정·Rule 승격)
    conf = db.scalar("SELECT COUNT(*) FROM quarantine_queue WHERE status='confirmed'") or 0
    ocr = db.scalar("SELECT COUNT(*) FROM ocr_drafts WHERE status='confirmed'") \
        if db.table_exists("ocr_drafts") else 0
    promoted = db.scalar(
        "SELECT COUNT(*) FROM causal_candidates WHERE status='promoted'") or 0
    solo = sum(1 for x in (conf, ocr, promoted) if x)
    lvl = {3: "녹", 2: "황"}.get(solo, "적")
    out.append({"risk_id": "R5 자립", "level": lvl,
                "metric": f"단독 수행 실기록 {solo}/3종 (격리 {conf}·OCR {ocr}·승격 {promoted})",
                "action": "" if lvl == "녹" else "스튜어드 동석 일정 확대 — W9 전 3종 채우기"})

    ts = common.now_iso()
    db.executemany("INSERT INTO risk_reports VALUES (?,?,?,?,?)",
                   [(ts, r["risk_id"], r["level"], r["metric"], r["action"]) for r in out])
    for r in out:
        if r["level"] != "녹":
            common.alert("warn", "OP-5", f"{r['risk_id']} {r['level']} — {r['metric']}")
    return out


def render_md(reports: list[dict], as_of: str) -> str:
    lines = [f"# 리스크 5 점검 — {as_of}", "",
             "| 리스크 | 판정 | 관측 지표 | 대응 |", "|---|---|---|---|"]
    mark = {"녹": "🟢", "황": "🟡", "적": "🔴"}
    for r in reports:
        lines.append(f"| {r['risk_id']} | {mark[r['level']]} {r['level']} | "
                     f"{r['metric']} | {r['action'] or '—'} |")
    return "\n".join(lines)
