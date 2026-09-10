"""공통 유틸 — 시각, 경보(사내 메신저 대체), 원본 보존."""
from __future__ import annotations

import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

from . import config, db

ALERT_DDL = """
CREATE TABLE IF NOT EXISTS alerts (
  alert_id  INTEGER PRIMARY KEY AUTOINCREMENT,
  level     TEXT NOT NULL CHECK (level IN ('info','warn','crit')),
  module    TEXT NOT NULL,
  message   TEXT NOT NULL,
  created_at TEXT NOT NULL
);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def alert(level: str, module: str, message: str) -> None:
    """경보 — demo: 테이블+stdout / prod: 사내 메신저 webhook 어댑터."""
    db.executescript(ALERT_DDL)
    db.execute(
        "INSERT INTO alerts (level, module, message, created_at) VALUES (?,?,?,?)",
        (level, module, message, now_iso()),
    )
    print(f"[ALERT/{level}] {module}: {message}")


def preserve_raw(src: Path, category: str) -> str:
    """원본 불변 보존(M1) — 내용 해시 이름으로 복사, 반환값은 원본 참조 키."""
    config.ensure_dirs()
    data = Path(src).read_bytes()
    sha = hashlib.sha256(data).hexdigest()[:16]
    dest_dir = config.RAW_DIR / category
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{sha}_{Path(src).name}"
    if not dest.exists():                      # 같은 내용은 한 번만 — 덮어쓰기 없음
        shutil.copy2(src, dest)
    return str(dest.relative_to(config.RAW_DIR))
