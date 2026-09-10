"""M2-3 특징량 저장소 — 정의 사전 + 시점 안전(point-in-time) 재현 생성.

규율: 모든 특징은 정의를 가진다. 생성은 기준 시점(as_of)을 인자로 받아
그 시점에 알 수 있던 값만 쓴다. M4는 이 저장소에서만 입력을 받는다.
수요예측 특징 20종 — 프로모션·명절은 '사전 인지' 특징(계획이므로 미래 참조 허용,
정의에 명시).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .. import db

# ── 정의 사전 (레지스트리 계약 features_demand.yaml 과 1:1) ──────────────
DEFINITIONS: dict[str, dict] = {
    "lag_1":            {"desc": "1일 전 판매량", "inputs": ["fact_sales.qty"], "pit": "past"},
    "lag_7":            {"desc": "7일 전 판매량", "inputs": ["fact_sales.qty"], "pit": "past"},
    "lag_14":           {"desc": "14일 전 판매량", "inputs": ["fact_sales.qty"], "pit": "past"},
    "ma_7":             {"desc": "직전 7일 이동평균", "inputs": ["fact_sales.qty"], "pit": "past"},
    "ma_14":            {"desc": "직전 14일 이동평균", "inputs": ["fact_sales.qty"], "pit": "past"},
    "ma_28":            {"desc": "직전 28일 이동평균", "inputs": ["fact_sales.qty"], "pit": "past"},
    "ewm_7":            {"desc": "지수평활(span=7)", "inputs": ["fact_sales.qty"], "pit": "past"},
    "std_14":           {"desc": "직전 14일 표준편차(변동성)", "inputs": ["fact_sales.qty"], "pit": "past"},
    "same_dow_ma_4":    {"desc": "같은 요일 최근 4회 평균", "inputs": ["fact_sales.qty"], "pit": "past"},
    "dow":              {"desc": "요일(0=월)", "inputs": ["dim_calendar.dow"], "pit": "known"},
    "is_weekend":       {"desc": "주말 여부", "inputs": ["dim_calendar"], "pit": "known"},
    "month":            {"desc": "월", "inputs": ["dim_calendar"], "pit": "known"},
    "seasonal_idx":     {"desc": "요일×월 계절지수(과거 판매/전체 평균)", "inputs": ["fact_sales"], "pit": "past"},
    "is_holiday_week":  {"desc": "명절 주간(사전 인지)", "inputs": ["dim_calendar"], "pit": "planned"},
    "promo_flag":       {"desc": "프로모션 여부(사전 인지 — 행사 계획)", "inputs": ["dim_promo"], "pit": "planned"},
    "days_since_start": {"desc": "데이터 시작 후 경과일(추세)", "inputs": ["dim_calendar"], "pit": "known"},
    "scrap_rate_7":     {"desc": "직전 7일 폐기율(공급 과잉 신호)", "inputs": ["fact_inventory_move"], "pit": "past"},
    "unit_price":       {"desc": "단가", "inputs": ["dim_product"], "pit": "known"},
    "channel_b2b":      {"desc": "B2B 채널 여부", "inputs": ["dim_store.channel"], "pit": "known"},
    "lag_364":          {"desc": "364일 전(작년 같은 요일) 판매량", "inputs": ["fact_sales.qty"], "pit": "past"},
}

VERSION = "v1.0"
OWNER = "ML 엔지니어"

DDL = """
CREATE TABLE IF NOT EXISTS feature_store_demand (
  as_of TEXT NOT NULL, date_key TEXT NOT NULL,
  store_id TEXT NOT NULL, product_id TEXT NOT NULL,
  features TEXT NOT NULL,          -- JSON {특징: 값}
  target REAL,                     -- 해당 일 실제 판매(학습용, as_of 이후는 NULL)
  PRIMARY KEY (as_of, date_key, store_id, product_id)
);
"""


def definitions() -> dict:
    return {"version": VERSION, "owner": OWNER, "features": DEFINITIONS}


def _grid(sales: pd.DataFrame) -> pd.DataFrame:
    """(date, store, product) 완전 격자 — 판매 0일도 행으로(결측=0 판매)."""
    dates = pd.date_range(sales["date_key"].min(), sales["date_key"].max(), freq="D")
    pairs = sales[["store_id", "product_id"]].drop_duplicates()
    grid = pairs.merge(pd.DataFrame({"date_key": dates.strftime("%Y-%m-%d")}), how="cross")
    g = grid.merge(sales, on=["date_key", "store_id", "product_id"], how="left")
    g["qty"] = g["qty"].fillna(0.0)
    return g.sort_values(["store_id", "product_id", "date_key"]).reset_index(drop=True)


def build(as_of: str, horizon: int = 0) -> pd.DataFrame:
    """특징 생성 — as_of까지의 사실만 사용. horizon>0이면 미래 date_key 행도
    생성(예측 입력용 — past 특징은 as_of 시점 값으로 고정된다)."""
    sales = db.df(
        "SELECT date_key, store_id, product_id, qty FROM fact_sales WHERE date_key <= ?",
        (as_of,))
    if sales.empty:
        raise ValueError("fact_sales 비어 있음 — M2 변환을 먼저 실행")
    cal = db.df("SELECT * FROM dim_calendar")
    promo = db.df("SELECT * FROM dim_promo") if db.table_exists("dim_promo") else pd.DataFrame()
    prod = db.df("SELECT product_id, unit_price FROM dim_product")
    stores = db.df("SELECT store_id, channel FROM dim_store")
    scrap = db.df(
        "SELECT date_key, product_id, SUM(qty) AS scrap_qty FROM fact_inventory_move "
        "WHERE move_type='scrap' AND date_key <= ? GROUP BY date_key, product_id", (as_of,))

    g = _grid(sales)
    if horizon > 0:
        future_dates = pd.date_range(pd.Timestamp(as_of) + pd.Timedelta(days=1),
                                     periods=horizon, freq="D").strftime("%Y-%m-%d")
        pairs = g[["store_id", "product_id"]].drop_duplicates()
        fut = pairs.merge(pd.DataFrame({"date_key": future_dates}), how="cross")
        fut["qty"] = np.nan
        g = pd.concat([g, fut], ignore_index=True) \
            .sort_values(["store_id", "product_id", "date_key"]).reset_index(drop=True)

    grp = g.groupby(["store_id", "product_id"], group_keys=False)
    q = g["qty"]
    g["lag_1"] = grp["qty"].shift(1)
    g["lag_7"] = grp["qty"].shift(7)
    g["lag_14"] = grp["qty"].shift(14)
    g["lag_364"] = grp["qty"].shift(364)
    g["ma_7"] = grp["qty"].apply(lambda s: s.shift(1).rolling(7, min_periods=3).mean())
    g["ma_14"] = grp["qty"].apply(lambda s: s.shift(1).rolling(14, min_periods=5).mean())
    g["ma_28"] = grp["qty"].apply(lambda s: s.shift(1).rolling(28, min_periods=7).mean())
    g["ewm_7"] = grp["qty"].apply(lambda s: s.shift(1).ewm(span=7, min_periods=3).mean())
    g["std_14"] = grp["qty"].apply(lambda s: s.shift(1).rolling(14, min_periods=5).std())
    g["same_dow_ma_4"] = grp["qty"].apply(
        lambda s: s.shift(7).rolling(28, min_periods=7).mean())   # 근사: 최근 4주 같은 요일

    # 미래 행의 past 특징은 미래 실측을 참조할 수 없다 — shift 계열은 이미 NaN이
    # 전파되므로 마지막 관측값으로 채운다(예측 시점 고정).
    past_cols = ["lag_1", "lag_7", "lag_14", "lag_364", "ma_7", "ma_14", "ma_28",
                 "ewm_7", "std_14", "same_dow_ma_4"]
    g[past_cols] = grp[past_cols].apply(lambda df_: df_.ffill())

    g = g.merge(cal, on="date_key", how="left")
    dt = pd.to_datetime(g["date_key"])
    g["dow"] = g["dow"].fillna(dt.dt.dayofweek)
    g["month"] = g["month"].fillna(dt.dt.month)
    g["is_weekend"] = g["is_weekend"].fillna((dt.dt.dayofweek >= 5).astype(int))
    g["is_holiday_week"] = g["is_holiday_week"].fillna(0)
    g["days_since_start"] = (dt - dt.min()).dt.days

    # 계절지수 — as_of 이전 데이터만으로 (dow, month)별 평균/전체 평균
    hist = g[g["date_key"] <= as_of]
    base = hist.groupby(["store_id", "product_id"])["qty"].mean().rename("base_mean")
    seas = hist.groupby(["store_id", "product_id", "dow", "month"])["qty"].mean().rename("cell_mean")
    seas = seas.reset_index().merge(base.reset_index(), on=["store_id", "product_id"])
    seas["seasonal_idx"] = seas["cell_mean"] / seas["base_mean"].replace(0, np.nan)
    g = g.merge(seas[["store_id", "product_id", "dow", "month", "seasonal_idx"]],
                on=["store_id", "product_id", "dow", "month"], how="left")
    g["seasonal_idx"] = g["seasonal_idx"].fillna(1.0)

    # 프로모션(사전 인지)
    g["promo_flag"] = 0
    for r in (promo.itertuples() if len(promo) else []):
        m = ((g["product_id"] == r.product_id) & (g["date_key"] >= r.date_start)
             & (g["date_key"] <= r.date_end))
        g.loc[m, "promo_flag"] = 1

    # 폐기율(직전 7일, 제품 단위)
    if len(scrap):
        sc = scrap.pivot_table(index="date_key", columns="product_id",
                               values="scrap_qty", aggfunc="sum").sort_index()
        sc = sc.rolling(7, min_periods=1).sum().stack().rename("scrap_7").reset_index()
        g = g.merge(sc, on=["date_key", "product_id"], how="left")
        g["scrap_rate_7"] = (g["scrap_7"].fillna(0)
                             / g["ma_7"].replace(0, np.nan).fillna(1) / 7).clip(0, 1)
        g = g.drop(columns=["scrap_7"])
    else:
        g["scrap_rate_7"] = 0.0

    g = g.merge(prod, on="product_id", how="left")
    g = g.merge(stores, on="store_id", how="left")
    g["channel_b2b"] = (g["channel"] == "B2B").astype(int)

    feat_cols = list(DEFINITIONS.keys())
    g["target"] = g["qty"]
    out = g[["date_key", "store_id", "product_id", "target"] + feat_cols].copy()
    out.insert(0, "as_of", as_of)
    return out


def materialize(as_of: str, horizon: int = 0) -> int:
    """저장소에 적재 — 같은 as_of 재실행 시 동일 결과(멱등)."""
    db.executescript(DDL)
    frame = build(as_of, horizon)
    import json
    feat_cols = list(DEFINITIONS.keys())
    rows = [(r["as_of"], r["date_key"], r["store_id"], r["product_id"],
             json.dumps({c: (None if pd.isna(r[c]) else float(r[c])) for c in feat_cols}),
             None if pd.isna(r["target"]) else float(r["target"]))
            for _, r in frame.iterrows()]
    db.execute("DELETE FROM feature_store_demand WHERE as_of=?", (as_of,))
    db.executemany(
        "INSERT INTO feature_store_demand VALUES (?,?,?,?,?,?)", rows)
    return len(rows)


def load_frame(as_of: str) -> pd.DataFrame:
    """M4 전용 입구 — 저장소에서 학습 프레임 반환."""
    import json
    rows = db.query("SELECT * FROM feature_store_demand WHERE as_of=?", (as_of,))
    if not rows:
        raise ValueError(f"특징 미생성: as_of={as_of} — materialize 먼저")
    recs = []
    for r in rows:
        rec = {"date_key": r["date_key"], "store_id": r["store_id"],
               "product_id": r["product_id"], "target": r["target"]}
        rec.update(json.loads(r["features"]))
        recs.append(rec)
    return pd.DataFrame(recs)
