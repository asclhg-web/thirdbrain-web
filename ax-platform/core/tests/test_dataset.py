"""M2 — 코드 매핑 격리 큐·계약 규칙·시점 안전."""
import pandas as pd
import pytest

from axp import db
from axp.dataset import codemap
from axp.custody import contracts


def test_quarantine_and_confirm(tmp_db):
    codemap.init()
    assert codemap.resolve("product", "낯선빵") is None          # 격리
    q = codemap.pending()
    assert q and q[0]["alias"] == "낯선빵"
    codemap.confirm(q[0]["q_id"], "P-NEW", "스튜어드")
    assert codemap.resolve("product", "낯선빵") == "P-NEW"       # 재발 없음
    assert not codemap.pending()


def test_seed_aliases(tmp_db):
    codemap.init()
    assert codemap.resolve("store", "본점") == "S-MAIN"


def test_vendor_alias_projection(tmp_db):
    """P5-V: 공급사 숫자 id → codemap 별칭 투영 — res_partner 미복제(PII)
    결정의 표시 경로. 사전에 없는 id는 숫자 그대로(정직한 폴백, 격리 없음)."""
    from axp import common
    from axp.dataset import transform
    from axp.ingest import staging
    staging.init()
    codemap.init()
    db.execute("INSERT INTO staging_purchase VALUES "
               "(1,'P1','2026-09-01','2026-09-02','7','M-FLOUR',10,900,'L1','2026-09-01','2026-09-01','t')")
    db.execute("INSERT INTO staging_purchase VALUES "
               "(2,'P2','2026-09-01','2026-09-02','3','M-SUGAR',5,700,'L2','2026-09-01','2026-09-01','t')")
    db.execute("INSERT OR REPLACE INTO code_dictionary "
               "(domain, alias, standard_code, confirmed_by, confirmed_at) VALUES "
               "('vendor','7','V-제빵T','steward', ?)", (common.now_iso(),))
    transform.run_all()
    vendors = dict(
        (r["lot_id"], r["vendor_id"])
        for r in db.query("SELECT lot_id, vendor_id FROM dim_material_lot"))
    assert vendors["L1"] == "V-제빵T"                 # 별칭 투영
    assert vendors["L2"] == "3"                       # 미등재 → 숫자 유지
    assert db.scalar(
        "SELECT vendor_id FROM fact_procurement WHERE po_ref='P1'") == "V-제빵T"
    assert not [q for q in codemap.pending() if q["domain"] == "vendor"]


def test_contract_rules_generated():
    rules = contracts.quality_rules("fact_sales")
    checks = {(r["column"], r["check"]) for r in rules}
    assert ("qty", "range") in checks and ("date_key", "not_null") in checks


def test_contract_missing_raises():
    with pytest.raises(contracts.ContractError):
        contracts.load("no_such_table")


def test_point_in_time_features(tmp_db):
    """미래 행의 past 특징이 미래 실측을 참조하지 않는다."""
    from axp.dataset import features, transform
    # 최소 판매 데이터 구성
    transform.apply_schema()
    rows = [{"date_key": f"2026-01-{d:02d}", "store_id": "S", "product_id": "P",
             "qty": 10.0 + d, "revenue": 0, "channel": "r", "promo_flag": 0}
            for d in range(1, 31)]
    cal = pd.DataFrame([{"date_key": r["date_key"], "dow": 0, "month": 1,
                         "is_weekend": 0, "is_holiday_week": 0} for r in rows])
    db.write_df(cal, "dim_calendar")                      # FK: 차원 먼저
    db.write_df(pd.DataFrame([{"product_id": "P", "product_name": "p",
                               "category": "c", "unit_price": 1}]), "dim_product")
    db.write_df(pd.DataFrame([{"store_id": "S", "store_name": "s",
                               "channel": "retail"}]), "dim_store")
    db.write_df(pd.DataFrame(rows), "fact_sales")
    f = features.build("2026-01-30", horizon=3)
    fut = f[f["date_key"] > "2026-01-30"]
    assert fut["target"].isna().all()
    # 미래 3행의 lag_1은 모두 as_of 시점 고정값(마지막 관측 이후 ffill)
    assert fut["lag_1"].nunique() == 1
