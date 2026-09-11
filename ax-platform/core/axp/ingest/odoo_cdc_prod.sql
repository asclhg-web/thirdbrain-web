-- M1-1 prod: PostgreSQL 논리 복제 구성 (Odoo 원장 서버에서 실행)
-- 전제: postgresql.conf 에 wal_level=logical, Odoo DB 접속 계정은 REPLICATION 권한.
-- 원칙: 원장에 쓰기 없음 — publication 은 읽기 전용 계약이다.
--
-- P3-I1: 고정 테이블 목록의 CREATE PUBLICATION 은 quality_* (Enterprise 전용) 등
--   미설치 모듈 테이블에서 즉시 실패한다(Odoo 17 Community 실측 확인).
--   → 존재하는 테이블만 골라 발행하는 모듈 인지형 DO 블록으로 구성한다.
--   대상 후보 13개 중 설치된 것만 발행되며, 목록은 axp_pub_tables 뷰로 남긴다.

-- 1) 발행(publication): 6대 테이블 계열 — 존재하는 테이블만
DO $$
DECLARE
  candidates text[] := ARRAY[
    'sale_order', 'sale_order_line',
    'purchase_order', 'purchase_order_line',
    'stock_move', 'stock_quant', 'stock_scrap',
    'mrp_production', 'mrp_workorder',
    'quality_check', 'quality_alert',          -- Enterprise 전용: 없으면 자동 제외
    'maintenance_request', 'maintenance_equipment'];
  t text;
  present text[] := '{}';
BEGIN
  FOREACH t IN ARRAY candidates LOOP
    IF to_regclass('public.' || t) IS NOT NULL THEN
      present := present || t;
    ELSE
      RAISE NOTICE 'axp_pub: 테이블 % 없음(모듈 미설치) — 발행 제외', t;
    END IF;
  END LOOP;
  IF array_length(present, 1) IS NULL THEN
    RAISE EXCEPTION 'axp_pub: 발행할 테이블이 하나도 없음 — Odoo DB 가 맞는지 확인';
  END IF;
  EXECUTE 'CREATE PUBLICATION axp_pub FOR TABLE ' || array_to_string(present, ', ');
  RAISE NOTICE 'axp_pub 발행: %', array_to_string(present, ', ');
END $$;

-- 발행 목록 확인(운영 점검용)
-- SELECT * FROM pg_publication_tables WHERE pubname = 'axp_pub';

-- 2) 수신측(플랫폼 PostgreSQL): 구독 생성
--    (스테이징 스키마에 동일 구조 테이블을 먼저 만든 뒤 — 구조는
--     pg_dump --schema-only -t <table> 로 원장에서 떠 온다)
CREATE SUBSCRIPTION axp_sub
  CONNECTION 'host=<odoo-db> dbname=<odoo> user=axp_repl password=<secret>'
  PUBLICATION axp_pub
  WITH (copy_data = true, create_slot = true, slot_name = 'axp_slot');
-- 주의(P2-I7): 원장과 수신측이 같은 클러스터(개발·리허설)면 create_slot=true 가
--   교착한다 — 슬롯을 pg_create_logical_replication_slot('axp_slot','pgoutput')
--   으로 선생성하고 create_slot=false 로 구독할 것.

-- 3) 슬롯 모니터링 (적체 시 경보 — axp-scheduler 가 주기 실행)
--    pg_replication_slots.restart_lsn 대비 pg_current_wal_lsn() 지연 바이트
SELECT slot_name,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag
FROM pg_replication_slots WHERE slot_name = 'axp_slot';

-- 4) 야간 정합 배치는 axp.ingest.odoo_cdc.reconcile() 이 수행
--    (건수·수량 합계를 원장과 대조, 오차 시 crit 경보)
