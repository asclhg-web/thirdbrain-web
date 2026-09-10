"""OP-3 주간 재학습 자동화 — 판정 → 재학습 → 그림자 비교 → 승격 게이트.

규율:
  · 재학습 사유가 있어야 재학습한다(드리프트 경보 2+ 또는 최근 WAPE 하한 초과).
  · 새 버전은 등록만 — 그림자 비교(최근 28일 홀드아웃)에서 이겨야 승격.
  · 모든 결정은 retrain_log에 수치 근거와 함께 남는다.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .. import common, db
from ..dataset import features
from . import cards, drift, forecast

WAPE_FLOOR = 0.12          # 성능 하한(G3 합의 초안)
DRIFT_ALERTS_TRIGGER = 2

DDL = """
CREATE TABLE IF NOT EXISTS retrain_log (
  run_at TEXT, as_of TEXT, decision TEXT, reason TEXT,
  old_version TEXT, new_version TEXT, old_wape REAL, new_wape REAL, promoted INTEGER
);
"""


def recent_wape(as_of: str, days: int = 28) -> float:
    """서빙 모델의 최근 holdout WAPE — as_of 이전 days일을 홀드아웃으로 재현."""
    cut = (pd.Timestamp(as_of) - pd.Timedelta(days=days)).date().isoformat()
    df = features.load_frame(as_of)
    hold = df[(df["date_key"] > cut) & df["target"].notna()]
    if hold.empty:
        return float("nan")
    card, bundle = cards.serving("demand_forecast")
    X = forecast._design(hold).fillna(0)
    for c in bundle["columns"]:
        if c not in X.columns:
            X[c] = 0.0
    pred = bundle["mid"].predict(X[bundle["columns"]]).clip(min=0)
    return forecast.wape(hold["target"], pred)


def weekly(as_of: str) -> dict:
    """주간 진입점 — 판정과 실행을 한 번에."""
    db.executescript(DDL)
    dr = drift.input_drift(as_of)
    n_alerts = int((dr["level"] == "경보").sum()) if len(dr) else 0
    cur_card = cards.get_card("demand_forecast") or {}
    old_ver = cur_card.get("version", "?")
    old_wape = recent_wape(as_of)

    reasons = []
    if n_alerts >= DRIFT_ALERTS_TRIGGER:
        reasons.append(f"드리프트 경보 {n_alerts}건")
    if not np.isnan(old_wape) and old_wape > WAPE_FLOOR:
        reasons.append(f"최근 28일 WAPE {old_wape:.1%} > 하한 {WAPE_FLOOR:.0%}")

    if not reasons:
        db.execute("INSERT INTO retrain_log VALUES (?,?,?,?,?,?,?,?,?)",
                   (common.now_iso(), as_of, "keep", "재학습 사유 없음",
                    old_ver, None, round(old_wape, 4), None, 0))
        return {"decision": "keep", "old_wape": round(old_wape, 4),
                "drift_alerts": n_alerts}

    # 재학습 — 다음 버전 번호로 등록만(승격은 게이트 통과 시)
    new_ver = f"v{int(old_ver.lstrip('v') or 1) + 1}"
    features.materialize(as_of, horizon=7)
    res = forecast.train_and_register(as_of, version=new_ver)   # register+promote
    # train_and_register는 promote까지 하므로, 게이트 판정을 위해 비교 후 되돌릴 수 있다
    new_wape = recent_wape(as_of)
    promoted = new_wape <= old_wape or np.isnan(old_wape)
    if not promoted:                                   # 게이트 불통과 → 롤백
        cards.promote("demand_forecast", old_ver)
    db.execute("INSERT INTO retrain_log VALUES (?,?,?,?,?,?,?,?,?)",
               (common.now_iso(), as_of, "retrain", "; ".join(reasons),
                old_ver, new_ver, round(old_wape, 4), round(new_wape, 4),
                int(promoted)))
    common.alert("info", "OP-3",
                 f"재학습 {new_ver}: {'승격' if promoted else f'게이트 불통과 — {old_ver} 유지'} "
                 f"(구 {old_wape:.1%} vs 신 {new_wape:.1%})")
    return {"decision": "retrain", "reasons": reasons, "old": old_ver,
            "new": new_ver, "old_wape": round(old_wape, 4),
            "new_wape": round(new_wape, 4), "promoted": promoted}
