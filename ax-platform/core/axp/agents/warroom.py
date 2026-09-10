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
        "SUM(status='error') errors FROM agent_runs GROUP BY agent") \
        if db.table_exists("agent_runs") else []
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
            "reject_reasons": reasons, "agent_runs": agent_runs,
            "kpi": kpi, "drift_top": drift_rows}


def render(as_of: str) -> str:
    m = metrics(as_of)
    reason_rows = "".join(f"<tr><td>{r['reason_code']}</td><td>{r['n']}</td></tr>"
                          for r in m["reject_reasons"]) or "<tr><td colspan=2>없음</td></tr>"
    agent_rows = "".join(
        f"<tr><td>{r['agent']}</td><td>{r['runs']}</td><td>{r['cards'] or 0}</td>"
        f"<td class={'warn' if r['errors'] else ''}>{r['errors'] or 0}</td></tr>"
        for r in m["agent_runs"]) or "<tr><td colspan=4>없음</td></tr>"
    drift_rows = "".join(
        f"<tr><td>{r['feature']}</td><td>{r['psi']}</td><td>{r['level']}</td></tr>"
        for r in m["drift_top"]) or "<tr><td colspan=3>-</td></tr>"
    status_rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>"
                          for k, v in sorted(m["by_status"].items()))
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
<h2>입력 드리프트 상위</h2><table><tr><th>특징</th><th>PSI</th><th>수준</th></tr>{drift_rows}</table>
<p><small>주간 리뷰 순서: ① 상단 KPI ② 반려 사유 → 개선 안건 ③ 에이전트 오류 ④ 드리프트 → 재학습 판정 ⑤ 승급/강등 결정</small></p>"""
    out = config.ARTIFACTS / "boards"
    out.mkdir(parents=True, exist_ok=True)
    p = out / "war_room.html"
    p.write_text(html, encoding="utf-8")
    return str(p)
