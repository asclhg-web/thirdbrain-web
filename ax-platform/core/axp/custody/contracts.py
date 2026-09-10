"""데이터 계약 로더 (M0-3/M2) — registry/contracts/*.yaml 을 읽고 검증한다.

계약 우선 원칙: 계약 없는 테이블은 품질 게이트(M2)가 거부하고,
노트북(M3)·학습(M4)은 계약에 있는 테이블·특징만 쓴다.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from .. import config

REQUIRED_KEYS = {"name", "kind", "owner", "version", "update_cycle", "columns"}
REQUIRED_COL_KEYS = {"name", "type"}


class ContractError(Exception):
    pass


def contract_dir() -> Path:
    return Path(config.REGISTRY) / "contracts"


def load(name: str) -> dict:
    path = contract_dir() / f"{name}.yaml"
    if not path.exists():
        raise ContractError(f"계약 없음: {name} — 계약 없는 연결은 배포하지 않는다")
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    validate(doc, name)
    return doc


def load_all() -> dict[str, dict]:
    out = {}
    for p in sorted(contract_dir().glob("*.yaml")):
        doc = yaml.safe_load(p.read_text(encoding="utf-8"))
        validate(doc, p.stem)
        out[p.stem] = doc
    return out


def validate(doc: dict, name: str) -> None:
    missing = REQUIRED_KEYS - set(doc)
    if missing:
        raise ContractError(f"{name}: 필수 항목 누락 {sorted(missing)}")
    for col in doc["columns"]:
        cmissing = REQUIRED_COL_KEYS - set(col)
        if cmissing:
            raise ContractError(f"{name}.{col.get('name','?')}: 컬럼 항목 누락 {sorted(cmissing)}")


def quality_rules(name: str) -> list[dict]:
    """계약의 컬럼 규칙 → 품질 게이트(M2)가 실행할 검사 목록."""
    doc = load(name)
    rules: list[dict] = []
    for col in doc["columns"]:
        c = col["name"]
        if col.get("required"):
            rules.append({"table": name, "column": c, "check": "not_null"})
        if "min" in col or "max" in col:
            rules.append({"table": name, "column": c, "check": "range",
                          "min": col.get("min"), "max": col.get("max")})
        if col.get("ref"):
            ref_t, ref_c = col["ref"].split(".")
            rules.append({"table": name, "column": c, "check": "ref",
                          "ref_table": ref_t, "ref_column": ref_c})
        if col.get("unique"):
            rules.append({"table": name, "column": c, "check": "unique"})
    return rules
