# 2단계 실행계획 이행 추적 (Phase A/B/C)

실행 환경: 클라우드 개발 컨테이너(PG16 로컬 설치, GPU 없음 — GPU 서버용
코드는 원격 접속형으로 작성). 근거 계획: docs/presentations/AX_Platform_Diagnosis_Plan.docx

| 계획 항목 | 상태 | 결과·측정치 |
|---|---|---|
| A1 PostgreSQL 전환 | **완료** | db.py 이중 백엔드(AXP_DB=sqlite/postgres). 호환 변환: ?→%s, 명명 파라미터, AUTOINCREMENT→BIGSERIAL, OR REPLACE/IGNORE→ON CONFLICT(PK·UNIQUE 자동 탐지), PRAGMA FK→session_replication_role, 리터럴 % 이스케이프, json_extract→jsonb, lastrowid→RETURNING. 테스트별 격리는 데이터 경로 기반 스키마(ax_*)로 재현 |
| A1 테스트 | **완료** | pytest 31/31 — SQLite·PostgreSQL 양쪽 green |
| A1 E2E(PG) | **완료** | 태성당 전 구간 PG 완주 **206.6s, exit 0** — WAPE 7.06%(SQLite 7.08%와 동일 수준)·이상탐지 recall 1.0·회귀 10/10·미매핑 0.11% → **백엔드 파리티 확인**. SQLite 64s 대비 3.2배(호출별 접속 방식) — 접속 풀링을 후속 최적화로 등록 |
| A2 Odoo CDC prod 검증 | **완료(시뮬레이터)** | wal_level=logical 설정, Odoo 16 표준 스키마 시뮬레이터 DB(deploy/odoo_sim_schema.sql, 13개 테이블) → publication 2종(전체/core) → **CREATE SUBSCRIPTION 실구동, 삽입 6행 즉시 복제 확인**, 슬롯 lag 모니터링 쿼리 실측. 같은 클러스터 구독 시 슬롯 선생성 필요(운영 runbook 반영). 한계: 실 Odoo 인스턴스가 아니라 표준 스키마 재현 — 고객 Odoo 버전·커스텀 필드 확인은 현장 몫 |
| A3 실패 알림 | **완료** | core/axp/notify.py — telegram/webhook/console/dryrun 채널, 최소 등급 필터, **반출 게이트 호스트 검사**(미허용 호스트 발신 차단), scheduler 사이클 요약 발신, common.alert 연동. 테스트 4건 |
| A3 백업/복구 리허설 | **완료** | E2E 전체 데이터(59테이블, 3.0MB) 기준 dump 0.78s / restore 1.59s. **함정 발견: 덤프에 논리 복제 구독이 포함되어 복원 DB가 이중 구독 생성** → 리허설·복제본 복원은 반드시 `pg_dump --no-subscriptions` (P2-I9, runbook 반영) |
| A4 CI | **완료** | .github/workflows/ax-platform-tests.yml — PG16 서비스 컨테이너, SQLite·PG 양쪽 pytest (저장소 Actions 활성화 필요) |
| C5 GPU 서버 LLM | **완료(코드)** | OllamaBackend 실전화: AXP_LLM=ollama·AXP_OLLAMA_URL(GPU 서버)·모델 env, 사설망/허용목록 게이트 검사, 인용 위반 1회 재생성, 불통 시 결정적 조립기 자동 폴백. 실 GPU 서버 접속 검증은 현장 몫 |

## PG 전환에서 발견한 이식성 이슈 (이슈 대장 연장 — P2-I)

- [P2-I1] REAL 컬럼에 `=''` 비교 → CAST(col AS TEXT)로 중립화 (quality.py)
- [P2-I2] HAVING에서 SELECT 별칭 사용 불가 → COUNT(*)로 (quality.py)
- [P2-I3] FROM 서브쿼리 별칭 필수 → `) d` (quality.py)
- [P2-I4] 문자열 리터럴 `%`(LIKE '%…%')가 psycopg 플레이스홀더와 충돌 → 선택적 이스케이프
- [P2-I5] json_extract는 SQLite 전용 → jsonb `->>`/`#>>` 변환 규칙
- [P2-I6] SUM(불리언) 불가 → SUM(CASE WHEN…) (warroom.py)
- [P2-I9] pg_dump 기본값이 구독을 포함 — 복원 드릴에서 이중 구독 사고 위험 → --no-subscriptions 표준화
- [P2-I7] 같은 클러스터 CREATE SUBSCRIPTION은 슬롯 선생성 + create_slot=false 필요

교훈: "표준 SQL만 쓴다"는 규율은 실제 두 번째 엔진을 돌려보기 전까지는
검증되지 않은 선언이다 — 6건 모두 데모에선 조용히 통과하던 코드였다.

| C1 통합 웹앱 v1 | **완료** | core/axp/webapp.py — 로그인(PBKDF2·서명 쿠키)·역할 강제(admin/steward/approver/viewer)·승인함 결정·격리 큐 확정+**확정 취소(undo, I-09 교훈)**·브리핑·War Room·감사 로그·비밀번호 변경. 테스트 5건 양쪽 백엔드 통과 |
| C2 Odoo 쓰기 커넥터 | **완료** | ingest/odoo_writeback.py — 승인 카드→구매발주 '초안'(확정은 사람이 Odoo에서), demo sqlite 실동작 + prod XML-RPC(ORM 경유, SQL 직삽 금지), 멱등 로그·감사 기록. 테스트 2건 |
| C3 정상 창 정식화 | **완료** | anomaly.normal_window_mask — 고장 전 14일·정비 후 2일 자동 제외(I-01 재발 방지의 코드화) |
| C3 콜드스타트 | 진행 | learn/coldstart.py — 유사 품목 전이(라인/상관 공여 선택, 규모 배율, 광폭 구간·근거 명시) — 검증 테스트 작성 중 |
