"""M3-2 야간 마이닝 배치 — 4M 조합별 불량률 + 변화 탐지.

산출 두 갈래:
  1) mining_candidates — 통계적으로 유의한 4M 조합(연관 후보) → M5의 CAUSAL_CANDIDATE 입력 큐
  2) 변화 탐지 상위 N → 아침 브리핑
원칙: 원인 단정 금지 — '~와 함께 나타났다'까지만. 판단은 그래프·사람의 몫.
"""
from __future__ import annotations

import itertools
import json
import math

import pandas as pd

from .. import common, db

DDL = """
CREATE TABLE IF NOT EXISTS mining_candidates (
  cand_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_date TEXT NOT NULL,
  dims TEXT NOT NULL,             -- JSON {차원: 값}
  window_start TEXT, window_end TEXT,
  n_produced REAL, n_defect REAL,
  rate REAL, base_rate REAL, lift REAL, z REAL,
  status TEXT DEFAULT 'new'       -- new | sent_to_graph
);
CREATE TABLE IF NOT EXISTS mining_changes (
  run_date TEXT NOT NULL, rank INTEGER,
  what TEXT, value REAL, prev REAL, delta_pct REAL, where_4m TEXT,
  PRIMARY KEY (run_date, rank)
);
"""

DIMS_1 = ["equipment_id", "worker_id", "sop_id", "shift", "product_id"]
DIMS_2 = [("equipment_id", "vendor"), ("worker_id", "shift"),
          ("equipment_id", "product_id"), ("sop_id", "shift")]
MIN_N = 500          # 조합 최소 생산량 — 소표본 잡음 배제
Z_THRESHOLD = 3.0    # 유의 기준


def _two_prop_z(x1: float, n1: float, x0: float, n0: float) -> float:
    """조합 불량률 vs 나머지 불량률의 2-표본 비율 z."""
    if n1 <= 0 or n0 <= 0:
        return 0.0
    p1, p0 = x1 / n1, x0 / n0
    p = (x1 + x0) / (n1 + n0)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n0))
    return 0.0 if se == 0 else (p1 - p0) / se


def _base_frame(start: str, end: str) -> pd.DataFrame:
    df = db.df("""
        SELECT p.mo_ref, p.date_key, p.shift, p.product_id, p.line_id, p.worker_id,
               p.equipment_id, p.sop_id, p.qty_planned,
               COALESCE(d.qty_defect, 0) AS qty_defect, d.material_lot_id
        FROM fact_production p LEFT JOIN fact_defect d USING (mo_ref)
        WHERE p.date_key BETWEEN ? AND ?""", (start, end))
    lots = db.df("SELECT lot_id, vendor_id AS vendor FROM dim_material_lot")
    return df.merge(lots, left_on="material_lot_id", right_on="lot_id", how="left")


def nightly(run_date: str, window_days: int = 56) -> dict:
    """야간 배치 — 최근 window 구간의 조합 탐색 + 전일/전주 변화."""
    db.executescript(DDL)
    end = run_date
    start = (pd.Timestamp(run_date) - pd.Timedelta(days=window_days)).date().isoformat()
    df = _base_frame(start, end)
    if df.empty:
        return {"candidates": 0, "changes": 0}
    total_prod, total_def = df["qty_planned"].sum(), df["qty_defect"].sum()

    combos: list[dict] = []
    dim_sets = [(d,) for d in DIMS_1] + list(DIMS_2)
    for dims in dim_sets:
        dims = list(dims)
        g = df.groupby(dims)[["qty_planned", "qty_defect"]].sum().reset_index()
        for _, r in g.iterrows():
            n1, x1 = r["qty_planned"], r["qty_defect"]
            if n1 < MIN_N:
                continue
            z = _two_prop_z(x1, n1, total_def - x1, total_prod - n1)
            if z >= Z_THRESHOLD:
                base = (total_def - x1) / (total_prod - n1)
                combos.append({
                    "dims": {d: r[d] for d in dims if pd.notna(r[d])},
                    "n_produced": float(n1), "n_defect": float(x1),
                    "rate": float(x1 / n1), "base_rate": float(base),
                    "lift": float((x1 / n1) / base) if base > 0 else 0.0,
                    "z": float(z),
                })
    combos.sort(key=lambda c: -c["z"])
    db.execute("DELETE FROM mining_candidates WHERE run_date=?", (run_date,))
    db.executemany(
        "INSERT INTO mining_candidates (run_date, dims, window_start, window_end, "
        "n_produced, n_defect, rate, base_rate, lift, z) VALUES (?,?,?,?,?,?,?,?,?,?)",
        [(run_date, json.dumps(c["dims"], ensure_ascii=False), start, end,
          c["n_produced"], c["n_defect"], c["rate"], c["base_rate"], c["lift"], c["z"])
         for c in combos])

    changes = detect_changes(run_date)
    return {"candidates": len(combos), "changes": len(changes),
            "top": combos[:5], "window": (start, end)}


def detect_changes(run_date: str, top_n: int = 5) -> list[dict]:
    """전일 대비 변화 상위 N — 지표: 폐기·불량·판매의 급변, 관리도 이탈."""
    db.executescript(DDL)
    prev = (pd.Timestamp(run_date) - pd.Timedelta(days=1)).date().isoformat()
    week_ago = (pd.Timestamp(run_date) - pd.Timedelta(days=7)).date().isoformat()
    rows: list[dict] = []

    def add(what, today, base, where=""):
        if base and base > 0:
            delta = (today - base) / base * 100
            if abs(delta) >= 25 and abs(today - base) >= 5:
                rows.append({"what": what, "value": float(today), "prev": float(base),
                             "delta_pct": round(delta, 1), "where_4m": where})

    for metric, sql, label in [
        ("폐기", "SELECT COALESCE(SUM(qty),0) FROM fact_inventory_move WHERE move_type='scrap' AND date_key=?", ""),
        ("불량", "SELECT COALESCE(SUM(qty_defect),0) FROM fact_defect WHERE date_key=?", ""),
        ("판매", "SELECT COALESCE(SUM(qty),0) FROM fact_sales WHERE date_key=?", ""),
    ]:
        today = db.scalar(sql, (run_date,)) or 0
        base = db.scalar(sql, (prev,)) or 0
        add(f"{metric}(전일 대비)", today, base)

    # 제품×라인 불량 급변 (전주 같은 요일 대비)
    t = db.df("SELECT product_id, line_id, SUM(qty_defect) AS v FROM fact_defect "
              "WHERE date_key=? GROUP BY product_id, line_id", (run_date,))
    b = db.df("SELECT product_id, line_id, SUM(qty_defect) AS v FROM fact_defect "
              "WHERE date_key=? GROUP BY product_id, line_id", (week_ago,))
    m = t.merge(b, on=["product_id", "line_id"], suffixes=("", "_prev"), how="left").fillna(0)
    for _, r in m.iterrows():
        add(f"불량 {r['product_id']}(전주 동요일)", r["v"], r["v_prev"],
            where=f"line={r['line_id']}")

    rows.sort(key=lambda r: -abs(r["delta_pct"]))
    rows = rows[:top_n]
    db.execute("DELETE FROM mining_changes WHERE run_date=?", (run_date,))
    db.executemany(
        "INSERT INTO mining_changes VALUES (?,?,?,?,?,?,?)",
        [(run_date, i + 1, r["what"], r["value"], r["prev"], r["delta_pct"], r["where_4m"])
         for i, r in enumerate(rows)])
    return rows


def new_candidates() -> list[dict]:
    """M5로 보낼 신규 후보."""
    db.executescript(DDL)
    rows = db.query("SELECT * FROM mining_candidates WHERE status='new' ORDER BY z DESC")
    for r in rows:
        r["dims"] = json.loads(r["dims"])
    return rows


def mark_sent(cand_ids: list[int]) -> None:
    db.executemany(
        "UPDATE mining_candidates SET status='sent_to_graph' WHERE cand_id=?",
        [(i,) for i in cand_ids])
