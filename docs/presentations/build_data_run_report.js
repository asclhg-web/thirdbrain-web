// AX 통합 데이터·성과 시연 보고서 (대표 보고용)
const fs = require("fs");
const path = require("path");
const D = require("docx");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        WidthType, AlignmentType, HeadingLevel, ImageRun, BorderStyle, ShadingType } = D;
const SP = __dirname;
const R = JSON.parse(fs.readFileSync(path.join(SP, "kpi_result.json"), "utf8"));

const F = "맑은 고딕";
const BROWN = "6E3A1C", GOLD = "C07F1E", TEAL = "0E8F86", RED = "A8493B", SUB = "76675A", INK = "2E241C";
function t(text, o = {}) { return new TextRun({ text, font: F, size: o.size || 20, bold: o.bold, color: o.color || INK, italics: o.italics }); }
function p(runs, o = {}) { return new Paragraph({ children: Array.isArray(runs) ? runs : [runs], spacing: { after: o.after ?? 120, before: o.before ?? 0, line: 276 }, alignment: o.align }); }
function h1(text) { return new Paragraph({ children: [t(text, { bold: true, size: 30, color: BROWN })], spacing: { before: 260, after: 130 }, heading: HeadingLevel.HEADING_1, border: { bottom: { color: "E7D9C6", size: 8, space: 4, style: BorderStyle.SINGLE } } }); }
function h2(text) { return new Paragraph({ children: [t(text, { bold: true, size: 24, color: GOLD })], spacing: { before: 180, after: 90 } }); }
function cell(runs, o = {}) { return new TableCell({ width: { size: o.w || 2000, type: WidthType.DXA }, shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill } : undefined, margins: { top: 40, bottom: 40, left: 90, right: 90 }, children: [new Paragraph({ children: Array.isArray(runs) ? runs : [runs], alignment: o.align, spacing: { after: 0, line: 260 } })] }); }
function headRow(cells, ws) { return new TableRow({ tableHeader: true, children: cells.map((c, i) => cell(t(c, { bold: true, color: "FFFFFF", size: 19 }), { w: ws[i], fill: BROWN, align: AlignmentType.CENTER })) }); }
function row(cells, ws, o = {}) { return new TableRow({ children: cells.map((c, i) => cell(Array.isArray(c) ? c : t(String(c), { size: 19, color: o.color }), { w: ws[i], fill: o.fill, align: o.align && o.align[i] })) }); }
function table(rows) { return new Table({ width: { size: 9360, type: WidthType.DXA }, rows, borders: ["top", "bottom", "left", "right", "insideHorizontal", "insideVertical"].reduce((a, k) => (a[k] = { style: BorderStyle.SINGLE, size: 4, color: "DCCDBB" }, a), {}) }); }
function gap() { return new Paragraph({ children: [t("")], spacing: { after: 60 } }); }

const kd = {}; R.kpis.forEach(k => kd[k.name] = k);
const stColor = s => s === "달성" ? TEAL : s === "미달" ? RED : SUB;

const doc = new Document({
  styles: { default: { document: { run: { font: F, size: 20 } } } },
  sections: [{
    properties: { page: { margin: { top: 900, bottom: 800, left: 1000, right: 1000 } } },
    children: [
      // 표지
      new Paragraph({ children: [t("AX 통합 데이터·성과 시연 보고서", { bold: true, size: 40, color: BROWN })], spacing: { before: 400, after: 120 }, alignment: AlignmentType.CENTER }),
      p(t("프로젝트 정의 → 데이터 반입 → 최종 판단 → KPI 달성도 (합성 데모 실행)", { size: 22, color: SUB }), { align: AlignmentType.CENTER, after: 60 }),
      p(t("2026. 9. 14 · 에이에스씨(ASC) · 대표 이형근 보고용", { size: 18, color: SUB }), { align: AlignmentType.CENTER, after: 300 }),
      p([t("요청: ", { bold: true }), t("부산세미나 집중 기간 중 자율 실행 — 각 모듈별 데모 데이터(수기 장표·엑셀·Odoo 샘플)를 만들어 프로젝트 정의부터 최종 판단·KPI 달성도까지 시스템을 돌리고, 필요사항을 워드로 정리.")]),
      p([t("정직 고지: ", { bold: true, color: RED }), t("아래 거래 수치는 태성당 구조로 만든 "), t("합성 샘플", { bold: true }), t("입니다. 파이프라인·판단·KPI 계산은 실제 코드가 수행했고, 실데이터 연결 시 같은 화면·같은 계산이 실수치로 돕니다.")]),
      gap(),

      // 1. 실행 요약
      h1("1. 실행 요약 — 전 모듈 수직 완주"),
      p([t("합성 제빵회사 데이터(판매 13,870 · 생산 7,207 · 불량 6,406 · 재고이동 15,788 · 센서 156,384행)를 M1 수집부터 M7 판단까지 "), t("67.6초에 완주", { bold: true, color: TEAL }), t("했습니다.")]),
      table([
        headRow(["단계", "결과(실측)"], [2600, 6760]),
        row(["M4 수요예측", `WAPE 7.0% (출발선 19.4% → 64% 개선)`], [2600, 6760], { fill: "FBF6EE" }),
        row(["M4 이상탐지", `OVEN-2 고장 13일 선행 감지 · 재현율 100% · 정상설비 오경보 2.8%`], [2600, 6760]),
        row(["M5 지식그래프", `6,694노드 대사 일치 · 규칙 2건 승격(RULE-0001·0002)`], [2600, 6760], { fill: "FBF6EE" }),
        row(["M6 판단", `회귀 30/30 통과 · 에이전트 5종 → 카드 ${R.cards.length}건`], [2600, 6760]),
        row(["M7 승인·환류", `첫 실승인·환류 완료 · SOP 개정 승인 · 감사 로그 10행`], [2600, 6760], { fill: "FBF6EE" }),
      ]),
      gap(),

      // 2. 모듈별 데모 데이터
      h1("2. 생성한 모듈별 데모 데이터 (첨부)"),
      p(t("각 엑셀은 [데이터(샘플)] + [빈양식(수기용)] 2시트 구성 — 현장에서 손으로 적는 장표와 업로드용 샘플을 함께 담았습니다.", { color: SUB, size: 19 })),
      table([
        headRow(["파일", "모듈", "행수", "용도·연결 KPI"], [2700, 1500, 900, 4260]),
        row(["01_판매장표.xlsx", "M1 수집", "800", "일 판매 집계 → 수요예측·결품/폐기 KPI"], [2700, 1500, 900, 4260], { fill: "FBF6EE" }),
        row(["02_생산일지.xlsx", "M1·M4", "552", "계획/완료 → 계획준수율 KPI"], [2700, 1500, 900, 4260]),
        row(["03_품질검사장표.xlsx", "M2·M4", "583", "불량유형/수량 → 불량률·품질 KPI"], [2700, 1500, 900, 4260], { fill: "FBF6EE" }),
        row(["04_정비이력장표.xlsx", "M4·M7", "5", "정비 소요/유형 → MTTR·고장건수 KPI"], [2700, 1500, 900, 4260]),
        row(["05_자재입고장표.xlsx", "M1", "245", "공급사/로트 → 설비×공급사 불량 규칙 근거"], [2700, 1500, 900, 4260], { fill: "FBF6EE" }),
        row(["06_Odoo샘플_판매주문.csv", "M1 CDC", "120", "Odoo sale_order 형태(name·date·amount·state)"], [2700, 1500, 900, 4260]),
        row(["07_Odoo샘플_발주.csv", "M1 CDC", "55", "Odoo purchase_order 형태"], [2700, 1500, 900, 4260], { fill: "FBF6EE" }),
        row(["08_Odoo샘플_정비요청.csv", "M1 CDC", "53", "Odoo maintenance_request 형태"], [2700, 1500, 900, 4260]),
      ]),
      gap(),

      // 3. 프로젝트 정의 → KPI 달성도
      h1("3. 프로젝트 정의 → KPI 달성도"),
      p([t("프로젝트: ", { bold: true }), t(`${R.project.name} — ${R.project.goal}`)]),
      h2("경영 목표 KPI (수기 실적)"),
      table([
        headRow(["KPI", "목표", "실적", "판정"], [3400, 1600, 1600, 2760]),
        ...["생산성 향상", "원가 절감", "납기 단축", "품질 향상"].map((n, i) => {
          const k = kd[n]; const fill = i % 2 ? "FBF6EE" : undefined;
          return row([n, `${k.target}%`, k.actual != null ? `${k.actual}%` : "-", [t(k.status, { bold: true, color: stColor(k.status) })]], [3400, 1600, 1600, 2760], { fill, align: [null, AlignmentType.CENTER, AlignmentType.CENTER, AlignmentType.CENTER] });
        }),
      ]),
      p([t("→ 경영 목표 4개 중 ", {}), t("3개 달성", { bold: true, color: TEAL }), t(", 원가 절감만 "), t("미달", { bold: true, color: RED }), t(" — 화면은 미달 KPI에 '다음 야간 배치에서 개선 카드가 제안됩니다'로 다음 행동을 안내(개선 루프).")], { before: 80 }),
      h2("기술 KPI (Odoo·장표 데이터로 자동 측정)"),
      table([
        headRow(["KPI", "목표", "실적", "판정"], [3400, 1600, 1600, 2760]),
        ...R.kpis.filter(k => k.area !== "경영 목표").map((k, i) => {
          const fill = i % 2 ? "FBF6EE" : undefined;
          const act = k.actual != null ? `${k.actual}${k.unit}` : "측정 전";
          return row([k.name, k.target != null ? `${k.target}${k.unit}` : "—", act, [t(k.status, { bold: true, color: stColor(k.status) })]], [3400, 1600, 1600, 2760], { fill, align: [null, AlignmentType.CENTER, AlignmentType.CENTER, AlignmentType.CENTER] });
        }),
      ]),
      p(t("※ '측정 전' 4개(WAPE·결품일수·리드타임·MTTR)는 데이터가 더 필요하거나 PG 전용 스냅샷이 필요한 지표 — 지어내지 않고 정직하게 '측정 전'으로 둡니다. 실데이터 온보딩 시 자동 결선됩니다.", { size: 18, color: SUB, italics: true })),
      gap(),
      h2("KPI 대시보드 (실행 화면 캡처)"),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ data: fs.readFileSync(path.join(SP, "kpi_dash_run.png")), transformation: { width: 560, height: 513 } })] }),
      gap(),

      // 4. 최종 판단 카드
      h1("4. 최종 판단 — 에이전트 카드"),
      p(t("에이전트 5종이 데이터에서 오늘의 제안을 카드로 만들었습니다(승인 대기/승인/반려 상태 포함).", { color: SUB, size: 19 })),
      table([
        headRow(["종류", "제안", "상태"], [1900, 5860, 1600]),
        ...R.cards.map((c, i) => row([c.kind, c.proposal.slice(0, 46), c.status], [1900, 5860, 1600], { fill: i % 2 ? "FBF6EE" : undefined })),
      ]),
      p([t("핵심 근거 카드: ", { bold: true }), t("설비 OVEN-2 × 공급사 V2 조합에서 불량률이 유의하게 높다 → 3주 3회 확인 후 규칙 승격 → SOP 개정 승인. "), t("모든 문장에 근거가 붙고, 원장까지 역추적됩니다.", { bold: true, color: TEAL })], { before: 80 }),
      gap(),

      // 5. 대표님께 필요한 것 (온보딩 요청서)
      h1("5. 대표님께 필요한 것 — 실데이터 온보딩 요청서"),
      p(t("지금은 합성 데모입니다. 실수치로 전환하려면 아래 자료가 필요합니다. 형식은 지금 쓰시는 그대로면 되고, 표준화·매핑은 저희가 합니다.", { size: 20 })),
      table([
        headRow(["구분", "필요 자료", "형식·비고"], [2000, 3560, 3800]),
        row(["필수 ①", "Odoo 읽기전용 접속", "host·db·user(REPLICATION 권장)·pw — 웹 [Odoo 연결 마법사]"], [2000, 3560, 3800], { fill: "FBF6EE" }),
        row(["필수 ②", "24개월 판매 엑셀", "일자·매장·상품·판매개수 (01_판매장표.xlsx 양식)"], [2000, 3560, 3800]),
        row(["권장 ③", "생산 일지·품질 검사", "02·03 장표 양식 — 계획준수율·불량률 KPI 자동화"], [2000, 3560, 3800], { fill: "FBF6EE" }),
        row(["권장 ④", "정비 이력·자재 입고", "04·05 장표 양식 — MTTR·설비×공급사 규칙 근거"], [2000, 3560, 3800]),
        row(["합의 ⑤", "KPI 기준정의", "생산성·원가·납기·품질의 계산식(어느 값÷어느 값)·기준선"], [2000, 3560, 3800], { fill: "FBF6EE" }),
      ]),
      p([t("KPI 자동 계산은 ", {}), t("지식센터 방식", { bold: true, color: TEAL }), t("으로 설계해 두었습니다(docs/kpi-auto-calc-via-knowledge.md) — ⑤ 계산식을 합의하면 코드 수정 없이 지식으로 등록해 자동 측정으로 전환합니다. 그 전까지는 수기 실적으로 운영.")], { before: 80 }),
      gap(),

      // 6. 데모 데이터 사용법
      h1("6. 첨부 데이터 사용법 (서버1)"),
      p([t("① 웹 ", {}), t("데이터 → 업로드", { bold: true }), t("에서 01~05 엑셀을 올리면 미리보기·매핑 후 반입됩니다. 처음 보는 매장·상품 이름은 '확인할 이름'으로 안내되어 표준 코드에 확정합니다.")]),
      p([t("② ", {}), t("성과 → 프로젝트·KPI → 새 프로젝트 정의", { bold: true }), t("에서 KPI 정의(생산성/원가/납기/품질)를 고르고 목표치를 적습니다.")]),
      p([t("③ 대시보드 ", {}), t("[지금 측정]", { bold: true }), t("으로 기술 KPI 자동 측정, 경영 목표는 "), t("[실적 기록]", { bold: true }), t("으로 실적을 넣으면 달성/미달이 판정됩니다.")]),
      p(t("첨부: demo_module_data.zip (엑셀 5 + Odoo CSV 3). 이 보고서와 함께 전달됩니다.", { size: 18, color: SUB, italics: true })),
      gap(),
      p([t("결론: ", { bold: true, color: TEAL }), t("데이터 부족 문제를 각 모듈 샘플로 채워 프로젝트 정의부터 최종 판단·KPI 달성도까지 전 과정을 실제로 돌렸습니다. 남은 것은 실데이터 연결(위 5장) 뿐이며, 연결 즉시 같은 화면이 실수치로 동작합니다.")]),
    ],
  }],
});

Packer.toBuffer(doc).then(b => {
  const out = "/home/user/thirdbrain-web/docs/presentations/AX_데이터·성과_시연보고서.docx";
  fs.writeFileSync(out, b);
  console.log("REPORT", out, b.length);
});
