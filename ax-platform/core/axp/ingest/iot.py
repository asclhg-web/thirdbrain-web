"""M1-4 IoT 수신·결측 경보.

demo: 파일 재생(합성 센서 CSV) → 시계열 적재.
prod: paho-mqtt 구독(topic: axp/<equipment>/<signal>) — 동일한 ingest_reading 사용.
원시 신호는 파괴적 보정 금지 — 보정값은 별도 컬럼/후처리에서.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from .. import common, db
from . import staging

EXPECTED_PERIOD_MIN = {"temp": 10, "current": 10, "vibration": 10}   # 신호별 기대 주기


def ingest_reading(ts: str, equipment_id: str, signal: str, value: float,
                   source: str = "mqtt") -> None:
    staging.init()
    db.execute(
        "INSERT INTO staging_iot (reading_ts, equipment_id, signal, value, "
        "_ingested_at, _source) VALUES (?,?,?,?,?,?)",
        (ts, equipment_id, signal, value, common.now_iso(), source),
    )


def ingest_frame(df: pd.DataFrame, source: str = "replay") -> int:
    """일괄 적재 — 컬럼: reading_ts, equipment_id, signal, value."""
    staging.init()
    ts = common.now_iso()
    db.executemany(
        "INSERT INTO staging_iot (reading_ts, equipment_id, signal, value, "
        "_ingested_at, _source) VALUES (?,?,?,?,?,?)",
        [(r.reading_ts, r.equipment_id, r.signal, float(r.value), ts, source)
         for r in df.itertuples()],
    )
    return len(df)


def gap_check(as_of: str | None = None) -> list[dict]:
    """결측·단선 탐지 — 신호별 마지막 수신이 기대 주기의 3배를 넘으면 경보."""
    staging.init()
    rows = db.query(
        "SELECT equipment_id, signal, MAX(reading_ts) AS last_ts "
        "FROM staging_iot GROUP BY equipment_id, signal")
    now = datetime.fromisoformat(as_of) if as_of else None
    gaps = []
    for r in rows:
        last = datetime.fromisoformat(r["last_ts"])
        ref = now or datetime.utcnow()
        period = EXPECTED_PERIOD_MIN.get(r["signal"], 10)
        if ref - last > timedelta(minutes=period * 3):
            gap = {"equipment_id": r["equipment_id"], "signal": r["signal"],
                   "last_ts": r["last_ts"], "gap_min": round((ref - last).total_seconds() / 60)}
            gaps.append(gap)
            common.alert("warn", "M1-4",
                         f"신호 단선 의심: {gap['equipment_id']}/{gap['signal']} "
                         f"마지막 수신 {gap['last_ts']} ({gap['gap_min']}분 경과)")
    return gaps
