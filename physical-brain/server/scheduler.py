"""실서비스 심장박동 — 서버와 함께 도는 백그라운드 루프 (T28에서 연결).

- 매 분: orchestrator.run_tick()  → 아침 브리핑·복약 알림·재알림·미확인 처리
- 5분마다: 볼트 동기화(VAULT_PATH) → 옵시디언에서 지식을 고치면 앱에 반영
- 끄기: PB_HEARTBEAT=0 (테스트 환경)
"""
import os
import threading
import time
import traceback
from datetime import datetime

_started = False
SYNC_EVERY_S = 300


def vault_path() -> str:
    return os.environ.get("VAULT_PATH") or os.path.join(
        os.path.dirname(__file__), "..", "graph", "sample_vault")


def _loop():
    from pipelines.ingest import process_inbox
    from pipelines.samsung_health import process_dropbox
    from pipelines.vault_sync import sync_vault
    from server.orchestrator import run_tick
    last_sync = 0.0
    while True:
        try:
            if time.time() - last_sync >= SYNC_EVERY_S:
                r = sync_vault(vault_path())
                last_sync = time.time()
                if r["changed"] or r["archived"]:
                    print(f"[볼트동기화] {r}", flush=True)
                ri = process_inbox()  # data/inbox 규약 CSV
                inbox = os.path.join(vault_path(), "인박스")  # 볼트 인박스: 삼성 zip 등
                rd = process_dropbox(inbox) if os.path.isdir(inbox) else {"ok": [], "failed": []}
                if ri["ok"] or ri["failed"] or rd["ok"] or rd["failed"]:
                    print(f"[실데이터] inbox={ri} 볼트인박스={rd}", flush=True)
                # G-Legacy: 주 1회 유산 패키지 자동 생성 — 언제 멈춰도 선물이 되도록
                from graph_core import legacy
                pkg = legacy.auto_build_if_due(7, vault_path())
                if pkg:
                    print(f"[유산패키지] 생성: {pkg}", flush=True)
                # R09: 주 1회 로봇 재검 — 인증이 과거가 되지 않도록 (Drift Check)
                from robot_lms import recheck as robot_recheck
                rr = robot_recheck.auto_if_due(datetime.now())
                if rr:
                    print(f"[로봇재검] {rr}", flush=True)
                # R10: 매달 초, 지난달 로봇 지능 리포트 자동 생성 (볼트 = 유산)
                from robot_lms import report as robot_report
                rp = robot_report.auto_if_due(datetime.now(), vault_path())
                if rp:
                    print(f"[로봇리포트] {rp['month']} 생성: {rp['path']}", flush=True)
            fired = run_tick(datetime.now())
            if fired:
                print(f"[규칙실행] {fired}", flush=True)
        except Exception:
            traceback.print_exc()
        # 다음 분 경계까지 대기 (시각 트리거 07:00 등을 놓치지 않도록)
        time.sleep(max(5, 61 - datetime.now().second))


def start():
    global _started
    if _started or os.environ.get("PB_HEARTBEAT", "1") == "0":
        return None
    _started = True
    t = threading.Thread(target=_loop, daemon=True, name="pb-heartbeat")
    t.start()
    print(f"[심장박동 시작] 볼트: {os.path.abspath(vault_path())}", flush=True)
    return t
