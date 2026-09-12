"""P4-4: 업타임 하트비트 — 웹앱 /health 를 두드리고, 연속 실패 시 경보.

보유 서버의 systemd 타이머(axp-heartbeat.timer, 5분)로 돈다.
경보는 플랫폼 notify 모듈(텔레그램/웹훅)을 재사용 — 다운 감지 시 1회,
복구 시 1회만 보낸다(상태 파일로 중복 억제). SLA 3장 "P1은 플랫폼이
먼저 감지·경보"의 구현체다.

환경: AXP_HEALTH_URL (기본 http://127.0.0.1:8900/health)
      AXP_HEARTBEAT_STATE (기본 /var/lib/axp/heartbeat.state)
      AXP_HEARTBEAT_FAILS (연속 실패 임계, 기본 2)
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))

URL = os.environ.get("AXP_HEALTH_URL", "http://127.0.0.1:8900/health")
STATE = Path(os.environ.get("AXP_HEARTBEAT_STATE", "/var/lib/axp/heartbeat.state"))
THRESHOLD = int(os.environ.get("AXP_HEARTBEAT_FAILS", "2"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {"fails": 0, "down_since": ""}


def _save(st: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st), encoding="utf-8")


def _alert(level: str, msg: str) -> None:
    try:
        from axp import common
        common.alert(level, "heartbeat", msg)
    except Exception:  # noqa: BLE001 — 플랫폼 DB가 죽어도 하트비트는 말한다
        print(f"[HEARTBEAT/{level}] {msg}")
        try:
            from axp import notify
            notify.send(level, "heartbeat", msg)
        except Exception:
            pass


def _check_recon(st: dict) -> None:
    """P5-O: 정합 배치 감시 — 최근 recon_log가 실패면 crit 1회(복구 시 info 1회).

    reconcile_prod는 야간 배치 안에서 경보를 내지만, 배치 자체가 안 돌거나
    운영자가 놓친 실패를 하트비트(5분)가 이중으로 잡는다. 상태 파일의
    recon_bad(실패 run_at)로 같은 실패의 반복 경보를 억제한다."""
    try:
        from axp import db
        row = db.one("SELECT run_at, ok FROM recon_log ORDER BY run_at DESC LIMIT 1")
    except Exception:  # noqa: BLE001 — recon 미구성 프로파일(체험 등)은 신호 없음
        return
    if not row:
        return
    if not row["ok"]:
        if st.get("recon_bad") != row["run_at"]:
            _alert("crit", f"정합 배치 실패 감지(run_at={row['run_at']}) — "
                           "recon_log 확인, 처방: 전량 재동기화")
            st["recon_bad"] = row["run_at"]
    elif st.get("recon_bad"):
        _alert("info", f"정합 배치 복구 — 최근 통과 run_at={row['run_at']}")
        st["recon_bad"] = ""


def check() -> int:
    st = _load()
    _check_recon(st)
    try:
        with urllib.request.urlopen(URL, timeout=10) as r:
            ok = r.status == 200 and json.loads(r.read()).get("ok") is True
    except Exception:  # noqa: BLE001
        ok = False

    if ok:
        if st.get("down_since"):
            _alert("info", f"웹앱 복구 — 다운 시작 {st['down_since']} → 복구 {_now()}")
        _save({**st, "fails": 0, "down_since": ""})
        return 0

    st["fails"] = st.get("fails", 0) + 1
    if st["fails"] == THRESHOLD:          # 임계 도달 순간 1회만 발화
        st["down_since"] = st.get("down_since") or _now()
        _alert("crit", f"웹앱 다운 감지({THRESHOLD}회 연속 실패): {URL}")
    _save(st)
    return 1


if __name__ == "__main__":
    sys.exit(check())
