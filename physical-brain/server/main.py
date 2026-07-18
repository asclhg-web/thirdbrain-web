"""피지컬브레인 FastAPI — API + 서버렌더 대시보드 (Jinja2, 오프라인 원칙: 외부 CDN 없음)."""
import math
import os
from datetime import datetime

import yaml
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from graph import store
from server import briefing, librarian, orchestrator
from server.events import adherence
from server.tasks_today import confirm, expand_today, today

app = FastAPI(title="Physical Brain", version="0.1.0")


@app.on_event("startup")
def _start_heartbeat():
    """실서비스 심장박동: 분당 규칙 틱 + 5분마다 볼트 동기화 (PB_HEARTBEAT=0으로 끔)."""
    from server import scheduler
    scheduler.start()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "web", "templates"))
RULES_DIR = orchestrator.RULES_DIR
SIGNALS = [("bp_sys", "수축기 혈압", "mmHg"), ("bp_dia", "이완기 혈압", "mmHg"),
           ("rhr", "안정 심박", "bpm"), ("hrv", "HRV", "ms"), ("glucose_spikes", "혈당 스파이크", "회")]
ACTS = [("sleep", "수면", "h"), ("walk", "걷기", "steps")]


# ---------- API ----------

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/api/ask")
def api_ask(body: dict):
    return librarian.answer(body.get("question", ""))


@app.get("/api/tasks/today")
def api_tasks():
    now = datetime.now()
    expand_today(now)
    return today(now)


@app.post("/api/tasks/{task_id}/confirm")
def api_confirm(task_id: int):
    r = confirm("", datetime.now(), task_id)
    return {"ok": bool(r), "task": r}


@app.get("/api/briefing/today")
def api_briefing(person: str = "나"):
    return {"person": person, "briefing": briefing.morning_briefing(person)}


@app.get("/api/events")
def api_events(person: str = "나", days: int = 7):
    return store.events(person, days)


@app.get("/api/mock/summary")
def api_mock_summary():
    return store.counts()


@app.get("/api/graph")
def api_graph():
    nodes, edges = [], []
    for t in ("Person", "Medication", "Regimen", "Place"):
        for n in store.nodes_by_type(t):
            nodes.append({"id": n["id"], "type": t, "label": n["props"].get("name", n["id"]),
                          "props": n["props"]})
    conn = store.get_conn()
    ids = {n["id"] for n in nodes}
    for r in conn.execute("SELECT src, rel, dst FROM edges").fetchall():
        if r["src"] in ids and r["dst"] in ids:
            edges.append({"src": r["src"], "rel": r["rel"], "dst": r["dst"]})
    # 측정값·이벤트는 개수 배지로 축약
    badges = store.counts()["nodes"]
    return {"nodes": nodes, "edges": edges, "badges": badges}


# ---------- 대시보드 (서버렌더) ----------

def spark_svg(points: list[float], w=560, h=90, missing_ok=True) -> str:
    """서버렌더 SVG 스파크라인. 결측은 선을 끊는다 — 0으로 그리지 않는다."""
    pts = [p for p in points if p is not None]
    if not pts:
        return '<svg width="560" height="90"><text x="10" y="50" fill="#888">데이터 없음</text></svg>'
    lo, hi = min(pts), max(pts)
    rng = (hi - lo) or 1
    seg, path = [], []
    for i, p in enumerate(points):
        if p is None:
            if seg:
                path.append(seg)
                seg = []
            continue
        x = 10 + i * (w - 20) / max(len(points) - 1, 1)
        y = h - 12 - (p - lo) / rng * (h - 30)
        seg.append(f"{x:.1f},{y:.1f}")
    if seg:
        path.append(seg)
    lines = "".join(f'<polyline fill="none" stroke="#4fc0b8" stroke-width="2" points="{" ".join(s)}"/>'
                    for s in path if len(s) > 1)
    dots = "".join(f'<circle cx="{s.split(",")[0]}" cy="{s.split(",")[1]}" r="2.5" fill="#e0a04a"/>'
                   for seg2 in path for s in [seg2[-1]])
    return (f'<svg width="{w}" height="{h}" role="img">{lines}{dots}'
            f'<text x="10" y="{h-2}" fill="#889" font-size="10">min {lo:.0f} · max {hi:.0f}</text></svg>')


@app.get("/", response_class=HTMLResponse)
def home(request: Request, person: str = "아버지"):
    now = datetime.now()
    expand_today(now)
    tasks = [t for t in today(now) if t["person"] == person]
    return templates.TemplateResponse(request, "home.html", {
        "person": person, "people": ["아버지", "나"],
        "briefing": briefing.morning_briefing(person, now),
        "tasks": tasks, "adherence": adherence(person, 7, now),
        "events": list(reversed(store.events(person, 2, None, now)))[:8],
    })


@app.get("/signals", response_class=HTMLResponse)
def signals(request: Request, person: str = "아버지"):
    now = datetime.now()
    charts = []
    for mtype, label, unit in SIGNALS:
        ms = store.measurements(person, mtype, 30, now)
        by_day: dict[str, list] = {}
        for m in ms:
            by_day.setdefault(m["measured_at"][:10], []).append(m["value"])
        days = [(now.date().fromordinal(now.date().toordinal() - i)).isoformat() for i in range(29, -1, -1)]
        series = [round(sum(by_day[d]) / len(by_day[d]), 1) if d in by_day else None for d in days]
        charts.append({"label": label, "unit": unit, "svg": spark_svg(series),
                       "n": len(ms), "gaps": series.count(None)})
    for kind, label, unit in ACTS:
        acts = store.activities(person, kind, 30, now)
        by_day = {a["at"][:10]: a["value"] for a in acts}
        days = [(now.date().fromordinal(now.date().toordinal() - i)).isoformat() for i in range(29, -1, -1)]
        series = [by_day.get(d) for d in days]
        charts.append({"label": label, "unit": unit, "svg": spark_svg(series),
                       "n": len(acts), "gaps": series.count(None)})
    return templates.TemplateResponse(request, "signals.html",
                                      {"person": person, "people": ["아버지", "나"], "charts": charts})


@app.get("/graphview", response_class=HTMLResponse)
def graphview(request: Request):
    g = api_graph()
    # 단순 원형 배치 (읽기 전용 뷰어 — 지식 수정은 볼트에서만)
    n = len(g["nodes"])
    for i, node in enumerate(g["nodes"]):
        ang = 2 * math.pi * i / max(n, 1)
        node["x"] = 420 + 300 * math.cos(ang)
        node["y"] = 300 + 240 * math.sin(ang)
    pos = {node["id"]: node for node in g["nodes"]}
    edges = [{"x1": pos[e["src"]]["x"], "y1": pos[e["src"]]["y"],
              "x2": pos[e["dst"]]["x"], "y2": pos[e["dst"]]["y"], "rel": e["rel"]} for e in g["edges"]]
    colors = {"Person": "#e0a04a", "Medication": "#4fc0b8", "Regimen": "#9fb2d8", "Place": "#b57de0"}
    return templates.TemplateResponse(request, "graphview.html",
                                      {"nodes": g["nodes"], "edges": edges, "badges": g["badges"],
                                       "colors": colors})


@app.get("/scenarios", response_class=HTMLResponse)
def scenarios_page(request: Request):
    rules = []
    for fn in sorted(os.listdir(RULES_DIR)):
        if fn.endswith(".yaml"):
            r = yaml.safe_load(open(os.path.join(RULES_DIR, fn), encoding="utf-8"))
            recent = [e for e in store.events("나", 7, "규칙실행") if e["payload"] == r["name"]][-10:]
            rules.append({"file": fn, "rule": r, "recent": recent})
    return templates.TemplateResponse(request, "scenarios.html", {"rules": rules})


@app.post("/scenarios/update")
def scenarios_update(file: str = Form(...), at: str = Form(""), enabled: str = Form("")):
    """안전한 파라미터만 편집: 시각·on/off. 구조 편집은 rules/*.yaml에서."""
    path = os.path.join(RULES_DIR, os.path.basename(file))
    r = yaml.safe_load(open(path, encoding="utf-8"))
    if at and r["trigger"].get("at"):
        r["trigger"]["at"] = at
    r["enabled"] = enabled == "on"
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(r, f, allow_unicode=True, sort_keys=False)
    return RedirectResponse("/scenarios", status_code=303)
