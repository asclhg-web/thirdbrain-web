"""T05·T06 검증: 목업 결측 원칙, CSV 인제스트(정상/실패)."""
import os
from datetime import datetime


def test_mock_missing_preserved(fresh_db):
    from pipelines.mock_health import generate
    r = generate(days=10, end=datetime(2026, 7, 15, 12, 0), seed=7)
    assert r["missing"] > 0  # 결측이 실제로 존재 (0 채우기 금지)
    ms = fresh_db.measurements("아버지", "bp_sys", 10, datetime(2026, 7, 15, 12, 0))
    assert ms and all(m["value"] > 60 for m in ms)


def test_ingest_ok_and_failed(fresh_db, tmp_path, monkeypatch):
    from pipelines import ingest
    monkeypatch.setattr(ingest, "INBOX", str(tmp_path / "inbox"))
    monkeypatch.setattr(ingest, "PROCESSED", str(tmp_path / "processed"))
    monkeypatch.setattr(ingest, "FAILED", str(tmp_path / "failed"))
    os.makedirs(ingest.INBOX)
    (tmp_path / "inbox" / "good.csv").write_text(
        "person,type,value,unit,measured_at\n나,bp_sys,124,mmHg,2026-07-15T07:00:00\n", encoding="utf-8")
    (tmp_path / "inbox" / "bad.csv").write_text("foo,bar\n1,2\n", encoding="utf-8")
    r = ingest.process_inbox()
    assert r["ok"] and r["ok"][0][1] == 1
    assert r["failed"] and "누락" in r["failed"][0][1]
    assert os.path.exists(str(tmp_path / "failed" / "bad.csv.error.txt"))
    ms = fresh_db.measurements("나", "bp_sys", 400, datetime(2026, 7, 16))
    assert any(m["value"] == 124 for m in ms)
