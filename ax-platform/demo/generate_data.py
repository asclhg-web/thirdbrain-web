"""합성 제빵회사 데이터 생성기 — 데모제과(가상).

24개월 판매·생산·구매·재고·품질·정비 + 90일 센서 + 엑셀 양식 2종.
품질 데이터에는 '심어 둔 원인'이 있다 — 플랫폼(M3 마이닝→M5 그래프→M6 카드)이
이것을 스스로 찾아내는지가 E2E 검증의 핵심이다.

심은 원인:
  P1) OVEN-2 × 밀가루 로트(공급사 V2, 7~8월분) → 불량률 3배
  P2) 야간조 × W-03 → 성형 불량 소폭 증가
  P3) OVEN-2 는 정비 직전 2주간 온도 편차·진동 상승 (센서에 드러남)
"""
from __future__ import annotations

import random
import sqlite3
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
from axp import config  # noqa: E402

RNG = np.random.default_rng(42)
random.seed(42)

START = date(2024, 9, 1)
END = date(2026, 8, 31)          # 24개월

PRODUCTS = {   # product_id: (이름, 기본 일판매(직영), 계절성 진폭, 단가)
    "P-CREAM":  ("크림빵", 120, 0.10, 1800),
    "P-RED":    ("단팥빵", 100, 0.15, 1700),
    "P-BAG":    ("바게트", 60, 0.05, 3500),
    "P-CAKE":   ("조각케이크", 45, 0.30, 4500),
    "P-SAND":   ("샌드위치", 80, 0.08, 4200),
    "P-PIE":    ("파이만쥬", 150, 0.25, 1500),
    "P-CROI":   ("크루아상", 70, 0.12, 2800),
    "P-DONUT":  ("도넛", 90, 0.10, 2000),
}
STORES = ["S-MAIN", "S-STATION", "B2B-MART", "B2B-CAFE"]   # 직영 2 + B2B 2
LINES = ["L1", "L2"]
WORKERS = ["W-01", "W-02", "W-03", "W-04", "W-05", "W-06"]
OVENS = {"L1": "OVEN-1", "L2": "OVEN-2"}
SOPS = {"P-CREAM": "SOP-BUN-01", "P-RED": "SOP-BUN-01", "P-BAG": "SOP-BREAD-02",
        "P-CAKE": "SOP-CAKE-03", "P-SAND": "SOP-COLD-04", "P-PIE": "SOP-PIE-05",
        "P-CROI": "SOP-LAM-06", "P-DONUT": "SOP-FRY-07"}
MATERIALS = {"M-FLOUR": "밀가루", "M-SUGAR": "설탕", "M-BUTTER": "버터",
             "M-CREAM": "생크림", "M-REDBEAN": "팥앙금"}
VENDORS = {"M-FLOUR": ["V1", "V2"], "M-SUGAR": ["V3"], "M-BUTTER": ["V4"],
           "M-CREAM": ["V4"], "M-REDBEAN": ["V5"]}
DEFECT_TYPES = ["탄화", "미성형", "충전 불량", "이물", "수분 과다"]

# 명절(수요 급증) — 대략의 설·추석 주간
HOLIDAY_WEEKS = [(date(2025, 1, 27), date(2025, 2, 2)), (date(2025, 10, 3), date(2025, 10, 9)),
                 (date(2026, 2, 14), date(2026, 2, 20))]


def is_holiday_week(d: date) -> bool:
    return any(a <= d <= b for a, b in HOLIDAY_WEEKS)


def daterange(a: date, b: date):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)


def gen_promos() -> pd.DataFrame:
    """월 1~2회, 제품 하나씩 1주 프로모션."""
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
    scale = {"S-MAIN": 1.0, "S-STATION": 0.65, "B2B-MART": 1.6, "B2B-CAFE": 0.5}[store]
    dow = [0.95, 0.9, 0.92, 0.95, 1.1, 1.45, 1.35][d.weekday()]          # 주말 산
    seas = 1 + seas_amp * np.sin(2 * np.pi * (d.timetuple().tm_yday - 30) / 365)
    trend = 1 + 0.10 * (d - START).days / 730                            # 완만한 성장
    holi = 1.9 if is_holiday_week(d) and pid in ("P-PIE", "P-CAKE") else (1.2 if is_holiday_week(d) else 1)
    pr = 1.35 if promo else 1.0
    mu = base * scale * dow * seas * trend * holi * pr
    return max(0, int(RNG.poisson(mu)))


def main() -> None:
    config.ensure_dirs()
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
        for store in STORES:
            channel = "B2B" if store.startswith("B2B") else "retail"
            for pid in PRODUCTS:
                if store == "B2B-CAFE" and pid in ("P-CAKE", "P-PIE"):
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

    # ── 구매(밀가루 로트 — 월 2회, 공급사 교대; P1의 '문제 로트'는 25年 7~8월 V2)
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

    def flour_lot_for(d: date) -> tuple[str, str]:
        cands = [(m, v, l, dd) for m, v, l, dd in lots
                 if m == "M-FLOUR" and dd <= d and (d - dd).days < 20]
        if not cands:
            cands = [x for x in lots if x[0] == "M-FLOUR"][:1]
        m, v, l, dd = cands[-1]
        return l, v

    # ── 생산 + 품질 (심은 원인 P1·P2)
    mrp, quality, moves = [], [], []
    mo_n = 0
    bad_lot_window = (date(2025, 7, 1), date(2025, 8, 31))
    for d in daterange(START, END):
        day_sales = {pid: sum(s[4] for s in sales if s[1] == d.isoformat() and s[3] == pid)
                     for pid in PRODUCTS}
        for pid, total in day_sales.items():
            if total <= 0:
                continue
            line = "L1" if pid in ("P-CREAM", "P-RED", "P-CROI", "P-DONUT") else "L2"
            for shift in (["주간", "야간"] if total > 250 else ["주간"]):
                mo_n += 1
                worker = random.choice(WORKERS[:4] if shift == "주간" else WORKERS[3:])
                equip = OVENS[line]
                planned = int(total * (0.65 if shift == "주간" else 0.45) * 1.06)
                lot, vendor = flour_lot_for(d)
                # 불량률: 기저 1.5% + 심은 원인
                rate = 0.015
                in_bad = (equip == "OVEN-2" and vendor == "V2"
                          and bad_lot_window[0] <= d <= bad_lot_window[1])
                if in_bad:
                    rate *= 3.0                                   # P1
                if shift == "야간" and worker == "W-03":
                    rate *= 1.6                                   # P2
                qty_def = int(RNG.binomial(planned, min(rate, 0.5)))
                done = planned - qty_def
                mrp.append((f"MO-{mo_n:06d}", d.isoformat(), pid, line, worker, equip,
                            SOPS[pid], planned, done, shift, d.isoformat() + "T18:00:00"))
                if qty_def > 0:
                    dtype = ("탄화" if in_bad and RNG.random() < 0.6
                             else ("미성형" if shift == "야간" and worker == "W-03"
                                   else random.choice(DEFECT_TYPES)))
                    memo = ""
                    if in_bad and RNG.random() < 0.25:
                        memo = "반죽 되직함, 오븐2 온도 편차 있는 듯"
                    elif dtype == "미성형" and RNG.random() < 0.2:
                        memo = "야간 성형 속도 문제로 보임"
                    quality.append((d.isoformat(), f"MO-{mo_n:06d}", pid, line, worker,
                                    equip, lot, SOPS[pid], dtype, qty_def, shift, memo,
                                    d.isoformat() + "T19:00:00"))
                moves.append((d.isoformat(), pid, "PROD", "WH", float(done), "production",
                              lot, "", d.isoformat() + "T18:30:00"))
        # 매장 출고 + 기한 폐기
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

    # ── 정비 이력 (P3: OVEN-2 고장 전 드리프트와 짝)
    maint = []
    for d, equip, etype, dur, note in [
        (date(2025, 3, 12), "OVEN-1", "예방 점검", 90, "정기"),
        (date(2025, 6, 20), "OVEN-2", "고장 수리", 320, "히터 소자 교체"),
        (date(2025, 9, 15), "OVEN-2", "예방 점검", 120, "온도 편차 조정"),
        (date(2026, 2, 10), "OVEN-1", "예방 점검", 90, "정기"),
        (date(2026, 6, 18), "OVEN-2", "고장 수리", 280, "컨베이어 베어링"),
    ]:
        maint.append((d.isoformat(), equip, etype, dur, note, d.isoformat() + "T10:00:00"))
    cur.executemany(
        "INSERT INTO maintenance_request (event_date, equipment_id, event_type, "
        "duration_min, note, write_date) VALUES (?,?,?,?,?,?)", maint)
    con.commit()
    con.close()

    # ── 센서 180일 (10분 주기) — P3 드리프트 포함, 고장 전 정상 구간 확보
    sensor_rows = []
    s_start = END - timedelta(days=180)
    fail2 = date(2026, 6, 18)
    for d in daterange(s_start, END):
        for hh in range(0, 24):
            for mm in (0, 10, 20, 30, 40, 50):
                ts = f"{d.isoformat()}T{hh:02d}:{mm:02d}:00"
                for equip in ("OVEN-1", "OVEN-2"):
                    drift = 0.0
                    if equip == "OVEN-2":
                        days_to_fail = (fail2 - d).days
                        if 0 <= days_to_fail <= 14:
                            drift = (14 - days_to_fail) / 14        # 고장 2주 전부터 상승
                    sensor_rows.append((ts, equip, "temp",
                                        round(210 + RNG.normal(0, 2.0) + drift * 8, 2)))
                    sensor_rows.append((ts, equip, "current",
                                        round(32 + RNG.normal(0, 0.8) + drift * 3, 2)))
                    sensor_rows.append((ts, equip, "vibration",
                                        round(0.8 + abs(RNG.normal(0, 0.1)) + drift * 0.9, 3)))
    pd.DataFrame(sensor_rows, columns=["reading_ts", "equipment_id", "signal", "value"]) \
        .to_csv(config.DATA / "sensor_replay.csv", index=False)

    # ── 엑셀 양식 2종 (업로더 시험용)
    xls_dir = config.DATA / "inbox"
    xls_dir.mkdir(parents=True, exist_ok=True)
    promo_xls = promos.copy()
    promo_xls["product_id"] = promo_xls["product_id"].map(lambda p: PRODUCTS[p][0])
    promo_xls.rename(columns={"date_start": "시작일", "date_end": "종료일",
                              "product_id": "제품코드", "promo_name": "행사명",
                              "discount_pct": "할인율"}) \
        .to_excel(xls_dir / "프로모션_달력.xlsx", index=False)   # 현실처럼 제품'명' 기입
    recent = [s for s in sales if s[1] >= (END - timedelta(days=14)).isoformat()
              and s[2] == "S-MAIN"]
    pd.DataFrame([{"판매일": r[1], "매장": r[2], "품목": r[3], "수량": r[4]} for r in recent]) \
        .to_excel(xls_dir / "본점_판매집계.xlsx", index=False)

    print(f"odoo.db: 판매 {len(sales):,} · 생산 {len(mrp):,} · 품질 {len(quality):,} · "
          f"이동 {len(moves):,} · 구매 {len(purchases):,} · 정비 {len(maint)}")
    print(f"센서 {len(sensor_rows):,}행 → sensor_replay.csv, 엑셀 2종 → inbox/")


if __name__ == "__main__":
    main()
