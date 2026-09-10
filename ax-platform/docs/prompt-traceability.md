# 실행 프롬프트집 ↔ 구현 추적 대조표

「AX 플랫폼 구축 실행 프롬프트집」의 작업 패키지 36개가 실제 코드 어디에
구현되었고 완료 판정을 통과했는지의 대조. 프롬프트집이 절차서라면 이 표는
그 절차서의 이행 증명이다.

범례: ✅ 구현·검증 통과 · 🔶 demo 대체 구현(prod 어댑터 지점 명시) · 🏗 현장 항목(P)

## 모듈 프롬프트 26

| 프롬프트 | 구현 위치 | 완료 판정 결과 |
|---|---|---|
| M0-1 컨테이너 기반 | deploy/docker-compose.yml·Caddyfile·runbook.md | 🔶 작성 완료 — 기동 검증은 현장(P-01) |
| M0-2 SSO·백업 | deploy/auth-roles.md·backup/backup.sh·restore-drill.md | 🔶 스크립트·절차 완비 — 리허설 현장(P-05) |
| M0-3 레지스트리·대장·게이트 | registry/ · axp/custody/{ledger,export_gate,contracts}.py | ✅ 계약 7건 등록 · 반출 로그-승인 일치 |
| M1-1 Odoo CDC | axp/ingest/odoo_cdc.py (+_prod.sql) | ✅ 6계열 일 정합 오차 0건 (demo 폴링, prod SQL 제공) |
| M1-2 엑셀 업로더 | axp/ingest/excel_uploader.py | ✅ 동일 양식 2회째 자동 매핑 · 한글 오류 리포트 |
| M1-3 장표 폼 3종 | axp/ingest/forms.py | ✅ 검증 거부 동작 · OCR 사람 확정 플로 |
| M1-4 IoT 수신·경보 | axp/ingest/iot.py | ✅ 156,384행 적재 · 단선 경보 발화 |
| M2-1 표준 스키마 6계열 | axp/dataset/schema.sql + registry/contracts/*.yaml | ✅ G2 심사표(docs/review-G2.md) 승인 |
| M2-2 변환·매핑·품질 게이트 | axp/dataset/{transform,codemap,quality}.py | ✅ 미매핑 0.16% · 멱등 재실행 · 일일 리포트 |
| M2-3 특징량 저장소 | axp/dataset/features.py | ✅ 20종 · 재현성·시점 안전 시험 통과 |
| M3-1 EDA 6종 | axp/studio/eda.py + demo/notebook_stratify_example.ipynb | ✅ p-관리도가 불량 창 이탈 표시 |
| M3-2 야간 마이닝·브리핑 | axp/studio/{mining,briefing}.py | ✅ 심은 원인 z=32 최상위 검출 |
| M3-3 보드 2종 | axp/studio/boards.py + deploy/superset-assets.md | ✅ 현장·경영 보드 생성 (Superset 등록은 prod) |
| M4-1 실험추적·모델 카드 | axp/learn/cards.py | 🔶 경량 레지스트리(D-03) — 필수 항목 누락 등록 거부 확인 |
| M4-2 수요예측·불량분류 | axp/learn/{forecast,classify}.py | ✅ WAPE 8.2%(출발선 20.0%) · AUC 0.73 · 시계열 분할 강제 |
| M4-3 이상탐지 | axp/learn/anomaly.py | 🔶 PCA 재구성 오차(D-07) — recall 1.0 · 13일 선행 |
| M4-4 재고 RL 파일럿 | axp/learn/{simulate,policy}.py | 🔶 CE 탐색(D-02) — 재생 검증 통과 · 11.1% 절감 · 카드로만 상신 |
| M5-1 그래프 스키마·적재 | axp/graph/{store,loader}.py | ✅ 9,839건 백필 · 건수 대사 일치 · Cypher 내보내기 |
| M5-2 확신도 루프 | axp/graph/confidence.py | ✅ 70%·3회 → 상신 → 사람 승인 → Rule 승격·이력 |
| M5-3 근거 API·역추적 | axp/graph/{evidence,evidence_view}.py + /rules/{id}/why | ✅ 경로 9ms · 역추적 HTML(규칙→조합→사실→원장) |
| M6-1 GraphRAG 조립 | axp/judge/assembler.py | 🔶 결정적 조립기(D-05, Ollama 어댑터) — 회귀 10/10 |
| M6-2 판단 카드 생성기 | axp/judge/{cards,generator}.py | ✅ 스키마 v1 · 근거 없는 카드 거부 · 수요 카드 자동 생성 |
| M6-3 반출 폴백 | axp/judge/fallback.py | ✅ 게이트 승인 후만 실행 · 캐시 적중 · 로그 일치 |
| M7-1 런타임·승인함 | axp/agents/{runtime,inbox}.py + odoo-addon/axp_inbox | ✅ 첫 승인→파라미터 환류·감사 로그 (Odoo 화면은 P-06) |
| M7-2 에이전트 5종 | axp/agents/five.py | ✅ 명세 선언 · 그림자 검증 · 4대 각 1카드 |
| M7-3 War Room·승급 | axp/agents/{warroom,promotion}.py | ✅ 승인율 미달 자동 반려 · 상한 이내 자동 실행 · 강등 감시 |

## 게이트 프롬프트 4

| 프롬프트 | 산출물 | 상태 |
|---|---|---|
| G1 헌장 | docs/charter-G1.md | ✅ CTQ 실측치 포함 — 서명은 실 고객사 |
| G2 규격 심사 | docs/review-G2.md | ✅ 7계약 항목별 판정 |
| G3 지표 합의 | docs/metrics-G3.md | ✅ 사업 번역 표 + 함정 점검 |
| G4 완주 판정 | docs/acceptance-G4.md + demo/acceptance.py | ✅ 6/6 자동 점검 + 회고 |

## 운영 프롬프트 6

| 프롬프트 | 코드화 | 상태 |
|---|---|---|
| OP-1 아침 브리핑 | studio/briefing.py (야간 배치 자동) | ✅ 변화만·원천 표기·급증 키워드 |
| OP-2 품질 조치 | dataset/quality.py + cli quarantine/confirm | ✅ 격리 확정 → 사전 축적 |
| OP-3 재학습 점검 | learn/retrain.py (주간 자동) | ✅ 판정→재학습→그림자→승격 게이트·롤백 |
| OP-4 War Room 리뷰 | agents/warroom.py | ✅ 회의 순서 내장 |
| OP-5 리스크 점검 | 관측 지표 전부 테이블화(수동 점검은 격주) | 🔶 지표 자동·판정 수동 |
| OP-6 W9 인수인계 | docs/handover-W9.md | 🏗 현장 검수 항목 |

**36개 중 ✅ 25 · 🔶 9(전부 prod 어댑터 지점 명시) · 🏗 2(현장 전용).**

## 계획 외 확장 구현 (프롬프트집 개정 시 편입 후보)

| 확장 | 구현 위치 | 근거 프롬프트 |
|---|---|---|
| 생산계획 에이전트(6호) — 용량 감안 생산 오더 | agents/five.py production_plan_agent | M7-2의 '+α', 2단계 재고·생산 앱 |
| 연속 경보 → 계획 정비 승격 | agents/five.py equip_alert_agent | M7-2 설비경보의 심화 |
| SOP 개정 제안(Rule→절차) | agents/five.py knowledge_agent | 3단계 지식센터 심화 |
| 승급 자동 실행 결선 | agents/runtime.py + inbox role='auto' | M7-3 |
| 재학습 자동화(판정→그림자→게이트) | learn/retrain.py | OP-3의 코드화 |
| 교차 원천 검증 | dataset/validation.py | M2 계약의 '검증용' 조항 |
| 리스크 5 자동 점검 | agents/risk.py | OP-5의 코드화 |
| 지식센터 씨앗(메모 급증·검색) | studio/knowledge.py | 4대 지능화 ④ 1단계 |
| 승인함 웹 UI(demo) | axp/inbox_ui.py (/inbox) | M7-1의 demo 대체 화면 |
| 개방 포맷 내보내기 | dataset/export.py | 인터페이스 원칙 ② |

프롬프트를 고치면 이 표도 고친다 — 둘의 어긋남이 곧 기술 부채다.
