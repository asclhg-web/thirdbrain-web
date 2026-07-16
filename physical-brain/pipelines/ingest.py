"""실데이터 인제스트(1차: 파일 기반). inbox/ 폴더의 CSV를 그래프로.

CSV 규약(헤더): person,type,value,unit,measured_at
- type: bp_sys|bp_dia|rhr|hrv|glucose|sleep_hours|steps ...
- 중복 방지: (person,type,measured_at) 기반 노드 id 멱등
"""
import argparse
import csv
import os
import shutil

from graph import store

BASE = os.path.join(os.path.dirname(__file__), "..", "data")
INBOX, PROCESSED, FAILED = (os.path.join(BASE, d) for d in ("inbox", "processed", "failed"))
REQUIRED = {"person", "type", "value", "unit", "measured_at"}


def ingest_file(path: str) -> dict:
    added = 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not REQUIRED.issubset(set(reader.fieldnames)):
            raise ValueError(f"필수 컬럼 누락: {REQUIRED - set(reader.fieldnames or [])}")
        for row in reader:
            person = row["person"].strip()
            pid = store.person_id(person)
            if not store.get_node(pid):
                store.upsert_node(pid, "Person", {"name": person})
            mtype = row["type"].strip()
            at = row["measured_at"].strip()
            if row["type"].strip() in ("sleep_hours", "steps", "walk"):
                kind = "sleep" if "sleep" in mtype else "walk"
                aid = f"activity:{person}:{kind}:{at}"
                store.upsert_node(aid, "Activity", {"kind": kind, "value": float(row["value"]),
                                                    "unit": row["unit"], "at": at})
                store.upsert_edge(pid, "PERFORMED", aid)
            else:
                mid = f"measurement:{person}:{mtype}:{at}"
                store.upsert_node(mid, "Measurement", {"type": mtype, "value": float(row["value"]),
                                                       "unit": row["unit"], "measured_at": at})
                store.upsert_edge(pid, "MEASURED", mid)
            added += 1
    return {"added": added}


def process_inbox() -> dict:
    for d in (INBOX, PROCESSED, FAILED):
        os.makedirs(d, exist_ok=True)
    ok, failed = [], []
    for fn in sorted(os.listdir(INBOX)):
        src = os.path.join(INBOX, fn)
        try:
            r = ingest_file(src)
            shutil.move(src, os.path.join(PROCESSED, fn))
            ok.append((fn, r["added"]))
        except Exception as e:
            shutil.move(src, os.path.join(FAILED, fn))
            with open(os.path.join(FAILED, fn + ".error.txt"), "w", encoding="utf-8") as ef:
                ef.write(str(e))
            failed.append((fn, str(e)))
    return {"ok": ok, "failed": failed}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true")
    args = ap.parse_args()
    print(process_inbox())
    if args.watch:
        import time
        while True:
            time.sleep(10)
            r = process_inbox()
            if r["ok"] or r["failed"]:
                print(r)
