"""M1-1 Odoo CDC 커넥터 — 6대 테이블 계열을 스테이징으로.

demo: 합성 Odoo DB(sqlite)를 증분 폴링(마지막 src_id 이후) — CDC 의미론 재현.
prod: PostgreSQL 논리 복제(wal_level=logical) — 구성 SQL은 odoo_cdc_prod.sql,
      본 모듈의 적재·정합 로직은 동일하게 재사용된다.

원칙: 원장에 쓰지 않는다. 스테이징에서 변환하지 않는다(원본 보존).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from .. import common, config, db
from . import staging

# Odoo 원천 테이블 → 스테이징 매핑 (demo 합성 스키마 기준, prod에서는 실제 컬럼명)
SERIES = {
    "sale_order_line":      ("staging_sales",
        "id, order_ref, order_date, store_id, product_id, qty, unit_price, channel, promo_flag, write_date"),
    "purchase_order_line":  ("staging_purchase",
        "id, po_ref, order_date, receipt_date, vendor_id, material_id, qty, unit_price, lot_id, write_date"),
    "stock_move":           ("staging_stock_move",
        "id, move_date, product_id, from_loc, to_loc, qty, move_type, lot_id, reason, write_date"),
    "mrp_production":       ("staging_mrp",
        "id, mo_ref, prod_date, product_id, line_id, worker_id, equipment_id, sop_id, qty_planned, qty_done, shift, write_date"),
    "quality_check":        ("staging_quality",
        "id, check_date, mo_ref, product_id, line_id, worker_id, equipment_id, material_lot_id, sop_id, defect_type, qty_defect, shift, memo, write_date"),
    "maintenance_request":  ("staging_maintenance",
        "id, event_date, equipment_id, event_type, duration_min, note, write_date"),
}


# P3: prod 적재 경로 — 논리 복제로 도착한 실테이블 위의 매핑 뷰(axp_prod.*,
# deploy/odoo17_prod_mapping.sql)를 증분 폴링해 스테이징으로 옮긴다.
# 뷰가 demo 스키마와 같은 모양·타입(text 캐스트)으로 투영하므로 하류는 동일.
PROD_SERIES = {
    "axp_prod.v_sales":         "staging_sales",
    "axp_prod.v_purchase":      "staging_purchase",
    "axp_prod.v_stock_move":    "staging_stock_move",
    "axp_prod.v_mrp":           "staging_mrp",
    "axp_prod.v_maintenance":   "staging_maintenance",
    "axp_prod.v_quality_scrap": "staging_quality",
}


def source_path() -> Path:
    return config.DATA / "odoo.db"          # demo 합성 Odoo


def sync(source: str = "odoo") -> dict[str, int]:
    """증분 동기화 — cdc_state의 last_src_id 이후 행만 가져온다(멱등)."""
    staging.init()
    counts: dict[str, int] = {}
    src = sqlite3.connect(source_path())
    src.row_factory = sqlite3.Row
    try:
        for otable, (stable, cols) in SERIES.items():
            # P2: 원천에 없는 테이블(모듈 미설치 고객)은 우아하게 건너뛴다 —
            # quality/maintenance 모듈이 없는 Odoo에서도 나머지 계열은 돈다(P-02).
            if not src.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                    (otable,)).fetchone():
                counts[stable] = -1   # 표식: 원천 테이블 없음
                continue
            last = db.scalar(
                "SELECT last_src_id FROM cdc_state WHERE table_name=?", (stable,)) or 0
            # P2-I11: 플랫폼이 만든 발주 '초안'(PO/AXP/*)은 재수집하지 않는다 —
            # 자기 산출물이 원천으로 되돌아오는 자기 환류 오염 차단.
            extra = (" AND (po_ref IS NULL OR po_ref NOT LIKE 'PO/AXP/%')"
                     if otable == "purchase_order_line" else "")
            rows = src.execute(
                f"SELECT {cols} FROM {otable} WHERE id > ?{extra} ORDER BY id", (last,)
            ).fetchall()
            if rows:
                ncols = len(rows[0])
                placeholders = ",".join(["?"] * (ncols + 2))
                ts = common.now_iso()
                db.executemany(
                    f"INSERT INTO {stable} VALUES ({placeholders})",
                    [tuple(r) + (ts, source) for r in rows],
                )
                db.execute(
                    "INSERT INTO cdc_state (table_name, last_src_id, last_run_at) VALUES (?,?,?) "
                    "ON CONFLICT(table_name) DO UPDATE SET last_src_id=excluded.last_src_id, "
                    "last_run_at=excluded.last_run_at",
                    (stable, rows[-1]["id"], ts),
                )
            counts[stable] = len(rows)
    finally:
        src.close()
    return counts


def sync_prod(source: str = "odoo_prod") -> dict[str, int]:
    """prod 증분 동기화 — 복제 매핑 뷰 → 스테이징 (PG 백엔드 전용, 멱등).

    demo sync()와 같은 cdc_state 체크포인트를 쓰므로 한 프로파일에서
    demo/prod를 섞지 않는 한 안전하다. 뷰가 없으면(복제 미구성) -1 표식.
    """
    if db.BACKEND != "postgres":
        raise RuntimeError("sync_prod는 PostgreSQL 백엔드 전용입니다 (AXP_DB=postgres)")
    staging.init()
    counts: dict[str, int] = {}
    for view, stable in PROD_SERIES.items():
        vschema, vname = view.split(".", 1)
        if not db.scalar(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema=? AND table_name=?", (vschema, vname)):
            counts[stable] = -1   # 매핑 뷰 없음(복제 미구성 또는 모듈 부재)
            continue
        st = db.one(
            "SELECT last_src_id, last_write_date FROM cdc_state WHERE table_name=?",
            (stable,))
        last = (st["last_src_id"] if st else 0) or 0
        last_wd = (st["last_write_date"] if st else None) or ""
        ts = common.now_iso()
        rows = db.query(f"SELECT * FROM {view} WHERE id > ? ORDER BY id", (last,))
        if rows:
            ncols = len(rows[0])
            placeholders = ",".join(["?"] * (ncols + 2))
            db.executemany(
                f"INSERT INTO {stable} VALUES ({placeholders})",
                [tuple(r.values()) + (ts, source) for r in rows])
        # P5-I5: 갱신 재수집 — 원장에서 제자리 갱신된 행(입고 후 로트 확정,
        # MO 완료 수량, 정비 종결 등)은 id 증분에 잡히지 않는다. write_date
        # 워터마크 이후 갱신된 기존 행을 다시 떠서 스테이징에서 대체한다.
        # (워터마크가 없는 기존 프로파일은 이번 실행에서 초기화만 되고,
        #  그 이전의 갱신은 전량 재동기화로만 따라잡는다 — 운영 문서에 명시)
        upd = []
        if last and last_wd:
            upd = db.query(
                f"SELECT * FROM {view} WHERE id <= ? AND write_date > ? ORDER BY id",
                (last, last_wd))
            if upd:
                ncols = len(upd[0])
                placeholders = ",".join(["?"] * (ncols + 2))
                for r in upd:
                    db.execute(f"DELETE FROM {stable} WHERE src_id=?", (r["id"],))
                db.executemany(
                    f"INSERT INTO {stable} VALUES ({placeholders})",
                    [tuple(r.values()) + (ts, source) for r in upd])
        new_last = rows[-1]["id"] if rows else last
        new_wd = db.scalar(f"SELECT MAX(write_date) FROM {view}") or last_wd or None
        db.execute(
            "INSERT INTO cdc_state (table_name, last_src_id, last_run_at, last_write_date) "
            "VALUES (?,?,?,?) "
            "ON CONFLICT(table_name) DO UPDATE SET last_src_id=excluded.last_src_id, "
            "last_run_at=excluded.last_run_at, last_write_date=excluded.last_write_date",
            (stable, new_last, ts, new_wd))
        counts[stable] = len(rows) + len(upd)
    return counts


def reconcile() -> dict:
    """야간 정합 배치 — 원장 대비 건수·수량 합계 대조. 오차는 경보."""
    src = sqlite3.connect(source_path())
    report, ok = [], True
    try:
        for otable, (stable, cols) in SERIES.items():
            if not src.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                    (otable,)).fetchone():
                continue   # 원천 테이블 없음(모듈 미설치) — sync와 동일 기준
            qty_col = "qty" if "qty," in cols or cols.endswith(", qty") else None
            if otable == "mrp_production":
                qty_col = "qty_done"
            if otable == "quality_check":
                qty_col = "qty_defect"
            if otable == "maintenance_request":
                qty_col = "duration_min"
            where = (" WHERE (po_ref IS NULL OR po_ref NOT LIKE 'PO/AXP/%')"
                     if otable == "purchase_order_line" else "")   # P2-I11 동일 기준
            o_cnt = src.execute(f"SELECT COUNT(*) FROM {otable}{where}").fetchone()[0]
            s_cnt = db.scalar(f"SELECT COUNT(*) FROM {stable}")
            row = {"series": stable, "odoo_count": o_cnt, "staging_count": s_cnt,
                   "count_diff": o_cnt - s_cnt}
            if qty_col:
                o_sum = src.execute(
                    f"SELECT COALESCE(SUM({qty_col}),0) FROM {otable}{where}").fetchone()[0]
                s_sum = db.scalar(f"SELECT COALESCE(SUM({qty_col}),0) FROM {stable}")
                row["qty_diff"] = round((o_sum or 0) - (s_sum or 0), 6)
            bad = row["count_diff"] != 0 or abs(row.get("qty_diff", 0)) > 1e-6
            row["ok"] = not bad
            if bad:
                ok = False
                common.alert("crit", "M1-1", f"정합 오차: {row}")
            report.append(row)
    finally:
        src.close()
    result = {"ok": ok, "series": report, "checked_at": common.now_iso()}
    db.executescript(
        "CREATE TABLE IF NOT EXISTS recon_log (run_at TEXT, ok INTEGER, detail TEXT)")
    import json
    db.execute("INSERT INTO recon_log VALUES (?,?,?)",
               (result["checked_at"], int(ok), json.dumps(report, ensure_ascii=False)))
    return result
