"""E2E 수직 완주 — 얇은 수직 완주의 실연: M0 지반부터 판단 카드 환류까지.

계획서 1단계 12주를 한 번의 실행으로 압축한다:
  G1 착수 → M0 커스터디 → M1 수집 → M2 표준화·특징 → M3 마이닝·브리핑
  → M4 학습(카드) → M5 그래프·확신도 → M6 판단 조립(회귀 10선)
  → M7 에이전트·승인함 → 첫 카드 승인·환류 → War Room → G4 수용 시험.

실행: python -m demo.run_e2e   (demo/out 을 새로 만든다)
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))

from axp import config  # noqa: E402

AS_OF = "2026-07-31"          # '오늘' — 이후 7일을 예측한다
STEWARD = "박스튜어드"
APPROVER = "김승인"
LEAD = "플랫폼 리드"


def step(title):
    print(f"\n{'='*8} {title} {'='*(60-len(title))}")


def main(fresh: bool = True) -> dict:
    t0 = time.time()
    summary: dict = {}

    if fresh and config.DATA.exists():
        shutil.rmtree(config.DATA)
    config.ensure_dirs()

    step("0. 합성 데이터(가상 제빵회사) 생성")
    import demo.generate_data as gen
    gen.main()

    step("1. M0 커스터디 — 대장·반출 게이트 초기화")
    from axp.custody import ledger, export_gate, contracts
    ledger.init(); export_gate.init()
    ledger.register("registry/contracts", "document", "registry/contracts/", STEWARD,
                    note="데이터 계약 7건")
    n_contracts = len(contracts.load_all())
    print(f"계약 {n_contracts}건 검증 통과, 자산 대장 가동")
    summary["contracts"] = n_contracts

    step("2. M1 수집 — Odoo CDC · 엑셀 · 장표 · IoT")
    from axp.ingest import odoo_cdc, excel_uploader as xu, forms, iot
    import pandas as pd
    counts = odoo_cdc.sync()
    recon = odoo_cdc.reconcile()
    print("CDC:", {k: v for k, v in counts.items() if v}, "| 정합:", recon["ok"])
    p = config.DATA / "inbox" / "본점_판매집계.xlsx"
    r1 = xu.upload(p, "이현업")
    if r1["status"] == "needs_mapping":
        xu.save_mapping(r1["profile"]["fingerprint"], "sales_summary",
                        {"판매일": "date", "매장": "store_id", "품목": "product_id",
                         "수량": "qty"}, "이현업")
    r2 = xu.upload(p, "이현업")
    p2 = config.DATA / "inbox" / "프로모션_달력.xlsx"
    r3 = xu.upload(p2, "이현업")
    if r3["status"] == "needs_mapping":
        xu.save_mapping(r3["profile"]["fingerprint"], "promo_calendar",
                        {"시작일": "date_start", "종료일": "date_end", "제품코드": "product_id",
                         "행사명": "promo_name", "할인율": "discount_pct"}, "이현업")
        r3 = xu.upload(p2, "이현업")
    print(f"엑셀: 판매집계 {r2['rows_ok']}행(2회째 자동 매핑) · 프로모션 {r3['rows_ok']}행")
    forms.submit("scrap", AS_OF, "김현장", "S-MAIN",
                 {"line_id": "S-MAIN", "product_id": "P-CREAM", "qty": 5,
                  "reason": "유통기한", "memo": "마감 소진 실패 — 금요일 과다 발주 느낌"})
    d = forms.submit_ocr_draft("inspection", AS_OF, "L2",
                               {"equipment_id": "OVEN-2", "item": "온도계 교정",
                                "result": "주의", "memo": "편차 커 보임"})
    forms.confirm_ocr(d, STEWARD)
    n_iot = iot.ingest_frame(pd.read_csv(config.DATA / "sensor_replay.csv"))
    print(f"장표 2건(OCR 1건 사람 확정) · IoT {n_iot:,}행")
    summary["m1"] = {"cdc_ok": recon["ok"], "iot_rows": n_iot}

    step("3. M2 표준 데이터셋 — 변환·품질 게이트·특징 20종")
    from axp.dataset import transform, quality, features, codemap
    tcounts = transform.run_all()
    q = quality.daily_report(AS_OF)
    (config.ARTIFACTS / "quality_report.md").write_text(
        quality.render_md(q), encoding="utf-8")
    pend = codemap.pending()
    if pend:                                          # 스튜어드 격리 확정 시연
        codemap.confirm(pend[0]["q_id"], "P-PIE", STEWARD)
    n_feat = features.materialize(AS_OF, horizon=7)
    print(f"사실 6계열 {sum(v for k, v in tcounts.items() if k.startswith('fact'))}행 · "
          f"품질 {'통과' if q['ok'] else '위반'} · 미매핑 {q['unmapped_rate']:.2%} · "
          f"특징 {n_feat:,}행")
    summary["m2"] = {"quality_ok": q["ok"], "unmapped_rate": q["unmapped_rate"]}

    step("4. M3 스튜디오 — EDA 6종·야간 마이닝·브리핑·보드")
    from axp.studio import eda, mining, briefing, boards
    eda.run_pack("2025-06-01", "2025-08-31")
    for rd in ("2025-08-15", "2025-09-01", "2025-09-20"):
        mining.nightly(rd)
    brief = briefing.build("2025-09-20")
    boards.field_board(AS_OF); boards.exec_board(AS_OF)
    top = mining.new_candidates()[:1]
    print("최상위 마이닝 후보:", top[0]["dims"] if top else "-",
          f"(lift ×{top[0]['lift']:.1f})" if top else "")

    step("5. M4 학습 엔진 — 수요예측·분류·이상탐지·Twin 정책")
    from axp.learn import forecast, classify, anomaly, simulate, policy
    fr = forecast.train_and_register(AS_OF)
    best = fr["comparison"].iloc[0]
    base = fr["comparison"][fr["comparison"]["model"] == "ewm_7"].iloc[0]
    print(f"수요예측: {best['model']} WAPE {best['wape']:.1%} "
          f"(출발선 ewm {base['wape']:.1%}) — 모델 카드 v1 등록")
    cl = classify.train_and_register("2024-09-01", "2026-03-01", "2026-08-31")
    an = anomaly.train_and_register("OVEN-2", "2026-03-05", "2026-05-20")
    anomaly.score_range("OVEN-2", "2026-03-05", "2026-08-31")
    hit = anomaly.weekly_hit_report("OVEN-2")
    print(f"이상탐지: 고장 {hit['failures']}건 중 {hit['detected']}건 선행 감지 "
          f"(선행 {hit['median_lead_days']}일)")
    rv = simulate.replay_validate("P-CREAM", "S-MAIN", "2026-05-01", AS_OF)
    print(f"Twin 재생 검증: {'통과' if rv['pass'] else '실패'} "
          f"(sim {rv['sim_scrap_rate']:.1%} vs 실제 {rv['actual_scrap_rate']:.1%})")
    summary["m4"] = {"forecast_wape": float(best["wape"]),
                     "baseline_wape": float(base["wape"]),
                     "anomaly_recall": hit["recall"], "twin_replay": rv["pass"]}

    step("6. M5 지식그래프 — 적재·백필·확신도 루프")
    from axp.graph import store, loader, confidence, evidence
    loader.load_dimensions()
    loader.backfill_defects("2024-09-01", "2026-08-31")
    grecon = loader.reconcile("2024-09-01", "2026-08-31")
    for rd in ("2025-08-15", "2025-09-01", "2025-09-20"):
        confidence.ingest_mining(rd)
    confidence.ingest_model_importance(classify.model_importance_candidates())
    print(f"그래프 {store.stats()['total_nodes']:,}노드 대사 {'일치' if grecon['ok'] else '불일치'} · "
          f"임계 도달 후보 대기")
    summary["m5"] = {"reconcile": grecon["ok"]}

    step("7. M6 판단 조립 — 회귀 질의 10선")
    from axp.judge import regression
    # Rule 승격 전이므로 규칙 질의는 후보로 답한다 — 승격은 M7 지식 카드로
    from axp.agents import five, runtime, inbox, promotion, warroom
    five.register_all()
    shadow = runtime.run_all({"run_date": AS_OF}, shadow=True)
    n_shadow = sum(len(r.get("cards", [])) for r in shadow)
    print(f"그림자 모드: 에이전트 5종 → 카드 {n_shadow}건 (승인 대기만)")

    step("8. M7 승인함 — 지식 승격·수요 카드 승인·환류")
    from axp.judge import cards as jcards
    # 지식 카드(Rule 승격 상신) 승인 → Rule 고정
    know = [c for c in inbox.pending() if c["kind"] == "knowledge"]
    if know:
        inbox.decide(know[0]["card_id"], APPROVER, "card_approver", True)
        print("Rule 승격:", confidence.rules("promoted")[0]["rule_id"])
    reg = regression.run()
    print(f"회귀 10선: {reg['n_pass']}/{reg['n_total']} {'통과' if reg['pass'] else '실패'}")
    summary["m6"] = {"regression": f"{reg['n_pass']}/{reg['n_total']}"}
    # 수요 카드 1건 검토→승인→환류, 1건 반려(사유)
    demand_cards = [c for c in inbox.pending() if c["kind"] == "demand_forecast"]
    cid = demand_cards[0]["card_id"]
    inbox.start_review(cid, APPROVER, "card_approver")
    dec = inbox.decide(cid, APPROVER, "card_approver", True)
    print("첫 실승인·환류:", dec["feedback"]["written"][0]["param"])
    if len(demand_cards) > 1:
        inbox.decide(demand_cards[1]["card_id"], APPROVER, "card_approver", False,
                     "시점 부적절", "명절 주간 별도 계획 예정")
    ev = evidence.why(jcards.get(cid)["evidence"])
    print("'왜?' 응답 — 모델 카드:", ev["model_card"]["model_id"],
          ev["model_card"]["version"])
    summary["m7"] = {"first_feedback": dec["feedback"]["written"][0]["param"],
                     "audit_rows": len(inbox.audit())}

    step("8b. 설비예지 데모 — 경보일의 점검 카드(2단계 앱 미리보기)")
    # OVEN-2 고장(6/18) 2주 전 드리프트 구간의 경보일로 설비경보 에이전트 실행
    from axp import db
    alert_day = db.scalar(
        "SELECT MIN(date_key) FROM anomaly_scores WHERE is_alert=1 "
        "AND equipment_id='OVEN-2' AND date_key>='2026-06-01'")
    if alert_day:
        r_eq = runtime.run_agent("equip_alert_agent", {"run_date": alert_day})
        if r_eq.get("cards"):
            eq_cid = r_eq["cards"][0]
            inbox.decide(eq_cid, APPROVER, "card_approver", True)
            flag = db.one("SELECT * FROM odoo_params WHERE param_key LIKE 'inspection_flag%'")
            print(f"경보일 {alert_day}: 점검 카드 {eq_cid} 승인 → "
                  f"{flag['param_key'] if flag else '환류 없음'} (고장 13일 전 선행 신호)")
            summary["equip_alert"] = {"alert_day": alert_day, "card": eq_cid}

    step("9. War Room·승급·산출물")
    wr = warroom.render(AS_OF)
    pr = promotion.request("demand_forecast", 2000, 0.3, LEAD)
    if pr["status"] == "requested":
        promotion.decide(pr["promo_id"], APPROVER, True)
    store.export_cypher(str(config.ARTIFACTS / "kg_export.cypher"))
    ledger.register("demand_forecast", "model",
                    "artifacts/models/demand_forecast_v1.pkl", "ML 엔지니어")
    ledger.register("war_room", "document", wr, LEAD)
    print("War Room:", wr)

    summary["elapsed_s"] = round(time.time() - t0, 1)
    (config.ARTIFACTS / "e2e_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2,
                   default=lambda o: bool(o) if hasattr(o, "__bool__") else str(o)),
        encoding="utf-8")
    print(f"\n수직 완주 완료 — {summary['elapsed_s']}s. 요약: artifacts/e2e_summary.json")
    return summary


if __name__ == "__main__":
    main(fresh="--keep" not in sys.argv)
