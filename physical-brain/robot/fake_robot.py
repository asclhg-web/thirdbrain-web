"""T25 — 가상 로봇. 실물 로봇이 오기 전, 어댑터·시나리오를 끝까지 검증하는 대역.

pb/cmd/# 을 구독해 move는 ~3초, manipulate는 ~2초 걸려 수행한 뒤
pb/report/result 로 회신한다. speed 인자로 가속(테스트: speed=0.01).

단독 실행(수동 관찰용): python3 -m robot.fake_robot
"""
import threading
import time

MOVE_S, MANIP_S, SAY_S = 3.0, 2.0, 0.5


class FakeRobot:
    def __init__(self, bus, speed: float = 1.0, fail_skills: set[str] | None = None):
        self.bus = bus
        self.speed = speed
        self.fail_skills = fail_skills or set()  # 고장 시나리오 주입용
        self.pose = "충전독"
        self.busy = False
        self.history: list[dict] = []
        bus.subscribe("pb/cmd/#", self._on_cmd)

    def _work(self, topic: str, p: dict):
        kind = topic.rsplit("/", 1)[-1]
        self.busy = True
        if kind == "move":
            time.sleep(MOVE_S * self.speed)
            self.pose = p["place"]
            ok, detail = True, f"도착: {p['place']}"
        elif kind == "manipulate":
            time.sleep(MANIP_S * self.speed)
            ok = p["skill"] not in self.fail_skills
            detail = f"수행: {p['skill']}" if ok else f"실패: {p['skill']} (그리퍼 오류)"
        else:  # say
            time.sleep(SAY_S * self.speed)
            ok, detail = True, f"발화: {p.get('text', '')}"
        self.busy = False
        self.history.append({"kind": kind, **p, "ok": ok})
        self.bus.publish("pb/report/result", {"id": p["id"], "ok": ok, "detail": detail})
        self.bus.publish("pb/report/state", {"battery": 87, "pose": self.pose, "busy": False})

    def _on_cmd(self, topic, payload):
        threading.Thread(target=self._work, args=(topic, payload), daemon=True).start()


if __name__ == "__main__":
    from datetime import datetime
    from robot.bus import LocalBus
    from robot.adapter import RobotAdapter

    bus = LocalBus()
    FakeRobot(bus)
    ad = RobotAdapter(bus, timeout_s=10)
    print("가상 로봇 데모 — 아침 시나리오의 로봇 파트")
    for step in [("move", "부엌 약 선반"), ("manipulate", "pick_pillbox"),
                 ("move", "거실"), ("manipulate", "serve_tray")]:
        t0 = time.time()
        r = ad.move(step[1], datetime.now()) if step[0] == "move" else ad.manipulate(step[1], datetime.now())
        print(f"  {step[0]}({step[1]}) → {r} ({time.time()-t0:.1f}s)")
