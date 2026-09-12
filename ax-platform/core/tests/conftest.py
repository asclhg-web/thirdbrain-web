import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from axp import config  # noqa: E402


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    """격리된 임시 데이터 루트 — 각 테스트가 깨끗한 DB에서 돈다.

    P3-I7: PG 백엔드에서는 테스트마다 스키마 ax_<md5(DATA)> 가 생기는데,
    정리하지 않으면 플랫폼 DB에 영구 누적된다(복구 드릴에서 적발 —
    잔류 테스트 스키마 30여 개, 덤프 비대·복원 FK 소음). 테스트 종료 시
    해당 스키마를 반드시 떨어뜨린다."""
    monkeypatch.setattr(config, "DATA", tmp_path)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "axp.db")
    monkeypatch.setattr(config, "RAW_DIR", tmp_path / "raw")
    monkeypatch.setattr(config, "ARTIFACTS", tmp_path / "artifacts")
    config.ensure_dirs()
    yield tmp_path
    if os.environ.get("AXP_DB", "sqlite") == "postgres":
        import hashlib

        from axp import db as _db
        schema = "ax_" + hashlib.md5(str(tmp_path).encode()).hexdigest()[:12]
        try:
            with _db.conn() as c:
                c.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
        except Exception:
            pass  # 정리 실패가 테스트를 깨뜨리진 않는다
        # P7-I1: 프로파일별 캐시 연결이 테스트마다 누적돼 스위트가 커지면
        # max_connections 고갈("too many clients")로 마지막 테스트가 깨진다 —
        # 이 테스트의 스키마 연결을 닫고 캐시에서 제거한다.
        cache = getattr(_db._tls, "pg", None) or {}
        raw = cache.pop(schema, None)
        if raw is not None:
            try:
                raw.close()
            except Exception:
                pass
