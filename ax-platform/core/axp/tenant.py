"""P4-1: 체험/고객 테넌트 프로비저닝 — 생성·리셋·파기·업로드 파기 원커맨드.

테넌트 = 독립 데이터 루트(AXP_DATA) 하나. 프로파일=스키마 분리 구조(P2)를
그대로 쓰므로, 테넌트를 만든다는 것은 템플릿 데이터 루트를 복제하고
프로파일을 그 고객 이름으로 바꾸는 일이다.

원칙:
- 체험 테넌트는 합성 데이터 템플릿에서 출발한다(고객 실데이터 아님).
- 파기(destroy)는 디렉터리와 PG 스키마를 함께 지운다 — P3-I7(스키마 잔류)의
  재발 방지가 여기 내장된다.
- purge_uploads 는 체험 고객이 올린 원본 파일을 시효(기본 24h) 뒤 지운다 —
  4단계 정직 조항("체험 파일 24시간 내 자동 파기")의 구현체다.
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from . import config

# 테넌트 루트: ax-platform/tenants/<이름>/out (환경변수로 재지정 가능)
import os

_AX_ROOT = Path(__file__).resolve().parents[2]      # …/ax-platform
TENANTS_ROOT = Path(os.environ.get("AXP_TENANTS_ROOT", str(_AX_ROOT / "tenants")))
DEFAULT_TEMPLATE = _AX_ROOT / "customers" / "taesungdang" / "out"

_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,30}$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _root(name: str) -> Path:
    return TENANTS_ROOT / name


def data_dir(name: str) -> Path:
    return _root(name) / "out"


def _schema_for(path: Path) -> str:
    return "ax_" + hashlib.md5(str(path).encode()).hexdigest()[:12]


def _drop_pg_schema(path: Path) -> bool:
    """PG 백엔드면 해당 데이터 루트의 스키마를 함께 파기 (P3-I7 재발 방지)."""
    if os.environ.get("AXP_DB", "sqlite") != "postgres":
        return False
    try:
        import psycopg
        dsn = os.environ.get("AXP_PG_DSN",
                             "host=127.0.0.1 user=axp password=axp dbname=axp")
        with psycopg.connect(dsn, autocommit=True) as c:
            # 식별자 검증(md5 hex 12자) 후 안전한 포맷 — LIKE 함정(P3-I8) 없음
            schema = _schema_for(path)
            if not re.fullmatch(r"ax_[0-9a-f]{12}", schema):
                return False
            c.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
        return True
    except Exception:
        return False


def _meta_path(name: str) -> Path:
    return _root(name) / "tenant.json"


def _reset_web_accounts(dst: Path) -> None:
    """P4-I1: 템플릿에 묻어온 웹 계정(axp_users)을 지운다 — 지우지 않으면
    부트스트랩이 건너뛰어 새 테넌트 비밀번호가 통하지 않는다(실측 적발).
    sqlite 데이터 루트만 해당(PG는 경로가 다르면 스키마 자체가 새로 생긴다)."""
    dbf = dst / "axp.db"
    if dbf.exists():
        import sqlite3
        con = sqlite3.connect(dbf)
        try:
            con.execute("DROP TABLE IF EXISTS axp_users")
            con.execute("DROP TABLE IF EXISTS axp_sessions")
            con.commit()
        finally:
            con.close()


def create(name: str, company: str | None = None,
           template: Path | None = None, trial: bool = True) -> dict:
    """테넌트 생성 — 템플릿 복제 + 프로파일 개명 + 체험 계정 발급."""
    if not _NAME_RE.match(name):
        raise ValueError("테넌트 이름은 소문자·숫자·하이픈 2~31자입니다 (예: bakery-t)")
    if _root(name).exists():
        raise ValueError(f"테넌트 '{name}' 이미 존재 — reset 또는 destroy 하세요")
    template = Path(template or DEFAULT_TEMPLATE)
    if not template.exists():
        raise ValueError(f"템플릿 없음: {template}")
    dst = data_dir(name)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template, dst)

    # 프로파일 개명 — 화면·브리핑의 회사명이 이 값을 따른다
    prof_path = dst / "profile.json"
    prof = json.loads(prof_path.read_text(encoding="utf-8")) if prof_path.exists() else {}
    prof["company"] = company or f"{name} (체험)"
    prof["profile"] = name
    if trial:
        prof["trial"] = True     # 웹앱 워터마크(P4-2)가 이 플래그를 읽는다
    prof_path.write_text(json.dumps(prof, ensure_ascii=False, indent=2), encoding="utf-8")
    _reset_web_accounts(dst)

    # 체험 계정 — 무작위 비밀번호, 파일은 0600 (웹앱 부트스트랩과 동일 규약)
    pw = secrets.token_urlsafe(9)
    cred = _root(name) / "initial-credentials.txt"
    cred.write_text(f"admin / {pw}\n(최초 로그인 후 비밀번호를 바꾸세요)\n", encoding="utf-8")
    cred.chmod(0o600)

    meta = {"name": name, "company": prof["company"], "trial": trial,
            "template": str(template), "created_at": _now(),
            "data_dir": str(dst), "bootstrap_pw": pw}
    _meta_path(name).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    _meta_path(name).chmod(0o600)
    return {k: v for k, v in meta.items() if k != "bootstrap_pw"} | {
        "credentials_file": str(cred)}


def reset(name: str) -> dict:
    """리셋 — 템플릿에서 재복제(매일 0시 크론용). 계정·메타는 유지."""
    meta_p = _meta_path(name)
    if not meta_p.exists():
        raise ValueError(f"테넌트 '{name}' 없음")
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    dst = data_dir(name)
    _drop_pg_schema(dst)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(Path(meta["template"]), dst)
    prof_path = dst / "profile.json"
    prof = json.loads(prof_path.read_text(encoding="utf-8")) if prof_path.exists() else {}
    prof["company"] = meta["company"]
    prof["profile"] = name
    if meta.get("trial"):
        prof["trial"] = True
    prof_path.write_text(json.dumps(prof, ensure_ascii=False, indent=2), encoding="utf-8")
    _reset_web_accounts(dst)
    meta["last_reset_at"] = _now()
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"name": name, "reset_at": meta["last_reset_at"]}


def destroy(name: str) -> dict:
    """파기 — 디렉터리 + PG 스키마를 함께 지운다."""
    root = _root(name)
    if not root.exists():
        raise ValueError(f"테넌트 '{name}' 없음")
    dropped = _drop_pg_schema(data_dir(name))
    shutil.rmtree(root)
    return {"name": name, "destroyed_at": _now(), "pg_schema_dropped": dropped}


def purge_uploads(name: str, hours: float = 24.0) -> dict:
    """체험 업로드 원본 파기 — raw/ 아래 시효 지난 파일 삭제(정직 조항 구현)."""
    raw = data_dir(name) / "raw"
    if not raw.exists():
        return {"name": name, "purged": 0}
    cutoff = time.time() - hours * 3600
    purged = []
    for f in raw.rglob("*"):
        if f.is_file() and f.stat().st_mtime < cutoff:
            f.unlink()
            purged.append(str(f.relative_to(raw)))
    return {"name": name, "purged": len(purged), "files": purged[:20]}


def listing() -> list[dict]:
    if not TENANTS_ROOT.exists():
        return []
    out = []
    for p in sorted(TENANTS_ROOT.iterdir()):
        mp = p / "tenant.json"
        if mp.exists():
            m = json.loads(mp.read_text(encoding="utf-8"))
            m.pop("bootstrap_pw", None)
            m["size_mb"] = round(sum(
                f.stat().st_size for f in p.rglob("*") if f.is_file()) / 1e6, 1)
            out.append(m)
    return out
