# 로봇 어댑터 v1 (T25)

오케스트레이터는 로봇을 모른다. `move / manipulate / say` 세 동사만 안다.
그 동사를 실제 하드웨어로 번역하는 것이 어댑터다. 1차의 `RobotStub`,
지금의 `FakeRobot`, 2차의 LeKiwi 실물이 **같은 토픽 규약**을 구현한다.

## 구조

```
오케스트레이터 ──ROBOT.move()──▶ RobotAdapter ──publish──▶ [버스] ──▶ 로봇(실물/가상)
     ▲                              │   ◀──pb/report/result──┘
     └── 이벤트 기록(로봇동작/로봇응답없음) ◀┘
```

- 개발/테스트: `LocalBus` (같은 프로세스, 의존성 0)
- 실물 로봇: `MqttBus` (mosquitto 브로커 경유, `pip install paho-mqtt`)

## 토픽 규약 v1

| 토픽 | 방향 | 페이로드 | 의미 |
|---|---|---|---|
| `pb/cmd/move` | 앱→로봇 | `{id, place}` | 장소로 이동 |
| `pb/cmd/manipulate` | 앱→로봇 | `{id, skill}` | 스킬 실행(pick_pillbox, serve_tray…) |
| `pb/cmd/say` | 앱→로봇 | `{id, text}` | 스피커 발화 |
| `pb/report/result` | 로봇→앱 | `{id, ok, detail}` | 명령 결과 회신 |
| `pb/report/state` | 로봇→앱 | `{battery, pose, busy}` | 상태 방송 |
| `pb/report/event` | 로봇→앱 | `{kind, payload}` | 로봇발 이벤트(장애물 등) |

규칙:
- 모든 명령에 `id`(상관관계 키)가 있고, 로봇은 반드시 같은 `id`로 회신한다.
- 어댑터는 타임아웃(기본 30초) 내 회신이 없으면 `ok=False` 처리하고
  **로봇응답없음** 이벤트를 남긴다. 시나리오는 알림만으로 계속 진행된다
  — 로봇이 죽어도 돌봄은 멈추지 않는다(이중 안전망).
- 실패도 정직하게: `ok=False` + detail. 0으로 채우지 않는 원칙의 로봇판.

## 연결 방법

```python
# 가상 로봇 (지금 이 환경에서 검증 완료)
from robot.bus import LocalBus
from robot.fake_robot import FakeRobot
from robot.adapter import RobotAdapter
from server import orchestrator

bus = LocalBus(); FakeRobot(bus)
orchestrator.use_robot(RobotAdapter(bus))

# 실물 로봇 (GPU 서버/젯슨) — 브로커만 바꾸면 끝
from robot.bus import MqttBus
bus = MqttBus("로봇IP"); bus.start()
orchestrator.use_robot(RobotAdapter(bus, timeout_s=60))
```

로봇 쪽(LeKiwi/젯슨)에서는 `pb/cmd/#`를 구독해 LeRobot 정책 실행 후
`pb/report/result`를 발행하는 노드를 올린다 — `fake_robot.py`가 그 뼈대다.

## 검증 상태

- `tests/test_robot.py` 5종: 버스 와일드카드, 왕복 성공, 무응답 타임아웃,
  스킬 실패 주입, **시나리오 A 종단(알림→이동→서빙→'먹었어'→복약완료)** ✅
- 실시간 데모: `python3 -m robot.fake_robot` (move 3초 / manipulate 2초)
