"""합성 거래 생성기 — 고객사 프로파일(demo/profiles.py) 위에서 돈다.

구조(회사·매장·제품·자재·어휘)는 프로파일의 실제 값, 거래 수치는 합성.
실데이터 전환 시 이 생성기 대신 M1 커넥터가 같은 스테이징을 채운다.

심은 검증 시나리오(프로파일 plant 절):
  P1) plant.equipment × plant.vendor 자재 로트(25年 7~8월) → 불량률 3배
  P2) 야간조 × plant.night_worker → 성형 불량 소폭 증가
  P3) plant.equipment 고장 전 2주 센서 드리프트
"""
from __future__ import annotations

import json
import random
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from axp import config  # noqa: E402
import profiles  # noqa: E402

RNG = np.random.default_rng(42)
random.seed(42)

START = date(2024, 9, 1)
END = date(2026, 8, 31)          # 24개월

WORKERS = ["W-01", "W-02", "W-03", "W-04", "W-05", "W-06"]
DEFECT_TYPES = ["탄화", "미성형", "충전 불량", "이물", "수분 과다"]
HOLIDAY_WEEKS = [(date(2025, 1, 27), date(2025, 2, 2)), (date(2025, 10, 3), date(2025, 10, 9)),
                 (date(2026, 2, 14), date(2026, 2, 20))]

# 프로파일 전개 (모듈 전역 — 함수들이 참조)
P = profiles.active()
PRODUCTS = P["products"]
STORES = P["stores"]
LINE_OF, DEFAULT_LINE = P["line_of"], P["default_line"]
OVENS = P["ovens"]
SOPS = P["sops"]
MATERIALS, VENDORS = P["materials"], P["vendors"]
PLANT = P["plant"]
HOLIDAY_PRODUCTS = set(P["holiday_products"])


def is_holiday_week(d: date) -> bool:
    return any(a <= d <= b for a, b in HOLIDAY_WEEKS)


def daterange(a: date, b: date):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)


def gen_promos() -> pd.DataFrame:
    rows = []
    d = START
    while d < END:
        for _ in range(RNG.integers(1, 3)):
            pid = random.choice(list(PRODUCTS))
            start = d + timedelta(days=int(RNG.integers(0, 20)))
            rows.append({"date_start": start.isoformat(),
                         "date_end": (start + timedelta(days=6)).isoformat(),
                         "product_id": pid,
                         "promo_name": f"{PRODUCTS[pid][0]} 특가",
                         "discount_pct": int(RNG.choice([10, 15, 20]))})
        d += timedelta(days=30)
    return pd.DataFrame(rows)


def demand(pid: str, store: str, d: date, promo: bool) -> int:
    base, seas_amp = PRODUCTS[pid][1], PRODUCTS[pid][2]
    scale = STORES[store][2]
    dow = [0.95, 0.9, 0.92, 0.95, 1.1, 1.45, 1.35][d.weekday()]
    seas = 1 + seas_amp * np.sin(2 * np.pi * (d.timetuple().tm_yday - 30) / 365)
    trend = 1 + 0.10 * (d - START).days / 730
    holi = 1.9 if is_holiday_week(d) and pid in HOLIDAY_PRODUCTS \
        else (1.2 if is_holiday_week(d) else 1)
    pr = 1.35 if promo else 1.0
    mu = base * scale * dow * seas * trend * holi * pr
    return max(0, int(RNG.poisson(mu)))


def write_profile_json() -> None:
    """런타임(변환·에이전트·E2E)이 읽는 프로파일 스냅샷 — 커스터디 대상."""
    doc = {
        "profile": profiles.active_name(),
        "company": P["company"],
        "product_names": {pid: v[0] for pid, v in PRODUCTS.items()},
        "product_prices": {pid: v[3] for pid, v in PRODUCTS.items()},
        "store_names": {sid: v[0] for sid, v in STORES.items()},
        "store_channels": {sid: v[1] for sid, v in STORES.items()},
        "primary_pairs": P["primary_pairs"],
        "primary_store": P["primary_store"],
        "primary_product": P["primary_product"],
        "alias_seed": P["alias_seed"],
        "name2code": P["name2code"],
        "plant": PLANT,
    }
    (config.DATA / "profile.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    config.ensure_dirs()
    write_profile_json()
    odoo = config.DATA / "odoo.db"
    odoo.unlink(missing_ok=True)
    con = sqlite3.connect(odoo)
    cur = con.cursor()
    cur.executescript("""
    CREATE TABLE sale_order_line (id INTEGER PRIMARY KEY, order_ref TEXT, order_date TEXT,
      store_id TEXT, product_id TEXT, qty REAL, unit_price REAL, channel TEXT,
      promo_flag INTEGER, write_date TEXT);
    CREATE TABLE purchase_order_line (id INTEGER PRIMARY KEY, po_ref TEXT, order_date TEXT,
      receipt_date TEXT, vendor_id TEXT, material_id TEXT, qty REAL, unit_price REAL,
      lot_id TEXT, write_date TEXT);
    CREATE TABLE stock_move (id INTEGER PRIMARY KEY, move_date TEXT, product_id TEXT,
      from_loc TEXT, to_loc TEXT, qty REAL, move_type TEXT, lot_id TEXT, reason TEXT,
      write_date TEXT);
    CREATE TABLE mrp_production (id INTEGER PRIMARY KEY, mo_ref TEXT, prod_date TEXT,
      product_id TEXT, line_id TEXT, worker_id TEXT, equipment_id TEXT, sop_id TEXT,
      qty_planned REAL, qty_done REAL, shift TEXT, write_date TEXT);
    CREATE TABLE quality_check (id INTEGER PRIMARY KEY, check_date TEXT, mo_ref TEXT,
      product_id TEXT, line_id TEXT, worker_id TEXT, equipment_id TEXT,
      material_lot_id TEXT, sop_id TEXT, defect_type TEXT, qty_defect REAL, shift TEXT,
      memo TEXT, write_date TEXT);
    CREATE TABLE maintenance_request (id INTEGER PRIMARY KEY, event_date TEXT,
      equipment_id TEXT, event_type TEXT, duration_min REAL, note TEXT, write_date TEXT);
    """)

    promos = gen_promos()
    promo_lookup: dict[tuple[str, str], bool] = {}
    for r in promos.itertuples():
        for d in daterange(date.fromisoformat(r.date_start), date.fromisoformat(r.date_end)):
            promo_lookup[(r.product_id, d.isoformat())] = True

    # ── 판매
    sales = []
    for d in daterange(START, END):
        for store, (sname, channel, scale, excludes) in STORES.items():
            for pid in PRODUCTS:
                if pid in excludes:
                    continue
                promo = promo_lookup.get((pid, d.isoformat()), False)
                q = demand(pid, store, d, promo)
                if q == 0:
                    continue
                sales.append((f"SO{d.strftime('%y%m%d')}{store[-3:]}", d.isoformat(), store,
                              pid, q, PRODUCTS[pid][3], channel, int(promo),
                              d.isoformat() + "T20:00:00"))
    cur.executemany(
        "INSERT INTO sale_order_line (order_ref, order_date, store_id, product_id, qty, "
        "unit_price, channel, promo_flag, write_date) VALUES (?,?,?,?,?,?,?,?,?)", sales)

    # ── 구매 (plant.material 로트가 P1의 무대 — 25年 7~8월 plant.vendor)
    purchases, lots = [], []
    po_n = 0
    for mat, vend_list in VENDORS.items():
        d = START
        while d < END:
            po_n += 1
            vendor = vend_list[po_n % len(vend_list)] if len(vend_list) > 1 else vend_list[0]
            lot = f"LOT-{mat[2:]}-{d.strftime('%y%m')}{'A' if po_n % 2 else 'B'}-{vendor}"
            lots.append((mat, vendor, lot, d))
            purchases.append((f"PO-{po_n:05d}", d.isoformat(),
                              (d + timedelta(days=2)).isoformat(), vendor, mat,
                              float(RNG.integers(200, 500)), float(RNG.integers(800, 2500)),
                              lot, d.isoformat() + "T09:00:00"))
            d += timedelta(days=15)
    cur.executemany(
        "INSERT INTO purchase_order_line (po_ref, order_date, receipt_date, vendor_id, "
        "material_id, qty, unit_price, lot_id, write_date) VALUES (?,?,?,?,?,?,?,?,?)",
        purchases)

    def plant_lot_for(d: date) -> tuple[str, str]:
        mat = PLANT["material"]
        cands = [(m, v, l, dd) for m, v, l, dd in lots
                 if m == mat and dd <= d and (d - dd).days < 20]
        if not cands:
            cands = [x for x in lots if x[0] == mat][:1]
        m, v, l, dd = cands[-1]
        return l, v

    # ── 생산 + 품질 (P1·P2)
    mrp, quality, moves = [], [], []
    mo_n = 0
    bad_window = (date(2025, 7, 1), date(2025, 8, 31))
    plant_eq, plant_vendor = PLANT["equipment"], PLANT["vendor"]
    night_worker = PLANT["night_worker"]
    eq_name = {v: k for k, v in OVENS.items()}
    memo_bad = f"반죽 되직함, {plant_eq.replace('OVEN-', '오븐')} 온도 편차 있는 듯"
    for d in daterange(START, END):
        day_sales = {pid: sum(s[4] for s in sales if s[1] == d.isoformat() and s[3] == pid)
                     for pid in PRODUCTS}
        for pid, total in day_sales.items():
            if total <= 0:
                continue
            line = LINE_OF.get(pid, DEFAULT_LINE)
            for shift in (["주간", "야간"] if total > 250 else ["주간"]):
                mo_n += 1
                worker = random.choice(WORKERS[:4] if shift == "주간" else WORKERS[3:])
                equip = OVENS[line]
                planned = int(total * (0.65 if shift == "주간" else 0.45) * 1.06)
                lot, vendor = plant_lot_for(d)
                rate = 0.015
                in_bad = (equip == plant_eq and vendor == plant_vendor
                          and bad_window[0] <= d <= bad_window[1])
                if in_bad:
                    rate *= 3.0                                   # P1
                if shift == "야간" and worker == night_worker:
                    rate *= 1.6                                   # P2
                qty_def = int(RNG.binomial(planned, min(rate, 0.5)))
                done = planned - qty_def
                mrp.append((f"MO-{mo_n:06d}", d.isoformat(), pid, line, worker, equip,
                            SOPS[pid], planned, done, shift, d.isoformat() + "T18:00:00"))
                if qty_def > 0:
                    dtype = ("탄화" if in_bad and RNG.random() < 0.6
                             else ("미성형" if shift == "야간" and worker == night_worker
                                   else random.choice(DEFECT_TYPES)))
                    memo = ""
                    if in_bad and RNG.random() < 0.25:
                        memo = memo_bad
                    elif dtype == "미성형" and RNG.random() < 0.2:
                        memo = "야간 성형 속도 문제로 보임"
                    quality.append((d.isoformat(), f"MO-{mo_n:06d}", pid, line, worker,
                                    equip, lot, SOPS[pid], dtype, qty_def, shift, memo,
                                    d.isoformat() + "T19:00:00"))
                moves.append((d.isoformat(), pid, "PROD", "WH", float(done), "production",
                              lot, "", d.isoformat() + "T18:30:00"))
        for pid, total in day_sales.items():
            if total > 0:
                moves.append((d.isoformat(), pid, "WH", "STORES", float(total), "delivery",
                              "", "", d.isoformat() + "T07:00:00"))
                waste = int(total * RNG.uniform(0.01, 0.05))
                if waste:
                    moves.append((d.isoformat(), pid, "STORES", "SCRAP", float(waste),
                                  "scrap", "", "유통기한", d.isoformat() + "T21:00:00"))
    cur.executemany(
        "INSERT INTO mrp_production (mo_ref, prod_date, product_id, line_id, worker_id, "
        "equipment_id, sop_id, qty_planned, qty_done, shift, write_date) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?)", mrp)
    cur.executemany(
        "INSERT INTO quality_check (check_date, mo_ref, product_id, line_id, worker_id, "
        "equipment_id, material_lot_id, sop_id, defect_type, qty_defect, shift, memo, "
        "write_date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", quality)
    cur.executemany(
        "INSERT INTO stock_move (move_date, product_id, from_loc, to_loc, qty, move_type, "
        "lot_id, reason, write_date) VALUES (?,?,?,?,?,?,?,?,?)", moves)

    # ── 정비 이력 (P3: plant 설비 고장 전 드리프트와 짝)
    other_eq = [e for e in OVENS.values() if e != plant_eq][0] if len(OVENS) > 1 else plant_eq
    maint = []
    for d, equip, etype, dur, note in [
        (date(2025, 3, 12), other_eq, "예방 점검", 90, "정기"),
        (date(2025, 6, 20), plant_eq, "고장 수리", 320, "히터 소자 교체"),
        (date(2025, 9, 15), plant_eq, "예방 점검", 120, "온도 편차 조정"),
        (date(2026, 2, 10), other_eq, "예방 점검", 90, "정기"),
        (date(2026, 6, 18), plant_eq, "고장 수리", 280, "컨베이어 베어링"),
    ]:
        maint.append((d.isoformat(), equip, etype, dur, note, d.isoformat() + "T10:00:00"))
    cur.executemany(
        "INSERT INTO maintenance_request (event_date, equipment_id, event_type, "
        "duration_min, note, write_date) VALUES (?,?,?,?,?,?)", maint)
    con.commit()
    con.close()

    # ── 센서 180일 — P3 드리프트
    sensor_rows = []
    s_start = END - timedelta(days=180)
    fail2 = date(2026, 6, 18)
    for d in daterange(s_start, END):
        for hh in range(0, 24):
            for mm in (0, 10, 20, 30, 40, 50):
                ts = f"{d.isoformat()}T{hh:02d}:{mm:02d}:00"
                for equip in OVENS.values():
                    drift = 0.0
                    if equip == plant_eq:
                        days_to_fail = (fail2 - d).days
                        if 0 <= days_to_fail <= 14:
                            drift = (14 - days_to_fail) / 14
                    sensor_rows.append((ts, equip, "temp",
                                        round(210 + RNG.normal(0, 2.0) + drift * 8, 2)))
                    sensor_rows.append((ts, equip, "current",
                                        round(32 + RNG.normal(0, 0.8) + drift * 3, 2)))
                    sensor_rows.append((ts, equip, "vibration",
                                        round(0.8 + abs(RNG.normal(0, 0.1)) + drift * 0.9, 3)))
    pd.DataFrame(sensor_rows, columns=["reading_ts", "equipment_id", "signal", "value"]) \
        .to_csv(config.DATA / "sensor_replay.csv", index=False)

    # ── 엑셀 양식 2종 — 주력 매장 판매집계 + 프로모션 달력(제품'명' 기입)
    xls_dir = config.DATA / "inbox"
    xls_dir.mkdir(parents=True, exist_ok=True)
    promo_xls = promos.copy()
    promo_xls["product_id"] = promo_xls["product_id"].map(lambda p: PRODUCTS[p][0])
    promo_xls.rename(columns={"date_start": "시작일", "date_end": "종료일",
                              "product_id": "제품코드", "promo_name": "행사명",
                              "discount_pct": "할인율"}) \
        .to_excel(xls_dir / "프로모션_달력.xlsx", index=False)
    primary = P["primary_store"]
    recent = [s for s in sales if s[1] >= (END - timedelta(days=14)).isoformat()
              and s[2] == primary]
    pd.DataFrame([{"판매일": r[1], "매장": r[2], "품목": r[3], "수량": r[4]} for r in recent]) \
        .to_excel(xls_dir / "본점_판매집계.xlsx", index=False)

    print(f"[{P['company']} · {profiles.active_name()}] "
          f"판매 {len(sales):,} · 생산 {len(mrp):,} · 품질 {len(quality):,} · "
          f"이동 {len(moves):,} · 구매 {len(purchases):,} · 정비 {len(maint)}")
    print(f"센서 {len(sensor_rows):,}행 · 엑셀 2종 · profile.json 기록")


if __name__ == "__main__":
    main()
