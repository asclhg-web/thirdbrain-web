"""고객사 프로파일 런타임 로더 — 생성기(M1 대체) 또는 온보딩이 기록한
config.DATA/profile.json 을 읽는다. 없으면 demo 기본값으로 동작한다.

변환(M2)·에이전트(M7)·E2E가 여기서 이름/주력 품목을 얻는다 — 코드에서
고객사 상수를 지우는 지점.
"""
from __future__ import annotations

import json

from . import config

_DEFAULT = {
    "profile": "demo", "company": "데모제과",
    "product_names": {"P-CREAM": "크림빵", "P-RED": "단팥빵", "P-BAG": "바게트",
                      "P-CAKE": "조각케이크", "P-SAND": "샌드위치", "P-PIE": "파이만쥬",
                      "P-CROI": "크루아상", "P-DONUT": "도넛"},
    "store_names": {"S-MAIN": "본점", "S-STATION": "역전점",
                    "B2B-MART": "마트 납품", "B2B-CAFE": "카페 납품"},
    "store_channels": {"S-MAIN": "retail", "S-STATION": "retail",
                       "B2B-MART": "B2B", "B2B-CAFE": "B2B"},
    "primary_pairs": [["S-MAIN", "P-CREAM"], ["S-MAIN", "P-PIE"],
                      ["B2B-MART", "P-CREAM"]],
    "primary_store": "S-MAIN", "primary_product": "P-CREAM",
    "alias_seed": [], "name2code": {},
    "plant": {"equipment": "OVEN-2", "material": "M-FLOUR", "vendor": "V2",
              "night_worker": "W-03"},
}


def load() -> dict:
    p = config.DATA / "profile.json"
    if p.exists():
        doc = json.loads(p.read_text(encoding="utf-8"))
        return {**_DEFAULT, **doc}
    return dict(_DEFAULT)


def company() -> str:
    return load()["company"]


def product_names() -> dict[str, str]:
    return load()["product_names"]


def store_names() -> dict[str, str]:
    return load()["store_names"]


def store_channels() -> dict[str, str]:
    return load()["store_channels"]


def primary_pairs() -> list[tuple[str, str]]:
    return [tuple(x) for x in load()["primary_pairs"]]


def primary_store() -> str:
    return load()["primary_store"]


def primary_product() -> str:
    return load()["primary_product"]


def alias_seed() -> list[tuple[str, str, str]]:
    return [tuple(x) for x in load()["alias_seed"]]


def name2code() -> dict[str, str]:
    return load()["name2code"]


def plant_equipment() -> str:
    return load()["plant"]["equipment"]
