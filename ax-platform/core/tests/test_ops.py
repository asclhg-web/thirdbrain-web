"""운영 자동화 — 재학습 게이트·교차 검증·지식센터·승급 자동 실행 규율."""
import pandas as pd
import pytest

from axp import db


def _seed_min_sales(tmp_db):
    from axp.dataset import transform
    transform.apply_schema()
    cal = pd.DataFrame([{"date_key": f"2026-01-{d:02d}", "dow": 0, "month": 1,
                         "is_weekend": 0, "is_holiday_week": 0} for d in range(1, 20)])
    db.write_df(cal, "dim_calendar")
    db.write_df(pd.DataFrame([{"product_id": "P", "product_name": "p",
                               "category": "c", "unit_price": 1}]), "dim_product")
    db.write_df(pd.DataFrame([{"store_id": "S", "store_name": "본점",
                               "channel": "retail"}]), "dim_store")
    rows = [{"date_key": f"2026-01-{d:02d}", "store_id": "S", "product_id": "P",
             "qty": 100.0, "revenue": 0, "channel": "r", "promo_flag": 0}
            for d in range(1, 20)]
    db.write_df(pd.DataFrame(rows), "fact_sales")


def test_cross_validation_catches_mismatch(tmp_db):
    """엑셀 수치가 원장과 다르면 반드시 잡는다 (I-09의 재발 방지)."""
    import json
    from axp.dataset import validation
    from axp.ingest import staging
    _seed_min_sales(tmp_db)
    staging.init()
    db.execute(
        "INSERT INTO staging_excel (upload_id, sheet_kind, row_no, payload, "
        "_raw_ref, _ingested_at, _source) VALUES (1,'sales_summary',0,?, '', '', 't')",
        (json.dumps({"date": "2026-01-05", "store_id": "S", "product_id": "P",
                     "qty": 160.0}),))
    v = validation.excel_vs_ledger()
    assert v["n_mismatch"] == 1
    assert v["mismatches"][0]["qty_ledger"] == 100.0


def test_memo_surge_needs_concentration(tmp_db):
    """분산된 키워드는 후보가 되지 않는다 — 집중(60%+·5건+)만."""
    from axp.dataset import transform
    from axp.studio import knowledge
    transform.apply_schema()
    rows = []
    for i in range(10):
        rows.append({"defect_id": i, "date_key": "2026-01-15", "shift": "주간",
                     "product_id": "P", "line_id": "L", "worker_id": "W",
                     "equipment_id": f"EQ-{i % 5}",     # 5개 설비에 분산
                     "material_lot_id": None, "sop_id": "S1",
                     "defect_type": "t", "qty_defect": 1, "qty_produced": 10,
                     "memo": "표면 미세균열 발생", "mo_ref": f"M{i}"})
    with db.conn() as c:                      # 차원 미시드 — FK 끄고 사실만 적재
        c.execute("PRAGMA foreign_keys=OFF")
        db.load_frame(c, pd.DataFrame(rows), "fact_defect")
    assert knowledge.surge_candidates("2026-01-20", weeks=2) == []


def test_auto_execute_requires_active_promotion(tmp_db):
    """승급 없는 유형은 role='auto' 승인이 거부된다."""
    from axp.agents import inbox
    from axp.judge import cards as jcards
    cid = jcards.create({
        "kind": "allocation", "agent": "t", "proposal": "p",
        "values": [{"name": "n", "value": 10, "source": "s"}],
        "evidence": {"kind": "dims", "dims": {"product_id": "P"},
                     "product_id": "P", "allocations": []},
        "approver": "a"})
    with pytest.raises(inbox.PermissionError_):
        inbox.decide(cid, "system(승급)", "auto", True)


def test_parquet_roundtrip(tmp_db):
    from axp.dataset import export
    _seed_min_sales(tmp_db)
    counts = export.export_parquet(tmp_db / "pq")
    assert counts["fact_sales"] == 19
    back = pd.read_parquet(tmp_db / "pq" / "fact_sales.parquet")
    assert len(back) == 19
