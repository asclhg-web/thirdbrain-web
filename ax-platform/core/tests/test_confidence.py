"""M5-2 확신도 루프 — 독립 확인·처리 순서(I-11 재발 방지)·반려 감쇠."""
import json

from axp import db
from axp.graph import confidence


def _seed_candidates(windows_z):
    """mining_candidates에 같은 조합의 관측 창들을 직접 심는다."""
    db.executescript("""
    CREATE TABLE IF NOT EXISTS mining_candidates (
      cand_id INTEGER PRIMARY KEY AUTOINCREMENT, run_date TEXT, dims TEXT,
      window_start TEXT, window_end TEXT, n_produced REAL, n_defect REAL,
      rate REAL, base_rate REAL, lift REAL, z REAL, status TEXT DEFAULT 'new');
    """)
    for w_end, z in windows_z:
        db.execute(
            "INSERT INTO mining_candidates (run_date, dims, window_start, window_end,"
            " n_produced, n_defect, rate, base_rate, lift, z) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (w_end, json.dumps({"equipment_id": "EQ-X"}), "2025-01-01", w_end,
             1000, 40, 0.04, 0.015, 2.6, z))


def test_out_of_order_windows_still_three_confirms(tmp_db):
    """I-11: 창이 뒤섞여 도착해도(z 큰 늦은 창 먼저) 확인 3회가 유지된다."""
    _seed_candidates([("2025-09-01", 33.0), ("2025-08-15", 32.0), ("2025-09-20", 25.0)])
    confidence.ingest_mining("2025-09-20")
    row = db.one("SELECT * FROM causal_candidates")
    confirms = json.loads(row["confirmations"])
    assert len(confirms) == 3
    assert row["confidence"] >= confidence.PROMOTE_CONF
    assert confidence.check_thresholds()          # 상신됨


def test_close_windows_not_independent(tmp_db):
    """14일 미만 간격의 창은 독립 확인으로 세지 않는다."""
    _seed_candidates([("2025-08-15", 30.0), ("2025-08-20", 30.0)])
    confidence.ingest_mining("2025-08-20")
    confirms = json.loads(db.one("SELECT confirmations FROM causal_candidates")["confirmations"])
    assert len(confirms) == 1


def test_reject_halves_confidence(tmp_db):
    _seed_candidates([("2025-08-15", 32.0), ("2025-09-01", 32.0), ("2025-09-20", 32.0)])
    confidence.ingest_mining("2025-09-20")
    sub = confidence.check_thresholds()[0]
    before = sub["confidence"]
    res = confidence.decide(sub["cc_id"], False, "승인자", "현장 확인 결과 무관")
    row = db.one("SELECT * FROM causal_candidates WHERE cc_id=?", (sub["cc_id"],))
    assert res["status"].startswith("rejected")
    assert row["status"] == "watching" and row["confidence"] < before / 1.9
