"""T29 검증: 삼성헬스 zip 파싱 → rhr·수면·걸음, 인박스 드롭 처리, 혈압 폼."""
import os
import zipfile

from pipelines.samsung_health import parse_export, process_dropbox

HR = (
    "com.samsung.shealth.tracker.heart_rate,6,meta\n"
    "com.samsung.health.heart_rate.start_time,com.samsung.health.heart_rate.heart_rate,extra\n"
    "2026-07-16 07:10:00.000,58,x\n"
    "2026-07-16 14:00:00.000,84,x\n"
    "2026-07-17 06:50:00.000,61,x\n"
)
SLEEP = (
    "com.samsung.shealth.sleep,5,meta\n"
    "com.samsung.health.sleep.start_time,com.samsung.health.sleep.end_time\n"
    "2026-07-15 23:10:00.000,2026-07-16 06:40:00.000\n"
    "2026-07-16 23:40:00.000,2026-07-17 05:50:00.000\n"
)
STEPS = (
    "com.samsung.shealth.step_daily_trend,3,meta\n"
    "count,day_time,source_type\n"
    "8123,1784217600000,-2\n"
    "9500,1784217600000,5\n"
    "6001,1784304000000,-2\n"
)


def make_zip(tmp_path):
    zp = tmp_path / "samsunghealth_test.zip"
    with zipfile.ZipFile(zp, "w") as z:
        z.writestr("export/com.samsung.shealth.tracker.heart_rate.20260718.csv", HR)
        z.writestr("export/com.samsung.shealth.sleep.20260718.csv", SLEEP)
        z.writestr("export/com.samsung.shealth.step_daily_trend.20260718.csv", STEPS)
    return zp


def test_parse_export(fresh_db, tmp_path):
    r = parse_export(str(make_zip(tmp_path)), person="나")
    assert r["rhr_days"] == 2 and r["sleep_nights"] == 2 and r["walk_days"] == 2
    assert not r["skipped"]
    from datetime import datetime
    now = datetime(2026, 7, 18)
    rhr = fresh_db.measurements("나", "rhr", 5, now)
    assert {m["value"] for m in rhr} >= {58.0, 61.0}, "일 최저 심박이 rhr로 저장되어야"
    sleeps = fresh_db.activities("나", "sleep", 5, now)
    assert any(abs(a["value"] - 7.5) < 0.01 for a in sleeps), "수면 시간 계산(23:10~06:40=7.5h)"
    walks = fresh_db.activities("나", "walk", 5, now)
    assert {a["value"] for a in walks} == {8123.0, 6001.0}, "source_type=-2만 채택해야"


def test_dropbox_zip_moved(fresh_db, tmp_path):
    inbox = tmp_path / "인박스"
    inbox.mkdir()
    make_zip(tmp_path).rename(inbox / "samsung.zip")
    r = process_dropbox(str(inbox))
    assert len(r["ok"]) == 1 and not r["failed"]
    assert os.path.exists(inbox / "처리됨" / "samsung.zip"), "처리 후 이동되어야"


def test_bp_form_records_and_checks(fresh_db):
    from fastapi.testclient import TestClient
    from server.main import app
    c = TestClient(app)
    resp = c.post("/bp", data={"person": "나", "sys": 142, "dia": 88}, follow_redirects=False)
    assert resp.status_code == 303
    from datetime import datetime, timedelta
    now = datetime.now() + timedelta(minutes=1)
    ms = fresh_db.measurements("나", "bp_sys", 1, now)
    assert ms and ms[-1]["value"] == 142.0
    ev = fresh_db.events("나", 1, "임계초과", now)
    assert ev, "135 초과는 1층 안전망이 즉시 기록해야"
