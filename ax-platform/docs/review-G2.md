# 표준 스키마 규격 승인 심사 (G2)

심사 대상: registry/contracts 계약 6+1건. 판정: 항목별 — '대체로 양호' 금지.

## 심사 체크리스트 (데모 구축분 자체 심사 결과)

| 계열 | 완전성¹ | 4M 키 | 시점 키 | 원천 매핑 | 품질 규칙 | 소유자 | 판정 |
|---|---|---|---|---|---|---|---|
| fact_sales | ✔ | 해당 없음² | ✔ | ✔ staging_sales | ✔ 4건 | ✔ | **승인** |
| fact_production | ✔ | ✔ Man·Machine·Method | ✔ +shift | ✔ staging_mrp | ✔ 7건 | ✔ | **승인** |
| fact_procurement | ✔ | ✔ Material(lot) | ✔ | ✔ staging_purchase | ✔ 6건 | ✔ | **승인** |
| fact_inventory_move | ✔ | 해당 없음² | ✔ | ✔ staging_stock_move | ✔ 4건 | ✔ | **승인** |
| fact_defect | ✔ | ✔ **4M 전부** | ✔ +shift | ✔ quality+mrp 조인 | ✔ 9건 | ✔ | **승인** |
| fact_equipment_event | ✔ | ✔ Machine | ✔ | ✔ staging_maintenance | ✔ 4건 | ✔ | **승인** |
| features_demand | ✔ | — | ✔ as_of | ✔ 20종 정의 사전 | 시점 안전 시험 | ✔ | **승인** |

¹ 완전성 = 컬럼·타입·단위·허용범위·갱신주기·품질규칙·소유자 전부 기재
² 판매·이동은 4M 사실이 아니라 수요·물류 사실 — 제품·매장·시점 키가 완전성 기준

## 자동 강제 확인

- 계약 로더가 필수 항목 누락 시 ContractError로 거부 (test_dataset.py 통과)
- 품질 게이트가 계약의 규칙에서 검사 자동 생성 — 계약 없는 테이블은 게이트 불통과
- 미매핑률 0.16% (기준 5%) · 격리 큐 확정 플로 실증

## 조치 목록

| 항목 | 내용 | 담당 | 기한 |
|---|---|---|---|
| (실 고객사 적용 시) | 현장 코드 사전 초기 시드(codemap.SEED)를 실 별칭으로 교체 | 스튜어드 | 5주차 |
| (실 고객사 적용 시) | 단위(EA/KG) 실측 검증 — 계약의 unit과 현장 단위 대조 | 데이터 엔지니어 | 5주차 |

**판정 초안: 승인 (조건부 항목은 실 고객사 전개 시 재확인)** — 최종 판정·서명은 회의에서.
