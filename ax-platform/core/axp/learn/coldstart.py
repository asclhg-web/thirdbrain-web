"""P2-C3: 신제품 콜드스타트 — 유사 품목 전이 예측.

베이커리 신제품은 이력이 0~4주뿐이라 GBDT가 학습할 수 없다. 원칙:
  1) 공여 품목(donor) 선택 — 지정 > 같은 라인 > 판매 패턴 상관 최고.
  2) 규모 보정 — 신제품의 관측 일평균 / 공여 품목 같은 기간 일평균.
     이력이 전무하면 출시 보수 계수(기본 0.6)를 쓴다.
  3) 불확실성 정직 표기 — 구간을 통상보다 넓게(P10 ×0.7, P90 ×1.5),
     카드 근거에 '콜드스타트(공여: X, 배율 r)'를 명시한다.
판정: 이력이 MIN_HISTORY(28일) 이상 쌓이면 자동으로 본 모델로 넘어간다.
"""
from __future__ import annotations

import pandas as pd

from .. import db

MIN_HISTORY = 28          # 이 미만이면 콜드스타트 대상
DONOR_MIN_DAYS = 120      # 공여 자격: 최소 이력
LAUNCH_RATIO = 0.6        # 이력 전무 시 보수 계수


def history_days(product_id: str) -> int:
    return db.scalar(
        "SELECT COUNT(DISTINCT date_key) FROM fact_sales WHERE product_id=?",
        (product_id,)) or 0


def needs_cold_start(product_id: str) -> bool:
    return history_days(product_id) < MIN_HISTORY


def _daily(product_id: str, start: str, end: str) -> pd.Series:
    df = db.df(
        "SELECT date_key, SUM(qty) qty FROM fact_sales "
        "WHERE product_id=? AND date_key BETWEEN ? AND ? GROUP BY date_key",
        (product_id, start, end))
    if df.empty:
        return pd.Series(dtype=float)
    return df.set_index("date_key")["qty"].astype(float)


def pick_donor(product_id: str, as_of: str, prefer: str | None = None) -> str:
    """공여 품목 — 지정 > 같은 라인 > 최근 90일 패턴 상관 최고."""
    if prefer:
        return prefer
    cands = [r["product_id"] for r in db.query(
        "SELECT product_id, COUNT(DISTINCT date_key) d FROM fact_sales "
        "WHERE product_id != ? GROUP BY product_id HAVING COUNT(DISTINCT date_key) >= ?",
        (product_id, DONOR_MIN_DAYS))]
    if not cands:
        raise ValueError("공여 자격(이력 120일+) 품목이 없다 — 콜드스타트 불가")
    try:  # 프로파일의 같은 라인 우선
        from .. import profile_rt
        line = profile_rt.line_of(product_id)
        same = [c for c in cands if profile_rt.line_of(c) == line]
        if same:
            cands = same
    except Exception:
        pass
    if len(cands) == 1:
        return cands[0]
    # 신제품 이력이 조금이라도 있으면 겹치는 날짜의 상관으로 고른다
    start = (pd.Timestamp(as_of) - pd.Timedelta(days=90)).date().isoformat()
    mine = _daily(product_id, start, as_of)
    best, best_r = cands[0], -2.0
    for c in cands:
        other = _daily(c, start, as_of)
        if len(mine) >= 7:
            j = mine.align(other, join="inner")
            r = j[0].corr(j[1]) if len(j[0]) >= 7 else -1.0
        else:
            r = float(other.mean())  # 이력 전무: 판매량 최대 품목
        if r is not None and r > best_r:
            best, best_r = c, r
    return best


def forecast(product_id: str, as_of: str, horizon: int = 7,
             donor: str | None = None) -> dict:
    """콜드스타트 예측 — 일별 수량 + 넓은 구간 + 근거 문자열."""
    donor = pick_donor(product_id, as_of, prefer=donor)
    start = (pd.Timestamp(as_of) - pd.Timedelta(days=28)).date().isoformat()
    d_hist = _daily(donor, start, as_of)
    if d_hist.empty:
        raise ValueError(f"공여 품목 {donor}의 최근 이력이 없다")
    mine = _daily(product_id, start, as_of)
    if len(mine) >= 5:
        joined = mine.align(d_hist, join="inner")
        ratio = float(joined[0].mean() / max(joined[1].mean(), 1e-9))
        ratio_src = f"관측 {len(mine)}일 배율"
    else:
        ratio = LAUNCH_RATIO
        ratio_src = f"출시 보수 계수 {LAUNCH_RATIO}"
    # 공여 품목의 요일 패턴을 그대로 전이
    dow_mean = d_hist.groupby(pd.to_datetime(d_hist.index).dayofweek).mean()
    days = pd.date_range(pd.Timestamp(as_of) + pd.Timedelta(days=1), periods=horizon)
    daily = [{"date_key": d.date().isoformat(),
              "p50": round(float(dow_mean.get(d.dayofweek, d_hist.mean())) * ratio, 1)}
             for d in days]
    total = round(sum(r["p50"] for r in daily), 1)
    return {
        "product_id": product_id, "donor": donor, "ratio": round(ratio, 3),
        "daily": daily,
        "total_p50": total,
        "total_p10": round(total * 0.7, 1),   # 정직한 광폭 구간
        "total_p90": round(total * 1.5, 1),
        "evidence": (f"콜드스타트: 공여 {donor} 요일 패턴 × 배율 {round(ratio,3)}"
                     f"({ratio_src}) — 이력 {history_days(product_id)}일 < {MIN_HISTORY}일"),
    }
