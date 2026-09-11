"""P2-C2: Odoo 쓰기 커넥터 — 승인된 카드를 구매발주 '초안'으로.

환류의 마지막 구간: 지금까지는 승인된 파라미터를 사람이 보고 Odoo에
입력해야 했다. 이 커넥터는 승인(executed)된 수요예측·재고 정책 카드를
Odoo 구매발주 초안(state='draft')으로 만들어 준다 — **발주 확정은
언제나 사람이 Odoo 화면에서** 한다. 초안 생성조차 감사 로그에 남는다.

demo: 합성 Odoo(sqlite)의 purchase_order/_line에 직접 초안 생성.
prod: Odoo 표준 XML-RPC(ORM 경유)만 사용 — SQL 직접 삽입은 ORM 검증을
  우회하므로 금지. 접속: ODOO_URL / ODOO_DB / ODOO_USER / ODOO_API_KEY.

멱등성: 같은 카드로 초안을 두 번 만들지 않는다(odoo_writeback_log).
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone

from .. import common, config, db
from . import odoo_cdc

DDL = """
CREATE TABLE IF NOT EXISTS odoo_writeback_log (
  wb_id INTEGER PRIMARY KEY AUTOINCREMENT,
  card_id INTEGER NOT NULL UNIQUE,
  target TEXT NOT NULL,            -- 'purchase_order'
  odoo_ref TEXT NOT NULL,          -- 생성된 초안 이름 (PO/AXP/...)
  payload TEXT NOT NULL,
  created_at TEXT NOT NULL
);
"""

ELIGIBLE_KINDS = ("demand_forecast", "replenish")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _eligible_cards() -> list[dict]:
    from ..judge import cards as _jc
    db.executescript(_jc.DDL)
    db.executescript(DDL)
    return db.query(
        "SELECT c.* FROM judgment_cards c "
        "LEFT JOIN odoo_writeback_log w ON w.card_id = c.card_id "
        f"WHERE c.status='executed' AND c.kind IN {ELIGIBLE_KINDS!r} "
        "AND w.card_id IS NULL ORDER BY c.card_id")


def _card_po_payload(card: dict) -> dict | None:
    """카드 → 발주 초안 페이로드. 수량은 승인된 P50(기준수량)."""
    try:
        rng = json.loads(card.get("range_json") or "{}")
        vals = json.loads(card.get("values_json") or "[]")
    except Exception:
        return None
    qty = rng.get("p50")
    if qty is None and vals:
        qty = vals[0].get("value")
    if not qty:
        return None
    # proposal 예: "파이만쥬(P-PIE) S-CHORYANG — ... 기준수량을 2015개로 제안"
    prod = None
    for token in str(card.get("proposal", "")).split():
        if token.startswith("(P-") and token.endswith(")"):
            prod = token.strip("()")
    if prod is None:
        import re
        m = re.search(r"\b(P-[A-Z]+)\b", str(card.get("proposal", "")))
        prod = m.group(1) if m else "P-UNKNOWN"
    return {"product_id": prod, "qty": float(qty),
            "origin": f"AXP card #{card['card_id']}",
            "note": card.get("proposal", "")[:200]}


def _demo_create_po(payload: dict) -> str:
    """demo: 합성 Odoo sqlite에 초안 발주 생성 (초안 테이블은 없으면 생성)."""
    con = sqlite3.connect(odoo_cdc.source_path())
    try:
        con.execute(
            "CREATE TABLE IF NOT EXISTS purchase_order ("
            "id INTEGER PRIMARY KEY, name TEXT, partner_id INTEGER, "
            "date_order TEXT, state TEXT, origin TEXT)")
        con.execute(
            "CREATE TABLE IF NOT EXISTS purchase_order_line ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, po_ref TEXT, order_date TEXT, "
            "receipt_date TEXT, vendor_id TEXT, material_id TEXT, qty REAL, "
            "unit_price REAL, lot_id TEXT, write_date TEXT)")
        po_id = con.execute(
            "SELECT COALESCE(MAX(id),0)+1 FROM purchase_order").fetchone()[0]
        name = f"PO/AXP/{po_id:05d}"
        con.execute(
            "INSERT INTO purchase_order (id, name, partner_id, date_order, state, origin) "
            "VALUES (?,?,?,?,?,?)",
            (po_id, name, 1, _now(), "draft", payload["origin"]))
        # 합성 스키마의 라인 테이블 형식(po_ref·qty)에 맞춰 초안 라인 기입
        con.execute(
            "INSERT INTO purchase_order_line "
            "(po_ref, order_date, vendor_id, material_id, qty, unit_price, write_date) "
            "VALUES (?,?,?,?,?,?,?)",
            (name, _now()[:10], "V-DRAFT", payload["product_id"],
             payload["qty"], 0, _now()))
        con.commit()
        return name
    finally:
        con.close()


def _prod_create_po(payload: dict) -> str:
    """prod: Odoo XML-RPC(ORM) — 초안 발주 생성. ODOO_* 환경변수 필요."""
    import xmlrpc.client
    url = os.environ["ODOO_URL"].rstrip("/")
    dbname = os.environ["ODOO_DB"]
    user = os.environ["ODOO_USER"]
    key = os.environ["ODOO_API_KEY"]
    common_ep = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common_ep.authenticate(dbname, user, key, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    def call(model, method, *args, **kw):
        return models.execute_kw(dbname, uid, key, model, method, list(args), kw)

    prod_ids = call("product.product", "search",
                    [["default_code", "=", payload["product_id"]]], limit=1)
    if not prod_ids:
        raise ValueError(f"Odoo에 품목 코드 {payload['product_id']} 없음 — 품목 마스터 매핑 확인")
    po_id = call("purchase.order", "create", {
        "partner_id": int(os.environ.get("ODOO_DEFAULT_VENDOR_ID", "1")),
        "origin": payload["origin"],
        "order_line": [(0, 0, {
            "product_id": prod_ids[0],
            "product_qty": payload["qty"],
            "name": payload["note"] or payload["product_id"],
        })],
    })
    return call("purchase.order", "read", [po_id], fields=["name"])[0]["name"]


def run(mode: str | None = None) -> dict:
    """승인된 미처리 카드 전부를 발주 초안으로. 반환: 처리 요약."""
    mode = mode or ("prod" if os.environ.get("ODOO_URL") else "demo")
    created, skipped = [], []
    for card in _eligible_cards():
        payload = _card_po_payload(card)
        if payload is None:
            skipped.append(card["card_id"])
            continue
        ref = _prod_create_po(payload) if mode == "prod" else _demo_create_po(payload)
        db.execute(
            "INSERT INTO odoo_writeback_log (card_id, target, odoo_ref, payload, created_at) "
            "VALUES (?,?,?,?,?)",
            (card["card_id"], "purchase_order", ref,
             json.dumps(payload, ensure_ascii=False), _now()))
        common.alert("info", "odoo_writeback",
                     f"카드 #{card['card_id']} → 발주 초안 {ref} (확정은 Odoo에서 사람)")
        created.append({"card_id": card["card_id"], "odoo_ref": ref})
    return {"mode": mode, "created": created, "skipped": skipped}
