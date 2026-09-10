-- M2-1 표준 데이터셋 스키마 — 사실 테이블 6계열 + 차원
-- 명명 규칙: 스네이크케이스, fact_/dim_ 접두어, 단수형.
-- 모든 사실 행은 시점 키(date_key, 필요시 shift)를 가지며,
-- 품질(fact_defect)은 4M 차원 키 전부를 가진다.

CREATE TABLE IF NOT EXISTS dim_calendar (
  date_key TEXT PRIMARY KEY, dow INTEGER, month INTEGER,
  is_weekend INTEGER, is_holiday_week INTEGER
);
CREATE TABLE IF NOT EXISTS dim_product (
  product_id TEXT PRIMARY KEY, product_name TEXT, category TEXT, unit_price REAL
);
CREATE TABLE IF NOT EXISTS dim_store (
  store_id TEXT PRIMARY KEY, store_name TEXT, channel TEXT
);
CREATE TABLE IF NOT EXISTS dim_worker (
  worker_id TEXT PRIMARY KEY, worker_name TEXT
);
CREATE TABLE IF NOT EXISTS dim_equipment (
  equipment_id TEXT PRIMARY KEY, line_id TEXT, equipment_type TEXT
);
CREATE TABLE IF NOT EXISTS dim_material (
  material_id TEXT PRIMARY KEY, material_name TEXT
);
CREATE TABLE IF NOT EXISTS dim_material_lot (
  lot_id TEXT PRIMARY KEY, material_id TEXT REFERENCES dim_material(material_id),
  vendor_id TEXT, received_date TEXT
);
CREATE TABLE IF NOT EXISTS dim_sop (
  sop_id TEXT PRIMARY KEY, sop_name TEXT
);
CREATE TABLE IF NOT EXISTS dim_promo (
  promo_id INTEGER PRIMARY KEY AUTOINCREMENT,
  date_start TEXT, date_end TEXT, product_id TEXT, promo_name TEXT, discount_pct REAL
);

-- 1) 판매
CREATE TABLE IF NOT EXISTS fact_sales (
  date_key TEXT NOT NULL REFERENCES dim_calendar(date_key),
  store_id TEXT NOT NULL REFERENCES dim_store(store_id),
  product_id TEXT NOT NULL REFERENCES dim_product(product_id),
  qty REAL NOT NULL, revenue REAL NOT NULL,
  channel TEXT, promo_flag INTEGER DEFAULT 0,
  PRIMARY KEY (date_key, store_id, product_id)
);
-- 2) 생산
CREATE TABLE IF NOT EXISTS fact_production (
  mo_ref TEXT NOT NULL, date_key TEXT NOT NULL, shift TEXT NOT NULL,
  line_id TEXT, product_id TEXT REFERENCES dim_product(product_id),
  worker_id TEXT REFERENCES dim_worker(worker_id),
  equipment_id TEXT REFERENCES dim_equipment(equipment_id),
  sop_id TEXT REFERENCES dim_sop(sop_id),
  qty_planned REAL, qty_done REAL,
  PRIMARY KEY (mo_ref)
);
-- 3) 구매·입고
CREATE TABLE IF NOT EXISTS fact_procurement (
  po_ref TEXT NOT NULL, date_key TEXT NOT NULL,
  vendor_id TEXT, material_id TEXT REFERENCES dim_material(material_id),
  lot_id TEXT REFERENCES dim_material_lot(lot_id),
  qty REAL, amount REAL,
  PRIMARY KEY (po_ref, material_id, lot_id)
);
-- 4) 재고이동·폐기
CREATE TABLE IF NOT EXISTS fact_inventory_move (
  move_id INTEGER PRIMARY KEY,
  date_key TEXT NOT NULL, product_id TEXT REFERENCES dim_product(product_id),
  from_loc TEXT, to_loc TEXT, move_type TEXT, qty REAL, lot_id TEXT, reason TEXT
);
-- 5) 품질 (defect_fact — 4M 차원 키 전부)
CREATE TABLE IF NOT EXISTS fact_defect (
  defect_id INTEGER PRIMARY KEY,
  date_key TEXT NOT NULL, shift TEXT,
  product_id TEXT REFERENCES dim_product(product_id),
  line_id TEXT,
  worker_id TEXT REFERENCES dim_worker(worker_id),               -- Man
  equipment_id TEXT REFERENCES dim_equipment(equipment_id),     -- Machine
  material_lot_id TEXT REFERENCES dim_material_lot(lot_id),     -- Material
  sop_id TEXT REFERENCES dim_sop(sop_id),                       -- Method
  defect_type TEXT, qty_defect REAL, qty_produced REAL, memo TEXT, mo_ref TEXT
);
-- 6) 설비 (정지·경보·정비 + 센서 일집계)
CREATE TABLE IF NOT EXISTS fact_equipment_event (
  event_id INTEGER PRIMARY KEY,
  date_key TEXT NOT NULL,
  equipment_id TEXT REFERENCES dim_equipment(equipment_id),
  event_type TEXT, duration_min REAL, note TEXT
);
CREATE TABLE IF NOT EXISTS fact_sensor_daily (
  date_key TEXT NOT NULL, equipment_id TEXT NOT NULL, signal TEXT NOT NULL,
  n INTEGER, mean REAL, std REAL, p95 REAL, max REAL,
  PRIMARY KEY (date_key, equipment_id, signal)
);
CREATE INDEX IF NOT EXISTS idx_defect_date ON fact_defect (date_key);
CREATE INDEX IF NOT EXISTS idx_sales_prod ON fact_sales (product_id, date_key);
