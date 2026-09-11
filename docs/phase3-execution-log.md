# 3단계 실행 로그 (Phase 3 Execution Log)

> 3단계 실행계획서(AX_P3_Comprehensive_Report.docx 제4장) 이행 기록.
> 원칙: 실측 없이 완료 표기하지 않는다. 문제는 P3-I 번호로 남긴다.

## 진행 현황

| 항목 | 내용 | 상태 | 실측 근거 |
|---|---|---|---|
| P3-1 | 실 Odoo 인스턴스 구축 + PG 연결 초기화 | **완료** | Odoo 17.0 Community 소스(GitHub 17.0 branch) → PG16 `odoo_real` DB, 모듈 70개 설치 |
| P3-2 | odoo_cdc_prod.sql 실Odoo 검증 + 버전 매트릭스 | **완료** | publication 11테이블 · 구독 11릴레이션 ready · ORM 문서 4종 실복제 · 매핑 뷰 6종 |
| P3-3 | Odoo 승인함 애드온(axp_inbox) 1차 | 진행 예정 | — |
| P3-4 | 웹앱 동시 사용자 부하 시험 | 대기 | — |
| P3-5 | POS 반입 어댑터 2종 | 대기 | — |
| P3-6 | SLA 초안 + 파일럿 현장 체크리스트 | 대기 | — |

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

## 문제 기록 (P3-I)

| 번호 | 문제 | 처리 |
|---|---|---|
| P3-I1 | 고정 목록 `CREATE PUBLICATION`이 Community에서 즉시 실패 — quality_* 테이블 부재. 정적 DDL은 고객 모듈 구성마다 깨진다 | odoo_cdc_prod.sql을 존재 테이블만 발행하는 DO 블록으로 개정, 제외분은 NOTICE로 가시화 (**해결**) |
| P3-I2 | PyPI에 Odoo 배포 없음 + 구식 sdist 다수가 최신 Debian/Python에서 빌드 실패 — 고객사 서버에서도 동일하게 겪을 설치 마찰 | 소스 clone + 휠 대체 절차를 본 로그에 기록. 운영은 공식 deb/도커 이미지를 1순위로 권고 (**우회 확립**) |
| P3-I3 | Odoo는 원장 테이블에 `qty`라는 단일 컬럼이 없고 모델마다 수량 컬럼명이 다름 — demo 스키마 그대로 붙이면 전 계열 적재 실패했을 것 | 매핑 뷰 6종으로 흡수, 매트릭스 문서화 (**해결**) |

## 남은 리스크

- **Enterprise 전용 quality 모듈**: Community 고객의 불량 데이터는 stock_scrap과
  현장 장표(M1-3)로만 커버 — 불량 유형 세분화는 장표 설계에 의존.
- **로트 추적(2차)**: lot_id는 stock_move_line 복제 추가가 필요 — P3 후속 범위.
- **이 리허설은 같은 클러스터**: 실제 2서버(원장↔플랫폼) 구간의 네트워크·방화벽·
  REPLICATION 계정 권한은 온사이트 점검 항목(SLA 체크리스트에 반영 예정).
