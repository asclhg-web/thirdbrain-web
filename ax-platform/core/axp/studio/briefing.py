"""M3-2/OP-1 아침 브리핑 — 어제의 변화 Top N, 5분 안에 읽는다.

규칙: 변화만 보고한다. 원인 단정 금지('~와 함께'). 모든 수치에 원천 표기.
"""
from __future__ import annotations

import json

from .. import config, db
from . import mining


def build(run_date: str) -> str:
    lines = [f"# 아침 브리핑 — {run_date}", ""]

    # 품질 이상은 최상단 경보
    q = db.one("SELECT * FROM quality_reports ORDER BY report_date DESC LIMIT 1")
    if q and not q["ok"]:
        lines += ["> ⚠️ **품질 경보** — 어제 품질 리포트에 위반이 있습니다. "
                  "(원천: quality_reports)", ""]

    changes = db.query("SELECT * FROM mining_changes WHERE run_date=? ORDER BY rank",
                       (run_date,))
    lines.append(f"## 어제의 변화 Top {len(changes)}")
    if not changes:
        lines.append("- 보고할 유의 변화 없음 (기준: ±25% 이상)")
    for c in changes:
        where = f" · 위치: {c['where_4m']}" if c["where_4m"] else ""
        arrow = "▲" if c["delta_pct"] > 0 else "▼"
        lines.append(
            f"- **{c['what']}** {arrow} {abs(c['delta_pct']):.0f}% "
            f"({c['prev']:.0f} → {c['value']:.0f}){where} — 다음 액션: 현장 확인 후 "
            f"층별 조회(EDA) 권장 (원천: mining_changes)")
    lines.append("")

    cands = db.query(
        "SELECT * FROM mining_candidates WHERE run_date=? ORDER BY z DESC LIMIT 3",
        (run_date,))
    if cands:
        lines.append("## 야간 마이닝 — 함께 나타난 조합(원인 아님, 후보)")
        for c in cands:
            dims = json.loads(c["dims"])
            where = " × ".join(f"{k}={v}" for k, v in dims.items())
            lines.append(
                f"- {where}: 불량률 {c['rate']:.1%} (기준 {c['base_rate']:.1%}, "
                f"×{c['lift']:.1f}, z={c['z']:.1f}) — 지식그래프 후보로 전달됨 "
                f"(원천: mining_candidates)")
        lines.append("")

    from . import knowledge
    surges = knowledge.surges(run_date)
    if surges:
        lines.append("## 현장의 말 — 이번 주 급증 키워드")
        for s in surges[:5]:
            lines.append(f"- \"{s['keyword']}\" {int(s['prev'])}→{s['n']}회 — "
                         f"현장 기록 원문은 검색으로 (원천: 메모 말뭉치)")
        lines.append("")

    if db.table_exists("judgment_cards"):
        pend = db.query(
            "SELECT approver, COUNT(*) AS n FROM judgment_cards "
            "WHERE status IN ('proposed','review') GROUP BY approver")
        if pend:
            lines.append("## 대기 중 판단 카드")
            for p in pend:
                lines.append(f"- {p['approver']}: {p['n']}건 승인 대기 (원천: judgment_cards)")
            lines.append("")

    lines.append("_이 브리핑은 야간 마이닝 배치가 자동 생성했습니다 — 변화만 담고, "
                 "원인은 단정하지 않습니다._")
    text = "\n".join(lines)
    out = config.ARTIFACTS / "briefings"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"briefing_{run_date}.md").write_text(text, encoding="utf-8")
    return text


def run_nightly_and_brief(run_date: str) -> str:
    """스케줄러 진입점 — 마이닝 후 브리핑."""
    mining.nightly(run_date)
    return build(run_date)
