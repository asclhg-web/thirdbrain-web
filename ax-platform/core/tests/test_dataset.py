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
