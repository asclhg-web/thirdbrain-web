"""M6-2 판단 카드 생성기 — 모델 수치+구간, 그래프 규칙, 대안을 카드로 합성."""
from __future__ import annotations

import pandas as pd

from .. import db
from ..graph import confidence
from ..learn import cards as model_cards
from ..learn import forecast
from . import assembler, cards


def demand_card(as_of: str, store_id: str, product_id: str,
                approver: str = "카드 승인자", agent: str = "demand_agent") -> int:
    """수요예측 카드 — 다음 7일 발주 제안."""
    pred = forecast.predict(as_of)
    sel = pred[(pred["store_id"] == store_id) & (pred["product_id"] == product_id)]
    if sel.empty:
        raise ValueError(f"예측 없음: {store_id}/{product_id}")
    total_p50 = float(sel["p50"].sum())
    total_p10, total_p90 = float(sel["p10"].sum()), float(sel["p90"].sum())
    mcard = model_cards.get_card("demand_forecast") or {}
    pname = db.scalar("SELECT product_name FROM dim_product WHERE product_id=?",
                      (product_id,)) or product_id

    # 관련 규칙(그래프) — 제품·설비 관련 승격 규칙이 있으면 카드에 병기
    related_rules = []
    for r in confidence.rules("promoted"):
        if product_id in r["dims"].values() or True:   # 전 규칙 노출(소수) — 판단 참고
            related_rules.append({"rule_id": r["rule_id"],
                                  "text": confidence.rule_text(r["dims"])})

    # 최근 실적(원장) — 근거의 사다리 첫 칸
    recent = db.df(
        "SELECT date_key, qty FROM fact_sales WHERE store_id=? AND product_id=? "
        "AND date_key<=? ORDER BY date_key DESC LIMIT 7",
        (store_id, product_id, as_of))
    recent_sum = float(recent["qty"].sum())

    horizon = (sel["date_key"].min(), sel["date_key"].max())
    proposal = (f"{pname}({product_id}) {store_id} — {horizon[0]}~{horizon[1]} "
                f"7일 발주 기준수량을 {total_p50:.0f}개로 제안")
    narrative = "\n".join([
        f"다음 7일 예측 합계는 {total_p50:.0f}개(P10 {total_p10:.0f}~P90 {total_p90:.0f})입니다. "
        f"[근거: demand_forecast {mcard.get('version')} 모델 카드]",
        f"직전 7일 실적은 {recent_sum:.0f}개였습니다. [근거: fact_sales ~{as_of}]",
        *[f"참고 규칙: {r['text']} [근거: Rule:{r['rule_id']}]" for r in related_rules[:2]],
    ])
    card = {
        "kind": "demand_forecast", "agent": agent,
        "proposal": proposal, "narrative": narrative,
        "values": [
            {"name": "7일 예측 합계", "value": round(total_p50), "unit": "EA",
             "source": f"demand_forecast {mcard.get('version')} (WAPE {mcard.get('metrics', {}).get('wape')})"},
            {"name": "직전 7일 실적", "value": round(recent_sum), "unit": "EA",
             "source": f"fact_sales ~{as_of}"},
        ],
        "range": {"p10": round(total_p10), "p50": round(total_p50), "p90": round(total_p90)},
        "evidence": {"kind": "forecast", "store_id": store_id, "product_id": product_id,
                     "model": f"demand_forecast {mcard.get('version')}",
                     "daily": sel.to_dict("records"),
                     "rules": [r["rule_id"] for r in related_rules[:2]]},
        "alternatives": [
            {"name": "보수 발주(P10)", "value": round(total_p10),
             "why_not": "결품 위험 증가 — 서비스 수준 저하"},
            {"name": "공격 발주(P90)", "value": round(total_p90),
             "why_not": "폐기 위험 증가 — 신선 제품 유통기한 1일"},
        ],
        "approver": approver,
    }
    return cards.create(card)


def policy_card(prop: dict, approver: str = "카드 승인자",
                agent: str = "replenish_agent") -> int:
    """재고 정책 제안 카드 — M4-4 Twin 검증 통과 제안만 받는다."""
    tw, base = prop["twin_result"], prop["baseline_result"]
    narrative = "\n".join([
        f"Twin {prop['evidence']['twin_days']}일 검증에서 제안 정책의 일 비용은 "
        f"{tw['cost_per_day']:.0f}원으로 기준선({prop['baseline_name']}) "
        f"{base['cost_per_day']:.0f}원 대비 {prop['saving_pct']}% 낮았습니다. "
        f"[근거: InventoryTwin {prop['evidence']['search']}]",
        f"서비스 수준 {tw['service_level']:.0%}, 폐기율 {tw['scrap_rate']:.0%}였습니다. "
        f"[근거: Twin 성적표]",
    ])
    card = {
        "kind": "replenish", "agent": agent,
        "proposal": (f"{prop['product_id']} {prop['store_id']} 발주 정책을 "
                     f"배율 {prop['proposed_policy']['demand_factor']}, "
                     f"안전 {prop['proposed_policy']['safety_days']}일로 변경 제안"),
        "narrative": narrative,
        "values": [
            {"name": "일 비용(제안)", "value": tw["cost_per_day"], "unit": "KRW/일",
             "source": "InventoryTwin 검증"},
            {"name": "일 비용(기준선)", "value": base["cost_per_day"], "unit": "KRW/일",
             "source": f"InventoryTwin {prop['baseline_name']}"},
        ],
        "range": {"saving_pct": prop["saving_pct"]},
        "evidence": {"kind": "twin", "detail": prop["evidence"],
                     "policy": prop["proposed_policy"]},
        "alternatives": [
            {"name": "현행 유지", "why_not": f"일 {base['cost_per_day'] - tw['cost_per_day']:.0f}원 초과 비용 지속"},
        ],
        "approver": approver,
    }
    return cards.create(card)
