-- P3-2: 실 Odoo 17 스키마 → AXP 스테이징 계열 매핑 뷰 (P-02 완결)
-- 실행 위치: 플랫폼 PostgreSQL(구독자 측) — 복제로 도착한 public.* 실테이블 위에
--   스테이징 계열과 같은 모양의 읽기 전용 뷰를 얹는다.
-- 원칙: 원장에 쓰기 없음. 뷰는 변환하지 않는 원본 투영이며, 코드값 표준화는
--   M2 codemap(격리 큐)이 담당한다.
--
-- 실측 근거: Odoo 17.0 Community (2026-09-11, PG16, 모듈: sale_management,
--   purchase, stock, mrp, maintenance / quality_*는 Enterprise 전용으로 부재).
-- 컬럼 차이 매트릭스(합성 demo 스키마 → 실 Odoo 17):
--   qty        → sale: product_uom_qty · purchase: product_qty · stock: product_uom_qty
--   order_ref  → sale_order.name (JOIN order_id) · po_ref → purchase_order.name (JOIN order_id)
--   order_date → sale_order.date_order · purchase_order.date_order (라인에는 날짜 없음)
--   store_id   → sale_order.warehouse_id (다점포는 창고=매장 규약)
--   channel    → sale_order.team_id (판매팀=채널 규약)
--   promo_flag → discount > 0 파생 (Community에는 프로모션 모듈 없음)
--   product_id → default_code 투영(P5-D2 v_product_code) — 없으면 이름→id 폴백
--   equipment_id/보전 → maintenance_request.equipment_id · event_type → maintenance_type
--   mrp: qty_planned → product_qty · qty_done → qty_producing (완료 시점) · line_id 없음(작업장은 mrp_workorder)

CREATE SCHEMA IF NOT EXISTS axp_prod;

-- P5-D2: 품목 id → 코드 투영 헬퍼 — default_code가 있으면 그것(P-PIE 등),
--   없으면 이름(번역 jsonb의 en_US → 아무 값), 최후엔 숫자 id.
--   발행에 product_product·product_template 필요(후보 목록 반영).
DROP VIEW IF EXISTS axp_prod.v_product_code CASCADE;
CREATE VIEW axp_prod.v_product_code AS
SELECT pp.id,
       COALESCE(NULLIF(pp.default_code, ''),
                pt.name->>'en_US',
                (SELECT v.value FROM jsonb_each_text(pt.name) v LIMIT 1),
                pp.id::text)              AS code
FROM public.product_product pp
JOIN public.product_template pt ON pt.id = pp.product_tmpl_id;

-- staging_sales ≈ (id, order_ref, order_date, store_id, product_id, qty, unit_price, channel, promo_flag, write_date)
DROP VIEW IF EXISTS axp_prod.v_sales;
CREATE VIEW axp_prod.v_sales AS
SELECT l.id,
       o.name                        AS order_ref,
       o.date_order::date::text      AS order_date,
       COALESCE(o.warehouse_id, 0)::text AS store_id,
       COALESCE(pc.code, l.product_id::text) AS product_id,
       l.product_uom_qty             AS qty,
       l.price_unit                  AS unit_price,
       COALESCE(o.team_id, 0)::text  AS channel,
       (COALESCE(l.discount, 0) > 0)::int AS promo_flag,
       l.write_date::text            AS write_date
FROM public.sale_order_line l
JOIN public.sale_order o ON o.id = l.order_id
LEFT JOIN axp_prod.v_product_code pc ON pc.id = l.product_id
WHERE COALESCE(l.display_type, '') = ''      -- 섹션/메모 라인 제외
  AND o.state IN ('sale', 'done');           -- 확정 주문만 (draft 견적 제외)

-- staging_purchase ≈ (id, po_ref, order_date, receipt_date, vendor_id, material_id, qty, unit_price, lot_id, write_date)
DROP VIEW IF EXISTS axp_prod.v_purchase;
CREATE VIEW axp_prod.v_purchase AS
SELECT l.id,
       o.name                        AS po_ref,
       o.date_order::date::text      AS order_date,
       l.date_planned::date::text    AS receipt_date,
       o.partner_id::text            AS vendor_id,
       COALESCE(pc.code, l.product_id::text) AS material_id,
       l.product_qty                 AS qty,
       l.price_unit                  AS unit_price,
       NULL::text                    AS lot_id,   -- 로트는 입고 stock_move_line에서 (2차)
       l.write_date::text            AS write_date
FROM public.purchase_order_line l
JOIN public.purchase_order o ON o.id = l.order_id
LEFT JOIN axp_prod.v_product_code pc ON pc.id = l.product_id
WHERE COALESCE(l.display_type, '') = ''
  AND o.name NOT LIKE 'PO/AXP/%';              -- P2-I11: 플랫폼 발주 초안 자기 환류 차단

-- staging_stock_move ≈ (id, move_date, product_id, from_loc, to_loc, qty, move_type, lot_id, reason, write_date)
-- P5-D: 로트 결선 — stock_move_line→stock_lot 조인(복수 로트 무브는 대표 1건).
--   발행에 stock_move_line·stock_lot 추가 필요(아래 후보 목록에 반영).
DROP VIEW IF EXISTS axp_prod.v_stock_move;
CREATE VIEW axp_prod.v_stock_move AS
SELECT m.id,
       m.date::date::text            AS move_date,
       COALESCE(pc.code, m.product_id::text) AS product_id,
       m.location_id::text           AS from_loc,
       m.location_dest_id::text      AS to_loc,
       m.product_uom_qty             AS qty,
       m.picking_type_id::text       AS move_type,
       (SELECT lt.name FROM public.stock_move_line ml
          LEFT JOIN public.stock_lot lt ON lt.id = ml.lot_id
         WHERE ml.move_id = m.id AND lt.name IS NOT NULL
         ORDER BY ml.id LIMIT 1)     AS lot_id,
       m.origin                      AS reason,
       m.write_date::text            AS write_date
FROM public.stock_move m
LEFT JOIN axp_prod.v_product_code pc ON pc.id = m.product_id
WHERE m.state = 'done';

-- staging_mrp ≈ (id, mo_ref, prod_date, product_id, line_id, worker_id, equipment_id, sop_id, qty_planned, qty_done, shift, write_date)
DROP VIEW IF EXISTS axp_prod.v_mrp;
CREATE VIEW axp_prod.v_mrp AS
SELECT p.id,
       p.name                        AS mo_ref,
       COALESCE(p.date_finished, p.date_start)::date::text AS prod_date,
       COALESCE(pc.code, p.product_id::text) AS product_id,
       -- P5-D: 작업장 결선 — workorder의 첫 작업장을 라인·설비로 (규약: 작업장=설비)
       (SELECT wc.id::text FROM public.mrp_workorder wo
          JOIN public.mrp_workcenter wc ON wc.id = wo.workcenter_id
         WHERE wo.production_id = p.id ORDER BY wo.id LIMIT 1) AS line_id,
       p.user_id::text               AS worker_id,
       (SELECT wc.name::text FROM public.mrp_workorder wo
          JOIN public.mrp_workcenter wc ON wc.id = wo.workcenter_id
         WHERE wo.production_id = p.id ORDER BY wo.id LIMIT 1) AS equipment_id,
       p.bom_id::text                AS sop_id,      -- BOM=표준작업 규약
       p.product_qty                 AS qty_planned,
       p.qty_producing               AS qty_done,
       NULL::text                    AS shift,       -- 교대는 현장 장표(M1-3)에서
       p.write_date::text            AS write_date
FROM public.mrp_production p
LEFT JOIN axp_prod.v_product_code pc ON pc.id = p.product_id
WHERE p.state IN ('progress', 'to_close', 'done');

-- staging_maintenance ≈ (id, event_date, equipment_id, event_type, duration_min, note, write_date)
DROP VIEW IF EXISTS axp_prod.v_maintenance;
CREATE VIEW axp_prod.v_maintenance AS
SELECT r.id,
       COALESCE(r.close_date, r.request_date)::text AS event_date,
       r.equipment_id::text          AS equipment_id,
       COALESCE(r.maintenance_type, 'corrective')   AS event_type,
       COALESCE(r.duration, 0) * 60                 AS duration_min,  -- duration은 시간 단위
       r.name                                       AS note,
       r.write_date::text                           AS write_date
FROM public.maintenance_request r;

-- staging_quality: Odoo Community에는 quality_check 없음(Enterprise 전용).
--   Enterprise 고객: quality_check(id, control_date, production_id, product_id,
--   team_id, user_id, quality_state, measure ...) 기준 뷰를 온사이트에서 추가.
--   Community 고객: 불량 집계는 stock_scrap + 현장 장표(M1-3)로 대체 —
--   v_quality_scrap이 그 대체 투영이다.
DROP VIEW IF EXISTS axp_prod.v_quality_scrap;
CREATE VIEW axp_prod.v_quality_scrap AS
SELECT s.id,
       s.date_done::date::text       AS check_date,
       s.origin                      AS mo_ref,
       COALESCE(pc.code, s.product_id::text) AS product_id,
       NULL::text                    AS line_id,
       s.create_uid::text            AS worker_id,
       NULL::text                    AS equipment_id,
       NULL::text                    AS material_lot_id,
       NULL::text                    AS sop_id,
       'scrap'                       AS defect_type,
       s.scrap_qty                   AS qty_defect,
       NULL::text                    AS shift,
       s.name                        AS memo,
       s.write_date::text            AS write_date
FROM public.stock_scrap s
LEFT JOIN axp_prod.v_product_code pc ON pc.id = s.product_id
WHERE s.state = 'done';
