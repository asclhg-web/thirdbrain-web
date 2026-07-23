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
BP = (
    "com.samsung.health.blood_pressure,4,meta\n"
    "com.samsung.health.blood_pressure.start_time,com.samsung.health.blood_pressure.systolic,"
    "com.samsung.health.blood_pressure.diastolic\n"
    "2026-07-16 08:05:00.000,128,82\n"
    "2026-07-17 08:10:00.000,999,82\n"          # 이상치 → 무시
    "2026-07-17 08:12:00.000,133,86\n"
)
SPO2 = (
    "com.samsung.shealth.tracker.oxygen_saturation,2,meta\n"
    "com.samsung.health.oxygen_saturation.start_time,com.samsung.health.oxygen_saturation.spo2\n"
    "2026-07-16 03:00:00.000,97\n"
    "2026-07-16 04:00:00.000,94\n"
    "2026-07-16 05:00:00.000,55\n"              # 이상치 → 무시
)
STRESS = (
    "com.samsung.shealth.stress,3,meta\n"
    "com.samsung.shealth.stress.start_time,com.samsung.shealth.stress.score\n"
    "2026-07-16 10:00:00.000,40\n"
    "2026-07-16 15:00:00.000,60\n"
)


def make_zip(tmp_path):
    zp = tmp_path / "samsunghealth_test.zip"
    with zipfile.ZipFile(zp, "w") as z:
        z.writestr("export/com.samsung.shealth.tracker.heart_rate.20260718.csv", HR)
        z.writestr("export/com.samsung.shealth.sleep.20260718.csv", SLEEP)
        z.writestr("export/com.samsung.shealth.step_daily_trend.20260718.csv", STEPS)
        z.writestr("export/com.samsung.health.blood_pressure.20260718.csv", BP)
        z.writestr("export/com.samsung.shealth.tracker.oxygen_saturation.20260718.csv", SPO2)
        z.writestr("export/com.samsung.shealth.stress.20260718.csv", STRESS)
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
    # H01 확장: 혈압(이상치 제외 2건) · 산소포화도(일 최저) · 스트레스(일 평균)
    assert r["bp_readings"] == 2 and r["spo2_days"] == 1 and r["stress_days"] == 1
    bps = fresh_db.measurements("나", "bp_sys", 5, now)
    assert {m["value"] for m in bps} == {128.0, 133.0}, "999는 이상치로 무시"
    spo2 = fresh_db.measurements("나", "spo2", 5, now)
    assert [m["value"] for m in spo2] == [94.0], "일 최저(97,94) 채택·55는 무시"
    stress = fresh_db.measurements("나", "stress", 5, now)
    assert [m["value"] for m in stress] == [50.0], "일 평균 (40+60)/2"


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
