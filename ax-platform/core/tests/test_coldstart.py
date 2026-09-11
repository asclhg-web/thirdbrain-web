"""P2-C3 — 신제품 콜드스타트: 공여 선택·배율·광폭 구간."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from axp import db  # noqa: E402
from axp.learn import coldstart  # noqa: E402


def _seed(tmp_db):
    db.executescript(
        "CREATE TABLE IF NOT EXISTS fact_sales ("
        "date_key TEXT, store_id TEXT, product_id TEXT, qty REAL, channel TEXT);")
    rows = []
    days = pd.date_range("2026-03-01", "2026-09-10")
    for d in days:  # 공여: 요일 패턴 뚜렷(주말 2배)
        base = 200 if d.dayofweek >= 5 else 100
        rows.append((d.date().isoformat(), "S-1", "P-DONOR", base, "retail"))
    for d in days[-10:]:  # 신제품: 10일, 공여의 절반 규모
        base = 100 if d.dayofweek >= 5 else 50
        rows.append((d.date().isoformat(), "S-1", "P-NEW", base, "retail"))
    db.executemany("INSERT INTO fact_sales VALUES (?,?,?,?,?)", rows)


def test_needs_cold_start(tmp_db):
    _seed(tmp_db)
    assert coldstart.needs_cold_start("P-NEW")
    assert not coldstart.needs_cold_start("P-DONOR")


def test_transfer_ratio_and_wide_range(tmp_db):
    _seed(tmp_db)
    r = coldstart.forecast("P-NEW", "2026-09-10", horizon=7)
    assert r["donor"] == "P-DONOR"
    assert 0.4 < r["ratio"] < 0.6          # 절반 규모가 배율로 잡힌다
    week = r["total_p50"]
    # 공여 주간(5×100+2×200=900)의 절반 근방
    assert 350 < week < 550, week
    assert r["total_p10"] < week < r["total_p90"]
    assert (r["total_p90"] - r["total_p10"]) / week > 0.5   # 광폭 구간
    assert "콜드스타트" in r["evidence"] and "P-DONOR" in r["evidence"]


def test_no_history_uses_launch_ratio(tmp_db):
    _seed(tmp_db)
    r = coldstart.forecast("P-BRANDNEW", "2026-09-10", horizon=7)
    assert r["ratio"] == coldstart.LAUNCH_RATIO
    assert "출시 보수 계수" in r["evidence"]
