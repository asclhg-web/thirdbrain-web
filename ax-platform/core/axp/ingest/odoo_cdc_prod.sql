-- M1-1 prod: PostgreSQL 논리 복제 구성 (Odoo 원장 서버에서 실행)
-- 전제: postgresql.conf 에 wal_level=logical, Odoo DB 접속 계정은 REPLICATION 권한.
-- 원칙: 원장에 쓰기 없음 — publication 은 읽기 전용 계약이다.

-- 1) 발행(publication): 6대 테이블 계열
CREATE PUBLICATION axp_pub FOR TABLE
  sale_order, sale_order_line,
  purchase_order, purchase_order_line,
  stock_move, stock_quant, stock_scrap,
  mrp_production, mrp_workorder,
  quality_check, quality_alert,
  maintenance_request, maintenance_equipment;

-- 2) 수신측(플랫폼 PostgreSQL): 구독 생성
--    (스테이징 스키마에 동일 구조 테이블을 먼저 만든 뒤)
CREATE SUBSCRIPTION axp_sub
  CONNECTION 'host=<odoo-db> dbname=<odoo> user=axp_repl password=<secret>'
  PUBLICATION axp_pub
  WITH (copy_data = true, create_slot = true, slot_name = 'axp_slot');

-- 3) 슬롯 모니터링 (적체 시 경보 — axp-scheduler 가 주기 실행)
--    pg_replication_slots.restart_lsn 대비 pg_current_wal_lsn() 지연 바이트
SELECT slot_name,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag
FROM pg_replication_slots WHERE slot_name = 'axp_slot';

-- 4) 야간 정합 배치는 axp.ingest.odoo_cdc.reconcile() 이 수행
--    (건수·수량 합계를 원장과 대조, 오차 시 crit 경보)
