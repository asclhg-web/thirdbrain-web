"""G08 검증: 몸 마스터 — 볼트 노트 하나로 측정 유형·임계값·차트가 생긴다 (코드 수정 0)."""
from datetime import datetime

from graph.body_master import chart_types, measure_types
from pipelines.vault_sync import sync_note
from server.safety import check_measurement


def _measure_note(tmp_path):
    p = tmp_path / "측정_허리둘레.md"
    p.write_text("---\ntype: measure\nname: 허리둘레\nkey: waist\nunit: cm\nwarn: 90\n---\n",
                 encoding="utf-8")
    return str(p)


def test_vault_note_adds_measure_type(fresh_db, tmp_path):
    assert "waist" not in measure_types()
    assert measure_types()["weight"]["unit"] == "kg", "체중은 이제 기본 사전(H02)"
    sync_note(_measure_note(tmp_path))
    mt = measure_types()["waist"]
    assert mt["label"] == "허리둘레" and mt["unit"] == "cm" and mt["warn"] == 90.0
    assert ("waist", "허리둘레", "cm") in chart_types(), "신호 페이지 차트에 자동 등장"


def test_vault_threshold_drives_safety_net(fresh_db, tmp_path):
    """노트의 warn 값이 1층 안전망을 작동시킨다 — 코드 수정 없이."""
    sync_note(_measure_note(tmp_path))
    now = datetime(2026, 7, 20, 9)
    alert = check_measurement("나", "waist", 95, now)
    assert alert and alert["level"] == "warn" and "허리둘레" in alert["text"]
    assert check_measurement("나", "waist", 80, now) is None


def test_vault_can_override_default_threshold(fresh_db, tmp_path):
    """기본 유형(bp_sys)의 임계값도 볼트로 조정 가능 — 주치의와 정한 개인 기준선."""
    p = tmp_path / "측정_혈압조정.md"
    p.write_text("---\ntype: measure\nname: 수축기 혈압\nkey: bp_sys\nwarn: 130\n---\n",
                 encoding="utf-8")
    sync_note(str(p))
    assert measure_types()["bp_sys"]["warn"] == 130.0
    assert check_measurement("나", "bp_sys", 132, datetime(2026, 7, 20)) is not None
