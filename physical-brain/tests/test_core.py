"""G01 검증: 그래프 코어 분리 — Frame 레지스트리 합집합·검증, 파사드 호환."""
from graph_core import registry


def test_personal_frame_registered():
    assert "personal-v2" in registry.frames()
    assert {"Person", "Skill", "Project"} <= registry.node_types()


def test_frame_union_and_isolation():
    """새 팩(Frame)을 등록하면 그 관계가 추가로 허용되고, 등록 없는 유형은 거부."""
    before = dict(registry._FRAMES)
    try:
        registry.register_frame("test-pack", ["Customer", "Order"],
                                {"PLACED_BY": ("Order", "Customer")})
        assert registry.validate_edge("PLACED_BY", "Order", "Customer")
        assert not registry.validate_edge("PLACED_BY", "Person", "Customer"), "규약 밖 조합 거부"
        assert not registry.validate_edge("NO_SUCH_REL", "Order", "Customer"), "미등록 관계 거부"
        assert registry.validate_edge("RELATES_TO", "Order", "Person"), "자유 관계는 팩 간 허용"
    finally:
        registry._FRAMES.clear()
        registry._FRAMES.update(before)


def test_core_rejects_unknown_node_type(fresh_db):
    import pytest
    with pytest.raises(AssertionError):
        fresh_db.upsert_node("x:1", "UnknownType", {"name": "x"})


def test_facade_backcompat(fresh_db):
    """기존 경로(graph.store)로 코어 기능이 전부 동작한다 — G01 완료 기준."""
    fresh_db.upsert_node("person:코어", "Person", {"name": "코어"})
    fresh_db.upsert_node("skill:테스트", "Skill", {"name": "테스트"})
    fresh_db.upsert_edge("person:코어", "LEARNS", "skill:테스트")
    assert fresh_db.get_node("person:코어")["props"]["name"] == "코어"
    assert fresh_db.neighbors("person:코어", "LEARNS")[0][1]["type"] == "Skill"
    assert "Person" in fresh_db.counts()["nodes"]


def test_doctor_healthy_on_seeded_db(fresh_db):
    """G02: 그래프 닥터 — 샘플 볼트 시드 상태는 스키마 위반 0이어야 한다."""
    from graph_core import doctor
    r = doctor.check()
    assert r["healthy"], f"위반 발견: {r['unknown_type_nodes']} {r['invalid_edges']}"
    assert any(f["name"] == "personal-v2" and f["version"] == "2.1" for f in r["frames"])
