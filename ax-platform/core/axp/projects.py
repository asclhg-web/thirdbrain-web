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
  m_id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 동일 초 다중 측정의 순서 보장
  kpi_id INTEGER NOT NULL, measured_at TEXT NOT NULL,
  value REAL, source TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS axp_stock_snapshots (   -- P7-5: 결품 KPI의 원천
  date_key TEXT NOT NULL, product_id TEXT NOT NULL, qty REAL,
  PRIMARY KEY (date_key, product_id)
);
CREATE TABLE IF NOT EXISTS axp_kpi_feedback (
  fb_id INTEGER PRIMARY KEY AUTOINCREMENT,
  kpi_id INTEGER NOT NULL,
  action TEXT NOT NULL CHECK (action IN ('adjust_target','improve','keep')),
  measured_m_id INTEGER,                    -- P7-I2: 어느 측정에 대한 행동인지
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
    # P7-1 직후 하루 사이 스키마 교정(m_id 추가): 측정치는 재계산 가능한
    # 파생값이므로 구버전 테이블은 재생성한다(원장 아님 — 손실 무해).
    try:
        db.scalar("SELECT m_id FROM axp_kpi_measurements LIMIT 1")
    except Exception:  # noqa: BLE001
        db.executescript("DROP TABLE IF EXISTS axp_kpi_measurements")
        db.executescript(DDL)
    try:                                     # P7-I2 마이그레이션(멱등)
        db.execute("ALTER TABLE axp_kpi_feedback ADD COLUMN measured_m_id INTEGER")
    except Exception:  # noqa: BLE001
        pass


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


def record_feedback(kpi_id: int, action: str, note: str, by: str,
                    measured_m_id: int | None = None) -> None:
    init()
    if action not in ("improve", "keep"):
        raise ValueError("action은 improve|keep")
    db.execute(
        "INSERT INTO axp_kpi_feedback (kpi_id, action, measured_m_id, note, decided_by, created_at) "
        "VALUES (?,?,?,?,?,?)",
        (kpi_id, action, measured_m_id, note, by, common.now_iso()))


def snapshot_stock(date_key: str | None = None) -> dict:
    """P7-5: 재고 일 스냅샷 — 복제된 stock_quant(내부 위치만)를 일자별로
    보존한다. 결품 일수 KPI의 원천. 같은 날 재실행은 대체(멱등)."""
    init()
    if db.BACKEND != "postgres":
        return {"skipped": "PG 전용(복제 실테이블 필요)"}
    have = db.scalar(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name IN ('stock_quant','stock_location')")
    if have < 2:
        return {"skipped": "stock_quant/stock_location 미복제"}
    from datetime import date as _date
    dk = date_key or _date.today().isoformat()
    rows = db.query(
        "SELECT COALESCE(pc.code, q.product_id::text) AS pid, SUM(q.quantity) AS qty "
        "FROM public.stock_quant q "
        "JOIN public.stock_location l ON l.id = q.location_id AND l.usage = 'internal' "
        "LEFT JOIN axp_prod.v_product_code pc ON pc.id = q.product_id GROUP BY 1")
    db.execute("DELETE FROM axp_stock_snapshots WHERE date_key=?", (dk,))
    for r in rows:
        db.execute("INSERT INTO axp_stock_snapshots (date_key, product_id, qty) VALUES (?,?,?)",
                   (dk, r["pid"], float(r["qty"] or 0)))
    return {"date_key": dk, "products": len(rows)}


# ── KPI 실측 엔진 — 사실 테이블에서 계산 가능한 것만, 나머지는 '측정 전' ──

def _m_wape() -> tuple[float | None, str]:
    try:
        import math

        from .learn import retrain
        # 벽시계가 아니라 데이터 최신일 기준 — 특징 저장소와 같은 기준점(P7-5 교정)
        as_of = db.scalar("SELECT MAX(date_key) FROM fact_sales")
        if not as_of:
            return None, "판매 실적 없음 — 데이터 축적 후 측정"
        v = retrain.recent_wape(str(as_of))
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return None, "서빙 모델 학습 전 — 판매 데이터 축적 후 측정"
        return round(float(v) * 100, 2), f"최근 28일 홀드아웃(기준일 {as_of})"
    except Exception as e:  # noqa: BLE001
        return None, f"측정 불가({str(e)[:40]}) — 모델 학습·특징 생성 후"


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


def _m_stockout_days() -> tuple[float | None, str]:
    """P7-5: 최근 30일 중 '판매 품목 재고 0 이하가 존재한 날' 수."""
    from datetime import date, timedelta
    if not db.table_exists("axp_stock_snapshots") or \
            not db.scalar("SELECT COUNT(*) FROM axp_stock_snapshots"):
        return None, "재고 스냅샷 축적 전 — 야간 stock_snapshot 단계가 쌓는다"
    cutoff = (date.today() - timedelta(days=30)).isoformat()
    days = db.scalar(
        "SELECT COUNT(DISTINCT date_key) FROM axp_stock_snapshots "
        "WHERE date_key >= ? AND qty <= 0 AND product_id IN "
        "(SELECT product_id FROM dim_product WHERE category='bakery')", (cutoff,)) or 0
    return float(days), "axp_stock_snapshots 최근 30일(내부 위치)"


def _m_mo_lead_days() -> tuple[float | None, str]:
    """P7-5: 완료 MO의 착수→완료 평균 일수 — 복제 실테이블에서 직접."""
    if db.BACKEND != "postgres" or not db.scalar(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema='public' AND table_name='mrp_production'"):
        return None, "MO 원장 미복제(실 Odoo 연결 후 측정)"
    v = db.scalar(
        "SELECT AVG(EXTRACT(EPOCH FROM (date_finished - date_start)) / 86400.0) "
        "FROM public.mrp_production "
        "WHERE state='done' AND date_finished IS NOT NULL AND date_start IS NOT NULL")
    if v is None:
        return None, "완료 MO 없음 — 생산 완료 축적 후 측정"
    return round(float(v), 2), "mrp_production 착수→완료 평균"


def _m_forecast_bias() -> tuple[float | None, str]:
    """P7-5: 수요 카드의 예측(p50) 대 실판매 편향% — 예측 로그=카드 근거."""
    from .judge import cards as jcards
    pairs = []
    for c in jcards.listing(kind="demand_forecast"):
        try:
            ev = json.loads(c["evidence_json"])
            for d in ev.get("daily", []):
                pairs.append((d["date_key"], str(ev.get("store_id")),
                              str(ev.get("product_id")), float(d.get("p50") or 0)))
        except Exception:  # noqa: BLE001 — 형식 밖 카드는 건너뜀
            continue
    if not pairs:
        return None, "수요예측 카드(예측 로그) 축적 후 측정"
    matched, biases = 0, []
    for dk, sid, pid, p50 in pairs:
        actual = db.scalar(
            "SELECT SUM(qty) FROM fact_sales WHERE date_key=? AND store_id=? AND product_id=?",
            (dk, sid, pid))
        if actual is None or actual <= 0:
            continue
        matched += 1
        biases.append((actual - p50) / actual * 100)
    if matched < 3:
        return None, f"예측-실판매 대조 표본 부족({matched}건<3) — 일자 경과 후 측정"
    return round(sum(biases) / len(biases), 2), f"수요 카드 p50 대 실판매 {matched}건"


def _m_weekly_questions() -> tuple[float | None, str]:
    """P7-5: 최근 7일 질문 수 — 웹앱 질문 로그."""
    from datetime import date, timedelta
    if not db.table_exists("question_log"):
        return None, "질문 로그 축적 전 — 질문 화면 사용 시 자동 기록"
    cutoff = (date.today() - timedelta(days=7)).isoformat()
    v = db.scalar("SELECT COUNT(*) FROM question_log WHERE at >= ?", (cutoff,))
    return float(v or 0), "question_log 최근 7일"


_MEASURES = {
    "wape": _m_wape,
    "scrap_rate": _m_scrap_rate,
    "defect_rate": _m_scrap_rate,          # 규약: 불량률=스크랩 기준(Community)
    "plan_adherence": _m_plan_adherence,
    "mttr_min": _m_mttr,
    "corrective_events": _m_corrective_events,
    "promoted_rules": _m_promoted_rules,
    # P7-5 결선: '측정 전' 4종이 원천이 생기면 자동으로 측정으로 전환된다
    "forecast_bias": _m_forecast_bias,
    "stockout_days": _m_stockout_days,
    "mo_lead_days": _m_mo_lead_days,
    "weekly_questions": _m_weekly_questions,
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


def measure_active_all() -> dict:
    """야간 배치 진입점 — 모든 활성 프로젝트 KPI를 측정(누적)."""
    init()
    total = {"projects": 0, "measured": 0, "pending": 0}
    for pr in listing():
        if pr["status"] != "active":
            continue
        r = measure_all(pr["project_id"])
        total["projects"] += 1
        total["measured"] += r["measured"]
        total["pending"] += r["pending"]
    return total


def series(kpi_id: int, limit: int = 30) -> list[dict]:
    init()
    rows = db.query(
        "SELECT measured_at, value FROM axp_kpi_measurements WHERE kpi_id=? "
        "ORDER BY m_id DESC LIMIT ?", (kpi_id, limit))
    return list(reversed(rows))


def latest(kpi_id: int) -> dict | None:
    init()
    return db.one("SELECT m_id, measured_at, value, source FROM axp_kpi_measurements "
                  "WHERE kpi_id=? ORDER BY m_id DESC LIMIT 1", (kpi_id,))


def kpi_status(k: dict) -> str:
    """달성 판정 — 목표 없음/측정 전/달성/미달."""
    m = latest(k["kpi_id"])
    if m is None:
        return "측정 전"
    if k["target"] is None:
        return "목표 미설정"
    ok = m["value"] <= k["target"] if k["direction"] == "down" else m["value"] >= k["target"]
    return "달성" if ok else "미달"
