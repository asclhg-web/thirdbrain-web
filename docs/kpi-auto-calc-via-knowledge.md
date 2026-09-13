# KPI 자동 계산 — 지식센터(지식그래프) 기반 설계 노트

대표 지시(2026-09-13): "일단 수기방식으로 셋팅해 놓고, 자동으로 Odoo를
이용한 계산방식은 지식센터에 넣어 이용하는 방법을 고려."

이 문서는 **설계(고려) 단계**의 기록이다. 지금 당장 구현하지 않는다 —
실데이터(태성당 Odoo) 온보딩 후 착수한다. 현재 경영 목표 KPI는 수기 실적
방식이 기본값으로 확정되어 동작 중이다.

## 1. 현재 상태 (수기, 확정)

- 경영 목표 KPI(생산성 향상·원가 절감·납기 단축·품질 향상)는
  `axp_project_kpis.area = 'objective'`로 등재되고, 목표치(%)만 지정한다.
- 측정은 사람이 실적을 입력 → `axp_kpi_measurements(source='수기:<담당>')`에
  누적 → 대시보드가 목표 대비 달성/미달 판정.
- `measure_all()`은 `area == OBJ_AREA`를 자동 측정에서 제외(수기 전용).

이 방식은 정직하다 — 생산성·품질 같은 지표는 회사마다 정의가 달라
데이터로 함부로 계산하면 근거 없는 숫자가 된다.

## 2. 목표 구조 — 계산식을 '코드'가 아니라 '지식'으로

기술 영역 KPI(WAPE·결품일수 등)는 `projects._MEASURES`에 **파이썬 코드로
하드코딩**되어 있다. 새 자동 KPI를 추가할 때마다 코드를 고쳐야 한다.
대신 **계산 정의 자체를 지식그래프에 등록**하면:

- 계산식이 설명 가능해지고(왜 이 숫자인가 → 근거 사다리),
- 코드 수정 없이 KPI를 추가·수정하며,
- 확신도 루프(승격/강등)와 반출 게이트 등 기존 지식센터 원칙을 그대로 탄다.

### 2.1 KPI 계산 정의 노드 (KPI-DEF)

지식그래프(`axp/graph/store.py`)에 새 노드 종류를 둔다:

```
KPI-DEF {
  kpi_code:      "cost_reduction"            # 경영 목표 key와 연결
  label:         "원가 절감률"
  formula:       "(baseline_cost - actual_cost) / baseline_cost * 100"
  sources: [                                  # Odoo 복제 뷰(axp_prod)만 참조
    {name: "actual_cost",   sql_view: "axp_prod.v_production_cost", period: "month"},
    {name: "baseline_cost", sql_view: "axp_prod.v_cost_baseline",   period: "fixed"}
  ]
  unit:          "%"
  direction:     "up"
  confidence:    0.0                          # 승격 전엔 수기 우선
  evidence:      "정의 근거(회계기준·합의 문서 ref)"
}
```

### 2.2 야간 배치 흐름

```
scheduler(야간)
  └ for KPI-DEF where confidence ≥ PROMOTE_CONF:
       값 = eval(formula, {소스별 SQL_view 집계})      # axp_prod 뷰에서만
       axp_kpi_measurements(source="자동:KPI-DEF:<code>")에 적재
  └ confidence < 임계면 자동 적재 보류 → 수기 유지(정직)
```

- 소스는 **복제된 Odoo 뷰(axp_prod.*)만** 허용 — 원본 Odoo 직접 조회 금지
  (사설망 반출 게이트·감사 원칙 유지).
- 자동/수기 충돌 시: 자동 값은 `source="자동:"`, 수기는 `source="수기:"`로
  구분 저장하고, 대시보드가 최근값을 쓰되 출처를 표기.

### 2.3 GraphRAG 연계 (왜?)

- KPI 값 옆 `[왜?]` → `evidence_view`가 KPI-DEF의 formula·sources·집계 구간·
  원장 근거까지 사다리로 내려간다. "원가 절감 12%는 어떻게 나온 숫자?"에
  계산식과 원천 뷰·행까지 답한다(근거 강제·수치 생성 금지 원칙 유지).

## 3. 웹 UI (예정)

- 프로젝트 KPI 카드: KPI-DEF가 연결되고 승격되면 **자동 측정**(배지 '자동'),
  없으면 지금처럼 **수기 실적 입력**('수기').
- 관리(admin) 화면에 **KPI-DEF 편집기** — 계산식·소스 뷰·확신도 관리.
  (지식센터 하위 메뉴로 배치: 지식그래프 · 질문 · **KPI 정의식**)

## 4. 단계 (실데이터 온보딩 후 착수)

1. `axp_prod`에 KPI 소스 뷰 정의(원가·납기·생산성 기준 — 회사와 합의).
2. 지식그래프에 KPI-DEF 노드 스키마 + 로더(`graph/loader.py`) 추가.
3. `projects.measure()`에 KPI-DEF 경로 추가(코드 하드코딩 대안).
4. 야간 배치 결선 + 자동/수기 출처 표기.
5. GraphRAG 근거 사다리에 KPI-DEF 편입.
6. 관리 화면 KPI-DEF 편집기.

## 5. 원칙 (불변)

- 정의가 불확실하면 **수기가 정답** — 확신도 승격 전엔 자동 적재 안 함.
- 자동 값도 **모든 수치에 근거** — formula·소스·원장까지 추적 가능.
- 계산은 그래프/뷰가, 서술은 LLM이 — **LLM은 숫자를 만들지 않는다**.

_기록: docs/phase8-execution-log.md(P9-3) 후속 설계. 구현 착수 시 P# 부여._
