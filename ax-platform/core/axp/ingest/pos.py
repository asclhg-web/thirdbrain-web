"""P3-5: POS 반입 어댑터 2종 — 판매 자료의 반입 마찰을 줄인다.

파일럿 현장의 실제 판매 원천은 Odoo가 아니라 POS인 경우가 많다.
국산 POS 정산 프로그램의 내보내기 파일을 그대로 받는다:

  ① daily  — 일별 정산 집계 (영업일자 × 매장 × 상품 단위 수량·금액)
  ② receipt — 영수증 단위 거래 로그 (영수증번호·판매일시·상품·수량·단가)

원칙(M1-2와 동일): 가져와서 정리한다 · 원본 불변 보존 · 개인정보 컬럼 차단 ·
오류는 한글로 몇 행 몇 열이 왜 거절됐는지. 열 이름은 동의어 사전으로 자동
매핑하고, 못 알아본 양식은 needs_mapping 으로 돌려준다(엑셀 업로더와 동일 UX).

중복 규칙: 같은 파일(sha256)은 두 번 반입하지 않는다(멱등). Odoo 판매와
겹치는 (매장×날짜)가 이미 스테이징에 있으면 이중 집계 경고를 낸다 —
판매 정본은 고객사 프로파일에서 pos 또는 odoo 중 하나로 정한다.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import pandas as pd

from .. import common, db
from . import staging
from .excel_uploader import strip_pii_columns

DDL = """
CREATE TABLE IF NOT EXISTS pos_uploads (
  upload_id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename TEXT, file_sha256 TEXT UNIQUE, adapter TEXT,
  rows_ok INTEGER, rows_rejected INTEGER, raw_ref TEXT,
  uploaded_by TEXT, uploaded_at TEXT
);
"""

# 열 이름 동의어 사전 — 국산 POS 내보내기에서 흔한 표기(공백·괄호 무시, 부분 일치)
SYNONYMS_DAILY = {
    "date":       ("영업일자", "판매일자", "매출일자", "일자", "date"),
    "store_id":   ("매장코드", "점포코드", "매장명", "점포명", "지점", "store"),
    "product_id": ("상품코드", "제품코드", "바코드", "product", "sku"),
    "product_name": ("상품명", "제품명", "품명"),
    "qty":        ("판매수량", "수량", "qty", "quantity"),
    "amount":     ("판매금액", "매출금액", "금액", "합계금액", "amount"),
    "discount":   ("할인금액", "할인", "에누리", "discount"),
}
SYNONYMS_RECEIPT = {
    "receipt_no": ("영수증번호", "영수번호", "거래번호", "주문번호", "receipt"),
    "sold_at":    ("판매일시", "거래일시", "결제일시", "판매시간", "datetime"),
    "store_id":   ("매장코드", "점포코드", "매장명", "점포명", "지점", "store"),
    "product_id": ("상품코드", "제품코드", "바코드", "product", "sku"),
    "product_name": ("상품명", "제품명", "품명"),
    "qty":        ("수량", "판매수량", "qty"),
    "unit_price": ("단가", "판매단가", "unit_price", "price"),
    "discount":   ("할인금액", "할인", "에누리", "discount"),
}
REQUIRED = {"daily": ("date", "store_id", "product_id", "qty"),
            "receipt": ("receipt_no", "sold_at", "product_id", "qty")}

_ENCODINGS = ("utf-8-sig", "cp949", "euc-kr", "utf-8")


def init() -> None:
    staging.init()
    db.executescript(DDL)


def _norm(col: str) -> str:
    return re.sub(r"[\s()\[\]/_-]", "", str(col)).lower()


def read_table(path: Path) -> pd.DataFrame:
    """CSV(cp949 포함)·엑셀을 가리지 않고 읽는다 — POS 내보내기의 현실."""
    path = Path(path)
    if path.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(path)
    last: Exception | None = None
    for enc in _ENCODINGS:
        try:
            with open(path, encoding=enc, newline="") as f:
                sample = f.read(4096)
                sep = ";" if sample.count(";") > sample.count(",") else ","
                if sample.count("\t") > max(sample.count(","), sample.count(";")):
                    sep = "\t"
            return pd.read_csv(path, encoding=enc, sep=sep)
        except (UnicodeDecodeError, UnicodeError) as e:
            last = e
    raise ValueError(f"인코딩을 해석하지 못했습니다({_ENCODINGS} 시도): {last}")


def auto_map(columns, adapter: str) -> tuple[dict, list]:
    """열 이름 → 표준 필드 자동 매핑. 반환: (매핑, 미충족 필수 필드)."""
    syn = SYNONYMS_DAILY if adapter == "daily" else SYNONYMS_RECEIPT
    mapping: dict[str, str] = {}
    for col in columns:
        n = _norm(col)
        for field, names in syn.items():
            if field in mapping.values():
                continue
            if any(_norm(s) in n or n in _norm(s) for s in names if len(_norm(s)) >= 2):
                mapping[str(col)] = field
                break
    missing = [f for f in REQUIRED[adapter] if f not in mapping.values()]
    return mapping, missing


def _dup_guard(sha: str) -> dict | None:
    row = db.one("SELECT upload_id, filename, uploaded_at FROM pos_uploads "
                 "WHERE file_sha256=?", (sha,))
    if row:
        return {"status": "duplicate", "upload_id": row["upload_id"],
                "message": f"같은 파일이 이미 반입됨({row['filename']}, {row['uploaded_at']}) — 건너뜀"}
    return None


def _double_count_check(dates_stores: set[tuple[str, str]]) -> list[str]:
    """Odoo 판매가 이미 있는 (날짜×매장)에 POS를 얹으면 이중 집계 — 경고."""
    warns = []
    for d, s in sorted(dates_stores)[:200]:
        n = db.scalar(
            "SELECT COUNT(*) FROM staging_sales WHERE order_date=? AND store_id=? "
            "AND _source NOT IN ('pos_daily','pos_receipt')", (d, str(s)))
        if n:
            warns.append(f"{d} 매장 {s}: Odoo 판매 {n}건과 중복 가능 — 판매 정본 확인 필요")
    if warns:
        common.alert("warn", "pos", f"이중 집계 위험 {len(warns)}건: " + "; ".join(warns[:3]))
    return warns


def ingest_daily(path: Path, by: str, channel: str = "pos") -> dict:
    """어댑터 ① 일별 정산 집계 → staging_sales.

    단가는 금액/수량으로 역산(할인 반영 후), promo_flag 는 할인>0.
    order_ref 는 POS/<영업일자>/<매장> — 원천 추적용.
    """
    init()
    path = Path(path)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if (dup := _dup_guard(sha)) is not None:
        return dup
    df = read_table(path)
    df, _ = strip_pii_columns(df, source=str(path))
    mapping, missing = auto_map(df.columns, "daily")
    if missing:
        return {"status": "needs_mapping", "missing": missing,
                "columns": [str(c) for c in df.columns],
                "message": f"필수 필드를 열에서 찾지 못함: {missing} — 열 이름을 알려 주세요."}
    inv = {v: k for k, v in mapping.items()}
    rows, errors = [], []
    for idx, r in df.iterrows():
        line = idx + 2
        try:
            d = pd.to_datetime(r[inv["date"]]).date().isoformat()
        except Exception:
            errors.append(f"{line}행 '{inv['date']}' 열: 날짜로 읽을 수 없음 ({r[inv['date']]})")
            continue
        try:
            qty = float(r[inv["qty"]])
        except Exception:
            errors.append(f"{line}행 '{inv['qty']}' 열: 수량이 숫자가 아님 ({r[inv['qty']]})")
            continue
        store = str(r[inv["store_id"]]).strip()
        prod = str(r[inv["product_id"]]).strip()
        if not store or not prod or pd.isna(r[inv["store_id"]]) or pd.isna(r[inv["product_id"]]):
            errors.append(f"{line}행: 매장/상품 비어 있음")
            continue
        amount = float(r[inv["amount"]]) if "amount" in inv and pd.notna(r.get(inv["amount"])) else None
        disc = float(r[inv["discount"]]) if "discount" in inv and pd.notna(r.get(inv["discount"])) else 0.0
        unit = round(amount / qty, 2) if amount and qty else None
        rows.append((None, f"POS/{d}/{store}", d, store, prod, qty, unit,
                     channel, 1 if disc > 0 else 0))
    return _commit(path, sha, "pos_daily", rows, errors, by)


def ingest_receipt(path: Path, by: str, channel: str = "pos") -> dict:
    """어댑터 ② 영수증 단위 거래 로그 → staging_sales (라인 그대로).

    order_ref 는 영수증번호 — 시간대 분석(M3)과 장바구니 분석의 재료가 된다.
    """
    init()
    path = Path(path)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if (dup := _dup_guard(sha)) is not None:
        return dup
    df = read_table(path)
    df, _ = strip_pii_columns(df, source=str(path))
    mapping, missing = auto_map(df.columns, "receipt")
    if missing:
        return {"status": "needs_mapping", "missing": missing,
                "columns": [str(c) for c in df.columns],
                "message": f"필수 필드를 열에서 찾지 못함: {missing} — 열 이름을 알려 주세요."}
    inv = {v: k for k, v in mapping.items()}
    rows, errors = [], []
    for idx, r in df.iterrows():
        line = idx + 2
        try:
            ts = pd.to_datetime(r[inv["sold_at"]])
            d = ts.date().isoformat()
        except Exception:
            errors.append(f"{line}행 '{inv['sold_at']}' 열: 일시로 읽을 수 없음 ({r[inv['sold_at']]})")
            continue
        try:
            qty = float(r[inv["qty"]])
        except Exception:
            errors.append(f"{line}행 '{inv['qty']}' 열: 수량이 숫자가 아님 ({r[inv['qty']]})")
            continue
        prod = str(r[inv["product_id"]]).strip()
        if not prod or pd.isna(r[inv["product_id"]]):
            errors.append(f"{line}행: 상품 비어 있음")
            continue
        ref = str(r[inv["receipt_no"]]).strip()
        store = str(r[inv["store_id"]]).strip() if "store_id" in inv else "S-POS"
        unit = float(r[inv["unit_price"]]) if "unit_price" in inv and pd.notna(r.get(inv["unit_price"])) else None
        disc = float(r[inv["discount"]]) if "discount" in inv and pd.notna(r.get(inv["discount"])) else 0.0
        rows.append((None, ref, d, store, prod, qty, unit, channel,
                     1 if disc > 0 else 0))
    return _commit(path, sha, "pos_receipt", rows, errors, by)


def _commit(path: Path, sha: str, adapter: str, rows: list, errors: list,
            by: str) -> dict:
    raw_ref = common.preserve_raw(Path(path), "pos")
    ts = common.now_iso()
    warns = _double_count_check({(r[2], r[3]) for r in rows})
    with db.conn() as c:
        c.executemany(
            "INSERT INTO staging_sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            [r + (ts, ts, adapter) for r in rows])
        cur = c.execute(
            "INSERT INTO pos_uploads (filename, file_sha256, adapter, rows_ok, "
            "rows_rejected, raw_ref, uploaded_by, uploaded_at) VALUES (?,?,?,?,?,?,?,?)",
            (Path(path).name, sha, adapter, len(rows), len(errors), raw_ref, by, ts))
        upload_id = cur.lastrowid
    if errors:
        common.alert("warn", "pos", f"{Path(path).name}: {len(errors)}행 거절 — 첫 오류: {errors[0]}")
    return {"status": "ok", "upload_id": upload_id, "adapter": adapter,
            "rows_ok": len(rows), "rows_rejected": len(errors),
            "errors": errors[:50], "double_count_warnings": warns[:10]}
