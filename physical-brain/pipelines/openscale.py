"""H05 — openScale(오픈소스 체중 앱) CSV 어댑터.

사용법(기기 구입 후): openScale 앱에서 내보내기(CSV) → 볼트 `인박스/`에 넣으면
심장박동이 자동 처리한다 (삼성 zip과 같은 길).

가져오는 것: 체중(weight, kg) · 체지방률(fat, %) · 근육률(muscle, %).
같은 시각 재내보내기는 덮어쓴다(멱등 — 측정 시각이 ID).
"""
import csv
import io
from datetime import datetime

from graph import store

COLS = {"weight": ("weight", "kg"), "fat": ("body_fat", "%"), "muscle": ("muscle", "%")}
RANGE = {"weight": (20, 300), "body_fat": (2, 70), "muscle": (10, 90)}


def looks_like(first_line: str) -> bool:
    """openScale CSV 판별 — weight + 날짜 컬럼이 있으면 (규약 CSV에는 person이 있다)."""
    h = first_line.lower()
    return "weight" in h and ("datetime" in h or "date" in h) and "person" not in h


def _dt(s: str) -> datetime | None:
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%d.%m.%Y %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            pass
    return None


def parse_csv(data: bytes, person: str = "나") -> dict:
    """openScale CSV → 측정 노드. 반환: 유형별 건수."""
    text = data.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    pid = store.person_id(person)
    if not store.get_node(pid):
        store.upsert_node(pid, "Person", {"name": person})
    counts = {"weight": 0, "body_fat": 0, "muscle": 0, "skipped": 0}

    date_col = next((c for c in (reader.fieldnames or [])
                     if c.lower() in ("datetime", "date")), None)
    if not date_col:
        return counts
    for row in reader:
        t = _dt(row.get(date_col, "") or "")
        if not t:
            counts["skipped"] += 1
            continue
        at = t.isoformat()
        for col, (mtype, unit) in COLS.items():
            raw = (row.get(col) or "").strip()
            if not raw:
                continue
            try:
                v = float(raw.replace(",", "."))
            except ValueError:
                continue
            lo, hi = RANGE[mtype]
            if not (lo <= v <= hi):
                continue
            mid = f"measurement:{person}:{mtype}:{at}"
            store.upsert_node(mid, "Measurement", {
                "type": mtype, "value": round(v, 1), "unit": unit,
                "measured_at": at, "src": "openscale"})
            store.upsert_edge(pid, "MEASURED", mid)
            counts[mtype] += 1
    return counts
