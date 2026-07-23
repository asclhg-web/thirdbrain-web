"""G09 검증: Odoo 거울(동기화)·일일결산·월결산·로봇 발주 HITL."""
from datetime import datetime

import pytest

from biz import closing, odoo_client, purchase
from graph_core import approvals

NOW = datetime(2026, 7, 22, 21, 30)


class FakeOdoo:
    """모의 Odoo — 어댑터 패턴 검증 (실인스턴스는 .env 4줄로 교체)."""

    def __init__(self):
        self.moves = [
            {"id": 101, "name": "INV/2026/0007", "move_type": "out_invoice",
             "amount_total": 350000.0, "invoice_date": "2026-07-22",
             "partner_id": [7, "교보문고"], "payment_state": "paid"},
            {"id": 102, "name": "BILL/2026/0031", "move_type": "in_invoice",
             "amount_total": 120000.0, "invoice_date": "2026-07-22",
             "partner_id": [12, "서버수리센터"], "payment_state": "not_paid"},
            {"id": 103, "name": "BILL/2026/0032", "move_type": "in_invoice",
             "amount_total": 80000.0, "invoice_date": "2026-07-05",
             "partner_id": [15, "로봇부품상사"], "payment_state": "paid"},
        ]
        self.created: list[tuple] = []
        self.partners = [{"id": 15, "name": "로봇부품상사"}]

    def search_read(self, model, domain, fields, limit=500):
        if model == "account.move":
            return self.moves
        if model == "res.partner":
            name = domain[0][2]
            return [p for p in self.partners if p["name"] == name][:limit]
        return []

    def create(self, model, values):
        self.created.append((model, values))
        return 900 + len(self.created)


@pytest.fixture()
def fake_odoo(fresh_db):
    fake = FakeOdoo()
    odoo_client.set_client(fake)
    yield fake
    odoo_client.set_client(None)


def test_sync_mirrors_odoo_into_graph(fake_odoo):
    r = closing.sync_from_odoo(now=NOW)
    assert r == {"docs": 3, "partners": 3}
    from graph_core import store
    assert len(store.nodes_by_type("BizDoc")) == 3
    names = {p["props"]["name"] for p in store.nodes_by_type("Partner")}
    assert names == {"교보문고", "서버수리센터", "로봇부품상사"}
    assert closing.sync_from_odoo(now=NOW)["docs"] == 3, "멱등 — 두 번 돌려도 안전"


def test_daily_and_monthly_close(fake_odoo):
    closing.sync_from_odoo(now=NOW)
    d = closing.close_day("2026-07-22")
    assert d["sales"] == 350000 and d["expense"] == 120000 and d["profit"] == 230000
    m = closing.close_month("2026-07")
    assert m["profit"] == 350000 - 120000 - 80000 and m["n_docs"] == 3
    assert m["by_partner"]["교보문고"] == 350000, "거래처별 기여 — 월말 교보 정산 확인용"


def test_auto_close_records_and_notifies(fake_odoo):
    r = closing.auto_close_if_due(NOW)
    assert r and r["profit"] == 230000
    assert closing.auto_close_if_due(NOW) is None, "하루 1회만"
    assert closing.auto_close_if_due(datetime(2026, 7, 23, 9)) is None, "21시 전에는 대기"
    from graph import store
    evs = store.events("나", 7, "일일결산", NOW)
    assert len(evs) == 1 and "230,000" in evs[0]["payload"]


def test_purchase_requires_human_approval(fake_odoo):
    """돈이 나가는 길에 자동은 없다 — 승인 전 Odoo 쓰기 0건."""
    aid = purchase.propose_purchase("LeKiwi 모터 세트", 2, 180000,
                                    "로봇 하드웨어 1차 발주", vendor="로봇부품상사", now=NOW)
    assert fake_odoo.created == [], "제안만으로는 아무것도 만들어지지 않는다"
    with pytest.raises(approvals.NotApproved):
        approvals.execute(aid)
    r = approvals.decide(aid, True, NOW)
    assert "초안 생성 완료" in r["result"]
    assert len(fake_odoo.created) == 1 and fake_odoo.created[0][0] == "purchase.order"


def test_purchase_rejected_writes_nothing(fake_odoo):
    aid = purchase.propose_purchase("아무거나", 1, 1000, "테스트", vendor="로봇부품상사", now=NOW)
    approvals.decide(aid, False, NOW)
    assert fake_odoo.created == []


def test_biz_page_renders(fake_odoo):
    from fastapi.testclient import TestClient
    from server.main import app
    c = TestClient(app)
    closing.sync_from_odoo(now=NOW)
    page = c.get("/biz").text
    assert "에이에스씨" in page and "발주 제안" in page
    assert "교보문고" in page and "350,000" in page, "월 결산 거래처 기여 노출"
    c.post("/biz/purchase", data={"item": "모터", "qty": 1, "est_price": 1000,
                                  "vendor": "로봇부품상사", "reason": "r"})
    assert any("발주 제안" in a["title"] for a in approvals.pending())
