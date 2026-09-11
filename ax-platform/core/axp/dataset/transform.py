"""M2-2 변환 — 스테이징 → 표준 사실 테이블 6계열. 멱등(재실행 안전).

dbt식 규율: 각 모델은 결정적 SELECT — 전량 재구축해도 같은 결과.
계보: 사실 행은 원천(mo_ref·po_ref·src_id)을 보존한다.
중복 원천 규칙: 판매의 정본은 Odoo(staging_sales) — 엑셀 판매집계는 검증용으로만
쓰고 사실 테이블에 더하지 않는다(이중 계상 방지, 계약서에 명시).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .. import config, db
from . import codemap

HOLIDAY_WEEKS = [("2025-01-27", "2025-02-02"), ("2025-10-03", "2025-10-09"),
                 ("2026-02-14", "2026-02-20")]

from .. import profile_rt


def _product_names() -> dict:
    return profile_rt.product_names()


def _store_meta() -> tuple[dict, dict]:
    return profile_rt.store_names(), profile_rt.store_channels()


def apply_schema() -> None:
    sql = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")
    db.executescript(sql)


def _rebuild(table: str, frame: pd.DataFrame) -> int:
    """전량 재구축(멱등) — 재구축 트랜잭션 동안만 FK 검사를 끈다.
    (부모 차원을 지웠다 다시 넣는 동안의 일시 위반 허용 — 종료 시 원상복구)"""
    with db.conn() as c:
        c.execute("PRAGMA foreign_keys=OFF")
        c.execute(f"DELETE FROM {table}")
        if len(frame):
            db.load_frame(c, frame, table)
        c.execute("PRAGMA foreign_keys=ON")
    return len(frame)


def build_dims() -> dict[str, int]:
    apply_schema()
    codemap.init()
    counts = {}
    # 달력 — 판매 기간 전체
    dates = db.df("SELECT DISTINCT order_date AS d FROM staging_sales ORDER BY d")["d"]
    cal = pd.DataFrame({"date_key": dates})
    dt = pd.to_datetime(cal["date_key"])
    cal["dow"] = dt.dt.dayofweek
    cal["month"] = dt.dt.month
    cal["is_weekend"] = (cal["dow"] >= 5).astype(int)
    cal["is_holiday_week"] = 0
    for a, b in HOLIDAY_WEEKS:
        cal.loc[(cal["date_key"] >= a) & (cal["date_key"] <= b), "is_holiday_week"] = 1
    counts["dim_calendar"] = _rebuild("dim_calendar", cal)

    pnames = _product_names()
    prod = db.df("SELECT product_id, AVG(unit_price) AS unit_price FROM staging_sales GROUP BY product_id")
    prod["product_name"] = prod["product_id"].map(pnames).fillna(prod["product_id"])
    prod["category"] = "bakery"
    counts["dim_product"] = _rebuild("dim_product", prod[["product_id", "product_name", "category", "unit_price"]])

    snames, schannels = _store_meta()
    stores = db.df("SELECT DISTINCT store_id FROM staging_sales")
    stores["store_name"] = stores["store_id"].map(lambda s: snames.get(s, s))
    stores["channel"] = stores["store_id"].map(lambda s: schannels.get(s, "retail"))
    counts["dim_store"] = _rebuild("dim_store", stores)

    workers = db.df("SELECT DISTINCT worker_id FROM staging_mrp")
    workers["worker_name"] = workers["worker_id"]
    counts["dim_worker"] = _rebuild("dim_worker", workers)

    equip = db.df("SELECT DISTINCT equipment_id, line_id FROM staging_mrp")
    equip["equipment_type"] = "oven"
    counts["dim_equipment"] = _rebuild("dim_equipment", equip)

    mats = db.df("SELECT DISTINCT material_id FROM staging_purchase")
    mats["material_name"] = mats["material_id"]
    counts["dim_material"] = _rebuild("dim_material", mats)

    lots = db.df(
        "SELECT lot_id, material_id, vendor_id, MIN(receipt_date) AS received_date "
        "FROM staging_purchase GROUP BY lot_id, material_id, vendor_id")
    counts["dim_material_lot"] = _rebuild("dim_material_lot", lots)

    sops = db.df("SELECT DISTINCT sop_id FROM staging_mrp")
    sops["sop_name"] = sops["sop_id"]
    counts["dim_sop"] = _rebuild("dim_sop", sops)

    # 프로모션 — 엑셀 업로드(promo_calendar)에서
    promo_rows = db.query(
        "SELECT payload FROM staging_excel WHERE sheet_kind='promo_calendar'")
    if promo_rows:
        seen = set()
        recs = []
        for r in promo_rows:
            p = json.loads(r["payload"])
            key = (p.get("date_start"), p.get("product_id"), p.get("promo_name"))
            if key in seen:
                continue
            seen.add(key)
            pid = codemap.resolve("product", p.get("product_id"), "promo_calendar") \
                or p.get("product_id")
            recs.append({"date_start": p.get("date_start"), "date_end": p.get("date_end"),
                         "product_id": pid, "promo_name": p.get("promo_name"),
                         "discount_pct": p.get("discount_pct")})
        db.execute("DELETE FROM dim_promo")
        db.write_df(pd.DataFrame(recs), "dim_promo")
        counts["dim_promo"] = len(recs)
    return counts


def build_facts() -> dict[str, int]:
    apply_schema()
    counts = {}
    sales = db.df("""
        SELECT order_date AS date_key, store_id, product_id,
               SUM(qty) AS qty, SUM(qty*unit_price) AS revenue,
               MAX(channel) AS channel, MAX(promo_flag) AS promo_flag
        FROM staging_sales GROUP BY order_date, store_id, product_id""")
    counts["fact_sales"] = _rebuild("fact_sales", sales)

    prodn = db.df("""
        SELECT mo_ref, prod_date AS date_key, shift, line_id, product_id,
               worker_id, equipment_id, sop_id, qty_planned, qty_done
        FROM staging_mrp""")
    counts["fact_production"] = _rebuild("fact_production", prodn)

    proc = db.df("""
        SELECT po_ref, receipt_date AS date_key, vendor_id, material_id, lot_id,
               qty, qty*unit_price AS amount
        FROM staging_purchase""")
    counts["fact_procurement"] = _rebuild("fact_procurement", proc)

    moves = db.df("""
        SELECT src_id AS move_id, move_date AS date_key, product_id, from_loc, to_loc,
               move_type, qty, lot_id, reason
        FROM staging_stock_move""")
    counts["fact_inventory_move"] = _rebuild("fact_inventory_move", moves)

    defects = db.df("""
        SELECT q.src_id AS defect_id, q.check_date AS date_key, q.shift, q.product_id,
               q.line_id, q.worker_id, q.equipment_id, q.material_lot_id, q.sop_id,
               q.defect_type, q.qty_defect, m.qty_planned AS qty_produced, q.memo, q.mo_ref
        FROM staging_quality q LEFT JOIN staging_mrp m ON m.mo_ref = q.mo_ref""")
    counts["fact_defect"] = _rebuild("fact_defect", defects)

    events = db.df("""
        SELECT src_id AS event_id, event_date AS date_key, equipment_id, event_type,
               duration_min, note
        FROM staging_maintenance""")
    counts["fact_equipment_event"] = _rebuild("fact_equipment_event", events)

    sensors = db.df("""
        SELECT substr(reading_ts,1,10) AS date_key, equipment_id, signal,
               COUNT(*) AS n, AVG(value) AS mean,
               0.0 AS std, 0.0 AS p95, MAX(value) AS max
        FROM staging_iot GROUP BY substr(reading_ts,1,10), equipment_id, signal""")
    if len(sensors):
        raw = db.df("SELECT substr(reading_ts,1,10) AS date_key, equipment_id, signal, value FROM staging_iot")
        agg = raw.groupby(["date_key", "equipment_id", "signal"])["value"] \
            .agg(std="std", p95=lambda s: s.quantile(0.95)).reset_index()
        sensors = sensors.drop(columns=["std", "p95"]).merge(agg, on=["date_key", "equipment_id", "signal"])
        sensors = sensors[["date_key", "equipment_id", "signal", "n", "mean", "std", "p95", "max"]]
    counts["fact_sensor_daily"] = _rebuild("fact_sensor_daily", sensors)
    return counts


def run_all() -> dict[str, int]:
    out = build_dims()
    out.update(build_facts())
    return out


if __name__ == "__main__":
    import sys
    if "--apply" in sys.argv:
        apply_schema()
        print("schema applied")
    else:
        print(run_all())
