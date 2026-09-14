"""데모 KPI 시딩 — 프로젝트 정의(경영 목표 + 기술 영역) → 측정 → 달성도.

환경변수(AXP_DATA·AXP_DB·AXP_PG_DSN·AXP_PROFILE)로 현재 데이터셋에 붙는다.
demo.run_e2e 로 fact_* 가 적재된 뒤 실행하면 성과 화면이 즉시 채워진다.
멱등: 이미 같은 이름의 프로젝트가 있으면 건너뛴다.

실행: python -m demo.demo_kpi_run   (또는 python demo/demo_kpi_run.py)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
from axp import projects, db  # noqa: E402

NAME = "AX 통합 성과 시연 1차"
GOAL = "수요예측·설비예지·재고로 결품·폐기·불량을 함께 줄이고 생산성 향상"
OBJECTIVE_TARGETS = {"productivity": 20.0, "cost": 10.0, "delivery": 15.0, "quality": 30.0}
OBJECTIVE_ACTUALS = {"productivity": 22.5, "cost": 8.0, "delivery": 18.0, "quality": 34.0}
TECH_TARGETS = {"plan_adherence": 95.0, "forecast_bias": 3.0, "scrap_rate": 2.0,
                "defect_rate": 3.0, "corrective_events": 2.0, "wape": 12.0,
                "stockout_days": 3.0, "mo_lead_days": 2.0, "mttr_min": 60.0}

# 수기 데모 표본 — 자동 원천(서빙 모델·재고 스냅샷·실 MO 원장)이 아직 없는
# 지표는 '측정 전'으로 비어 보인다. 대표 지침("일단 수기방식으로 셋팅")에 따라
# 현장 보고 가정의 표본값을 넣어 성과 화면을 채운다. 원천이 연결되면
# measure_all 이 실측을 덮어써(이력 최신값 우선) 자동 전환된다.
DEMO_TECH_SAMPLES = {"wape": 7.0, "stockout_days": 2.0, "mo_lead_days": 1.8}


def main() -> dict:
    projects.init()
    existing = next((p for p in projects.listing() if p["name"] == NAME), None)
    if existing:
        print(f"이미 존재 — 프로젝트 #{existing['project_id']} '{NAME}' (건너뜀)")
        pid = existing["project_id"]
    else:
        p = projects.create(
            NAME, GOAL, "이형근",
            areas=["demand", "inventory", "production", "equipment"],
            objectives=[{"key": k, "target": t} for k, t in OBJECTIVE_TARGETS.items()])
        pid = p["project_id"]
        print(f"프로젝트 생성 #{pid} — 경영목표 4 · 기술영역 4")

    # 재고 일 스냅샷 — 서버1(PG)에 stock_quant가 복제돼 있으면 결품 일수를
    # 실측으로 잡는다(sqlite·미복제 환경은 skip → 아래 수기 표본이 채움).
    snap = projects.snapshot_stock()
    if snap.get("products"):
        print(f"재고 스냅샷: {snap['products']}품목 @ {snap['date_key']}")

    # 기술 KPI 자동 측정(fact_*에서) + 목표 설정
    r = projects.measure_all(pid)
    print(f"자동 측정: 실측 {r['measured']}건 · 측정 전 {r['pending']}건")
    for k in projects.get(pid)["kpis"]:
        if k["area"] != projects.OBJ_AREA and k["kpi_code"] in TECH_TARGETS \
                and projects.latest(k["kpi_id"]) and k["target"] is None:
            projects.set_target(k["kpi_id"], TECH_TARGETS[k["kpi_code"]], "이형근")

    # 경영 목표 수기 실적(현장 보고 가정) — 없을 때만
    for k in projects.get(pid)["kpis"]:
        if k["area"] == projects.OBJ_AREA and k["kpi_code"] in OBJECTIVE_ACTUALS \
                and not projects.latest(k["kpi_id"]):
            projects.record_value(k["kpi_id"], OBJECTIVE_ACTUALS[k["kpi_code"]], by="현장보고")

    # 기술 KPI 중 자동 원천이 아직 없어 '측정 전'인 지표는 수기 표본으로 채운다
    # (달성도 화면이 비지 않도록) — 목표도 함께 고정한다.
    for k in projects.get(pid)["kpis"]:
        if k["kpi_code"] in DEMO_TECH_SAMPLES and not projects.latest(k["kpi_id"]):
            if k["target"] is None and k["kpi_code"] in TECH_TARGETS:
                projects.set_target(k["kpi_id"], TECH_TARGETS[k["kpi_code"]], "이형근")
            projects.record_value(k["kpi_id"], DEMO_TECH_SAMPLES[k["kpi_code"]],
                                  by="현장보고(데모 표본)")

    print("\n=== KPI 달성도 ===")
    done = 0
    for k in projects.get(pid)["kpis"]:
        m = projects.latest(k["kpi_id"])
        st = projects.kpi_status(k)
        done += st == "달성"
        val = f"{m['value']:g}" if m else "측정 전"
        print(f"  [{projects.area_label(k['area'])}] {k['kpi_name']}: "
              f"목표 {k['target']} · 실적 {val} {k['unit']} → {st}")
    print(f"\n달성 {done}건 · 판단 카드 {db.scalar('SELECT COUNT(*) FROM judgment_cards')}건")
    return {"project_id": pid, "achieved": done}


if __name__ == "__main__":
    main()
