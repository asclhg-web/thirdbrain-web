"""P5-S6: 내부 API 공유 키 — 설정 시 X-API-Key 없으면 401 (/health 제외)."""
import os

from fastapi.testclient import TestClient

from axp import api


def test_api_key_enforced_when_set(tmp_db, monkeypatch):
    monkeypatch.setenv("AXP_API_KEY", "sekrit")
    c = TestClient(api.app)
    assert c.get("/health").status_code == 200            # 하트비트는 예외
    assert c.get("/cards").status_code == 401
    assert c.get("/cards", headers={"X-API-Key": "wrong"}).status_code == 401
    assert c.get("/cards", headers={"X-API-Key": "sekrit"}).status_code == 200


def test_api_open_when_unset(tmp_db, monkeypatch):
    monkeypatch.delenv("AXP_API_KEY", raising=False)
    c = TestClient(api.app)
    assert c.get("/cards").status_code == 200             # 기존 동작 유지
