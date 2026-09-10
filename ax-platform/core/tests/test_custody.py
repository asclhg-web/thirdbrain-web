"""M0 커스터디 — 반출 게이트·자산 대장 규율."""
import pytest

from axp.custody import export_gate, ledger


def test_export_requires_approval(tmp_db):
    rid = export_gate.request("t", "api.anthropic.com", "why", "me", "payload")
    with pytest.raises(export_gate.ExportDenied):
        export_gate.check_and_mark_executed(rid, "payload", "api.anthropic.com")


def test_export_payload_tamper_blocked(tmp_db):
    rid = export_gate.request("t", "api.anthropic.com", "why", "me", "payload")
    export_gate.decide(rid, "approver", True)
    with pytest.raises(export_gate.ExportDenied):
        export_gate.check_and_mark_executed(rid, "DIFFERENT", "api.anthropic.com")


def test_export_approved_flow_and_reconcile(tmp_db):
    rid = export_gate.request("t", "api.anthropic.com", "why", "me", "p")
    export_gate.decide(rid, "approver", True)
    row = export_gate.check_and_mark_executed(rid, "p", "api.anthropic.com")
    assert row["status"] == "executed"
    assert export_gate.reconcile()["ok"]


def test_ledger_versions(tmp_db):
    ledger.register("a", "script", "x.py", "me", version="v1")
    ledger.register("a", "script", "x.py", "me", version="v2")
    assert ledger.latest("a")["version"] == "v2"
