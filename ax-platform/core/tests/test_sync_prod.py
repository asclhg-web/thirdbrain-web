"""P3: prod 적재기(sync_prod) 테스트 — 매핑 뷰 → 스테이징 증분·멱등 (PG 전용)."""
import uuid

import pytest

from axp import db
from axp.ingest import odoo_cdc, staging

pytestmark = pytest.mark.skipif(
    db.BACKEND != "postgres", reason="sync_prod는 PostgreSQL 백엔드 전용")


@pytest.fixture()
def prod_view(tmp_db, monkeypatch):
    """실 매핑 뷰를 흉내내는 임시 스키마·테이블 — 실뷰와 같은 컬럼 순서."""
    schema = "test_prod_" + uuid.uuid4().hex[:8]
    with db.conn() as c:
        c.execute(f"CREATE SCHEMA {schema}")
        c.execute(f"""CREATE TABLE {schema}.v_sales (
            id INTEGER, order_ref TEXT, order_date TEXT, store_id TEXT,
            product_id TEXT, qty REAL, unit_price REAL, channel TEXT,
            promo_flag INTEGER, write_date TEXT)""")
        c.execute(f"INSERT INTO {schema}.v_sales VALUES "
                  "(1,'S00001','2026-09-01','1','7',120,1200,'1',0,'2026-09-01'),"
                  "(2,'S00002','2026-09-02','1','8',80,900,'1',1,'2026-09-02')")
    monkeypatch.setattr(odoo_cdc, "PROD_SERIES", {
        f"{schema}.v_sales": "staging_sales",
        f"{schema}.v_missing": "staging_quality",   # 부재 뷰 → -1 표식 검증
    })
    yield schema
    with db.conn() as c:
        c.execute(f"DROP SCHEMA {schema} CASCADE")


def test_sync_prod_incremental_and_idempotent(prod_view):
    staging.init()
    r1 = odoo_cdc.sync_prod()
    assert r1["staging_sales"] == 2
    assert r1["staging_quality"] == -1          # 뷰 없음 — 우아한 스킵
    assert db.scalar("SELECT COUNT(*) FROM staging_sales") == 2
    row = db.one("SELECT * FROM staging_sales WHERE src_id=2")
    assert row["order_ref"] == "S00002" and row["promo_flag"] == 1
    assert row["_source"] == "odoo_prod"

    r2 = odoo_cdc.sync_prod()                   # 멱등 — 새 행 없음
    assert r2["staging_sales"] == 0

    with db.conn() as c:                        # 증분 — id 3 추가분만
        c.execute(f"INSERT INTO {prod_view}.v_sales VALUES "
                  "(3,'S00003','2026-09-03','1','7',60,1200,'1',0,'2026-09-03')")
    r3 = odoo_cdc.sync_prod()
    assert r3["staging_sales"] == 1
    assert db.scalar("SELECT COUNT(*) FROM staging_sales") == 3


def test_sync_prod_rejects_sqlite(monkeypatch, tmp_db):
    monkeypatch.setattr(db, "BACKEND", "sqlite")
    with pytest.raises(RuntimeError):
        odoo_cdc.sync_prod()
