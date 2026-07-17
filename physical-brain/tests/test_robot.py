"""T25 검증: 버스 → 어댑터 → 가상 로봇 왕복 + 시나리오 A 로봇 연동 종단 검증."""
from datetime import datetime, timedelta

from robot.adapter import RobotAdapter
from robot.bus import LocalBus
from robot.fake_robot import FakeRobot


def test_bus_wildcards():
    bus = LocalBus()
    got = []
    bus.subscribe("pb/cmd/#", lambda t, p: got.append(t))
    bus.subscribe("pb/+/result", lambda t, p: got.append("R:" + t))
    bus.publish("pb/cmd/move", {})
    bus.publish("pb/report/result", {})
    assert got == ["pb/cmd/move", "R:pb/report/result"]


def test_adapter_roundtrip(fresh_db):
    """move/manipulate가 결과를 회신받고 로봇동작 이벤트로 남는다."""
    bus = LocalBus()
    robot = FakeRobot(bus, speed=0.01)
    ad = RobotAdapter(bus, timeout_s=5)
    now = datetime(2026, 7, 20, 7, 0)
    assert ad.move("부엌 약 선반", now)["ok"]
    assert ad.manipulate("serve_tray", now)["ok"]
    assert robot.pose == "부엌 약 선반"
    ev = fresh_db.events("나", 1, "로봇동작", now + timedelta(hours=1))
    assert {"move:부엌 약 선반", "manipulate:serve_tray"} <= {e["payload"] for e in ev}


def test_adapter_timeout_is_honest(fresh_db):
    """로봇 무응답 → ok=False + 로봇응답없음 이벤트('미확인은 미확인으로')."""
    bus = LocalBus()  # 로봇 없음
    ad = RobotAdapter(bus, timeout_s=0.05)
    now = datetime(2026, 7, 20, 7, 0)
    assert ad.move("거실", now)["ok"] is False
    ev = fresh_db.events("나", 1, "로봇응답없음", now + timedelta(hours=1))
    assert any("move:거실" in e["payload"] for e in ev)


def test_adapter_failure_reported(fresh_db):
    """스킬 실패(그리퍼 오류 주입) → ok=False 로 정직하게 보고."""
    bus = LocalBus()
    FakeRobot(bus, speed=0.01, fail_skills={"pick_pillbox"})
    ad = RobotAdapter(bus, timeout_s=5)
    now = datetime(2026, 7, 20, 7, 0)
    r = ad.manipulate("pick_pillbox", now)
    assert r["ok"] is False and "그리퍼" in r["detail"]


def test_scenario_a_with_fake_robot(fresh_db):
    """시나리오 A 종단: 07:00 알림 → 어댑터 경유 이동·서빙 → '먹었어' → 복약완료.
    RobotStub 대신 실제 명령 왕복(가상 로봇)으로 하루를 완주한다."""
    from server import orchestrator
    from server.tasks_today import confirm

    bus = LocalBus()
    robot = FakeRobot(bus, speed=0.01)
    ad = RobotAdapter(bus, timeout_s=5)
    orchestrator.use_robot(ad)
    try:
        day = datetime(2026, 7, 21)
        t = day.replace(hour=6, minute=0)
        while t <= day.replace(hour=10, minute=0):
            orchestrator.run_tick(t)
            if t.strftime("%H:%M") == "07:10":
                confirm("아버지", t)
                confirm("나", t)
            t += timedelta(minutes=5)
    finally:
        orchestrator.use_robot(orchestrator.RobotStub)

    kinds = [(h["kind"], h.get("place") or h.get("skill")) for h in robot.history]
    assert ("move", "부엌 약 선반") in kinds, "로봇이 실제로 이동 명령을 수행해야 한다"
    assert ("manipulate", "serve_tray") in kinds, "로봇이 실제로 서빙을 수행해야 한다"
    done = fresh_db.events("아버지", 1, "복약완료", day.replace(hour=23))
    assert done, "로봇 연동 하에서도 복약 확인 루프가 닫혀야 한다"
    assert all(e["ok"] for e in ad.log), "가상 로봇 정상 상태에서는 전 명령 성공이어야 한다"
