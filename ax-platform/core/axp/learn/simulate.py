"""M4-4 재고 Digital Twin — 정책 학습의 유일한 운동장.

철칙: 학습은 이 시뮬레이터 안에서만. 산출은 정책 '제안' 카드로만.
재생 검증: 현행 정책을 넣으면 실제 실적(폐기율·결품 근사)과 유사해야 한다.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .. import db


@dataclass
class Costs:
    holding_per_day: float = 30.0      # 보관비/개/일
    stockout: float = 1200.0           # 결품 기회비용/개 (마진 근사)
    scrap: float = 800.0               # 폐기 원가/개


@dataclass
class Policy:
    """기준재고(base-stock) 정책 — 내일 수요 예측 × 계수 + 안전재고."""
    demand_factor: float = 1.0         # 예측 대비 발주 배율
    safety_days: float = 0.5           # 안전재고(평균 수요 일수)
    shelf_life_days: int = 1           # 유통기한 — 신선 빵: 당일 판매, 익일 폐기

    def order_qty(self, forecast_next: float, on_hand: float, avg_demand: float) -> float:
        target = forecast_next * self.demand_factor + avg_demand * self.safety_days
        return max(0.0, target - on_hand)


class InventoryTwin:
    """일 단위 신선재고 시뮬레이터 — FIFO, 유통기한 폐기, 리드타임 1일."""

    def __init__(self, demand_series: np.ndarray, forecast_series: np.ndarray,
                 costs: Costs = Costs()):
        assert len(demand_series) == len(forecast_series)
        self.demand = demand_series.astype(float)
        self.forecast = forecast_series.astype(float)
        self.costs = costs

    def run(self, policy: Policy) -> dict:
        ages: list[tuple[float, int]] = []      # (수량, 경과일) FIFO
        avg_d = float(self.demand.mean())
        stockout = scrap = holding = served = 0.0
        pipeline = 0.0                            # 리드타임 1일 발주 잔량
        for t in range(len(self.demand)):
            # 입고(전일 발주분)
            if pipeline > 0:
                ages.append((pipeline, 0))
                pipeline = 0.0
            # 판매(FIFO)
            need = self.demand[t]
            new_ages = []
            for qty, age in ages:
                take = min(qty, need)
                served += take
                need -= take
                rest = qty - take
                if rest > 0:
                    new_ages.append((rest, age))
            stockout += need
            # 노화·폐기
            ages = []
            for qty, age in new_ages:
                if age + 1 >= policy.shelf_life_days:
                    scrap += qty
                else:
                    ages.append((qty, age + 1))
            on_hand = sum(q for q, _ in ages)
            holding += on_hand
            # 발주(내일 입고)
            f_next = self.forecast[min(t + 1, len(self.forecast) - 1)]
            pipeline = policy.order_qty(f_next, on_hand, avg_d)
        n = len(self.demand)
        total_demand = float(self.demand.sum())
        cost = (holding * self.costs.holding_per_day
                + stockout * self.costs.stockout + scrap * self.costs.scrap)
        return {"days": n, "total_demand": total_demand,
                "service_level": served / max(total_demand, 1),
                "stockout_qty": stockout, "scrap_qty": scrap,
                "scrap_rate": scrap / max(served + scrap, 1),
                "avg_on_hand": holding / n, "total_cost": cost,
                "cost_per_day": cost / n}


def build_twin(product_id: str, store_id: str, start: str, end: str,
               forecast_kind: str = "ewm") -> InventoryTwin:
    """실제 수요(fact_sales)로 트윈 구성. 예측열은 평활(재생 검증용) 또는 모델."""
    df = db.df(
        "SELECT date_key, qty FROM fact_sales WHERE product_id=? AND store_id=? "
        "AND date_key BETWEEN ? AND ? ORDER BY date_key",
        (product_id, store_id, start, end))
    dates = pd.date_range(start, end, freq="D").strftime("%Y-%m-%d")
    s = df.set_index("date_key")["qty"].reindex(dates).fillna(0.0)
    if forecast_kind == "ewm":
        fc = s.shift(1).ewm(span=7, min_periods=1).mean()
    else:                                   # 'dow': 지난주 같은 요일 — 현장 발주 관행
        fc = s.shift(7)
    fc = fc.fillna(s.mean())
    return InventoryTwin(s.values, fc.values)


def replay_validate(product_id: str, store_id: str, start: str, end: str) -> dict:
    """재생 검증 — 현행 유사 정책(같은 요일 발주, 소폭 여유)의 폐기율이
    실제 폐기율(전사 fact 기준)과 같은 자릿수인지."""
    twin = build_twin(product_id, store_id, start, end, forecast_kind="dow")
    sim = twin.run(Policy(demand_factor=1.02, safety_days=0.05))
    actual_scrap = db.scalar(
        "SELECT SUM(qty) FROM fact_inventory_move WHERE move_type='scrap' "
        "AND product_id=? AND date_key BETWEEN ? AND ?", (product_id, start, end)) or 0
    actual_sales = db.scalar(
        "SELECT SUM(qty) FROM fact_sales WHERE product_id=? AND date_key BETWEEN ? AND ?",
        (product_id, start, end)) or 1
    actual_rate = actual_scrap / (actual_scrap + actual_sales)
    ratio = sim["scrap_rate"] / max(actual_rate, 1e-6)
    return {"sim_scrap_rate": round(sim["scrap_rate"], 4),
            "actual_scrap_rate": round(actual_rate, 4),
            "ratio": round(ratio, 2),
            "pass": 0.2 <= ratio <= 5.0,     # 같은 자릿수(합의 범위)
            "sim": sim}
