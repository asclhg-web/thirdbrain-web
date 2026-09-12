"""M0-P 프로젝트·KPI 센터 — 정의→요구사항→모듈·알고리즘→KPI→성과→피드백 루프 (P7).

7단계의 핵심 임팩트: 프로젝트를 정의하고, 5대 지능화 요구사항에서 우리
회사에 맞는 모듈·알고리즘을 고르고, KPI를 선정해 대시보드로 성과를 보고,
미달 KPI에 개선 제안(판단 카드)을 받아 사람이 승인·조정하면 다시 측정되는
무한 개선 루프.

정직성 원칙: KPI는 '측정 가능'과 '측정 전'을 구분한다 — 사실 테이블에서
계산할 수 없는 지표는 값을 지어내지 않고 어떤 데이터가 더 필요한지 말한다.
"""
from __future__ import annotations

import json

from . import common, db

DDL = """
CREATE TABLE IF NOT EXISTS axp_projects (
  project_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, goal TEXT DEFAULT '', owner TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'active'
         CHECK (status IN ('active','review','closed')),
  areas TEXT NOT NULL DEFAULT '[]',        -- 선택 요구사항 영역 코드 JSON
  modules TEXT NOT NULL DEFAULT '[]',      -- [{area, module, algorithm}] JSON
  created_at TEXT, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS axp_project_kpis (
  kpi_id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  area TEXT NOT NULL, kpi_code TEXT NOT NULL, kpi_name TEXT NOT NULL,
  unit TEXT DEFAULT '', direction TEXT NOT NULL DEFAULT 'down'
       CHECK (direction IN ('down','up')),
  baseline REAL, target REAL,
  status TEXT NOT NULL DEFAULT 'active'
         CHECK (status IN ('active','retired')),
  created_at TEXT
);
CREATE TABLE IF NOT EXISTS axp_kpi_measurements (
  kpi_id INTEGER NOT NULL, measured_at TEXT NOT NULL,
  value REAL, source TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS axp_kpi_feedback (
  fb_id INTEGER PRIMARY KEY AUTOINCREMENT,
  kpi_id INTEGER NOT NULL,
  action TEXT NOT NULL CHECK (action IN ('adjust_target','improve','keep')),
  note TEXT DEFAULT '', old_target REAL, new_target REAL,
  decided_by TEXT, created_at TEXT
);
"""

# ── 5대 지능화 요구사항 카탈로그 — 영역 → 플랫폼 실물 모듈·알고리즘·KPI ──
# module/algorithm은 이 플랫폼에 실제로 존재하는 구성요소만 적는다(정직성).
AREAS: dict[str, dict] = {
    "demand": {
        "name": "수요예측 지능화",
        "modules": [
            ("M4 수요예측", "GBM 분위수 회귀(P50/P90) + 명절·프로모션 특징량"),
            ("M4 콜드스타트", "신제품 유사군 이전 예측"),
            ("M7 수요 에이전트", "일 배치 발주 기준수량 카드(승인제)"),
        ],
        "kpis": [
            ("wape", "예측 오차(WAPE)", "%", "down"),
            ("forecast_bias", "예측 편향(실측-예측)", "%", "down"),
        ],
    },
    "inventory": {
        "name": "재고 최적화",
        "modules": [
            ("M7 재보충 에이전트", "예측 기반 재보충 제안 카드"),
            ("M1 로트 추적", "입고 실로트 결선·backfill(P5-I5)"),
        ],
        "kpis": [
            ("scrap_rate", "폐기(스크랩)율", "%", "down"),
            ("stockout_days", "결품 일수", "일", "down"),
        ],
    },
    "production": {
        "name": "생산계획·작업지시 지능화",
        "modules": [
            ("M7 생산계획 에이전트", "익일 수요를 라인 용량 안에서 생산 오더로"),
            ("P-06 Odoo 환류", "승인 카드 → Odoo MO/발주 초안"),
        ],
        "kpis": [
            ("plan_adherence", "계획 준수율(완료/계획)", "%", "up"),
            ("mo_lead_days", "생산 리드타임(착수→완료)", "일", "down"),
        ],
    },
    "equipment": {
        "name": "설비예지보전·품질·안전 지능화",
        "modules": [
            ("M4 이상탐지", "센서·이력 기반 이상 점수(Isolation Forest 계열)"),
            ("M7 설비 경보 에이전트", "임계 초과 시 점검 제안 카드"),
            ("M2 품질 게이트", "계약 기반 위반 검출 + 격리 큐"),
        ],
        "kpis": [
            ("mttr_min", "정비 평균 소요(분)", "분", "down"),
            ("defect_rate", "불량(스크랩)률", "%", "down"),
            ("corrective_events", "월 고장 정비 건수", "건", "down"),
        ],
    },
    "knowledge": {
        "name": "지식센터 지능화",
        "modules": [
            ("M5 지식그래프", "4M 연결 + 확신도 승격/강등 루프"),
            ("M6 질문(GraphRAG)", "'왜?'에 근거 사다리로 답"),
        ],
        "kpis": [
            ("promoted_rules", "승격 운영 규칙 수", "건", "up"),
            ("weekly_questions", "주간 질문 활용 수", "건", "up"),
        ],
    },
}


def init() -> None:
    db.executescript(DDL)


def create(name: str, goal: str, owner: str, areas: list[str],
           modules: list[dict] | None = None) -> dict:
    """프로젝트 정의 — 선택 영역의 카탈로그 KPI가 자동 등재된다(목표는 비움)."""
    init()
    name = (name or "").strip()
    if not name:
        raise ValueError("프로젝트 이름을 입력하세요.")
    bad = [a for a in areas if a not in AREAS]
    if bad or not areas:
        raise ValueError(f"요구사항 영역을 확인하세요: {bad or '선택 없음'}")
    if modules is None:                     # 기본: 선택 영역의 카탈로그 전 모듈
        modules = [{"area": a, "module": m, "algorithm": alg}
                   for a in areas for m, alg in AREAS[a]["modules"]]
    now = common.now_iso()
    with db.conn() as c:
        cur = c.execute(
            "INSERT INTO axp_projects (name, goal, owner, areas, modules, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (name, goal.strip(), owner, json.dumps(areas),
             json.dumps(modules, ensure_ascii=False), now, now))
        pid = cur.lastrowid
    for a in areas:
        for code, kname, unit, direction in AREAS[a]["kpis"]:
            db.execute(
                "INSERT INTO axp_project_kpis (project_id, area, kpi_code, kpi_name, unit, direction, created_at) "
                "VALUES (?,?,?,?,?,?,?)", (pid, a, code, kname, unit, direction, now))
    common.alert("info", "M0-P", f"프로젝트 정의: {name} (영역 {len(areas)}·KPI 자동 등재)")
    return get(pid)


def get(project_id: int) -> dict:
    init()
    row = db.one("SELECT * FROM axp_projects WHERE project_id=?", (project_id,))
    if not row:
        raise ValueError(f"프로젝트 {project_id} 없음")
    out = dict(row)
    out["areas"] = json.loads(out["areas"])
    out["modules"] = json.loads(out["modules"])
    out["kpis"] = db.query(
        "SELECT * FROM axp_project_kpis WHERE project_id=? AND status='active' ORDER BY kpi_id",
        (project_id,))
    return out


def listing() -> list[dict]:
    init()
    return db.query("SELECT * FROM axp_projects ORDER BY project_id DESC")


def set_target(kpi_id: int, target: float, by: str,
               baseline: float | None = None, note: str = "") -> None:
    """KPI 목표 설정·조정 — 조정 이력은 feedback에 남는다(무한 루프의 조정 단계)."""
    init()
    k = db.one("SELECT * FROM axp_project_kpis WHERE kpi_id=?", (kpi_id,))
    if not k:
        raise ValueError(f"KPI {kpi_id} 없음")
    db.execute("UPDATE axp_project_kpis SET target=?, baseline=COALESCE(?, baseline) "
               "WHERE kpi_id=?", (target, baseline, kpi_id))
    db.execute(
        "INSERT INTO axp_kpi_feedback (kpi_id, action, note, old_target, new_target, decided_by, created_at) "
        "VALUES (?,?,?,?,?,?,?)",
        (kpi_id, "adjust_target", note, k["target"], target, by, common.now_iso()))


def record_feedback(kpi_id: int, action: str, note: str, by: str) -> None:
    init()
    if action not in ("improve", "keep"):
        raise ValueError("action은 improve|keep")
    db.execute(
        "INSERT INTO axp_kpi_feedback (kpi_id, action, note, decided_by, created_at) "
        "VALUES (?,?,?,?,?)", (kpi_id, action, note, by, common.now_iso()))


# ── KPI 실측 엔진 — 사실 테이블에서 계산 가능한 것만, 나머지는 '측정 전' ──

def _m_wape() -> tuple[float | None, str]:
    try:
        from .learn import retrain
        import math
        v = retrain.recent_wape(common.now_iso()[:10])
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return None, "서빙 모델 학습 전 — 판매 데이터 축적 후 측정"
        return round(float(v) * 100, 2), "retrain.recent_wape(최근 28일 홀드아웃)"
    except Exception as e:  # noqa: BLE001
        return None, f"서빙 모델 학습 전({type(e).__name__}) — 판매 데이터 축적 후 측정"


def _m_scrap_rate() -> tuple[float | None, str]:
    prod = db.scalar("SELECT COALESCE(SUM(qty_done),0) FROM fact_production") or 0
    scrap = db.scalar(
        "SELECT COALESCE(SUM(qty_defect),0) FROM fact_defect WHERE defect_type='scrap'") or 0
    if prod <= 0:
        return None, "생산 실적 없음 — MO 완료 축적 후 측정"
    return round(scrap / prod * 100, 2), "fact_defect(scrap)/fact_production"


def _m_plan_adherence() -> tuple[float | None, str]:
    row = db.one("SELECT SUM(qty_planned) AS p, SUM(qty_done) AS d FROM fact_production")
    if not row or not row["p"]:
        return None, "생산 실적 없음 — MO 완료 축적 후 측정"
    return round(min(row["d"] / row["p"], 1.0) * 100, 2), "fact_production done/planned"


def _m_mttr() -> tuple[float | None, str]:
    v = db.scalar("SELECT AVG(duration_min) FROM fact_equipment_event "
                  "WHERE event_type='corrective' AND duration_min > 0")
    if v is None:
        return None, "고장 정비 이력 없음 — 정비 기록 축적 후 측정"
    return round(float(v), 1), "fact_equipment_event corrective 평균"


def _m_corrective_events() -> tuple[float | None, str]:
    from datetime import date, timedelta
    cutoff = (date.today() - timedelta(days=30)).isoformat()
    cnt = db.scalar("SELECT COUNT(*) FROM fact_equipment_event "
                    "WHERE event_type='corrective' AND date_key >= ?", (cutoff,))
    return float(cnt or 0), "fact_equipment_event 최근 30일"


def _m_promoted_rules() -> tuple[float | None, str]:
    if not db.table_exists("causal_candidates"):
        return None, "지식그래프 미구축"
    v = db.scalar("SELECT COUNT(*) FROM causal_candidates WHERE status='promoted'")
    return float(v or 0), "causal_candidates promoted"


_MEASURES = {
    "wape": _m_wape,
    "scrap_rate": _m_scrap_rate,
    "defect_rate": _m_scrap_rate,          # 규약: 불량률=스크랩 기준(Community)
    "plan_adherence": _m_plan_adherence,
    "mttr_min": _m_mttr,
    "corrective_events": _m_corrective_events,
    "promoted_rules": _m_promoted_rules,
    # 아래는 현재 사실 테이블로 계산 불가 — 필요한 데이터를 정직하게 말한다
    "forecast_bias": lambda: (None, "예측 로그 축적 후 측정(서빙 예측 대 실판매 대조)"),
    "stockout_days": lambda: (None, "재고 수준(stock_quant) 스냅샷 축적 후 측정"),
    "mo_lead_days": lambda: (None, "MO 착수·완료 시각 축적 후 측정(현재 완료일만 보존)"),
    "weekly_questions": lambda: (None, "질문 로그 집계 결선 후 측정"),
}


def measure(kpi_code: str) -> tuple[float | None, str]:
    fn = _MEASURES.get(kpi_code)
    if fn is None:
        return None, "측정식 미정의"
    return fn()


def measure_all(project_id: int) -> dict:
    """프로젝트 KPI 일괄 측정 — 측정치는 이력으로 쌓인다(차트의 원천)."""
    p = get(project_id)
    now = common.now_iso()
    out = {"measured": 0, "pending": 0}
    for k in p["kpis"]:
        value, source = measure(k["kpi_code"])
        if value is None:
            out["pending"] += 1
            continue
        db.execute("INSERT INTO axp_kpi_measurements (kpi_id, measured_at, value, source) "
                   "VALUES (?,?,?,?)", (k["kpi_id"], now, value, source))
        out["measured"] += 1
    return out


def series(kpi_id: int, limit: int = 30) -> list[dict]:
    init()
    rows = db.query(
        "SELECT measured_at, value FROM axp_kpi_measurements WHERE kpi_id=? "
        "ORDER BY measured_at DESC LIMIT ?", (kpi_id, limit))
    return list(reversed(rows))


def latest(kpi_id: int) -> dict | None:
    init()
    return db.one("SELECT measured_at, value, source FROM axp_kpi_measurements "
                  "WHERE kpi_id=? ORDER BY measured_at DESC LIMIT 1", (kpi_id,))


def kpi_status(k: dict) -> str:
    """달성 판정 — 목표 없음/측정 전/달성/미달."""
    m = latest(k["kpi_id"])
    if m is None:
        return "측정 전"
    if k["target"] is None:
        return "목표 미설정"
    ok = m["value"] <= k["target"] if k["direction"] == "down" else m["value"] >= k["target"]
    return "달성" if ok else "미달"
