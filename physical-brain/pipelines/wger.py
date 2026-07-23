"""H06 — Wger(오픈소스 운동 관리 서버) REST API 어댑터.

사용법(운동 습관이 생기면): RTX 서버에 Wger를 띄우고 .env 2줄이면 켜진다:
  WGER_URL=http://localhost:8820
  WGER_API_KEY=...   (Wger 화면: 설정 → API 키)

가져오는 것: 운동 세션(→ 활동 'workout', 1회 단위 — 주간 횟수가 관리도 재료),
체중 기록(→ weight 측정). 심장박동이 하루 1회 자동 동기화.
설정 없으면 조용히 잠들어 있다 — 고장이 아니다.
"""
import os
from datetime import datetime, timedelta

from graph import store

_OVERRIDE = None  # 테스트·모의용


def set_client(c) -> None:
    global _OVERRIDE
    _OVERRIDE = c


def configured() -> bool:
    return bool(os.environ.get("WGER_URL") and os.environ.get("WGER_API_KEY"))


class WgerClient:
    def __init__(self):
        self.url = os.environ.get("WGER_URL", "").rstrip("/")
        self.key = os.environ.get("WGER_API_KEY", "")

    def _get(self, path: str, params: dict) -> list[dict]:
        import httpx
        r = httpx.get(f"{self.url}/api/v2/{path}/",
                      params={**params, "limit": 200, "format": "json"},
                      headers={"Authorization": f"Token {self.key}"}, timeout=20)
        r.raise_for_status()
        return r.json().get("results", [])

    def sessions(self, since: str) -> list[dict]:
        return [s for s in self._get("workoutsession", {}) if s.get("date", "") >= since]

    def weights(self, since: str) -> list[dict]:
        return [w for w in self._get("weightentry", {}) if w.get("date", "") >= since]


def get_client():
    return _OVERRIDE if _OVERRIDE is not None else WgerClient()


def sync(person: str = "나", days: int = 30, client=None,
         now: datetime | None = None) -> dict:
    """Wger → 그래프 (멱등). 세션=활동 1회, 체중=측정."""
    now = now or datetime.now()
    client = client or get_client()
    since = (now - timedelta(days=days)).date().isoformat()
    pid = store.person_id(person)
    if not store.get_node(pid):
        store.upsert_node(pid, "Person", {"name": person})

    n_w = 0
    for s in client.sessions(since):
        d = s.get("date", "")
        if not d:
            continue
        aid = f"activity:{person}:workout:{d}T18:00:00"
        store.upsert_node(aid, "Activity", {
            "kind": "workout", "value": 1.0, "unit": "회", "at": f"{d}T18:00:00",
            "note": str(s.get("notes") or ""), "src": "wger"})
        store.upsert_edge(pid, "PERFORMED", aid)
        n_w += 1
    n_kg = 0
    for w in client.weights(since):
        d, v = w.get("date", ""), w.get("weight")
        try:
            v = float(v)
        except (TypeError, ValueError):
            continue
        if not d or not (20 <= v <= 300):
            continue
        mid = f"measurement:{person}:weight:{d}T07:00:00"
        store.upsert_node(mid, "Measurement", {
            "type": "weight", "value": round(v, 1), "unit": "kg",
            "measured_at": f"{d}T07:00:00", "src": "wger"})
        store.upsert_edge(pid, "MEASURED", mid)
        n_kg += 1
    return {"workouts": n_w, "weights": n_kg}


def auto_sync_if_due(now: datetime | None = None) -> dict | None:
    """심장박동용 — 하루 1회. 미설정이면 조용히 None."""
    now = now or datetime.now()
    if not configured() and _OVERRIDE is None:
        return None
    today = now.date().isoformat()
    done = any(e["props"].get("kind") == "운동동기화"
               and e["props"].get("at", "").startswith(today)
               for e in store.nodes_by_type("Event"))
    if done:
        return None
    r = sync(now=now)
    from server.events import record_event
    record_event("나", "운동동기화", f"세션 {r['workouts']} 체중 {r['weights']}", now)
    return r
