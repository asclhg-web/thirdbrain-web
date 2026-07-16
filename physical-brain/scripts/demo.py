"""T20 데모: 가상 하루를 가속 실행 — 아침 브리핑 → 복약 서빙·확인 → 혈당 대응 → 저녁 준비.

알림은 텔레그램(설정 시) 또는 data/outbox.log 로 발송된다.
"""
from datetime import datetime, timedelta

from graph import store
from pipelines.mock_health import generate
from server.orchestrator import ROBOT, run_tick
from server.tasks_today import confirm

DAY = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def main():
    print("── 피지컬브레인 가상 하루 데모 ──")
    print("데이터:", store.counts()["nodes"])
    generate(days=7, end=DAY.replace(hour=6), seed=11)

    t = DAY.replace(hour=6, minute=0)
    end = DAY.replace(hour=22, minute=0)
    while t <= end:
        fired = run_tick(t)
        for name in fired:
            print(f"  [{t.strftime('%H:%M')}] 규칙 실행: {name}")
        if t.strftime("%H:%M") == "07:15":
            r = confirm("아버지", t)
            print(f"  [{t.strftime('%H:%M')}] 아버지: \"먹었다\" → {r['med'] if r else '?'} 확인")
        t += timedelta(minutes=5)

    print("\n── 결과 ──")
    print("로봇 동작 로그:", [f"{a['cmd']}:{a.get('skill', a.get('place'))}" for a in ROBOT.log])
    done = store.events("아버지", 1, "복약완료", end)
    print("복약완료 이벤트:", [e["payload"] for e in done])
    print("발송함(outbox) 확인: data/outbox.log")
    print("대시보드: make dev → http://localhost:8800")


if __name__ == "__main__":
    main()
