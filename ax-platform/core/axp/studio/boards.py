"""M3-3 보드 2종 — 현장(폐기·결품·정지)·경영(KPI). demo: 정적 HTML.

prod: 같은 쿼리를 Superset 데이터셋으로 등록한다(지표 정의는 계약을 따른다).
5초 규칙: 상단에 이상 신호 요약부터.
"""
from __future__ import annotations

from .. import config, db

CSS = """<style>
body{font-family:'Noto Sans CJK KR',sans-serif;margin:24px;background:#F8F2EA;color:#2E241C}
h1{color:#6E3A1C} .cards{display:flex;gap:14px;flex-wrap:wrap;margin:14px 0}
.card{background:#fff;border:1px solid #DCCDBB;border-radius:10px;padding:14px 18px;min-width:150px}
.card b{font-size:24px} .bad b{color:#A8493B} .ok b{color:#0E8F86}
table{border-collapse:collapse;background:#fff;margin:10px 0}
td,th{border:1px solid #DCCDBB;padding:6px 12px;font-size:14px}
th{background:#6E3A1C;color:#fff} .warn{background:#FDECEA}
small{color:#76675A}</style>"""


def _kpi(label, value, bad=False, unit=""):
    cls = "bad" if bad else "ok"
    return f'<div class="card {cls}">{label}<br><b>{value}</b> <small>{unit}</small></div>'


def field_board(run_date: str) -> str:
    """현장 보드 — 오늘·어제의 폐기·결품 신호·정지."""
    scrap_t = db.scalar("SELECT COALESCE(SUM(qty),0) FROM fact_inventory_move "
                        "WHERE move_type='scrap' AND date_key=?", (run_date,)) or 0
    prev = db.scalar("SELECT date_key FROM dim_calendar WHERE date_key<? "
                     "ORDER BY date_key DESC LIMIT 1", (run_date,))
    scrap_y = db.scalar("SELECT COALESCE(SUM(qty),0) FROM fact_inventory_move "
                        "WHERE move_type='scrap' AND date_key=?", (prev,)) or 0
    defect = db.scalar("SELECT COALESCE(SUM(qty_defect),0) FROM fact_defect WHERE date_key=?",
                       (run_date,)) or 0
    stops = db.scalar("SELECT COALESCE(SUM(duration_min),0) FROM fact_equipment_event "
                      "WHERE date_key=? AND event_type LIKE '%수리%'", (run_date,)) or 0
    lines = db.df("""
        SELECT p.line_id, SUM(p.qty_planned) AS 생산, COALESCE(SUM(d.qty_defect),0) AS 불량
        FROM fact_production p LEFT JOIN fact_defect d USING (mo_ref)
        WHERE p.date_key=? GROUP BY p.line_id""", (run_date,))
    rows = "".join(
        f"<tr{' class=warn' if r.불량/max(r.생산,1)>0.03 else ''}>"
        f"<td>{r.line_id}</td><td>{int(r.생산):,}</td><td>{int(r.불량):,}</td>"
        f"<td>{r.불량/max(r.생산,1):.1%}</td></tr>"
        for r in lines.itertuples())
    html = f"""<!doctype html><meta charset="utf-8"><title>현장 보드</title>{CSS}
<h1>현장 보드 — {run_date}</h1>
<div class="cards">
{_kpi("오늘 폐기", f"{int(scrap_t):,}", scrap_t > scrap_y * 1.3, "EA")}
{_kpi("어제 폐기", f"{int(scrap_y):,}", False, "EA")}
{_kpi("오늘 불량", f"{int(defect):,}", False, "EA")}
{_kpi("설비 정지", f"{int(stops)}", stops > 0, "분")}
</div>
<table><tr><th>라인</th><th>생산</th><th>불량</th><th>불량률</th></tr>{rows}</table>
<small>지표 정의: registry/contracts (계약 기준) · 자동 생성 보드</small>"""
    out = config.ARTIFACTS / "boards"
    out.mkdir(parents=True, exist_ok=True)
    p = out / "field_board.html"
    p.write_text(html, encoding="utf-8")
    return str(p)


def exec_board(run_date: str, days: int = 28) -> str:
    """경영 보드 — 최근 4주 KPI 추세와 목표 대비."""
    start = db.scalar("SELECT MIN(date_key) FROM (SELECT date_key FROM dim_calendar "
                      "WHERE date_key<=? ORDER BY date_key DESC LIMIT ?)", (run_date, days))
    rev = db.scalar("SELECT COALESCE(SUM(revenue),0) FROM fact_sales "
                    "WHERE date_key BETWEEN ? AND ?", (start, run_date)) or 0
    qty = db.scalar("SELECT COALESCE(SUM(qty),0) FROM fact_sales "
                    "WHERE date_key BETWEEN ? AND ?", (start, run_date)) or 1
    scrap = db.scalar("SELECT COALESCE(SUM(qty),0) FROM fact_inventory_move "
                      "WHERE move_type='scrap' AND date_key BETWEEN ? AND ?",
                      (start, run_date)) or 0
    prod = db.scalar("SELECT COALESCE(SUM(qty_planned),0) FROM fact_production "
                     "WHERE date_key BETWEEN ? AND ?", (start, run_date)) or 1
    defect = db.scalar("SELECT COALESCE(SUM(qty_defect),0) FROM fact_defect "
                       "WHERE date_key BETWEEN ? AND ?", (start, run_date)) or 0
    weekly = db.df("""
        SELECT substr(date_key,1,7) AS 월, SUM(revenue) AS 매출
        FROM fact_sales GROUP BY substr(date_key,1,7) ORDER BY 월 DESC LIMIT 6""")
    rows = "".join(f"<tr><td>{r.월}</td><td>{int(r.매출):,}</td></tr>"
                   for r in weekly.itertuples())
    html = f"""<!doctype html><meta charset="utf-8"><title>경영 보드</title>{CSS}
<h1>경영 보드 — 최근 {days}일 ({start} ~ {run_date})</h1>
<div class="cards">
{_kpi("매출", f"{int(rev):,}", False, "원")}
{_kpi("폐기율", f"{scrap / qty:.1%}", scrap / qty > 0.04)}
{_kpi("불량률", f"{defect / prod:.1%}", defect / prod > 0.02)}
{_kpi("일평균 판매", f"{int(qty / days):,}", False, "EA")}
</div>
<h2>월별 매출</h2>
<table><tr><th>월</th><th>매출(원)</th></tr>{rows}</table>
<small>지표 정의: registry/contracts · 자동 생성 보드</small>"""
    out = config.ARTIFACTS / "boards"
    out.mkdir(parents=True, exist_ok=True)
    p = out / "exec_board.html"
    p.write_text(html, encoding="utf-8")
    return str(p)
