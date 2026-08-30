const { Document, Packer, Paragraph, TextRun, HeadingLevel } = require("docx");
const fs = require("fs");
const items = [
  ["h","일러두기"],
  ["h","프롤로그. 왜 지금, 지능형 AI ERP인가 — 3정5S에서 LLM 무한 루프까지"],
  ["p","제1부. 현장에서 플랫폼으로 — 지능형 ERP 컨설팅 방법론"],
  ["c","제1장. ERP 50년과 지능형 ERP: 동기ERP에서 AI ERP까지"],
  ["c","제2장. 컨설팅의 출발: 현장 진단과 3정5S — 데이터 품질의 원점"],
  ["c","제3장. 눈으로 보는 관리에서 데이터로 보는 관리로"],
  ["c","제4장. 부품전개와 일정계획: 제번·추번에서 MRP·APS까지"],
  ["c","제5장. DMAIC 데이터 루프: 수집·학습·추론의 무한 사이클"],
  ["c","제6장. AX 컨설팅 5단계 로드맵: 진단에서 환류까지"],
  ["c","제7장. 공정편성의 재구축과 예측 플랫폼의 완성"],
  ["p","제2부. Odoo 플랫폼과 지능형 ERP의 적용 — 모듈별 경영컨설팅"],
  ["c","제8장. Odoo 플랫폼 총론: 왜 단일 플랫폼인가 — 그리고 컨설팅 구조"],
  ["c","제9장. 웹사이트·이커머스: 고객 접점의 컨설팅"],
  ["c","제10장. CRM·판매: 영업 파이프라인의 컨설팅"],
  ["c","제11장. 매입(구매): 조달의 컨설팅"],
  ["c","제12장. 재고 관리: 물류의 컨설팅"],
  ["c","제13장. 제조 관리: 생산의 컨설팅"],
  ["c","제14장. 회계: 재무의 컨설팅"],
  ["c","제15장. Odoo AI·지식센터: 지능의 내장과 그 너머"],
  ["c","제16장. 확장 부스터: 지식그래프 아키텍처 구축"],
  ["c","제17장. 2부 결산: 모듈 도입 우선순위와 전사 컨설팅 로드맵"],
  ["p","제3부. 온톨로지 메커니즘으로 완성하는 AX — 온톨로지-지식그래프 변환기와 성공사례"],
  ["c","제18장. 경영 사각지대 — ERP가 보지 못하는 곳"],
  ["c","제19장. 온톨로지-지식그래프 — 말이 시스템이 되는 길"],
  ["c","제20장. 실행하는 온톨로지 — Agent Workflow와 Odoo 통합"],
  ["c","제21장. 증명 — 성공사례와 첫 90일"],
  ["h","에필로그. 두 개의 뇌, 하나의 기업"],
];
const kids = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "목차", bold: true })] }),
  new Paragraph({ children: [new TextRun({ text: "『AI ERP 혁명 — Odoo와 지능형 ERP』  |  이형근 · 정인호 · 송무준  |  에이에스씨 (신국판, 210쪽)", color: "666666", size: 18 })], spacing: { after: 300 } }),
];
for (const [k, t] of items) {
  if (k === "p") kids.push(new Paragraph({ children: [new TextRun({ text: t, bold: true, color: "0F86C0" })], spacing: { before: 260, after: 120 } }));
  else if (k === "h") kids.push(new Paragraph({ children: [new TextRun({ text: t, bold: true })], spacing: { before: 200, after: 120 } }));
  else kids.push(new Paragraph({ children: [new TextRun("    " + t)], spacing: { after: 90 } }));
}
const doc = new Document({
  styles: { default: { document: { run: { font: "Malgun Gothic", size: 21 } } } },
  sections: [{ children: kids }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync("목차소개.docx", b); console.log("생성: 목차소개.docx"); });
