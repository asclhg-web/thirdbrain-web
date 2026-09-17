// (주)코아콘 Odoo ERP 구축 제안서 (PPT) — 열관리·정밀장비 제조 맞춤
const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
p.layout = "W";
const F = "맑은 고딕";
const NAVY="1F3A5F", PURPLE="714B67", TEAL="0E8F86", GOLD="C07F1E", RED="B03A2E",
      INK="222B36", SUB="6B7480", LINE="C9D3DE", BG="FFFFFF", TINT="F5F8FB", HEAD="EAF0F6";
const W=13.333, H=7.5, MX=0.7;

function titleBar(s, kicker, title){
  s.addShape("rect",{x:0,y:0,w:W,h:1.15,fill:{color:NAVY}});
  s.addShape("rect",{x:0,y:1.15,w:W,h:0.06,fill:{color:PURPLE}});
  if(kicker) s.addText(kicker,{x:MX,y:0.16,w:11,h:0.3,fontFace:F,fontSize:12,color:"AEC2DA",bold:true,charSpacing:1});
  s.addText(title,{x:MX,y:0.42,w:12,h:0.6,fontFace:F,fontSize:25,color:"FFFFFF",bold:true});
  s.addText("(주)코아콘 · Odoo ERP 구축 제안",{x:W-4.6,y:0.16,w:3.9,h:0.3,fontFace:F,fontSize:10,color:"AEC2DA",align:"right"});
}
function foot(s,n){
  s.addText("에이에스씨(ASC) · AX 플랫폼 사업팀",{x:MX,y:H-0.42,w:6,h:0.3,fontFace:F,fontSize:9,color:SUB});
  s.addText(String(n),{x:W-1.0,y:H-0.42,w:0.5,h:0.3,fontFace:F,fontSize:10,color:SUB,align:"right"});
}
function bullets(s, items, x, y, w, opt={}){
  const arr=items.map(it=>({text:(typeof it==="string"?it:it.t),options:{fontFace:F,fontSize:opt.fs||14,color:opt.color||INK,bold:it.b,bullet:{code:"2022",indent:16},paraSpaceAfter:opt.sa!=null?opt.sa:8,breakLine:true}}));
  s.addText(arr,{x,y,w,h:opt.h||4,valign:"top"});
}
function chip(s,x,y,w,h,label,body,accent){
  s.addShape("roundRect",{x,y,w,h,rectRadius:0.08,fill:{color:TINT},line:{color:LINE,width:1}});
  s.addShape("rect",{x,y,w:0.09,h,fill:{color:accent||PURPLE}});
  s.addText(label,{x:x+0.2,y:y+0.12,w:w-0.35,h:0.4,fontFace:F,fontSize:14,bold:true,color:NAVY});
  s.addText(body,{x:x+0.2,y:y+0.55,w:w-0.35,h:h-0.65,fontFace:F,fontSize:11.5,color:INK,valign:"top",lineSpacingMultiple:1.02});
}

// ── 1. 표지
let s=p.addSlide(); s.background={color:NAVY};
s.addShape("rect",{x:0,y:4.7,w:W,h:0.05,fill:{color:PURPLE}});
s.addText("Odoo ERP 구축 제안서",{x:0.9,y:2.3,w:11.5,h:1.0,fontFace:F,fontSize:46,bold:true,color:"FFFFFF"});
s.addText("주식회사 코아콘 (COREcon) 귀중",{x:0.92,y:3.45,w:11,h:0.6,fontFace:F,fontSize:23,color:"E6C9A8",bold:true});
s.addText("이카운트 ERP → Odoo 통합 전환  ·  표준제품 판매 + 프로젝트형 장비를 하나로",{x:0.92,y:4.95,w:11.8,h:0.5,fontFace:F,fontSize:15,color:"AEC2DA"});
s.addText("2026. 9  ·  에이에스씨(ASC) · AX 플랫폼 사업팀  ·  odooaierp.com",{x:0.92,y:6.5,w:11.5,h:0.4,fontFace:F,fontSize:12,color:"8FA6BF"});

// ── 2. 목차
s=p.addSlide(); s.background={color:BG}; titleBar(s,"CONTENTS","목차");
const toc=[["1","제안 배경 — 이카운트 현황과 코아콘 사업 특성"],["2","Odoo 솔루션 개요 (End-to-End)"],
["3","코아콘 To-Be 아키텍처"],["4","핵심 개선 — 2트랙 영업·생산·프로젝트 손익·승인"],
["5","요구사항 정의 (핵심)"],["6","데이터 이관 · 구축 방법론 · 일정"],["7","기대효과 & 다음 단계"]];
let ty=1.7;
toc.forEach(([n,txt])=>{
  s.addShape("roundRect",{x:MX,y:ty,w:0.55,h:0.55,rectRadius:0.06,fill:{color:PURPLE}});
  s.addText(n,{x:MX,y:ty,w:0.55,h:0.55,fontFace:F,fontSize:20,bold:true,color:"FFFFFF",align:"center",valign:"middle"});
  s.addText(txt,{x:MX+0.8,y:ty,w:10.5,h:0.55,fontFace:F,fontSize:16,color:INK,valign:"middle"});
  ty+=0.72;
});
foot(s,2);

// ── 3. 제안 배경
s=p.addSlide(); s.background={color:BG}; titleBar(s,"01. BACKGROUND","제안 배경 — 이카운트 현황과 코아콘 사업 특성");
s.addText("코아콘은 오일쿨러·히트펌프·반도체 제조장비·의료기기 등 열관리·정밀장비를 제조·연구개발하는 첨단 기술기업으로, 표준제품 반복 판매와 고객 맞춤형 장비 프로젝트가 혼합된 구조입니다. 현행 이카운트 ERP는 아래 특성을 담기 어렵습니다.",
  {x:MX,y:1.42,w:12,h:0.9,fontFace:F,fontSize:13.5,color:INK,valign:"top"});
const rows=[
  ["화면·업무 분절","기능별 화면이 각각 — 이동·중복 입력 많음","영업기회 한 화면에서 견적·수주·배송·청구 연결"],
  ["불필요 기능","안 쓰는 기능이 많아 복잡·사용성 저하","필요한 모듈만 선택 구성 — 단순·직관 UI"],
  ["프로젝트 손익","장비 프로젝트 예상/실적 손익 관리 취약","프로젝트 단위 매입·생산·외주·인건비 연결 P&L"],
  ["생산·BOM·시리얼","BOM 생산계획·시리얼 추적 관리 한계","MPS→작업지시→실행, 시리얼/Lot 추적 표준 지원"],
  ["성과·KPI","목표 대비 성과 집계·가시화 어려움","원가·납기·품질·수익 KPI 대시보드"],
];
s.addTable([["구분","이카운트 현황의 한계","Odoo 전환 시 개선"].map(h=>({text:h,options:{fill:PURPLE,color:"FFFFFF",bold:true,fontFace:F,fontSize:13,align:"center",valign:"middle"}})),
  ...rows.map((r,i)=>r.map((c,j)=>({text:c,options:{fill:i%2?TINT:"FFFFFF",color:INK,fontFace:F,fontSize:12,bold:j==0,valign:"middle",align:j==0?"center":"left"}})))],
  {x:MX,y:2.5,w:12,colW:[2.7,4.65,4.65],rowH:0.62,border:{type:"solid",color:LINE,pt:0.5}});
foot(s,3);

// ── 4. Odoo 솔루션 개요
s=p.addSlide(); s.background={color:BG}; titleBar(s,"02. SOLUTION","Odoo 솔루션 개요 — End-to-End 통합");
s.addText("영업(기회) → 구매·수출입 → 생산·재고 → 프로젝트·설치 → 재무·경영까지 전 업무 흐름을 단일 플랫폼으로 통합합니다. 각 담당자는 역할 기반으로 참여하고, 데이터는 분절 없이 연계·누적됩니다.",
  {x:MX,y:1.45,w:12,h:0.7,fontFace:F,fontSize:13.5,color:INK,valign:"top"});
const flow=["영업/기회\n(제품·프로젝트)","구매·수출입\n(부품·센서)","생산\n(BOM·작업지시)","재고\n(시리얼·Lot)","프로젝트·회계\n(손익·승인)"];
let fx=MX; const fw=2.28, gap=0.15;
flow.forEach((txt,i)=>{
  s.addShape("roundRect",{x:fx,y:2.5,w:fw,h:1.1,rectRadius:0.1,fill:{color:i%2?NAVY:PURPLE}});
  s.addText(txt,{x:fx,y:2.5,w:fw,h:1.1,fontFace:F,fontSize:12.5,bold:true,color:"FFFFFF",align:"center",valign:"middle"});
  if(i<flow.length-1) s.addText("▶",{x:fx+fw-0.02,y:2.5,w:gap+0.12,h:1.1,fontFace:F,fontSize:12,color:SUB,align:"center",valign:"middle"});
  fx+=fw+gap;
});
chip(s,MX,4.0,3.85,1.7,"하나의 플랫폼","영업·구매·생산·재고·프로젝트·회계를 단일 데이터로 통합 — 중복 입력 해소.",TEAL);
chip(s,MX+4.05,4.0,3.85,1.7,"제품+프로젝트 동시","표준제품 판매와 프로젝트형 장비 수주를 한 시스템에서 관리.",PURPLE);
chip(s,MX+8.1,4.0,3.85,1.7,"승인 기반 통제","구매·전표·수주에 승인 Workflow — 시스템이 규칙을 지킴.",GOLD);
foot(s,4);

// ── 5. To-Be 아키텍처
s=p.addSlide(); s.background={color:BG}; titleBar(s,"03. ARCHITECTURE","코아콘 To-Be 아키텍처");
const blocks=[
  ["영업 관리","상품·영업기회·견적·수주 · 표준+프로젝트 2트랙",PURPLE],
  ["구매·수출입","부품·센서 수입 · 공급자 · 매입청구 · 외주",NAVY],
  ["생산","BOM · 생산계획(MPS) · 작업지시 · 작업실행",TEAL],
  ["재고","입출고 · 시리얼/Lot 추적 · 위치(WMS 기초)",PURPLE],
  ["프로젝트·회계","고객/R&D 프로젝트 · P&L · AP/AR 승인 · 전표",NAVY],
  ["성과·경영","원가·납기·품질·수익률 KPI 대시보드",GOLD],
];
const bw=3.85, bh=1.5, bgap=0.28;
blocks.forEach((b,i)=>{
  const col=i%3, row=Math.floor(i/3);
  const x=MX+col*(bw+bgap), y=1.7+row*(bh+0.35);
  s.addShape("roundRect",{x,y,w:bw,h:bh,rectRadius:0.08,fill:{color:TINT},line:{color:b[2],width:1.5}});
  s.addText(b[0],{x:x+0.2,y:y+0.15,w:bw-0.4,h:0.4,fontFace:F,fontSize:16,bold:true,color:b[2]});
  s.addText(b[1],{x:x+0.2,y:y+0.62,w:bw-0.4,h:bh-0.7,fontFace:F,fontSize:12,color:INK,valign:"top"});
});
s.addShape("roundRect",{x:MX,y:4.95,w:12,h:0.7,rectRadius:0.06,fill:{color:HEAD}});
s.addText("공통 / 기본 모듈 — 사용자·권한·조직·기준정보·승인 Workflow",{x:MX,y:4.95,w:12,h:0.7,fontFace:F,fontSize:13,bold:true,color:NAVY,align:"center",valign:"middle"});
s.addText("※ 프로젝트·시리얼·원가·매출 정보가 실시간 연결되어 운영 관리부터 경영 의사결정까지 일관된 기준의 데이터를 제공합니다.",
  {x:MX,y:5.85,w:12,h:0.5,fontFace:F,fontSize:11,color:SUB,italic:true});
foot(s,5);

// ── 6. 핵심개선 4종
s=p.addSlide(); s.background={color:BG}; titleBar(s,"04. KEY IMPROVEMENTS","핵심 개선 — 2트랙 영업 · 생산 · 프로젝트 손익 · 승인");
chip(s,MX,1.55,5.85,2.4,"① 표준제품 + 프로젝트 2트랙 영업",
  "· Lead→기회→견적→수주 파이프라인 표준화\n· 오일쿨러·히트펌프 등 표준제품은 사양·용량 옵션 구성\n· 한 견적에 장비·부품·외주·SW 혼합 구성(Mixed Sale)",TEAL);
chip(s,MX+6.15,1.55,5.85,2.4,"② BOM 생산 · 시리얼 추적",
  "· BOM 기준 생산계획(MPS)→작업지시→작업실행\n· 장비 단위 Serial, 부품/소모품 Lot 추적\n· 입고→검수→생산→출고 전 과정 이력 통합",PURPLE);
chip(s,MX,4.15,5.85,2.4,"③ 프로젝트 손익 (P&L)",
  "· Opportunity→Project 전환, 고객/R&D 구분 관리\n· 프로젝트별 매입·생산·외주·인건비·설치비 연결\n· 예상 손익 vs 실적 손익 비교 분석",NAVY);
chip(s,MX+6.15,4.15,5.85,2.4,"④ 발주 · 회계 연동 (승인)",
  "· 생산계획·수주 기반 발주 → 매입청구 → 전표\n· 구매·전표·수주에 승인 Workflow 적용\n· 외화(수입)·홈택스 세금계산서 연동",GOLD);
foot(s,6);

// ── 7. 요구사항 정의(핵심)
s=p.addSlide(); s.background={color:BG}; titleBar(s,"05. REQUIREMENTS","요구사항 정의 (핵심 1차)");
const req=[
  ["영업/CRM","Lead→기회→견적→수주 파이프라인, 표준+프로젝트 2트랙 관리"],
  ["영업/CRM","한 견적에 장비·부품·외주·SW 혼합 구성, 예상 손익(P&L) 확인"],
  ["구매/수출입","부품·센서 수입 문서 관리, 생산·수주 기반 발주 + 승인 Workflow"],
  ["생산","BOM 기준 생산계획(MPS)→작업지시→작업실행, 표준원가 관리"],
  ["재고","장비 단위 Serial·부품 Lot 추적, Location 기본 재고 관리"],
  ["프로젝트","기회→프로젝트 전환, 매입·생산·외주·인건비 연결 손익 분석"],
  ["회계","AP/AR 승인, 외화·환차손익, 계정·거래처 원장·Aging"],
  ["성과","원가·납기·품질·수익률 목표 대비 KPI 대시보드 제공"],
  ["연동","이카운트 데이터 이관 · 홈택스 · 기업은행/전자결재(협의)"],
];
s.addTable([["구분","요구사항 (세부·수치는 분석 단계 확정)"].map(h=>({text:h,options:{fill:NAVY,color:"FFFFFF",bold:true,fontFace:F,fontSize:13,align:"center",valign:"middle"}})),
  ...req.map((r,i)=>r.map((c,j)=>({text:c,options:{fill:i%2?TINT:"FFFFFF",color:INK,fontFace:F,fontSize:12,bold:j==0,valign:"middle",align:j==0?"center":"left"}})))],
  {x:MX,y:1.55,w:12,colW:[2.2,9.8],rowH:0.5,border:{type:"solid",color:LINE,pt:0.5}});
foot(s,7);

// ── 8. 이관·방법론·일정
s=p.addSlide(); s.background={color:BG}; titleBar(s,"06. METHOD & PLAN","데이터 이관 · 구축 방법론 · 일정");
s.addText("이카운트 → Odoo 데이터 이관",{x:MX,y:1.5,w:6,h:0.4,fontFace:F,fontSize:15,bold:true,color:NAVY});
bullets(s,[
  "추출 : 거래처·품목·BOM·재고·미결 채권채무를 엑셀로 추출",
  "매핑 : Odoo 표준 필드로 정규화(품목코드·계정·거래처)",
  "검증 : 테스트 환경 적재 후 잔액·수량 대사(오차 0)",
  "전환 : Go-Live 기준일 재고·미결 잔액 이관 후 개시",
],MX,1.95,5.7,{fs:12.5,sa:6});
s.addText("구축 방법론 (Agile 스프린트)",{x:MX+6.3,y:1.5,w:6,h:0.4,fontFace:F,fontSize:15,bold:true,color:NAVY});
bullets(s,[
  "Discovery(요구사항 분석) → Blueprint(설계) 확정",
  "Realization : 3~4회 스프린트로 핵심부터 가동",
  "각 스프린트 리뷰에 Key User 참여 → 갭 최소화",
  "Testing(UAT) → 교육 → Go-Live → 안정화",
],MX+6.3,1.95,5.7,{fs:12.5,sa:6});
const plan=[
  ["1. 분석·설계","1~2개월","요구사항 정의·To-Be 설계·데이터 이관 계획"],
  ["2. 개발·구축","2~4개월","영업·구매·생산·재고·프로젝트·회계 설정 + 이관(스프린트)"],
  ["3. 테스트·교육","~1개월","UAT·업무별 교육·운영 가이드"],
  ["4. Go-Live","","운영 적용 + 안정화(Hypercare)"],
];
s.addTable([["단계","기간(안)","주요 활동"].map(h=>({text:h,options:{fill:PURPLE,color:"FFFFFF",bold:true,fontFace:F,fontSize:12.5,align:"center",valign:"middle"}})),
  ...plan.map((r,i)=>r.map((c,j)=>({text:c,options:{fill:i%2?TINT:"FFFFFF",color:INK,fontFace:F,fontSize:12,valign:"middle",align:j==2?"left":"center"}})))],
  {x:MX,y:4.35,w:12,colW:[2.6,2.4,7.0],rowH:0.5,border:{type:"solid",color:LINE,pt:0.5}});
s.addText("※ 표준 기준 약 6~9개월, 코아콘 실제 범위·인력에 따라 착수 시 확정합니다.",{x:MX,y:6.55,w:12,h:0.3,fontFace:F,fontSize:11,color:SUB,italic:true});
foot(s,8);

// ── 9. 기대효과 & 다음단계
s=p.addSlide(); s.background={color:BG}; titleBar(s,"07. VALUE & NEXT","기대효과 & 다음 단계");
const kpi=[["프로젝트 손익","예상 vs 실적 손익 관리 기준 확립"],
["업무 통합","중복 입력 해소·처리 리드타임 단축"],
["생산·재고 정확도","재고 정확도·계획 준수율 향상"],
["성과 가시화","원가·납기·품질·수익 KPI 실시간 제공"]];
let kx=MX;
kpi.forEach((k,i)=>{
  s.addShape("roundRect",{x:kx,y:1.55,w:2.85,h:1.7,rectRadius:0.08,fill:{color:TINT},line:{color:TEAL,width:1.2}});
  s.addText(k[0],{x:kx,y:1.72,w:2.85,h:0.5,fontFace:F,fontSize:14.5,bold:true,color:NAVY,align:"center"});
  s.addText(k[1],{x:kx+0.15,y:2.28,w:2.55,h:0.9,fontFace:F,fontSize:11.5,color:INK,align:"center",valign:"top"});
  kx+=2.98;
});
s.addText("다음 단계 (Next Step)",{x:MX,y:3.7,w:6,h:0.4,fontFace:F,fontSize:15,bold:true,color:NAVY});
bullets(s,[
  "본 제안 검토 및 피드백",
  "현행(이카운트) 업무·데이터 기반 요구사항 분석 워크숍(업무별 1~3회)",
  "To-Be 설계·최종 범위·일정·견적 확정(Sign-off)",
  "핵심 모듈 파일럿 우선 가동 → 단계적 전면 전환",
],MX,4.15,12,{fs:13,sa:7});
s.addShape("rect",{x:MX,y:6.35,w:12,h:0.02,fill:{color:LINE}});
s.addText([{text:"제안·문의   ",options:{bold:true,color:NAVY}},{text:"에이에스씨(ASC) · AX 플랫폼 사업팀   ·   odooaierp.com   ·   asclhg@gmail.com",options:{color:INK}}],
  {x:MX,y:6.5,w:12,h:0.4,fontFace:F,fontSize:12});
foot(s,9);

const out="/home/user/thirdbrain-web/docs/presentations/코아콘_Odoo_ERP_구축_제안서.pptx";
p.writeFile({fileName:out}).then(()=>console.log("PPT",out));
