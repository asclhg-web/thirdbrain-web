"""개방 포맷 내보내기 (인터페이스 원칙 ②) — 사실·차원 테이블을 Parquet으로.

"특정 모듈이 죽어도 데이터는 읽힌다" — SQLite/PostgreSQL이 없어도 Parquet은
어디서든 열린다. 야간 배치가 매일 갱신하고, 자산 대장에 위치를 남긴다.
prod: 같은 함수가 MinIO(s3://parquet)로 쓴다.
"""
from __future__ import annotations

from pathlib import Path

from .. import config, db

TABLES = ["fact_sales", "fact_production", "fact_procurement",
          "fact_inventory_move", "fact_defect", "fact_equipment_event",
          "fact_sensor_daily", "dim_calendar", "dim_product", "dim_store",
          "dim_worker", "dim_equipment", "dim_material_lot", "dim_sop", "dim_promo"]


def export_parquet(out_dir: Path | None = None) -> dict[str, int]:
    out = Path(out_dir) if out_dir else (config.DATA / "parquet")
    out.mkdir(parents=True, exist_ok=True)
    counts = {}
    for t in TABLES:
        if not db.table_exists(t):
            continue
        frame = db.df(f"SELECT * FROM {t}")
        frame.to_parquet(out / f"{t}.parquet", index=False)
        counts[t] = len(frame)
    from ..custody import ledger
    ledger.register("parquet_export", "dataset", str(out), "데이터 엔지니어",
                    note=f"{len(counts)}개 테이블, 개방 포맷 사본")
    return counts
