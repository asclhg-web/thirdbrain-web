"""P2-C2 — Odoo 쓰기 커넥터: 승인 카드→발주 초안, 멱등성."""
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from axp import db  # noqa: E402
from axp.ingest import odoo_cdc, odoo_writeback  # noqa: E402
from axp import db as _db  # noqa: E402,F401
from axp.judge import cards as jcards  # noqa: E402


def _mk_card(status="executed"):
    db.executescript(jcards.DDL)
    cur_id = db.query(
        "SELECT COALESCE(MAX(card_id),0)+1 AS n FROM judgment_cards")[0]["n"]
    db.execute(
        "INSERT INTO judgment_cards (kind, agent, proposal, narrative, values_json, "
        "range_json, evidence_json, alternatives_json, approver, status, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        ("demand_forecast", "demand_agent",
         "파이만쥬(P-PIE) S-TEST — 7일 발주 기준수량을 2015개로 제안",
         "테스트 [근거: t]", json.dumps([{"name": "합계", "value": 2015}]),
         json.dumps({"p10": 1800, "p50": 2015, "p90": 2100}),
         "[]", "[]", "카드 승인자", status, "2026-09-11T00:00:00"))
    return cur_id


def test_writeback_creates_draft_and_is_idempotent(tmp_db):
    cid = _mk_card()
    r1 = odoo_writeback.run(mode="demo")
    assert len(r1["created"]) == 1 and r1["created"][0]["card_id"] == cid
    ref = r1["created"][0]["odoo_ref"]
    con = sqlite3.connect(odoo_cdc.source_path())
    row = con.execute("SELECT state, origin FROM purchase_order WHERE name=?",
                      (ref,)).fetchone()
    assert row == ("draft", f"AXP card #{cid}")
    qty = con.execute("SELECT qty FROM purchase_order_line WHERE po_ref=?",
                      (ref,)).fetchone()[0]
    assert qty == 2015
    # 멱등: 두 번째 실행은 아무 것도 만들지 않는다
    r2 = odoo_writeback.run(mode="demo")
    assert r2["created"] == []


def test_writeback_ignores_unapproved(tmp_db):
    _mk_card(status="proposed")
    r = odoo_writeback.run(mode="demo")
    assert r["created"] == []


def test_drafts_not_reingested_by_cdc(tmp_db):
    """P2-I11 회귀 — 플랫폼 초안(PO/AXP/*)은 CDC가 재수집하지 않는다."""
    cid = _mk_card()
    odoo_writeback.run(mode="demo")
    counts = odoo_cdc.sync()
    n = db.scalar("SELECT COUNT(*) FROM staging_purchase WHERE po_ref LIKE 'PO/AXP/%'")
    assert n == 0, "초안이 스테이징으로 되돌아왔다 — 자기 환류 오염"
    rec = odoo_cdc.reconcile()
    pu = [r for r in rec["series"] if r["series"] == "staging_purchase"][0]
    assert pu["ok"], pu   # 초안 제외 기준으로 정합도 일치해야 한다
