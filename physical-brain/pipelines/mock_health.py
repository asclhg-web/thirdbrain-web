"""개발용 건강 데이터 목업 생성기 — 현실적 패턴 + 10% 결측(0 채우기 금지).

패턴 설계(도서 5장 근거):
- 혈압: 아버지 평균 138/88(요일 변동, 월요일↑), 나 122/78. 아침·저녁 각 1세트.
- RHR: 개인 기준선 ±5, '음주 가정일'(금요일) +8
- HRV: 주중 완만 하락, 주말 회복
- 혈당(CGM 요약: 일별 스파이크 횟수): '면 요리 날'(수요일) 급등
- 수면: 목요일 무너짐(도서의 '놀란 점' 패턴 재현), 걷음수
"""
import argparse
import random
from datetime import datetime, timedelta

from graph import store


def wipe_all_measurements() -> int:
    """실데이터 전환용(T29): 모든 측정·활동 삭제. 지식(약·규칙)과 이벤트는 유지.
    주의: 실데이터 입력 '시작 전' 1회만 사용할 것."""
    conn = store.get_conn()
    n = conn.execute("SELECT COUNT(*) c FROM nodes WHERE type IN ('Measurement','Activity')").fetchone()["c"]
    conn.execute("DELETE FROM edges WHERE dst IN (SELECT id FROM nodes WHERE type IN ('Measurement','Activity'))")
    conn.execute("DELETE FROM nodes WHERE type IN ('Measurement','Activity')")
    conn.commit()
    return n

PROFILES = {
    "아버지": {"bp": (138, 88), "rhr": 66, "hrv": 32, "sleep": 6.8, "steps": 5200},
    "나": {"bp": (122, 78), "rhr": 58, "hrv": 48, "sleep": 6.5, "steps": 7400},
}
MISSING_RATE = 0.10


def _mid(person, mtype, value, unit, at: datetime):
    mid = f"measurement:{person}:{mtype}:{at.isoformat()}"
    store.upsert_node(mid, "Measurement", {
        "type": mtype, "value": round(value, 1), "unit": unit, "measured_at": at.isoformat()})
    store.upsert_edge(store.person_id(person), "MEASURED", mid)


def _act(person, kind, value, unit, at: datetime):
    aid = f"activity:{person}:{kind}:{at.isoformat()}"
    store.upsert_node(aid, "Activity", {"kind": kind, "value": round(value, 1), "unit": unit, "at": at.isoformat()})
    store.upsert_edge(store.person_id(person), "PERFORMED", aid)


def generate(days: int = 30, end: datetime | None = None, seed: int = 42):
    rng = random.Random(seed)
    end = end or datetime.now()
    made, missing = 0, 0
    for person, p in PROFILES.items():
        pid = store.person_id(person)
        if not store.get_node(pid):
            store.upsert_node(pid, "Person", {"name": person})
        for d in range(days, 0, -1):
            day = (end - timedelta(days=d)).replace(hour=0, minute=0, second=0, microsecond=0)
            wd = day.weekday()  # 월0 ... 일6
            # 혈압 (아침 07:05 / 저녁 21:40)
            for hh, mm, drift in ((7, 5, 3 if wd == 0 else 0), (21, 40, -2)):
                if rng.random() < MISSING_RATE:
                    missing += 1
                    continue
                sys_v = rng.gauss(p["bp"][0] + drift, 4)
                dia_v = rng.gauss(p["bp"][1] + drift * 0.5, 3)
                at = day.replace(hour=hh, minute=mm)
                _mid(person, "bp_sys", sys_v, "mmHg", at)
                _mid(person, "bp_dia", dia_v, "mmHg", at)
                made += 2
            # RHR / HRV (기상 시 자동)
            if rng.random() >= MISSING_RATE:
                boost = 8 if wd == 4 else 0  # 금요일 과음 가정
                _mid(person, "rhr", rng.gauss(p["rhr"] + boost, 2), "bpm", day.replace(hour=6, minute=50))
                _mid(person, "hrv", rng.gauss(p["hrv"] - (wd * 0.8 if wd < 5 else -2), 3), "ms",
                     day.replace(hour=6, minute=50))
                made += 2
            else:
                missing += 1
            # 혈당 스파이크 횟수 (CGM 일별 요약)
            if rng.random() >= MISSING_RATE:
                spikes = (2 if wd == 2 else 0) + (1 if rng.random() < 0.25 else 0)  # 수요일 면 요리
                _mid(person, "glucose_spikes", spikes, "회", day.replace(hour=23, minute=0))
                made += 1
            # 수면·걸음
            sleep = p["sleep"] + (-1.6 if wd == 3 else rng.gauss(0, 0.5))  # 목요일 무너짐
            _act(person, "sleep", max(3.5, sleep), "h", day.replace(hour=23, minute=30))
            _act(person, "walk", max(0, rng.gauss(p["steps"], 1500)), "steps", day.replace(hour=20, minute=0))
            made += 2
    return {"made": made, "missing": missing}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--wipe", action="store_true",
                    help="모든 측정·활동 삭제 (실데이터 시작 전 1회, T29)")
    args = ap.parse_args()
    if args.wipe:
        print("삭제:", wipe_all_measurements(), "건 |", store.counts())
    else:
        print("목업 생성:", generate(args.days), "|", store.counts())
