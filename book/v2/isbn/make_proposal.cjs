const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType } = require("docx");
const fs = require("fs");

const F = "Malgun Gothic";
const BLUE = "1B3F94", RED = "C0392B", GRAY = "666666";

function P(text, opts = {}) {
  return new Paragraph({
    alignment: opts.center ? AlignmentType.CENTER : undefined,
    spacing: { after: opts.after ?? 160, line: 320 },
    children: [new TextRun({ text, bold: opts.bold, size: opts.size ?? 21, color: opts.color, italics: opts.i })],
  });
}
function H1(t) { return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 200 }, children: [new TextRun({ text: t, bold: true, color: BLUE })] }); }
function H2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 140 }, children: [new TextRun({ text: t, bold: true })] }); }
function LI(t, lvl=0) { return new Paragraph({ bullet: { level: lvl }, spacing: { after: 80, line: 300 }, children: [new TextRun({ text: t, size: 21 })] }); }

function TBL(headers, rows, widths) {
  const total = widths.reduce((a,b)=>a+b,0);
  const mk = (t, head=false) => new TableCell({
    width: { size: 0, type: WidthType.AUTO },
    shading: head ? { type: ShadingType.CLEAR, fill: "E8EEF9" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ spacing: { after: 0, line: 280 }, children: [new TextRun({ text: t, bold: head, size: 19 })] })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    rows: [ new TableRow({ children: headers.map(h=>mk(h,true)) }),
            ...rows.map(r=>new TableRow({ children: r.map(c=>mk(c)) })) ],
  });
}
const SP = () => P("", { after: 120 });

const doc = new Document({
  styles: { default: { document: { run: { font: F, size: 21 } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1300, bottom: 1300, left: 1400, right: 1400 } } },
    children: [
      P("", { after: 600 }),
      P("asc.kr 웹사이트 전환 제안서", { center: true, bold: true, size: 40, color: BLUE, after: 200 }),
      P("thirdbrain.kr → asc.kr : 에이에스씨 회사 홈페이지 + 『Odoo를 중심으로 AI ERP 혁명』 + 『서드브레인』 통합 홍보 사이트", { center: true, size: 22, after: 200 }),
      P("(주)에이에스씨  |  작성: 2026. 9.  |  버전 1.0", { center: true, size: 19, color: GRAY, after: 500 }),

      H1("1. 제안 배경과 목적"),
      P("현재 thirdbrain.kr은 『서드브레인』 단일 도서의 홍보 사이트로 운영되고 있고, 별도로 에이에스씨 회사 홈페이지(asc-web 시안)가 제작되어 있다. 두 사이트를 따로 운영하면 방문자·검색 유입·관리 노력이 분산된다. 본 제안은 하나의 도메인 asc.kr 아래에 ① 에이에스씨 회사 소개와 컨설팅 사업, ② 신간 『Odoo를 중심으로 AI ERP 혁명』, ③ 기간(旣刊) 『서드브레인』과 그 실천 프로그램을 통합하여, \"책으로 신뢰를 만들고 컨설팅으로 연결한다\"는 하나의 흐름을 완성하는 것을 목적으로 한다."),
      LI("회사(에이에스씨)가 상위 브랜드, 두 권의 책은 회사의 전문성을 증명하는 대표 콘텐츠로 배치"),
      LI("서드브레인의 기존 콘텐츠(블로그·뇌건강 부록·프로그램·EEG)는 폐기하지 않고 '서드브레인' 섹션으로 이관"),
      LI("thirdbrain.kr 주소는 유지하되 asc.kr의 서드브레인 섹션으로 자동 연결(리다이렉트)하여 기존 검색 유입과 인쇄물의 QR·링크를 보존"),

      H1("2. 현황 분석"),
      H2("2.1 thirdbrain.kr (현행)"),
      TBL(["항목","현황"], [
        ["성격","『서드브레인』 도서 홍보 원페이지형 사이트 + 블로그"],
        ["메뉴","홈 · 책 소개 · 프로그램(30일 몰입/부트캠프) · EEG 프로젝트 · 뇌건강 · 블로그 · 소개"],
        ["콘텐츠 자산","책 랜딩, 추천사, 뇌건강 부록 6편, 블로그, 30일 프로그램 신청, 홍보 포스터/QR"],
        ["기술","Astro 6 + Tailwind (AstroWind), GitHub 저장소, Netlify 배포(유료 계정)"],
      ], [2200, 6900]),
      H2("2.2 asc-web (제작 완료된 시안)"),
      TBL(["항목","현황"], [
        ["성격","에이에스씨 회사 홈페이지 시안 (같은 저장소 asc-web/ 폴더, 빌드 검증 완료)"],
        ["메뉴","홈 · 회사 소개 · Odoo AI ERP · 책 소개(AI ERP 혁명) · 블로그 · 게시판 · [책 구매]"],
        ["콘텐츠 자산","회사 소개(OBTS 방법론·서비스 형태·3인 컨설턴트), IT-지능화-OT 아키텍처, 신간 랜딩, 블로그 3편, 게시판 공지"],
        ["미결","asc.kr 도메인 연결, ASC 로고 원본 반영, 교보 구매 링크(출간 후 확정)"],
      ], [2200, 6900]),
      SP(),
      P("두 자산의 성격이 상호보완적이다 — thirdbrain.kr은 콘텐츠(블로그·부록·프로그램)가 풍부하고, asc-web은 회사·사업·신간 구조가 완성되어 있다. 통합 시 서로의 부족을 정확히 메운다."),

      H1("3. 통합 사이트 구조(안)"),
      H2("3.1 메뉴 구성"),
      TBL(["메뉴","내용","출처"], [
        ["홈","에이에스씨 슬로건(기록하는 ERP에서 판단하는 ERP로) + 사업 영역 + 두 책 소개 카드 + 컨설팅 문의 CTA","asc-web 홈 확장"],
        ["회사 소개","회사 개요·문제의식·서비스 형태·진행 절차·3인 컨설턴트·연락처","asc-web"],
        ["Odoo AI ERP","IT-지능화-OT 3계층 아키텍처, 4대 지능화, 도입 로드맵, FAQ","asc-web"],
        ["책 — AI ERP 혁명","신간 랜딩: 표지·3부 구성·목차·저자·판형/가격·FAQ·교보 구매","asc-web"],
        ["책 — 서드브레인","기존 thirdbrain.kr 책 랜딩 + 추천사 + 교보 구매","thirdbrain 이관"],
        ["프로그램","30일 몰입·부트캠프·EEG 프로젝트 (서드브레인 실천 프로그램)","thirdbrain 이관"],
        ["뇌건강","뇌건강 부록 6편 (수면·운동·명상·영양 등)","thirdbrain 이관"],
        ["블로그","AI ERP 칼럼 + 서드브레인 글 통합 (카테고리로 구분: AI ERP / 뇌경영 / 소식)","양쪽 통합"],
        ["게시판","공지사항·안내 (이메일 문의 연동)","asc-web"],
        ["[책 구매]","헤더 버튼 — 클릭 시 두 책 선택(AI ERP 혁명 / 서드브레인 → 각 교보 페이지)","신규"],
      ], [1700, 5200, 2200]),
      H2("3.2 상단 메뉴 표시(안)"),
      P("홈 · 회사 소개 · Odoo AI ERP · 책(▾ AI ERP 혁명 / 서드브레인) · 프로그램 · 블로그 · 게시판 · [책 구매]", { bold: true }),
      P("'책' 메뉴는 드롭다운으로 두 권을 나란히 노출한다. '뇌건강'은 서드브레인 하위 또는 블로그 카테고리로 배치하여 상단 메뉴를 8개 이하로 유지한다.", { color: GRAY, size: 19 }),

      H1("4. 페이지별 상세 기획"),
      H2("4.1 홈 (/)"),
      LI("히어로: \"기록하는 ERP에서 판단하는 ERP로\" + Odoo 아키텍처 이미지 + [컨설팅 문의]/[책 보기]"),
      LI("사업 영역 6카드: Odoo 지능형 ERP · 온톨로지-지식그래프 AX · 스마트공장/MES/IoT · 수요예측/생산계획 · AI 교육/출판 · 전국 3거점"),
      LI("두 책 소개 섹션: 『Odoo를 중심으로 AI ERP 혁명』(기업의 지능화) + 『서드브레인』(개인의 지능화) — \"기업의 서드브레인, 사람의 서드브레인\"이라는 하나의 메시지로 묶음"),
      LI("AX 5단계 방법론 스텝 + 실적 통계 + 컨설팅 문의 CTA"),
      H2("4.2 책 — AI ERP 혁명 (/book)"),
      LI("표지 히어로(터미널 Odoo ERP 디자인 반영판), 210쪽·21장·그림표 200+ 통계"),
      LI("3부 구성과 목차 미리보기, 세 저자 소개, 종이책 25,000원/전자책 15,000원·ISBN 표기"),
      LI("교보 구매 버튼(출간 후 실제 상품 URL로 교체), 컨설팅 연결 CTA(\"책의 방법론 그대로 구축해 드립니다\")"),
      H2("4.3 책 — 서드브레인 (/thirdbrain)"),
      LI("기존 thirdbrain.kr 홈의 책 섹션 이관: 세 개의 뇌, 목차, 추천사(서유헌 교수), 교보 구매"),
      LI("30일 몰입/부트캠프/EEG는 /program 으로 연결 유지"),
      H2("4.4 프로그램·뇌건강·블로그·게시판"),
      LI("프로그램(/program)·EEG(/eeg)·뇌건강 부록(/appendix): 기존 페이지 그대로 이관, 주소 유지"),
      LI("블로그: 기존 서드브레인 글 + AI ERP 칼럼 통합, 카테고리(AI ERP / 뇌경영 / 소식)로 구분"),
      LI("게시판: 공지·안내 목록형. 초기에는 정적 운영(관리자가 글 추가), 향후 댓글/문의폼(Tally 등) 연동 검토"),

      H1("5. 브랜드·디자인 방향"),
      LI("상위 브랜드: ASC 로고(남색 ASC + 빨간 점, AI System Creator) — 헤더·파비콘·OG 이미지에 일관 적용"),
      LI("색상: ASC 남색(#1B3F94)을 주색으로, 책별 보조색(AI ERP 혁명 = 하늘색/노랑 표지 톤, 서드브레인 = 기존 톤) 유지"),
      LI("두 책이 나란히 설 때의 원칙: 회사가 이야기의 주어, 책은 증거 — \"30년 현장의 결론을 책으로 쓰고, 시스템으로 만든다\""),

      H1("6. 도메인·이관 계획"),
      H2("6.1 도메인 전략"),
      TBL(["도메인","역할","설정"], [
        ["asc.kr","본 사이트(정식 주소)","Netlify 새 사이트에 Primary domain으로 연결"],
        ["thirdbrain.kr","보조(기존 링크 보존)","asc.kr/thirdbrain 으로 301 리다이렉트 (또는 전체를 asc.kr로)"],
        ["www.asc.kr","보조","asc.kr로 리다이렉트"],
      ], [2100, 3100, 3900]),
      H2("6.2 주소(URL) 보존 원칙"),
      P("기존 인쇄물·QR·검색에 노출된 thirdbrain.kr 주소가 깨지지 않도록 다음 매핑을 Netlify 리다이렉트로 설정한다."),
      TBL(["기존 주소","새 주소"], [
        ["thirdbrain.kr/","asc.kr/thirdbrain"],
        ["thirdbrain.kr/program · /eeg · /appendix","asc.kr/program · /eeg · /appendix (그대로)"],
        ["thirdbrain.kr/블로그 글 주소","asc.kr/블로그 동일 주소 (그대로)"],
      ], [4300, 4800]),
      H2("6.3 작업 단계"),
      TBL(["단계","작업","기간","비고"], [
        ["1","통합 사이트 구축: asc-web에 서드브레인 섹션(책/프로그램/EEG/뇌건강/블로그 글) 이관, '책' 드롭다운 메뉴 구성","2~3일","코드 작업 (Claude 수행)"],
        ["2","검수: 전 페이지 미리보기 링크로 확인·수정","1~2일","발주자 검토"],
        ["3","Netlify 배포: 새 사이트 생성(Base asc-web) → 임시주소 확인","30분","발주자 클릭 + 안내"],
        ["4","도메인 연결: asc.kr DNS 설정, thirdbrain.kr 리다이렉트 전환","1일 (DNS 전파 포함)","기존 Netlify 계정 내 처리"],
        ["5","마무리: 교보 상품 링크 확정 반영, 검색엔진(구글 서치콘솔·네이버 서치어드바이저) 등록","출간 후","운영 단계"],
      ], [700, 4700, 1700, 2000]),

      H1("7. 운영 방안"),
      LI("콘텐츠 갱신: 블로그는 마크다운 파일 추가(작성 요청 시 Claude가 대행 가능), 게시판은 목록에 항목 추가"),
      LI("배포 자동화: GitHub에 수정 반영(push) 시 Netlify가 자동 재배포 — 별도 서버 관리 불필요"),
      LI("비용: 기존 Netlify 유료 계정 내에서 사이트 추가 운영(추가 호스팅 비용 없음), asc.kr 도메인 등록비만 유지"),
      LI("측정: 방문 통계(Netlify Analytics 또는 무료 GA4), 책 구매 버튼 클릭 추적"),

      H1("8. 의사결정 요청 사항"),
      TBL(["번호","결정 사항","선택지(권장 굵게)"], [
        ["1","thirdbrain.kr 처리","① 전체를 asc.kr로 리다이렉트(관리 단순, 권장) ② 당분간 양쪽 병행 운영"],
        ["2","상단 메뉴 '뇌건강' 위치","① 블로그 카테고리로 통합(메뉴 간결, 권장) ② 상단 메뉴 유지"],
        ["3","30일 몰입·부트캠프 지속 여부","① 유지(서드브레인 섹션에) ② 축소하여 책 소개만"],
        ["4","게시판 문의 방식","① 이메일 안내(즉시 가능, 권장) ② Tally 문의폼 연동 ③ 추후 실시간 게시판"],
        ["5","ASC 로고","원본 파일(AI/PNG) 제공 시 즉시 교체 — 현재는 재현 로고타입 사용 중"],
      ], [700, 2700, 5700]),

      H1("9. 결론"),
      P("이미 검증된 서드브레인 사이트의 뼈대와 완성된 asc-web 시안이 있어, 통합에 필요한 것은 새 개발이 아니라 '재배치'다. 1주 이내에 asc.kr에서 회사·신간·서드브레인이 한 흐름으로 만나는 사이트를 열 수 있다. 승인해 주시면 1단계(통합 구축)부터 바로 진행하고, 각 단계마다 미리보기 링크로 확인을 받겠다."),
      SP(),
      P("(주)에이에스씨  |  asclhg@gmail.com  |  asc.kr", { center: true, color: GRAY, size: 19 }),
    ],
  }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync("/home/user/thirdbrain-web/asc-web/asc.kr_전환_제안서.docx", b); console.log("생성 완료"); });
