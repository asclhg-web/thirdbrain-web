"""H05+H06 검증: openScale CSV 어댑터 · Wger API 어댑터 (기기 없이 모의로)."""
from datetime import datetime

from pipelines import openscale, wger

NOW = datetime(2026, 7, 23, 10)

OPENSCALE_CSV = (
    "dateTime,weight,fat,water,muscle,comment\n"
    "2026-07-21 07:30,72.5,23.1,55.0,38.2,\n"
    "2026-07-22 07:31,72.1,22.9,55.2,38.4,아침\n"
    "2026-07-23 07:29,500,22.0,55.0,38.0,\n"      # 체중 이상치 → 체중만 무시
    "잘못된날짜,70,20,50,30,\n"                     # 날짜 불량 → 행 무시
).encode("utf-8")


def test_openscale_parse(fresh_db):
    r = openscale.parse_csv(OPENSCALE_CSV, "나")
    assert r["weight"] == 2 and r["body_fat"] == 3 and r["muscle"] == 3
    assert r["skipped"] == 1
    ws = fresh_db.measurements("나", "weight", 7, NOW)
    assert {m["value"] for m in ws} == {72.5, 72.1}, "500kg 이상치 제외"
    fats = fresh_db.measurements("나", "body_fat", 7, NOW)
    assert all(m["unit"] == "%" for m in fats)


def test_openscale_routes_through_inbox(fresh_db, tmp_path):
    """인박스에 openScale CSV를 넣으면 규약 CSV와 구분해 자동 처리·이동."""
    from pipelines.samsung_health import process_dropbox
    inbox = tmp_path / "인박스"
    inbox.mkdir()
    (inbox / "openscale_export.csv").write_bytes(OPENSCALE_CSV)
    r = process_dropbox(str(inbox))
    assert len(r["ok"]) == 1 and not r["failed"]
    assert r["ok"][0][1]["weight"] == 2
    assert (inbox / "처리됨" / "openscale_export.csv").exists()


class FakeWger:
    def sessions(self, since):
        return [{"date": "2026-07-21", "notes": "하체"},
                {"date": "2026-07-22", "notes": ""}]

    def weights(self, since):
        return [{"date": "2026-07-22", "weight": "72.3"},
                {"date": "2026-07-20", "weight": "999"}]  # 이상치 → 무시


def test_wger_sync(fresh_db):
    r = wger.sync("나", client=FakeWger(), now=NOW)
    assert r == {"workouts": 2, "weights": 1}
    acts = fresh_db.activities("나", "workout", 7, NOW)
    assert len(acts) == 2 and all(a["value"] == 1.0 for a in acts)
    ws = fresh_db.measurements("나", "weight", 7, NOW)
    assert [m["value"] for m in ws] == [72.3]
    assert wger.sync("나", client=FakeWger(), now=NOW)["workouts"] == 2, "멱등"


def test_wger_auto_once_a_day(fresh_db):
    assert wger.auto_sync_if_due(NOW) is None, "미설정이면 조용히 잠든다"
    wger.set_client(FakeWger())
    try:
        assert wger.auto_sync_if_due(NOW)["workouts"] == 2
        assert wger.auto_sync_if_due(NOW) is None, "하루 1회만"
    finally:
        wger.set_client(None)
