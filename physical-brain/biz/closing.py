"""일일결산 (G09) — Odoo 매출·지출을 그래프로 비추고, 매일 손익을 닫는다.

동기화(읽기, 자동): account.move(전기된 고객송장=매출, 공급업체청구서=지출)
→ BizDoc 노드 + Partner 노드(거래처) + WITH 엣지. 원본은 Odoo, 그래프는 거울.

결산: 그래프에서 날짜·월 단위 매출/지출/손익 집계 → '일일결산' 이벤트 + 알림.
심장박동이 매일 저녁(21시 이후) 자동으로 닫는다 — Control 없는 기능은 미완성.
"""
from datetime import datetime

from graph_core import store

import biz  # noqa: F401 — Frame 등록 보장
from biz import odoo_client

MOVE_KIND = {"out_invoice": "매출", "out_refund": "매출취소",
             "in_invoice": "지출", "in_refund": "지출취소"}
SIGN = {"매출": 1, "매출취소": -1, "지출": 1, "지출취소": -1}


def sync_from_odoo(client=None, days: int = 120, now: datetime | None = None) -> dict:
    """Odoo → 그래프 동기화 (멱등). 반환: {docs, partners}."""
    now = now or datetime.now()
    client = client or odoo_client.get_client()
    since = datetime.fromordinal(now.toordinal() - days).date().isoformat()
    moves = client.search_read(
        "account.move",
        [["move_type", "in", list(MOVE_KIND)], ["state", "=", "posted"],
         ["invoice_date", ">=", since]],
        ["name", "move_type", "amount_total", "invoice_date", "partner_id", "payment_state"])
    partners, docs = set(), 0
    for m in moves:
        pid_raw, pname = (m.get("partner_id") or [0, "미지정"])[:2]
        pid = f"partner:{pid_raw}"
        if pid not in partners:
            store.upsert_node(pid, "Partner", {"name": pname, "source": "odoo"})
            partners.add(pid)
        kind = MOVE_KIND[m["move_type"]]
        did = f"bizdoc:{m['id']}" if m.get("id") else f"bizdoc:{m['name']}"
        store.upsert_node(did, "BizDoc", {
            "name": m["name"], "kind": kind, "amount": float(m["amount_total"]),
            "date": m.get("invoice_date") or "", "paid": m.get("payment_state", ""),
            "source": "odoo"})
        store.upsert_edge(did, "WITH", pid)
        docs += 1
    return {"docs": docs, "partners": len(partners)}


def _sum(docs: list[dict], group: str) -> float:
    total = 0.0
    for d in docs:
        k = d["props"].get("kind", "")
        if k.startswith(group):
            total += SIGN[k] * float(d["props"].get("amount", 0))
    return total


def close_day(date: str) -> dict:
    """하루 결산 — {date, sales, expense, profit, docs}."""
    docs = [d for d in store.nodes_by_type("BizDoc") if d["props"].get("date") == date]
    sales, expense = _sum(docs, "매출"), _sum(docs, "지출")
    return {"date": date, "sales": sales, "expense": expense,
            "profit": sales - expense,
            "docs": sorted((d["props"] for d in docs), key=lambda p: p.get("name", ""))}


def close_month(month: str) -> dict:
    """월 결산 — 월말 교보문고 정산이 들어오는 단위."""
    docs = [d for d in store.nodes_by_type("BizDoc")
            if d["props"].get("date", "").startswith(month)]
    sales, expense = _sum(docs, "매출"), _sum(docs, "지출")
    by_partner: dict[str, float] = {}
    for d in docs:
        for _r, pt in store.neighbors(d["id"], "WITH"):
            k = d["props"].get("kind", "")
            name = pt["props"].get("name", "?")
            by_partner[name] = by_partner.get(name, 0) + SIGN.get(k, 0) * (
                float(d["props"].get("amount", 0)) if k.startswith("매출")
                else -float(d["props"].get("amount", 0)))
    return {"month": month, "sales": sales, "expense": expense,
            "profit": sales - expense, "n_docs": len(docs), "by_partner": by_partner}


def _closed_today(date: str) -> bool:
    return any(e["props"].get("kind") == "일일결산" and date in e["props"].get("payload", "")
               for e in store.nodes_by_type("Event"))


def auto_close_if_due(now: datetime | None = None) -> dict | None:
    """심장박동용 — 매일 21시 이후 1회: 동기화(가능하면)→오늘 결산→기록·알림.
    Odoo 미설정이면 조용히 None (기능은 잠들어 있을 뿐 고장이 아니다)."""
    now = now or datetime.now()
    if not odoo_client.configured() and odoo_client._OVERRIDE is None:
        return None
    if now.hour < 21:
        return None
    today = now.date().isoformat()
    if _closed_today(today):
        return None
    try:
        sync_from_odoo(now=now)
    except Exception as e:
        print(f"[일일결산] 동기화 실패(결산은 기존 거울로 진행): {e}", flush=True)
    r = close_day(today)
    from server import notify
    from server.events import record_event
    record_event("나", "일일결산",
                 f"{today} 매출 {r['sales']:,.0f} 지출 {r['expense']:,.0f} 손익 {r['profit']:,.0f}", now)
    notify.send("나", f"📒 {today} 일일결산 — 매출 {r['sales']:,.0f}원 · "
                      f"지출 {r['expense']:,.0f}원 · 손익 {r['profit']:,.0f}원", "biz", now)
    return r
