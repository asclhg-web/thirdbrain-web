"""T01·T17~T19 검증: API·대시보드 페이지."""
from fastapi.testclient import TestClient


def _client(fresh_db):
    from server.main import app
    return TestClient(app)


def test_health(fresh_db):
    c = _client(fresh_db)
    assert c.get("/health").json()["status"] == "ok"


def test_ask_api(fresh_db):
    from datetime import datetime
    from pipelines.mock_health import generate
    generate(days=7, end=datetime.now(), seed=5)
    c = _client(fresh_db)
    r = c.post("/api/ask", json={"question": "오늘 아버지 약 뭐야?"}).json()
    assert "혈압약" in r["answer"]


def test_dashboard_pages(fresh_db):
    from datetime import datetime
    from pipelines.mock_health import generate
    generate(days=7, end=datetime.now(), seed=5)
    c = _client(fresh_db)
    for path in ("/", "/signals", "/graphview", "/scenarios"):
        r = c.get(path)
        assert r.status_code == 200, path
    assert "피지컬브레인" in c.get("/").text
    assert "결측" in c.get("/signals").text  # 결측 표시 원칙 노출
