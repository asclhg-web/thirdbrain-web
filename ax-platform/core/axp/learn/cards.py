"""M4-1 모델 카드 레지스트리 — 카드 없는 모델은 배포 불가.

demo: 파일(pickle)+DB 레지스트리. prod: MLflow 어댑터가 같은 카드 규격을 태그로 강제.
필수 항목이 하나라도 빠지면 등록이 거부된다.
"""
from __future__ import annotations

import json
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .. import config, db

REQUIRED = ["model_id", "problem", "data_range", "features_ref", "algorithm",
            "params", "metrics", "validation_scheme", "version"]

DDL = """
CREATE TABLE IF NOT EXISTS model_cards (
  model_id TEXT NOT NULL, version TEXT NOT NULL,
  card TEXT NOT NULL,             -- JSON 전체 카드
  artifact_path TEXT,             -- 직렬화 모델 위치
  status TEXT NOT NULL DEFAULT 'registered'
         CHECK (status IN ('registered','serving','retired')),
  registered_at TEXT NOT NULL,
  PRIMARY KEY (model_id, version)
);
"""


class CardError(Exception):
    pass


def _models_dir() -> Path:
    d = config.ARTIFACTS / "models"
    d.mkdir(parents=True, exist_ok=True)
    return d


def register(card: dict[str, Any], model_obj: Any | None = None) -> dict:
    """카드 검증 → 모델 직렬화 → 등록. 필수 항목 누락 시 CardError."""
    db.executescript(DDL)
    missing = [k for k in REQUIRED if k not in card or card[k] in (None, "", {})]
    if missing:
        raise CardError(f"모델 카드 필수 항목 누락: {missing} — 등록 거부")
    if "metrics" in card and not isinstance(card["metrics"], dict):
        raise CardError("metrics는 {지표: 값} 형식이어야 한다")
    path = None
    if model_obj is not None:
        path = _models_dir() / f"{card['model_id']}_{card['version']}.pkl"
        with open(path, "wb") as f:
            pickle.dump(model_obj, f)
        path = str(path)
    db.execute(
        "INSERT OR REPLACE INTO model_cards VALUES (?,?,?,?,?,?)",
        (card["model_id"], card["version"], json.dumps(card, ensure_ascii=False),
         path, "registered",
         datetime.now(timezone.utc).isoformat(timespec="seconds")))
    return {"model_id": card["model_id"], "version": card["version"], "artifact": path}


def promote(model_id: str, version: str) -> None:
    """serving 승격 — 같은 model_id의 기존 serving은 retired."""
    db.executescript(DDL)
    if db.one("SELECT 1 FROM model_cards WHERE model_id=? AND version=?",
              (model_id, version)) is None:
        raise CardError(f"미등록 모델 {model_id}:{version} — 카드 없는 모델은 배포 불가")
    db.execute("UPDATE model_cards SET status='retired' "
               "WHERE model_id=? AND status='serving'", (model_id,))
    db.execute("UPDATE model_cards SET status='serving' "
               "WHERE model_id=? AND version=?", (model_id, version))


def serving(model_id: str) -> tuple[dict, Any]:
    """서빙 모델 로드 — 카드와 모델 객체."""
    db.executescript(DDL)
    row = db.one("SELECT * FROM model_cards WHERE model_id=? AND status='serving'",
                 (model_id,))
    if row is None:
        row = db.one("SELECT * FROM model_cards WHERE model_id=? "
                     "ORDER BY registered_at DESC LIMIT 1", (model_id,))
    if row is None:
        raise CardError(f"모델 없음: {model_id}")
    card = json.loads(row["card"])
    obj = None
    if row["artifact_path"]:
        with open(row["artifact_path"], "rb") as f:
            obj = pickle.load(f)
    return card, obj


def get_card(model_id: str, version: str | None = None) -> dict | None:
    db.executescript(DDL)
    if version:
        row = db.one("SELECT card FROM model_cards WHERE model_id=? AND version=?",
                     (model_id, version))
    else:
        row = db.one("SELECT card FROM model_cards WHERE model_id=? "
                     "ORDER BY registered_at DESC LIMIT 1", (model_id,))
    return json.loads(row["card"]) if row else None


def listing() -> list[dict]:
    db.executescript(DDL)
    return db.query("SELECT model_id, version, status, registered_at FROM model_cards "
                    "ORDER BY model_id, registered_at")
