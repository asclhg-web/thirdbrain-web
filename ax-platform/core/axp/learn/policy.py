"""M4-4 정책 탐색 — Twin 안에서만 학습하는 RL-lite(교차 엔트로피 방법).

RLlib 백엔드는 어댑터로 교체 가능(ISSUES.md D-02). 안전장치는 동일:
  · 시뮬레이터 밖 학습 금지 — 입력은 Twin뿐.
  · 기준선(현행·통계 정책)을 먼저 기록 — 이기지 못한 정책은 상신 금지.
  · 산출은 정책 제안 dict — M6가 판단 카드로 조립, M7 승인함으로.
"""
from __future__ import annotations

import numpy as np

from .simulate import InventoryTwin, Policy


def baseline_scores(twin: InventoryTwin) -> dict[str, dict]:
    """비교 기준선 — 현행 유사·뉴스벤더(통계) 정책의 성적."""
    current = twin.run(Policy(demand_factor=1.02, safety_days=0.05))
    # 뉴스벤더 근사: 임계 서비스율 = Cu/(Cu+Co)
    cu, co = twin.costs.stockout, twin.costs.scrap + twin.costs.holding_per_day
    critical = cu / (cu + co)
    z = {0.5: 0.0, 0.6: 0.25}.get(round(critical, 1), 0.6 if critical > 0.55 else 0.2)
    nv = twin.run(Policy(demand_factor=1.0, safety_days=float(z)))
    return {"current_like": current, "newsvendor": nv,
            "critical_ratio": round(critical, 3)}


def cross_entropy_search(twin: InventoryTwin, n_iter: int = 12, pop: int = 40,
                         elite_frac: float = 0.2, seed: int = 0) -> dict:
    """교차 엔트로피 탐색 — (demand_factor, safety_days) 2차원 정책 공간."""
    rng = np.random.default_rng(seed)
    mu = np.array([1.0, 0.5])
    sigma = np.array([0.25, 0.5])
    history = []
    for it in range(n_iter):
        cand = rng.normal(mu, sigma, size=(pop, 2))
        cand[:, 0] = cand[:, 0].clip(0.5, 2.0)
        cand[:, 1] = cand[:, 1].clip(0.0, 2.0)
        scores = np.array([twin.run(Policy(df, sd))["total_cost"]
                           for df, sd in cand])
        elite = cand[np.argsort(scores)[: max(2, int(pop * elite_frac))]]
        mu, sigma = elite.mean(axis=0), elite.std(axis=0) + 1e-3
        history.append({"iter": it, "best_cost": float(scores.min()),
                        "mu": mu.round(3).tolist()})
    best = Policy(float(mu[0]), float(mu[1]))
    return {"policy": {"demand_factor": round(best.demand_factor, 3),
                       "safety_days": round(best.safety_days, 3)},
            "result": twin.run(best), "history": history}


def propose(twin: InventoryTwin, product_id: str, store_id: str) -> dict | None:
    """정책 제안 생성 — 기준선을 이긴 경우에만. (이기지 못하면 None: 상신 금지)"""
    base = baseline_scores(twin)
    search = cross_entropy_search(twin)
    candidates = {k: v for k, v in base.items() if isinstance(v, dict)}
    best_base_name = min(candidates, key=lambda k: candidates[k]["total_cost"])
    best_base = candidates[best_base_name]
    cand = search["result"]
    if cand["total_cost"] >= best_base["total_cost"]:
        return None
    saving_pct = (best_base["total_cost"] - cand["total_cost"]) / best_base["total_cost"] * 100
    return {
        "kind": "inventory_policy",
        "product_id": product_id, "store_id": store_id,
        "proposed_policy": search["policy"],
        "twin_result": {k: round(v, 2) if isinstance(v, float) else v
                        for k, v in cand.items()},
        "baseline_name": best_base_name,
        "baseline_result": {k: round(v, 2) if isinstance(v, float) else v
                            for k, v in best_base.items()},
        "saving_pct": round(saving_pct, 1),
        "evidence": {"twin_days": cand["days"],
                     "search": "cross-entropy 12 iter × 40 pop (Twin 내부만)"},
    }
