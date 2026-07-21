"""G12 검증: 에이전트 빌더 — 초안 자동 생성→승인→YAML 활성화→오케스트레이터 발화."""
from datetime import datetime

from graph_core import approvals
from pipelines.vault_sync import sync_note
from server import agent_builder, orchestrator


def _add_weight_measure(tmp_path):
    p = tmp_path / "측정_몸무게.md"
    p.write_text("---\ntype: measure\nname: 몸무게\nkey: weight\nunit: kg\nwarn: 90\n---\n",
                 encoding="utf-8")
    sync_note(str(p))


def test_drafts_only_for_uncovered_measures(fresh_db, tmp_path):
    """혈당 스파이크는 기존 규칙(시나리오 B)이 있어 초안 대상이 아니고, 새 유형만 초안."""
    _add_weight_measure(tmp_path)
    drafts = agent_builder.suggest_rules()
    keys = {d["key"] for d in drafts}
    assert "weight" in keys
    assert "glucose_spikes" not in keys, "이미 규칙이 있는 측정은 제외"


def test_draft_to_live_rule_full_loop(fresh_db, tmp_path, monkeypatch):
    """초안→승인→YAML 생성→run_tick에서 실제 발화 — 에이전트 탄생의 전 과정."""
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    monkeypatch.setattr(orchestrator, "RULES_DIR", str(rules_dir))
    orchestrator._COOLDOWN.clear()
    _add_weight_measure(tmp_path)

    draft = next(d for d in agent_builder.suggest_rules() if d["key"] == "weight")
    now = datetime(2026, 7, 20, 9, 0)
    aid = agent_builder.propose_rule(draft, now)
    assert not list(rules_dir.glob("*.yaml")), "승인 전 규칙 파일 0개 (HITL)"

    approvals.decide(aid, approve=True, now=now)
    assert (rules_dir / "auto_weight.yaml").exists(), "승인 후 규칙 활성화"

    fresh_db.upsert_node(f"measurement:나:weight:{now.isoformat()}", "Measurement",
                         {"type": "weight", "value": 95.0, "unit": "kg",
                          "measured_at": now.isoformat()})
    fresh_db.upsert_edge("person:나", "MEASURED", f"measurement:나:weight:{now.isoformat()}")
    fired = orchestrator.run_tick(now.replace(minute=5))
    assert "몸무게 주의 알림 (자동 초안)" in fired, "새 에이전트가 실제로 발화"
    sent = fresh_db.events("나", 1, "알림발송", now.replace(hour=23))
    assert any("몸무게" in e["payload"] for e in sent)
