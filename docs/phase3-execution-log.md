# 3단계 실행 로그 (Phase 3 Execution Log)

> 3단계 실행계획서(AX_P3_Comprehensive_Report.docx 제4장) 이행 기록.
> 원칙: 실측 없이 완료 표기하지 않는다. 문제는 P3-I 번호로 남긴다.

## 진행 현황

| 항목 | 내용 | 상태 | 실측 근거 |
|---|---|---|---|
| P3-1 | 실 Odoo 인스턴스 구축 + PG 연결 초기화 | **완료** | Odoo 17.0 Community 소스(GitHub 17.0 branch) → PG16 `odoo_real` DB, 모듈 70개 설치 |
| P3-2 | odoo_cdc_prod.sql 실Odoo 검증 + 버전 매트릭스 | **완료** | publication 11테이블 · 구독 11릴레이션 ready · ORM 문서 4종 실복제 · 매핑 뷰 6종 |
| P3-3 | Odoo 승인함 애드온(axp_inbox) 1차 | **완료** | 실 Odoo 17 설치 → 동기화 47카드 → 승인·반려·권한·재동기화 E2E 실측 |
| P3-4 | 웹앱 동시 사용자 부하 시험 + psycopg_pool 판단 | **완료** | 820요청 무오류 · 동시20 p95 319ms · 판단: 파일럿 규모에선 도입 보류(기준 명문화) |
| P3-5 | POS 반입 어댑터 2종 | **완료** | cp949 정산 CSV·영수증 로그 반입 실측, 테스트 5종, CLI `pos daily|receipt` |
| P3-6 | SLA 초안 + 파일럿 현장 체크리스트 | **완료** | ax-platform/docs/sla-draft.md(실측 근거 SLO) · pilot-site-checklist.md(A~G 게이트) |

## P3-1: 실 Odoo 인스턴스 (2026-09-11)

- **확보 경로**: PyPI에는 odoo 패키지 없음(`pip download odoo` → from versions: none),
  nightly.odoo.com은 이 환경의 프록시가 차단(403). **GitHub `odoo/odoo` 17.0 브랜치
  shallow clone**으로 확보(40,079 파일, 1.2GB).
- **의존성**: Python 3.11 기준 requirements 설치. 구식 sdist 7종(ebaysdk, psycopg2,
  python-ldap, rjsmin, vobject, docopt, ofxparse)은 Debian setuptools의
  `install_layout` 버그로 빌드 실패 → 휠 대체(psycopg2-binary, docopt-ng, 최신
  rjsmin/vobject)로 해결. num2words는 `--no-deps`(docopt-ng가 모듈 제공).
- **TLS 스택**: Debian 시스템 cryptography 41은 pip으로 제거 불가 + urllib3 1.26의
  pyopenssl contrib와 비호환 → Odoo의 py3.12 핀 세트(cryptography 42.0.8,
  pyOpenSSL 24.1.0, urllib3 2.0.7)로 `--ignore-installed` 정렬.
- **초기화**: `odoo-bin -d odoo_real -i base --without-demo=all` →
  `-i sale_management,purchase,stock,mrp,maintenance` — **모듈 70개 installed**.
- **모듈 구성 실측**: quality_check/quality_alert는 **Enterprise 전용**이라
  Community에는 테이블 자체가 없음 — P2-I12(원천 테이블 부재 우아한 스킵)가
  가정이 아니라 실제 Community 고객의 기본 상태임을 확인.

## P3-2: 논리 복제 실Odoo 검증 + 컬럼 매트릭스 (2026-09-11)

**리허설 구성**: 같은 PG16 클러스터에서 `odoo_real`(원장) → `axp`(플랫폼) 구독.

1. **발행**: odoo_cdc_prod.sql을 모듈 인지형으로 개정(P3-I1) 후 실행 —
   후보 13테이블 중 존재하는 **11테이블 발행**, quality 2종은 NOTICE와 함께 자동 제외.
2. **구독**: 발행 11테이블 구조를 `pg_dump --schema-only`로 떠서 구독자에 생성
   (외부 모듈 FK·trgm 인덱스는 실패해도 복제에 무관), 같은 클러스터이므로
   슬롯 선생성 + `create_slot=false`(P2-I7 규칙) — **11릴레이션 모두 state=r**.
3. **실데이터 검증**: Odoo **ORM 경유**(odoo-bin shell)로 파트너·품목 생성,
   판매주문 S00001 확정, 발주 P00001, 정비요청 1건 → 전 행이 구독자 DB에 도착.
   출고 WH/OUT/00001 `button_validate()` 완료 → stock_move state='done' 반영 확인.
4. **매핑 뷰**(deploy/odoo17_prod_mapping.sql): 실컬럼 → 스테이징 계열 투영
   `axp_prod.v_sales/v_purchase/v_stock_move/v_mrp/v_maintenance/v_quality_scrap`
   6종 생성·조회 실증(S00001 qty 500·확정만 투영, done 무브만 투영 확인).

**컬럼 차이 매트릭스 (합성 demo → 실 Odoo 17 Community, 핵심만)**

| demo 컬럼 | 실 Odoo 17 | 비고 |
|---|---|---|
| qty | sale: `product_uom_qty` / purchase: `product_qty` / stock: `product_uom_qty` | 모델마다 다름 — 뷰에서 통일 |
| order_ref / po_ref | `sale_order.name` / `purchase_order.name` | 라인→헤더 JOIN 필요 |
| order_date | 헤더 `date_order` | 라인 테이블에는 날짜 없음 |
| store_id | `sale_order.warehouse_id` | 창고=매장 규약 |
| channel | `sale_order.team_id` | 판매팀=채널 규약 |
| promo_flag | `discount > 0` 파생 | Community에 프로모션 모듈 없음 |
| lot_id | `stock_move_line` (2차 범위) | 라인 테이블에 없음 |
| equipment/event_type | `maintenance_request.equipment_id`/`maintenance_type` | duration은 시간 단위 → ×60 |
| qty_planned/qty_done | `mrp_production.product_qty`/`qty_producing` | 작업장별은 mrp_workorder(2차) |
| quality_check 계열 | **Community 부재** | stock_scrap + 현장 장표로 대체(v_quality_scrap) |

**운영 판정**: 실 Odoo에 붙일 때 코드 변경 없이 필요한 것은 ① 모듈 인지형
publication(개정 완료) ② 매핑 뷰 세트(작성 완료) ③ M2 codemap의 코드값 표준화
(기존 기능). 스테이징 적재기는 뷰를 SELECT하는 것으로 동일 로직 재사용 가능.

## P3-3: Odoo 승인함 애드온(axp_inbox) 실설치 검증 (2026-09-11)

P2에서 만든 스켈레톤을 **실 Odoo 17에 설치**하고 플랫폼 API와 왕복 검증했다.

- **설치**: `-i axp_inbox` 무경고 통과 — 모델 테이블·뷰 3종·크론·권한 그룹 등록 확인.
- **동기화**: axp-api(태성당 데이터 사본)를 띄우고 `cron_sync()` → **47카드 동기화,
  대기 5건·7개 유형** 전부 화면 모델에 적재.
- **승인 환류 E2E**: Odoo 승인 버튼 → 플랫폼 `/decide` → 자동 실행 —
  `replenish_policy:demand_factor 0.928→0.92` 파라미터 기록 + 감사 로그 2건
  (approve/Administrator, feedback/system) 실측. 재동기화 시 Odoo 화면 상태도
  executed로 따라옴.
- **반려 흐름**: 사유 미선택 반려는 UserError로 차단, 사유 지정 반려는 플랫폼
  reject_reasons + 감사 로그("현장 사정: 행사 물량 별도 협의 중")에 기록.
- **권한**: 열람 전용 사용자의 승인 시도는 AccessError로 차단(그룹 매트릭스 작동).
- **'왜?' 버튼**: `/cards/43/why` 근거 경로(모델 카드 wape 0.0708 포함) 표시 확인.

## P3-4: 웹앱 동시 사용자 부하 시험 + psycopg_pool 판단 (2026-09-11)

**구성**: PG 백엔드(소크 데이터) + uvicorn 단일 워커, 로그인 세션 쿠키로
주요 5페이지(승인함·브리핑·격리큐·감사·자동실행) 라운드로빈 + POST /ask 별도.

| 동시 사용자 | 요청 | 성공 | p50 | p95 | max | RPS |
|---|---|---|---|---|---|---|
| 1 | 20 | 100% | 4ms | 7ms | 10ms | 201 |
| 5 | 100 | 100% | 34ms | 72ms | 83ms | 130 |
| 10 | 200 | 100% | 70ms | 167ms | 177ms | 120 |
| 20 | 400 | 100% | 134ms | 319ms | 357ms | 123 |
| /ask 질의 ×100 (동시 10) | 100 | 100% | 50ms | 93ms | 122ms | 181 |

- **오류 0건**(820요청). PG 동시 연결 최고 21개 — 스레드별 연결 풀(P2 도입)이
  요청마다 재접속 없이 동작함을 실측.
- **psycopg_pool 판단: 파일럿 규모(동시 ≤20)에서는 도입 보류.**
  근거: 현 구조의 연결 상한은 uvicorn 스레드풀(40) × 워커 수라 단일 워커에서는
  PG max_connections(100)에 여유. **도입 기준(명문)**: ① 워커 2개 이상으로
  수평 확장할 때(40×N이 100에 근접) ② 동시 사용자 50 초과 목표 ③ 연결
  대기/거부 오류 관측 시 — 이때 psycopg_pool(min 4/max 20)로 전환한다.

## P3-5: POS 반입 어댑터 2종 (2026-09-11)

파일럿 현장의 판매 원천은 Odoo가 아니라 POS인 경우가 많다 —
`core/axp/ingest/pos.py` 신설, CLI `python3 -m axp.cli pos daily|receipt <파일> --by <이름>`.

- **어댑터 ① daily**: 일별 정산 집계(영업일자×매장×상품). 단가는 금액/수량 역산,
  promo_flag는 할인>0, order_ref `POS/<일자>/<매장>`.
- **어댑터 ② receipt**: 영수증 단위 거래 로그 — order_ref=영수증번호로 라인 보존
  (시간대·장바구니 분석 재료).
- **현실 대응**: cp949/euc-kr/utf-8 자동 판별 + 콤마/세미콜론/탭 구분자 자동 판별,
  열 이름 동의어 사전 자동 매핑(못 알아본 양식은 needs_mapping으로 반문),
  PII 컬럼 차단(M1-2 재사용), 원본 불변 보존, 오류는 "몇 행 몇 열이 왜" 한글로.
- **안전장치**: 같은 파일(sha256) 재반입 차단(멱등) · Odoo 판매와 겹치는
  (날짜×매장) 이중 집계 경고 — CLI 스모크에서 실제 경고 발화 확인.
- 테스트 5종 추가(cp949·자동매핑·PII, 멱등, 영수증 세미콜론, needs_mapping,
  이중 집계) — **전체 56/56 양쪽 백엔드 green**.

## P3-6: SLA 초안 + 파일럿 현장 체크리스트 (2026-09-11)

- **ax-platform/docs/sla-draft.md**: 파일럿용 SLA v0.1 — SLO 8항목 전부를 이
  저장소의 실측(부하 p95 319ms, E2E 53.5s, 소크 3일, 복구 리허설)에 근거해
  설정. 장애 4등급 대응 시간, 정직 조항(카드는 제안, 정확도는 SLO가 아니라
  보고 지표, 합성 데이터 성능은 참고치) 명문화.
- **ax-platform/docs/pilot-site-checklist.md**: 온사이트 D0~4주차 게이트 A~G —
  이 저장소에서 리허설로 실증된 항목([리허설 완료])과 현장에서만 확인 가능한
  항목을 구분. 판매 정본 선언(Odoo vs POS), wal_level 재시작 창구,
  `--no-subscriptions` 백업 확인(P2-I9) 등 이번 단계 실측에서 나온 함정 반영.

## 백업/복구 드릴 — 실구독 상태 (2026-09-11, 12주 계획 W2 항목)

플랫폼 DB(axp)에 **실제 구독(axp_sub_real)이 걸린 상태**로 드릴을 수행 —
P2-I9(pg_dump 구독 포함 사고)를 리허설이 아닌 실물로 재검증했다.

- 기본 `pg_dump`: 덤프에 `CREATE SUBSCRIPTION` **1건 포함** — 이 덤프를 복원하면
  복원본이 원장에서 재복제를 시작하는 이중 수집 사고로 이어진다(실측 확인).
  `--no-subscriptions` 덤프에는 0건 — 운영 표준 유지 근거 확정.
- 복원: 54MB 덤프 → 신규 DB 복원 **6초**, 판매 라인 건수 원본과 일치.
- 드릴이 적발한 잔여물: 복원 중 FK 오류 16건 → 추적 결과 **파이프라인 버그가
  아니라 pytest 잔류 스키마**(P3-I7)의 테스트 데이터(의도적으로 dim 없이 fact만
  넣는 테스트). 정리 후 재발 방지 코드 반영.

## 문제 기록 (P3-I)

| 번호 | 문제 | 처리 |
|---|---|---|
| P3-I1 | 고정 목록 `CREATE PUBLICATION`이 Community에서 즉시 실패 — quality_* 테이블 부재. 정적 DDL은 고객 모듈 구성마다 깨진다 | odoo_cdc_prod.sql을 존재 테이블만 발행하는 DO 블록으로 개정, 제외분은 NOTICE로 가시화 (**해결**) |
| P3-I2 | PyPI에 Odoo 배포 없음 + 구식 sdist 다수가 최신 Debian/Python에서 빌드 실패 — 고객사 서버에서도 동일하게 겪을 설치 마찰 | 소스 clone + 휠 대체 절차를 본 로그에 기록. 운영은 공식 deb/도커 이미지를 1순위로 권고 (**우회 확립**) |
| P3-I3 | Odoo는 원장 테이블에 `qty`라는 단일 컬럼이 없고 모델마다 수량 컬럼명이 다름 — demo 스키마 그대로 붙이면 전 계열 적재 실패했을 것 | 매핑 뷰 6종으로 흡수, 매트릭스 문서화 (**해결**) |
| P3-I4 | axp_inbox의 kind 선택지에 production_plan 누락 — 실동기화에서 ValueError로 **전체 동기화 중단**(한 카드 불량이 전량을 막는 구조) | 선택지 추가 + 행 단위 savepoint 격리로 개정(성공/실패 카운트 로깅), v17.0.0.2 (**해결**) |
| P3-I5 | 첫 동기화 실패 시 같은 트랜잭션의 api_base 설정까지 롤백돼 이후 동기화가 기본값(axp-api:8000)으로 조용히 0건 — 운영에서 원인 찾기 어려운 유형 | 설정 저장은 별도 커밋으로 분리하는 운영 절차를 로그에 명시. cron 경로는 자동 커밋이라 영향 없음 (**절차 확립**) |
| P3-I6 | 복원 드릴 중 fact_defect FK 오류 16건 — 원인 추적 결과 잔류 pytest 스키마의 의도적 테스트 데이터(파이프라인 무결성 문제 아님). 단, FK를 끈 채 적재하는 구조(sqlite PRAGMA 대응)라 원본에선 고아가 조용히 통과함을 확인 | 정합은 reconcile·quality 게이트가 담당(기존 설계 유지), 잔류 스키마는 P3-I7로 해소 (**원인 규명**) |
| P3-I7 | PG 백엔드 pytest가 실행마다 스키마 ax_*를 만들고 정리하지 않아 플랫폼 DB에 30여 개 영구 누적 — 덤프 비대·복원 소음·이름 충돌 위험 | 잔류 스키마 일괄 정리 + conftest tmp_db 종료 시 해당 스키마 DROP(실측: 56테스트 후 스키마 수 불변) (**해결**) |

## 남은 리스크

- **Enterprise 전용 quality 모듈**: Community 고객의 불량 데이터는 stock_scrap과
  현장 장표(M1-3)로만 커버 — 불량 유형 세분화는 장표 설계에 의존.
- **로트 추적(2차)**: lot_id는 stock_move_line 복제 추가가 필요 — P3 후속 범위.
- **이 리허설은 같은 클러스터**: 실제 2서버(원장↔플랫폼) 구간의 네트워크·방화벽·
  REPLICATION 계정 권한은 온사이트 점검 항목(SLA 체크리스트에 반영 예정).
