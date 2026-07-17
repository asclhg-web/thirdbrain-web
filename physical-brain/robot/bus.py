"""T25 — 메시지 버스. 로봇 어댑터와 로봇(실물/가상)이 대화하는 통로.

토픽 규약(robot-adapter-v1):
  pb/cmd/move        {id, place}
  pb/cmd/manipulate  {id, skill}
  pb/cmd/say         {id, text}
  pb/report/result   {id, ok, detail}
  pb/report/state    {battery, pose, busy}
  pb/report/event    {kind, payload}

LocalBus  — 같은 프로세스 안 pub/sub (테스트·가상로봇용, 의존성 0)
MqttBus   — 실제 로봇용. paho-mqtt 설치 시 동일 API (publish/subscribe)
"""
import fnmatch
import json
import threading


class LocalBus:
    """프로세스 내 pub/sub. 토픽 와일드카드는 MQTT 규약(#, +)을 지원한다."""

    def __init__(self):
        self._subs: list[tuple[str, callable]] = []
        self._lock = threading.Lock()

    @staticmethod
    def _match(pattern: str, topic: str) -> bool:
        # MQTT 와일드카드 → fnmatch: '#'는 이하 전부, '+'는 한 레벨
        pat = pattern.replace("#", "*")
        if "+" in pat:
            pp, tp = pat.split("/"), topic.split("/")
            if len(pp) != len(tp):
                return False
            return all(a == "+" or fnmatch.fnmatch(b, a) for a, b in zip(pp, tp))
        return fnmatch.fnmatch(topic, pat)

    def subscribe(self, pattern: str, handler):
        with self._lock:
            self._subs.append((pattern, handler))

    def publish(self, topic: str, payload: dict):
        with self._lock:
            targets = [h for p, h in self._subs if self._match(p, topic)]
        for h in targets:
            h(topic, payload)


class MqttBus:
    """실물 로봇용 — 브로커(mosquitto 등) 경유. paho-mqtt 필요.

    사용: bus = MqttBus("192.168.x.x"); bus.start()
    """

    def __init__(self, host: str = "localhost", port: int = 1883):
        import paho.mqtt.client as mqtt  # 선택 의존성
        self._c = mqtt.Client()
        self._handlers: list[tuple[str, callable]] = []
        self._c.on_message = self._on_message
        self._host, self._port = host, port

    def start(self):
        self._c.connect(self._host, self._port)
        self._c.loop_start()

    def _on_message(self, client, userdata, msg):
        payload = json.loads(msg.payload.decode("utf-8"))
        for pattern, h in self._handlers:
            if LocalBus._match(pattern, msg.topic):
                h(msg.topic, payload)

    def subscribe(self, pattern: str, handler):
        self._handlers.append((pattern, handler))
        self._c.subscribe(pattern)

    def publish(self, topic: str, payload: dict):
        self._c.publish(topic, json.dumps(payload, ensure_ascii=False))
