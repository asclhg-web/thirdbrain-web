"""실행 모드·경로 설정 (M0).

demo(기본): SQLite + 로컬 파일 — 외부 서비스 없이 전 파이프라인이 돈다.
prod: PostgreSQL·MinIO·Neo4j·Ollama — 환경변수로 접속 정보를 받는다.
코어 로직은 두 모드에서 동일하다.
"""
from __future__ import annotations

import os
from pathlib import Path

MODE = os.environ.get("AXP_MODE", "demo")

# 데이터 루트: demo/out (저장소 밖 산출물이면 AXP_DATA로 재지정)
_default_root = Path(__file__).resolve().parents[2] / "demo" / "out"
DATA = Path(os.environ.get("AXP_DATA", str(_default_root)))

DB_PATH = DATA / "axp.db"            # demo: 스테이징·표준·운영 테이블이 한 파일
RAW_DIR = DATA / "raw"               # 원본 불변 보존(M1) — prod에서는 MinIO
ARTIFACTS = DATA / "artifacts"       # 모델·리포트·보드
REGISTRY = Path(os.environ.get(
    "AXP_REGISTRY", str(Path(__file__).resolve().parents[2] / "registry")))

TZ = os.environ.get("AXP_TZ", "Asia/Seoul")

# 반출 게이트가 허용하는 외부 목적지(M0-3) — 그 외는 차단
EXPORT_ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("EXPORT_ALLOWED_HOSTS", "").split(",") if h.strip()
]


def ensure_dirs() -> None:
    for p in (DATA, RAW_DIR, ARTIFACTS):
        p.mkdir(parents=True, exist_ok=True)
