"""오케스트레이터 — "[조건]이 되면 [확인]하고 [행동]을 발행한다" (YAML 규칙).

행동 3종: say(→notify), move/manipulate(1차: 시뮬레이션 스텁 — 2차 로봇 어댑터가
동일 인터페이스 구현), record(이벤트). 모든 실행은 이벤트로 남는다.
가상 시계(now 인자) 지원 → 테스트에서 하루를 초 단위로 가속 가능.
"""
import os
from datetime import datetime

import yaml

from graph import store
from server import briefing, notify, report, safety
from server.events import record_event
from server.tasks_today import expand_today, tick as tasks_tick

RULES_DIR = os.path.join(os.path.dirname(__file__), "rules")
_COOLDOWN: dict[str, str] = {}  # rule_name → last fired date/hour key


class RobotStub:
    """2차에서 /robot/adapter.py 가 이 인터페이스를 그대로 구현한다."""
    log: list[dict] = []

    @classmethod
    def move(cls, place: str, now: datetime):
        cls.log.append({"cmd": "move", "place": place, "at": now.isoformat()})
        record_event("나", "로봇동작", f"move→{place}", now)
        return {"ok": True}

    @classmethod
    def manipulate(cls, skill: str, now: datetime):
        cls.log.append({"cmd": "manipulate", "skill": skill, "at": now.isoformat()})
        record_event("나", "로봇동작", f"manipulate:{skill}", now)
        return {"ok": True}


ROBOT = RobotStub


def load_rules() -> list[dict]:
    rules = []
    for fn in sorted(os.listdir(RULES_DIR)):
        if fn.endswith(".yaml"):
            with open(os.path.join(RULES_DIR, fn), encoding="utf-8") as f:
                r = yaml.safe_load(f)
                if r and r.get("enabled", True):
                    rules.append(r)
    return rules


def _time_match(rule, now: datetime) -> bool:
    at = rule["trigger"].get("at", "")
    key = f"{rule['name']}:{now.date()}:{at}"
    if now.strftime("%H:%M") == at and _COOLDOWN.get(rule["name"]) != key:
        _COOLDOWN[rule["name"]] = key
        return True
    return False


def _measurement_match(rule, now: datetime) -> dict | None:
    t = rule["trigger"]
    person, mtype = t.get("person", "나"), t["measurement"]
    vals = store.measurements(person, mtype, 1, now)
    if not vals:
        return None
    latest = vals[-1]
    # 스파이크 '직후' 대응 원칙: 최근 2시간 내 측정값에만 반응
    from datetime import timedelta
    if datetime.fromisoformat(latest["measured_at"]) < now - timedelta(hours=2):
        return None
    v = latest["value"]
    if v >= t.get("gte", float("inf")):
        cd_h = rule.get("cooldown_hours", 0)
        key = f"{rule['name']}:{now.date()}:{now.hour // max(cd_h, 1) if cd_h else now.isoformat()}"
        if _COOLDOWN.get(rule["name"]) == key:
            return None
        _COOLDOWN[rule["name"]] = key
        return {"value": v, "person": person}
    return None


def _run_actions(rule, ctx: dict, now: datetime, fired: list):
    for act in rule.get("actions", []):
        typ = act["type"]
        person = act.get("person", ctx.get("person", "나"))
        if typ == "briefing":
            notify.send(person, briefing.morning_briefing(person, now), "briefing", now)
        elif typ == "say":
            notify.send(person, act["text"].format(**ctx), act.get("kind", "reminder"), now)
        elif typ == "move":
            ROBOT.move(act["place"], now)
        elif typ == "manipulate":
            ROBOT.manipulate(act["skill"], now)
        elif typ == "tasks_tick":
            for a in tasks_tick(now):
                t = a["task"]
                if a["type"] == "announce":
                    notify.send(t["person"], f"💊 {t['med']} 드실 시간이에요 ({t['time']}"
                                + (f", {t['condition']}" if t["condition"] else "") + ")."
                                + (f" ⚠{t['caution']}" if t["caution"] else ""), "reminder", now)
                    ROBOT.manipulate("serve_tray", now)
                elif a["type"] == "remind":
                    notify.send(t["person"], f"🔁 {t['med']} 확인 부탁드려요. 드셨으면 '먹었어'라고 답해주세요.",
                                "reminder", now)
                elif a["type"] == "unconfirmed":
                    notify.notify_guardian(t["person"], f"{t['med']} 복약 미확인 ({t['time']})", now)
        elif typ == "weekly_report":
            notify.send(person, report.weekly_report(person, now), "report", now)
            if person == "아버지":
                notify.send("보호자", report.guardian_version(person, now), "report", now)
        elif typ == "record":
            record_event(person, act["kind"], act.get("payload", ""), now)
    record_event("나", "규칙실행", rule["name"], now)
    fired.append(rule["name"])


def run_tick(now: datetime | None = None) -> list[str]:
    """분 단위 심장박동 — 스케줄러(또는 가상 시계)가 호출."""
    now = now or datetime.now()
    fired: list[str] = []
    expand_today(now)
    for rule in load_rules():
        tt = rule["trigger"]["type"]
        if tt == "time" and _time_match(rule, now):
            _run_actions(rule, {"person": rule["trigger"].get("person", "나")}, now, fired)
        elif tt == "measurement":
            ctx = _measurement_match(rule, now)
            if ctx:
                _run_actions(rule, ctx, now, fired)
        elif tt == "always":  # 태스크 틱 전용
            _run_actions(rule, {}, now, fired) if rule.get("silent") else None
    # 태스크 상태 전이는 규칙과 무관하게 항상 돈다
    for a in tasks_tick(now):
        t = a["task"]
        if a["type"] == "announce":
            notify.send(t["person"], f"💊 {t['med']} 드실 시간이에요 ({t['time']}"
                        + (f", {t['condition']}" if t["condition"] else "") + ")."
                        + (f" ⚠{t['caution']}" if t["caution"] else ""), "reminder", now)
            ROBOT.move("부엌 약 선반", now)
            ROBOT.manipulate("serve_tray", now)
        elif a["type"] == "remind":
            notify.send(t["person"], f"🔁 {t['med']} 확인 부탁드려요. 드셨으면 '먹었어'라고 답해주세요.", "reminder", now)
        elif a["type"] == "unconfirmed":
            notify.notify_guardian(t["person"], f"{t['med']} 복약 미확인 ({t['time']})", now)
    return fired
