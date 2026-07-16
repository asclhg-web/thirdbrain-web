"""알림 발송기 — 텔레그램(.env 토큰) 또는 dry-run(data/outbox.log).

보호자 라우팅: 아버지의 복약 확인/미확인은 보호자 채널로도 전달.
"""
import os
from datetime import datetime

import httpx

from server.events import record_event

OUTBOX = os.path.join(os.path.dirname(__file__), "..", "data", "outbox.log")


def send(person: str, text: str, kind: str = "alert", now: datetime | None = None) -> dict:
    now = now or datetime.now()
    token = os.environ.get("TELEGRAM_TOKEN", "")
    chat = os.environ.get(f"TELEGRAM_CHAT_{person}", "")
    mode = "telegram" if (token and chat) else "dry-run"
    if mode == "telegram":
        try:
            httpx.post(f"https://api.telegram.org/bot{token}/sendMessage",
                       json={"chat_id": chat, "text": text}, timeout=10)
        except Exception:
            mode = "dry-run(전송실패)"
    if mode != "telegram":
        os.makedirs(os.path.dirname(OUTBOX), exist_ok=True)
        with open(OUTBOX, "a", encoding="utf-8") as f:
            f.write(f"[{now.isoformat()}] → {person} ({kind}): {text}\n")
    record_event(person, "알림발송", f"{kind}: {text[:80]}", now)
    return {"mode": mode, "person": person, "kind": kind}


def notify_guardian(about_person: str, text: str, now: datetime | None = None):
    """보호자 알림 — '전화할 거리를 만든다'."""
    return send("보호자", f"[{about_person}] {text}", kind="guardian", now=now)
