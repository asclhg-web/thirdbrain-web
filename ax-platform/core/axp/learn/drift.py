"""M4-1 드리프트 감지 — 입력 분포(PSI)·성능 주간 비교."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..dataset import features


def psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """Population Stability Index — 0.1 주의, 0.25 경보."""
    expected, actual = np.asarray(expected, float), np.asarray(actual, float)
    qs = np.quantile(expected[~np.isnan(expected)], np.linspace(0, 1, bins + 1))
    qs[0], qs[-1] = -np.inf, np.inf
    e_pct = np.histogram(expected, qs)[0] / max(len(expected), 1)
    a_pct = np.histogram(actual, qs)[0] / max(len(actual), 1)
    e_pct, a_pct = np.clip(e_pct, 1e-4, None), np.clip(a_pct, 1e-4, None)
    return float(np.sum((a_pct - e_pct) * np.log(a_pct / e_pct)))


def input_drift(as_of: str, ref_days: int = 84, cur_days: int = 14) -> pd.DataFrame:
    """특징별 PSI — 기준 구간(예: 직전 12주) vs 최근 2주."""
    df = features.load_frame(as_of)
    df = df[df["target"].notna()]
    end = pd.Timestamp(as_of)
    cur_start = (end - pd.Timedelta(days=cur_days)).date().isoformat()
    ref_start = (end - pd.Timedelta(days=ref_days + cur_days)).date().isoformat()
    ref = df[(df["date_key"] >= ref_start) & (df["date_key"] < cur_start)]
    cur = df[df["date_key"] >= cur_start]
    calendar_feats = {"days_since_start", "month", "dow", "is_weekend",
                      "is_holiday_week", "promo_flag"}   # 달력·계획 특징은 당연히 이동 — 제외
    rows = []
    for f in features.DEFINITIONS:
        if f in calendar_feats or ref[f].nunique() < 3:
            continue
        v = psi(ref[f].values, cur[f].values)
        rows.append({"feature": f, "psi": round(v, 4),
                     "level": "경보" if v > 0.25 else ("주의" if v > 0.1 else "정상")})
    return pd.DataFrame(rows).sort_values("psi", ascending=False).reset_index(drop=True)
