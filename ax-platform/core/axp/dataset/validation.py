"""교차 원천 검증 (M2 계약의 '검증용' 조항 실체화).

fact_sales의 정본은 Odoo. 엑셀 판매집계(staging_excel sales_summary)는 사실
테이블에 더하지 않고 여기서 정본과 대조한다 — 두 수가 다르면 어느 쪽이 거짓말을
하는지 사람이 물어야 할 신호다.
"""
from __future__ import annotations

import json

import pandas as pd

from .. import common, db
from . import codemap

DDL = """
CREATE TABLE IF NOT EXISTS validation_reports (
  run_at TEXT, source TEXT, n_compared INTEGER, n_mismatch INTEGER,
  detail TEXT
);
"""

TOLERANCE = 0.001    # 수량 상대 오차 허용


def excel_vs_ledger() -> dict:
    """엑셀 판매집계 ↔ fact_sales 대조 — (일, 매장, 제품) 격자."""
    db.executescript(DDL)
    rows = db.query(
        "SELECT payload FROM staging_excel WHERE sheet_kind='sales_summary'")
    if not rows:
        return {"n_compared": 0, "n_mismatch": 0, "note": "엑셀 판매집계 없음"}
    recs = []
    for r in rows:
        p = json.loads(r["payload"])
        store = codemap.resolve("store", p.get("store_id"), "sales_validation") or p.get("store_id")
        prod = codemap.resolve("product", p.get("product_id"), "sales_validation") or p.get("product_id")
        recs.append({"date_key": p.get("date"), "store_id": store,
                     "product_id": prod, "qty_excel": float(p.get("qty") or 0)})
    ex = pd.DataFrame(recs).groupby(["date_key", "store_id", "product_id"],
                                    as_index=False)["qty_excel"].sum()
    led = db.df(
        "SELECT date_key, store_id, product_id, qty AS qty_ledger FROM fact_sales")
    m = ex.merge(led, on=["date_key", "store_id", "product_id"], how="left")
    m["qty_ledger"] = m["qty_ledger"].fillna(0)
    m["diff"] = (m["qty_excel"] - m["qty_ledger"]).abs()
    m["rel"] = m["diff"] / m[["qty_excel", "qty_ledger"]].max(axis=1).clip(lower=1)
    bad = m[m["rel"] > TOLERANCE]
    result = {"n_compared": len(m), "n_mismatch": len(bad),
              "mismatches": bad.head(20).to_dict("records")}
    db.execute("INSERT INTO validation_reports VALUES (?,?,?,?,?)",
               (common.now_iso(), "excel_sales_summary", len(m), len(bad),
                json.dumps(result["mismatches"], ensure_ascii=False)))
    if len(bad):
        common.alert("warn", "M2-검증",
                     f"엑셀 판매집계와 원장 불일치 {len(bad)}건 — 어느 쪽이 맞는지 확인 필요")
    return result
