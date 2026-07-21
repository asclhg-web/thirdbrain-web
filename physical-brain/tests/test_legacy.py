"""G-Legacy 검증: 유산 패키지 생성·상속 리허설 — 언제 멈춰도 선물이 되도록."""
from datetime import datetime

from graph_core import legacy


def _make_vault(tmp_path):
    v = tmp_path / "vault"
    v.mkdir()
    (v / "나.md").write_text("---\ntype: person\nname: 나\n---\n마음의 기록.", encoding="utf-8")
    (v / "마음_기록.md").write_text("오늘도 딸을 생각하며.", encoding="utf-8")
    return str(v)


def test_build_and_rehearse(fresh_db, tmp_path):
    """패키지 생성 → 안내문·manifest·DB·볼트 포함 → 리허설 검증 통과."""
    fresh_db.upsert_node("person:나", "Person", {"name": "나"})
    out = legacy.build_package(_make_vault(tmp_path), datetime(2026, 7, 20, 22))
    assert out.endswith(".zip")

    check = legacy.verify_package(out)
    assert check["healthy"], f"리허설 실패: {check['issues']}"
    assert check["vault_files"] == 2, "마음의 기록(마크다운)이 꾸러미에 들어간다"
    assert check["profiles"] and check["profiles"][0]["nodes"] > 0

    import zipfile
    with zipfile.ZipFile(out) as z:
        readme = z.read("README_받는이에게.md").decode("utf-8")
    assert "당신의 선택" in readme and "지어낸 것이 없습니다" in readme, "헌장 원칙이 안내문에"


def test_verify_detects_corruption(fresh_db, tmp_path):
    """망가진 패키지는 리허설이 정직하게 잡아낸다 — 검증 없는 백업은 유산이 아니다."""
    out = legacy.build_package(_make_vault(tmp_path), datetime(2026, 7, 20, 22))
    import zipfile
    broken = str(tmp_path / "broken.zip")
    with zipfile.ZipFile(out) as src, zipfile.ZipFile(broken, "w") as dst:
        for m in src.namelist():
            if m != "manifest.json":
                dst.writestr(m, src.read(m))
    check = legacy.verify_package(broken)
    assert not check["healthy"] and any("manifest" in i for i in check["issues"])


def test_auto_build_weekly_only(fresh_db, tmp_path):
    """자동 생성은 주 1회 — 방금 만들었으면 다시 만들지 않는다."""
    v = _make_vault(tmp_path)
    first = legacy.auto_build_if_due(7, v)
    assert first, "패키지가 없으면 생성"
    assert legacy.auto_build_if_due(7, v) is None, "7일 안 지났으면 생략"
