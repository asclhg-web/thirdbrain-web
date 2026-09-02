const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType } = require("docx");
const fs = require("fs");
const F = "Malgun Gothic"; const BLUE = "1B3F94", RED = "C0392B", GRAY = "666666", ODOO = "714B67";
function P(text, o = {}) { return new Paragraph({ alignment: o.center ? AlignmentType.CENTER : undefined, spacing: { after: o.after ?? 160, line: 320 }, children: [new TextRun({ text, bold: o.bold, size: o.size ?? 21, color: o.color, italics: o.i })] }); }
function H1(t) { return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 200 }, children: [new TextRun({ text: t, bold: true, color: BLUE })] }); }
function H2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 140 }, children: [new TextRun({ text: t, bold: true })] }); }
function LI(t, lvl=0) { return new Paragraph({ bullet: { level: lvl }, spacing: { after: 80, line: 300 }, children: [new TextRun({ text: t, size: 21 })] }); }
function TBL(headers, rows, widths) {
  const total = widths.reduce((a,b)=>a+b,0);
  const mk = (t, head=false) => new TableCell({ width: { size: 0, type: WidthType.AUTO }, shading: head ? { type: ShadingType.CLEAR, fill: "EDE6EB" } : undefined, margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: [new Paragraph({ spacing: { after: 0, line: 280 }, children: [new TextRun({ text: t, bold: head, size: 19 })] })] });
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, rows: [ new TableRow({ children: headers.map(h=>mk(h,true)) }), ...rows.map(r=>new TableRow({ children: r.map(c=>mk(c)) })) ] });
}
const SP = () => P("", { after: 120 });

const doc = new Document({
  styles: { default: { document: { run: { font: F, size: 21 } } } },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1300, bottom: 1300, left: 1400, right: 1400 } } }, children: [
    P("", { after: 500 }),
    P("asc.kr 웹사이트 구축 제안서 (2판)", { center: true, bold: true, size: 40, color: BLUE, after: 160 }),
    P("Odoo 공식 파트너사 홈페이지 — 9월 15일 부산 Odoo 세미나 협찬 연계", { center: true, size: 23, color: ODOO, after: 160 }),
    P("에이에스씨 회사 + Odoo AI ERP 사업 + 『Odoo를 중심으로 AI ERP 혁명』 + 『서드브레인』 통합", { center: true, size: 20, after: 160 }),
    P("(주)에이에스씨  |  작성 2026. 9. 2.  |  버전 2.0  |  ★ 세미나 D-13", { center: true, size: 19, color: GRAY, after: 460 }),

    H1("1. 이번 판에서 달라진 방향"),
    LI("★ 홈 화면의 주인공을 'Odoo'로 — 에이에스씨는 Odoo 파트너사이며, 방문자의 첫 질문(\"Odoo 구축을 맡길 수 있는 회사인가\")에 첫 화면이 답해야 한다."),
    LI("★ 9월 15일 부산 Odoo 세미나(에이에스씨 협찬)를 사이트 오픈의 기폭제로 — 세미나 배너·행사 페이지를 최상단에 배치하고, 세미나 전(9월 10일 전후) 1차 오픈을 목표로 한다."),
    LI("★ 국내외 Odoo 파트너사 홈페이지의 표준 구성을 벤치마킹해 파트너사다운 신뢰 요소(파트너 배지·구축 사례·데모 신청)를 갖춘다."),
    LI("두 권의 책(『Odoo를 중심으로 AI ERP 혁명』·『서드브레인』)은 회사 전문성의 증거로 배치하되, 순서상 Odoo 사업 다음이다."),

    H1("2. Odoo 파트너사 홈페이지 벤치마킹"),
    P("국내 공식 파트너(링크업인포텍 link-up.co.kr, 에코두비즈 ecodoobiz.com, VTI코리아 등)와 해외 파트너 사이트의 공통 구성 요소를 정리하면 다음과 같다."),
    TBL(["구성 요소","내용","asc.kr 반영"], [
      ["파트너 배지","'Odoo Official/Ready/Silver/Gold Partner' 배지와 Odoo 공식 파트너 목록 페이지 링크","헤더·푸터·회사소개에 배지 노출 (등급 확인 필요 → 7장)"],
      ["첫 화면 = Odoo 서비스","\"Odoo로 ERP를 구축합니다\" 명제 + 데모/상담 버튼이 첫 화면","홈 히어로를 Odoo 중심으로 재구성"],
      ["서비스 메뉴","구축(Implementation)·커스터마이징·마이그레이션·교육·유지보수 구분","'Odoo 서비스' 페이지 5개 서비스 카드"],
      ["산업별 솔루션","제조·유통·서비스 등 업종별 적용안","제조(주력)·유통·이커머스 3개 업종 섹션"],
      ["구축 사례(레퍼런스)","고객사 로고·성과 수치·후기","사례 페이지 신설 (자료 제공 필요 → 7장)"],
      ["데모 신청","Odoo 화면을 보여주는 시연 예약 폼/캘린더","'데모 신청' CTA (이메일→향후 폼)"],
      ["이벤트/세미나","세미나 안내와 신청, 후기","부산 세미나 특집 페이지 + 상단 배너"],
      ["Odoo 최신 소식","버전 릴리스·기능 소개 블로그","블로그 'Odoo' 카테고리"],
    ], [1900, 3900, 3300]),

    H1("3. 사이트 구조(안) — Odoo 우선"),
    H2("3.1 상단 메뉴"),
    P("홈 · Odoo 서비스 · 세미나 · 구축 사례 · 책(▾ AI ERP 혁명 / 서드브레인) · 회사 소개 · 블로그 · 게시판 · [상담 신청]", { bold: true }),
    H2("3.2 홈 화면 구성 (위에서 아래로)"),
    TBL(["순서","섹션","내용"], [
      ["0","세미나 띠배너","\"9/15(월) 부산 Odoo 세미나 — 에이에스씨 협찬\" + 신청 링크 (세미나 후에는 후기로 교체)"],
      ["1","히어로","\"Odoo 공식 파트너 에이에스씨\" + 파트너 배지 + [무료 상담]/[세미나 신청] 버튼 + Odoo 화면/아키텍처 이미지"],
      ["2","Odoo 서비스 6카드","구축 · 커스터마이징 · 데이터 이관 · 교육 · 유지보수 · AI 지능화(온톨로지-지식그래프)"],
      ["3","왜 에이에스씨인가","30년 ERP·MES·SCM × 전국 3거점 × 저서 출간 — 파트너사 중의 차별점"],
      ["4","IT-지능화-OT 아키텍처","기존 다이어그램 + AX 5단계 방법론"],
      ["5","구축 사례 미리보기","대표 사례 2~3건 카드 (자료 확보 시)"],
      ["6","두 책 소개","기업의 지능화(『AI ERP 혁명』) + 사람의 지능화(『서드브레인』) 나란히"],
      ["7","상담 CTA","\"AI 이야기는 석 달 뒤에 — 먼저 진단부터\" + 문의"],
    ], [700, 2100, 6300]),
    H2("3.3 세미나 페이지 (/seminar)"),
    LI("행사 개요: 일시(9/15) · 장소 · 주최/주관 · 협찬(에이에스씨 로고) · 대상"),
    LI("프로그램 시간표, 연사 소개, 참가 신청 버튼(주최측 신청 링크 연결)"),
    LI("에이에스씨 발표/부스 안내 + 『AI ERP 혁명』 출간 소개(현장 이벤트가 있다면 함께)"),
    LI("세미나 종료 후: 발표 자료·사진·후기 게시로 전환 (검색 유입 자산화)"),
    H2("3.4 기타 페이지"),
    LI("Odoo 서비스(/odoo): 기존 페이지 확장 — 5개 서비스 상세 + 업종별 적용 + 도입 로드맵 + FAQ"),
    LI("구축 사례(/cases): 사례 카드(업종·규모·도입 모듈·성과). 공개 가능 사례 확보 전에는 익명화 사례로 시작"),
    LI("책 2종·회사 소개·블로그·게시판: 1판 제안서 구성 유지 (서드브레인 콘텐츠 이관 포함)"),
    LI("thirdbrain.kr → asc.kr/thirdbrain 301 리다이렉트로 기존 링크·QR 보존"),

    H1("4. 일정 (세미나 역산)"),
    TBL(["단계","작업","기한","담당"], [
      ["D-13~D-10","① 사장님 준비자료 접수(7장) ② 홈·세미나 페이지 우선 구축","9/2~9/5","자료: 사장님 / 구축: Claude"],
      ["D-9~D-7","1차 검수(미리보기 링크) → 수정 → Netlify 배포 + asc.kr 연결","9/6~9/8","검수: 사장님 / 작업: Claude+안내"],
      ["D-6~D-1","★ 1차 오픈 상태로 세미나 홍보 활용(명함·발표자료에 asc.kr 기재) · 잔여 페이지(사례·책·이관) 완성","9/9~9/14","공동"],
      ["D-Day","세미나 당일 — 사이트가 명함이 된다","9/15","—"],
      ["D+7 이내","세미나 후기 게시, thirdbrain.kr 리다이렉트 전환, 서치콘솔 등록","~9/22","Claude+안내"],
    ], [1500, 4600, 1400, 1600]),

    H1("5. 브랜드·디자인"),
    LI("주색: ASC 남색(#1B3F94) + 포인트 빨강 / Odoo 보라(#714B67)는 Odoo 관련 요소(배지·버튼)에 제한적으로 사용해 파트너십을 시각화"),
    LI("헤더: ASC 로고(원본) + 'Odoo Official Partner' 배지 병기"),
    LI("사진 톤: 현장(공장·창고·세미나) 실사진 우선 — 파트너사 사이트의 신뢰는 실물에서 나온다"),

    H1("6. 기술·운영 (변경 없음 요약)"),
    LI("Astro 정적 사이트, GitHub 저장소(asc-web/), Netlify 배포(기존 유료 계정, 추가 비용 없음)"),
    LI("수정 → GitHub 반영 → 자동 재배포. 블로그·게시판 글은 요청만 주시면 Claude가 대행"),

    H1("7. ★ 사장님이 준비해 주실 자료 (중요)"),
    P("아래 자료가 오는 순서대로 페이지가 완성됩니다. ◎=오픈 전 필수, ○=오픈 후 보완 가능.", { color: RED, bold: true }),
    H2("7.1 Odoo 파트너십 (◎ 최우선)"),
    TBL(["번호","자료","용도·비고"], [
      ["1","파트너 등급과 명칭 (예: Ready/Silver/Gold Partner, 등록 연도)","배지 표기 문구 — 잘못 표기하면 안 되므로 정확한 등급 필수"],
      ["2","Odoo 공식 파트너 목록 페이지의 에이에스씨 링크 (odoo.com/partners 내)","배지 클릭 시 연결해 공신력 증명"],
      ["3","Odoo 파트너 배지 이미지 (Odoo 파트너 포털에서 다운로드 가능)","헤더·푸터 게시 (없으면 텍스트 배지로 대체)"],
    ], [700, 4400, 4000]),
    H2("7.2 부산 세미나 (◎ 오픈 전 필수)"),
    TBL(["번호","자료","용도·비고"], [
      ["4","행사 정식 명칭 · 일시 · 장소(건물/층) · 주최/주관/협찬사 목록","세미나 페이지 개요"],
      ["5","프로그램 시간표(세션명·연사·시간) 또는 안내 포스터 원본","시간표 섹션 (포스터만 있어도 시작 가능)"],
      ["6","참가 신청 방법(신청 페이지 링크·전화·이메일)","신청 버튼 연결"],
      ["7","에이에스씨의 역할 (발표 여부·발표 제목·부스·현장 이벤트)","협찬사 소개 섹션"],
      ["8","협찬 관련 로고 사용 조건 (주최측 로고를 실어도 되는지)","저작권·초상권 확인"],
    ], [700, 4400, 4000]),
    H2("7.3 회사 기본 정보 (◎ 사이트 하단 법적 표기)"),
    TBL(["번호","자료","용도·비고"], [
      ["9","법인 정식 명칭 · 대표자명 · 사업자등록번호 · (통신판매업 신고번호 있으면)","푸터 필수 표기 (전자상거래 관련 법정 표기)"],
      ["10","정확한 주소 (도로명 전체) · 대표 전화번호","연락처 — 현재 '나주시 레이크뷰빌딩'까지만 확보됨"],
      ["11","ASC 로고 원본 파일 (AI/EPS/고해상 PNG)","현재는 재현 로고타입 사용 중 — 원본으로 교체"],
      ["12","대표/컨설턴트 프로필 사진 (또는 게재 여부 결정)","회사 소개 팀 섹션"],
    ], [700, 4400, 4000]),
    H2("7.4 구축 사례 (○ 오픈 후 보완 가능하나 빠를수록 좋음)"),
    TBL(["번호","자료","용도·비고"], [
      ["13","공개 가능한 고객 사례 2~3건: 업종·규모·도입 모듈·기간·성과 수치","사례 페이지 — 회사명 공개 불가 시 '전남 소재 부품 제조사(50인)' 식 익명화"],
      ["14","고객 로고 사용 동의 여부","사례 카드·홈 로고 벨트"],
      ["15","현장·세미나·워크숍 사진","홈·회사소개·블로그 (스마트폰 사진도 충분)"],
    ], [700, 4400, 4000]),
    H2("7.5 기타 (○)"),
    TBL(["번호","자료","용도·비고"], [
      ["16","교보문고 도서 상품 페이지 URL (출간 승인 후)","'책 구매' 버튼 연결 — 현재는 검색 링크"],
      ["17","상담·데모 신청 받을 방법 (이메일 유지 / 전화 병기 / 예약 캘린더)","상담 CTA 연결 방식 결정"],
      ["18","도메인 관리 정보 (asc.kr을 등록한 업체 로그인 가능 여부)","DNS 연결 단계에서 필요"],
      ["19","세미나 후: 발표자료 PDF·행사 사진","후기 페이지 자산화"],
    ], [700, 4400, 4000]),

    H1("8. 의사결정 요청"),
    TBL(["번호","결정 사항","권장안"], [
      ["1","1차 오픈 범위","홈+세미나+Odoo 서비스+회사소개+책(신간) 5페이지 선오픈, 나머지는 D+7까지"],
      ["2","thirdbrain.kr 처리","asc.kr/thirdbrain 으로 301 리다이렉트 (기존 QR·검색 보존)"],
      ["3","상담 채널","1차: 이메일+전화 병기 → 2차: 신청 폼 (Tally 무료)"],
      ["4","세미나 배너 문구","\"9/15 부산 Odoo 세미나 — Odoo 파트너 에이에스씨가 함께합니다\" (수정 환영)"],
    ], [700, 2600, 5800]),

    H1("9. 결론"),
    P("세미나(9/15)까지 13일 — 사이트가 세미나에서 배포될 명함·발표자료의 도착지가 되려면 9월 10일 전후 1차 오픈이 필요합니다. 뼈대(asc-web)와 콘텐츠(서드브레인·책·아키텍처)는 준비되어 있으므로, 결정적 변수는 7장의 준비 자료입니다. 7.1(파트너십)과 7.2(세미나) 자료를 먼저 보내주시면 즉시 홈·세미나 페이지 구축에 착수하고, 매 단계 미리보기 링크로 확인받겠습니다."),
    SP(),
    P("(주)에이에스씨  |  asclhg@gmail.com  |  asc.kr", { center: true, color: GRAY, size: 19 }),
  ] }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync("/home/user/thirdbrain-web/asc-web/asc.kr_구축_제안서_v2.docx", b); console.log("생성 완료"); });
