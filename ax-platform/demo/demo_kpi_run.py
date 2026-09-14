"""프로젝트 정의 → 판단 → KPI 달성도까지 전 과정 실행(합성 데모 위에서)."""
import os, sys, json
SP = "/tmp/claude-0/-home-user-thirdbrain-web/bc639c69-a342-56eb-af6c-6a89fd170e25/scratchpad"
os.environ.update(AXP_DATA=SP + "/e2e_out", AXP_DB="sqlite", AXP_PROFILE="taesungdang")
sys.path.insert(0, "/home/user/thirdbrain-web/ax-platform/core")
from axp import projects, db

projects.init()

# ── 1. 프로젝트 정의 — 경영 목표 KPI(수기) + 기술 영역 KPI(자동) ──
if not projects.listing():
    p = projects.create(
        "AX 통합 성과 시연 1차",
        "수요예측·설비예지·재고로 결품·폐기·불량을 함께 줄이고 생산성 향상",
        "이형근",
        areas=["demand", "inventory", "production", "equipment"],
        objectives=[
            {"key": "productivity", "target": 20.0},   # 생산성 향상 목표 20%
            {"key": "cost",         "target": 10.0},   # 원가 절감 목표 10%
            {"key": "delivery",     "target": 15.0},   # 납기 단축 목표 15%
            {"key": "quality",      "target": 30.0},   # 품질(불량 감소) 목표 30%
        ])
else:
    p = projects.listing()[0]
pid = p["project_id"]

# ── 2. 기술 영역 KPI 자동 측정(fact_*에서) ──
r = projects.measure_all(pid)
print(f"자동 측정: 실측 {r['measured']}건 · 측정 전 {r['pending']}건")

# 자동 측정된 기술 KPI에 목표 설정 → 달성/미달 판정이 보이도록
TECH_TARGETS = {"plan_adherence": 95.0, "forecast_bias": 3.0, "scrap_rate": 2.0,
                "defect_rate": 3.0, "corrective_events": 2.0, "wape": 12.0,
                "stockout_days": 3.0, "mo_lead_days": 2.0, "mttr_min": 60.0}
for k in projects.get(pid)["kpis"]:
    if k["area"] != projects.OBJ_AREA and k["kpi_code"] in TECH_TARGETS \
            and projects.latest(k["kpi_id"]):
        projects.set_target(k["kpi_id"], TECH_TARGETS[k["kpi_code"]], "이형근")

# ── 3. 경영 목표 KPI 수기 실적 기록(현장 보고 가정) ──
actuals = {"productivity": 22.5, "cost": 8.0, "delivery": 18.0, "quality": 34.0}
for k in projects.get(pid)["kpis"]:
    if k["area"] == projects.OBJ_AREA and k["kpi_code"] in actuals:
        projects.record_value(k["kpi_id"], actuals[k["kpi_code"]], by="현장보고")

# ── 4. KPI 달성도 표 산출 ──
rows = []
for k in projects.get(pid)["kpis"]:
    m = projects.latest(k["kpi_id"])
    st = projects.kpi_status(k)
    rows.append({
        "area": projects.area_label(k["area"]),
        "name": k["kpi_name"],
        "unit": k["unit"],
        "target": k["target"],
        "actual": (round(m["value"], 2) if m else None),
        "direction": ("낮을수록 좋음" if k["direction"] == "down" else "높을수록 좋음"),
        "status": st,
    })

# 판단 카드 요약
cards = db.query("SELECT kind, proposal, status FROM judgment_cards ORDER BY card_id")
card_rows = [{"kind": c["kind"], "proposal": c["proposal"], "status": c["status"]} for c in cards]

out = {"project": {"id": pid, "name": p["name"], "goal": p["goal"]},
       "kpis": rows, "cards": card_rows,
       "measured": r["measured"], "pending": r["pending"]}
json.dump(out, open(SP + "/kpi_result.json", "w"), ensure_ascii=False, indent=1)

print("\n=== KPI 달성도 ===")
for x in rows:
    a = f"{x['actual']}" if x["actual"] is not None else "측정 전"
    print(f"  [{x['area']}] {x['name']}: 목표 {x['target']} · 실적 {a} {x['unit']} → {x['status']}")
print(f"\n판단 카드 {len(card_rows)}건")
