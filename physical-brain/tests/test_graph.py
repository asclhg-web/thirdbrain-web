"""T02·T03·T04 검증: 스키마, 시드, 증분 동기화·아카이브."""
import os
import shutil


def test_seed_counts(fresh_db):
    c = fresh_db.counts()
    assert c["nodes"]["Person"] == 2
    assert c["nodes"]["Medication"] == 3
    assert c["nodes"]["Regimen"] == 3
    assert c["nodes"]["Place"] == 4
    assert c["edges"] == 6  # TAKES 3 + HAS_RULE 3


def test_schema_violation(fresh_db):
    import pytest
    fresh_db.upsert_node("place:테스트", "Place", {"name": "테스트"})
    with pytest.raises(ValueError):
        fresh_db.upsert_edge("person:나", "TAKES", "place:테스트")  # 사람이 장소를 복용 불가


def test_regimen_expansion(fresh_db):
    rs = fresh_db.regimens_for("아버지")
    assert len(rs) == 2  # 혈압약 + 전립선약
    assert rs[0]["time"] == "07:00" and "자몽" in rs[0]["caution"]


def test_incremental_sync_and_archive(fresh_db, tmp_path):
    """노트 수정→갱신 / 삭제→archived (물리 삭제 금지)."""
    from pipelines.vault_sync import sync_vault
    vault = tmp_path / "vault"
    src = os.path.join(os.path.dirname(__file__), "..", "graph", "sample_vault")
    shutil.copytree(src, vault)
    r1 = sync_vault(str(vault))
    assert r1["changed"] == 0  # 동일 내용 → 증분 0 (해시)
    # 수정: 복약 시간 변경
    p = vault / "혈압약.md"
    p.write_text(p.read_text(encoding="utf-8").replace("07:00", "07:30"), encoding="utf-8")
    r2 = sync_vault(str(vault))
    assert r2["changed"] == 1
    assert fresh_db.regimens_for("아버지")[0]["time"] == "07:30"
    # 삭제 → archived
    (vault / "전립선약.md").unlink()
    r3 = sync_vault(str(vault))
    assert r3["archived"] >= 1
    assert len(fresh_db.regimens_for("아버지")) == 1
