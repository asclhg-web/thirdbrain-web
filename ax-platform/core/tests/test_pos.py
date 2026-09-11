"""P3-5: POS 반입 어댑터 2종 테스트 — cp949 정산 CSV·영수증 로그·멱등·이중 집계."""
import os
from pathlib import Path

import pytest

from axp import db
from axp.ingest import pos


@pytest.fixture()
def daily_csv(tmp_path):
    # 국산 POS 정산 내보내기 흉내: cp949, 담당자 연락처(PII) 열 포함
    p = tmp_path / "정산_20250901.csv"
    text = ("영업일자,매장명,상품코드,상품명,판매수량,판매금액,할인금액,담당자 연락처\n"
            "2025-09-01,S-CHORYANG,P-PIE,파이만쥬,120,144000,0,010-0000-0000\n"
            "2025-09-01,S-CHORYANG,P-BREAD,단팥빵,80,96000,4800,010-0000-0000\n"
            "2025-09-01,S-NAMPO,P-PIE,파이만쥬,abc,0,0,010-0000-0000\n")
    p.write_bytes(text.encode("cp949"))
    return p


@pytest.fixture()
def receipt_csv(tmp_path):
    p = tmp_path / "영수증로그.csv"
    p.write_text(
        "영수증번호;판매일시;매장코드;상품코드;수량;단가;할인금액\n"
        "R-0001;2025-09-01 08:12:00;S-CHORYANG;P-PIE;2;1200;0\n"
        "R-0001;2025-09-01 08:12:00;S-CHORYANG;P-BREAD;1;1200;200\n"
        "R-0002;2025-09-01 09:30:00;S-CHORYANG;P-PIE;3;1200;0\n",
        encoding="utf-8-sig")
    return p


def test_daily_cp949_automap_and_pii(tmp_db, daily_csv):
    res = pos.ingest_daily(daily_csv, by="tester")
    assert res["status"] == "ok"
    assert res["rows_ok"] == 2 and res["rows_rejected"] == 1   # abc 수량 거절
    assert "수량이 숫자가 아님" in res["errors"][0]
    rows = db.query("SELECT * FROM staging_sales WHERE _source='pos_daily' ORDER BY product_id")
    assert len(rows) == 2
    bread = [r for r in rows if r["product_id"] == "P-BREAD"][0]
    assert bread["promo_flag"] == 1 and bread["unit_price"] == 1200.0
    assert bread["order_ref"] == "POS/2025-09-01/S-CHORYANG"
    # PII 열은 스테이징 어디에도 남지 않는다
    assert not any("연락처" in str(r) or "010-0000" in str(r) for r in rows)


def test_daily_idempotent(tmp_db, daily_csv):
    first = pos.ingest_daily(daily_csv, by="tester")
    assert first["status"] == "ok"
    again = pos.ingest_daily(daily_csv, by="tester")
    assert again["status"] == "duplicate"
    assert db.scalar("SELECT COUNT(*) FROM staging_sales WHERE _source='pos_daily'") == 2


def test_receipt_semicolon_and_lines(tmp_db, receipt_csv):
    res = pos.ingest_receipt(receipt_csv, by="tester")
    assert res["status"] == "ok" and res["rows_ok"] == 3
    rows = db.query("SELECT * FROM staging_sales WHERE _source='pos_receipt' ORDER BY src_id")
    refs = {r["order_ref"] for r in rows}
    assert refs == {"R-0001", "R-0002"}
    assert all(r["order_date"] == "2025-09-01" for r in rows)
    assert sum(1 for r in rows if r["promo_flag"] == 1) == 1


def test_needs_mapping_when_unknown(tmp_db, tmp_path):
    p = tmp_path / "unknown.csv"
    p.write_text("colA,colB\n1,2\n", encoding="utf-8")
    res = pos.ingest_daily(p, by="tester")
    assert res["status"] == "needs_mapping"
    assert "date" in res["missing"]


def test_double_count_warning(tmp_db, daily_csv):
    pos.init()
    ts = "2025-09-01T00:00:00"
    db.execute("INSERT INTO staging_sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
               (1, "SO900", "2025-09-01", "S-CHORYANG", "P-PIE", 10, 1200,
                "store", 0, ts, ts, "odoo"))
    res = pos.ingest_daily(daily_csv, by="tester")
    assert res["status"] == "ok"
    assert any("S-CHORYANG" in w for w in res["double_count_warnings"])
