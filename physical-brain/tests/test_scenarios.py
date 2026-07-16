"""T14·T15 검증: 가상 시계로 하루를 초 단위 가속 — 시나리오 A·B·C 전 상태 전이."""
from datetime import datetime, timedelta


def simulate_day(day: datetime, step_min: int = 5, confirm_at: str | None = "07:10"):
    """가상 하루: step_min 간격으로 오케스트레이터 틱. confirm_at 시각에 '먹었어'."""
    from server.orchestrator import run_tick
    from server.tasks_today import confirm
    fired = []
    t = day.replace(hour=6, minute=0)
    end = day.replace(hour=23, minute=0)
    while t <= end:
        fired += run_tick(t)
        if confirm_at and t.strftime("%H:%M") == confirm_at:
            confirm("아버지", t)
            confirm("나", t)
        t += timedelta(minutes=step_min)
    return fired


def test_scenario_a_confirmed(fresh_db):
    """아침: 07:00 브리핑·서빙 → 07:10 '먹었어' → 복약완료 이벤트."""
    day = datetime(2026, 7, 15)
    from pipelines.mock_health import generate
    generate(days=7, end=day.replace(hour=6), seed=3)
    fired = simulate_day(day)
    assert "아침 브리핑" in fired
    done = fresh_db.events("아버지", 1, "복약완료", day.replace(hour=23))
    assert done, "확인 응답이 복약완료로 기록되어야 한다"
    robots = fresh_db.events("나", 1, "로봇동작", day.replace(hour=23))
    assert any("serve_tray" in e["payload"] for e in robots)


def test_scenario_a_unconfirmed_honest(fresh_db):
    """무응답: 20분 재알림 → 미확인으로 정직하게 기록 + 보호자 알림."""
    day = datetime(2026, 7, 16)
    simulate_day(day, confirm_at=None)
    unconf = fresh_db.events("아버지", 1, "복약미확인", day.replace(hour=23))
    assert unconf, "무응답은 unconfirmed 이벤트로 남아야 한다"
    guardian = fresh_db.events("보호자", 1, "알림발송", day.replace(hour=23))
    assert any("미확인" in e["payload"] for e in guardian)


def test_scenario_b_nudge_once(fresh_db):
    """혈당 급등 → 산책 권유는 쿨다운 내 1회만."""
    from server.orchestrator import run_tick, _COOLDOWN
    _COOLDOWN.clear()
    day = datetime(2026, 7, 17)
    fresh_db.upsert_node(f"measurement:나:glucose_spikes:{day.replace(hour=13).isoformat()}",
                         "Measurement", {"type": "glucose_spikes", "value": 3, "unit": "회",
                                         "measured_at": day.replace(hour=13).isoformat()})
    fresh_db.upsert_edge("person:나", "MEASURED", f"measurement:나:glucose_spikes:{day.replace(hour=13).isoformat()}")
    fired1 = run_tick(day.replace(hour=13, minute=5))
    fired2 = run_tick(day.replace(hour=13, minute=10))  # 쿨다운 내 재발화 금지
    assert fired1.count("혈당 스파이크 대응") == 1
    assert fired2.count("혈당 스파이크 대응") == 0


def test_scenario_c_evening(fresh_db):
    """저녁 21:30: 내일 트레이 준비 + 하루마감."""
    from server.orchestrator import run_tick, ROBOT
    ROBOT.log.clear()
    day = datetime(2026, 7, 18)
    run_tick(day.replace(hour=21, minute=30))
    assert any(a.get("skill") == "prepare_tomorrow_tray" for a in ROBOT.log)
    assert fresh_db.events("아버지", 1, "하루마감", day.replace(hour=23))
