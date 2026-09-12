-- P6-3: Odoo 17 Enterprise 품질 모듈(quality) 매핑 뷰 — ★미검증 초안★
--
-- 정직성 고지: 이 파일은 Enterprise 인스턴스에서 실행해 본 적이 없다.
--   Community에는 quality_check가 없어 실측이 불가능하며(P3-2 실측),
--   컬럼 목록은 Odoo 17 공개 소스(addons/quality — Enterprise 배포에
--   포함되는 quality 코어 모델 정의)를 근거로 작성했다. Enterprise 고객
--   첫 계약 때 아래 '온사이트 검증 절차'를 반드시 통과시킨 뒤에만
--   운영에 편입한다. 검증 전에는 어떤 문서에도 '지원'이라 쓰지 않는다.
--
-- 전제: odoo_cdc_prod.sql 후보 목록의 quality_check·quality_alert가
--   Enterprise에서는 존재하므로 자동 발행된다(모듈 인지형 DO 블록).
--   구독 새로고침(ALTER SUBSCRIPTION ... REFRESH PUBLICATION WITH
--   (copy_data=true)) 후 이 뷰를 적용한다.
--
-- 온사이트 검증 절차 (Enterprise 고객 D0~D3, 체크리스트 C절에 편입):
--   1) \d public.quality_check 로 실컬럼 대조 — 아래 가정 컬럼과 차이를
--      기록하고 이 파일을 수정한다(버전 매트릭스에 추가).
--   2) 뷰 적용 후 SELECT * FROM axp_prod.v_quality LIMIT 5 육안 대조.
--   3) 검사 1건을 Odoo 화면에서 생성·합격 처리 → 뷰 도달 확인(소크 1행).
--   4) reconcile_prod 계열 대조에 staging_quality가 참여하는지 확인.
--
-- 가정 컬럼(Odoo 17 quality.check): id, control_date(datetime),
--   production_id(mrp_production FK), product_id, picking_id, team_id,
--   user_id, quality_state('none'|'pass'|'fail'), measure(float),
--   test_type_id, note(html), write_date.
--   불합격 수량: Odoo 품질 검사는 '판정'이지 수량이 아니다 — 수량 기반
--   불량 집계는 여전히 stock_scrap(v_quality_scrap)이 정본이고, 이 뷰는
--   판정 이벤트(합/불)를 사실 계열에 더한다(qty_defect=불합격 시 1).

DROP VIEW IF EXISTS axp_prod.v_quality;
CREATE VIEW axp_prod.v_quality AS
SELECT q.id,
       q.control_date::date::text    AS check_date,
       mp.name                       AS mo_ref,
       COALESCE(pc.code, q.product_id::text) AS product_id,
       NULL::text                    AS line_id,
       q.user_id::text               AS worker_id,
       NULL::text                    AS equipment_id,
       NULL::text                    AS material_lot_id,
       NULL::text                    AS sop_id,
       ('quality_' || q.quality_state) AS defect_type,   -- quality_pass/quality_fail
       CASE WHEN q.quality_state = 'fail' THEN 1 ELSE 0 END AS qty_defect,
       NULL::text                    AS shift,
       q.note::text                  AS memo,
       q.write_date::text            AS write_date
FROM public.quality_check q
LEFT JOIN public.mrp_production mp ON mp.id = q.production_id
LEFT JOIN axp_prod.v_product_code pc ON pc.id = q.product_id
WHERE q.quality_state IN ('pass', 'fail');   -- 미판정(none)은 제외
