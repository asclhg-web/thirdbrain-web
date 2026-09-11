"""M7-3 War Room — 카드 처리율·승인율·반려 사유·효과 KPI·드리프트 한 화면."""
from __future__ import annotations

import json

from .. import config, db
from ..learn import drift

CSS = """<style>
body{font-family:'Noto Sans CJK KR',sans-serif;margin:24px;background:#2B1D12;color:#F8F2EA}
h1{color:#E8A33D} h2{color:#D8C6B2;margin-top:28px}
.cards{display:flex;gap:14px;flex-wrap:wrap;margin:14px 0}
.card{background:#3E2C1D;border-radius:10px;padding:14px 20px;min-width:160px}
.card b{font-size:26px;color:#E8A33D} .card small{color:#D8C6B2}
table{border-collapse:collapse;background:#3E2C1D;margin:8px 0}
td,th{border:1px solid #5a4632;padding:6px 12px;font-size:14px;color:#F8F2EA}
th{background:#6E3A1C} .warn{color:#E8A33D}</style>"""


def metrics(as_of: str) -> dict:
    from ..judge import cards as _jc
    db.executescript(_jc.DDL)
    total = db.scalar("SELECT COUNT(*) FROM judgment_cards") or 0
    by_status = {r["status"]: r["n"] for r in db.query(
        "SELECT status, COUNT(*) n FROM judgment_cards GROUP BY status")}
    decided = sum(by_status.get(s, 0) for s in ("approved", "rejected", "executed"))
    approved = by_status.get("approved", 0) + by_status.get("executed", 0)
    reasons = db.query(
        "SELECT reason_code, COUNT(*) n FROM reject_feedback GROUP BY reason_code "
        "ORDER BY n DESC") if db.table_exists("reject_feedback") else []
    agent_runs = db.query(
        "SELECT agent, COUNT(*) runs, SUM(cards_created) cards, "
        "SUM(CASE WHEN status='error' THEN 1 ELSE 0 END) errors FROM agent_runs GROUP BY agent") \
        if db.table_exists("agent_runs") else []
    funnel = {}
    if db.table_exists("causal_candidates"):
        # P2: 지식 퍼널 — 마이닝 후보의 거짓 양성률 추적(M3)
        f = {r["status"]: r["n"] for r in db.query(
            "SELECT status, COUNT(*) n FROM causal_candidates GROUP BY status")}
        resolved = f.get("promoted", 0) + f.get("rejected", 0) + f.get("demoted", 0)
        funnel = {"watching": f.get("watching", 0), "submitted": f.get("submitted", 0),
                  "promoted": f.get("promoted", 0), "rejected": f.get("rejected", 0),
                  "demoted": f.get("demoted", 0),
                  "fp_rate": round((f.get("rejected", 0) + f.get("demoted", 0))
                                    / resolved, 3) if resolved else None}
    risks = []
    if db.table_exists("risk_reports"):
        latest = db.scalar("SELECT MAX(run_at) FROM risk_reports")
        if latest:
            risks = db.query("SELECT risk_id, level, metric, action FROM risk_reports "
                             "WHERE run_at=?", (latest,))
    kpi = {}
    if db.table_exists("fact_sales"):
        kpi["scrap_28d"] = db.scalar(
            "SELECT COALESCE(SUM(qty),0) FROM fact_inventory_move WHERE move_type='scrap' "
            "AND date_key BETWEEN date(?,'-27 days') AND ?", (as_of, as_of))
        kpi["defect_28d"] = db.scalar(
            "SELECT COALESCE(SUM(qty_defect),0) FROM fact_defect "
            "WHERE date_key BETWEEN date(?,'-27 days') AND ?", (as_of, as_of))
    try:
        dr = drift.input_drift(as_of)
        kpi["drift_alerts"] = int((dr["level"] == "경보").sum())
        drift_rows = dr.head(5).to_dict("records")
    except Exception:
        kpi["drift_alerts"] = 0
        drift_rows = []
    return {"as_of": as_of, "total_cards": total, "by_status": by_status,
            "processing_rate": (decided / total) if total else 0,
            "approval_rate": (approved / decided) if decided else 0,
            "reject_reasons": reasons, "funnel": funnel, "agent_runs": agent_runs,
            "kpi": kpi, "drift_top": drift_rows, "risks": risks}


def render(as_of: str) -> str:
    # P5-SEC1: 이 파일은 웹앱이 그대로 서빙한다 — DB 유래 값도 전부 이스케이프
    # (반려 사유 등은 사용자 입력에서 왔다). as_of 반사도 동일.
    from html import escape as _e
    m = metrics(as_of)
    as_of = _e(str(as_of))          # 이후의 HTML 삽입용(질의는 원값으로 이미 수행)
    reason_rows = "".join(f"<tr><td>{_e(str(r['reason_code']))}</td><td>{r['n']}</td></tr>"
                          for r in m["reject_reasons"]) or "<tr><td colspan=2>없음</td></tr>"
    agent_rows = "".join(
        f"<tr><td>{_e(str(r['agent']))}</td><td>{r['runs']}</td><td>{r['cards'] or 0}</td>"
        f"<td class={'warn' if r['errors'] else ''}>{r['errors'] or 0}</td></tr>"
        for r in m["agent_runs"]) or "<tr><td colspan=4>없음</td></tr>"
    drift_rows = "".join(
        f"<tr><td>{_e(str(r['feature']))}</td><td>{r['psi']}</td><td>{_e(str(r['level']))}</td></tr>"
        for r in m["drift_top"]) or "<tr><td colspan=3>-</td></tr>"
    mark = {"녹": "🟢", "황": "🟡", "적": "🔴"}
    risk_rows = "".join(
        f"<tr><td>{_e(str(r['risk_id']))}</td><td>{mark.get(r['level'], '')} {_e(str(r['level']))}</td>"
        f"<td>{_e(str(r['metric']))}</td><td>{_e(str(r['action'] or '—'))}</td></tr>"
        for r in m["risks"]) or "<tr><td colspan=4>점검 이력 없음(격주)</td></tr>"
    status_rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>"
                          for k, v in sorted(m["by_status"].items()))
    fn = m.get("funnel") or {}
    funnel_w, funnel_s = fn.get("watching", 0), fn.get("submitted", 0)
    funnel_p, funnel_r, funnel_d = fn.get("promoted", 0), fn.get("rejected", 0), fn.get("demoted", 0)
    funnel_fp = f"{fn['fp_rate']:.0%}" if fn.get("fp_rate") is not None else "—"
    html = f"""<!doctype html><meta charset="utf-8"><title>War Room</title>{CSS}
<h1>War Room — {as_of}</h1>
<div class="cards">
<div class="card">카드 총수<br><b>{m['total_cards']}</b></div>
<div class="card">처리율<br><b>{m['processing_rate']:.0%}</b></div>
<div class="card">승인율<br><b>{m['approval_rate']:.0%}</b></div>
<div class="card">28일 폐기<br><b>{m['kpi'].get('scrap_28d', 0):,.0f}</b> <small>EA</small></div>
<div class="card">28일 불량<br><b>{m['kpi'].get('defect_28d', 0):,.0f}</b> <small>EA</small></div>
<div class="card">드리프트 경보<br><b>{m['kpi'].get('drift_alerts', 0)}</b></div>
</div>
<h2>카드 상태</h2><table><tr><th>상태</th><th>건수</th></tr>{status_rows}</table>
<h2>반려 사유 분포</h2><table><tr><th>사유</th><th>건수</th></tr>{reason_rows}</table>
<h2>에이전트 가동</h2><table><tr><th>에이전트</th><th>실행</th><th>카드</th><th>오류</th></tr>{agent_rows}</table>
<h2>지식 퍼널 — 원인 후보의 생애</h2>
<table><tr><th>관찰</th><th>상신</th><th>승격</th><th>반려</th><th>강등</th><th>거짓 양성률</th></tr>
<tr><td>{funnel_w}</td><td>{funnel_s}</td><td>{funnel_p}</td><td>{funnel_r}</td><td>{funnel_d}</td><td><b>{funnel_fp}</b></td></tr></table>
<h2>입력 드리프트 상위</h2><table><tr><th>특징</th><th>PSI</th><th>수준</th></tr>{drift_rows}</table>
<h2>리스크 5 (격주 자동 점검)</h2><table><tr><th>리스크</th><th>판정</th><th>관측 지표</th><th>대응</th></tr>{risk_rows}</table>
<p><small>주간 리뷰 순서: ① 상단 KPI ② 반려 사유 → 개선 안건 ③ 에이전트 오류 ④ 드리프트 → 재학습 판정 ⑤ 승급/강등 결정</small></p>"""
    out = config.ARTIFACTS / "boards"
    out.mkdir(parents=True, exist_ok=True)
    p = out / "war_room.html"
    p.write_text(html, encoding="utf-8")
    return str(p)
