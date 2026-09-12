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
from ..learn import anomaly, forecast, policy, simulate
from . import runtime


def _require_model(model_id: str) -> None:
    """P5-N: 학습 전 사전 검사 — 서빙 모델이 없으면 실패가 아니라 대기."""
    from ..learn import cards as lcards
    try:
        lcards.serving(model_id)
    except lcards.CardError as e:
        raise runtime.NotReady(
            f"{model_id} 학습 전({e}) — 데이터 축적 후 M4 학습이 승급되면 카드 생성 시작")


def demand_agent(ctx: dict) -> list[int]:
    from .. import profile_rt
    _require_model("demand_forecast")
    as_of = ctx["run_date"]
    pairs = ctx.get("pairs") or profile_rt.primary_pairs()
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
    from .. import profile_rt
    out = []
    for store_id, product_id in ctx.get("pairs") or [
            (profile_rt.primary_store(), profile_rt.primary_product())]:
        twin = simulate.build_twin(product_id, store_id, start, as_of, forecast_kind="dow")
        prop = policy.propose(twin, product_id, store_id)
        if prop:                                   # 기준선을 이긴 제안만
            out.append(generator.policy_card(prop, agent="replenish_agent"))
    return out


def allocation_agent(ctx: dict) -> list[int]:
    """생산 완료 이벤트 — 예측 비중대로 매장 배분안."""
    from .. import profile_rt
    as_of = ctx["run_date"]
    product_id = ctx.get("product_id") or profile_rt.primary_product()
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
    if not db.table_exists("anomaly_scores"):
        raise runtime.NotReady(
            "이상탐지 점수 테이블 없음 — 센서·정비 데이터 축적 후 M4 이상탐지가 만들면 시작")
    as_of = ctx["run_date"]
    alerts = db.query(
        "SELECT * FROM anomaly_scores WHERE is_alert=1 AND date_key=?", (as_of,))
    out = []
    for a in alerts:
        eq = a["equipment_id"]
        rep = anomaly.weekly_hit_report(eq)
        # 연속 경보 일수 — 3일 이상이면 '점검'이 아니라 '계획 정비'를 제안한다
        streak = db.scalar("""
            SELECT COUNT(*) FROM anomaly_scores
            WHERE equipment_id=? AND is_alert=1
              AND date_key > date(?, '-5 days') AND date_key <= ?""",
            (eq, as_of, as_of)) or 1
        planned = streak >= 3
        proposal = (f"{eq} 연속 {streak}일 이상 신호 — 48시간 내 계획 정비(부하 낮은 "
                    f"야간대) 제안" if planned
                    else f"{eq} 이상 신호 — 점검(온도계 교정·구동부 확인) 제안")
        card = {
            "kind": "equip_alert", "agent": "equip_alert_agent",
            "proposal": proposal,
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
                         "equipment_id": eq, "date": a["date_key"],
                         "alert_streak_days": int(streak),
                         "recommendation": "planned_maintenance" if planned else "inspection"},
            "alternatives": [{"name": "관망", "why_not": "과거 고장 전 동일 패턴 — 선행 정비가 저비용"}],
            "approver": "카드 승인자",
        }
        out.append(jcards.create(card))
    return out


def production_plan_agent(ctx: dict) -> list[int]:
    """⑥ 생산계획(2단계 확장) — 익일 수요 예측을 라인 용량 안에서 생산 오더로.

    용량 = 라인별 과거 최대 일 계획량 × 1.1. 초과분은 '용량 초과' 경고와 함께
    감축안을 제시 — 결정은 언제나 카드 승인으로."""
    _require_model("demand_forecast")
    as_of = ctx["run_date"]
    pred = forecast.predict(as_of)
    next_day = pred["date_key"].min()
    day = pred[pred["date_key"] == next_day]
    by_prod = day.groupby("product_id")[["p50", "p90"]].sum().reset_index()
    if by_prod.empty:
        return []
    lines = db.df("""
        SELECT product_id, line_id, MAX(daily) AS cap FROM (
          SELECT product_id, line_id, date_key, SUM(qty_planned) AS daily
          FROM fact_production GROUP BY product_id, line_id, date_key)
        GROUP BY product_id, line_id""")
    line_cap = db.df("""
        SELECT line_id, MAX(daily)*1.1 AS cap FROM (
          SELECT line_id, date_key, SUM(qty_planned) AS daily
          FROM fact_production GROUP BY line_id, date_key)
        GROUP BY line_id""").set_index("line_id")["cap"]
    plan, warn = [], []
    load = {l: 0.0 for l in line_cap.index}
    for r in by_prod.itertuples():
        lrow = lines[lines["product_id"] == r.product_id]
        line = lrow.iloc[0]["line_id"] if len(lrow) else "L1"
        qty = float(r.p50) * 1.03                     # 폐기 여유 3%
        load[line] = load.get(line, 0) + qty
        plan.append({"product_id": r.product_id, "line_id": line,
                     "qty": round(qty), "p90": round(float(r.p90))})
    for line, used in load.items():
        cap = float(line_cap.get(line, used))
        if used > cap:
            warn.append(f"{line} 용량 초과: 계획 {used:.0f} > 용량 {cap:.0f} — "
                        f"저마진 품목 감축 또는 조 추가 검토")
    narrative = "\n".join(
        [f"{p['product_id']} {p['qty']}개({p['line_id']}) — 예측 P50+여유 3%. "
         f"[근거: demand_forecast 예측 {next_day}]" for p in plan[:6]]
        + [f"경고: {w} [근거: fact_production 라인 용량]" for w in warn])
    card = {
        "kind": "production_plan", "agent": "production_plan_agent",
        "proposal": f"{next_day} 생산계획 — {len(plan)}개 품목, 총 "
                    f"{sum(p['qty'] for p in plan):,}개"
                    + (f" (용량 경고 {len(warn)}건)" if warn else ""),
        "narrative": narrative,
        "values": [{"name": f"생산 {p['product_id']}", "value": p["qty"], "unit": "EA",
                    "source": f"demand_forecast P50×1.03 ({next_day})"} for p in plan],
        "range": {"total_p50": sum(p["qty"] for p in plan),
                  "total_p90": sum(p["p90"] for p in plan)},
        "evidence": {"kind": "forecast", "store_id": "ALL", "product_id": "ALL",
                     "plan_date": next_day, "plan": plan, "capacity_warnings": warn,
                     "daily": day.to_dict("records")[:10]},
        "alternatives": [
            {"name": "P90 기준 생산", "why_not": "신선 폐기 급증 — 유통기한 1일"},
            {"name": "전일 실적 반복", "why_not": "요일·행사 변동 무시"}],
        "approver": "카드 승인자",
    }
    return [jcards.create(card)]


def knowledge_agent(ctx: dict) -> list[int]:
    """⑤ 지식검증 — Rule 승격 상신 + 승격된 규칙의 SOP 개정 제안(3단계 심화).

    승격은 지식의 '고정', SOP 개정은 지식의 '작업 표준화' — 규칙이 문장으로
    남지 않고 현장 절차가 되게 한다."""
    subs = confidence.check_thresholds()
    out = []
    # 승격 완료 규칙 중 SOP 개정 카드가 아직 없는 것 → 개정 제안
    for rule in confidence.rules("promoted"):
        already = db.one(
            "SELECT 1 FROM judgment_cards WHERE kind='sop_revision' "
            "AND evidence_json LIKE ?", (f'%{rule["rule_id"]}%',))
        if already:
            continue
        dims = rule["dims"]
        from ..graph import evidence as ev
        where, params = ev._dims_filter_sql(dims)
        top_sop = db.one(
            f"SELECT sop_id, COUNT(*) n FROM fact_defect WHERE {where} "
            f"AND sop_id IS NOT NULL GROUP BY sop_id ORDER BY n DESC LIMIT 1", params)
        if not top_sop:
            continue
        sop_id = top_sop["sop_id"]
        cond = " × ".join(f"{k}={v}" for k, v in dims.items())
        card = {
            "kind": "sop_revision", "agent": "knowledge_agent",
            "proposal": f"{sop_id} 개정 제안 — '{cond} 조건 투입 전 사전 점검' 항목 추가",
            "narrative": "\n".join([
                f"승격 규칙: {confidence.rule_text(dims)} [근거: Rule:{rule['rule_id']}]",
                f"이 조합의 불량이 {sop_id} 작업에서 {top_sop['n']}건 확인되었습니다. "
                f"[근거: fact_defect sop_id 집계]",
                "규칙이 문장으로만 남으면 담당자가 바뀔 때 사라집니다 — 표준작업에 "
                "점검 항목으로 고정할 것을 제안합니다. [근거: 커스터디 원칙(구조가 지킨다)]"]),
            "values": [{"name": "관련 불량 건수", "value": int(top_sop["n"]),
                        "source": "fact_defect 집계"}],
            "evidence": {"kind": "rule", "rule_key": rule["rule_id"],
                         "sop_id": sop_id, "dims": dims},
            "alternatives": [{"name": "구두 전파", "why_not": "교대·이직 시 소실 — 재발 반복"}],
            "approver": "카드 승인자",
        }
        out.append(jcards.create(card))
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
    "production_plan_agent": "트리거: 일 배치 05:30 · 입력: 익일 예측+라인 용량(fact_production) · 카드: 품목×라인 생산 오더(용량 경고 포함) · 승인자: 카드 승인자",
    "demand_agent": "트리거: 일 배치 07:00 · 입력: 특징 저장소 · 호출: demand_forecast 모델 · 카드: 7일 발주 기준수량 · 승인자: 카드 승인자",
    "replenish_agent": "트리거: 주 1회(월) · 입력: fact_sales 90일 · 호출: InventoryTwin+정책 탐색 · 카드: 정책 변경(기준선 우위 시만) · 승인자: 카드 승인자",
    "allocation_agent": "트리거: 생산 완료 이벤트 · 입력: fact_production 금일 · 호출: 판매 비중 · 카드: 매장 배분안 · 승인자: 카드 승인자",
    "equip_alert_agent": "트리거: 이상 점수 임계 이벤트 · 입력: anomaly_scores · 호출: 감지기+적중 리포트 · 카드: 점검 제안 · 승인자: 카드 승인자",
    "knowledge_agent": "트리거: 확신도 임계 이벤트 · 입력: causal_candidates · 호출: confidence 루프 · 카드: Rule 승격 상신 · 승인자: 카드 승인자",
}


def register_all() -> None:
    runtime.register("production_plan_agent", "daily", production_plan_agent,
                     SPECS["production_plan_agent"])
    runtime.register("demand_agent", "daily", demand_agent, SPECS["demand_agent"])
    runtime.register("replenish_agent", "weekly", replenish_agent, SPECS["replenish_agent"])
    runtime.register("allocation_agent", "event:production_done", allocation_agent,
                     SPECS["allocation_agent"])
    runtime.register("equip_alert_agent", "event:anomaly", equip_alert_agent,
                     SPECS["equip_alert_agent"])
    runtime.register("knowledge_agent", "event:confidence", knowledge_agent,
                     SPECS["knowledge_agent"])
