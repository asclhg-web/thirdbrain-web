"""야간 배치 오케스트레이션 — axp-scheduler 컨테이너의 진입점.

순서(계획서 '이벤트와 배치의 이원화'의 배치 절반):
  01:00 CDC 정합 → 02:00 변환 → 02:30 품질 리포트 → 03:00 그래프 적재
  → 03:30 마이닝 → 04:00 확신도 루프 → 06:30 에이전트(일 배치) → 07:00 브리핑
실행: python -m axp.scheduler --once <날짜>   (테스트: 한 사이클)
      python -m axp.scheduler --schedule      (prod: 매일 루프)
실패한 단계는 경보를 남기고 다음 단계로 — 침묵 실패 금지.
"""
from __future__ import annotations

import sys
import time
from datetime import date, datetime, timedelta

from . import common


def run_cycle(run_date: str, shadow: bool = False) -> dict:
    results: dict[str, str] = {}

    def stage(name: str, fn):
        try:
            fn()
            results[name] = "ok"
        except Exception as e:  # noqa: BLE001
            results[name] = f"error: {e}"
            common.alert("crit", "scheduler", f"{name} 실패: {e}")

    from .ingest import odoo_cdc, iot
    stage("cdc_sync", lambda: odoo_cdc.sync())
    stage("cdc_reconcile", lambda: odoo_cdc.reconcile())
    stage("iot_gap_check", lambda: iot.gap_check())

    from .dataset import transform, quality, features, validation
    stage("transform", lambda: transform.run_all())
    stage("quality_report", lambda: quality.daily_report(run_date))
    stage("cross_validation", lambda: validation.excel_vs_ledger())
    stage("features", lambda: features.materialize(run_date, horizon=7))

    from .graph import loader, confidence
    start = (date.fromisoformat(run_date) - timedelta(days=3)).isoformat()
    stage("graph_load", lambda: (loader.load_dimensions(),
                                 loader.backfill_defects(start, run_date)))

    from .studio import mining, briefing, boards, knowledge
    stage("mining", lambda: mining.nightly(run_date))
    stage("confidence", lambda: confidence.ingest_mining(run_date))
    stage("memo_candidates",
          lambda: confidence.ingest_model_importance(knowledge.surge_candidates(run_date)))

    # 주 1회(월요일): 재학습 판정·개방 포맷 내보내기
    if date.fromisoformat(run_date).weekday() == 0:
        from .learn import retrain
        from .dataset import export
        stage("weekly_retrain", lambda: retrain.weekly(run_date))
        stage("rule_review", lambda: confidence.review_promoted(run_date))
        stage("parquet_export", lambda: export.export_parquet())
        # 격주(짝수 ISO 주): 리스크 5 자동 점검
        if date.fromisoformat(run_date).isocalendar().week % 2 == 0:
            from .agents import risk
            stage("risk_check", lambda: risk.check_all(run_date))

    from .agents import five, runtime, promotion
    five.register_all()
    stage("agents", lambda: runtime.run_all({"run_date": run_date}, shadow=shadow))
    stage("promotion_monitor", lambda: promotion.monitor_and_demote())

    stage("briefing", lambda: briefing.build(run_date))
    stage("boards", lambda: (boards.field_board(run_date), boards.exec_board(run_date)))

    from .agents import warroom
    stage("warroom", lambda: warroom.render(run_date))
    try:
        from . import notify
        notify.cycle_summary(run_date, results)
    except Exception:
        pass
    return results


def main() -> None:
    args = sys.argv[1:]
    if "--once" in args:
        run_date = args[args.index("--once") + 1] if len(args) > args.index("--once") + 1 \
            else date.today().isoformat()
        res = run_cycle(run_date, shadow="--shadow" in args)
        bad = {k: v for k, v in res.items() if v != "ok"}
        print("cycle:", "전 단계 정상" if not bad else f"실패 {bad}")
        sys.exit(0 if not bad else 1)
    if "--schedule" in args:
        print("스케줄 모드 — 매일 01:00 사이클 (Ctrl+C 종료)")
        while True:
            now = datetime.now()
            nxt = (now + timedelta(days=1)).replace(hour=1, minute=0, second=0)
            time.sleep(max(60, (nxt - now).total_seconds()))
            run_cycle(date.today().isoformat())
    print(__doc__)


if __name__ == "__main__":
    main()
