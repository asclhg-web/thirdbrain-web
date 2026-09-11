"""M4-3 설비 이상탐지 — 관리도(기준선) 먼저, 그 다음 재구성 오차.

demo의 '오토인코더'는 PCA 재구성 오차로 구현(ISSUES.md D-07) — 정상 구간을
저차원으로 압축·복원했을 때의 오차가 크면 이상. TF/Keras 오토인코더는
DeepBackend 훅으로 교체 가능(인터페이스 동일: fit/score).
경보 폭주 방지: 일 상한(MAX_ALERTS_PER_DAY).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from .. import common, db
from . import cards

SIGNALS = ["temp", "current", "vibration"]
MAX_ALERTS_PER_DAY = 3

DDL = """
CREATE TABLE IF NOT EXISTS anomaly_scores (
  date_key TEXT NOT NULL, equipment_id TEXT NOT NULL,
  score REAL, threshold REAL, is_alert INTEGER,
  PRIMARY KEY (date_key, equipment_id)
);
"""


def _daily_matrix(equipment_id: str, start: str, end: str) -> pd.DataFrame:
    df = db.df("""
        SELECT date_key, signal, mean, std, p95, max FROM fact_sensor_daily
        WHERE equipment_id=? AND date_key BETWEEN ? AND ?""",
        (equipment_id, start, end))
    if df.empty:
        return df
    wide = df.pivot_table(index="date_key", values=["mean", "std", "p95", "max"],
                          columns="signal")
    wide.columns = [f"{a}_{b}" for a, b in wide.columns]
    return wide.dropna()


def control_baseline(equipment_id: str, start: str, end: str) -> pd.DataFrame:
    """기준선: 신호별 X-MR 관리도 이탈 일수."""
    df = db.df("""
        SELECT date_key, signal, mean FROM fact_sensor_daily
        WHERE equipment_id=? AND date_key BETWEEN ? AND ?""",
        (equipment_id, start, end))
    out = []
    for sig, g in df.groupby("signal"):
        mu, sd = g["mean"].mean(), g["mean"].std()
        ooc = g[np.abs(g["mean"] - mu) > 3 * sd]
        out.append({"signal": sig, "ooc_days": len(ooc),
                    "days": g["date_key"].tolist() if len(ooc) < 10 else []})
    return pd.DataFrame(out)


class ReconstructionDetector:
    """정상 구간 학습 → 재구성 오차 점수. (PCA demo / TF AE prod 훅)"""

    def __init__(self, n_components: int = 4):
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=n_components)
        self.threshold_: float | None = None

    def fit(self, X: pd.DataFrame, quantile: float = 0.995) -> "ReconstructionDetector":
        Z = self.scaler.fit_transform(X)
        self.pca.fit(Z)
        err = self._errors(Z)
        self.threshold_ = float(np.quantile(err, quantile))
        return self

    def _errors(self, Z: np.ndarray) -> np.ndarray:
        rec = self.pca.inverse_transform(self.pca.transform(Z))
        return ((Z - rec) ** 2).mean(axis=1)

    def score(self, X: pd.DataFrame) -> np.ndarray:
        return self._errors(self.scaler.transform(X))


def normal_window_mask(equipment_id: str, pre_fail_days: int = 14,
                       post_maint_days: int = 2) -> set[str]:
    """P2-C3: 정상 구간에서 제외할 날짜 집합 — I-01 재발 방지의 정식화.

    고장 수리일은 그 '이전 pre_fail_days'까지 제외한다(고장 전 드리프트가
    정상으로 학습되는 것을 차단). 정비일은 직후 post_maint_days까지 제외
    (부품 교체 직후의 과도 상태)."""
    from datetime import date, timedelta
    bad: set[str] = set()
    for r in db.query(
            "SELECT date_key, event_type FROM fact_equipment_event WHERE equipment_id=?",
            (equipment_id,)):
        d = date.fromisoformat(r["date_key"])
        bad.add(r["date_key"])
        if "고장" in (r["event_type"] or ""):
            for k in range(1, pre_fail_days + 1):
                bad.add((d - timedelta(days=k)).isoformat())
        for k in range(1, post_maint_days + 1):
            bad.add((d + timedelta(days=k)).isoformat())
    return bad


def train_and_register(equipment_id: str, train_start: str, train_end: str,
                       version: str = "v1") -> dict:
    """정상 구간(train)으로 학습 — 고장 전 드리프트·정비 직후까지 제외."""
    bad_days = normal_window_mask(equipment_id)
    X = _daily_matrix(equipment_id, train_start, train_end)
    X = X[~X.index.isin(bad_days)]
    if len(X) < 30:
        raise ValueError(f"정상 구간 표본 부족: {len(X)}일")
    det = ReconstructionDetector().fit(X)
    card = {
        "model_id": f"anomaly_{equipment_id}",
        "problem": f"{equipment_id} 센서 이상탐지(재구성 오차)",
        "data_range": f"{train_start}~{train_end} (정비·고장전14일 제외 {len(X)}일)",
        "features_ref": "fact_sensor_daily mean/std/p95/max × temp/current/vibration",
        "algorithm": "PCA 재구성 오차 (TF 오토인코더 훅 교체 가능)",
        "params": {"n_components": 4, "threshold_quantile": 0.995},
        "metrics": {"threshold": round(det.threshold_, 5)},
        "validation_scheme": "정상 구간 학습 → 전체 구간 점수화(고장 전 상승 확인)",
        "version": version,
    }
    reg = cards.register(card, det)
    cards.promote(f"anomaly_{equipment_id}", version)
    return {"card": card, "registered": reg}


def score_range(equipment_id: str, start: str, end: str) -> pd.DataFrame:
    """구간 점수화 + 경보 기록(일 상한 적용)."""
    db.executescript(DDL)
    card, det = cards.serving(f"anomaly_{equipment_id}")
    X = _daily_matrix(equipment_id, start, end)
    s = det.score(X)
    out = pd.DataFrame({"date_key": X.index, "equipment_id": equipment_id,
                        "score": s, "threshold": det.threshold_})
    out["is_alert"] = (out["score"] > out["threshold"]).astype(int)
    n_alerts = 0
    for r in out[out["is_alert"] == 1].itertuples():
        if n_alerts < MAX_ALERTS_PER_DAY:
            common.alert("warn", "M4-3",
                         f"{equipment_id} 이상 점수 {r.score:.3f} > 임계 {r.threshold:.3f} ({r.date_key})")
            n_alerts += 1
    db.executemany(
        "INSERT OR REPLACE INTO anomaly_scores VALUES (?,?,?,?,?)",
        [(r.date_key, equipment_id, float(r.score), float(r.threshold), int(r.is_alert))
         for r in out.itertuples()])
    return out


def weekly_hit_report(equipment_id: str) -> dict:
    """적중률 리포트 — 경보 vs 실제 고장(fact_equipment_event '고장').
    선행 14일 내 경보가 있으면 적중."""
    db.executescript(DDL)
    cover = db.one("SELECT MIN(date_key) a, MAX(date_key) b FROM anomaly_scores "
                   "WHERE equipment_id=?", (equipment_id,))
    fails = db.query(
        "SELECT date_key FROM fact_equipment_event "
        "WHERE equipment_id=? AND event_type LIKE '%고장%' "
        "AND date_key BETWEEN ? AND ?",                       # 점수 커버리지 내 고장만
        (equipment_id, cover["a"] or "0000", cover["b"] or "9999"))
    alerts = db.df("SELECT date_key FROM anomaly_scores "
                   "WHERE equipment_id=? AND is_alert=1", (equipment_id,))
    hits, lead_days = 0, []
    for f in fails:
        fd = pd.Timestamp(f["date_key"])
        prior = alerts[(pd.to_datetime(alerts["date_key"]) < fd)
                       & (pd.to_datetime(alerts["date_key"]) >= fd - pd.Timedelta(days=14))]
        if len(prior):
            hits += 1
            lead_days.append(int((fd - pd.to_datetime(prior["date_key"]).min()).days))
    n_alert_days = int(alerts["date_key"].nunique()) if len(alerts) else 0
    total_days = db.scalar(
        "SELECT COUNT(DISTINCT date_key) FROM anomaly_scores WHERE equipment_id=?",
        (equipment_id,)) or 1
    return {"equipment_id": equipment_id, "failures": len(fails), "detected": hits,
            "recall": hits / max(len(fails), 1),
            "alert_day_rate": n_alert_days / total_days,
            "median_lead_days": float(np.median(lead_days)) if lead_days else None}
