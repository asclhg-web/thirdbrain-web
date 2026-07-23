"""T29 — 삼성헬스 '개인 데이터 다운로드' zip → 그래프 (갤럭시 워치8 실데이터).

가져오는 것: 맥박(일별 안정 심박 근사=일 최저), 수면(밤별 시간), 걸음(일별),
혈압(측정 시각 그대로), 산소포화도(일 최저), 스트레스(일 평균) — H01 확장.
사용:  python -m pipelines.samsung_health --zip 다운로드.zip [--person 나]
자동:  볼트의 `인박스/` 폴더에 zip을 넣으면 심장박동이 5분 내 처리
       (처리 후 `인박스/처리됨/`으로 이동 — 옵시디언/OneDrive에서 확인 가능)

파서는 삼성 CSV의 관례(1행 메타데이터, 2행 헤더, 접두사 붙은 컬럼명)를
관대하게 처리한다. 실패한 파일은 건너뛰고 이유를 남긴다.
"""
import argparse
import csv
import io
import os
import shutil
import zipfile
from collections import defaultdict
from datetime import datetime

from graph import store

SLEEP_MAX_H = 16  # 이상치 세션 무시


def _dt(s: str) -> datetime | None:
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    try:  # epoch ms
        return datetime.fromtimestamp(float(s) / 1000)
    except (ValueError, OSError):
        return None


def _rows(data: bytes) -> tuple[list[str], list[dict]]:
    """삼성 CSV: 1행 메타 → 2행 헤더. 일반 CSV면 1행 헤더로 폴백."""
    text = data.decode("utf-8-sig", errors="replace")
    lines = text.splitlines()
    if not lines:
        return [], []
    reader = list(csv.reader(lines))
    start = 1 if lines[0].startswith("com.samsung") else 0
    if len(reader) <= start:
        return [], []
    header = reader[start]
    rows = [dict(zip(header, r)) for r in reader[start + 1:] if len(r) > 1]
    return header, rows


def _col(header: list[str], suffix: str) -> str | None:
    for h in header:
        if h == suffix or h.endswith("." + suffix):
            return h
    return None


def _ensure_person(person: str) -> str:
    pid = store.person_id(person)
    if not store.get_node(pid):
        store.upsert_node(pid, "Person", {"name": person})
    return pid


def _put_measurement(person, mtype, value, unit, at_iso):
    pid = _ensure_person(person)
    mid = f"measurement:{person}:{mtype}:{at_iso}"
    store.upsert_node(mid, "Measurement", {"type": mtype, "value": round(float(value), 1),
                                           "unit": unit, "measured_at": at_iso, "src": "samsung"})
    store.upsert_edge(pid, "MEASURED", mid)


def _put_activity(person, kind, value, unit, at_iso):
    pid = _ensure_person(person)
    aid = f"activity:{person}:{kind}:{at_iso}"
    store.upsert_node(aid, "Activity", {"kind": kind, "value": round(float(value), 1),
                                        "unit": unit, "at": at_iso, "src": "samsung"})
    store.upsert_edge(pid, "PERFORMED", aid)


def _parse_heart_rate(header, rows, person) -> int:
    t_col, hr_col = _col(header, "start_time"), _col(header, "heart_rate")
    if not (t_col and hr_col):
        return 0
    day_min: dict[str, float] = {}
    for r in rows:
        t, v = _dt(r.get(t_col, "")), r.get(hr_col, "")
        try:
            v = float(v)
        except (TypeError, ValueError):
            continue
        if not t or not (25 < v < 250):
            continue
        d = t.date().isoformat()
        day_min[d] = min(day_min.get(d, 999), v)
    for d, v in day_min.items():
        _put_measurement(person, "rhr", v, "bpm", f"{d}T06:00:00")
    return len(day_min)


def _parse_sleep(header, rows, person) -> int:
    s_col, e_col = _col(header, "start_time"), _col(header, "end_time")
    if not (s_col and e_col):
        return 0
    night_h: dict[str, float] = defaultdict(float)
    for r in rows:
        s, e = _dt(r.get(s_col, "")), _dt(r.get(e_col, ""))
        if not s or not e:
            continue
        h = (e - s).total_seconds() / 3600
        if 0 < h <= SLEEP_MAX_H:
            night_h[e.date().isoformat()] += h
    for d, h in night_h.items():
        _put_activity(person, "sleep", round(h, 1), "h", f"{d}T08:00:00")
    return len(night_h)


def _parse_steps(header, rows, person) -> int:
    c_col, d_col = _col(header, "count"), _col(header, "day_time")
    src_col = _col(header, "source_type")
    if not (c_col and d_col):
        return 0
    day_steps: dict[str, float] = {}
    for r in rows:
        if src_col and r.get(src_col, "") not in ("", "-2"):  # -2 = 기기 통합값
            continue
        t = _dt(r.get(d_col, ""))
        try:
            v = float(r.get(c_col, ""))
        except (TypeError, ValueError):
            continue
        if t and v >= 0:
            day_steps[t.date().isoformat()] = max(day_steps.get(t.date().isoformat(), 0), v)
    for d, v in day_steps.items():
        _put_activity(person, "walk", v, "steps", f"{d}T00:00:00")
    return len(day_steps)


def _parse_bp(header, rows, person) -> int:
    """혈압계 연동 기록 — 측정 시각 그대로 보존 (H01)."""
    t_col = _col(header, "start_time")
    s_col, d_col = _col(header, "systolic"), _col(header, "diastolic")
    if not (t_col and s_col and d_col):
        return 0
    n = 0
    for r in rows:
        t = _dt(r.get(t_col, ""))
        try:
            s, d = float(r.get(s_col, "")), float(r.get(d_col, ""))
        except (TypeError, ValueError):
            continue
        if not t or not (50 < s < 260 and 30 < d < 200):
            continue
        at = t.isoformat()
        _put_measurement(person, "bp_sys", s, "mmHg", at)
        _put_measurement(person, "bp_dia", d, "mmHg", at)
        n += 1
    return n


def _parse_spo2(header, rows, person) -> int:
    """산소포화도 — 하루 최저값(가장 나쁜 순간)을 보존 (H01)."""
    t_col, v_col = _col(header, "start_time"), _col(header, "spo2")
    if not (t_col and v_col):
        return 0
    day_min: dict[str, float] = {}
    for r in rows:
        t = _dt(r.get(t_col, ""))
        try:
            v = float(r.get(v_col, ""))
        except (TypeError, ValueError):
            continue
        if not t or not (70 <= v <= 100):
            continue
        d = t.date().isoformat()
        day_min[d] = min(day_min.get(d, 101), v)
    for d, v in day_min.items():
        _put_measurement(person, "spo2", v, "%", f"{d}T06:00:00")
    return len(day_min)


def _parse_stress(header, rows, person) -> int:
    """스트레스 점수 — 하루 평균 (해석하지 않고 추이만) (H01)."""
    t_col, v_col = _col(header, "start_time"), _col(header, "score")
    if not (t_col and v_col):
        return 0
    day_vals: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        t = _dt(r.get(t_col, ""))
        try:
            v = float(r.get(v_col, ""))
        except (TypeError, ValueError):
            continue
        if t and 0 < v <= 100:
            day_vals[t.date().isoformat()].append(v)
    for d, vs in day_vals.items():
        _put_measurement(person, "stress", sum(vs) / len(vs), "점", f"{d}T12:00:00")
    return len(day_vals)


KIND_PARSERS = [("heart_rate", _parse_heart_rate), ("sleep", _parse_sleep),
                ("step_daily_trend", _parse_steps), ("blood_pressure", _parse_bp),
                ("oxygen_saturation", _parse_spo2), ("stress", _parse_stress)]


def parse_export(path: str, person: str = "나") -> dict:
    """zip(또는 풀린 폴더)에서 심박·수면·걸음을 그래프로. 반환: 종류별 일수."""
    result = {"rhr_days": 0, "sleep_nights": 0, "walk_days": 0,
              "bp_readings": 0, "spo2_days": 0, "stress_days": 0, "skipped": []}
    keymap = {"heart_rate": "rhr_days", "sleep": "sleep_nights", "step_daily_trend": "walk_days",
              "blood_pressure": "bp_readings", "oxygen_saturation": "spo2_days",
              "stress": "stress_days"}

    def each_csv():
        if zipfile.is_zipfile(path):
            with zipfile.ZipFile(path) as z:
                for name in z.namelist():
                    if name.endswith(".csv"):
                        yield os.path.basename(name), z.read(name)
        else:
            for root, _d, files in os.walk(path):
                for fn in files:
                    if fn.endswith(".csv"):
                        yield fn, open(os.path.join(root, fn), "rb").read()

    for fn, data in each_csv():
        for kind, parser in KIND_PARSERS:
            # 'sleep'은 sleep_stage/sleep_goal 등과 구분
            if f".{kind}." in fn:
                try:
                    header, rows = _rows(data)
                    result[keymap[kind]] += parser(header, rows, person)
                except Exception as e:
                    result["skipped"].append(f"{fn}: {e}")
                break
    return result


def process_dropbox(dirpath: str, person: str = "나") -> dict:
    """볼트 인박스 폴더 처리: 삼성 zip + 규약 CSV(person,type,value,unit,measured_at)."""
    from pipelines.ingest import ingest_file
    done_dir, fail_dir = os.path.join(dirpath, "처리됨"), os.path.join(dirpath, "실패")
    ok, failed = [], []
    for fn in sorted(os.listdir(dirpath)):
        src = os.path.join(dirpath, fn)
        if not os.path.isfile(src):
            continue
        try:
            if fn.lower().endswith(".zip"):
                r = parse_export(src, person)
                ok.append((fn, r))
            elif fn.lower().endswith(".csv"):
                r = ingest_file(src)
                ok.append((fn, r))
            else:
                continue
            os.makedirs(done_dir, exist_ok=True)
            shutil.move(src, os.path.join(done_dir, fn))
        except Exception as e:
            os.makedirs(fail_dir, exist_ok=True)
            shutil.move(src, os.path.join(fail_dir, fn))
            with open(os.path.join(fail_dir, fn + ".error.txt"), "w", encoding="utf-8") as ef:
                ef.write(str(e))
            failed.append((fn, str(e)))
    return {"ok": ok, "failed": failed}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True, help="삼성헬스 다운로드 zip (또는 풀린 폴더)")
    ap.add_argument("--person", default="나")
    args = ap.parse_args()
    print(parse_export(args.zip, args.person))
