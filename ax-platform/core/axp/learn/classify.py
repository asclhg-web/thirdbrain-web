"""M4-2 불량분류 — 로지스틱(설명 쉬움) → GBDT(1순위 실전).

문제: 제조오더의 조건(4M)으로 고불량 위험을 사전 분류.
검증: 시간 분할(과거 학습 → 미래 검증). 임계는 비용 관점으로 스튜어드와 합의.
특징 중요도 상위는 M5의 원인 후보(CAUSAL_CANDIDATE) 입력이 된다.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.inspection import permutation_importance

from .. import db
from . import cards

CAT = ["product_id", "line_id", "worker_id", "equipment_id", "sop_id", "shift", "vendor"]
HIGH_DEFECT = 0.03          # 불량률 3% 이상 = 고불량 MO


def _frame(start: str, end: str) -> pd.DataFrame:
    df = db.df("""
        SELECT p.mo_ref, p.date_key, p.shift, p.product_id, p.line_id, p.worker_id,
               p.equipment_id, p.sop_id, p.qty_planned,
               COALESCE(d.qty_defect,0) AS qty_defect, d.material_lot_id
        FROM fact_production p LEFT JOIN fact_defect d USING (mo_ref)
        WHERE p.date_key BETWEEN ? AND ?""", (start, end))
    lots = db.df("SELECT lot_id, vendor_id AS vendor FROM dim_material_lot")
    df = df.merge(lots, left_on="material_lot_id", right_on="lot_id", how="left")
    df["y"] = (df["qty_defect"] / df["qty_planned"].clip(lower=1) >= HIGH_DEFECT).astype(int)
    return df


def _design(df: pd.DataFrame) -> pd.DataFrame:
    return pd.get_dummies(df[CAT + ["qty_planned"]], columns=CAT, dtype=float)


def train_and_register(start: str, split: str, end: str, version: str = "v1") -> dict:
    """start~split 학습, split~end 검증(시간 분할)."""
    df = _frame(start, end)
    train, val = df[df["date_key"] < split], df[df["date_key"] >= split]
    Xtr, Xv = _design(train), _design(val)
    Xv = Xv.reindex(columns=Xtr.columns, fill_value=0.0)
    ytr, yv = train["y"], val["y"]

    logit = LogisticRegression(max_iter=2000).fit(Xtr.fillna(0), ytr)
    auc_logit = roc_auc_score(yv, logit.predict_proba(Xv.fillna(0))[:, 1])
    gbdt = HistGradientBoostingClassifier(max_iter=200, random_state=0).fit(Xtr.fillna(0), ytr)
    auc_gbdt = roc_auc_score(yv, gbdt.predict_proba(Xv.fillna(0))[:, 1])

    winner = "gbdt" if auc_gbdt >= auc_logit else "logistic"
    win_model = gbdt if winner == "gbdt" else logit
    p_win = win_model.predict_proba(Xv.fillna(0))[:, 1]

    # 임계 — 미탐 비용 > 오탐 비용 가정: 재현율 0.7 이상에서 정밀도 최대(합의 초안)
    best_thr, best_prec = 0.5, 0
    for thr in np.arange(0.05, 0.9, 0.05):
        pred = (p_win >= thr).astype(int)
        tn, fp, fn, tp = confusion_matrix(yv, pred).ravel()
        rec = tp / max(tp + fn, 1)
        prec = tp / max(tp + fp, 1)
        if rec >= 0.7 and prec > best_prec:
            best_thr, best_prec = float(thr), float(prec)

    imp = permutation_importance(win_model, Xv.fillna(0), yv, n_repeats=3, random_state=0)
    top = sorted(zip(Xtr.columns, imp.importances_mean), key=lambda t: -t[1])[:10]
    card = {
        "model_id": "defect_classifier",
        "problem": f"제조오더 고불량(불량률 {HIGH_DEFECT:.0%}+) 위험 분류",
        "data_range": f"{start}~{end} (검증 {split}~)",
        "features_ref": "fact_production 4M 원핫 + qty_planned (계약 fact_defect v1.0)",
        "algorithm": f"{winner} (로지스틱 vs GBDT 비교 후)",
        "params": {"threshold": best_thr},
        "metrics": {"auc_gbdt": round(float(auc_gbdt), 4),
                    "auc_logistic": round(float(auc_logit), 4),
                    "precision_at_recall70": round(best_prec, 4)},
        "validation_scheme": f"시간 분할 — {split} 이전 학습/이후 검증",
        "version": version,
        "top_features": [{"feature": f, "importance": round(float(v), 5)} for f, v in top],
    }
    bundle = {"model": gbdt if winner == "gbdt" else logit,
              "columns": list(Xtr.columns), "threshold": best_thr}
    reg = cards.register(card, bundle)
    cards.promote("defect_classifier", version)
    return {"card": card, "registered": reg}


def model_importance_candidates() -> list[dict]:
    """카드의 특징 중요도 상위 → M5 원인 후보 입력."""
    card = cards.get_card("defect_classifier")
    if not card:
        return []
    out = []
    for t in card.get("top_features", [])[:6]:
        f = t["feature"]
        for prefix in CAT:                       # 원핫 컬럼명 = "<차원>_<값>"
            if f.startswith(prefix + "_"):
                out.append({"dims": {prefix: f[len(prefix) + 1:]},
                            "importance": t["importance"],
                            "source": "defect_classifier " + card["version"]})
                break
    return out
