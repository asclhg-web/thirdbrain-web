"""로봇 발주 (G09) — 자동이 아니라 '자동 제안 + 사람 승인'이다.

로봇/에이전트는 propose_purchase()로 제안만 할 수 있다. 승인 큐에서 사람이
승인하는 순간에만 Odoo에 발주서(purchase.order) 초안이 만들어진다 — 그것도
Odoo 안에서 '초안' 상태다(이중 안전망: 최종 확정도 Odoo에서 사람이 한다).
돈이 나가는 길에 자동은 없다 (유산 헌장 HITL).
"""
from datetime import datetime

from graph_core import approvals

from biz import odoo_client

KIND = "odoo_purchase"


def propose_purchase(item: str, qty: int, est_price: float, reason: str,
                     vendor: str = "", proposed_by: str = "robot",
                     now: datetime | None = None) -> int:
    """발주 제안 → 승인 큐. 실행은 사람 승인 후에만."""
    title = f"발주 제안: {item} ×{qty} (약 {est_price:,.0f}원)"
    return approvals.propose(KIND, title, {
        "item": item, "qty": qty, "est_price": est_price,
        "reason": reason, "vendor": vendor}, proposed_by, now)


def _exec_purchase(detail: dict) -> str:
    """승인 시에만 호출된다 — Odoo에 발주서 '초안' 생성."""
    try:
        client = odoo_client.get_client()
        vendor_ids = client.search_read(
            "res.partner", [["name", "=", detail.get("vendor", "")]], ["id"], 1) \
            if detail.get("vendor") else []
        vendor_id = vendor_ids[0]["id"] if vendor_ids else False
        if not vendor_id:
            return ("Odoo에 해당 공급업체가 없어 발주 초안을 만들지 못했습니다 — "
                    "Odoo에서 거래처를 먼저 등록하거나 공급업체명을 확인해 주세요.")
        po_id = client.create("purchase.order", {
            "partner_id": vendor_id,
            "notes": f"[브레인그래프 승인 발주] {detail.get('item')} ×{detail.get('qty')} "
                     f"(예상 {detail.get('est_price', 0):,.0f}원) — 사유: {detail.get('reason', '')}",
        })
        return f"Odoo 발주서 초안 생성 완료 (purchase.order id={po_id}) — Odoo에서 품목·가격 확정 후 발송하세요."
    except Exception as e:
        return f"Odoo 발주 초안 생성 실패({e}) — 연결 확인 후 다시 제안해 주세요."


approvals.register_executor(KIND, _exec_purchase)
