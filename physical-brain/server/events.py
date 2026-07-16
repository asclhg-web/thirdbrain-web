"""이벤트 기록기 — 모든 유의미한 사건은 이 함수 하나로 그래프에 남긴다."""
from datetime import datetime

from graph import store

KINDS = ["복약완료", "복약미확인", "복약누락", "알림발송", "임계초과", "결측감지",
         "브리핑", "주간리포트", "하루마감", "규칙실행", "로봇동작"]


def record_event(person: str, kind: str, payload: str = "", at: datetime | None = None) -> str:
    at = at or datetime.now()
    import hashlib
    sig = hashlib.sha1(payload.encode()).hexdigest()[:6]  # 동일 시각·종류의 서로 다른 이벤트 충돌 방지
    eid = f"event:{person}:{kind}:{at.isoformat()}:{sig}"
    store.upsert_node(eid, "Event", {"kind": kind, "at": at.isoformat(), "payload": payload})
    pid = store.person_id(person)
    if not store.get_node(pid):
        store.upsert_node(pid, "Person", {"name": person})
    store.upsert_edge(pid, "OCCURRED", eid)
    return eid


def adherence(person: str, days: int = 7, now: datetime | None = None) -> dict:
    """주간 복약 준수율 = 완료 / (완료+미확인+누락). 분모 0이면 None."""
    done = len(store.events(person, days, "복약완료", now))
    unconf = len(store.events(person, days, "복약미확인", now))
    missed = len(store.events(person, days, "복약누락", now))
    total = done + unconf + missed
    return {"done": done, "unconfirmed": unconf, "missed": missed,
            "rate": round(done / total * 100, 1) if total else None}
