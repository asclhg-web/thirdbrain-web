// 태성당 Odoo ERP 구축 제안서 (PPT) — 베이커리 맞춤, 표준제안서 구조 참조
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
  s.addText(title,{x:MX,y:0.42,w:12,h:0.6,fontFace:F,fontSize:26,color:"FFFFFF",bold:true});
  s.addText("태성당 · Odoo ERP 구축 제안",{x:W-4.3,y:0.16,w:3.6,h:0.3,fontFace:F,fontSize:10,color:"AEC2DA",align:"right"});
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
s.addText("Odoo ERP 구축 제안서",{x:0.9,y:2.35,w:11.5,h:1.0,fontFace:F,fontSize:46,bold:true,color:"FFFFFF"});
s.addText("태성당 베이커리 귀중",{x:0.92,y:3.5,w:11,h:0.6,fontFace:F,fontSize:24,color:"E6C9A8",bold:true});
s.addText("이카운트 ERP → Odoo 통합 전환  ·  원자재–생산–매장/B2B–회계를 하나로",{x:0.92,y:4.95,w:11.5,h:0.5,fontFace:F,fontSize:15,color:"AEC2DA"});
s.addText("2026. 9  ·  에이에스씨(ASC) · AX 플랫폼 사업팀  ·  odooaierp.com",{x:0.92,y:6.5,w:11.5,h:0.4,fontFace:F,fontSize:12,color:"8FA6BF"});

// ── 2. 목차
s=p.addSlide(); s.background={color:BG}; titleBar(s,"CONTENTS","목차");
const toc=[["1","제안 배경 — 이카운트 현황과 베이커리 특수성"],["2","Odoo 솔루션 개요 (End-to-End)"],
["3","베이커리 To-Be 아키텍처"],["4","핵심 개선 — 원자재·완제품·발주회계·생산"],
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
s=p.addSlide(); s.background={color:BG}; titleBar(s,"01. BACKGROUND","제안 배경 — 이카운트 현황과 베이커리 특수성");
s.addText("태성당은 원자재→반제품→완제품으로 이어지는 제조와 매장·B2B 유통을 함께 운영하는 베이커리 제조기업입니다. 현행 이카운트 ERP는 기본 회계·재고에는 쓰이나, 아래 특수성을 담기 어렵습니다.",
  {x:MX,y:1.45,w:12,h:0.8,fontFace:F,fontSize:13.5,color:INK,valign:"top"});
const rows=[
  ["화면·업무 분절","기능별 화면이 각각 — 이동·중복 입력 많음","한 화면에서 수주→생산→출고→청구 연결"],
  ["유통기한(FEFO)","원자재·완제품 유통기한/로트 관리 취약","Lot·유통기한 기반 FEFO 출고·추적"],
  ["수요예측·폐기","계절·행사 수요 편차로 결품·폐기 발생","수요예측 기반 생산계획으로 결품·폐기↓"],
  ["매장+B2B 발주","매장 판매(POS)와 B2B 발주 채널 분리","POS·B2B 주문을 하나의 재고·회계로"],
  ["성과·KPI","목표 대비 성과 집계·가시화 어려움","결품·폐기·납기·수익 KPI 대시보드"],
];
s.addTable([["구분","이카운트 현황의 한계","Odoo 전환 시 개선"].map(h=>({text:h,options:{fill:PURPLE,color:"FFFFFF",bold:true,fontFace:F,fontSize:13,align:"center",valign:"middle"}})),
  ...rows.map((r,i)=>r.map((c,j)=>({text:c,options:{fill:i%2?TINT:"FFFFFF",color:INK,fontFace:F,fontSize:12,bold:j==0,valign:"middle",align:j==0?"center":"left"}})))],
  {x:MX,y:2.45,w:12,colW:[2.6,4.7,4.7],rowH:0.62,border:{type:"solid",color:LINE,pt:0.5}});
foot(s,3);

// ── 4. Odoo 솔루션 개요
s=p.addSlide(); s.background={color:BG}; titleBar(s,"02. SOLUTION","Odoo 솔루션 개요 — End-to-End 통합");
s.addText("영업/주문 → 구매 → 생산 → 재고 → 회계까지 전 업무 흐름을 단일 플랫폼으로 통합합니다. 각 담당자는 역할 기반으로 참여하고, 데이터는 분절 없이 연계·누적됩니다.",
  {x:MX,y:1.45,w:12,h:0.7,fontFace:F,fontSize:13.5,color:INK,valign:"top"});
const flow=["주문/판매\n(매장·B2B)","구매\n(원자재)","생산\n(BOM·작업지시)","재고\n(로트·FEFO)","회계\n(AP/AR·승인)"];
let fx=MX; const fw=2.28, gap=0.15;
flow.forEach((txt,i)=>{
  s.addShape("roundRect",{x:fx,y:2.5,w:fw,h:1.1,rectRadius:0.1,fill:{color:i%2?NAVY:PURPLE}});
  s.addText(txt,{x:fx,y:2.5,w:fw,h:1.1,fontFace:F,fontSize:13,bold:true,color:"FFFFFF",align:"center",valign:"middle"});
  if(i<flow.length-1) s.addText("▶",{x:fx+fw-0.02,y:2.5,w:gap+0.12,h:1.1,fontFace:F,fontSize:12,color:SUB,align:"center",valign:"middle"});
  fx+=fw+gap;
});
chip(s,MX,4.0,3.85,1.7,"한 번의 입력, 끝까지 연결","주문·생산·출고·청구가 자동 연계되어 중복 입력과 누락을 없앱니다.",TEAL);
chip(s,MX+4.05,4.0,3.85,1.7,"현장이 그대로 데이터","POS·바코드·작업지시가 곧 재고·회계 데이터가 됩니다.",PURPLE);
chip(s,MX+8.1,4.0,3.85,1.7,"필요한 모듈만","베이커리에 필요한 기능만 구성 — 단순·직관 UI.",GOLD);
foot(s,4);

// ── 5. To-Be 아키텍처
s=p.addSlide(); s.background={color:BG}; titleBar(s,"03. ARCHITECTURE","베이커리 To-Be 아키텍처");
const blocks=[
  ["영업·주문","매장 POS · B2B 발주 · 견적 · 고객",PURPLE],
  ["구매·수입","원자재 발주 · 공급사 · 매입청구",NAVY],
  ["생산","BOM · 생산계획(MPS) · 작업지시 · 실행",TEAL],
  ["재고","입출고 · 로트/유통기한 · FEFO · 위치",PURPLE],
  ["회계·재무","AP/AR 승인 · 전표 · 세금계산서 · 원장",NAVY],
  ["성과·경영","결품·폐기·납기·수익 KPI 대시보드",GOLD],
];
let bx=MX, by=1.7; const bw=3.85, bh=1.5, bgap=0.28;
blocks.forEach((b,i)=>{
  const col=i%3, row=Math.floor(i/3);
  const x=MX+col*(bw+bgap), y=1.7+row*(bh+0.35);
  s.addShape("roundRect",{x,y,w:bw,h:bh,rectRadius:0.08,fill:{color:TINT},line:{color:b[2],width:1.5}});
  s.addText(b[0],{x:x+0.2,y:y+0.15,w:bw-0.4,h:0.4,fontFace:F,fontSize:16,bold:true,color:b[2]});
  s.addText(b[1],{x:x+0.2,y:y+0.62,w:bw-0.4,h:bh-0.7,fontFace:F,fontSize:12.5,color:INK,valign:"top"});
});
s.addShape("roundRect",{x:MX,y:4.95,w:12,h:0.7,rectRadius:0.06,fill:{color:HEAD}});
s.addText("공통 / 기본 모듈 — 사용자·권한·조직·기준정보·승인 Workflow",{x:MX,y:4.95,w:12,h:0.7,fontFace:F,fontSize:13,bold:true,color:NAVY,align:"center",valign:"middle"});
s.addText("※ 프로젝트·시리얼·원가·매출 정보가 실시간 연결되어 운영 관리부터 경영 의사결정까지 일관된 기준의 데이터를 제공합니다.",
  {x:MX,y:5.85,w:12,h:0.5,fontFace:F,fontSize:11,color:SUB,italic:true});
foot(s,5);

// ── 6. 핵심개선 ①②
s=p.addSlide(); s.background={color:BG}; titleBar(s,"04. KEY IMPROVEMENTS","핵심 개선 ① 원자재·유통기한   ② 완제품·매장/B2B");
chip(s,MX,1.55,5.85,2.4,"① 원자재 로트 · 유통기한(FEFO)",
  "· 원자재/부자재를 Lot·유통기한 단위로 입고·관리\n· 선입선출(FEFO) 자동 출고 권고로 폐기 최소화\n· 입고→검수→생산→출고 전 과정 추적성 확보",TEAL);
chip(s,MX+6.15,1.55,5.85,2.4,"② 완제품 · 매장(POS) · B2B",
  "· 매장 판매(POS)와 B2B 발주를 하나의 재고로 통합\n· 완제품 생산 후 채널별 배분·주문 처리\n· 채널·품목별 판매 분석과 재고 가시성 확보",PURPLE);
chip(s,MX,4.15,5.85,2.4,"③ 발주 · 회계 연동 (승인)",
  "· 수요/생산 기반 원자재 발주 → 매입청구 → 전표\n· 구매·전표에 Odoo 승인 Workflow 적용\n· 세금계산서(홈택스) 연동으로 손 가던 연결을 자동화",NAVY);
chip(s,MX+6.15,4.15,5.85,2.4,"④ 생산계획 · 작업지시",
  "· 수요예측·주문 기반 생산계획(MPS) 수립\n· BOM 기준 작업지시 → 현장 작업실행 → 실적\n· 생산 실적·재고가 실시간 반영, 납기 대응력↑",GOLD);
foot(s,6);

// ── 7. 요구사항 정의(핵심)
s=p.addSlide(); s.background={color:BG}; titleBar(s,"05. REQUIREMENTS","요구사항 정의 (핵심 1차)");
const req=[
  ["영업/주문","매장 POS·B2B 발주를 하나의 재고·회계로 통합 관리한다"],
  ["영업/주문","고객·거래처별 단가·여신 관리, 채널별 판매 분석을 제공한다"],
  ["구매","원자재 발주는 생산계획·주문 기반으로 연결되며 승인 Workflow가 적용된다"],
  ["생산","BOM 기준 생산계획(MPS)→작업지시→작업실행을 관리한다"],
  ["재고","원자재·완제품을 Lot·유통기한으로 관리하고 FEFO 출고를 지원한다"],
  ["회계","AP/AR 전표에 승인 단계가 적용되고, 세금계산서(홈택스)를 연동한다"],
  ["성과","결품·폐기율·납기·수익 등 목표 대비 KPI를 대시보드로 제공한다"],
  ["연동","이카운트 데이터(거래처·품목·BOM·재고·미결잔액)를 이관한다"],
];
s.addTable([["구분","요구사항 (세부·수치는 분석 단계 확정)"].map(h=>({text:h,options:{fill:NAVY,color:"FFFFFF",bold:true,fontFace:F,fontSize:13,align:"center",valign:"middle"}})),
  ...req.map((r,i)=>r.map((c,j)=>({text:c,options:{fill:i%2?TINT:"FFFFFF",color:INK,fontFace:F,fontSize:12.5,bold:j==0,valign:"middle",align:j==0?"center":"left"}})))],
  {x:MX,y:1.6,w:12,colW:[2.2,9.8],rowH:0.55,border:{type:"solid",color:LINE,pt:0.5}});
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
// 일정 표
const plan=[
  ["1. 분석·설계","1~2개월","요구사항 정의·To-Be 설계·데이터 이관 계획"],
  ["2. 개발·구축","2~4개월","POS·발주·생산·재고·회계 설정 + 이관(스프린트)"],
  ["3. 테스트·교육","~1개월","UAT·업무별 교육·운영 가이드"],
  ["4. Go-Live","","운영 적용 + 안정화(Hypercare)"],
];
s.addTable([["단계","기간(안)","주요 활동"].map(h=>({text:h,options:{fill:PURPLE,color:"FFFFFF",bold:true,fontFace:F,fontSize:12.5,align:"center",valign:"middle"}})),
  ...plan.map((r,i)=>r.map((c,j)=>({text:c,options:{fill:i%2?TINT:"FFFFFF",color:INK,fontFace:F,fontSize:12,valign:"middle",align:j==2?"left":"center"}})))],
  {x:MX,y:4.35,w:12,colW:[2.6,2.4,7.0],rowH:0.5,border:{type:"solid",color:LINE,pt:0.5}});
s.addText("※ 표준 기준 약 4~7개월, 태성당 실제 범위·인력에 따라 착수 시 확정합니다.",{x:MX,y:6.55,w:12,h:0.3,fontFace:F,fontSize:11,color:SUB,italic:true});
foot(s,8);

// ── 9. 기대효과 & 다음단계
s=p.addSlide(); s.background={color:BG}; titleBar(s,"07. VALUE & NEXT","기대효과 & 다음 단계");
const kpi=[["결품·폐기","수요예측 기반 생산계획으로 결품·폐기 감소"],
["납기·정확도","재고 정확도·계획 준수율 향상"],
["업무 통합","중복 입력 해소·처리 리드타임 단축"],
["성과 가시화","목표 대비 KPI 달성도 실시간 제공"]];
let kx=MX;
kpi.forEach((k,i)=>{
  s.addShape("roundRect",{x:kx,y:1.55,w:2.85,h:1.7,rectRadius:0.08,fill:{color:TINT},line:{color:TEAL,width:1.2}});
  s.addText(k[0],{x:kx,y:1.72,w:2.85,h:0.5,fontFace:F,fontSize:15,bold:true,color:NAVY,align:"center"});
  s.addText(k[1],{x:kx+0.15,y:2.25,w:2.55,h:0.9,fontFace:F,fontSize:11.5,color:INK,align:"center",valign:"top"});
  kx+=2.98;
});
s.addText("다음 단계 (Next Step)",{x:MX,y:3.7,w:6,h:0.4,fontFace:F,fontSize:15,bold:true,color:NAVY});
bullets(s,[
  "본 제안 검토 및 피드백",
  "현행(이카운트) 업무·데이터 기반 요구사항 분석 워크숍",
  "To-Be 설계·최종 범위·일정·견적 확정(Sign-off)",
  "핵심 모듈 파일럿 우선 가동 → 단계적 전면 전환",
],MX,4.15,12,{fs:13,sa:7});
s.addShape("rect",{x:MX,y:6.35,w:12,h:0.02,fill:{color:LINE}});
s.addText([{text:"제안·문의   ",options:{bold:true,color:NAVY}},{text:"에이에스씨(ASC) · AX 플랫폼 사업팀   ·   odooaierp.com   ·   asclhg@gmail.com",options:{color:INK}}],
  {x:MX,y:6.5,w:12,h:0.4,fontFace:F,fontSize:12});
foot(s,9);

const out="/home/user/thirdbrain-web/docs/presentations/태성당_Odoo_ERP_구축_제안서.pptx";
p.writeFile({fileName:out}).then(()=>console.log("PPT",out));
