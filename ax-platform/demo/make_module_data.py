"""각 모듈용 샘플 장표(엑셀)·Odoo 샘플(CSV) 생성 — 합성 데모 fact에서.

각 엑셀은 [데이터(샘플)] + [빈양식(수기용)] 2시트. 웹 업로드 표준필드에 맞춘 헤더.
"""
import os, sys
SP = "/tmp/claude-0/-home-user-thirdbrain-web/bc639c69-a342-56eb-af6c-6a89fd170e25/scratchpad"
os.environ.update(AXP_DATA=SP + "/e2e_out", AXP_DB="sqlite", AXP_PROFILE="taesungdang")
sys.path.insert(0, "/home/user/thirdbrain-web/ax-platform/core")
sys.path.insert(0, "/home/user/thirdbrain-web/ax-platform/demo")
from pathlib import Path
import pandas as pd
from axp import db
import profiles

OUT = Path(SP + "/demo_module_data"); OUT.mkdir(exist_ok=True)
P = profiles.active()
def _name(v):
    return v[0] if isinstance(v, (list, tuple)) else v
SNAME = {k: _name(v) for k, v in P["stores"].items()}
PNAME = {k: _name(v) for k, v in P["products"].items()}
VNAME = {k: _name(v) for k, v in P.get("vendors", {}).items()}


def write_xlsx(fname, title, data_df, blank_cols, note):
    path = OUT / fname
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        data_df.to_excel(xw, sheet_name="데이터(샘플)", index=False)
        blank = pd.DataFrame([{c: "" for c in blank_cols} for _ in range(8)])
        blank.to_excel(xw, sheet_name="빈양식(수기용)", index=False)
        ws = xw.sheets["빈양식(수기용)"]
        ws.cell(row=11, column=1, value=note)
    print(f"  {fname}: {len(data_df)}행 → {path.name}")


# ── M1 판매 장표 (sales_summary: date/store/product/qty) ──
sales = db.query("SELECT date_key AS 일자, store_id AS 매장코드, product_id AS 상품코드, "
                 "qty AS 판매개수 FROM fact_sales WHERE date_key >= '2026-06-01' "
                 "ORDER BY date_key, store_id LIMIT 800")
sdf = pd.DataFrame(sales)
sdf.insert(2, "매장명", sdf["매장코드"].map(SNAME).fillna(sdf["매장코드"]))
sdf.insert(4, "상품명", sdf["상품코드"].map(PNAME).fillna(sdf["상품코드"]))
write_xlsx("01_판매장표.xlsx", "일 판매 집계", sdf,
           ["일자", "매장명", "상품명", "판매개수"],
           "※ 수기 작성: 일자(YYYY-MM-DD)·매장명·상품명·판매개수. 업로드 시 표준필드 date/store_id/product_id/qty 로 매핑됩니다.")

# ── M1/M4 생산 일지 (production) ──
prod = db.query("SELECT date_key AS 일자, product_id AS 상품코드, "
                "SUM(qty_planned) AS 계획수량, SUM(qty_done) AS 완료수량 "
                "FROM fact_production WHERE date_key >= '2026-06-01' "
                "GROUP BY date_key, product_id ORDER BY date_key LIMIT 600")
pdf = pd.DataFrame(prod)
pdf.insert(2, "상품명", pdf["상품코드"].map(PNAME).fillna(pdf["상품코드"]))
write_xlsx("02_생산일지.xlsx", "일 생산 실적", pdf,
           ["일자", "상품명", "계획수량", "완료수량"],
           "※ 수기 작성: 일자·상품명·계획수량·완료수량. 계획준수율(완료/계획) KPI의 원천입니다.")

# ── M2/M4 품질 검사 장표 (defect) ──
defe = db.query("SELECT date_key AS 일자, equipment_id AS 설비, defect_type AS 불량유형, "
                "SUM(qty_defect) AS 불량수량, SUM(qty_produced) AS 생산수량 FROM fact_defect "
                "WHERE date_key >= '2026-06-01' GROUP BY date_key, equipment_id, defect_type "
                "ORDER BY date_key LIMIT 600")
write_xlsx("03_품질검사장표.xlsx", "품질 검사 일지", pd.DataFrame(defe),
           ["일자", "설비", "불량유형", "불량수량"],
           "※ 수기 작성: 일자·설비·불량유형·불량수량. 불량률·품질 KPI의 원천입니다.")

# ── M4/M7 정비 이력 장표 (equipment_event) ──
eq = db.query("SELECT date_key AS 정비일, equipment_id AS 설비, event_type AS 정비유형, "
              "duration_min AS 소요분, note AS 비고 FROM fact_equipment_event "
              "ORDER BY date_key LIMIT 200")
write_xlsx("04_정비이력장표.xlsx", "설비 정비 이력", pd.DataFrame(eq),
           ["정비일", "설비", "정비유형", "소요분", "비고"],
           "※ 수기 작성: 정비일·설비·정비유형(정기/고장)·소요분. 정비소요(MTTR)·고장건수 KPI의 원천입니다.")

# ── M1 자재 입고 장표 (procurement) ──
proc = db.query("SELECT date_key AS 입고일, material_id AS 자재, vendor_id AS 공급사코드, "
                "lot_id AS 로트번호, qty AS 입고수량, amount AS 금액 FROM fact_procurement "
                "ORDER BY date_key LIMIT 250")
prdf = pd.DataFrame(proc)
prdf.insert(2, "공급사명", prdf["공급사코드"].map(VNAME).fillna(prdf["공급사코드"]))
write_xlsx("05_자재입고장표.xlsx", "자재 입고 이력", prdf,
           ["입고일", "자재", "공급사명", "로트번호", "입고수량"],
           "※ 수기 작성: 입고일·자재·공급사·로트번호·수량. 설비×공급사 불량 규칙(근거)의 원천입니다.")

print("엑셀 장표 생성 완료 →", OUT)
