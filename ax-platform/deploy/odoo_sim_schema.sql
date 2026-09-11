-- P2-A2: Odoo 16 표준 스키마 축약본 — odoo_cdc_prod.sql 검증용 시뮬레이터.
-- 실 Odoo의 동명 테이블에서 CDC가 실제로 읽는 컬럼만 추렸다.
-- (버전 메모: quality_*·maintenance_* 는 해당 모듈 설치 시에만 존재 —
--  미설치 고객은 axp_pub_core 발행을 사용한다. 아래 두 발행 모두 제공.)

CREATE TABLE IF NOT EXISTS sale_order (
  id BIGSERIAL PRIMARY KEY, name VARCHAR, partner_id BIGINT,
  date_order TIMESTAMP, state VARCHAR, amount_total NUMERIC
);
CREATE TABLE IF NOT EXISTS sale_order_line (
  id BIGSERIAL PRIMARY KEY, order_id BIGINT, product_id BIGINT,
  product_uom_qty NUMERIC, price_unit NUMERIC, qty_delivered NUMERIC
);
CREATE TABLE IF NOT EXISTS purchase_order (
  id BIGSERIAL PRIMARY KEY, name VARCHAR, partner_id BIGINT,
  date_order TIMESTAMP, state VARCHAR, amount_total NUMERIC
);
CREATE TABLE IF NOT EXISTS purchase_order_line (
  id BIGSERIAL PRIMARY KEY, order_id BIGINT, product_id BIGINT,
  product_qty NUMERIC, price_unit NUMERIC
);
CREATE TABLE IF NOT EXISTS stock_move (
  id BIGSERIAL PRIMARY KEY, name VARCHAR, product_id BIGINT,
  product_uom_qty NUMERIC, state VARCHAR, date TIMESTAMP,
  location_id BIGINT, location_dest_id BIGINT
);
CREATE TABLE IF NOT EXISTS stock_quant (
  id BIGSERIAL PRIMARY KEY, product_id BIGINT, location_id BIGINT,
  quantity NUMERIC, in_date TIMESTAMP
);
CREATE TABLE IF NOT EXISTS stock_scrap (
  id BIGSERIAL PRIMARY KEY, name VARCHAR, product_id BIGINT,
  scrap_qty NUMERIC, date_done TIMESTAMP, origin VARCHAR
);
CREATE TABLE IF NOT EXISTS mrp_production (
  id BIGSERIAL PRIMARY KEY, name VARCHAR, product_id BIGINT,
  product_qty NUMERIC, qty_produced NUMERIC, state VARCHAR,
  date_start TIMESTAMP, date_finished TIMESTAMP
);
CREATE TABLE IF NOT EXISTS mrp_workorder (
  id BIGSERIAL PRIMARY KEY, name VARCHAR, production_id BIGINT,
  workcenter_id BIGINT, state VARCHAR, duration NUMERIC
);
CREATE TABLE IF NOT EXISTS quality_check (
  id BIGSERIAL PRIMARY KEY, name VARCHAR, product_id BIGINT,
  quality_state VARCHAR, control_date TIMESTAMP
);
CREATE TABLE IF NOT EXISTS quality_alert (
  id BIGSERIAL PRIMARY KEY, name VARCHAR, product_id BIGINT,
  stage_id BIGINT, description TEXT
);
CREATE TABLE IF NOT EXISTS maintenance_equipment (
  id BIGSERIAL PRIMARY KEY, name VARCHAR, serial_no VARCHAR,
  location VARCHAR, effective_date DATE
);
CREATE TABLE IF NOT EXISTS maintenance_request (
  id BIGSERIAL PRIMARY KEY, name VARCHAR, equipment_id BIGINT,
  maintenance_type VARCHAR, request_date DATE, stage_id BIGINT,
  duration NUMERIC
);

-- 발행 2종: 전체(quality·maintenance 모듈 포함) / core(6대 계열만)
DROP PUBLICATION IF EXISTS axp_pub;
CREATE PUBLICATION axp_pub FOR TABLE
  sale_order, sale_order_line,
  purchase_order, purchase_order_line,
  stock_move, stock_quant, stock_scrap,
  mrp_production, mrp_workorder,
  quality_check, quality_alert,
  maintenance_request, maintenance_equipment;

DROP PUBLICATION IF EXISTS axp_pub_core;
CREATE PUBLICATION axp_pub_core FOR TABLE
  sale_order, sale_order_line,
  purchase_order, purchase_order_line,
  stock_move, stock_quant, stock_scrap,
  mrp_production, mrp_workorder;
