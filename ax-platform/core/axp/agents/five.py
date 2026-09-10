"""M7-2 기본 에이전트 5종 — 4대 지능화와 1:1+α.

① demand_agent      수요예측(일 배치) — 매장×주력 제품 발주 카드
② replenish_agent   보충 정책(Twin 검증 통과 시) — 정책 변경 카드
③ allocation_agent  배분(생산 완료) — 지점 배분안 카드
④ equip_alert_agent 설비경보(이상 점수 임계) — 점검 제안 + M6 해설
⑤ knowledge_agent   지식검증(확신도 임계) — Rule 승격 상신 카드

각 에이전트는 명세(spec) 한 줄을 등록 시 선언한다 — 명세서 없는 구현 금지.
"""
from __future__ import annotations

from .. import db
from ..graph import confidence
from ..judge import cards as jcards
from ..judge import generator
from ..learn import anomaly, policy, simulate
from . import runtime


def demand_agent(ctx: dict) -> list[int]:
    as_of = ctx["run_date"]
    pairs = ctx.get("pairs") or [("S-MAIN", "P-CREAM"), ("S-MAIN", "P-PIE"),
                                 ("B2B-MART", "P-CREAM")]
    out = []
    for store_id, product_id in pairs:
        out.append(generator.demand_card(as_of, store_id, product_id,
                                         agent="demand_agent"))
    return out


def replenish_agent(ctx: dict) -> list[int]:
    as_of = ctx["run_date"]
    start = (db.scalar("SELECT date_key FROM dim_calendar WHERE date_key<=? "
                       "ORDER BY date_key DESC LIMIT 1 OFFSET 90", (as_of,))
             or "2026-05-01")
    out = []
    for store_id, product_id in ctx.get("pairs") or [("S-MAIN", "P-CREAM")]:
        twin = simulate.build_twin(product_id, store_id, start, as_of, forecast_kind="dow")
        prop = policy.propose(twin, product_id, store_id)
        if prop:                                   # 기준선을 이긴 제안만
            out.append(generator.policy_card(prop, agent="replenish_agent"))
    return out


def allocation_agent(ctx: dict) -> list[int]:
    """생산 완료 이벤트 — 예측 비중대로 매장 배분안."""
    as_of, product_id = ctx["run_date"], ctx.get("product_id", "P-CREAM")
    done = db.scalar(
        "SELECT SUM(qty_done) FROM fact_production WHERE date_key=? AND product_id=?",
        (as_of, product_id)) or 0
    if done <= 0:
        return []
    shares = db.df(
        "SELECT store_id, SUM(qty) qty FROM fact_sales "
        "WHERE product_id=? AND date_key BETWEEN date(?,'-27 days') AND ? GROUP BY store_id",
        (product_id, as_of, as_of))
    total = shares["qty"].sum()
    allocations = [{"store_id": r.store_id, "qty": round(done * r.qty / total)}
                   for r in shares.itertuples()]
    card = {
        "kind": "allocation", "agent": "allocation_agent",
        "proposal": f"{product_id} 금일 생산 {done:.0f}개를 최근 4주 판매 비중대로 배분 제안",
        "narrative": "\n".join(
            f"{a['store_id']}에 {a['qty']}개 — 최근 4주 판매 비중 기준. [근거: fact_sales 4주]"
            for a in allocations),
        "values": [{"name": f"배분 {a['store_id']}", "value": a["qty"], "unit": "EA",
                    "source": "fact_production 금일 + fact_sales 4주 비중"}
                   for a in allocations],
        "evidence": {"kind": "dims", "dims": {"product_id": product_id},
                     "product_id": product_id, "allocations": allocations,
                     "produced": done},
        "alternatives": [{"name": "균등 배분", "why_not": "매장별 수요 차이 무시 — 결품·폐기 동시 증가"}],
        "approver": "카드 승인자",
    }
    return [jcards.create(card)]


def equip_alert_agent(ctx: dict) -> list[int]:
    """이상 점수 임계 초과 설비 — 점검 제안 카드(+해설)."""
    as_of = ctx["run_date"]
    alerts = db.query(
        "SELECT * FROM anomaly_scores WHERE is_alert=1 AND date_key=?", (as_of,))
    out = []
    for a in alerts:
        eq = a["equipment_id"]
        rep = anomaly.weekly_hit_report(eq)
        card = {
            "kind": "equip_alert", "agent": "equip_alert_agent",
            "proposal": f"{eq} 이상 신호 — 점검(온도계 교정·구동부 확인) 제안",
            "narrative": "\n".join([
                f"{a['date_key']} 재구성 오차 {a['score']:.3f}가 임계 {a['threshold']:.3f}를 "
                f"초과했습니다. [근거: anomaly_scores {eq}]",
                f"이 감지기의 과거 적중: 고장 {rep['failures']}건 중 {rep['detected']}건 "
                f"선행 감지. [근거: weekly_hit_report]"]),
            "values": [
                {"name": "이상 점수", "value": round(a["score"], 3),
                 "source": f"anomaly_{eq} 모델"},
                {"name": "임계", "value": round(a["threshold"], 3),
                 "source": f"anomaly_{eq} 모델 카드"}],
            "evidence": {"kind": "dims", "dims": {"equipment_id": eq},
                         "equipment_id": eq, "date": a["date_key"]},
            "alternatives": [{"name": "관망", "why_not": "과거 고장 전 동일 패턴 — 선행 정비가 저비용"}],
            "approver": "카드 승인자",
        }
        out.append(jcards.create(card))
    return out


def knowledge_agent(ctx: dict) -> list[int]:
    """확신도 임계 도달 후보 — Rule 승격 상신 카드."""
    subs = confidence.check_thresholds()
    out = []
    for s in subs:
        card = {
            "kind": "knowledge", "agent": "knowledge_agent",
            "proposal": f"원인 후보의 Rule 승격 상신 — {confidence.rule_text(s['dims'])}",
            "narrative": (f"확신도 {s['confidence']:.0%}, 독립 확인 {s['confirmations']}회로 "
                          f"임계(70%·3회)에 도달했습니다. [근거: causal_candidates {s['cc_id']}]"),
            "values": [{"name": "확신도", "value": round(s["confidence"], 3),
                        "source": "confidence 루프(독립 창 누적)"},
                       {"name": "확인 횟수", "value": s["confirmations"],
                        "source": "causal_candidates.confirmations"}],
            "evidence": {"kind": "dims", "dims": s["dims"], "cc_id": s["cc_id"]},
            "alternatives": [{"name": "계속 관찰", "why_not": "임계 도달 — 지연 시 동일 불량 반복 비용"}],
            "approver": "카드 승인자",
        }
        out.append(jcards.create(card))
    return out


SPECS = {
    "demand_agent": "트리거: 일 배치 07:00 · 입력: 특징 저장소 · 호출: demand_forecast 모델 · 카드: 7일 발주 기준수량 · 승인자: 카드 승인자",
    "replenish_agent": "트리거: 주 1회(월) · 입력: fact_sales 90일 · 호출: InventoryTwin+정책 탐색 · 카드: 정책 변경(기준선 우위 시만) · 승인자: 카드 승인자",
    "allocation_agent": "트리거: 생산 완료 이벤트 · 입력: fact_production 금일 · 호출: 판매 비중 · 카드: 매장 배분안 · 승인자: 카드 승인자",
    "equip_alert_agent": "트리거: 이상 점수 임계 이벤트 · 입력: anomaly_scores · 호출: 감지기+적중 리포트 · 카드: 점검 제안 · 승인자: 카드 승인자",
    "knowledge_agent": "트리거: 확신도 임계 이벤트 · 입력: causal_candidates · 호출: confidence 루프 · 카드: Rule 승격 상신 · 승인자: 카드 승인자",
}


def register_all() -> None:
    runtime.register("demand_agent", "daily", demand_agent, SPECS["demand_agent"])
    runtime.register("replenish_agent", "weekly", replenish_agent, SPECS["replenish_agent"])
    runtime.register("allocation_agent", "event:production_done", allocation_agent,
                     SPECS["allocation_agent"])
    runtime.register("equip_alert_agent", "event:anomaly", equip_alert_agent,
                     SPECS["equip_alert_agent"])
    runtime.register("knowledge_agent", "event:confidence", knowledge_agent,
                     SPECS["knowledge_agent"])
