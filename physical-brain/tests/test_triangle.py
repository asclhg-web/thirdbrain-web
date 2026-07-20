"""온톨로지 v2 검증: Skill·Project·CONTRIBUTES_TO — 삼각(몸×학습×프로젝트) 모델."""
from datetime import datetime

from graph.schema import validate_edge
from pipelines.vault_sync import sync_note


def _write(tmp_path, fn, text):
    p = tmp_path / fn
    p.write_text(text, encoding="utf-8")
    return str(p)


def test_schema_v2_rules():
    assert validate_edge("LEARNS", "Person", "Skill")
    assert validate_edge("WORKS_ON", "Person", "Project")
    assert validate_edge("CONTRIBUTES_TO", "Activity", "Skill")
    assert validate_edge("CONTRIBUTES_TO", "Activity", "Project")
    assert not validate_edge("CONTRIBUTES_TO", "Person", "Skill"), "사람이 아니라 활동이 기여한다"


def test_triangle_notes_sync(fresh_db, tmp_path):
    """스킬·프로젝트·활동 노트 → LEARNS/WORKS_ON/CONTRIBUTES_TO 엣지."""
    sync_note(_write(tmp_path, "학습_라인댄스스텝.md",
                     '---\ntype: skill\nname: 라인댄스 스텝\nfor: "[[아내]]"\n---\n'))
    sync_note(_write(tmp_path, "프로젝트_발표회.md",
                     '---\ntype: project\nname: 라인댄스 발표회\nfor: "[[아내]]"\nstatus: active\n---\n'))
    sync_note(_write(tmp_path, "활동_연습.md",
                     '---\ntype: activity\nname: 라인댄스 연습\nfor: "[[아내]]"\n'
                     'date: 2026-07-19\nkind: 운동\nbody: 운동 90분\n'
                     'skills: "[[라인댄스 스텝]]"\nprojects: "[[라인댄스 발표회]]"\n---\n'))
    pid = fresh_db.person_id("아내")
    assert any(n["type"] == "Skill" for _r, n in fresh_db.neighbors(pid, "LEARNS"))
    assert any(n["type"] == "Project" for _r, n in fresh_db.neighbors(pid, "WORKS_ON"))
    act = fresh_db.get_node("activity:라인댄스_연습")
    assert act and act["props"]["at"] == "2026-07-19"
    targets = {n["type"] for _r, n in fresh_db.neighbors("activity:라인댄스_연습", "CONTRIBUTES_TO")}
    assert targets == {"Skill", "Project"}, "일석삼조: 한 활동이 학습·프로젝트에 동시 기여"


def test_triangle_week_summary(fresh_db, tmp_path):
    """홈 위젯 집계: 몸+학습+프로젝트 3영역 기여 + 교차기여율 100%."""
    sync_note(_write(tmp_path, "활동_연습.md",
                     '---\ntype: activity\nname: 라인댄스 연습\nfor: "[[아내]]"\n'
                     'date: 2026-07-19\nkind: 운동\n'
                     'skills: "[[스텝]]"\nprojects: "[[발표회]]"\n---\n'))
    tri = fresh_db.triangle_week("아내", datetime(2026, 7, 20))
    assert tri["total"] == 1
    assert tri["몸"] == 1 and tri["학습"] == 1 and tri["프로젝트"] == 1
    assert tri["cross_rate"] == 100
