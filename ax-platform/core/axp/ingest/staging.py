"""스테이징 (M1) — 원천별 테이블, 원본 컬럼 그대로 + 수집 메타.

변환은 M2의 일이다. 여기서는 받아서 보존만 한다.
"""
from __future__ import annotations

from .. import db

DDL = """
CREATE TABLE IF NOT EXISTS staging_sales (
  src_id INTEGER, order_ref TEXT, order_date TEXT, store_id TEXT, product_id TEXT,
  qty REAL, unit_price REAL, channel TEXT, promo_flag INTEGER,
  _write_date TEXT, _ingested_at TEXT, _source TEXT
);
CREATE TABLE IF NOT EXISTS staging_purchase (
  src_id INTEGER, po_ref TEXT, order_date TEXT, receipt_date TEXT, vendor_id TEXT,
  material_id TEXT, qty REAL, unit_price REAL, lot_id TEXT,
  _write_date TEXT, _ingested_at TEXT, _source TEXT
);
CREATE TABLE IF NOT EXISTS staging_stock_move (
  src_id INTEGER, move_date TEXT, product_id TEXT, from_loc TEXT, to_loc TEXT,
  qty REAL, move_type TEXT, lot_id TEXT, reason TEXT,
  _write_date TEXT, _ingested_at TEXT, _source TEXT
);
CREATE TABLE IF NOT EXISTS staging_mrp (
  src_id INTEGER, mo_ref TEXT, prod_date TEXT, product_id TEXT, line_id TEXT,
  worker_id TEXT, equipment_id TEXT, sop_id TEXT, qty_planned REAL, qty_done REAL,
  shift TEXT, _write_date TEXT, _ingested_at TEXT, _source TEXT
);
CREATE TABLE IF NOT EXISTS staging_quality (
  src_id INTEGER, check_date TEXT, mo_ref TEXT, product_id TEXT, line_id TEXT,
  worker_id TEXT, equipment_id TEXT, material_lot_id TEXT, sop_id TEXT,
  defect_type TEXT, qty_defect REAL, shift TEXT, memo TEXT,
  _write_date TEXT, _ingested_at TEXT, _source TEXT
);
CREATE TABLE IF NOT EXISTS staging_maintenance (
  src_id INTEGER, event_date TEXT, equipment_id TEXT, event_type TEXT,
  duration_min REAL, note TEXT,
  _write_date TEXT, _ingested_at TEXT, _source TEXT
);
CREATE TABLE IF NOT EXISTS staging_excel (
  upload_id INTEGER, sheet_kind TEXT, row_no INTEGER, payload TEXT,
  _raw_ref TEXT, _ingested_at TEXT, _source TEXT
);
CREATE TABLE IF NOT EXISTS staging_forms (
  form_id INTEGER PRIMARY KEY AUTOINCREMENT,
  form_type TEXT NOT NULL, submitted_by TEXT, line_id TEXT, form_date TEXT,
  payload TEXT NOT NULL, memo TEXT DEFAULT '',
  _ingested_at TEXT, _source TEXT
);
CREATE TABLE IF NOT EXISTS staging_iot (
  reading_ts TEXT NOT NULL, equipment_id TEXT NOT NULL, signal TEXT NOT NULL,
  value REAL, _ingested_at TEXT, _source TEXT
);
CREATE INDEX IF NOT EXISTS idx_iot_ts ON staging_iot (equipment_id, signal, reading_ts);
CREATE TABLE IF NOT EXISTS cdc_state (
  table_name TEXT PRIMARY KEY, last_src_id INTEGER NOT NULL DEFAULT 0,
  last_run_at TEXT, last_write_date TEXT
);
"""


def init() -> None:
    db.executescript(DDL)
    # P5-I5 마이그레이션: 이 DDL 이전에 만들어진 DB의 cdc_state에는
    # 갱신 워터마크 컬럼이 없다 — 있으면 그대로, 없으면 추가(멱등).
    try:
        db.execute("ALTER TABLE cdc_state ADD COLUMN last_write_date TEXT")
    except Exception:
        pass
