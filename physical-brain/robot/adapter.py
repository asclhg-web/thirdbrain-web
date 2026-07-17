"""T25 — 로봇 어댑터. 오케스트레이터의 RobotStub과 동일 인터페이스(move/manipulate).

명령을 버스에 발행하고 pb/report/result 를 기다린다(동기, 타임아웃).
- 성공: 로봇동작 이벤트 기록
- 타임아웃/실패: 로봇응답없음 이벤트 기록 → 시나리오는 알림만으로 계속 진행
  (로봇이 죽어도 돌봄은 멈추지 않는다 — 이중 안전망 원칙)

교체 방법: orchestrator.use_robot(RobotAdapter(bus))
"""
import threading
import uuid
from datetime import datetime

from server.events import record_event


class RobotAdapter:
    def __init__(self, bus, timeout_s: float = 30.0, person: str = "나"):
        self.bus = bus
        self.timeout_s = timeout_s
        self.person = person
        self.log: list[dict] = []
        self._waiting: dict[str, dict] = {}  # cmd id → {event, result}
        bus.subscribe("pb/report/result", self._on_result)
        bus.subscribe("pb/report/event", self._on_event)

    # ── 수신 ──
    def _on_result(self, topic, payload):
        w = self._waiting.get(payload.get("id", ""))
        if w:
            w["result"] = payload
            w["event"].set()

    def _on_event(self, topic, payload):
        record_event(self.person, payload.get("kind", "로봇이벤트"),
                     payload.get("payload", ""), datetime.now())

    # ── 발행(동기 대기) ──
    def _command(self, kind: str, body: dict, label: str, now: datetime) -> dict:
        cid = uuid.uuid4().hex[:8]
        w = {"event": threading.Event(), "result": None}
        self._waiting[cid] = w
        self.bus.publish(f"pb/cmd/{kind}", {"id": cid, **body})
        ok = w["event"].wait(self.timeout_s) and (w["result"] or {}).get("ok", False)
        self._waiting.pop(cid, None)
        entry = {"cmd": kind, **body, "ok": ok, "at": now.isoformat()}
        self.log.append(entry)
        if ok:
            record_event(self.person, "로봇동작", f"{kind}:{label}", now)
        else:
            record_event(self.person, "로봇응답없음", f"{kind}:{label}", now)
        return {"ok": ok, "detail": (w["result"] or {}).get("detail", "")}

    # ── RobotStub 인터페이스 ──
    def move(self, place: str, now: datetime) -> dict:
        return self._command("move", {"place": place}, place, now)

    def manipulate(self, skill: str, now: datetime) -> dict:
        return self._command("manipulate", {"skill": skill}, skill, now)

    def say(self, text: str, now: datetime) -> dict:
        return self._command("say", {"text": text}, text[:20], now)
