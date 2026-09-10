"""고객사 프로파일 — 온보딩의 실체. 회사의 실제 구조(매장·제품·어휘)를 선언하면
생성기·변환·에이전트가 그 구조로 돈다. 실데이터 전환 시 이 프로파일은 그대로
남고 원천(M1)만 합성 → 실제로 바뀐다.

선택: 환경변수 AXP_PROFILE (demo | taesungdang). 기본 demo.

태성당 프로파일 출처: 제안서 작업에서 확인된 공개 사실(1950년 창업 부산 초량
본점, 파이만쥬 주력, 별빛샌드 부산/대구, 선물·납품 수요). 거래 수치는 전부
합성이며, <확인 필요> 항목은 docs/onboarding-taesungdang.md의 자료 요청서로
확정한다. 제품·설비 ID 체계는 demo와 동일하게 유지 — 회귀 질의·계약이 그대로
통한다(이름만 고객사 어휘).
"""
from __future__ import annotations

import os

PROFILES: dict[str, dict] = {
    # ── 일반 데모(가상 제빵회사) — 기존 동작 그대로 ─────────────────
    "demo": {
        "company": "데모제과",
        "products": {   # id: (이름, 기본 일판매(주력 매장), 계절 진폭, 단가)
            "P-CREAM": ("크림빵", 120, 0.10, 1800),
            "P-RED":   ("단팥빵", 100, 0.15, 1700),
            "P-BAG":   ("바게트", 60, 0.05, 3500),
            "P-CAKE":  ("조각케이크", 45, 0.30, 4500),
            "P-SAND":  ("샌드위치", 80, 0.08, 4200),
            "P-PIE":   ("파이만쥬", 150, 0.25, 1500),
            "P-CROI":  ("크루아상", 70, 0.12, 2800),
            "P-DONUT": ("도넛", 90, 0.10, 2000),
        },
        "stores": {     # id: (이름, 채널, 수요 배율, 제외 품목)
            "S-MAIN":    ("본점", "retail", 1.0, []),
            "S-STATION": ("역전점", "retail", 0.65, []),
            "B2B-MART":  ("마트 납품", "B2B", 1.6, []),
            "B2B-CAFE":  ("카페 납품", "B2B", 0.5, ["P-CAKE", "P-PIE"]),
        },
        "line_of": {"P-CREAM": "L1", "P-RED": "L1", "P-CROI": "L1", "P-DONUT": "L1"},
        "default_line": "L2",
        "ovens": {"L1": "OVEN-1", "L2": "OVEN-2"},
        "sops": {"P-CREAM": "SOP-BUN-01", "P-RED": "SOP-BUN-01", "P-BAG": "SOP-BREAD-02",
                 "P-CAKE": "SOP-CAKE-03", "P-SAND": "SOP-COLD-04", "P-PIE": "SOP-PIE-05",
                 "P-CROI": "SOP-LAM-06", "P-DONUT": "SOP-FRY-07"},
        "materials": {"M-FLOUR": "밀가루", "M-SUGAR": "설탕", "M-BUTTER": "버터",
                      "M-CREAM": "생크림", "M-REDBEAN": "팥앙금"},
        "vendors": {"M-FLOUR": ["V1", "V2"], "M-SUGAR": ["V3"], "M-BUTTER": ["V4"],
                    "M-CREAM": ["V4"], "M-REDBEAN": ["V5"]},
        "plant": {"equipment": "OVEN-2", "material": "M-FLOUR", "vendor": "V2",
                  "night_worker": "W-03"},
        "holiday_products": ["P-PIE", "P-CAKE"],
        "primary_pairs": [["S-MAIN", "P-CREAM"], ["S-MAIN", "P-PIE"],
                          ["B2B-MART", "P-CREAM"]],
        "primary_store": "S-MAIN", "primary_product": "P-CREAM",
        "alias_seed": [
            ["store", "본점", "S-MAIN"], ["store", "역전점", "S-STATION"],
            ["store", "마트납품", "B2B-MART"], ["store", "카페납품", "B2B-CAFE"],
            ["product", "크림빵", "P-CREAM"], ["product", "단팥빵", "P-RED"],
            ["product", "파이만쥬", "P-PIE"],
        ],
        "name2code": {"바게트": "P-BAG", "조각케이크": "P-CAKE", "샌드위치": "P-SAND",
                      "크루아상": "P-CROI", "도넛": "P-DONUT"},
    },

    # ── 주식회사 태성당 (부산 초량, 1950) — 구조는 실제, 거래는 합성 ────
    "taesungdang": {
        "company": "주식회사 태성당",
        "products": {
            # 파이만쥬 — 주력·선물 수요(명절 급증 큼)
            "P-PIE":   ("파이만쥬", 260, 0.30, 1500),
            # 별빛샌드 — 부산/대구 매장 주력 과자 <구성·단가 확인 필요>
            "P-SAND":  ("별빛샌드", 140, 0.15, 2500),
            "P-RED":   ("단팥빵", 90, 0.12, 1800),
            "P-CREAM": ("크림빵", 80, 0.10, 1800),
            "P-CAKE":  ("카스테라", 50, 0.20, 6500),   # <품목 확인 필요>
            "P-BAG":   ("우유식빵", 45, 0.05, 3800),   # <품목 확인 필요>
        },
        "stores": {
            "S-CHORYANG": ("초량 본점", "retail", 1.0, []),
            "S-STAR-BS":  ("별빛샌드 부산점", "retail", 0.7, ["P-CAKE", "P-BAG"]),
            "S-STAR-DG":  ("별빛샌드 대구점", "retail", 0.55, ["P-CAKE", "P-BAG"]),
            "B2B-GIFT":   ("선물세트·기업 납품", "B2B", 1.3, ["P-BAG"]),  # <채널 확인 필요>
        },
        "line_of": {"P-RED": "L1", "P-CREAM": "L1", "P-CAKE": "L1", "P-BAG": "L1"},
        "default_line": "L2",                        # L2 = 파이만쥬·별빛샌드 라인
        "ovens": {"L1": "OVEN-1", "L2": "OVEN-2"},
        "sops": {"P-PIE": "SOP-PIE-05", "P-SAND": "SOP-SAND-01", "P-RED": "SOP-BUN-01",
                 "P-CREAM": "SOP-BUN-01", "P-CAKE": "SOP-CAST-02", "P-BAG": "SOP-BREAD-02"},
        "materials": {"M-FLOUR": "밀가루", "M-REDBEAN": "팥앙금", "M-SUGAR": "설탕",
                      "M-BUTTER": "버터", "M-EGG": "계란"},
        "vendors": {"M-FLOUR": ["V1"], "M-REDBEAN": ["V2", "V5"], "M-SUGAR": ["V3"],
                    "M-BUTTER": ["V4"], "M-EGG": ["V6"]},
        # 심은 검증 시나리오: 파이만쥬 라인(OVEN-2) × 팥앙금 V2 로트 — 실데이터
        # 전환 시 이 절은 사라지고 실제 불량 데이터가 그 자리를 채운다
        "plant": {"equipment": "OVEN-2", "material": "M-REDBEAN", "vendor": "V2",
                  "night_worker": "W-03"},
        "holiday_products": ["P-PIE", "P-SAND"],     # 명절 선물 수요
        "primary_pairs": [["S-CHORYANG", "P-PIE"], ["B2B-GIFT", "P-PIE"],
                          ["S-STAR-BS", "P-SAND"]],
        "primary_store": "S-CHORYANG", "primary_product": "P-PIE",
        "alias_seed": [
            ["store", "본점", "S-CHORYANG"], ["store", "초량", "S-CHORYANG"],
            ["store", "부산점", "S-STAR-BS"], ["store", "대구점", "S-STAR-DG"],
            ["store", "선물납품", "B2B-GIFT"],
            ["product", "파이만쥬", "P-PIE"], ["product", "만쥬", "P-PIE"],
            ["product", "별빛샌드", "P-SAND"], ["product", "샌드", "P-SAND"],
            ["product", "단팥빵", "P-RED"], ["product", "크림빵", "P-CREAM"],
        ],
        "name2code": {"카스테라": "P-CAKE", "우유식빵": "P-BAG"},
    },
}


def active_name() -> str:
    return os.environ.get("AXP_PROFILE", "demo")


def active() -> dict:
    return PROFILES[active_name()]
