"""M1-2 엑셀 업로더·매핑 저장소.

원칙: "정리하고 가져오라"가 아니라 "가져와서 정리한다".
같은 양식(열 구성 지문)은 1회 매핑 후 자동. 원본은 불변 보존.
오류는 한글로 — 몇 행 몇 열이 왜 거절됐는지.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from .. import common, db
from . import staging

DDL = """
CREATE TABLE IF NOT EXISTS excel_mappings (
  fingerprint TEXT PRIMARY KEY,      -- 열 이름 시퀀스의 해시
  sheet_kind  TEXT NOT NULL,         -- sales_summary | promo_calendar | vendor_price | ...
  mapping     TEXT NOT NULL,         -- {원본열: 표준필드}
  date_format TEXT DEFAULT '',
  created_by  TEXT,
  created_at  TEXT
);
CREATE TABLE IF NOT EXISTS excel_uploads (
  upload_id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename TEXT, fingerprint TEXT, sheet_kind TEXT,
  rows_ok INTEGER, rows_rejected INTEGER, raw_ref TEXT,
  uploaded_by TEXT, uploaded_at TEXT
);
"""

# 표준 필드 사전 — 매핑의 목적지 (sheet_kind 별 필수 필드)
STANDARD_FIELDS = {
    "sales_summary": {"date": True, "store_id": True, "product_id": True, "qty": True},
    "promo_calendar": {"date_start": True, "date_end": True, "product_id": True,
                       "promo_name": False, "discount_pct": False},
    "vendor_price": {"vendor_id": True, "material_id": True, "unit_price": True,
                     "valid_from": False},
}


def init() -> None:
    staging.init()
    db.executescript(DDL)


def fingerprint(columns: list[str]) -> str:
    norm = "|".join(str(c).strip().lower() for c in columns)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]


def profile(path: Path, sheet: str | int = 0) -> dict:
    """시트 프로파일링 — 헤더 탐지·열 타입 추정. 업로드 UI의 미리보기 재료."""
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    header_row = 0
    for i in range(min(5, len(raw))):          # 상단 5행에서 헤더 후보 탐색
        row = raw.iloc[i]
        if row.notna().sum() >= max(2, int(raw.shape[1] * 0.6)) and row.astype(str).str.len().mean() < 30:
            header_row = i
            break
    df = pd.read_excel(path, sheet_name=sheet, header=header_row)
    df = df.dropna(axis=1, how="all")
    cols = []
    for c in df.columns:
        s = df[c].dropna()
        guess = "text"
        if len(s):
            if pd.api.types.is_numeric_dtype(s):
                guess = "number"
            else:
                try:
                    pd.to_datetime(s.head(20), errors="raise", format="mixed")
                    guess = "date"
                except Exception:
                    guess = "text"
        cols.append({"name": str(c), "type_guess": guess,
                     "sample": [str(v) for v in s.head(3).tolist()]})
    return {"header_row": header_row, "n_rows": len(df),
            "fingerprint": fingerprint([c["name"] for c in cols]), "columns": cols}


def save_mapping(fp: str, sheet_kind: str, mapping: dict[str, str],
                 by: str, date_format: str = "") -> None:
    """매핑 저장 — 같은 지문은 다음부터 자동 적용된다."""
    init()
    required = {f for f, req in STANDARD_FIELDS[sheet_kind].items() if req}
    missing = required - set(mapping.values())
    if missing:
        raise ValueError(f"필수 표준 필드 미매핑: {sorted(missing)}")
    db.execute(
        "INSERT OR REPLACE INTO excel_mappings VALUES (?,?,?,?,?,?)",
        (fp, sheet_kind, json.dumps(mapping, ensure_ascii=False), date_format,
         by, common.now_iso()),
    )


def find_mapping(fp: str) -> dict | None:
    init()
    return db.one("SELECT * FROM excel_mappings WHERE fingerprint=?", (fp,))


def upload(path: Path, by: str, sheet: str | int = 0) -> dict:
    """업로드 실행 — 지문 매핑이 있으면 자동, 없으면 매핑 필요 응답.

    반환: {status: mapped|needs_mapping, upload_id, errors: [한글 오류]}
    """
    init()
    prof = profile(path, sheet)
    m = find_mapping(prof["fingerprint"])
    raw_ref = common.preserve_raw(Path(path), "excel")
    if m is None:
        return {"status": "needs_mapping", "profile": prof, "raw_ref": raw_ref,
                "message": "처음 보는 양식입니다 — 열 매핑을 지정하면 다음부터 자동으로 받아들입니다."}

    mapping = json.loads(m["mapping"])
    kind = m["sheet_kind"]
    df = pd.read_excel(path, sheet_name=sheet, header=prof["header_row"])
    errors: list[str] = []
    ok_rows: list[dict] = []
    required = {f for f, req in STANDARD_FIELDS[kind].items() if req}
    for idx, row in df.iterrows():
        rec, bad = {}, None
        for src_col, std_field in mapping.items():
            val = row.get(src_col)
            if std_field in required and (pd.isna(val) or str(val).strip() == ""):
                bad = f"{idx + prof['header_row'] + 2}행 '{src_col}' 열: 필수값 비어 있음"
                break
            if std_field.startswith("date") and not pd.isna(val):
                try:
                    val = pd.to_datetime(val).date().isoformat()
                except Exception:
                    bad = f"{idx + prof['header_row'] + 2}행 '{src_col}' 열: 날짜로 읽을 수 없음 ({val})"
                    break
            if std_field == "qty" and not pd.isna(val):
                try:
                    val = float(val)
                except Exception:
                    bad = f"{idx + prof['header_row'] + 2}행 '{src_col}' 열: 숫자가 아님 ({val})"
                    break
            rec[std_field] = None if pd.isna(val) else val
        if bad:
            errors.append(bad)
        else:
            ok_rows.append(rec)

    with db.conn() as c:
        cur = c.execute(
            "INSERT INTO excel_uploads (filename, fingerprint, sheet_kind, rows_ok, "
            "rows_rejected, raw_ref, uploaded_by, uploaded_at) VALUES (?,?,?,?,?,?,?,?)",
            (Path(path).name, prof["fingerprint"], kind, len(ok_rows), len(errors),
             raw_ref, by, common.now_iso()),
        )
        upload_id = cur.lastrowid
        c.executemany(
            "INSERT INTO staging_excel (upload_id, sheet_kind, row_no, payload, "
            "_raw_ref, _ingested_at, _source) VALUES (?,?,?,?,?,?,?)",
            [(upload_id, kind, i, json.dumps(r, ensure_ascii=False), raw_ref,
              common.now_iso(), "excel") for i, r in enumerate(ok_rows)],
        )
    return {"status": "mapped", "upload_id": upload_id, "sheet_kind": kind,
            "rows_ok": len(ok_rows), "rows_rejected": len(errors), "errors": errors[:50]}
