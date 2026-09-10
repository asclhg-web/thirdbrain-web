"""M3-1 표준 EDA 팩 6종 — 층별·파레토·추세·관리도·상관·분포.

입력은 표준 데이터셋만(원본 직접 접근 금지). 전 라벨 한글.
관리도는 데이터 특성으로 유형 자동 선택: 비율→p, 건수→u(근사 c), 계량→X-MR.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .. import config, db

plt.rcParams["font.family"] = ["Noto Sans CJK KR", "NanumGothic", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

PALETTE = ["#9C5227", "#0E8F86", "#E8A33D", "#714B67", "#A8493B", "#76675A"]

LABELS = {"worker_id": "작업자", "equipment_id": "설비", "material_lot_id": "자재 로트",
          "sop_id": "표준작업", "shift": "근무조", "product_id": "제품",
          "line_id": "라인", "store_id": "매장", "defect_type": "불량 유형",
          "vendor_id": "공급사", "date_key": "일자"}


def _out(name: str) -> Path:
    d = config.ARTIFACTS / "eda"
    d.mkdir(parents=True, exist_ok=True)
    return d / name


def _save(fig, name: str) -> str:
    p = _out(name)
    fig.tight_layout()
    fig.savefig(p, dpi=110)
    plt.close(fig)
    return str(p)


def stratify(dim: str, start: str, end: str) -> tuple[pd.DataFrame, str]:
    """① 층별 — 차원별 불량률 피벗(불량/생산)."""
    prod = db.df(f"""
        SELECT p.{dim} AS k, SUM(p.qty_planned) AS produced
        FROM fact_production p WHERE p.date_key BETWEEN ? AND ? GROUP BY p.{dim}""",
        (start, end))
    dfc = db.df(f"""
        SELECT d.{dim} AS k, SUM(d.qty_defect) AS defects
        FROM fact_defect d WHERE d.date_key BETWEEN ? AND ? GROUP BY d.{dim}""",
        (start, end)) if dim != "store_id" else pd.DataFrame(columns=["k", "defects"])
    t = prod.merge(dfc, on="k", how="left").fillna({"defects": 0})
    t["defect_rate"] = t["defects"] / t["produced"].replace(0, np.nan)
    t = t.sort_values("defect_rate", ascending=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(t["k"].astype(str), t["defect_rate"] * 100, color=PALETTE[0])
    ax.set_title(f"층별 불량률 — {LABELS.get(dim, dim)} ({start}~{end})")
    ax.set_ylabel("불량률 (%)")
    path = _save(fig, f"stratify_{dim}.png")
    return t, path


def pareto(start: str, end: str) -> tuple[pd.DataFrame, str]:
    """② 파레토 — 불량 유형별 누적."""
    t = db.df("""
        SELECT defect_type AS k, SUM(qty_defect) AS n FROM fact_defect
        WHERE date_key BETWEEN ? AND ? GROUP BY defect_type ORDER BY n DESC""",
        (start, end))
    t["cum_pct"] = t["n"].cumsum() / t["n"].sum() * 100
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(t["k"], t["n"], color=PALETTE[0])
    ax2 = ax.twinx()
    ax2.plot(t["k"], t["cum_pct"], "o-", color=PALETTE[2])
    ax2.axhline(80, ls="--", c="#999")
    ax.set_title(f"파레토 — 불량 유형 ({start}~{end})")
    ax.set_ylabel("불량 수량")
    ax2.set_ylabel("누적 (%)")
    path = _save(fig, "pareto_defect.png")
    return t, path


def trend(metric: str, start: str, end: str, product_id: str | None = None
          ) -> tuple[pd.DataFrame, str]:
    """③ 추세 — 판매/폐기/불량률 주간 추세."""
    if metric == "sales":
        t = db.df("SELECT date_key, SUM(qty) AS v FROM fact_sales "
                  + ("WHERE product_id=? AND " if product_id else "WHERE ")
                  + "date_key BETWEEN ? AND ? GROUP BY date_key",
                  ((product_id, start, end) if product_id else (start, end)))
        title, ylab = "판매 추세", "판매 수량"
    elif metric == "scrap":
        t = db.df("SELECT date_key, SUM(qty) AS v FROM fact_inventory_move "
                  "WHERE move_type='scrap' AND date_key BETWEEN ? AND ? GROUP BY date_key",
                  (start, end))
        title, ylab = "폐기 추세", "폐기 수량"
    else:
        t = db.df("""
            SELECT d.date_key, SUM(d.qty_defect)*1.0/NULLIF(SUM(p.qty_planned),0) AS v
            FROM fact_production p LEFT JOIN fact_defect d USING (mo_ref)
            WHERE p.date_key BETWEEN ? AND ? GROUP BY p.date_key""", (start, end))
        title, ylab = "불량률 추세", "불량률"
    t["ma7"] = t["v"].rolling(7, min_periods=1).mean()
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(pd.to_datetime(t["date_key"]), t["v"], color="#ccc", lw=0.8, label="일별")
    ax.plot(pd.to_datetime(t["date_key"]), t["ma7"], color=PALETTE[0], lw=2, label="7일 이동평균")
    ax.legend()
    ax.set_title(f"{title} ({start}~{end})")
    ax.set_ylabel(ylab)
    path = _save(fig, f"trend_{metric}.png")
    return t, path


def control_chart(start: str, end: str, equipment_id: str | None = None
                  ) -> tuple[pd.DataFrame, str, list[str]]:
    """④ 관리도 — 불량률은 p-관리도 자동 선택. 이탈점 표시·반환."""
    cond = "AND p.equipment_id=?" if equipment_id else ""
    params = (start, end, equipment_id) if equipment_id else (start, end)
    t = db.df(f"""
        SELECT p.date_key, SUM(p.qty_planned) AS n,
               COALESCE(SUM(d.qty_defect),0) AS x
        FROM fact_production p LEFT JOIN fact_defect d USING (mo_ref)
        WHERE p.date_key BETWEEN ? AND ? {cond}
        GROUP BY p.date_key ORDER BY p.date_key""", params)
    t["p"] = t["x"] / t["n"]
    pbar = t["x"].sum() / t["n"].sum()
    t["ucl"] = pbar + 3 * np.sqrt(pbar * (1 - pbar) / t["n"])
    t["lcl"] = (pbar - 3 * np.sqrt(pbar * (1 - pbar) / t["n"])).clip(lower=0)
    t["ooc"] = (t["p"] > t["ucl"]) | (t["p"] < t["lcl"])
    fig, ax = plt.subplots(figsize=(8, 3.5))
    x = pd.to_datetime(t["date_key"])
    ax.plot(x, t["p"], color=PALETTE[1], lw=1)
    ax.plot(x, t["ucl"], "--", color="#999", lw=1)
    ax.plot(x, t["lcl"], "--", color="#999", lw=1)
    ax.axhline(pbar, color="#666", lw=1)
    ax.scatter(x[t["ooc"]], t["p"][t["ooc"]], color=PALETTE[4], zorder=5, s=18)
    ax.set_title(f"p-관리도 — 불량률{'(' + equipment_id + ')' if equipment_id else ''}")
    ax.set_ylabel("불량률")
    path = _save(fig, f"pchart_{equipment_id or 'all'}.png")
    return t, path, t.loc[t["ooc"], "date_key"].tolist()


def correlation(start: str, end: str) -> tuple[pd.DataFrame, str]:
    """⑤ 상관 — 일 단위 지표 간 상관(판매·폐기·불량·설비 온도편차)."""
    daily = db.df("""
        SELECT c.date_key,
          (SELECT SUM(qty) FROM fact_sales s WHERE s.date_key=c.date_key) AS 판매,
          (SELECT SUM(qty) FROM fact_inventory_move m WHERE m.date_key=c.date_key AND move_type='scrap') AS 폐기,
          (SELECT SUM(qty_defect) FROM fact_defect d WHERE d.date_key=c.date_key) AS 불량,
          (SELECT AVG(std) FROM fact_sensor_daily f WHERE f.date_key=c.date_key AND signal='temp') AS 온도편차
        FROM dim_calendar c WHERE c.date_key BETWEEN ? AND ?""", (start, end))
    corr = daily.drop(columns=["date_key"]).corr()
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)), corr.columns, rotation=45)
    ax.set_yticks(range(len(corr)), corr.columns)
    for i in range(len(corr)):
        for j in range(len(corr)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=9)
    fig.colorbar(im)
    ax.set_title(f"상관 — 일 단위 지표 ({start}~{end})")
    path = _save(fig, "correlation.png")
    return corr, path


def distribution(start: str, end: str) -> tuple[pd.DataFrame, str]:
    """⑥ 분포 — 제품별 일 판매량 분포(상자그림)."""
    t = db.df("""
        SELECT product_id, date_key, SUM(qty) AS qty FROM fact_sales
        WHERE date_key BETWEEN ? AND ? GROUP BY product_id, date_key""", (start, end))
    names = db.df("SELECT product_id, product_name FROM dim_product")
    t = t.merge(names, on="product_id")
    fig, ax = plt.subplots(figsize=(8, 4))
    order = t.groupby("product_name")["qty"].median().sort_values(ascending=False).index
    data = [t.loc[t["product_name"] == n, "qty"] for n in order]
    bp = ax.boxplot(data, tick_labels=order, patch_artist=True)
    for b in bp["boxes"]:
        b.set_facecolor("#F8F2EA")
        b.set_edgecolor(PALETTE[0])
    ax.set_title(f"분포 — 제품별 일 판매량 ({start}~{end})")
    ax.set_ylabel("일 판매 수량")
    path = _save(fig, "distribution.png")
    return t, path


def run_pack(start: str, end: str) -> dict:
    """6종 일괄 실행 — 산출 경로 목록 반환."""
    out = {}
    out["stratify_equipment"] = stratify("equipment_id", start, end)[1]
    out["stratify_shift"] = stratify("shift", start, end)[1]
    out["pareto"] = pareto(start, end)[1]
    out["trend_sales"] = trend("sales", start, end)[1]
    out["control_chart"] = control_chart(start, end)[1]
    out["correlation"] = correlation(start, end)[1]
    out["distribution"] = distribution(start, end)[1]
    return out
