"""프로필 (G06) — 한 사람이 여러 그래프(개인·기업·투자·가족)를 소유한다.

격리 원칙: 프로필 = 별도 DB 파일. 가장 강한 격리이자 유산 헌장 제4원칙
(이동 가능한 패키지)의 실현 — 프로필 하나가 곧 상속 단위다.
레지스트리는 사람이 읽을 수 있는 JSON 파일(data/profiles.json)에 둔다.
"""
import json
import os
import re
from datetime import datetime

from graph_core import store

KINDS = ["personal", "business", "investment", "family"]


def _registry_path() -> str:
    base = os.path.dirname(os.path.abspath(
        os.environ.get("PB_DB", store.db_path())))
    return os.path.join(base, "profiles.json")


def _load() -> dict:
    p = _registry_path()
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    # 최초: 현재 DB를 '기본(개인)' 프로필로 등록
    reg = {"active": "default",
           "profiles": [{"id": "default", "name": "기본(개인)", "kind": "personal",
                         "db": None, "created_at": datetime.now().isoformat()}]}
    _save(reg)
    return reg


def _save(reg: dict) -> None:
    p = _registry_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)


def list_profiles() -> list[dict]:
    reg = _load()
    return [{**pr, "active": pr["id"] == reg["active"]} for pr in reg["profiles"]]


def active() -> dict:
    reg = _load()
    return next(p for p in reg["profiles"] if p["id"] == reg["active"])


def create(name: str, kind: str = "personal") -> dict:
    assert kind in KINDS, f"unknown kind {kind}"
    reg = _load()
    pid = re.sub(r"[^\w가-힣]+", "-", name.strip()).strip("-") or "profile"
    if any(p["id"] == pid for p in reg["profiles"]):
        pid = f"{pid}-{len(reg['profiles'])}"
    db = os.path.join(os.path.dirname(_registry_path()), f"brain-{pid}.db")
    prof = {"id": pid, "name": name, "kind": kind, "db": db,
            "created_at": datetime.now().isoformat()}
    reg["profiles"].append(prof)
    _save(reg)
    return prof


def activate(profile_id: str) -> dict:
    """프로필 전환 — DB 연결을 해당 프로필 파일로 교체 (완전 격리)."""
    reg = _load()
    prof = next((p for p in reg["profiles"] if p["id"] == profile_id), None)
    if not prof:
        raise ValueError(f"프로필 없음: {profile_id}")
    reg["active"] = profile_id
    _save(reg)
    store.set_db_path(prof["db"])  # None(기본)이면 env/기본 경로로
    store.reset_conn()
    return prof
