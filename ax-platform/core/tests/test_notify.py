"""P2-A3 — 알림 모듈: dry-run 기록·등급 필터·반출 게이트 차단."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from axp import config, notify  # noqa: E402


def test_dryrun_writes_log(tmp_db, monkeypatch):
    monkeypatch.delenv("AXP_NOTIFY", raising=False)
    r = notify.send("crit", "test", "장애 발생")
    assert r.get("dryrun", "").startswith("ok")
    log = (config.ARTIFACTS / "notify.log").read_text(encoding="utf-8")
    assert "장애 발생" in log


def test_level_filter(tmp_db, monkeypatch):
    monkeypatch.setenv("AXP_NOTIFY_MIN_LEVEL", "crit")
    r = notify.send("warn", "test", "이건 안 나감")
    assert "skipped" in r


def test_export_gate_blocks_unlisted_webhook(tmp_db, monkeypatch):
    monkeypatch.setenv("AXP_NOTIFY", "webhook")
    monkeypatch.setenv("AXP_WEBHOOK_URL", "https://evil.example.com/hook")
    monkeypatch.setattr(config, "EXPORT_ALLOWED_HOSTS", ["hooks.company.co.kr"])
    r = notify.send("crit", "test", "게이트 시험")
    assert r["webhook"] == "blocked(export-gate)"
    log = (config.ARTIFACTS / "notify.log").read_text(encoding="utf-8")
    assert "반출 게이트 차단" in log


def test_cycle_summary_crit_on_failure(tmp_db, monkeypatch):
    monkeypatch.delenv("AXP_NOTIFY", raising=False)
    r = notify.cycle_summary("2026-09-11", {"a": "ok", "b": "error: X"})
    assert r.get("dryrun", "").startswith("ok")
    log = (config.ARTIFACTS / "notify.log").read_text(encoding="utf-8")
    assert "1/2 단계 실패" in log
