# Superset 자산 정의 (M3-3 prod 등록용)

demo의 정적 보드(field/exec/war_room.html)와 같은 지표를 Superset으로 올릴 때의
데이터셋·차트 정의. **지표 SQL은 계약의 정의를 그대로 쓴다** — 자체 계산 금지.

## 데이터베이스 연결

- `AXP PostgreSQL` — postgresql://axp@postgres:5432/axp (읽기 전용 계정 `axp_bi`)

## 데이터셋 (SQL Lab → Save as dataset)

| 이름 | SQL |
|---|---|
| ds_daily_scrap | `SELECT date_key, product_id, SUM(qty) qty FROM fact_inventory_move WHERE move_type='scrap' GROUP BY 1,2` |
| ds_daily_defect | `SELECT p.date_key, p.line_id, SUM(p.qty_planned) produced, COALESCE(SUM(d.qty_defect),0) defects FROM fact_production p LEFT JOIN fact_defect d USING (mo_ref) GROUP BY 1,2` |
| ds_daily_sales | `SELECT date_key, store_id, product_id, SUM(qty) qty, SUM(revenue) revenue FROM fact_sales GROUP BY 1,2,3` |
| ds_cards | `SELECT card_id, kind, agent, status, approver, created_at, decided_at FROM judgment_cards` |
| ds_quality | `SELECT report_date, ok, unmapped_rate FROM quality_reports` |
| ds_anomaly | `SELECT date_key, equipment_id, score, threshold, is_alert FROM anomaly_scores` |

## 현장 보드 (dashboard: AXP-현장)

1. Big Number — 오늘 폐기 (ds_daily_scrap, SUM(qty), 필터 오늘) · 비교: 어제
2. Big Number — 오늘 불량 (ds_daily_defect)
3. Table — 라인별 생산/불량/불량률 (ds_daily_defect, 조건부 서식 불량률>3%)
4. Time-series — 폐기 14일 추세 (ds_daily_scrap)

## 경영 보드 (dashboard: AXP-경영)

1. Big Number — 28일 매출 (ds_daily_sales SUM(revenue))
2. Big Number — 폐기율 = SUM(scrap)/(SUM(sales)+SUM(scrap)) — 목표선 4%
3. Big Number — 불량률 — 목표선 2%
4. Time-series — 월별 매출 (ds_daily_sales, 월 그레인)

## War Room (dashboard: AXP-WarRoom)

1. Big Number ×3 — 카드 총수/처리율/승인율 (ds_cards)
2. Pie — 반려 사유 분포 (reject_feedback 조인)
3. Table — 에이전트 가동·오류 (agent_runs)
4. Time-series — anomaly score vs threshold (ds_anomaly, 설비 필터)
5. Table — 드리프트 상위 (별도 뷰 필요 시 axp-api /warroom 사용)

권한: 현장 보드 = 전 역할, 경영 보드 = 리드·스튜어드·승인자 (auth-roles.md 매트릭스).
