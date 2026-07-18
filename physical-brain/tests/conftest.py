import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest  # noqa: E402


@pytest.fixture()
def fresh_db(tmp_path, monkeypatch):
    """테스트마다 격리된 DB + 샘플 볼트 시드."""
    monkeypatch.setenv("PB_DB", str(tmp_path / "test.db"))
    monkeypatch.setenv("LLM_MODEL", "")  # 규칙 기반 폴백 강제 (오프라인)
    monkeypatch.setenv("PB_HEARTBEAT", "0")  # 테스트에서는 백그라운드 루프 금지
    from graph import store
    store.reset_conn()
    from pipelines.vault_sync import sync_vault
    vault = os.path.join(os.path.dirname(__file__), "..", "graph", "sample_vault")
    sync_vault(vault)
    yield store
    store.reset_conn()
