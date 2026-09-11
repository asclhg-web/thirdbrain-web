"""P2-C1: 통합 웹앱 v1 — 로그인·역할·승인함·격리 큐(undo)·브리핑·War Room·감사.

현장이 매일 쓰는 도구를 데모용 단일 페이지에서 정식 다중 사용자 앱으로.
  실행:  uvicorn axp.webapp:app --host 0.0.0.0 --port 8900
  계정:  axp_users 테이블 — 최초 기동 시 3계정 부트스트랩
         (admin/steward/approver, 초기 비밀번호는 AXP_BOOTSTRAP_PW 또는 'change-me!')
         ⚠ 운영 전 반드시 비밀번호 변경(/password) — 로그인 화면에도 경고 표시.
  세션:  HMAC 서명 쿠키(AXP_SECRET). HTTPS는 Caddy(deploy)가 담당.
  역할:  approver=카드 결정 · steward=격리 확정/취소 · admin=전부 · viewer=열람.
"""
from __future__ import annotations

import hashlib
import hmac
import html
import json
import os
import secrets
from datetime import datetime, timezone

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from . import common, config, db
from .agents import inbox
from .dataset import codemap
from .graph import confidence, evidence
from .judge import cards as jcards

SECRET = os.environ.get("AXP_SECRET", "dev-secret-change-me")
BOOTSTRAP_PW = os.environ.get("AXP_BOOTSTRAP_PW", "")  # 비우면 무작위 생성

app = FastAPI(title="AX Platform Web", docs_url=None, redoc_url=None)

USERS_DDL = """
CREATE TABLE IF NOT EXISTS axp_users (
  username TEXT PRIMARY KEY,
  pw_hash TEXT NOT NULL,
  salt TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin','steward','approver','viewer')),
  display TEXT NOT NULL,
  must_change INTEGER NOT NULL DEFAULT 1
);
"""


def _hash(pw: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 60_000).hex()


def ensure_users() -> None:
    """최초 기동 부트스트랩 — 초기 비밀번호는 계정별 무작위 생성이 기본.

    생성된 비밀번호는 데이터 루트의 initial-credentials.txt(0600)에 딱 한 번
    기록된다 — 관리자가 봉투처럼 전달하고 파일은 삭제한다. AXP_BOOTSTRAP_PW를
    지정하면(개발·테스트용) 세 계정이 그 값을 공유한다."""
    db.executescript(USERS_DDL)
    if db.scalar("SELECT COUNT(*) FROM axp_users"):
        return
    config.ensure_dirs()
    lines = []
    for u, role, disp in (("admin", "admin", "관리자"),
                          ("steward", "steward", "스튜어드"),
                          ("approver", "approver", "카드 승인자")):
        pw = BOOTSTRAP_PW or secrets.token_urlsafe(9)
        salt = secrets.token_hex(8)
        db.execute(
            "INSERT INTO axp_users VALUES (?,?,?,?,?,1)",
            (u, _hash(pw, salt), salt, role, disp))
        lines.append(f"{u} ({disp}): {pw}")
    if not BOOTSTRAP_PW:
        cred = config.DATA / "initial-credentials.txt"
        cred.write_text(
            "AX 플랫폼 초기 계정 — 첫 로그인 후 비밀번호를 변경하고 이 파일을 삭제하세요.\n"
            + "\n".join(lines) + "\n", encoding="utf-8")
        try:
            cred.chmod(0o600)
        except OSError:
            pass
        print(f"[webapp] 초기 계정 비밀번호를 {cred}에 기록했습니다 (0600).")


def _sign(value: str) -> str:
    return hmac.new(SECRET.encode(), value.encode(), hashlib.sha256).hexdigest()[:32]


def current_user(request: Request) -> dict | None:
    tok = request.cookies.get("axp_session", "")
    if "|" not in tok:
        return None
    name, sig = tok.rsplit("|", 1)
    if not hmac.compare_digest(_sign(name), sig):
        return None
    ensure_users()
    return db.one("SELECT * FROM axp_users WHERE username=?", (name,))


def _require(request: Request, roles: tuple[str, ...] = ()) -> dict | Response:
    u = current_user(request)
    if u is None:
        return RedirectResponse("/login", status_code=303)
    if roles and u["role"] not in roles + ("admin",):
        return HTMLResponse(page(u, "권한 없음",
            f"<div class='card warn'>이 작업은 {' 또는 '.join(roles)} 역할이 필요합니다.</div>"), 403)
    return u


# ── 레이아웃 ─────────────────────────────────────────────
STYLE = """<style>
*{box-sizing:border-box}body{font-family:'Noto Sans KR','Malgun Gothic',sans-serif;
margin:0;background:#F8F2EA;color:#2E241C;line-height:1.6}
a{color:inherit;text-decoration:none}
header{background:#2B1D12;color:#EDE3D5;padding:10px 0;position:sticky;top:0;z-index:9}
.wrap{max-width:1060px;margin:0 auto;padding:0 18px}
header .bar{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.mark{background:#6E3A1C;color:#E8A33D;border-radius:7px;padding:3px 9px;font-weight:900}
header nav a{margin-right:14px;font-size:14px;color:#C9B8A2}
header nav a.on{color:#E8A33D;font-weight:700}
header .who{margin-left:auto;font-size:13px;color:#B9A78F}
main{padding:26px 0 60px}
h2{color:#6E3A1C;margin:0 0 6px}
p.sub{color:#76675A;font-size:14px;margin:0 0 18px}
.card{background:#fff;border:1px solid #DCCDBB;border-left:7px solid #9C5227;
border-radius:12px;padding:16px 20px;margin-bottom:14px}
.card.ok{border-left-color:#0E8F86}.card.warn{border-left-color:#A8493B}
.chip{display:inline-block;color:#fff;border-radius:11px;padding:1px 10px;
font-size:12px;font-weight:700;margin-right:8px;background:#C07F1E}
.ln{font-size:13.5px;margin:3px 0}.ln small{color:#76675A;font-size:11.5px}
.btn{border:none;border-radius:7px;padding:7px 16px;font-size:13px;font-weight:700;
cursor:pointer;font-family:inherit}
.btn.ok{background:#0E8F86;color:#fff}.btn.no{background:#A8493B;color:#fff}
.btn.why{background:#E8A33D;color:#2B1D12}.btn.plain{background:#EFE5D8;color:#6E3A1C}
input,select{border:1px solid #DCCDBB;border-radius:7px;padding:7px 10px;
font-family:inherit;font-size:13px}
table{border-collapse:collapse;width:100%;background:#fff;font-size:13px;margin-bottom:16px}
td,th{border:1px solid #DCCDBB;padding:7px 10px;text-align:left}
th{background:#6E3A1C;color:#fff;font-size:12.5px}
.note{background:#FDF3E0;border:1px solid #DCCDBB;border-radius:9px;
padding:10px 14px;font-size:13px;margin-bottom:16px}
form.inline{display:inline-flex;gap:6px;align-items:center;flex-wrap:wrap}
@media(max-width:640px){header nav a{margin-right:9px;font-size:13px}}
</style>"""

NAV = [("/inbox", "승인함", ("approver", "viewer", "steward")),
       ("/quarantine", "격리 큐", ("steward", "viewer", "approver")),
       ("/briefing", "브리핑", ("viewer", "steward", "approver")),
       ("/ask", "질문", ("viewer", "steward", "approver")),
       ("/rules", "규칙", ("viewer", "steward", "approver")),
       ("/warroom", "War Room", ("viewer", "steward", "approver")),
       ("/audit", "감사 로그", ("viewer", "steward", "approver")),
       ("/promotions", "자동실행", ("approver", "viewer")),
       ("/assets", "자산 대장", ("steward", "viewer"))]


def page(user: dict | None, title: str, body: str, active: str = "") -> str:
    nav = "".join(
        f"<a href='{p}' class='{'on' if p == active else ''}'>{t}</a>"
        for p, t, _ in NAV)
    who = (f"<span class='who'>{html.escape(user['display'])} ({user['role']}) · "
           f"<a href='/password' style='color:#B9A78F'>비밀번호</a> · "
           f"<a href='/logout' style='color:#B9A78F'>로그아웃</a></span>") if user else ""
    warn = ("<div class='note'>⚠ 초기 비밀번호 사용 중 — <a href='/password'><b>지금 변경</b></a>하세요.</div>"
            if user and user.get("must_change") else "")
    return f"""<!doctype html><meta charset='utf-8'>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — AX 플랫폼</title>{STYLE}
<header><div class="wrap bar"><span class="mark">AX</span><b>AX 플랫폼</b>
<nav>{nav}</nav>{who}</div></header>
<main><div class="wrap">{warn}{body}</div></main>"""


# ── 인증 ────────────────────────────────────────────────
@app.get("/login", response_class=HTMLResponse)
def login_form():
    return page(None, "로그인", """
<h2>로그인</h2><p class="sub">판단의 공장 — 결정은 언제나 사람이 합니다</p>
<form method="post" class="card" style="max-width:360px">
  <p><input name="username" placeholder="아이디" style="width:100%"></p>
  <p><input name="password" type="password" placeholder="비밀번호" style="width:100%"></p>
  <button class="btn ok" style="width:100%">들어가기</button>
</form>""")


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    ensure_users()
    u = db.one("SELECT * FROM axp_users WHERE username=?", (username,))
    if not u or not hmac.compare_digest(u["pw_hash"], _hash(password, u["salt"])):
        return HTMLResponse(page(None, "로그인", "<div class='card warn'>아이디 또는 비밀번호가 다릅니다. <a href='/login'>다시</a></div>"), 401)
    r = RedirectResponse("/inbox", status_code=303)
    r.set_cookie("axp_session", f"{username}|{_sign(username)}",
                 httponly=True, samesite="lax")
    return r


@app.get("/logout")
def logout():
    r = RedirectResponse("/login", status_code=303)
    r.delete_cookie("axp_session")
    return r


@app.get("/password", response_class=HTMLResponse)
def password_form(request: Request):
    u = _require(request)
    if isinstance(u, Response):
        return u
    return HTMLResponse(page(u, "비밀번호 변경", """
<h2>비밀번호 변경</h2>
<form method="post" class="card" style="max-width:360px">
  <p><input name="new_pw" type="password" placeholder="새 비밀번호(8자 이상)" style="width:100%"></p>
  <button class="btn ok" style="width:100%">변경</button>
</form>"""))


@app.post("/password")
def password_change(request: Request, new_pw: str = Form(...)):
    u = _require(request)
    if isinstance(u, Response):
        return u
    if len(new_pw) < 8:
        return HTMLResponse(page(u, "비밀번호", "<div class='card warn'>8자 이상이어야 합니다.</div>"), 400)
    salt = secrets.token_hex(8)
    db.execute("UPDATE axp_users SET pw_hash=?, salt=?, must_change=0 WHERE username=?",
               (_hash(new_pw, salt), salt, u["username"]))
    return RedirectResponse("/inbox", status_code=303)


# ── 승인함 ───────────────────────────────────────────────
def _fmt_narr(text: str) -> str:
    import re as _re
    out = []
    for l in (text or "").splitlines():
        if not l.strip():
            continue
        e = html.escape(l)
        e = _re.sub(r"\[근거: Rule:(RULE-\d+)\]",
                    r"<small>〔근거: <a href='/why/\1' style='text-decoration:underline'>Rule:\1</a>〕</small>", e)
        e = _re.sub(r"\[근거: ([^\]]+)\]", r"<small>〔근거: \1〕</small>", e)
        out.append(f"<div class='ln'>{e}</div>")
    return "".join(out[:4])


@app.get("/", response_class=HTMLResponse)
@app.get("/inbox", response_class=HTMLResponse)
def inbox_page(request: Request):
    u = _require(request)
    if isinstance(u, Response):
        return u
    rows = jcards.listing(status="proposed")
    can = u["role"] in ("approver", "admin")
    body = [f"<h2>판단 카드 승인함</h2><p class='sub'>대기 {len(rows)}건 — 수치·구간·근거·대안, 결정은 사람이</p>"]
    reasons = ["현장 사정(행사·날씨)", "시점 부적절", "수치 의문 — 재검토", "기타"]
    for c in rows:
        rng = json.loads(c.get("range_json") or "{}")
        rtxt = (f"구간 P10 {rng.get('p10')} · P50 {rng.get('p50')} · P90 {rng.get('p90')}"
                if rng.get("p50") else "")
        act = ""
        if can:
            opts = "".join(f"<option>{r}</option>" for r in reasons)
            act = f"""<div style="margin-top:8px">
<form class="inline" method="post" action="/cards/{c['card_id']}/decide">
  <button class="btn ok" name="approve" value="1">승인 → 환류</button>
  <select name="reason"><option value="">반려 사유…</option>{opts}</select>
  <button class="btn no" name="approve" value="0">반려</button>
</form></div>"""
        body.append(f"""<div class="card">
<b><span class="chip">{html.escape(c['kind'])}</span>#{c['card_id']}</b> {html.escape(c.get('proposal',''))}
<div style="color:#0E8F86;font-size:12.5px;font-weight:700">{rtxt}</div>
{_fmt_narr(c.get('narrative',''))}{act}</div>""")
    if not rows:
        body.append("<div class='card ok'>대기 카드가 없습니다 — 시스템은 정상 순환 중.</div>")
    return HTMLResponse(page(u, "승인함", "".join(body), "/inbox"))


@app.post("/cards/{card_id}/decide")
def card_decide(card_id: int, request: Request,
                approve: str = Form(...), reason: str = Form("")):
    u = _require(request, roles=("approver",))
    if isinstance(u, Response):
        return u
    ok = approve == "1"
    if not ok and not reason:
        return HTMLResponse(page(u, "반려", "<div class='card warn'>반려에는 사유가 필수입니다 — 사유는 다음 학습의 재료입니다. <a href='/inbox'>돌아가기</a></div>"), 400)
    inbox.decide(card_id, actor=u["display"], role="card_approver",
                 approve=ok, reason_code=reason[:20], reason_text=reason)
    if ok:
        inbox.apply_feedback(card_id, actor=u["display"])
    return RedirectResponse("/inbox", status_code=303)


# ── 격리 큐 (스튜어드) ──────────────────────────────────
@app.get("/quarantine", response_class=HTMLResponse)
def quarantine_page(request: Request):
    u = _require(request)
    if isinstance(u, Response):
        return u
    can = u["role"] in ("steward", "admin")
    pend = codemap.pending()
    recent = db.query(
        "SELECT * FROM quarantine_queue WHERE status='confirmed' "
        "ORDER BY decided_at DESC LIMIT 10") if db.table_exists("quarantine_queue") else []
    rows = "".join(f"""<tr><td>{q['q_id']}</td><td>{html.escape(q['domain'])}</td>
<td><b>{html.escape(q['alias'])}</b></td><td>{q['n_rows']}</td><td>
{f'''<form class="inline" method="post" action="/quarantine/{q['q_id']}/confirm">
<input name="code" placeholder="표준 코드" size="12">
<button class="btn ok">확정</button></form>''' if can else '-'}</td></tr>"""
        for q in pend)
    undo = "".join(f"""<tr><td>{q['q_id']}</td><td>{html.escape(q['alias'])}</td>
<td>{html.escape(q.get('proposed_code') or '')}</td><td>{html.escape(q.get('decided_by') or '')}</td><td>
{f'''<form class="inline" method="post" action="/quarantine/{q['q_id']}/undo">
<button class="btn no">확정 취소</button></form>''' if can else '-'}</td></tr>"""
        for q in recent)
    body = f"""<h2>격리 큐</h2>
<p class="sub">처음 보는 현장 어휘 — 확신 없으면 추측하지 말고 현장에 물어보세요 (I-09 교훈)</p>
<table><tr><th>#</th><th>영역</th><th>별칭</th><th>행수</th><th>확정</th></tr>{rows or '<tr><td colspan=5>대기 없음 ✔</td></tr>'}</table>
<h2 style="font-size:17px">최근 확정 — 잘못 확정했다면 취소하세요</h2>
<p class="sub">취소하면 다음 야간 배치의 전량 재구축이 소급 반영합니다</p>
<table><tr><th>#</th><th>별칭</th><th>확정 코드</th><th>확정자</th><th>취소</th></tr>{undo or '<tr><td colspan=5>기록 없음</td></tr>'}</table>"""
    return HTMLResponse(page(u, "격리 큐", body, "/quarantine"))


@app.post("/quarantine/{q_id}/confirm")
def quarantine_confirm(q_id: int, request: Request, code: str = Form(...)):
    u = _require(request, roles=("steward",))
    if isinstance(u, Response):
        return u
    codemap.confirm(q_id, code.strip(), by=u["display"])
    return RedirectResponse("/quarantine", status_code=303)


@app.post("/quarantine/{q_id}/undo")
def quarantine_undo(q_id: int, request: Request):
    u = _require(request, roles=("steward",))
    if isinstance(u, Response):
        return u
    codemap.unconfirm(q_id, by=u["display"])
    return RedirectResponse("/quarantine", status_code=303)


# ── 근거 사다리 ('왜?') ──────────────────────────────────
@app.get("/why/{rule_id}", response_class=HTMLResponse)
def why_page(rule_id: str, request: Request):
    u = _require(request)
    if isinstance(u, Response):
        return u
    try:
        res = evidence.evidence_for_rule(rule_id)
    except Exception as e:  # noqa: BLE001
        return HTMLResponse(page(u, "왜?", f"<div class='card warn'>근거 조회 실패: {html.escape(str(e))}</div>"), 404)
    text = evidence.render_path_text(res)
    steps = "".join(
        f"<div class='card' style='margin-bottom:6px'><div class='ln'>{html.escape(l)}</div></div>"
        for l in text.splitlines() if l.strip())
    return HTMLResponse(page(u, "근거 역추적",
        f"<h2>왜? — {html.escape(rule_id)} 근거 역추적</h2>"
        f"<p class='sub'>규칙 → 조합 → 사실 → 원장 원본까지 — 경로에 없는 주장은 없다</p>{steps}",
        "/inbox"))


@app.get("/rules", response_class=HTMLResponse)
def rules_page(request: Request):
    u = _require(request)
    if isinstance(u, Response):
        return u
    rows = confidence.rules("promoted")
    body = "".join(
        f"<div class='card'><b>{html.escape(r['rule_id'])}</b> — {html.escape(r.get('text') or '')} "
        f"(확신도 {round((r.get('confidence') or 0)*100)}%) "
        f"<a class='btn why' style='float:right' href='/why/{html.escape(r['rule_id'])}'>왜? (근거)</a></div>"
        for r in rows) or "<div class='card'>승격된 규칙이 없습니다.</div>"
    return HTMLResponse(page(u, "규칙", f"<h2>승격 규칙</h2><p class='sub'>확신도 70%×3회 재현을 통과한 지식</p>{body}", "/inbox"))


# ── 질문(ask) — 그래프 검색 + 인용 강제 답변 ─────────────
ASK_EXAMPLES = ["OVEN-2 불량의 원인은?", "승격된 규칙 목록", "OVEN-2 정비 이력",
                "현장 기록에서 야간 관련", "V2 공급사 원인 후보"]


def _route_question(q: str):
    """질문 → 검색 라우팅. 반환 (retrieved, 설명) — 근거 없는 답은 없다."""
    import re as _re
    from .studio import knowledge
    from .judge import assembler as asm
    ent = _re.search(r"\b(OVEN-\d+|[VW]-?\d+|V\d+|[PS]-[A-Z]+(?:-[A-Z]+)?)\b", q.upper())
    if "이력" in q and ent:
        return asm.search_history(ent.group(1)), f"정비 이력 검색: {ent.group(1)}"
    if "규칙" in q:
        return asm.search_rules(), "승격 규칙 검색"
    if "기록" in q or "메모" in q:
        return knowledge.search_memos(q), "현장 기록 검색"
    if ent:
        return asm.search_cause(ent.group(1)), f"원인 검색: {ent.group(1)}"
    return None, None


@app.get("/ask", response_class=HTMLResponse)
@app.post("/ask", response_class=HTMLResponse)
async def ask_page(request: Request):
    u = _require(request)
    if isinstance(u, Response):
        return u
    q, answer_html = "", ""
    if request.method == "POST":
        form = await request.form()
        q = str(form.get("q", "")).strip()
        if q:
            from .judge import assembler as asm
            retrieved, desc = _route_question(q)
            if retrieved is None:
                answer_html = ("<div class='card warn'>질문을 해석하지 못했습니다 — "
                               "설비/제품 코드(OVEN-2, P-PIE…)를 포함하거나 '규칙'/'이력'/'기록'을 넣어 보세요.</div>")
            else:
                text = asm.answer(q, retrieved)
                lines = "".join(f"<div class='ln'>{_fmt_narr_line(l)}</div>"
                                for l in text.splitlines() if l.strip())
                answer_html = (f"<div class='card ok'><div style='font-size:12px;color:#76675A'>{html.escape(desc)}"
                               f" · 모든 문장에 근거 강제</div>{lines}</div>")
    ex = "".join(f"<button class='btn plain' name='q' value='{html.escape(e)}'>{html.escape(e)}</button> "
                 for e in ASK_EXAMPLES)
    body = f"""<h2>질문 — '왜?'에 끝까지 답합니다</h2>
<p class="sub">답변의 모든 문장은 그래프 검색 결과에서만 조립되고 〔근거〕 표기가 강제됩니다</p>
<form method="post" class="card">
  <div style="display:flex;gap:8px"><input name="q" value="{html.escape(q)}"
    placeholder="예: OVEN-2 불량의 원인은?" style="flex:1"><button class="btn why">질문</button></div>
  <div style="margin-top:10px">{ex}</div>
</form>{answer_html}"""
    return HTMLResponse(page(u, "질문", body, "/ask"))


def _fmt_narr_line(l: str) -> str:
    import re as _re
    e = html.escape(l)
    e = _re.sub(r"\[근거: Rule:(RULE-\d+)\]",
                r"<small>〔근거: <a href='/why/\1' style='text-decoration:underline'>Rule:\1</a>〕</small>", e)
    return _re.sub(r"\[근거: ([^\]]+)\]", r"<small>〔근거: \1〕</small>", e)


# ── 자동 실행 승급 관리 (M7-3 정책 화면) ─────────────────
@app.get("/promotions", response_class=HTMLResponse)
def promotions_page(request: Request):
    u = _require(request)
    if isinstance(u, Response):
        return u
    from .agents import promotion
    db.executescript(promotion.DDL)
    rows = db.query("SELECT * FROM promotions ORDER BY promo_id DESC LIMIT 30")
    can = u["role"] in ("approver", "admin")
    body = [f"""<h2>자동 실행 승급 관리</h2>
<p class="sub">저위험 카드의 자동 실행 — 상한과 승인율 조건 안에서만, 위반 시 자동 강등</p>"""]
    if can:
        body.append("""<form method="post" action="/promotions/request" class="card">
<b>새 승급 신청</b>
<div class="inline" style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap">
<select name="kind"><option>demand_forecast</option><option>replenish</option>
<option>allocation</option><option>production_plan</option></select>
<input name="amount_cap" placeholder="수량/금액 상한 (예: 2000)" size="18">
<input name="min_rate" placeholder="최소 승인율 (예: 0.8)" size="14">
<button class="btn ok">신청 (조건 자동 검사)</button></div></form>""")
    trows = []
    for r in rows:
        act = ""
        if can and r["status"] == "requested":
            act = (f"<form class='inline' method='post' action='/promotions/{r['promo_id']}/decide'>"
                   f"<button class='btn ok' name='ok' value='1'>승인</button>"
                   f"<button class='btn no' name='ok' value='0'>반려</button></form>")
        elif can and r["status"] == "active":
            act = (f"<form class='inline' method='post' action='/promotions/{r['promo_id']}/demote'>"
                   f"<button class='btn no'>수동 강등</button></form>")
        trows.append(f"<tr><td>{r['promo_id']}</td><td>{html.escape(r['kind'])}</td>"
                     f"<td>{r['amount_cap']}</td><td>{round(r['min_approval_rate']*100)}%</td>"
                     f"<td><b>{html.escape(r['status'])}</b></td>"
                     f"<td>{html.escape(r.get('demote_reason') or '')}</td><td>{act}</td></tr>")
    body.append("<table><tr><th>#</th><th>유형</th><th>상한</th><th>최소 승인율</th>"
                "<th>상태</th><th>강등 사유</th><th>조치</th></tr>"
                + ("".join(trows) or "<tr><td colspan=7>승급 이력 없음</td></tr>") + "</table>")
    body.append("<div class='note'>승급 조건을 어기면(상한 초과·승인율 하락) 야간 감시가 자동 강등합니다 — 최종 결정은 War Room에서 사람.</div>")
    return HTMLResponse(page(u, "자동실행", "".join(body), "/promotions"))


@app.post("/promotions/request")
def promotions_request(request: Request, kind: str = Form(...),
                       amount_cap: str = Form(...), min_rate: str = Form(...)):
    u = _require(request, roles=("approver",))
    if isinstance(u, Response):
        return u
    from .agents import promotion
    try:
        promotion.request(kind, float(amount_cap), float(min_rate), by=u["display"])
    except ValueError:
        return HTMLResponse(page(u, "자동실행", "<div class='card warn'>상한·승인율은 숫자로 입력하세요. <a href='/promotions'>돌아가기</a></div>"), 400)
    return RedirectResponse("/promotions", status_code=303)


@app.post("/promotions/{promo_id}/decide")
def promotions_decide(promo_id: int, request: Request, ok: str = Form(...)):
    u = _require(request, roles=("approver",))
    if isinstance(u, Response):
        return u
    from .agents import promotion
    promotion.decide(promo_id, approver=u["display"], approve=ok == "1")
    return RedirectResponse("/promotions", status_code=303)


@app.post("/promotions/{promo_id}/demote")
def promotions_demote(promo_id: int, request: Request):
    u = _require(request, roles=("approver",))
    if isinstance(u, Response):
        return u
    from .agents import promotion
    db.executescript(promotion.DDL)
    db.execute("UPDATE promotions SET status='demoted', demoted_at=?, demote_reason=? "
               "WHERE promo_id=? AND status='active'",
               (datetime.now(timezone.utc).isoformat(timespec='seconds'),
                f"수동 강등({u['display']})", promo_id))
    common.alert("warn", "promotion", f"승급 #{promo_id} 수동 강등 by {u['display']}")
    return RedirectResponse("/promotions", status_code=303)


# ── 자산 대장 (M0 커스터디) ──────────────────────────────
@app.get("/assets", response_class=HTMLResponse)
def assets_page(request: Request):
    u = _require(request)
    if isinstance(u, Response):
        return u
    from .custody import ledger
    rows = ledger.listing()
    can = u["role"] in ("steward", "admin")
    form = ""
    if can:
        form = """<form method="post" action="/assets/register" class="card">
<b>자산 등록</b> <span style="font-size:12px;color:#76675A">— 반입된 모든 자료는 여기 등록되어야 반출 게이트의 보호를 받습니다</span>
<div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap">
<input name="asset_id" placeholder="자산 ID (예: pos-2026-09)" size="16">
<select name="kind"><option>dataset</option><option>document</option><option>model</option><option>script</option></select>
<input name="location" placeholder="위치/경로" size="22">
<input name="note" placeholder="비고" size="18">
<button class="btn ok">등록</button></div></form>"""
    trows = "".join(
        f"<tr><td>{html.escape(r['asset_id'])}</td><td>{html.escape(r['version'])}</td>"
        f"<td>{html.escape(r['kind'])}</td><td>{html.escape(r['location'])}</td>"
        f"<td>{html.escape(r['owner'])}</td><td>{html.escape(str(r['updated_at'])[:16])}</td></tr>"
        for r in rows)
    body = (f"<h2>자산 대장</h2><p class='sub'>고객 자료의 등기부 — 등록 {len(rows)}건, 전 자료 태성당 자산 귀속 원칙</p>"
            + form + "<table><tr><th>자산</th><th>버전</th><th>종류</th><th>위치</th>"
            "<th>담당</th><th>갱신</th></tr>"
            + (trows or "<tr><td colspan=6>등록 자산 없음</td></tr>") + "</table>")
    return HTMLResponse(page(u, "자산 대장", body, "/assets"))


@app.post("/assets/register")
def assets_register(request: Request, asset_id: str = Form(...), kind: str = Form(...),
                    location: str = Form(...), note: str = Form("")):
    u = _require(request, roles=("steward",))
    if isinstance(u, Response):
        return u
    from .custody import ledger
    ledger.register(asset_id.strip(), kind, location.strip(), owner=u["display"], note=note)
    return RedirectResponse("/assets", status_code=303)


# ── 브리핑 · War Room · 감사 ────────────────────────────
@app.get("/briefing", response_class=HTMLResponse)
def briefing_page(request: Request):
    u = _require(request)
    if isinstance(u, Response):
        return u
    bdir = config.ARTIFACTS / "briefings"
    files = sorted(bdir.glob("briefing_*.md")) if bdir.exists() else []
    if not files:
        return HTMLResponse(page(u, "브리핑", "<div class='card'>발행된 브리핑이 없습니다.</div>", "/briefing"))
    md = files[-1].read_text(encoding="utf-8")
    out, in_ul = [], False
    for l in md.splitlines():
        if l.startswith("# "):
            out.append(f"<h2>{html.escape(l[2:])}</h2>")
        elif l.startswith("## "):
            if in_ul: out.append("</ul>"); in_ul = False
            out.append(f"<h3 style='color:#6E3A1C'>{html.escape(l[3:])}</h3>")
        elif l.startswith("- "):
            if not in_ul: out.append("<ul>"); in_ul = True
            out.append(f"<li style='font-size:14px'>{html.escape(l[2:])}</li>")
        elif l.strip():
            if in_ul: out.append("</ul>"); in_ul = False
            out.append(f"<p style='font-size:14px'>{html.escape(l)}</p>")
    if in_ul:
        out.append("</ul>")
    return HTMLResponse(page(u, "브리핑", f"<div class='card'>{''.join(out)}</div>", "/briefing"))


@app.get("/warroom", response_class=HTMLResponse)
def warroom_page(request: Request):
    u = _require(request)
    if isinstance(u, Response):
        return u
    f = config.ARTIFACTS / "boards" / "war_room.html"
    if not f.exists():
        return HTMLResponse(page(u, "War Room", "<div class='card'>War Room 보드가 아직 생성되지 않았습니다.</div>", "/warroom"))
    return HTMLResponse(page(u, "War Room",
        f"<iframe src='/warroom/raw' style='width:100%;height:78vh;border:1px solid #DCCDBB;border-radius:12px;background:#fff'></iframe>",
        "/warroom"))


@app.get("/warroom/raw", response_class=HTMLResponse)
def warroom_raw(request: Request):
    u = _require(request)
    if isinstance(u, Response):
        return u
    return HTMLResponse((config.ARTIFACTS / "boards" / "war_room.html").read_text(encoding="utf-8"))


@app.get("/audit", response_class=HTMLResponse)
def audit_page(request: Request):
    u = _require(request)
    if isinstance(u, Response):
        return u
    rows = inbox.audit()[:60]
    body = "".join(
        f"<tr><td>{html.escape(str(r.get('at',''))[:16])}</td><td>{html.escape(r.get('action',''))}</td>"
        f"<td>{html.escape(r.get('actor',''))}</td><td>#{r.get('card_id')}</td>"
        f"<td>{html.escape((r.get('note') or '')[:80])}</td></tr>" for r in rows)
    return HTMLResponse(page(u, "감사 로그",
        f"<h2>감사 로그</h2><p class='sub'>누가 · 언제 · 무엇을 — 수정 불가 기록</p>"
        f"<table><tr><th>시각</th><th>행위</th><th>담당</th><th>카드</th><th>비고</th></tr>{body}</table>",
        "/audit"))
