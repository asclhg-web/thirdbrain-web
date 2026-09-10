"""M4-2 수요예측 — 단순한 것부터: 평활(출발선) → GBDT(기본기).

규율:
  · 입력은 특징량 저장소(M2-3)만.
  · 검증은 시계열 분할(과거 학습→미래 검증) 롤링 — 무작위 셔플 금지.
  · 예측 구간(P10~P90)을 함께 산출 — 판단 카드의 '구간' 필드.
  · 단계별 지표 비교표를 남기고, 이긴 모델만 카드와 함께 등록한다.
딥러닝(TF 시계열)은 개선 여지가 수치로 확인될 때만 — DeepBackend 훅으로 접속.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from ..dataset import features
from . import cards

FEATURE_COLS = list(features.DEFINITIONS.keys())
CAT_COLS = ["store_id", "product_id"]


def _design(df: pd.DataFrame) -> pd.DataFrame:
    X = pd.get_dummies(df[CAT_COLS + FEATURE_COLS], columns=CAT_COLS, dtype=float)
    return X


def wape(y, yhat) -> float:
    y, yhat = np.asarray(y, float), np.asarray(yhat, float)
    return float(np.abs(y - yhat).sum() / max(np.abs(y).sum(), 1e-9))


def mape(y, yhat, floor: float = 5.0) -> float:
    """소량일 판매의 폭주 방지 — 분모 하한(floor) 있는 MAPE."""
    y, yhat = np.asarray(y, float), np.asarray(yhat, float)
    return float(np.mean(np.abs(y - yhat) / np.maximum(np.abs(y), floor)))


# ── 출발선: 평활 계열 ─────────────────────────────────────────────
def baseline_predict(df: pd.DataFrame, kind: str) -> pd.Series:
    if kind == "naive_dow":            # 지난주 같은 요일
        return df["lag_7"]
    if kind == "ma_7":
        return df["ma_7"]
    if kind == "ewm_7":
        return df["ewm_7"]
    raise ValueError(kind)


# ── 시계열 롤링 검증 ─────────────────────────────────────────────
def rolling_folds(dates: pd.Series, n_folds: int = 4, val_days: int = 28
                  ) -> list[tuple[str, str]]:
    """뒤에서부터 val_days 창 n_folds개 — (검증 시작일, 종료일)."""
    end = pd.Timestamp(dates.max())
    folds = []
    for i in range(n_folds):
        v_end = end - pd.Timedelta(days=i * val_days)
        v_start = v_end - pd.Timedelta(days=val_days - 1)
        folds.append((v_start.date().isoformat(), v_end.date().isoformat()))
    return list(reversed(folds))


def evaluate(as_of: str, n_folds: int = 4, val_days: int = 28) -> pd.DataFrame:
    """비교표 — 출발선 3종 vs GBDT. 폴드 평균 WAPE·MAPE."""
    df = features.load_frame(as_of)
    df = df[df["target"].notna()].copy()
    rows = []
    for v_start, v_end in rolling_folds(df["date_key"], n_folds, val_days):
        train = df[df["date_key"] < v_start]
        val = df[(df["date_key"] >= v_start) & (df["date_key"] <= v_end)]
        if len(train) < 1000 or val.empty:
            continue
        for kind in ("naive_dow", "ma_7", "ewm_7"):
            pred = baseline_predict(val, kind).fillna(0)
            rows.append({"model": kind, "fold": v_start,
                         "wape": wape(val["target"], pred),
                         "mape": mape(val["target"], pred)})
        model = HistGradientBoostingRegressor(
            max_iter=300, learning_rate=0.06, max_depth=6, random_state=0)
        model.fit(_design(train).fillna(0), train["target"])
        pred = model.predict(_design(val).fillna(0)).clip(min=0)
        rows.append({"model": "gbdt", "fold": v_start,
                     "wape": wape(val["target"], pred),
                     "mape": mape(val["target"], pred)})
    res = pd.DataFrame(rows)
    return res.groupby("model")[["wape", "mape"]].mean().sort_values("wape").reset_index()


# ── 학습·등록·예측 ───────────────────────────────────────────────
def train_and_register(as_of: str, version: str = "v1") -> dict:
    """최종 학습(as_of까지 전체) + 분위수 모델(P10·P90) + 카드 등록."""
    df = features.load_frame(as_of)
    train = df[df["target"].notna()]
    comparison = evaluate(as_of)
    X, y = _design(train).fillna(0), train["target"]

    mid = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.06,
                                        max_depth=6, random_state=0).fit(X, y)
    lo = HistGradientBoostingRegressor(loss="quantile", quantile=0.1, max_iter=200,
                                       random_state=0).fit(X, y)
    hi = HistGradientBoostingRegressor(loss="quantile", quantile=0.9, max_iter=200,
                                       random_state=0).fit(X, y)
    bundle = {"mid": mid, "lo": lo, "hi": hi, "columns": list(X.columns)}

    best = comparison.iloc[0]
    baseline_row = comparison[comparison["model"] == "ewm_7"].iloc[0]
    card = {
        "model_id": "demand_forecast",
        "problem": "일×매장×제품 수요예측 (수직 완주 유스케이스)",
        "data_range": f"~{as_of}",
        "features_ref": f"features_demand {features.VERSION} (20종)",
        "algorithm": "HistGradientBoosting 회귀 + 분위수(P10/P90)",
        "params": {"max_iter": 300, "learning_rate": 0.06, "max_depth": 6},
        "metrics": {"wape": round(float(best["wape"]), 4),
                    "mape": round(float(best["mape"]), 4),
                    "baseline_ewm_wape": round(float(baseline_row["wape"]), 4)},
        "validation_scheme": "시계열 롤링 4폴드 × 28일 (셔플 금지)",
        "version": version,
        "comparison": comparison.to_dict("records"),
    }
    reg = cards.register(card, bundle)
    cards.promote("demand_forecast", version)
    return {"card": card, "registered": reg, "comparison": comparison}


def predict(as_of: str, horizon: int = 7) -> pd.DataFrame:
    """서빙 예측 — 특징 저장소의 미래 행 입력, P10/P50/P90 반환."""
    card, bundle = cards.serving("demand_forecast")
    df = features.load_frame(as_of)
    fut = df[df["target"].isna()].copy()
    if fut.empty:
        raise ValueError("미래 행 없음 — features.materialize(as_of, horizon>0) 먼저")
    X = _design(fut).fillna(0)
    for c in bundle["columns"]:
        if c not in X.columns:
            X[c] = 0.0
    X = X[bundle["columns"]]
    fut["p50"] = bundle["mid"].predict(X).clip(min=0).round(1)
    fut["p10"] = np.minimum(bundle["lo"].predict(X).clip(min=0), fut["p50"]).round(1)
    fut["p90"] = np.maximum(bundle["hi"].predict(X).clip(min=0), fut["p50"]).round(1)
    out = fut[["date_key", "store_id", "product_id", "p10", "p50", "p90"]]
    return out.sort_values(["date_key", "store_id", "product_id"]).reset_index(drop=True)
