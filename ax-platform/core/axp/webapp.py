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
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from . import common, config, db
from .agents import inbox
from .dataset import codemap
from .graph import confidence, evidence
from .judge import cards as jcards

SECRET = os.environ.get("AXP_SECRET", "")
if not SECRET:
    if os.environ.get("AXP_MODE") == "prod":
        # P5-SEC3: 운영에서 서명 키 없이 뜨면 세션·CSRF 전부 위조 가능 — 기동 거부
        raise RuntimeError("AXP_SECRET 미설정 — 운영(prod)에서는 필수입니다 (/etc/axp/env)")
    SECRET = "dev-secret-change-me"      # 개발·테스트 전용 폴백
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
CREATE TABLE IF NOT EXISTS axp_login_attempts (
  username TEXT PRIMARY KEY,
  fails INTEGER NOT NULL DEFAULT 0,
  locked_until TEXT NOT NULL DEFAULT ''
);
"""

# P4-2: 공개 인터넷 대비 — 실패 5회면 15분 잠금(존재하지 않는 계정도 동일
# 동작으로 계정 존재 여부를 흘리지 않는다). 잠금 발생은 경보로 남긴다.
LOCK_THRESHOLD = int(os.environ.get("AXP_LOCK_THRESHOLD", "5"))
LOCK_MINUTES = int(os.environ.get("AXP_LOCK_MINUTES", "15"))


def _login_locked(username: str) -> bool:
    row = db.one("SELECT locked_until FROM axp_login_attempts WHERE username=?",
                 (username,))
    return bool(row and row["locked_until"] and
                row["locked_until"] > datetime.now(timezone.utc).isoformat())


def _login_fail(username: str) -> None:
    row = db.one("SELECT fails FROM axp_login_attempts WHERE username=?", (username,))
    fails = (row["fails"] if row else 0) + 1
    locked = ""
    if fails >= LOCK_THRESHOLD:
        locked = (datetime.now(timezone.utc)
                  + timedelta(minutes=LOCK_MINUTES)).isoformat()
        common.alert("warn", "webapp",
                     f"로그인 {fails}회 실패로 계정 잠금({LOCK_MINUTES}분): {username}")
        fails = 0
    db.execute(
        "INSERT INTO axp_login_attempts (username, fails, locked_until) VALUES (?,?,?) "
        "ON CONFLICT(username) DO UPDATE SET fails=excluded.fails, "
        "locked_until=excluded.locked_until", (username, fails, locked))


def _login_ok(username: str) -> None:
    db.execute("DELETE FROM axp_login_attempts WHERE username=?", (username,))


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


# P5-S1: 세션 만료 — 토큰은 username|만료시각|서명. 만료 지나면 재로그인.
# P5-SEC2: 서명에 비밀번호 해시 조각을 바인딩 — 비밀번호 변경·재발급 즉시
#   기존 세션 전부 무효(도난 쿠키 축출). 'sess|' 접두로 CSRF와 도메인 분리(P5-SEC4).
SESSION_HOURS = int(os.environ.get("AXP_SESSION_HOURS", "12"))


def _session_sig(username: str, exp: str | int, pw_hash: str) -> str:
    return _sign(f"sess|{username}|{exp}|{pw_hash[:12]}")


def _session_token(username: str) -> str:
    u = db.one("SELECT pw_hash FROM axp_users WHERE username=?", (username,))
    exp = int((datetime.now(timezone.utc)
               + timedelta(hours=SESSION_HOURS)).timestamp())
    return f"{username}|{exp}|{_session_sig(username, exp, u['pw_hash'])}"


def current_user(request: Request) -> dict | None:
    tok = request.cookies.get("axp_session", "")
    parts = tok.rsplit("|", 2)
    if len(parts) != 3:
        return None
    name, exp, sig = parts
    try:
        if int(exp) < datetime.now(timezone.utc).timestamp():
            return None                        # 만료 — 재로그인 유도
    except ValueError:
        return None
    ensure_users()
    u = db.one("SELECT * FROM axp_users WHERE username=?", (name,))
    if u is None or not hmac.compare_digest(
            _session_sig(name, exp, u["pw_hash"]), sig):
        return None                            # 위조 또는 비밀번호 변경 후 구세션
    return u


# P5-S3: CSRF — 세션에서 파생한 토큰을 모든 POST 폼에 심고 검사한다.
# 'csrf|' 접두 + 말미 고정 문자열로 세션 서명과 형식이 절대 겹치지 않는다(P5-SEC4).
def _csrf_token(u: dict) -> str:
    return _sign("csrf|" + u["username"] + "|form")


def csrf_field(u: dict) -> str:
    return f"<input type='hidden' name='_csrf' value='{_csrf_token(u)}'>"


async def _csrf_ok(request: Request, u: dict) -> bool:
    form = await request.form()
    return hmac.compare_digest(str(form.get("_csrf", "")), _csrf_token(u))


def _require(request: Request, roles: tuple[str, ...] = ()) -> dict | Response:
    u = current_user(request)
    if u is None:
        return RedirectResponse("/login", status_code=303)
    # P5-S2: 초기 비밀번호 상태면 변경 전까지 다른 화면을 막는다
    if u.get("must_change") and request.url.path not in ("/password", "/logout"):
        return RedirectResponse("/password", status_code=303)
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
.subnav{padding:6px 0 8px}
.subnav a{color:#D8C9B4;text-decoration:none;font-size:13px;margin-right:14px;
  padding:2px 8px;border-radius:10px}
.subnav a.on{background:#4A3521;color:#fff}
/* P8-4: 휴대폰에서 승인·브리핑이 그대로 쓰이도록 — 탭 타깃 확대,
   표는 가로 스크롤, 입력은 16px(iOS 자동 확대 방지) */
@media(max-width:640px){header nav a{margin-right:9px;font-size:13px}
main{padding:16px 0 44px}
.btn{padding:10px 16px;font-size:14px}
input,select{font-size:16px}
table{display:block;overflow-x:auto}
.subnav{overflow-x:auto;white-space:nowrap}}
</style>"""

# P5-S3/S4: CSRF 중앙 강제(로그인 제외 전 POST) + 보안 헤더.
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    if request.method == "POST" and request.url.path != "/login":
        u = current_user(request)
        if u is not None:
            body = await request.body()

            async def replay():
                return {"type": "http.request", "body": body, "more_body": False}

            tmp = Request(request.scope, replay)
            try:
                form = await tmp.form()
                ok = hmac.compare_digest(str(form.get("_csrf", "")), _csrf_token(u))
            except Exception:  # noqa: BLE001
                ok = False
            request._receive = replay          # 하류 핸들러가 본문을 다시 읽도록
            if not ok:
                return HTMLResponse(page(u, "보안",
                    "<div class='card warn'>보안 토큰이 유효하지 않습니다 — "
                    "화면을 새로고침한 뒤 다시 시도하세요.</div>"), 403)
    resp = await call_next(request)
    resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "same-origin")
    resp.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
        "form-action 'self'; base-uri 'none'")   # P5-SEC1: 주입 폼의 외부 전송 차단
    return resp


# P8-1: 정보구조 — 기능 목록(14개 평면 메뉴)에서 '일' 중심 4허브+관리로 재편.
# 기존 주소는 전부 보존(화면은 그대로, 묶음과 이름만 사용자 말로 바꾼다).
# 관리 허브는 admin에게만 노출되고, 접근 권한은 종전대로 각 라우트의
# _require가 강제한다(메뉴 숨김은 정리이지 보안이 아니다).
HUBS = [
    ("오늘", "/today", (), [("/today", "오늘 할 일"), ("/briefing", "아침 브리핑"),
                            ("/ask", "질문")]),
    ("데이터", "/upload", (), [("/upload", "자료 반입"), ("/connect", "Odoo 연결"),
                               ("/quarantine", "확인할 이름(격리)"),
                               ("/runs", "지금 반영(배치)"), ("/assets", "자산 대장")]),
    ("판단", "/inbox", (), [("/inbox", "승인함"), ("/promotions", "자동실행 위임"),
                            ("/rules", "규칙"), ("/warroom", "War Room")]),
    ("성과", "/projects", (), [("/projects", "프로젝트·KPI"), ("/audit", "감사 로그")]),
    ("관리", "/users", ("admin",), [("/users", "계정"), ("/setup", "온보딩 설정"),
                                    ("/billing", "과금"), ("/signups", "체험 신청")]),
]

# P8-1: 역할이 홈을 결정한다 — 대표는 성과부터, 승인자는 결정부터.
HOME_BY_ROLE = {"admin": "/today", "steward": "/upload",
                "approver": "/inbox", "viewer": "/projects"}


def page(user: dict | None, title: str, body: str, active: str = "") -> str:
    # P8-1: 2단 내비 — 윗줄은 허브 4+관리, 아랫줄은 현재 허브의 화면들.
    role = (user or {}).get("role", "")
    cur_hub = next((h for h in HUBS if any(p == active for p, _ in h[3])), None)
    nav = "".join(
        f"<a href='{h[1]}' class='{'on' if cur_hub is h else ''}'>{h[0]}</a>"
        for h in HUBS if not h[2] or role in h[2])
    subnav = ""
    if cur_hub and (not cur_hub[2] or role in cur_hub[2]):
        subnav = ("<div class='wrap subnav'>" + "".join(
            f"<a href='{p}' class='{'on' if p == active else ''}'>{t}</a>"
            for p, t in cur_hub[3]) + "</div>")
    who = (f"<span class='who'>{html.escape(user['display'])} ({user['role']}) · "
           f"<a href='/password' style='color:#B9A78F'>비밀번호</a> · "
           f"<form method='post' action='/logout' style='display:inline'>"
           f"<button style='background:none;border:none;color:#B9A78F;cursor:pointer;"
           f"padding:0;font:inherit;text-decoration:underline'>로그아웃</button></form></span>") if user else ""
    warn = ("<div class='note'>⚠ 초기 비밀번호 사용 중 — <a href='/password'><b>지금 변경</b></a>하세요.</div>"
            if user and user.get("must_change") else "")
    # P4-2: 회사명 표시 + 체험판 워터마크 — 합성 데이터임을 화면에 상시 고지
    from . import profile_rt
    prof = profile_rt.load()
    brand = html.escape(prof.get("company", "") or "")
    trial_badge = ("<span style='background:#A8493B;color:#fff;border-radius:4px;"
                   "padding:2px 8px;font-size:12px;margin-left:8px'>체험판 · 합성 데이터</span>"
                   if prof.get("trial") else "")
    brand_html = (f"<span style='color:#B9A78F;margin-left:10px'>{brand}</span>"
                  if brand else "") + trial_badge
    doc = f"""<!doctype html><meta charset='utf-8'>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — AX 플랫폼</title>{STYLE}
<header><div class="wrap bar"><span class="mark">AX</span><b>AX 플랫폼</b>{brand_html}
<nav>{nav}</nav>{who}</div>{subnav}</header>
<main><div class="wrap">{warn}{body}</div></main>"""
    if user is not None:
        # P5-S3: 모든 POST 폼에 CSRF 토큰 자동 주입 — 폼을 새로 만들어도 자동 방어
        import re as _re
        doc = _re.sub(r"(<form\b[^>]*method=[\"']post[\"'][^>]*>)",
                      lambda m: m.group(1) + csrf_field(user), doc,
                      flags=_re.IGNORECASE)
    return doc


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
    if _login_locked(username):
        return HTMLResponse(page(None, "로그인",
            f"<div class='card warn'>로그인이 잠시 잠겼습니다({LOCK_MINUTES}분) — "
            f"연속 실패가 많았습니다. 잠시 후 다시 시도하세요.</div>"), 423)
    u = db.one("SELECT * FROM axp_users WHERE username=?", (username,))
    if not u or not hmac.compare_digest(u["pw_hash"], _hash(password, u["salt"])):
        _login_fail(username)
        return HTMLResponse(page(None, "로그인", "<div class='card warn'>아이디 또는 비밀번호가 다릅니다. <a href='/login'>다시</a></div>"), 401)
    _login_ok(username)
    # P6-1: 미납 잠금 — 관리자만 들어와 수납·해제할 수 있다(데이터는 보존).
    from . import billing
    if billing.is_locked() and u["role"] != "admin":
        return HTMLResponse(page(None, "이용 정지",
            "<div class='card warn'><b>구독 미납으로 이용이 잠시 정지되었습니다.</b><br>"
            "데이터는 안전하게 보존 중입니다 — 관리자(계약 담당)에게 문의해 주세요.</div>"), 402)
    # P8-1: 역할별 홈 — 대표는 성과, 승인자는 판단, 실무는 데이터, admin은 오늘
    r = RedirectResponse(HOME_BY_ROLE.get(u["role"], "/inbox"), status_code=303)
    r.set_cookie("axp_session", _session_token(username),
                 httponly=True, samesite="lax",
                 secure=os.environ.get("AXP_MODE") == "prod",
                 max_age=SESSION_HOURS * 3600)
    return r


@app.post("/logout")
def logout():
    # P5-SEC5: 상태 변경은 POST + CSRF — 외부 페이지의 강제 로그아웃 차단
    r = RedirectResponse("/login", status_code=303)
    r.delete_cookie("axp_session")
    return r


@app.get("/logout")
def logout_get():
    return RedirectResponse("/inbox", status_code=303)   # GET은 아무것도 바꾸지 않는다


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
def root_page(request: Request):
    u = _require(request)
    if isinstance(u, Response):
        return u
    return RedirectResponse(HOME_BY_ROLE.get(u["role"], "/inbox"), status_code=303)


# ── P8-3: 시작 여정 5단계 — 전부 끝나면 사라진다 ──────────────────
def _journey_card() -> str:
    from . import profile_rt
    from . import projects as _pj
    prof = profile_rt.load()
    _pj.init()
    has_data = any(
        db.table_exists(t) and (db.scalar(f"SELECT COUNT(*) FROM {t}") or 0)
        for t in ("staging_sales", "fact_sales"))
    steps = [
        ("회사 설정", bool(prof.get("company")), "/setup"),
        ("자료 반입", has_data, "/upload"),
        ("프로젝트 정의", (db.scalar("SELECT COUNT(*) FROM axp_projects") or 0) > 0, "/projects"),
        ("KPI 목표 설정", (db.scalar(
            "SELECT COUNT(*) FROM axp_project_kpis WHERE target IS NOT NULL") or 0) > 0, "/projects"),
        ("첫 측정", (db.scalar("SELECT COUNT(*) FROM axp_kpi_measurements") or 0) > 0, "/projects"),
    ]
    done = sum(1 for _, ok, _2 in steps if ok)
    if done == len(steps):
        return ""
    items = " ".join(
        (f"<span style='color:#0E8F86'>✓ {name}</span>" if ok
         else f"<a href='{href}'><b>→ {name}</b></a>")
        for name, ok, href in steps)
    return (f"<div class='card' style='border-left:4px solid #C07F1E'>"
            f"<b>시작 여정 {done}/{len(steps)}</b>"
            f"<div class='sub' style='margin-top:4px'>{items}</div>"
            f"<div class='sub'>화살표가 붙은 다음 단계를 누르면 그 화면으로 갑니다 — "
            f"5단계가 끝나면 이 카드는 사라집니다.</div></div>")


# ── P8-2: '오늘' 홈 — 브리핑·할 일·질문이 한 화면에 ────────────────
def _today_body(u: dict) -> str:
    from . import projects
    todos: list[tuple[str, str, str]] = []
    if db.table_exists("judgment_cards"):
        n = db.scalar("SELECT COUNT(*) FROM judgment_cards WHERE status='proposed'") or 0
        if n:
            todos.append((f"승인 대기 카드 {n}건", "/inbox", "AI 제안이 결정을 기다립니다"))
    if db.table_exists("quarantine_queue"):
        n = db.scalar("SELECT COUNT(*) FROM quarantine_queue WHERE status='pending'") or 0
        if n:
            todos.append((f"확인할 이름 {n}건", "/quarantine",
                          "처음 본 매장·품목 이름 — 확정해야 반입이 완성됩니다"))
    try:
        miss = projects.underachieving()
    except Exception:  # noqa: BLE001 — 프로젝트 미사용 프로파일에서도 홈은 뜬다
        miss = []
    if miss:
        names = " · ".join(f"{m['project']}: {m['kpi_name']}" for m in miss[:4])
        todos.append((f"목표 미달 KPI {len(miss)}건", f"/projects/{miss[0]['project_id']}",
                      names))
    cards = "".join(
        f"<a href='{href}' style='text-decoration:none;color:inherit'><div class='card'>"
        f"<b style='color:#A8493B'>{html.escape(head)} →</b>"
        f"<div class='sub'>{html.escape(sub)}</div></div></a>"
        for head, href, sub in todos)
    if not todos:
        cards = ("<div class='card'><b style='color:#0E8F86'>오늘 처리할 일이 없습니다 ✓</b>"
                 "<div class='sub'>새 자료가 들어오거나 KPI가 미달로 바뀌면 여기에 나타납니다.</div></div>")
    admin_line = ""
    if u["role"] == "admin":
        admin_line = ("<p class='sub'>시스템: <a href='/status'>상태 페이지</a> · "
                      "<a href='/runs'>배치·재학습 이력</a></p>")
    return f"""<h2>오늘 — {html.escape(common.now_iso()[:10])}</h2>
<p class="sub">할 일을 하나씩 누르면 바로 그 화면으로 갑니다. 자세한 어제 이야기는
<a href='/briefing'>아침 브리핑</a>에.</p>
{_journey_card()}
{cards}
<form method="post" action="/ask" class="card" style="max-width:640px">
  <b>무엇이든 물어보세요</b>
  <p style="display:flex;gap:6px"><input name="q" placeholder="예: 이번 주 폐기율 왜 올랐어?"
     style="flex:1"><button class="btn ok">질문</button></p>
</form>
{admin_line}"""


@app.get("/today", response_class=HTMLResponse)
def today_page(request: Request):
    u = _require(request)
    if isinstance(u, Response):
        return u
    return HTMLResponse(page(u, "오늘", _today_body(u), "/today"))


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
    # P5-SEC1: 사유 코드는 서버에서 화이트리스트 강제 — 셀렉트는 클라이언트일 뿐
    if not ok and reason not in inbox.REJECT_REASONS:
        return HTMLResponse(page(u, "반려",
            f"<div class='card warn'>사유는 목록에서 선택하세요: {', '.join(inbox.REJECT_REASONS)}</div>"), 400)
    inbox.decide(card_id, actor=u["display"], role="card_approver",
                 approve=ok, reason_code=reason[:20], reason_text=reason)
    if ok:
        inbox.apply_feedback(card_id, actor=u["display"])
    return RedirectResponse("/inbox", status_code=303)


# ── 격리 큐 (스튜어드) ──────────────────────────────────
# ── P4-12: 수동 배치 실행 — 업로드한 자료를 기다림 없이 반영 (admin) ──
RUNS_DDL = """
CREATE TABLE IF NOT EXISTS batch_runs (
  run_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_date TEXT NOT NULL, requested_by TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'running'
         CHECK (status IN ('running','done','failed')),
  summary TEXT DEFAULT '', started_at TEXT NOT NULL, finished_at TEXT
);
"""


def _runs_page(u, msg: str = "") -> str:
    db.executescript(RUNS_DDL)
    rows = db.query("SELECT * FROM batch_runs ORDER BY run_id DESC LIMIT 10")
    running = any(r["status"] == "running" for r in rows)
    trs = "".join(
        f"<tr><td>#{r['run_id']}</td><td>{html.escape(r['run_date'])}</td>"
        f"<td>{ {'running': '실행 중…', 'done': '완료', 'failed': '실패'}[r['status']] }</td>"
        f"<td>{html.escape(r['requested_by'])}</td>"
        f"<td>{html.escape((r['summary'] or '')[:120])}</td>"
        f"<td>{html.escape(r['started_at'][11:19])}~{html.escape((r['finished_at'] or '')[11:19])}</td></tr>"
        for r in rows)
    today = datetime.now(timezone.utc).date().isoformat()
    btn = ("<div class='card warn'>이미 실행 중입니다 — 끝나면 아래 이력에 결과가 남습니다. "
           "<a href='/runs'>새로고침</a></div>" if running else f"""
<form method="post" class="card" style="max-width:460px">
  <b>지금 실행</b><p class="sub">업로드한 자료를 야간 배치를 기다리지 않고 반영합니다
  (표준화→품질→특징량→그래프→에이전트→브리핑 — 수 분 소요).</p>
  <p><input name="run_date" value="{today}" style="width:160px"> 기준일</p>
  <button class="btn ok">배치 실행</button>
</form>""")
    # P5-O: 에이전트 최근 상태 — '학습 전 대기'(P5-N)를 운영자가 화면에서
    # 보게 한다(crit이 아닌 이유와 시작 조건이 사유에 담긴다).
    agents_html = ""
    if db.table_exists("agent_runs"):
        ag = db.query(
            "SELECT agent, status, error FROM agent_runs "
            "WHERE run_id IN (SELECT MAX(run_id) FROM agent_runs GROUP BY agent) "
            "ORDER BY agent")
        if ag:
            lbl = {"ok": "정상", "waiting": "대기(학습 전)",
                   "error": "실패", "running": "실행 중"}
            ars = "".join(
                f"<tr><td>{html.escape(a['agent'])}</td>"
                f"<td>{lbl.get(a['status'], html.escape(a['status'] or ''))}</td>"
                f"<td class='sub'>{html.escape((a['error'] or '')[:140])}</td></tr>"
                for a in ag)
            agents_html = (f"<div class='card'><b>에이전트 최근 상태</b>"
                           f"<table style='width:100%;margin-top:8px'>"
                           f"<tr><th>에이전트</th><th>상태</th><th>사유</th></tr>{ars}</table></div>")
    # P6-5: 재학습 이력 — 주간 판정(keep/retrain·게이트 승격 여부)을 화면으로.
    retrain_html = ""
    if db.table_exists("retrain_log"):
        rl = db.query("SELECT * FROM retrain_log ORDER BY run_at DESC LIMIT 5")
        if rl:
            rrs = "".join(
                f"<tr><td>{html.escape((r['as_of'] or '')[:10])}</td>"
                f"<td>{'유지' if r['decision'] == 'keep' else '재학습'}</td>"
                f"<td class='sub'>{html.escape(r['reason'] or '')}</td>"
                f"<td>{html.escape(r['old_version'] or '')}"
                f"{('→' + html.escape(r['new_version'])) if r['new_version'] else ''}</td>"
                f"<td>{'승격' if r['promoted'] else ('—' if r['decision'] == 'keep' else '게이트 불통과')}</td></tr>"
                for r in rl)
            retrain_html = ("<div class='card'><b>모델 재학습 이력(주간)</b>"
                            "<table style='width:100%;margin-top:8px'>"
                            "<tr><th>기준일</th><th>판정</th><th>사유</th><th>버전</th><th>결과</th></tr>"
                            f"{rrs}</table></div>")
    return f"""<h2>배치 실행 — 판단의 공장을 지금 돌립니다</h2>{msg}{btn}
<div class="card"><b>최근 실행</b><table style="width:100%;margin-top:8px">
<tr><th>#</th><th>기준일</th><th>상태</th><th>요청자</th><th>요약</th><th>시각(UTC)</th></tr>{trs}</table></div>{agents_html}{retrain_html}"""


def _run_cycle_bg(run_id: int, run_date: str) -> None:
    """백그라운드 스레드 — 자체 예외 처리로 상태를 반드시 기록한다."""
    try:
        from . import scheduler
        res = scheduler.run_cycle(run_date)
        bad = {k: v for k, v in res.items() if v != "ok"}
        db.execute("UPDATE batch_runs SET status=?, summary=?, finished_at=? WHERE run_id=?",
                   ("done" if not bad else "failed",
                    "전 단계 정상" if not bad else f"실패 단계: {', '.join(bad)}",
                    common.now_iso(), run_id))
    except Exception as e:  # noqa: BLE001
        db.execute("UPDATE batch_runs SET status='failed', summary=?, finished_at=? WHERE run_id=?",
                   (str(e)[:300], common.now_iso(), run_id))


@app.get("/runs", response_class=HTMLResponse)
def runs_page(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    return HTMLResponse(page(u, "배치 실행", _runs_page(u), "/runs"))


@app.post("/runs", response_class=HTMLResponse)
async def runs_start(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    db.executescript(RUNS_DDL)
    if db.one("SELECT 1 FROM batch_runs WHERE status='running'"):
        return HTMLResponse(page(u, "배치 실행", _runs_page(u,
            "<div class='card warn'>이미 실행 중 — 동시 실행은 막습니다.</div>"), "/runs"), 409)
    form = await request.form()
    run_date = str(form.get("run_date", "")).strip() \
        or datetime.now(timezone.utc).date().isoformat()
    try:
        datetime.fromisoformat(run_date)
    except ValueError:
        return HTMLResponse(page(u, "배치 실행", _runs_page(u,
            "<div class='card warn'>기준일 형식은 YYYY-MM-DD 입니다.</div>"), "/runs"), 400)
    with db.conn() as c:
        cur = c.execute(
            "INSERT INTO batch_runs (run_date, requested_by, started_at) VALUES (?,?,?)",
            (run_date, u["username"], common.now_iso()))
        run_id = cur.lastrowid
    import threading
    threading.Thread(target=_run_cycle_bg, args=(run_id, run_date),
                     daemon=True).start()
    common.alert("info", "webapp", f"수동 배치 실행 #{run_id}({run_date}) by {u['username']}")
    return HTMLResponse(page(u, "배치 실행", _runs_page(u,
        f"<div class='card ok'>실행 #{run_id} 시작 — 이력에서 진행을 확인하세요.</div>"),
        "/runs"))


# ── P4-10: 계정 관리 — 추가·임시 비밀번호 재발급·잠금 해제 (admin) ────
ROLES = ("admin", "steward", "approver", "viewer")
ROLE_LABEL = {"admin": "관리자", "steward": "데이터 스튜어드",
              "approver": "승인자", "viewer": "열람"}


def _users_page(u, msg: str = "") -> str:
    rows = db.query("SELECT username, role, display, must_change FROM axp_users "
                    "ORDER BY username")
    locks = {r["username"]: r for r in db.query(
        "SELECT username, fails, locked_until FROM axp_login_attempts")}
    now = datetime.now(timezone.utc).isoformat()
    trs = ""
    for r in rows:
        lk = locks.get(r["username"])
        locked = bool(lk and lk["locked_until"] and lk["locked_until"] > now)
        state = ("잠금 중" if locked else
                 ("초기 비밀번호" if r["must_change"] else "정상"))
        actions = (f"<form method='post' action='/users/reset' style='display:inline'>"
                   f"<input type='hidden' name='username' value='{html.escape(r['username'])}'>"
                   f"<button class='btn plain'>임시 비밀번호 재발급</button></form>")
        if locked or (lk and lk["fails"]):
            actions += (f" <form method='post' action='/users/unlock' style='display:inline'>"
                        f"<input type='hidden' name='username' value='{html.escape(r['username'])}'>"
                        f"<button class='btn plain'>잠금 해제</button></form>")
        trs += (f"<tr><td>{html.escape(r['username'])}</td>"
                f"<td>{ROLE_LABEL.get(r['role'], r['role'])}</td>"
                f"<td>{html.escape(r['display'])}</td>"
                f"<td>{state}</td><td>{actions}</td></tr>")
    opts = "".join(f"<option value='{r}'>{ROLE_LABEL[r]}</option>"
                   for r in ("viewer", "approver", "steward", "admin"))
    return f"""<h2>계정 관리 — 발급은 봉투처럼</h2>
<p class="sub">임시 비밀번호는 이 화면에 <b>한 번만</b> 표시됩니다 — 전달 후에는 다시 볼 수 없고,
사용자는 첫 로그인에서 변경해야 합니다. 체험 신청(승인제) 접수 후 여기서 계정을 만들어 회신하세요.</p>{msg}
<div class="card"><table style="width:100%">
<tr><th>아이디</th><th>역할</th><th>표시 이름</th><th>상태</th><th>동작</th></tr>{trs}</table></div>
<form method="post" action="/users/add" class="card" style="max-width:560px">
  <b>새 계정</b>
  <p style="display:flex;gap:8px;margin-top:8px">
    <input name="username" placeholder="아이디 (영소문자·숫자)" style="flex:1" required>
    <select name="role">{opts}</select></p>
  <p><input name="display" placeholder="표시 이름 (예: 김순희)" style="width:100%" required></p>
  <button class="btn ok">계정 만들기</button>
</form>"""


# ── P7-2: 프로젝트·KPI 센터 — 정의→모듈·알고리즘→KPI→성과→피드백 ──
def _kpi_svg(vals: list[float], target: float | None, direction: str) -> str:
    """측정 시계열의 소형 SVG 차트 — 외부 라이브러리 없이 서버에서 그린다."""
    if not vals:
        return "<span class='sub'>측정 전</span>"
    w, h, pad = 260, 64, 6
    lo, hi = min(vals + ([target] if target is not None else [])), \
        max(vals + ([target] if target is not None else []))
    if hi == lo:
        hi = lo + 1
    def sx(i):
        return pad + (w - 2 * pad) * (i / max(len(vals) - 1, 1))
    def sy(v):
        return h - pad - (h - 2 * pad) * ((v - lo) / (hi - lo))
    pts = " ".join(f"{sx(i):.1f},{sy(v):.1f}" for i, v in enumerate(vals))
    tline = ""
    if target is not None:
        ty = sy(target)
        tline = (f"<line x1='{pad}' y1='{ty:.1f}' x2='{w-pad}' y2='{ty:.1f}' "
                 f"stroke='#C07F1E' stroke-dasharray='4 3' stroke-width='1.5'/>")
    dots = "".join(f"<circle cx='{sx(i):.1f}' cy='{sy(v):.1f}' r='2.5' fill='#0E8F86'/>"
                   for i, v in enumerate(vals))
    return (f"<svg width='{w}' height='{h}' viewBox='0 0 {w} {h}' role='img'>"
            f"<polyline points='{pts}' fill='none' stroke='#0E8F86' stroke-width='2'/>"
            f"{tline}{dots}</svg>")


def _projects_list(u, msg: str = "") -> str:
    from . import projects
    rows = projects.listing()
    trs = "".join(
        f"<tr><td><a href='/projects/{r['project_id']}'>#{r['project_id']} "
        f"{html.escape(r['name'])}</a></td>"
        f"<td class='sub'>{html.escape(r['goal'] or '')}</td>"
        f"<td>{html.escape(r['status'])}</td><td>{html.escape(r['created_at'][:10])}</td></tr>"
        for r in rows)
    if not rows:   # P8-3: 빈 상태에도 다음 행동을 안내한다
        trs = ("<tr><td colspan='4' class='sub'>아직 프로젝트가 없습니다 — "
               "아래 <b>새 프로젝트 정의</b>에서 첫 프로젝트를 만들면 "
               "그 영역의 모듈·KPI가 자동 등재됩니다.</td></tr>")
    areas = "".join(
        f"<label style='display:block;margin:4px 0'><input type='checkbox' name='areas' "
        f"value='{code}'> <b>{html.escape(a['name'])}</b> "
        f"<span class='sub'>— {html.escape(' · '.join(m for m, _ in a['modules']))}</span></label>"
        for code, a in projects.AREAS.items())
    return f"""<h2>프로젝트 — 정의에서 성과까지</h2>
<p class="sub">프로젝트를 정의하고 5대 지능화 요구사항에서 우리 회사에 맞는 모듈·알고리즘·KPI를 고르면,
대시보드가 성과를 보여주고 미달 KPI에는 개선 제안 카드가 승인함으로 옵니다 — 조정하면 다시 측정되는 루프입니다.</p>{msg}
<div class="card"><b>프로젝트 목록</b><table style="width:100%;margin-top:8px">
<tr><th>프로젝트</th><th>목표</th><th>상태</th><th>생성</th></tr>{trs}</table></div>
<form method="post" action="/projects/create" class="card" style="max-width:720px">
  <b>새 프로젝트 정의</b>
  <p><input name="name" placeholder="프로젝트 이름 (예: 폐기 절감 1차)" style="width:100%"></p>
  <p><input name="goal" placeholder="경영 목표 한 줄 (예: 월 폐기 20% 절감)" style="width:100%"></p>
  <p class="sub">요구사항 영역 — 고르면 그 영역의 모듈·알고리즘·KPI가 자동 등재됩니다(목표치는 다음 화면에서):</p>
  {areas}
  <button class="btn ok">프로젝트 만들기</button>
</form>"""


@app.get("/projects", response_class=HTMLResponse)
def projects_page(request: Request):
    u = _require(request, ("viewer", "steward", "approver"))
    if isinstance(u, Response):
        return u
    return HTMLResponse(page(u, "프로젝트", _projects_list(u), "/projects"))


@app.post("/projects/create", response_class=HTMLResponse)
async def projects_create(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    from . import projects
    form = await request.form()
    try:
        p = projects.create(str(form.get("name", "")), str(form.get("goal", "")),
                            u["username"], [str(a) for a in form.getlist("areas")])
    except ValueError as e:
        return HTMLResponse(page(u, "프로젝트", _projects_list(u,
            f"<div class='card warn'>{html.escape(str(e))}</div>"), "/projects"), 400)
    return RedirectResponse(f"/projects/{p['project_id']}", status_code=303)


def jcards_listing_kpi():
    from .judge import cards as jcards
    return jcards.listing(status="proposed", kind="kpi_improve")


def _project_dash(u, pid: int, msg: str = "") -> str:
    from . import projects
    p = projects.get(pid)
    stat_color = {"달성": "#0E8F86", "미달": "#A8493B",
                  "측정 전": "#76675A", "목표 미설정": "#C07F1E"}
    cards = []
    for k in p["kpis"]:
        st = projects.kpi_status(k)
        m = projects.latest(k["kpi_id"])
        ser = [r["value"] for r in projects.series(k["kpi_id"])]
        _, pending_reason = (None, "") if m else projects.measure(k["kpi_code"])
        val = (f"{m['value']:g} {html.escape(k['unit'])}" if m
               else f"<span class='sub'>{html.escape(pending_reason)}</span>")
        tgt = f"{k['target']:g}" if k["target"] is not None else "—"
        base = f"{k['baseline']:g}" if k["baseline"] is not None else "—"
        # P7-9: 루프 상태 한 줄 — 미달이면 개선 카드가 어디쯤 있는지 보여준다
        loop_line = ""
        if st == "미달" and m is not None:
            import json as _json
            open_card = next(
                (c["card_id"] for c in jcards_listing_kpi()
                 if _json.loads(c["evidence_json"]).get("kpi_id") == k["kpi_id"]), None)
            if open_card:
                loop_line = (f"<div class='sub'>개선 카드 <a href='/inbox'>#{open_card} "
                             f"승인 대기</a></div>")
            elif db.one("SELECT 1 FROM axp_kpi_feedback WHERE kpi_id=? AND action='improve' "
                        "AND measured_m_id=?", (k["kpi_id"], m["m_id"])):
                loop_line = "<div class='sub'>개선 활동 기록됨 — 다음 측정에서 재판정</div>"
            else:
                loop_line = "<div class='sub'>다음 야간 배치에서 개선 카드가 제안됩니다</div>"
        adjust = f"""<form method="post" action="/projects/{pid}/target" style="margin-top:6px">
  <input type="hidden" name="kpi_id" value="{k['kpi_id']}">
  <input name="target" placeholder="목표" style="width:70px" value="{k['target'] if k['target'] is not None else ''}">
  <input name="note" placeholder="조정 사유" style="width:150px">
  <button class="btn">목표 조정</button></form>""" if u["role"] == "admin" else ""
        cards.append(f"""<div class="card" style="display:inline-block;vertical-align:top;width:340px;margin-right:10px">
  <b>{html.escape(k['kpi_name'])}</b>
  <span style="color:{stat_color.get(st, '#2E241C')};font-weight:700;float:right">{st}</span>
  <div class="sub">{html.escape(projects.AREAS[k['area']]['name'])} · {'낮을수록' if k['direction'] == 'down' else '높을수록'} 좋음</div>
  <div style="font-size:1.5em;margin:6px 0">{val}</div>
  <div class="sub">기준선 {base} · 목표 {tgt}</div>
  {_kpi_svg(ser, k['target'], k['direction'])}{loop_line}{adjust}</div>""")
    mods = "".join(
        f"<tr><td>{html.escape(projects.AREAS[m['area']]['name'])}</td>"
        f"<td>{html.escape(m['module'])}</td><td class='sub'>{html.escape(m['algorithm'])}</td></tr>"
        for m in p["modules"])
    fb = db.query(
        "SELECT f.*, k.kpi_name FROM axp_kpi_feedback f "
        "JOIN axp_project_kpis k ON k.kpi_id=f.kpi_id WHERE k.project_id=? "
        "ORDER BY f.fb_id DESC LIMIT 10", (pid,))
    fbs = "".join(
        f"<tr><td>{html.escape(f['created_at'][:16])}</td><td>{html.escape(f['kpi_name'])}</td>"
        f"<td>{ {'adjust_target': '목표 조정', 'improve': '개선', 'keep': '유지'}[f['action']] }"
        f"{(' ' + str(f['old_target']) + '→' + str(f['new_target'])) if f['action'] == 'adjust_target' else ''}</td>"
        f"<td class='sub'>{html.escape(f['note'] or '')}</td><td>{html.escape(f['decided_by'] or '')}</td></tr>"
        for f in fb)
    # P8-3(대표 실사용 적발): 주 행동 버튼이 캡션 속에 묻혀 못 찾았다 —
    # 제목 옆의 큰 버튼으로 승격.
    measure_btn = (f"<form method='post' action='/projects/{pid}/measure' style='display:inline'>"
                   f"<button class='btn ok' style='font-size:15px;padding:8px 18px'>"
                   f"지금 측정</button></form>"
                   if u["role"] in ("admin", "steward") else "")
    return f"""<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">
<h2 style="margin:0 0 4px">{html.escape(p['name'])} — KPI 대시보드</h2>{measure_btn}</div>
<p class="sub">{html.escape(p['goal'] or '')} · 담당 {html.escape(p['owner'] or '-')} ·
측정은 야간 배치가 자동 누적하고, [지금 측정]은 즉시 갱신합니다.</p>{msg}
<div>{''.join(cards)}</div>
<div class="card"><b>선택 모듈·알고리즘</b><table style="width:100%;margin-top:8px">
<tr><th>영역</th><th>모듈</th><th>알고리즘·방식</th></tr>{mods}</table></div>
<div class="card"><b>피드백·조정 이력 (루프의 기록)</b><table style="width:100%;margin-top:8px">
<tr><th>시각</th><th>KPI</th><th>행동</th><th>메모</th><th>결정자</th></tr>{fbs}</table></div>
<p><a href="/projects">← 프로젝트 목록</a></p>"""


@app.get("/projects/{pid}", response_class=HTMLResponse)
def project_dash(request: Request, pid: int):
    u = _require(request, ("viewer", "steward", "approver"))
    if isinstance(u, Response):
        return u
    from . import projects
    try:
        return HTMLResponse(page(u, "프로젝트", _project_dash(u, pid), "/projects"))
    except ValueError as e:
        return HTMLResponse(page(u, "프로젝트", f"<div class='card warn'>{html.escape(str(e))}</div>"), 404)


@app.post("/projects/{pid}/measure", response_class=HTMLResponse)
async def project_measure(request: Request, pid: int):
    u = _require(request, ("steward",))
    if isinstance(u, Response):
        return u
    from . import projects
    r = projects.measure_all(pid)
    return HTMLResponse(page(u, "프로젝트", _project_dash(u, pid,
        f"<div class='card ok'>측정 완료 — 실측 {r['measured']}건, 측정 전 {r['pending']}건</div>"),
        "/projects"))


@app.post("/projects/{pid}/target", response_class=HTMLResponse)
async def project_target(request: Request, pid: int):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    from . import projects
    form = await request.form()
    try:
        projects.set_target(int(str(form.get("kpi_id", "0"))),
                            float(str(form.get("target", ""))), u["username"],
                            note=str(form.get("note", "")))
    except (ValueError, TypeError) as e:
        return HTMLResponse(page(u, "프로젝트", _project_dash(u, pid,
            f"<div class='card warn'>목표값을 확인하세요: {html.escape(str(e))}</div>"), "/projects"), 400)
    return RedirectResponse(f"/projects/{pid}", status_code=303)


# ── P6-2: 체험 신청·발급 — 승인제 기본, 자동 발급은 스위치 ─────────
_SIGNUP_FORM = """<h2>체험 신청</h2>
<p class="sub">신청 후 {mode} 체험 데이터는 합성 데이터이며, 업로드 파일은 24시간 뒤 파기됩니다.</p>{msg}
<form method="post" class="card" style="max-width:460px">
  <p><input name="company" placeholder="회사명" style="width:100%"></p>
  <p><input name="email" placeholder="이메일" style="width:100%"></p>
  <p><input name="contact" placeholder="담당자 이름(선택)" style="width:100%"></p>
  <p><textarea name="note" placeholder="쓰시는 ERP·궁금한 점(선택)" style="width:100%;height:60px"></textarea></p>
  <p style="display:none"><input name="website" tabindex="-1" autocomplete="off"></p>
  <button class="btn ok" style="width:100%">신청</button>
</form>"""


def _signup_mode() -> str:
    from . import signup
    return ("계정이 즉시 발급됩니다." if signup.auto_issue_enabled()
            else "담당자가 확인 후 1영업일 안에 계정을 보내 드립니다(승인제).")


@app.get("/signup", response_class=HTMLResponse)
def signup_form():
    return HTMLResponse(page(None, "체험 신청",
                             _SIGNUP_FORM.format(mode=_signup_mode(), msg="")))


@app.post("/signup", response_class=HTMLResponse)
async def signup_submit(request: Request):
    from . import signup
    form = await request.form()
    if str(form.get("website", "")):          # 허니팟 — 봇은 조용히 성공 화면만
        return HTMLResponse(page(None, "체험 신청",
            "<div class='card ok'>신청이 접수되었습니다.</div>"))
    try:
        row = signup.submit(str(form.get("company", "")), str(form.get("email", "")),
                            str(form.get("contact", "")), str(form.get("note", "")))
    except ValueError as e:
        return HTMLResponse(page(None, "체험 신청",
            _SIGNUP_FORM.format(mode=_signup_mode(),
                                msg=f"<div class='card warn'>{html.escape(str(e))}</div>")), 400)
    if signup.auto_issue_enabled():
        try:
            r = signup.issue(row["req_id"], "auto(AXP_AUTO_ISSUE)")
            creds = Path(r["tenant"]["credentials_file"]).read_text(encoding="utf-8")
            return HTMLResponse(page(None, "체험 발급", f"""
<div class='card ok'><b>체험 계정이 발급되었습니다 — 이 화면은 한 번만 보입니다.</b>
<pre style='white-space:pre-wrap'>{html.escape(creds)}</pre>
<p class='sub'>첫 로그인에서 비밀번호를 바꾸게 됩니다. 접속 주소는 안내 메일을 확인하세요.</p></div>"""))
        except Exception as e:  # noqa: BLE001 — 발급 실패는 대기로 남고 사람이 잇는다
            common.alert("warn", "signup", f"자동 발급 실패 #{row['req_id']}: {e} — 승인제 경로로 대기")
    return HTMLResponse(page(None, "체험 신청",
        "<div class='card ok'>신청이 접수되었습니다 — 담당자가 확인 후 이메일로 안내드립니다.</div>"))


def _signups_page(u, msg: str = "") -> str:
    from . import signup
    rows = signup.pending()
    trs = "".join(
        f"<tr><td>#{r['req_id']}</td><td>{html.escape(r['company'])}</td>"
        f"<td>{html.escape(r['email'])}</td><td class='sub'>{html.escape(r['note'] or '')}</td>"
        f"<td><form method='post' action='/signups/issue' style='display:inline'>"
        f"<input type='hidden' name='req_id' value='{r['req_id']}'>"
        f"<button class='btn ok'>발급</button></form> "
        f"<form method='post' action='/signups/reject' style='display:inline'>"
        f"<input type='hidden' name='req_id' value='{r['req_id']}'>"
        f"<button class='btn'>반려</button></form></td></tr>" for r in rows)
    mode = "자동 발급 켜짐(AXP_AUTO_ISSUE=1)" if signup.auto_issue_enabled() \
        else "승인제(자동 발급 꺼짐 — 접수된 결정)"
    return (f"<h2>체험 신청 관리</h2><p class='sub'>현재 모드: {mode}. 발급 시 테넌트가 만들어지고 "
            f"초기 비밀번호 파일 경로가 표시됩니다 — 이메일 발송은 수동입니다(SMTP 결선 전).</p>{msg}"
            f"<div class='card'><b>대기 {len(rows)}건</b><table style='width:100%;margin-top:8px'>"
            f"<tr><th>#</th><th>회사</th><th>이메일</th><th>메모</th><th></th></tr>{trs}</table></div>")


@app.get("/signups", response_class=HTMLResponse)
def signups_page(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    return HTMLResponse(page(u, "체험 신청 관리", _signups_page(u), "/signups"))


@app.post("/signups/issue", response_class=HTMLResponse)
async def signups_issue(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    from . import signup
    form = await request.form()
    try:
        r = signup.issue(int(str(form.get("req_id", "0"))), u["username"])
        msg = (f"<div class='card ok'>발급 완료 — 테넌트 {html.escape(r['request']['tenant_name'])} · "
               f"초기 계정: {html.escape(r['tenant']['credentials_file'])}</div>")
    except (ValueError, TypeError) as e:
        msg = f"<div class='card warn'>{html.escape(str(e))}</div>"
    return HTMLResponse(page(u, "체험 신청 관리", _signups_page(u, msg), "/signups"))


@app.post("/signups/reject", response_class=HTMLResponse)
async def signups_reject(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    from . import signup
    form = await request.form()
    try:
        signup.reject(int(str(form.get("req_id", "0"))), u["username"])
    except (ValueError, TypeError):
        pass
    return RedirectResponse("/signups", status_code=303)


# ── P6-1: 과금 — 구독·청구·미납 잠금 (admin) ─────────────────────
def _billing_page(u, msg: str = "") -> str:
    from . import billing
    sub = billing.get()
    inv = billing.invoices()
    stat_lbl = {"active": "정상", "past_due": "납기 경과", "locked": "미납 잠금"}
    if sub:
        head = (f"<div class='card'><b>구독</b> — 플랜 {html.escape(sub['plan'])} · "
                f"월 {sub['monthly_fee']:,}원 · 상태 <b>{stat_lbl.get(sub['status'], sub['status'])}</b>"
                + (f" <form method='post' action='/billing/unlock' style='display:inline'>"
                   f"<button class='btn'>잠금 해제</button></form>"
                   if sub["status"] == "locked" else "") + "</div>")
    else:
        head = "<div class='card sub'>구독 미설정 — 아래에서 플랜을 정하면 과금이 시작됩니다.</div>"
    ivs = "".join(
        f"<tr><td>#{i['invoice_id']}</td><td>{html.escape(i['period'])}</td>"
        f"<td>{i['amount']:,}원</td>"
        f"<td>{ {'issued': '발행', 'paid': '수납', 'overdue': '미납'}[i['status']] }</td>"
        f"<td>{html.escape(i['due_date'] or '')}</td>"
        f"<td>{('' if i['status'] == 'paid' else f'''<form method='post' action='/billing/paid' style='display:inline'><input type='hidden' name='invoice_id' value='{i['invoice_id']}'><button class='btn ok'>수납 처리</button></form>''')}</td></tr>"
        for i in inv)
    plans = "".join(f"<option value='{k}'>{k}</option>" for k in ("trial", "standard", "pilot"))
    return f"""<h2>과금 — 구독과 청구</h2>
<p class="sub">수납은 사람이 확인하고 기록합니다(자동 출금은 결제 수단 확정 후 — 6단계 계획서 A4).
잠금은 데이터를 지우지 않습니다 — 로그인만 막고, 수납 즉시 원상복구.</p>{msg}{head}
<form method="post" action="/billing/plan" class="card" style="max-width:460px">
  <b>플랜 설정</b>
  <p><select name="plan">{plans}</select>
     <input name="monthly_fee" placeholder="월 요금(원)" style="width:140px"> </p>
  <button class="btn ok">저장</button>
</form>
<form method="post" action="/billing/issue" class="card" style="max-width:460px">
  <b>이번 달 청구 발행</b><p class="sub">멱등 — 이미 발행된 달은 그대로 둡니다. trial(0원)은 발행 없음.</p>
  <button class="btn ok">발행</button>
</form>
<div class="card"><b>청구 이력</b><table style="width:100%;margin-top:8px">
<tr><th>#</th><th>기간</th><th>금액</th><th>상태</th><th>납기</th><th></th></tr>{ivs}</table></div>"""


@app.get("/billing", response_class=HTMLResponse)
def billing_page(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    return HTMLResponse(page(u, "과금", _billing_page(u), "/billing"))


@app.post("/billing/plan", response_class=HTMLResponse)
async def billing_plan(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    from . import billing
    form = await request.form()
    try:
        fee = int(str(form.get("monthly_fee", "0")).replace(",", "") or 0)
        billing.set_plan(str(form.get("plan", "")), fee, u["username"])
    except ValueError as e:
        return HTMLResponse(page(u, "과금", _billing_page(u,
            f"<div class='card warn'>{html.escape(str(e))}</div>"), "/billing"), 400)
    return RedirectResponse("/billing", status_code=303)


@app.post("/billing/issue", response_class=HTMLResponse)
async def billing_issue(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    from . import billing
    billing.issue()
    return RedirectResponse("/billing", status_code=303)


@app.post("/billing/paid", response_class=HTMLResponse)
async def billing_paid(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    from . import billing
    form = await request.form()
    try:
        billing.mark_paid(int(str(form.get("invoice_id", "0"))), u["username"])
    except (ValueError, TypeError) as e:
        return HTMLResponse(page(u, "과금", _billing_page(u,
            f"<div class='card warn'>{html.escape(str(e))}</div>"), "/billing"), 400)
    return RedirectResponse("/billing", status_code=303)


@app.post("/billing/unlock", response_class=HTMLResponse)
async def billing_unlock(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    from . import billing
    billing.unlock(u["username"])
    return RedirectResponse("/billing", status_code=303)


@app.get("/users", response_class=HTMLResponse)
def users_page(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    ensure_users()
    return HTMLResponse(page(u, "계정 관리", _users_page(u), "/users"))


@app.post("/users/add", response_class=HTMLResponse)
async def users_add(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    form = await request.form()
    username = str(form.get("username", "")).strip().lower()
    role = str(form.get("role", "viewer"))
    display = str(form.get("display", "")).strip()
    import re as _re
    # P5-SEC4: 순수 숫자 아이디 금지(토큰 형식과의 교차 해석 여지 제거)
    if not _re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,30}", username) \
            or username.isdigit() or role not in ROLES or not display:
        return HTMLResponse(page(u, "계정 관리", _users_page(u,
            "<div class='card warn'>아이디(영소문자·숫자 2~31자)·역할·표시 이름을 확인하세요.</div>"),
            "/users"), 400)
    if db.one("SELECT 1 FROM axp_users WHERE username=?", (username,)):
        return HTMLResponse(page(u, "계정 관리", _users_page(u,
            f"<div class='card warn'>이미 있는 아이디입니다: {html.escape(username)}</div>"),
            "/users"), 400)
    pw = secrets.token_urlsafe(9)
    salt = secrets.token_hex(8)
    db.execute("INSERT INTO axp_users VALUES (?,?,?,?,?,1)",
               (username, _hash(pw, salt), salt, role, display))
    common.alert("info", "webapp", f"계정 생성: {username}({role}) by {u['username']}")
    return HTMLResponse(page(u, "계정 관리", _users_page(u,
        f"<div class='card ok'><b>계정 생성</b> — {html.escape(username)} / "
        f"임시 비밀번호 <code>{html.escape(pw)}</code> (지금만 표시 — 안전하게 전달하세요)</div>"),
        "/users"))


@app.post("/users/reset", response_class=HTMLResponse)
async def users_reset(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    form = await request.form()
    username = str(form.get("username", "")).strip()
    if not db.one("SELECT 1 FROM axp_users WHERE username=?", (username,)):
        return HTMLResponse(page(u, "계정 관리", _users_page(u,
            "<div class='card warn'>없는 계정입니다.</div>"), "/users"), 404)
    pw = secrets.token_urlsafe(9)
    salt = secrets.token_hex(8)
    db.execute("UPDATE axp_users SET pw_hash=?, salt=?, must_change=1 WHERE username=?",
               (_hash(pw, salt), salt, username))
    db.execute("DELETE FROM axp_login_attempts WHERE username=?", (username,))
    common.alert("info", "webapp", f"비밀번호 재발급: {username} by {u['username']}")
    return HTMLResponse(page(u, "계정 관리", _users_page(u,
        f"<div class='card ok'><b>재발급</b> — {html.escape(username)} / 임시 비밀번호 "
        f"<code>{html.escape(pw)}</code> (지금만 표시 · 첫 로그인에서 변경 강제)</div>"),
        "/users"))


@app.post("/users/unlock", response_class=HTMLResponse)
async def users_unlock(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    form = await request.form()
    username = str(form.get("username", "")).strip()
    db.execute("DELETE FROM axp_login_attempts WHERE username=?", (username,))
    common.alert("info", "webapp", f"잠금 해제: {username} by {u['username']}")
    return HTMLResponse(page(u, "계정 관리", _users_page(u,
        f"<div class='card ok'>잠금 해제 — {html.escape(username)}</div>"), "/users"))


# ── P4-9: 온보딩 위저드 1차 — 매장·품목·코드 사전을 화면에서 (W6) ────
def _setup_form(u, msg: str = "") -> str:
    from . import profile_rt
    prof = profile_rt.load()
    stores = "\n".join(
        f"{code}={name}" + (f"={prof.get('store_channels', {}).get(code, '')}"
                            if prof.get('store_channels', {}).get(code) else "")
        for code, name in prof.get("store_names", {}).items())
    prods = "\n".join(f"{c}={n}" for c, n in prof.get("product_names", {}).items())
    aliases = "\n".join(f"{d},{a},{c}" for d, a, c in prof.get("alias_seed", []))
    return f"""<h2>온보딩 설정 — 우리 회사 말로 바꿉니다</h2>
<p class="sub">여기서 정한 이름이 브리핑·승인함·질문 화면 전체에 쓰입니다.
코드 별칭은 엑셀·장표의 현장 표기를 표준 코드로 잇는 사전입니다(격리 큐가 그 관문).</p>{msg}
<form method="post" class="card" style="max-width:680px">
  <p><b>회사명</b><br><input name="company" value="{html.escape(prof.get('company', ''))}" style="width:100%"></p>
  <p><b>매장</b> — 한 줄에 하나: <code>코드=이름</code> 또는 <code>코드=이름=채널</code> (채널: retail/B2B)<br>
  <textarea name="stores" style="width:100%;height:110px;font-family:monospace">{html.escape(stores)}</textarea></p>
  <p><b>품목</b> — 한 줄에 하나: <code>코드=이름</code><br>
  <textarea name="products" style="width:100%;height:110px;font-family:monospace">{html.escape(prods)}</textarea></p>
  <p><b>코드 별칭 사전</b> — 한 줄에 하나: <code>영역,현장표기,표준코드</code> (영역: store/product/worker/equipment)<br>
  <textarea name="aliases" style="width:100%;height:90px;font-family:monospace">{html.escape(aliases)}</textarea></p>
  <button class="btn ok">저장</button>
  <span class="sub" style="margin-left:8px">저장 즉시 코드 사전에도 반영됩니다</span>
</form>"""


def _parse_kv_lines(text: str, what: str, errors: list[str],
                    max_parts: int = 2) -> dict:
    out: dict = {}
    for i, line in enumerate(str(text).splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("=")]
        if len(parts) < 2 or not parts[0] or not parts[1]:
            errors.append(f"{what} {i}행: '코드=이름' 형식이 아닙니다 — {line[:40]}")
            continue
        if parts[0] in out:
            errors.append(f"{what} {i}행: 코드 중복 — {parts[0]}")
            continue
        out[parts[0]] = parts[1:max_parts + 1] if max_parts > 1 else parts[1]
    return out


@app.get("/setup", response_class=HTMLResponse)
def setup_form(request: Request):
    u = _require(request, ("steward",))
    if isinstance(u, Response):
        return u
    return HTMLResponse(page(u, "온보딩 설정", _setup_form(u), "/setup"))


@app.post("/setup", response_class=HTMLResponse)
async def setup_save(request: Request):
    u = _require(request, ("steward",))
    if isinstance(u, Response):
        return u
    form = await request.form()
    errors: list[str] = []
    stores_raw = _parse_kv_lines(form.get("stores", ""), "매장", errors, max_parts=2)
    prods = {k: v[0] for k, v in
             _parse_kv_lines(form.get("products", ""), "품목", errors).items()}
    aliases: list[list[str]] = []
    for i, line in enumerate(str(form.get("aliases", "")).splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 3 or parts[0] not in ("store", "product", "worker", "equipment"):
            errors.append(f"별칭 {i}행: '영역,현장표기,표준코드' 형식이 아닙니다 — {line[:40]}")
            continue
        aliases.append(parts)
    company = str(form.get("company", "")).strip()
    if not company:
        errors.append("회사명이 비어 있습니다")
    if errors:
        msg = ("<div class='card warn'><b>저장하지 않았습니다</b> — 아래를 고쳐 주세요"
               + "".join(f"<div class='ln'>· {html.escape(e)}</div>" for e in errors)
               + "</div>")
        return HTMLResponse(page(u, "온보딩 설정", _setup_form(u, msg), "/setup"), 400)

    from . import profile_rt
    prof = profile_rt.load()
    prof["company"] = company
    prof["store_names"] = {k: v[0] for k, v in stores_raw.items()}
    prof["store_channels"] = {k: v[1] for k, v in stores_raw.items() if len(v) > 1 and v[1]}
    prof["product_names"] = prods
    prof["alias_seed"] = aliases
    (config.DATA / "profile.json").write_text(
        json.dumps(prof, ensure_ascii=False, indent=2), encoding="utf-8")
    from .dataset import codemap
    codemap.init()      # alias_seed가 코드 사전으로 들어간다
    common.alert("info", "setup", f"온보딩 설정 저장: {u['username']} — "
                 f"매장 {len(prof['store_names'])}·품목 {len(prods)}·별칭 {len(aliases)}")
    msg = (f"<div class='card ok'><b>저장 완료</b> — 매장 {len(prof['store_names'])}개 · "
           f"품목 {len(prods)}개 · 별칭 {len(aliases)}건이 코드 사전에 반영됐습니다.</div>")
    return HTMLResponse(page(u, "온보딩 설정", _setup_form(u, msg), "/setup"))


# ── P4-6: Odoo 연결 마법사 — 3단계 실증 절차(P3-2)의 제품화 1차 ──────
CDC_CANDIDATES = [
    "sale_order", "sale_order_line", "purchase_order", "purchase_order_line",
    "stock_move", "stock_quant", "stock_scrap", "mrp_production",
    "mrp_workorder", "quality_check", "quality_alert",
    "maintenance_request", "maintenance_equipment"]


def _connect_form(msg: str = "") -> str:
    return f"""<h2>Odoo 연결 마법사 — 붙기 전에 검사부터</h2>
<p class="sub">Odoo DB에 <b>읽기 전용</b>으로 접속해 버전·모듈·복제 설정을 검사하고,
귀사 구성에 맞는 발행(publication) SQL을 만들어 드립니다. 여기서 원장에 쓰기는 없습니다.
비밀번호는 저장하지 않습니다.</p>{msg}
<form method="post" class="card" style="max-width:560px">
  <p><input name="host" placeholder="Odoo DB 호스트 (예: 192.168.0.10)" style="width:100%" required></p>
  <p style="display:flex;gap:8px">
    <input name="port" placeholder="포트" value="5432" style="width:120px">
    <input name="dbname" placeholder="DB 이름 (예: odoo)" style="flex:1" required></p>
  <p style="display:flex;gap:8px">
    <input name="user" placeholder="계정 (읽기·REPLICATION 권장)" style="flex:1" required>
    <input name="password" type="password" placeholder="비밀번호" style="flex:1" required></p>
  <button class="btn ok">검사 실행</button>
</form>"""


@app.get("/connect", response_class=HTMLResponse)
def connect_form(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    return HTMLResponse(page(u, "Odoo 연결", _connect_form(), "/connect"))


@app.post("/connect", response_class=HTMLResponse)
async def connect_check(request: Request):
    u = _require(request, ("admin",))
    if isinstance(u, Response):
        return u
    form = await request.form()
    host = str(form.get("host", "")).strip()
    port = str(form.get("port", "5432")).strip() or "5432"
    dbname = str(form.get("dbname", "")).strip()
    user_ = str(form.get("user", "")).strip()
    pw = str(form.get("password", ""))
    try:
        import psycopg
        con = psycopg.connect(host=host, port=int(port), dbname=dbname,
                              user=user_, password=pw, connect_timeout=8)
    except Exception as e:  # noqa: BLE001
        return HTMLResponse(page(u, "Odoo 연결", _connect_form(
            f"<div class='card warn'>접속 실패 — {html.escape(str(e)[:250])}"
            "<div class='sub'>방화벽(5432)·pg_hba.conf·계정을 확인하세요. "
            "현장 체크리스트 B·C 참조.</div></div>"), "/connect"), 400)
    try:
        with con:
            cur = con.execute(
                "SELECT latest_version FROM ir_module_module WHERE name='base'")
            row = cur.fetchone()
            odoo_ver = row[0] if row else "?"
            n_mod = con.execute(
                "SELECT count(*) FROM ir_module_module WHERE state='installed'"
            ).fetchone()[0]
            wal = con.execute("SHOW wal_level").fetchone()[0]
            present, absent = [], []
            for t in CDC_CANDIDATES:
                (present if con.execute(
                    "SELECT to_regclass('public.' || %s)", (t,)
                ).fetchone()[0] else absent).append(t)
            has_pub = bool(con.execute(
                "SELECT 1 FROM pg_publication WHERE pubname='axp_pub'").fetchone())
            can_repl = con.execute(
                "SELECT rolreplication OR rolsuper FROM pg_roles WHERE rolname=%s",
                (user_,)).fetchone()
            can_repl = bool(can_repl and can_repl[0])
    except Exception as e:  # noqa: BLE001
        return HTMLResponse(page(u, "Odoo 연결", _connect_form(
            f"<div class='card warn'>검사 중 오류 — {html.escape(str(e)[:250])}"
            "<div class='sub'>Odoo DB가 맞는지 확인하세요(ir_module_module 필요).</div></div>"),
            "/connect"), 400)
    finally:
        con.close()

    pub_sql = ("-- axp_pub — 이 Odoo 인스턴스 실검사 결과 기반 (생성: " + common.now_iso() + ")\n"
               "CREATE PUBLICATION axp_pub FOR TABLE\n  "
               + ",\n  ".join(present) + ";")
    ok = lambda b: ("<span style='color:#0E8F86'>✔</span>" if b
                    else "<span style='color:#A8493B'>✘</span>")
    checks = f"""
<div class="card"><b>검사 결과 — {html.escape(host)}/{html.escape(dbname)}</b>
  <div class="ln">{ok(True)} Odoo 버전: <b>{html.escape(str(odoo_ver))}</b> · 설치 모듈 {n_mod}개</div>
  <div class="ln">{ok(wal == 'logical')} wal_level = {html.escape(wal)}
    {'— 논리 복제 가능' if wal == 'logical' else " — <b>postgresql.conf에서 wal_level=logical 로 바꾸고 재시작해야 합니다</b>"}</div>
  <div class="ln">{ok(can_repl)} 계정 REPLICATION 권한 {'있음' if can_repl else '없음 — 구독 생성에 필요(읽기 검사에는 무관)'}</div>
  <div class="ln">{ok(True)} CDC 대상 테이블: <b>{len(present)}개 발행 가능</b>
    {('· 부재 ' + str(len(absent)) + '개(모듈 미설치 — 자동 제외): ' + ', '.join(absent)) if absent else ''}</div>
  <div class="ln">{ok(not has_pub)} 발행 axp_pub {'이미 존재 — 재생성 전 DROP PUBLICATION 필요' if has_pub else '미존재 — 아래 SQL로 생성'}</div>
</div>
<div class="card"><b>이 인스턴스용 발행 SQL</b> — Odoo DB에서 관리자(DBA)가 실행하세요
  <textarea readonly style="width:100%;height:160px;font-family:monospace;font-size:13px;margin-top:8px">{html.escape(pub_sql)}</textarea>
  <div class="sub">다음 단계: 플랫폼 서버에서 구독 생성(odoo_cdc_prod.sql 2절) →
  매핑 뷰 적용(odoo17_prod_mapping.sql) → 정합 대조. 절차는 현장 체크리스트 C를 따릅니다.</div>
</div>"""
    return HTMLResponse(page(u, "Odoo 연결", _connect_form() + checks, "/connect"))


# ── P4-4: 공개 상태 — 하트비트·status 페이지 (인증 없음, 최소 정보) ──
@app.get("/health")
def health():
    """하트비트 표적 — DB까지 왕복해야 ok. 민감 정보 없음."""
    try:
        db.scalar("SELECT 1")
        return {"ok": True, "ts": common.now_iso()}
    except Exception:  # noqa: BLE001
        return Response(json.dumps({"ok": False}), status_code=503,
                        media_type="application/json")


@app.get("/status", response_class=HTMLResponse)
def status_page():
    """공개 상태 페이지 — 가용성 신호만 보여준다(수치·데이터 노출 없음)."""
    try:
        db.scalar("SELECT 1")
        db_ok = True
    except Exception:  # noqa: BLE001
        db_ok = False
    crit_24h = 0
    recon_ok = None   # P5-R2: 최근 정합 배치 신호(불리언만 — 수치 비노출 원칙 유지)
    if db_ok:
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
            crit_24h = db.scalar(
                "SELECT COUNT(*) FROM alerts WHERE level='crit' AND created_at>?",
                (cutoff,)) or 0
        except Exception:  # noqa: BLE001
            pass
        try:
            row = db.one("SELECT ok FROM recon_log ORDER BY run_at DESC LIMIT 1")
            recon_ok = bool(row["ok"]) if row else None
        except Exception:  # noqa: BLE001
            pass
    dot = lambda ok: ("<span style='color:#0E8F86'>●</span>" if ok
                      else "<span style='color:#A8493B'>●</span>")
    body = f"""<h2>서비스 상태</h2>
<div class="card">
  <div class="ln">{dot(True)} 웹 애플리케이션 — 정상</div>
  <div class="ln">{dot(db_ok)} 데이터베이스 — {'정상' if db_ok else '점검 중'}</div>
  <div class="ln">{dot(crit_24h == 0)} 야간 파이프라인 — {'최근 24시간 심각 경보 없음' if crit_24h == 0 else f'점검 중(심각 경보 {crit_24h}건)'}</div>
  <div class="ln">{dot(recon_ok is not False)} 데이터 정합 — {'최근 정합 배치 통과' if recon_ok else ('점검 중' if recon_ok is False else '정합 배치 대기')}</div>
  <div class="sub" style="margin-top:8px">기준 시각: {common.now_iso()} (UTC)</div>
</div>"""
    return HTMLResponse(page(None, "서비스 상태", body),
                        200 if db_ok else 503)


# ── P4-3: 자료 반입 — 엑셀·POS 파일을 화면에서 올린다 ─────────
UPLOAD_KINDS = {
    "excel": ("엑셀 (판매집계·행사달력·단가표)", None),
    "pos_daily": ("POS 일별 정산 집계", "daily"),
    "pos_receipt": ("POS 영수증 거래 로그", "receipt"),
}
MAX_UPLOAD_MB = int(os.environ.get("AXP_MAX_UPLOAD_MB", "20"))


def _pipeline_strip() -> str:
    """P8-3: 반입 파이프라인 한 줄 — 지금 어디까지 왔는지 보여준다."""
    quar = (db.scalar("SELECT COUNT(*) FROM quarantine_queue WHERE status='pending'") or 0) \
        if db.table_exists("quarantine_queue") else 0
    last = db.one("SELECT run_date, status FROM batch_runs ORDER BY run_id DESC LIMIT 1") \
        if db.table_exists("batch_runs") else None
    last_txt = f"마지막 반영 {last['run_date']} ({last['status']})" if last else "아직 반영 전"
    q_txt = (f"<a href='/quarantine'><b style='color:#A8493B'>확인할 이름 {quar}건</b></a>"
             if quar else "확인할 이름 없음 ✓")
    return (f"<div class='card' style='padding:8px 14px'><span class='sub'>"
            f"<b>① 업로드</b>(이 화면) → <b>② 열 매핑</b>(모르는 양식이면 화면에서 지정) → "
            f"<b>③ {q_txt}</b> → <b>④ <a href='/runs'>지금 반영</a></b> · {last_txt}"
            f"</span></div>")


def _upload_form(msg: str = "") -> str:
    opts = "".join(f"<option value='{k}'>{v[0]}</option>" for k, v in UPLOAD_KINDS.items())
    return f"""<h2>자료 반입 — 가져와서 정리합니다</h2>
<p class="sub">개인정보 컬럼(연락처·주소 등)은 반입 시점에 자동 차단되고, 원본은 불변 보존됩니다.
같은 파일을 두 번 올려도 중복 반입되지 않습니다.</p>{_pipeline_strip()}{msg}
<form method="post" enctype="multipart/form-data" class="card" style="max-width:560px">
  <p><select name="kind" style="width:100%">{opts}</select></p>
  <p><input type="file" name="file" required accept=".csv,.xlsx,.xls" style="width:100%"></p>
  <button class="btn ok">반입</button>
  <span class="sub" style="margin-left:8px">CSV(cp949 포함)·엑셀 · 최대 {MAX_UPLOAD_MB}MB</span>
</form>"""


# P7-12(서버1 실사용 적발): '처음 보는 양식'에서 열 매핑 등록이 웹에 없어
# 관리자 명령이 필요했다 — 화면에서 클릭으로 등록하고 즉시 재반입한다.
_MAP_FIELD_LABELS = {
    "": "(무시)", "date": "판매일(날짜)", "store_id": "매장", "product_id": "품목",
    "qty": "수량", "date_start": "시작일", "date_end": "종료일",
    "promo_name": "행사명", "discount_pct": "할인율",
    "vendor_id": "공급사", "material_id": "자재", "unit_price": "단가",
    "valid_from": "적용 시작일",
}
_MAP_GUESS = (("판매일", "date"), ("일자", "date"), ("날짜", "date"),
              ("매장", "store_id"), ("지점", "store_id"),
              ("품목", "product_id"), ("제품", "product_id"), ("상품", "product_id"),
              ("수량", "qty"), ("시작", "date_start"), ("종료", "date_end"),
              ("행사", "promo_name"), ("할인", "discount_pct"),
              ("공급", "vendor_id"), ("자재", "material_id"), ("단가", "unit_price"))


def _excel_mapping_form(res: dict, src: str) -> str:
    from .ingest.excel_uploader import STANDARD_FIELDS
    prof = res.get("profile") or {}
    kind_opts = "".join(
        f"<option value='{k}'>{lbl}</option>" for k, lbl in
        (("sales_summary", "판매 집계"), ("promo_calendar", "프로모션 달력"),
         ("vendor_price", "단가표")) if k in STANDARD_FIELDS)
    rows = []
    for c in prof.get("columns", []):
        name = c["name"]
        guess = next((f for kw, f in _MAP_GUESS if kw in name), "")
        opts = "".join(
            f"<option value='{f}'{' selected' if f == guess else ''}>{lbl}</option>"
            for f, lbl in _MAP_FIELD_LABELS.items())
        sample = " · ".join(c.get("sample", [])[:2])
        rows.append(
            f"<tr><td><b>{html.escape(name)}</b><div class='sub'>{html.escape(sample)}</div></td>"
            f"<td><select name='map__{html.escape(name)}'>{opts}</select></td></tr>")
    return f"""<div class="card warn"><b>처음 보는 양식</b> — 아래에서 각 열이 무엇인지 지정하면
등록되고, 이 파일이 바로 반입됩니다(다음부터는 자동).
<form method="post" action="/upload/mapping" style="margin-top:8px">
  <input type="hidden" name="fingerprint" value="{html.escape(prof.get('fingerprint', ''))}">
  <input type="hidden" name="src" value="{html.escape(src)}">
  <p>양식 종류: <select name="sheet_kind">{kind_opts}</select></p>
  <table style="width:100%">{''.join(rows)}</table>
  <button class="btn ok" style="margin-top:8px">등록하고 바로 반입</button>
</form></div>"""


@app.post("/upload/mapping", response_class=HTMLResponse)
async def upload_mapping(request: Request):
    u = _require(request, ("steward",))
    if isinstance(u, Response):
        return u
    form = await request.form()
    from pathlib import Path as _P
    from .ingest import excel_uploader as xu
    fp = str(form.get("fingerprint", ""))
    sheet_kind = str(form.get("sheet_kind", ""))
    src = _P(str(form.get("src", "")))
    mapping = {k[len("map__"):]: str(v) for k, v in form.items()
               if k.startswith("map__") and str(v)}
    inbox_dir = (config.DATA / "raw" / "webupload").resolve()
    ok_src = src.is_file() and str(src.resolve()).startswith(str(inbox_dir) + os.sep)
    if not (fp and sheet_kind in xu.STANDARD_FIELDS and ok_src):
        return HTMLResponse(page(u, "자료 반입", _upload_form(
            "<div class='card warn'>매핑 등록 정보가 올바르지 않습니다 — 파일을 다시 업로드하세요.</div>"),
            "/upload"), 400)
    try:
        xu.save_mapping(fp, sheet_kind, mapping, by=u["username"])
    except ValueError as e:
        return HTMLResponse(page(u, "자료 반입", _upload_form(
            f"<div class='card warn'>{html.escape(str(e))} — 필수 열을 지정해 주세요.</div>"),
            "/upload"), 400)
    common.alert("info", "webapp",
                 f"열 매핑 등록: {sheet_kind} {fp} by {u['username']}")
    res = xu.upload(src, by=u["username"])
    errs = "".join(f"<div class='ln'>· {html.escape(e)}</div>" for e in res.get("errors", [])[:10])
    body = (f"<div class='card ok'><b>매핑 등록·반입 완료</b> — {res.get('rows_ok', 0)}행"
            f" (거절 {res.get('rows_rejected', 0)}행)"
            + (f"<div style='margin-top:6px'>{errs}</div>" if errs else "")
            + "<div class='sub' style='margin-top:6px'>같은 양식은 다음부터 자동 반입됩니다. "
              "미확인 코드는 <a href='/quarantine'>격리 큐</a>에서, 반영은 "
              "<a href='/runs'>배치 실행</a>에서.</div></div>")
    return HTMLResponse(page(u, "자료 반입", _upload_form() + body, "/upload"))


@app.get("/upload", response_class=HTMLResponse)
def upload_form(request: Request):
    u = _require(request, ("steward",))
    if isinstance(u, Response):
        return u
    return HTMLResponse(page(u, "자료 반입", _upload_form(), "/upload"))


@app.post("/upload", response_class=HTMLResponse)
async def upload_post(request: Request):
    u = _require(request, ("steward",))
    if isinstance(u, Response):
        return u
    form = await request.form()
    kind = str(form.get("kind", ""))
    f = form.get("file")
    if kind not in UPLOAD_KINDS or f is None or not getattr(f, "filename", ""):
        return HTMLResponse(page(u, "자료 반입", _upload_form(
            "<div class='card warn'>파일과 유형을 선택하세요.</div>"), "/upload"), 400)
    data = await f.read()
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        return HTMLResponse(page(u, "자료 반입", _upload_form(
            f"<div class='card warn'>파일이 너무 큽니다(최대 {MAX_UPLOAD_MB}MB).</div>"), "/upload"), 413)
    # P6-4: 테넌트 저장 총량 상한 — 파일 1건 크기와 별개로 raw 수신함
    # 누적이 쿼터를 넘으면 반입 거부(체험 남용·디스크 고갈 방지).
    # 체험 테넌트는 24시간 파기(purge-uploads)가 있어 정상 사용은 안 걸린다.
    quota = int(os.environ.get("AXP_TENANT_QUOTA_MB", "500"))
    raw_dir = config.DATA / "raw"
    used = sum(p.stat().st_size for p in raw_dir.rglob("*") if p.is_file()) \
        if raw_dir.exists() else 0
    if used + len(data) > quota * 1024 * 1024:
        common.alert("warn", "webapp",
                     f"업로드 쿼터 초과 거부: 사용 {used // (1024*1024)}MB / 상한 {quota}MB (by {u['username']})")
        return HTMLResponse(page(u, "자료 반입", _upload_form(
            f"<div class='card warn'>저장 공간 상한({quota}MB)에 도달했습니다 — "
            f"오래된 업로드가 파기된 뒤 다시 시도하거나 관리자에게 문의하세요.</div>"), "/upload"), 413)
    # 안전한 파일명으로 수신함에 저장 후 어댑터 호출(원본 보존은 어댑터가 수행)
    import re as _re
    from pathlib import Path as _P
    safe = _re.sub(r"[^\w.\-가-힣]", "_", f.filename)[-80:] or "upload.bin"
    inbox_dir = config.DATA / "raw" / "webupload"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    dst = inbox_dir / f"{common.now_iso().replace(':', '')}_{safe}"
    dst.write_bytes(data)
    try:
        if kind == "excel":
            from .ingest import excel_uploader
            res = excel_uploader.upload(dst, by=u["username"])
        else:
            from .ingest import pos
            fn = pos.ingest_daily if UPLOAD_KINDS[kind][1] == "daily" else pos.ingest_receipt
            res = fn(dst, by=u["username"])
    except Exception as e:  # noqa: BLE001
        return HTMLResponse(page(u, "자료 반입", _upload_form(
            f"<div class='card warn'>반입 실패: {html.escape(str(e)[:300])}</div>"), "/upload"), 500)
    if res.get("status") == "needs_mapping":
        if kind == "excel" and res.get("profile"):
            body = _excel_mapping_form(res, str(dst))     # P7-12: 화면에서 바로 등록
        else:
            cols = ", ".join(res.get("columns", [])[:20]) or \
                ", ".join(c["name"] for c in res.get("profile", {}).get("columns", [])[:20])
            body = (f"<div class='card warn'><b>처음 보는 양식</b> — {html.escape(res.get('message',''))}"
                    f"<div class='sub'>발견한 열: {html.escape(cols)}</div>"
                    f"<div class='sub'>열 매핑 등록은 관리자에게 요청하세요(다음부터 자동 반입).</div></div>")
    elif res.get("status") == "duplicate":
        body = f"<div class='card warn'>{html.escape(res.get('message',''))}</div>"
    else:
        errs = "".join(f"<div class='ln'>· {html.escape(e)}</div>" for e in res.get("errors", [])[:10])
        warns = "".join(f"<div class='ln'>⚠ {html.escape(w)}</div>"
                        for w in res.get("double_count_warnings", [])[:5])
        # P4-11: 반입 직후 미리보기 — 무엇이 들어왔는지 바로 보여준다
        preview = ""
        if kind != "excel" and res.get("rows_ok"):
            try:
                pv = db.one(
                    "SELECT MIN(order_date) AS d0, MAX(order_date) AS d1, "
                    "COUNT(DISTINCT store_id) AS stores, "
                    "COUNT(DISTINCT product_id) AS prods, "
                    "COALESCE(SUM(qty),0) AS qty "
                    "FROM staging_sales WHERE _source LIKE 'pos%'")
                if pv and pv["d0"]:
                    preview = (f"<div style='margin-top:6px' class='sub'>반입 미리보기 — "
                               f"기간 {html.escape(str(pv['d0']))}~{html.escape(str(pv['d1']))} · "
                               f"매장 {pv['stores']}곳 · 상품 {pv['prods']}종 · "
                               f"수량 합계 {pv['qty']:,.0f}</div>")
            except Exception:  # noqa: BLE001 — 미리보기는 반입 성공을 가리지 않는다
                pass
        body = (f"<div class='card ok'><b>반입 완료</b> — {res.get('rows_ok', 0)}행"
                f" (거절 {res.get('rows_rejected', 0)}행)" + preview
                + (f"<div style='margin-top:6px'>{errs}</div>" if errs else "")
                + (f"<div style='margin-top:6px'>{warns}</div>" if warns else "")
                + "<div class='sub' style='margin-top:6px'>미확인 코드는 <a href='/quarantine'>격리 큐</a>에서 확정하세요. "
                  "브리핑 반영은 다음 야간 배치(또는 관리자 수동 실행) 후입니다.</div></div>")
    return HTMLResponse(page(u, "자료 반입", _upload_form() + body, "/upload"))


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
{f'''<div class="card"><b>일괄 처리 (P5-U2)</b>
<form method="post" action="/quarantine/bulk" style="margin-top:8px">
  <textarea name="lines" placeholder="한 줄에 하나: 번호=표준코드   예) 12=P-COOKIE" style="width:100%;height:70px;font-family:monospace"></textarea>
  <button class="btn ok" style="margin-top:6px">일괄 확정</button>
</form>
<form method="post" action="/quarantine/drain" style="margin-top:6px">
  <button class="btn plain">표준 코드와 똑같은 별칭 자동 확정</button>
  <span class="sub">별칭이 이미 표준 코드와 완전 일치하는 건만 (예: 별칭 P-PIE → P-PIE)</span>
</form></div>''' if can else ''}
<h2 style="font-size:17px">최근 확정 — 잘못 확정했다면 취소하세요</h2>
<p class="sub">취소하면 다음 야간 배치의 전량 재구축이 소급 반영합니다</p>
<table><tr><th>#</th><th>별칭</th><th>확정 코드</th><th>확정자</th><th>취소</th></tr>{undo or '<tr><td colspan=5>기록 없음</td></tr>'}</table>"""
    return HTMLResponse(page(u, "격리 큐", body, "/quarantine"))


@app.post("/quarantine/bulk")
async def quarantine_bulk(request: Request):
    """P5-U2: 일괄 확정 — '번호=코드' 줄 단위, 틀린 줄은 한글 사유와 함께 건너뜀."""
    u = _require(request, roles=("steward",))
    if isinstance(u, Response):
        return u
    form = await request.form()
    done, errors = 0, []
    for i, line in enumerate(str(form.get("lines", "")).splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.replace("=", " ").split()]
        if len(parts) != 2 or not parts[0].isdigit() or not parts[1]:
            errors.append(f"{i}행: '번호=코드' 형식이 아닙니다 — {line[:30]}")
            continue
        try:
            codemap.confirm(int(parts[0]), parts[1], by=u["display"])
            done += 1
        except Exception as e:  # noqa: BLE001
            errors.append(f"{i}행(#{parts[0]}): {str(e)[:60]}")
    note = (f"<div class='card ok'>일괄 확정 {done}건"
            + ("".join(f"<div class='ln'>· {html.escape(e)}</div>" for e in errors[:10]) if errors else "")
            + "</div>")
    common.alert("info", "quarantine", f"일괄 확정 {done}건·거절 {len(errors)}건 by {u['username']}")
    resp = quarantine_page(request)
    return HTMLResponse(resp.body.decode().replace("<h2>격리 큐</h2>", f"<h2>격리 큐</h2>{note}", 1))


@app.post("/quarantine/drain")
def quarantine_drain(request: Request):
    """자기 일치 자동 확정 — 별칭이 표준 코드와 완전 일치하는 대기 건."""
    u = _require(request, roles=("steward",))
    if isinstance(u, Response):
        return u
    n = codemap.drain_self_matches(by=f"자동(표준 일치, {u['display']})")
    common.alert("info", "quarantine", f"자기 일치 자동 확정 {n}건 by {u['username']}")
    return RedirectResponse("/quarantine", status_code=303)


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
            # P7-5: 질문 활용 KPI의 원천 — 누가 언제 물었는지만(답변은 미보존)
            db.executescript(
                "CREATE TABLE IF NOT EXISTS question_log ("
                "q_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "username TEXT, question TEXT, at TEXT)")
            db.execute("INSERT INTO question_log (username, question, at) VALUES (?,?,?)",
                       (u["username"], q[:200], common.now_iso()))
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
def audit_page(request: Request, card: str = "", action: str = "", days: str = ""):
    """P5-U1: 검색·필터 — '왜 이 발주가 나갔나'를 카드 번호로 바로 찾는다."""
    u = _require(request)
    if isinstance(u, Response):
        return u
    inbox_ = inbox
    db.executescript(inbox_.DDL)
    sql = "SELECT * FROM audit_log WHERE 1=1"
    params: list = []
    card_n = int(card) if card.strip().lstrip("#").isdigit() else None
    if card.strip() and card_n is not None:
        sql += " AND card_id=?"
        params.append(int(card.strip().lstrip("#")))
    if action:
        sql += " AND action=?"
        params.append(action)
    if days.strip().isdigit():
        cutoff = (datetime.now(timezone.utc) - timedelta(days=int(days))).isoformat()
        sql += " AND at>=?"
        params.append(cutoff)
    rows = db.query(sql + " ORDER BY log_id DESC LIMIT 200", tuple(params))
    actions = [r["action"] for r in db.query(
        "SELECT DISTINCT action FROM audit_log ORDER BY action")]
    opts = "<option value=''>전체 행위</option>" + "".join(
        f"<option value='{html.escape(a)}' {'selected' if a == action else ''}>{html.escape(a)}</option>"
        for a in actions)
    body = "".join(
        f"<tr><td>{html.escape(str(r.get('at',''))[:16])}</td><td>{html.escape(r.get('action',''))}</td>"
        f"<td>{html.escape(r.get('actor',''))}</td>"
        f"<td><a href='/audit?card={r.get('card_id')}'>#{r.get('card_id')}</a></td>"
        f"<td>{html.escape((r.get('note') or '')[:80])}</td></tr>" for r in rows)
    filt = f"""<form method="get" class="card" style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
  <input name="card" value="{html.escape(card)}" placeholder="카드 번호" style="width:110px">
  <select name="action">{opts}</select>
  <select name="days">
    <option value=''>전체 기간</option>
    <option value='7' {'selected' if days == '7' else ''}>최근 7일</option>
    <option value='30' {'selected' if days == '30' else ''}>최근 30일</option>
  </select>
  <button class="btn plain">검색</button>
  <span class="sub">{len(rows)}건 (최대 200)</span>
</form>"""
    return HTMLResponse(page(u, "감사 로그",
        f"<h2>감사 로그</h2><p class='sub'>누가 · 언제 · 무엇을 — 수정 불가 기록</p>{filt}"
        f"<table><tr><th>시각</th><th>행위</th><th>담당</th><th>카드</th><th>비고</th></tr>{body}</table>",
        "/audit"))
