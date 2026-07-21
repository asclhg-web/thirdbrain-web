"""G06 검증: 프로필 — 별도 DB 격리, 전환, 복귀."""
from graph_core import profiles, store as core_store


def test_default_profile_exists(fresh_db):
    ps = profiles.list_profiles()
    assert any(p["id"] == "default" and p["active"] for p in ps)


def test_profile_isolation_and_switch_back(fresh_db):
    """프로필 B에 쓴 데이터는 A(기본)에서 보이지 않는다 — 완전 격리."""
    try:
        fresh_db.upsert_node("person:본인", "Person", {"name": "본인"})
        assert fresh_db.get_node("person:본인")

        b = profiles.create("아내", "personal")
        profiles.activate(b["id"])
        assert fresh_db.get_node("person:본인") is None, "새 프로필은 빈 그래프"
        fresh_db.upsert_node("person:아내", "Person", {"name": "아내"})
        assert fresh_db.get_node("person:아내")

        profiles.activate("default")
        assert fresh_db.get_node("person:본인"), "기본 프로필 데이터 유지"
        assert fresh_db.get_node("person:아내") is None, "격리 확인"
    finally:
        core_store.set_db_path(None)
        core_store.reset_conn()


def test_profiles_page(fresh_db):
    from fastapi.testclient import TestClient
    from server.main import app
    c = TestClient(app)
    try:
        r = c.post("/profiles/create", data={"name": "투자", "kind": "investment"},
                   follow_redirects=True)
        assert "투자" in r.text and "investment" in r.text
    finally:
        core_store.set_db_path(None)
        core_store.reset_conn()
