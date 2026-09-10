"""플랫폼 API — 근거(M5-3)·카드(M6)·승인함(M7)·War Room 을 한 서비스로.

기동: uvicorn axp.api:app --host 0.0.0.0 --port 8000
prod에서는 Keycloak 미들웨어가 역할 헤더를 채운다(demo: X-Role 헤더).
"""
from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse

from .agents import inbox, warroom
from .graph import evidence
from .judge import cards as jcards

app = FastAPI(title="AX Platform", version="0.1.0")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/cards")
def list_cards(status: str | None = None):
    return jcards.listing(status=status)


@app.get("/cards/{card_id}")
def get_card(card_id: int):
    try:
        return jcards.get(card_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@app.get("/cards/{card_id}/why")
def why(card_id: int):
    """'왜?' 버튼 — 근거 경로 전개 (M5-3)."""
    card = jcards.get(card_id)
    res = evidence.why(card["evidence"])
    if "path" in res:
        res["text"] = evidence.render_path_text(res)
    return res


@app.post("/cards/{card_id}/decide")
def decide(card_id: int, approve: bool, actor: str,
           reason_code: str = "", reason_text: str = "",
           x_role: str = Header(default="viewer")):
    try:
        return inbox.decide(card_id, actor, x_role, approve, reason_code, reason_text)
    except inbox.PermissionError_ as e:
        raise HTTPException(403, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/audit/{card_id}")
def audit(card_id: int):
    return inbox.audit(card_id)


@app.get("/warroom", response_class=HTMLResponse)
def war_room(as_of: str):
    from pathlib import Path
    return Path(warroom.render(as_of)).read_text(encoding="utf-8")


@app.get("/rules", response_class=PlainTextResponse)
def rules():
    from .judge import assembler
    return assembler.answer("규칙", assembler.search_rules())


# ── 반출 게이트 (M0-3) — n8n 워크플로가 호출하는 원장 API ─────────────
@app.post("/export/request")
def export_request(what: str, dest: str, why: str, requester: str, payload: str):
    from .custody import export_gate
    return {"req_id": export_gate.request(what, dest, why, requester, payload),
            "what": what, "dest": dest}


@app.post("/export/decide")
def export_decide(req_id: int, approver: str, approve: bool):
    from .custody import export_gate
    return export_gate.decide(req_id, approver, approve)


@app.post("/export/execute")
def export_execute(req_id: int, payload: str, dest: str):
    from .custody import export_gate
    try:
        return export_gate.check_and_mark_executed(req_id, payload, dest)
    except export_gate.ExportDenied as e:
        raise HTTPException(403, str(e))


@app.get("/export/audit")
def export_audit():
    from .custody import export_gate
    return export_gate.audit_log()
