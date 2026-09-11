"""자산 대장 (M0-3) — 데이터셋·스크립트·모델·문서의 소유자/버전/위치/갱신 이력.

커스터디 헌장 1조(산출물 귀속)의 실체: 여기 등록되지 않은 산출물은 자산이 아니다.
"""
from __future__ import annotations

from datetime import datetime, timezone

from .. import db

DDL = """
CREATE TABLE IF NOT EXISTS asset_ledger (
  asset_id   TEXT NOT NULL,
  version    TEXT NOT NULL,
  kind       TEXT NOT NULL CHECK (kind IN ('dataset','script','model','document','workflow')),
  location   TEXT NOT NULL,
  owner      TEXT NOT NULL,
  note       TEXT DEFAULT '',
  updated_at TEXT NOT NULL,
  PRIMARY KEY (asset_id, version)
);
"""


def init() -> None:
    db.executescript(DDL)


def register(asset_id: str, kind: str, location: str, owner: str,
             version: str = "v1", note: str = "") -> dict:
    init()
    row = {
        "asset_id": asset_id, "version": version, "kind": kind,
        "location": location, "owner": owner, "note": note,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    db.execute(
        "INSERT OR REPLACE INTO asset_ledger "
        "(asset_id, version, kind, location, owner, note, updated_at) "
        "VALUES (:asset_id, :version, :kind, :location, :owner, :note, :updated_at)",
        row,
    )
    return row


def latest(asset_id: str) -> dict | None:
    init()
    return db.one(
        "SELECT * FROM asset_ledger WHERE asset_id=? "
        "ORDER BY updated_at DESC, version DESC LIMIT 1",
        (asset_id,),
    )


def listing(kind: str | None = None) -> list[dict]:
    init()
    if kind:
        return db.query(
            "SELECT * FROM asset_ledger WHERE kind=? ORDER BY asset_id, updated_at",
            (kind,),
        )
    return db.query("SELECT * FROM asset_ledger ORDER BY asset_id, updated_at")
