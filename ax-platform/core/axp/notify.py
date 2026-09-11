"""실패 알림 실연동 (P2-A3) — 경보를 사람에게 보낸다.

채널은 환경변수로 선택하며, 모든 외부 발신은 반출 게이트의 허용 호스트
목록(EXPORT_ALLOWED_HOSTS)을 통과해야 한다 — 알림조차 게이트 밖으로는
나가지 않는다. 설정이 없으면 dry-run(파일 기록)으로 동작해 파이프라인을
막지 않는다.

  AXP_NOTIFY            채널 목록: telegram,webhook,console (기본: dryrun)
  AXP_NOTIFY_MIN_LEVEL  발신 최소 등급 info|warn|crit (기본 warn)
  TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID
  AXP_WEBHOOK_URL       JSON POST 웹훅(카카오워크·슬랙 호환형)
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from . import config

_LEVELS = {"info": 0, "warn": 1, "crit": 2}


def _min_level() -> int:
    return _LEVELS.get(os.environ.get("AXP_NOTIFY_MIN_LEVEL", "warn"), 1)


def _channels() -> list[str]:
    raw = os.environ.get("AXP_NOTIFY", "").strip()
    return [c.strip() for c in raw.split(",") if c.strip()] or ["dryrun"]


def _host_allowed(url: str) -> bool:
    host = urllib.parse.urlparse(url).hostname or ""
    allowed = set(config.EXPORT_ALLOWED_HOSTS)
    # 텔레그램 공식 API는 명시 등록을 요구하되 오해를 줄이기 위해 이름을 밝힌다
    return host in allowed


def _post_json(url: str, payload: dict, timeout: int = 10) -> None:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=timeout).read()


def _dryrun_log(text: str) -> None:
    config.ensure_dirs()
    path = config.ARTIFACTS / "notify.log"
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{stamp} {text}\n")


def send(level: str, module: str, message: str) -> dict:
    """경보 발신. 반환: 채널별 결과(테스트·감사용)."""
    results: dict[str, str] = {}
    if _LEVELS.get(level, 0) < _min_level():
        return {"skipped": f"level {level} < min"}
    text = f"[AX/{level}] {module}: {message}"
    for ch in _channels():
        try:
            if ch == "console":
                print(text)
                results[ch] = "ok"
            elif ch == "dryrun":
                _dryrun_log(text)
                results[ch] = "ok(dryrun)"
            elif ch == "telegram":
                token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
                chat = os.environ.get("TELEGRAM_CHAT_ID", "")
                if not token or not chat:
                    _dryrun_log("(telegram 미설정) " + text)
                    results[ch] = "dryrun(no-config)"
                    continue
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                if not _host_allowed(url):
                    _dryrun_log("(반출 게이트 차단: api.telegram.org 미허용) " + text)
                    results[ch] = "blocked(export-gate)"
                    continue
                _post_json(url, {"chat_id": chat, "text": text})
                results[ch] = "ok"
            elif ch == "webhook":
                url = os.environ.get("AXP_WEBHOOK_URL", "")
                if not url:
                    _dryrun_log("(webhook 미설정) " + text)
                    results[ch] = "dryrun(no-config)"
                    continue
                if not _host_allowed(url):
                    _dryrun_log(f"(반출 게이트 차단: {urllib.parse.urlparse(url).hostname} 미허용) " + text)
                    results[ch] = "blocked(export-gate)"
                    continue
                _post_json(url, {"text": text, "level": level, "module": module})
                results[ch] = "ok"
            else:
                results[ch] = "unknown-channel"
        except Exception as e:  # noqa: BLE001 — 알림 실패가 파이프라인을 죽이면 안 된다
            _dryrun_log(f"(발신 실패 {ch}: {e}) " + text)
            results[ch] = f"error: {e}"
    return results


def cycle_summary(run_date: str, results: dict[str, str]) -> dict:
    """야간 배치 종료 요약 — 실패가 있으면 crit, 없으면 info."""
    fails = {k: v for k, v in results.items() if v != "ok"}
    if fails:
        msg = (f"야간 배치 {run_date}: {len(fails)}/{len(results)} 단계 실패 — "
               + ", ".join(f"{k}({v})" for k, v in list(fails.items())[:5]))
        return send("crit", "scheduler", msg)
    return send("info", "scheduler",
                f"야간 배치 {run_date}: 전체 {len(results)}단계 정상 완료")
