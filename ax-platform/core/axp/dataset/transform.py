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

from .. import common, config, db
from . import codemap

HOLIDAY_WEEKS = [("2025-01-27", "2025-02-02"), ("2025-10-03", "2025-10-09"),
                 ("2026-02-14", "2026-02-20")]

from .. import profile_rt


def _product_names() -> dict:
    return profile_rt.product_names()


def _store_meta() -> tuple[dict, dict]:
    return profile_rt.store_names(), profile_rt.store_channels()


def _vendor_alias() -> dict:
    """P5-V: 공급사 표시 별칭 — res_partner는 PII(이메일·전화)로 복제하지
    않는다(P5-D3 결정). 원장 숫자 id를 codemap 사전('vendor' 도메인 —
    고객사 프로파일 어휘 시드나 스튜어드 확정으로 채워진다)의 별칭으로
    투영하고, 사전에 없으면 숫자 id 그대로 둔다(격리 큐 미적재 —
    숫자 id는 오류가 아니라 정직한 폴백이다)."""
    try:
        rows = db.query(
            "SELECT alias, standard_code FROM code_dictionary WHERE domain='vendor'")
    except Exception:  # noqa: BLE001 — 사전 미초기화 프로파일
        return {}
    return {r["alias"]: r["standard_code"] for r in rows}


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
    # P5-I3: 달력은 판매만이 아니라 전 사실 계열의 일자를 덮어야 한다 —
    # 실 Odoo에선 미래 착수 MO(생산예정일)가 판매 달력 밖이라 참조 고아가 됐다.
    dates = db.df("""
        SELECT DISTINCT d FROM (
            SELECT order_date AS d FROM staging_sales
            UNION SELECT prod_date FROM staging_mrp
            UNION SELECT receipt_date FROM staging_purchase
            UNION SELECT move_date FROM staging_stock_move
            UNION SELECT check_date FROM staging_quality
            UNION SELECT substr(event_date, 1, 10) FROM staging_maintenance
        ) u WHERE d IS NOT NULL AND d != '' ORDER BY d""")["d"]
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
    prod["category"] = "bakery"
    # P5-I4: 재고 이동·생산에만 나타나는 품목(자재 입고 등)도 차원에 합류 —
    # 실 Odoo 무브는 판매 품목만이 아니라 자재도 다루므로, 판매만으로 만든
    # 차원은 fact_inventory_move.product_id 참조 고아를 만든다.
    extra = db.df("""
        SELECT DISTINCT product_id FROM (
            SELECT product_id FROM staging_stock_move
            UNION SELECT product_id FROM staging_mrp
        ) u WHERE product_id IS NOT NULL AND product_id != ''
          AND product_id NOT IN (SELECT product_id FROM staging_sales)""")
    if len(extra):
        mats = set(db.df("SELECT DISTINCT material_id FROM staging_purchase")["material_id"])
        extra["unit_price"] = None
        extra["category"] = extra["product_id"].map(
            lambda p: "material" if p in mats else "bakery")
        prod = pd.concat([prod, extra], ignore_index=True)
    prod["product_name"] = prod["product_id"].map(pnames).fillna(prod["product_id"])
    counts["dim_product"] = _rebuild("dim_product", prod[["product_id", "product_name", "category", "unit_price"]])

    snames, schannels = _store_meta()
    stores = db.df("SELECT DISTINCT store_id FROM staging_sales")
    stores["store_name"] = stores["store_id"].map(lambda s: snames.get(s, s))
    stores["channel"] = stores["store_id"].map(lambda s: schannels.get(s, "retail"))
    counts["dim_store"] = _rebuild("dim_store", stores)

    workers = db.df(
        "SELECT DISTINCT worker_id FROM staging_mrp WHERE worker_id IS NOT NULL")
    workers["worker_name"] = workers["worker_id"]
    counts["dim_worker"] = _rebuild("dim_worker", workers)

    # P5-I1(복구 드릴 적발): 실 Odoo 경로에선 설비가 생산(staging_mrp)이 아니라
    # 정비(staging_maintenance)에서 온다 — mrp만 보면 정비 사실이 고아가 된다.
    # 두 원천의 합집합으로 차원을 만들고 NULL 설비는 제외한다.
    equip = db.df("""
        SELECT equipment_id, MIN(line_id) AS line_id FROM (
            SELECT equipment_id, line_id FROM staging_mrp
             WHERE equipment_id IS NOT NULL
            UNION ALL
            SELECT equipment_id, NULL AS line_id FROM staging_maintenance
             WHERE equipment_id IS NOT NULL
        ) e GROUP BY equipment_id""")
    equip["equipment_type"] = "oven"
    counts["dim_equipment"] = _rebuild("dim_equipment", equip)

    mats = db.df("SELECT DISTINCT material_id FROM staging_purchase")
    mats["material_name"] = mats["material_id"]
    counts["dim_material"] = _rebuild("dim_material", mats)

    # P3-I9: 실 Odoo에서는 발주 시점에 로트가 없다(로트는 입고에서 생긴다) —
    # 미상 로트를 제외하면 fact_procurement(PK에 lot_id 포함)가 NULL로 깨진다.
    # 제외 대신 'LOT-미상' 표식으로 차원·사실 양쪽에 일관 적재한다(원장 보존).
    # P5-D 후속: 입고(stock_move)에서 확정된 실로트도 차원에 합류 —
    # 발주 시점 'LOT-미상' 표식이 입고 후 재처리(backfill)에서 실로트로 이어진다.
    unk = "COALESCE(lot_id, 'LOT-미상:'||material_id||':'||COALESCE(vendor_id,''))"
    lots = db.df(
        f"""SELECT lot_id, MIN(material_id) AS material_id,
                   MIN(vendor_id) AS vendor_id, MIN(received_date) AS received_date
            FROM (
                SELECT {unk} AS lot_id, material_id, vendor_id,
                       receipt_date AS received_date
                  FROM staging_purchase
                UNION ALL
                SELECT lot_id, product_id AS material_id, NULL AS vendor_id,
                       move_date AS received_date
                  FROM staging_stock_move WHERE lot_id IS NOT NULL
            ) u GROUP BY lot_id""")
    n_unk = int(lots["lot_id"].astype(str).str.startswith("LOT-미상").sum()) if len(lots) else 0
    if n_unk:
        common.alert("warn", "transform",
                     f"lot_id 없는 조달 {n_unk}건 — 'LOT-미상' 표식으로 적재(입고 확정 시 재처리 대상)")
    valias = _vendor_alias()
    if len(lots) and valias:
        lots["vendor_id"] = lots["vendor_id"].map(lambda v: valias.get(v, v))
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

    # P5-I2: 실 Odoo MO에는 교대(shift)가 없다(교대는 현장 장표 소관) —
    # NOT NULL 사실 키를 '미상' 표식으로 지켜 적재한다. 장표 반입 시 재처리로 채움.
    prodn = db.df("""
        SELECT mo_ref, prod_date AS date_key,
               COALESCE(shift, '미상') AS shift, line_id, product_id,
               worker_id, equipment_id, sop_id, qty_planned, qty_done
        FROM staging_mrp""")
    counts["fact_production"] = _rebuild("fact_production", prodn)

    proc = db.df("""
        SELECT po_ref, receipt_date AS date_key, vendor_id, material_id,
               COALESCE(lot_id, 'LOT-미상:'||material_id||':'||COALESCE(vendor_id,'')) AS lot_id,
               qty, qty*unit_price AS amount
        FROM staging_purchase""")
    # P5-V: 공급사 별칭 투영 — 로트 표식(키)은 원장 표기를 유지하고
    # 표시 속성(vendor_id)만 별칭으로 (dim_material_lot과 같은 규칙)
    valias = _vendor_alias()
    if len(proc) and valias:
        proc["vendor_id"] = proc["vendor_id"].map(lambda v: valias.get(v, v))
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
