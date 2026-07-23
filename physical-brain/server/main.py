"""피지컬브레인 FastAPI — API + 서버렌더 대시보드 (Jinja2, 오프라인 원칙: 외부 CDN 없음)."""
import math
import os
from datetime import datetime

import yaml
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from graph import store
from robot_lms import exam as robot_exam  # R01 — DDL 등록을 위해 상단 임포트
from graph_core import approvals as kgapprovals
from graph_core import cycle as kgcycle
from graph_core import profiles as kgprofiles
from server import briefing, librarian, notify, orchestrator, safety
from server.events import adherence
from server.tasks_today import confirm, expand_today, today

app = FastAPI(title="Physical Brain", version="0.1.0")


def _active_profile_name() -> str:
    try:
        return kgprofiles.active()["name"]
    except Exception:
        return ""


@app.on_event("startup")
def _start_heartbeat():
    """실서비스 심장박동: 분당 규칙 틱 + 5분마다 볼트 동기화 (PB_HEARTBEAT=0으로 끔)."""
    from server import scheduler
    scheduler.start()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "web", "templates"))
templates.env.globals["profile_name"] = _active_profile_name
RULES_DIR = orchestrator.RULES_DIR
from graph.body_master import chart_types  # G08 몸 마스터: 측정 유형 사전(볼트로 확장)

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


@app.post("/bp")
def bp_submit(person: str = Form(...), sys_v: int = Form(..., alias="sys"), dia_v: int = Form(..., alias="dia")):
    """혈압 수동 입력 (T29) — 저장 즉시 1층 안전망 검사, 위반 시 알림."""
    now = datetime.now()
    pid = store.person_id(person)
    if not store.get_node(pid):
        store.upsert_node(pid, "Person", {"name": person})
    for mtype, v in (("bp_sys", sys_v), ("bp_dia", dia_v)):
        mid = f"measurement:{person}:{mtype}:{now.isoformat()}"
        store.upsert_node(mid, "Measurement", {"type": mtype, "value": float(v),
                                               "unit": "mmHg", "measured_at": now.isoformat(), "src": "manual"})
        store.upsert_edge(pid, "MEASURED", mid)
        alert = safety.check_measurement(person, mtype, float(v), now)
        if alert:
            notify.send(person, alert["text"], "safety", now)
    return RedirectResponse(f"/?person={person}", status_code=303)


@app.post("/measure")
def measure_submit(person: str = Form(...), mtype: str = Form(...), value: float = Form(...)):
    """일반 측정 입력 (H02) — 측정 유형 사전의 어떤 유형이든 (체중 등)."""
    from graph.body_master import measure_types
    mt = measure_types().get(mtype)
    if not mt:
        return RedirectResponse(f"/?person={person}", status_code=303)
    now = datetime.now()
    pid = store.person_id(person)
    if not store.get_node(pid):
        store.upsert_node(pid, "Person", {"name": person})
    mid = f"measurement:{person}:{mtype}:{now.isoformat()}"
    store.upsert_node(mid, "Measurement", {"type": mtype, "value": float(value),
                                           "unit": mt.get("unit", ""),
                                           "measured_at": now.isoformat(), "src": "manual"})
    store.upsert_edge(pid, "MEASURED", mid)
    alert = safety.check_measurement(person, mtype, float(value), now)
    if alert:
        notify.send(person, alert["text"], "safety", now)
    return RedirectResponse(f"/?person={person}", status_code=303)


@app.get("/cycle", response_class=HTMLResponse)
def cycle_page(request: Request, new: int = 0, template: str = ""):
    """KG-DMAIC 사이클 보드 (G04) — Define 위저드(+G15 템플릿) + 갭 보드."""
    from server.cycle_templates import TEMPLATES
    cs = kgcycle.cycles()
    if new or template or not cs:
        return templates.TemplateResponse(request, "cycle.html", {
            "board": None, "templates": TEMPLATES,
            "preset": TEMPLATES.get(template)})
    return templates.TemplateResponse(request, "cycle.html", {
        "board": kgcycle.board(cs[0]["id"]), "templates": TEMPLATES, "preset": None})


@app.post("/cycle/create")
def cycle_create(name: str = Form(...), purpose: str = Form(...), cqs: str = Form(...),
                 ctq1: str = Form(""), ctq1_target: str = Form(""),
                 ctq2: str = Form(""), ctq2_target: str = Form(""),
                 ctq3: str = Form(""), ctq3_target: str = Form("")):
    ctqs = [{"name": n, "target": t} for n, t in
            ((ctq1, ctq1_target), (ctq2, ctq2_target), (ctq3, ctq3_target)) if n.strip()]
    kgcycle.create_cycle(name, purpose, cqs.splitlines(), ctqs)
    return RedirectResponse("/cycle", status_code=303)


@app.post("/cycle/{cycle_id}/measure")
def cycle_measure(cycle_id: int):
    """CQ 전수 실측 — 근거 있는 답만 '응답 가능'으로 인정."""
    kgcycle.measure(cycle_id, librarian.answer)
    return RedirectResponse("/cycle", status_code=303)


@app.get("/approvals", response_class=HTMLResponse)
def approvals_page(request: Request):
    """승인 큐 (G05) + 에이전트 빌더 초안 (G12)."""
    from server import agent_builder
    return templates.TemplateResponse(request, "approvals.html", {
        "pending": kgapprovals.pending(), "history": kgapprovals.history(),
        "drafts": agent_builder.suggest_rules()})


@app.post("/agents/propose")
def agents_propose(key: str = Form(...)):
    """규칙 초안을 승인 큐로 — 활성화는 승인 후에만 (G12)."""
    from server import agent_builder
    d = next((d for d in agent_builder.suggest_rules() if d["key"] == key), None)
    if d:
        agent_builder.propose_rule(d)
    return RedirectResponse("/approvals", status_code=303)


@app.post("/approvals/{approval_id}/decide")
def approvals_decide(approval_id: int, approve: int = Form(...)):
    kgapprovals.decide(approval_id, bool(approve))
    return RedirectResponse("/approvals", status_code=303)


@app.get("/profiles", response_class=HTMLResponse)
def profiles_page(request: Request):
    """프로필 (G06) — 그래프의 소유·전환 + 유산 패키지 (G-Legacy)."""
    from graph_core import legacy
    latest = legacy.latest_package()
    return templates.TemplateResponse(request, "profiles.html", {
        "profiles": kgprofiles.list_profiles(),
        "legacy_latest": os.path.basename(latest) if latest else None,
        "legacy_check": legacy.verify_package(latest) if latest else None})


@app.post("/legacy/build")
def legacy_build():
    """유산 패키지 지금 만들기 + 즉시 리허설 검증."""
    from graph_core import legacy
    from server.scheduler import vault_path
    legacy.build_package(vault_path())
    return RedirectResponse("/profiles", status_code=303)


@app.post("/profiles/create")
def profiles_create(name: str = Form(...), kind: str = Form("personal")):
    kgprofiles.create(name, kind)
    return RedirectResponse("/profiles", status_code=303)


@app.post("/profiles/{profile_id}/activate")
def profiles_activate(profile_id: str):
    kgprofiles.activate(profile_id)
    return RedirectResponse("/profiles", status_code=303)


@app.get("/learning", response_class=HTMLResponse)
def learning_page(request: Request, person: str = ""):
    """학습 마스터 (G08-L) — 커리큘럼 트리·숙달 현황·다음 걸음 퀴즈."""
    from graph import learning_master as lm
    people = people_list()
    person = person if person in people else people[0]
    if not store.nodes_by_type("Concept"):
        lm.seed_curriculum()
    return templates.TemplateResponse(request, "learning.html", {
        "person": person, "people": people,
        "progress": lm.progress(person), "quiz": lm.quiz_candidates(person, 20)})


@app.post("/learning/quiz")
def learning_quiz(person: str = Form(...), concept_id: str = Form(...), correct: int = Form(...)):
    from graph import learning_master as lm
    lm.record_quiz(person, concept_id, bool(correct))
    return RedirectResponse(f"/learning?person={person}", status_code=303)


@app.get("/work", response_class=HTMLResponse)
def work_page(request: Request, person: str = ""):
    """일 마스터 (G08-W) — 목표(OKR)·과업(칸반)·산출물(PARA)의 1인 밸류체인."""
    from graph import work_master as wm
    people = people_list()
    person = person if person in people else people[0]
    return templates.TemplateResponse(request, "work.html", {
        "person": person, "people": people, "board": wm.board(person),
        "weekly_done": wm.weekly_done(person)})


@app.post("/work/objective")
def work_objective(project: str = Form(...), title: str = Form(...),
                   kr: str = Form(""), person: str = Form("나")):
    from graph import work_master as wm
    wm.add_objective(project, title, kr, person)
    return RedirectResponse(f"/work?person={person}", status_code=303)


@app.post("/work/task")
def work_task(objective_id: str = Form(...), title: str = Form(...), person: str = Form("나")):
    from graph import work_master as wm
    wm.add_task(objective_id, title)
    return RedirectResponse(f"/work?person={person}", status_code=303)


@app.post("/work/task/move")
def work_task_move(task_id: str = Form(...), status: str = Form(...), person: str = Form("나")):
    from graph import work_master as wm
    wm.move_task(task_id, status)
    return RedirectResponse(f"/work?person={person}", status_code=303)


@app.post("/mind")
def mind_submit(person: str = Form(...), mood: str = Form(...), memo: str = Form("")):
    """마음 기록 (G08-M) — 하루 한 번의 감정 태그 + 한 줄. 해석하지 않고 보존한다."""
    from graph.mind_master import record_mood
    record_mood(person, mood, memo)
    return RedirectResponse(f"/?person={person}", status_code=303)


@app.get("/robot", response_class=HTMLResponse)
def robot_page(request: Request, err: str = ""):
    """로봇 검정 (R01) + 프로필 (R02) + 분야팩 (R03·R04) + 대화 게이트 (R05)."""
    from robot_lms import domain as robot_domain
    from robot_lms import profile as robot_profile
    return templates.TemplateResponse(request, "robot.html", {
        "card": robot_exam.report_card(), "err": err,
        "profile": robot_profile.robot_profile(),
        "packs": robot_domain.packs(), "pack_kinds": robot_domain.KINDS,
        "pack_detail": robot_domain.latest_test_detail(),
        "llm_model": os.environ.get("LLM_MODEL", "")})


@app.post("/api/robot/chat")
def api_robot_chat(body: dict):
    """로봇 대화 API (R05·R08) — 음성 클라이언트의 입과 귀가 이곳으로 연결된다."""
    from robot_lms import gate as robot_gate
    return robot_gate.converse(body.get("question", ""))


@app.get("/robot/report", response_class=HTMLResponse)
def robot_report_page(request: Request, month: str = ""):
    """월간 로봇 지능 리포트 (R10) — 성장 일지 열람 + 이번 달 미리보기 생성."""
    from robot_lms import report as robot_report
    rs = robot_report.reports()
    if not month and rs:
        month = rs[0]["month"]
    body = (robot_report.get_report(month) or {}).get("body") if month else None
    return templates.TemplateResponse(request, "robot_report.html", {
        "reports": rs, "month": month, "body": body})


@app.post("/robot/report/build")
def robot_report_build():
    """이번 달 리포트 즉시 생성(진행 중 스냅샷) — 월말을 기다리지 않고 미리 본다."""
    from robot_lms import report as robot_report
    from server.scheduler import vault_path
    month = datetime.now().strftime("%Y-%m")
    robot_report.build_report(month, vault_dir=vault_path())
    return RedirectResponse(f"/robot/report?month={month}", status_code=303)


@app.get("/robot/chat", response_class=HTMLResponse)
def robot_chat(request: Request, q: str = ""):
    """로봇과 대화 (R05) — 인증된 분야만 열린다. 미인증은 정직하게 물러선다."""
    from robot_lms import gate as robot_gate
    chat = robot_gate.converse(q) if q.strip() else None
    return templates.TemplateResponse(request, "robot_chat.html", {"q": q, "chat": chat})


@app.post("/robot/exam")
def robot_exam_run():
    """로봇 검정 응시 — 실서버의 LLM이 전 문항에 답한다 (수 분 소요 가능)."""
    try:
        robot_exam.run_exam(robot_exam.llm_ask, model=os.environ.get("LLM_MODEL", ""))
    except Exception as e:  # LLM 부재 등 — 지어내지 않고 정직하게 알린다
        return RedirectResponse(f"/robot?err={e}", status_code=303)
    return RedirectResponse("/robot", status_code=303)


@app.post("/robot/pack/create")
def robot_pack_create(name: str = Form(...), kind: str = Form("care")):
    """분야팩 등록 (R03) — 그래프에서 문항이 자동 생성된다."""
    from robot_lms import domain as robot_domain
    robot_domain.create_pack(name, kind)
    return RedirectResponse("/robot", status_code=303)


@app.post("/robot/pack/{pack_id}/test")
def robot_pack_test(pack_id: int):
    """자기시험 (R04) — 사서 파이프라인(LLM+그래프)이 응시, 정답+근거 이중 채점."""
    from robot_lms import domain as robot_domain
    try:
        robot_domain.self_test(pack_id, librarian.answer)
    except Exception as e:
        return RedirectResponse(f"/robot?err={e}", status_code=303)
    return RedirectResponse("/robot", status_code=303)


@app.get("/biz", response_class=HTMLResponse)
def biz_page(request: Request, err: str = ""):
    """기업 그래프 (G09) — 에이에스씨 일일결산 보드 + 로봇 발주 제안(HITL)."""
    from biz import closing, odoo_client
    now = datetime.now()
    today, month = now.date().isoformat(), now.strftime("%Y-%m")
    return templates.TemplateResponse(request, "biz.html", {
        "configured": odoo_client.configured(), "err": err,
        "today": today, "day": closing.close_day(today),
        "month_label": month, "month": closing.close_month(month)})


@app.post("/biz/sync")
def biz_sync():
    """Odoo → 그래프 수동 동기화 (심장박동 외 즉시 반영용)."""
    from biz import closing
    try:
        closing.sync_from_odoo()
    except Exception as e:
        return RedirectResponse(f"/biz?err={e}", status_code=303)
    return RedirectResponse("/biz", status_code=303)


@app.post("/biz/purchase")
def biz_purchase(item: str = Form(...), qty: int = Form(1),
                 est_price: float = Form(0), vendor: str = Form(""),
                 reason: str = Form("")):
    """발주 제안 → 승인 큐. 승인해야만 Odoo에 초안이 생긴다."""
    from biz.purchase import propose_purchase
    propose_purchase(item, qty, est_price, reason, vendor, proposed_by="사람(화면)")
    return RedirectResponse("/approvals", status_code=303)


@app.get("/interview", response_class=HTMLResponse)
def interview_page(request: Request):
    """암묵지 인터뷰 (G11) — 그래프의 끊긴 곳이 질문이 된다."""
    from graph import gap_finders  # noqa: F401 — 갭 발견자·실행기 등록
    from graph_core import interview as itv
    itv.scan()
    return templates.TemplateResponse(request, "interview.html", {"due": itv.due(5)})


@app.post("/interview/{seed_id:path}/answer")
def interview_answer(seed_id: str, response: str = Form(...)):
    from graph_core import interview as itv
    itv.answer(seed_id, response)
    return RedirectResponse("/interview", status_code=303)


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


def people_list() -> list[str]:
    """그래프의 실제 인물 목록 (샘플 하드코딩 제거 — 볼트가 진실의 원본)."""
    names = [p["props"].get("name", "") for p in store.nodes_by_type("Person")]
    return [n for n in names if n] or ["나"]


@app.get("/", response_class=HTMLResponse)
def home(request: Request, person: str = ""):
    now = datetime.now()
    people = people_list()
    person = person if person in people else people[0]
    expand_today(now)
    tasks = [t for t in today(now) if t["person"] == person]
    from graph.body_master import measure_types
    from graph.mind_master import MOODS, week_moods
    from server.wellbeing import week_card
    return templates.TemplateResponse(request, "home.html", {
        "person": person, "people": people,
        "briefing": briefing.morning_briefing(person, now),
        "tasks": tasks, "adherence": adherence(person, 7, now),
        "triangle": store.triangle_week(person, now),
        "moods": MOODS, "mind": week_moods(person, now),
        "wellbeing": week_card(person, now),
        "input_types": [m for k, m in measure_types().items()
                        if k not in ("bp_sys", "bp_dia")],
        "events": list(reversed(store.events(person, 2, None, now)))[:8],
    })


@app.get("/signals", response_class=HTMLResponse)
def signals(request: Request, person: str = ""):
    people = people_list()
    person = person if person in people else people[0]
    now = datetime.now()
    charts = []
    for mtype, label, unit in chart_types():
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
                                      {"person": person, "people": people, "charts": charts})


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
