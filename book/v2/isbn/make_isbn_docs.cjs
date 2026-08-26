// ISBN 신청 서류 6종 생성 (교보 POD·서지정보 등록용)
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel,
  BorderStyle,
} = require("docx");

const DIR = __dirname;
const FONT = "맑은 고딕";

const base = {
  styles: {
    default: {
      document: { run: { font: FONT, size: 22 }, paragraph: { spacing: { line: 340, after: 120 } } },
      heading1: { run: { font: FONT, size: 30, bold: true, color: "1E2761" }, paragraph: { spacing: { before: 0, after: 240 } } },
      heading2: { run: { font: FONT, size: 24, bold: true, color: "0F86C0" }, paragraph: { spacing: { before: 200, after: 120 } } },
    },
  },
};

const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const P = (t, opts = {}) => new Paragraph({
  alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
  spacing: opts.spacing,
  children: [new TextRun({ text: t, bold: !!opts.bold, size: opts.size, color: opts.color })],
});
const META = () => [
  P("도서명: AI ERP 혁명 — Odoo와 지능형 ERP", { bold: true }),
  P("지은이: 이형근 · 정인호  |  발행처: 에이에스씨  |  판형: 신국판(152×225mm), 210쪽"),
  new Paragraph({ spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "1CA5E5" } }, children: [] }),
];

function make(name, children) {
  const doc = new Document({ ...base, sections: [{ children }] });
  return Packer.toBuffer(doc).then((buf) => {
    fs.writeFileSync(path.join(DIR, name), buf);
    console.log("생성:", name);
  });
}

const 책소개 =
  "30년 ERP 컨설턴트와 온톨로지 AX 설계자가 함께 쓴 중소기업 지능형 ERP 실행서. 3정5S와 " +
  "눈으로 보는 관리를 데이터의 세계로 옮기고, DMAIC를 LLM이 상시로 돌리는 무한 루프로 재설계한다. " +
  "오픈소스 Odoo를 몸체로, JEDAIX 온톨로지를 판단의 층위로 — 기록하는 ERP가 판단하는 ERP로 " +
  "완성되는 길을 그림과 사례로 안내한다.";

const 요약 =
  "1부는 3정5S·눈으로 보는 관리·DMAIC를 데이터 방법론으로 번역한 컨설팅 방법론, 2부는 Odoo " +
  "모듈별 경영컨설팅과 4대 지능화(수요예측 영업·재고 최적화·설비예지·지식센터), 3부는 경영 " +
  "사각지대를 발굴해 실행으로 잇는 JEDAIX 온톨로지와 성공사례·첫 90일 로드맵이다. AI가 기업을 " +
  "대체하지 않는다 — 서드브레인을 가진 기업이 대체한다.";

const 서평 =
  "관리판과 3정5S에서 출발해 온톨로지와 LLM 무한 루프에 이르는 여정이 빙산·내비게이션·베이스캠프 " +
  "같은 비유와 70점에 가까운 그림으로 쉽게 읽힌다. ERP 도입을 고민하는 경영자, 데이터로 공장을 " +
  "바꾸려는 실무자, AX를 설계하는 컨설턴트 모두에게 내일 아침 시작할 수 있는 실행의 지도를 건네는 " +
  "책이다.";

// 글자수 검증 (공백 포함 200자 이내)
for (const [n, t] of [["책소개", 책소개], ["요약", 요약], ["서평", 서평]]) {
  console.log(`${n}: ${t.length}자`);
  if (t.length > 200) throw new Error(`${n} 200자 초과!`);
}

const toc = [
  ["", "프롤로그. 왜 지금, 지능형 AI ERP인가 — 3정5S에서 LLM 무한 루프까지"],
  ["제1부. 현장에서 플랫폼으로 — 지능형 ERP 컨설팅 방법론", ""],
  ["", "제1장. ERP 50년과 지능형 ERP: 동기ERP에서 AI ERP까지"],
  ["", "제2장. 컨설팅의 출발: 현장 진단과 3정5S — 데이터 품질의 원점"],
  ["", "제3장. 눈으로 보는 관리에서 데이터로 보는 관리로"],
  ["", "제4장. 부품전개와 일정계획: 제번·추번에서 MRP·APS까지"],
  ["", "제5장. DMAIC 데이터 루프: 수집·학습·추론의 무한 사이클"],
  ["", "제6장. AX 컨설팅 5단계 로드맵: 진단에서 환류까지"],
  ["", "제7장. 공정편성의 재구축과 예측 플랫폼의 완성"],
  ["제2부. Odoo 플랫폼과 지능형 ERP의 적용 — 모듈별 경영컨설팅", ""],
  ["", "제8장. Odoo 플랫폼 총론: 왜 단일 플랫폼인가 — 그리고 컨설팅 구조"],
  ["", "제9장. 웹사이트·이커머스: 고객 접점의 컨설팅"],
  ["", "제10장. CRM·판매: 영업 파이프라인의 컨설팅"],
  ["", "제11장. 매입(구매): 조달의 컨설팅"],
  ["", "제12장. 재고 관리: 물류의 컨설팅"],
  ["", "제13장. 제조 관리: 생산의 컨설팅"],
  ["", "제14장. 회계: 재무의 컨설팅"],
  ["", "제15장. Odoo AI·지식센터: 지능의 내장과 그 너머"],
  ["", "제16장. 확장 부스터: 서드브레인 아키텍처 구축"],
  ["", "제17장. 2부 결산: 모듈 도입 우선순위와 전사 컨설팅 로드맵"],
  ["제3부. 온톨로지 메커니즘으로 완성하는 AX — JEDAIX 방법론과 성공사례", ""],
  ["", "제18장. 경영 사각지대 — ERP가 보지 못하는 곳"],
  ["", "제19장. JEDAIX 온톨로지 — 말이 시스템이 되는 길"],
  ["", "제20장. 실행하는 온톨로지 — Agent Workflow와 Odoo 통합"],
  ["", "제21장. 증명 — 성공사례와 첫 90일"],
  ["", "에필로그. 두 개의 뇌, 하나의 기업"],
];

(async () => {
  await make("1_책소개.docx", [H1("책소개 (200자 이내)"), ...META(), P(책소개), P(`(공백 포함 ${책소개.length}자)`, { size: 18, color: "888888" })]);

  await make("2_목차.docx", [
    H1("목차"), ...META(),
    ...toc.flatMap(([part, ch]) => part ? [H2(part)] : [P("  " + ch)]),
  ]);

  await make("3_저자소개.docx", [
    H1("저자소개"), ...META(),
    H2("이형근"),
    P("ERP·MES·SCM 컨설턴트로 30년간 제조 현장의 전산화와 데이터 경영을 도왔다. 다품종소량·수주생산 공장에서 " +
      "3정5S와 눈으로 보는 관리를 배웠고, 『동기ERP』의 계보 위에서 데이터의 3정5S와 DMAIC 무한 루프 방법론을 " +
      "정립했다. 현재 에이에스씨(ASC, AI System Creator)에서 오픈소스 Odoo 기반 중소기업 지능형 ERP 구축을 " +
      "컨설팅하고 있다."),
    H2("정인호"),
    P("i7/JEDAIX 대표 컨설턴트. 경영 사각지대의 암묵지를 발굴해 업무에 쓸 수 있는 지식으로 키우는 온톨로지 기반 " +
      "AX 방법론 JEDAIX — 5 Space × 6 Station 워크벤치와 PTGDA 알고리즘, Ontology 기반 AI-Agent Workflow — 를 " +
      "설계·구축했다. 기계가 발굴하고 사람이 통치하는(Govern) 인간 중심의 AI 전환을 컨설팅하고 있다."),
  ]);

  await make("4_요약.docx", [H1("요약 (200자 이내)"), ...META(), P(요약), P(`(공백 포함 ${요약.length}자)`, { size: 18, color: "888888" })]);

  await make("5_서평.docx", [H1("서평 (200자 이내)"), ...META(), P(서평), P(`(공백 포함 ${서평.length}자)`, { size: 18, color: "888888" })]);

  await make("6_판권지.docx", [
    P("", { spacing: { after: 2400 } }),
    P("AI ERP 혁명", { center: true, bold: true, size: 40 }),
    P("Odoo와 지능형 ERP", { center: true, size: 26, color: "0F86C0" }),
    P("", { spacing: { after: 1200 } }),
    P("초판 1쇄 발행  2026년 ○○월 ○○일", { center: true }),
    P("", { spacing: { after: 400 } }),
    P("지은이  이형근 · 정인호", { center: true }),
    P("펴낸곳  에이에스씨", { center: true }),
    P("전자우편  asclhg@gmail.com", { center: true }),
    P("출판등록  제 ○○○-○○-○○○○○호 (등록 후 기입)", { center: true }),
    P("", { spacing: { after: 400 } }),
    P("판형  신국판(152×225mm)  |  쪽수  210쪽", { center: true }),
    P("ISBN  ○○○-○○-○○○○○-○○-○ (발급 후 기입)", { center: true }),
    P("정가  ○○,○○○원", { center: true }),
    P("", { spacing: { after: 800 } }),
    P("ⓒ 이형근 · 정인호, 2026", { center: true }),
    P("이 책은 저작권법에 따라 보호받는 저작물이므로 무단 전재와 복제를 금합니다.", { center: true, size: 18 }),
    P("이 책 내용의 전부 또는 일부를 이용하려면 반드시 저작권자와 에이에스씨의 서면 동의를 받아야 합니다.", { center: true, size: 18 }),
    P("잘못 만들어진 책은 구입하신 곳에서 바꾸어 드립니다.", { center: true, size: 18 }),
  ]);
})();
