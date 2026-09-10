import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from axp import config  # noqa: E402


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    """격리된 임시 데이터 루트 — 각 테스트가 깨끗한 DB에서 돈다."""
    monkeypatch.setattr(config, "DATA", tmp_path)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "axp.db")
    monkeypatch.setattr(config, "RAW_DIR", tmp_path / "raw")
    monkeypatch.setattr(config, "ARTIFACTS", tmp_path / "artifacts")
    config.ensure_dirs()
    return tmp_path
