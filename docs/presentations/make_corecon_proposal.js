// (주)코아콘 Odoo ERP 구축 1차 제안서 + 요구사항 정의서 (Word)
const fs = require("fs");
const D = require("docx");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, BorderStyle, ShadingType, HeadingLevel, VerticalAlign, PageBreak } = D;

const F = "맑은 고딕";
const NAVY="1F3A5F", PURPLE="714B67", TEAL="0E8F86", GOLD="C07F1E", RED="B03A2E",
      INK="222B36", SUB="6B7480", LINE="C9D3DE", HEADBG="EAF0F6", TINT="F5F8FB";
function t(x,o={}){return new TextRun({text:x,font:F,size:o.size||20,bold:o.bold,color:o.color||INK,italics:o.i});}
function p(runs,o={}){return new Paragraph({children:Array.isArray(runs)?runs:[runs],spacing:{after:o.after??110,before:o.before||0,line:o.line||288},alignment:o.align});}
function h1(x,o={}){return new Paragraph({heading:HeadingLevel.HEADING_1,pageBreakBefore:o.br,spacing:{before:o.br?60:280,after:140},border:{bottom:{color:NAVY,size:12,space:5,style:BorderStyle.SINGLE}},children:[t(x,{bold:true,size:28,color:NAVY})]});}
function h2(x){return new Paragraph({heading:HeadingLevel.HEADING_2,spacing:{before:190,after:90},children:[t("▎",{color:PURPLE,size:22,bold:true}),t(x,{bold:true,size:23,color:NAVY})]});}
function bul(x,o={}){return new Paragraph({spacing:{after:o.after??70,line:284},indent:{left:360,hanging:210},children:[t("• ",{bold:true,color:PURPLE}),...(Array.isArray(x)?x:[t(x)])]});}
function num(n,x){return new Paragraph({spacing:{after:70,line:284},indent:{left:380,hanging:250},children:[t(n+". ",{bold:true,color:TEAL}),...(Array.isArray(x)?x:[t(x)])]});}
function spacer(h){return p(t("",{size:h||8}),{after:h||40});}

function tbl(cw,header,rows,o={}){
  const b=()=>({style:BorderStyle.SINGLE,size:6,color:LINE});
  const hc=header.map((h,i)=>new TableCell({width:{size:cw[i],type:WidthType.DXA},shading:{type:ShadingType.CLEAR,fill:o.headfill||NAVY,color:"auto"},margins:{top:56,bottom:56,left:96,right:96},verticalAlign:VerticalAlign.CENTER,children:[p(t(h,{bold:true,size:o.hsize||18,color:o.hcolor||"FFFFFF"}),{after:0,align:AlignmentType.CENTER})]}));
  const rr=rows.map((r,ri)=>new TableRow({children:r.map((c,i)=>new TableCell({width:{size:cw[i],type:WidthType.DXA},shading:ri%2?{type:ShadingType.CLEAR,fill:TINT,color:"auto"}:undefined,margins:{top:48,bottom:48,left:96,right:96},verticalAlign:VerticalAlign.CENTER,children:[Array.isArray(c)?p(c,{after:0,size:o.size}):p(t(c,{size:o.size||17,color:(typeof c==='string'&&c.includes('미지원')?RED:INK)}),{after:0,align:o.center?AlignmentType.CENTER:AlignmentType.LEFT})]}))}));
  return new Table({width:{size:cw.reduce((a,b)=>a+b,0),type:WidthType.DXA},columnWidths:cw,
    borders:{top:b(),bottom:b(),left:b(),right:b(),insideHorizontal:b(),insideVertical:b()},rows:[new TableRow({tableHeader:true,children:hc}),...rr]});
}

const kids=[];

// ─────────── 표지 ───────────
kids.push(p(t("",{size:40}),{after:200}));
kids.push(p(t("Odoo ERP 구축 1차 제안서",{bold:true,size:52,color:NAVY}),{align:AlignmentType.CENTER,after:80}));
kids.push(new Paragraph({border:{bottom:{style:BorderStyle.SINGLE,size:16,color:PURPLE,space:8}},children:[t("",{size:2})],spacing:{after:160}}));
kids.push(p(t("요구사항 정의서 포함",{size:26,color:PURPLE,bold:true}),{align:AlignmentType.CENTER,after:60}));
kids.push(p(t("이카운트 ERP → Odoo 통합 전환 · 열관리·정밀장비 제조 맞춤",{size:20,color:SUB}),{align:AlignmentType.CENTER,after:520}));
kids.push(tbl([2400,6000],["구분","내용"],[
  ["제안 대상","주식회사 코아콘 (COREcon) 귀중"],
  ["사업 분야","열관리 솔루션·정밀장비 제조 및 연구개발 (오일쿨러·히트펌프·반도체 제조장비·산업용 에어컨·의료기기·센서 등)"],
  ["현행 시스템","이카운트(ECOUNT) ERP"],
  ["제안 범위","Odoo ERP 도입 — 영업·구매·수출입·생산·재고·프로젝트·회계·성과(KPI) 통합"],
  ["제안 일자","2026년 9월"],
  ["제 안 사","에이에스씨(ASC) · AX 플랫폼 사업팀 · odooaierp.com · asclhg@gmail.com"],
],{headfill:NAVY,size:18}));
kids.push(new Paragraph({children:[new PageBreak()]}));

// ─────────── 1. 제안 개요 ───────────
kids.push(h1("1. 제안 개요"));
kids.push(p([t("본 제안서는 ",{}),t("주식회사 코아콘",{bold:true}),t("이 현재 사용 중인 이카운트(ECOUNT) ERP를 ",{}),t("Odoo 통합 ERP",{bold:true,color:PURPLE}),t("로 전환하기 위한 ",{}),t("1차 제안 및 요구사항 정의",{bold:true}),t("를 담고 있습니다. 코아콘의 사업 특성인 ",{}),t("‘표준제품 판매 + 프로젝트형 장비 제조’ 2트랙 구조",{bold:true}),t("를 하나의 데이터 모델로 연결하여, 영업 기회부터 생산·프로젝트 손익·경영 성과(KPI)까지 단절 없이 관리하는 것을 목표로 합니다.")]));
kids.push(h2("제안의 핵심"));
kids.push(bul([t("하나의 플랫폼 : ",{bold:true}),t("영업–구매–수출입–생산–재고–프로젝트–회계를 단일 데이터로 통합 (화면 분산·중복 입력 해소)")]));
kids.push(bul([t("제조+프로젝트 동시 지원 : ",{bold:true}),t("오일쿨러·히트펌프 등 표준제품 판매와 반도체 제조장비·의료기기 등 프로젝트형 수주를 한 시스템에서")]));
kids.push(bul([t("승인 기반 통제 : ",{bold:true}),t("구매·전표·수주에 Odoo 승인 Workflow 적용 — ‘문서’가 아니라 ‘시스템’이 규칙을 지킴")]));
kids.push(bul([t("성과 가시화 : ",{bold:true}),t("프로젝트별 예상 손익 vs 실적 손익, 목표 대비 KPI 달성도를 실시간 대시보드로 제공")]));
kids.push(bul([t("단계적 전환 : ",{bold:true}),t("Agile 스프린트 방식으로 핵심부터 빠르게 가동하고, 확장(WMS/MES·품질·AI 성과관리)은 다음 단계로")]));

// ─────────── 2. 제안 배경 ───────────
kids.push(h1("2. 제안 배경 — 현황과 전환 필요성"));
kids.push(p([t("코아콘은 ",{}),t("열관리·정밀장비 제조와 연구개발",{bold:true}),t("을 함께 수행하는 첨단 기술기업으로, 표준제품의 반복 판매와 고객 맞춤형 장비 프로젝트가 혼합된 사업 구조를 가지고 있습니다. 현행 이카운트 ERP는 도입 이후 기본적인 회계·재고 관리에는 활용되고 있으나, 아래와 같은 구조적 한계가 확인됩니다.")]));
kids.push(h2("현행(이카운트) 주요 한계 — 신청 내용 기반"));
kids.push(tbl([3000,3300,3100],["구분","현행 이카운트의 한계","Odoo 전환 시 개선"],[
  ["화면·업무 분절","기능별 화면이 각각 분리되어 있어 업무 이동·중복 입력이 많음","영업기회 한 화면에서 견적·수주·배송·청구까지 연결"],
  ["불필요 기능","실제로 쓰지 않는 기능이 많아 복잡하고 사용성이 떨어짐","필요한 모듈만 선택 구성 — 단순·직관 UI"],
  ["프로젝트 손익","프로젝트형 장비 사업의 예상/실적 손익 관리가 취약","프로젝트 단위 매입·생산·외주·인건비 연결 손익(P&L)"],
  ["생산·BOM","BOM 기반 생산계획·작업지시·시리얼 추적 관리 한계","MPS→작업지시→실행, 시리얼/Lot 추적 표준 지원"],
  ["성과·KPI","목표 대비 성과를 자동으로 집계·가시화하기 어려움","KPI 대시보드·프로젝트 진척·수익률 실시간 추적"],
],{headfill:PURPLE,size:16}));
kids.push(spacer());
kids.push(h2("전환 목표"));
kids.push(bul("영업–구매–생산–재고–프로젝트–회계를 하나의 데이터 모델로 제공"));
kids.push(bul("표준제품 판매와 프로젝트형 제조·설치 비즈니스를 동시 수용"));
kids.push(bul("향후 사업 확장(생산 고도화, 품질/서비스, WMS/MES 연계, AI 성과관리)을 고려한 장기 IT 기반 마련"));

// ─────────── 3. Odoo 솔루션 개요 ───────────
kids.push(h1("3. Odoo 솔루션 개요", {br:true}));
kids.push(p([t("Odoo는 ",{}),t("영업(기회) → 구매·수출입 → 생산·재고 → 프로젝트·설치 → 재무·경영",{bold:true}),t("까지 전 업무 흐름을 단일 플랫폼으로 통합 관리하는 End-to-End ERP입니다. 각 단계 관여자(영업·구매·생산·물류·프로젝트·재무·경영)는 역할 기반으로 참여하며, 데이터는 분절 없이 연계·누적됩니다.")]));
kids.push(h2("코아콘 적용 모듈 맵"));
kids.push(tbl([2100,6300],["영역","핵심 기능"],[
  ["영업 관리(CRM/판매)","상품·영업기회·고객·수익률·견적·주문·목표관리 — 표준제품+프로젝트 2트랙"],
  ["구매·수출입","매입주문·매입청구서·수입(전자부품/센서)·공급자 관리·수출 문서"],
  ["생산 관리","BOM·생산계획(MPS)·작업장·작업지시·생산실행·자재명세"],
  ["재고 관리","입·출고·재고조정·시리얼/Lot 추적·Location(WMS 기초)"],
  ["프로젝트 관리","고객 프로젝트·R&D 개발 프로젝트·태스크·진척·수익성(P&L)"],
  ["회계·재무","AP/AR 승인·전표·외화·장부·거래처 원장·프로젝트 연계"],
  ["성과·경영(KPI)","목표 대비 달성도·프로젝트 손익·수익률 대시보드"],
],{headfill:NAVY,size:17}));
kids.push(spacer());
kids.push(p([t("특히 코아콘이 관심 모듈로 지정한 ",{}),t("발주·회계 연동 · 생산계획 · 성과/KPI 관리",{bold:true,color:PURPLE}),t("는 Odoo 기본 기능과 승인 Workflow로 우선 구현이 가능합니다.")]));

// ─────────── 4. 요구사항 정의서 ───────────
kids.push(h1("4. 요구사항 정의서 (코아콘 맞춤 1차)", {br:true}));
kids.push(p([t("아래는 코아콘의 사업 구조(열관리·정밀장비 제조 + R&D + 프로젝트형 수주)를 반영한 ",{}),t("1차 요구사항 정의",{bold:true}),t("입니다. 세부 수치·프로세스는 착수 단계의 요구사항 분석(인터뷰·현행 문서 검토)에서 확정합니다. ",{}),t("‘협의’ 표시 항목",{bold:true,color:GOLD}),t("은 분석 단계 재확인 대상입니다.")]));

function reqTable(title, rows){
  kids.push(h2(title));
  kids.push(tbl([560,1500,1500,4200,640],["No","중분류","세부","요구사항","협의"],rows,{headfill:NAVY,size:15,hsize:15,center:false}));
  kids.push(spacer());
}
// 4-1 회사개요/IT전략
reqTable("4-1. 회사 개요 · IT 전략", [
  ["1","조직 규모","인원","약 30~80명 규모의 임직원이 사용하는 것을 전제로 설계한다.",""],
  ["2","사업 구조","매출 구조","표준제품 판매(오일쿨러·히트펌프·산업용 에어컨 등)와 프로젝트형 장비(반도체 제조장비·의료기기 등)가 혼합된 2트랙 구조를 지원한다.",""],
  ["3","제품/서비스","구성","하드웨어(HW), 제어 SW, 외주 매입 품목을 포함하는 사업 구조를 가진다.",""],
  ["4","제품/서비스","수입 구조","전자부품·센서 등 일부 품목은 해외 수입 중심으로 조달한다.",[t("협의",{color:GOLD,size:15})]],
  ["5","IT 전략","ERP 중심","ERP는 Odoo를 중심 시스템으로 사용하며 이카운트를 대체한다.",""],
  ["6","IT 전략","협업툴","기존 협업툴(있을 경우)은 병행 사용하되 ERP 대체 가능 영역은 단계적으로 통합을 고려한다.",[t("협의",{color:GOLD,size:15})]],
]);
// 4-2 영업/CRM
reqTable("4-2. 영업 · CRM", [
  ["7","기본 구조","프로세스","영업 프로세스는 Lead → Opportunity → Quotation → Sales Order 단계로 관리되어야 한다.",""],
  ["8","영업 유형","2트랙","표준제품 판매와 프로젝트형 장비의 2트랙 구조로 관리하되, 세부 운영 방식은 협의한다.",[t("협의",{color:GOLD,size:15})]],
  ["9","제품 구성","Mixed Sale","하나의 견적/주문 내에 장비·부품·외주·SW 라이선스를 혼합 구성할 수 있어야 한다.",""],
  ["10","제품 구성","옵션 구조","표준제품(오일쿨러·히트펌프 등)은 사양·용량 옵션 구조로 관리한다.",""],
  ["11","손익 관리","예상 손익","견적/영업기회 단계에서 예상 매출·원가·프로젝트 손익(P&L)을 확인할 수 있어야 한다.",""],
  ["12","활동 관리","이력","각 영업기회의 미팅·통화·메모 등 Follow-up 이력이 기록·관리되어야 한다.",""],
  ["13","영업 예측","매출 예측","품목·수량·예상 납기 기준의 매출 예측으로 선발주·재고·생산 준비 판단에 활용한다.",""],
]);
// 4-3 구매/수출입
reqTable("4-3. 구매 · 수출입", [
  ["14","매입 구조","구분","매입은 국내 매입과 해외 매입으로 구분 관리되어야 한다.",""],
  ["15","매입 구조","연계","매입은 생산계획·작업지시 또는 영업/수주 기반으로 연결 관리되어야 한다.",""],
  ["16","매입 유형","구분","매입 품목은 원자재·부품·소모품·외주·수리 등으로 구분 관리한다.",""],
  ["17","수입 관리","문서","수입 부품(전자부품·센서 등)은 Invoice·Packing List·B/L 등 수입 문서를 관리한다.",[t("협의",{color:GOLD,size:15})]],
  ["18","승인","구매 승인","구매·발주·수주에 대해 Odoo 승인 Workflow가 적용되어야 한다.",""],
]);
// 4-4 제조/재고
reqTable("4-4. 제조 · 재고", [
  ["19","생산","BOM 기준","생산은 BOM 기준으로 관리되며, 단순 조립과 복합 장비 생산을 모두 지원해야 한다.",""],
  ["20","원가","생산품","생산품은 표준원가(Standard Cost = 직접비 + 표준비용) 기준으로 관리한다.",[t("협의",{color:GOLD,size:15})]],
  ["21","계획","생산계획","수요예측·수주 기반으로 생산계획(MPS)→작업지시→작업실행을 관리한다. (관심 모듈)",""],
  ["22","추적성","시리얼","장비 단위 Serial 관리 및 납품 이력 관리가 가능해야 한다.",""],
  ["23","추적성","Lot","일부 부품·소모품에 대해 Lot 관리가 가능해야 한다.",""],
  ["24","재고","위치","초기에는 Location/Bin 수준의 기본 재고 관리를 수행한다. (WMS는 확장)",""],
]);
// 4-5 회계/재무
reqTable("4-5. 회계 · 재무", [
  ["25","기본 회계","AP/AR","매입채무(AP)·매출채권(AR)은 Odoo 내에서 관리되며, 전표 입력 시 승인 단계가 적용된다.",""],
  ["26","외화","수입 거래","해외 수입 중심의 외화 거래를 관리하고, 환차손익을 계산·분개할 수 있어야 한다.",[t("협의",{color:GOLD,size:15})]],
  ["27","장부","원장","계정별·거래처별 원장, 합계잔액시산표, Aging Report를 제공해야 한다.",""],
  ["28","관리 보고","프로젝트 손익","프로젝트별 손익 현황을 제공하며, AR/AP 입력 단계에서 프로젝트를 선택할 수 있어야 한다.",""],
  ["29","마감","월 Closing","월 마감 이후 수정이 필요한 경우 Closing을 Open하고 수정할 수 있어야 한다.",""],
]);
// 4-6 프로젝트/성과
reqTable("4-6. 프로젝트 · 성과(KPI)", [
  ["30","프로젝트","전환","Opportunity를 Project로 전환하여 관리할 수 있어야 한다.",""],
  ["31","프로젝트","유형","프로젝트는 고객(장비 납품) 프로젝트와 내부 R&D·개선 프로젝트로 구분 관리한다.",""],
  ["32","비용/수익","연계","프로젝트 기준으로 매입·생산·외주·인건비·출고/설치 비용을 연결 관리한다.",""],
  ["33","손익 분석","비교","프로젝트별 예상 손익과 실적 손익을 비교 분석할 수 있어야 한다.",""],
  ["34","납품 이후","설치 이력","시리얼 기준으로 설치 이력 및 향후 유지보수/AS 관리로 확장 가능한 구조를 고려한다.",[t("협의",{color:GOLD,size:15})]],
  ["35","성과","KPI 대시보드","목표(원가·납기·품질·수익률 등) 대비 실적 달성도를 대시보드로 제공한다. (관심 모듈)",""],
]);
// 통합 요구사항
kids.push(h2("4-7. 통합(연동) 요구사항"));
kids.push(tbl([2100,3400,2900],["연동 대상","내용","비고"],[
  ["이카운트 데이터 이관","거래처·품목·BOM·재고·미결 채권채무 등 기초 데이터 이관","Phase 1 필수"],
  ["국세청 홈택스","매출·매입 세금계산서 연동","Odoo 본사 연동 개발 활용"],
  ["기업은행/전자결재","자금·지출결의 연동","API 범위 협의(견적 포함)"],
  ["모바일","모바일/외부 접속(재고 바코드 등)","Odoo 기본 앱 활용"],
  ["관세청 Unipass","수입면장·통관(해외 수입 시)","해당 시 API 협의"],
],{headfill:PURPLE,size:16}));

// ─────────── 5. 구축 방법론·일정 ───────────
kids.push(h1("5. 구축 방법론 · 일정", {br:true}));
kids.push(p([t("검증된 6단계 방법론",{bold:true}),t("(Discovery → Blueprint → Realization → Testing → Training → Go-Live)에 ",{}),t("Agile 스프린트(3~4회)",{bold:true,color:PURPLE}),t("를 접목합니다. 각 스프린트 종료 시 코아콘 Key User의 리뷰·피드백을 반영해 요구사항과 실제 시스템 간의 갭(Gap)을 최소화합니다.")]));
kids.push(tbl([1400,2600,4400],["단계","기간(안)","주요 활동·산출물"],[
  ["1. 분석 설계","1~2개월","요구사항 정의·As-Is 분석·통합 범위·WBS"],
  ["2. 설계(Blueprint)","","To-Be 설계서·화면 흐름·커스터마이징 범위 확정(Sign-off)"],
  ["3. 개발·구축","2~4개월","CRM·구매·생산·재고·회계 설정 + 이카운트 데이터 이관(스프린트 3회)"],
  ["4. 테스트","","통합·사용자 인수 테스트(UAT)·이슈 개선"],
  ["5. 교육·인수","","업무별 교육·운영 가이드·Go-Live 체크리스트"],
  ["6. Go-Live","","운영 적용 + 안정화(Hypercare) + 유지보수 전환"],
],{headfill:NAVY,size:17}));
kids.push(spacer());
kids.push(p([t("※ 표준 프로젝트 기준 약 6~9개월이며, ",{color:SUB}),t("코아콘의 실제 범위·인력에 따라 착수 시 확정",{color:SUB,bold:true}),t("합니다. 미완 기능은 차기 Phase로 이관하여 Go-Live 일정을 지킵니다.",{color:SUB})]));

// ─────────── 6. 데이터 이관 ───────────
kids.push(h2("이카운트 → Odoo 데이터 이관 방안"));
kids.push(num(1,[t("추출 : ",{bold:true}),t("이카운트에서 거래처·품목·BOM·재고·미결 채권채무를 엑셀로 추출")]));
kids.push(num(2,[t("정제·매핑 : ",{bold:true}),t("Odoo 표준 필드로 매핑(품목코드·계정·거래처 코드 정규화)")]));
kids.push(num(3,[t("적재·검증 : ",{bold:true}),t("테스트 환경에 적재 후 잔액·수량 대사(對査), 오차 0 확인")]));
kids.push(num(4,[t("전환 : ",{bold:true}),t("Go-Live 시점 기준일 재고·미결 잔액 이관 후 개시")]));

// ─────────── 7. 기대효과 ───────────
kids.push(h1("6. 기대효과 & 사업관리", {br:true}));
kids.push(h2("기대효과 (판정 KPI 예시)"));
kids.push(tbl([3600,2400,2400],["기대효과","측정 지표","목표(협의)"],[
  ["업무 통합·중복입력 해소","중복 입력 건수·처리 리드타임","단축"],
  ["프로젝트 손익 가시성","예상 vs 실적 손익 오차","관리 기준 확립"],
  ["재고·생산 정확도","재고 정확도·계획 준수율","향상"],
  ["구매·전표 통제","승인 Workflow 적용률","전 항목 적용"],
  ["경영 성과 가시화","KPI 달성도 대시보드","실시간 제공"],
],{headfill:TEAL,size:17,center:true}));
kids.push(spacer());
kids.push(h2("리스크 관리 · 고객사 참여"));
kids.push(bul([t("요구사항 동결 : ",{bold:true}),t("분석 종료 시점 Requirements Freeze, 변경은 Change Request 절차로 관리")]));
kids.push(bul([t("전담 체계 : ",{bold:true}),t("코아콘 전담 PM + 업무별 Key User(영업·구매·생산·회계·프로젝트) 지정 → 의사결정 지연 방지")]));
kids.push(bul([t("데이터·현행 문서 제공 : ",{bold:true}),t("거래처·품목·BOM·프로젝트·회계 등 기존 데이터와 현행 프로세스 문서 제공")]));
kids.push(bul([t("단계 검증 : ",{bold:true}),t("스프린트 리뷰마다 Key User 참여로 품질 확보·재개발 방지")]));

// ─────────── 8. 다음 단계 ───────────
kids.push(h1("7. 다음 단계 (Next Step)"));
kids.push(num(1,"본 1차 제안·요구사항 정의서 검토 및 피드백"));
kids.push(num(2,"현행(이카운트) 업무·데이터 기반 요구사항 분석 워크숍(업무별 1~3회)"));
kids.push(num(3,"To-Be 설계서·최종 범위·일정·견적 확정(Sign-off)"));
kids.push(num(4,"파일럿(핵심 모듈) 우선 가동 → 단계적 전면 전환"));
kids.push(spacer(16));
kids.push(new Paragraph({shading:{type:ShadingType.CLEAR,fill:HEADBG,color:"auto"},spacing:{before:120,after:60,line:300},border:{left:{style:BorderStyle.SINGLE,size:24,color:PURPLE,space:12}},children:[
  t("  제안·문의   ",{bold:true,size:20,color:NAVY}),t("에이에스씨(ASC) · AX 플랫폼 사업팀   ·   웹 odooaierp.com   ·   이메일 asclhg@gmail.com",{size:18})]}));
kids.push(p(t("본 제안서의 수치·일정·범위는 1차 제안 기준이며, 요구사항 분석 후 상호 협의하여 확정합니다.",{size:16,color:SUB,i:true}),{before:80}));

const doc=new Document({styles:{default:{document:{run:{font:F,size:20,color:INK}}}},
  sections:[{properties:{page:{margin:{top:1080,bottom:1000,left:1100,right:1100}}},children:kids}]});
Packer.toBuffer(doc).then(b=>{
  const out="/home/user/thirdbrain-web/docs/presentations/코아콘_Odoo_ERP_구축_제안서.docx";
  fs.writeFileSync(out,b); console.log("PROPOSAL",out,b.length);
});
