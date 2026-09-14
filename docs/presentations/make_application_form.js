// 에이에스씨 AX 플랫폼 구축 참가 신청서 — 1장
const fs = require("fs");
const D = require("docx");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, BorderStyle, ShadingType, VerticalAlign } = D;

const F = "맑은 고딕";
const BROWN="6E3A1C", GOLD="C07F1E", INK="2E241C", SUB="76675A", LINE="D9C7B0", HEADBG="F3E9DA";

function t(x,o={}){return new TextRun({text:x,font:F,size:o.size||18,bold:o.bold,color:o.color||INK,italics:o.i});}
function p(runs,o={}){return new Paragraph({children:Array.isArray(runs)?runs:[runs],
  spacing:{after:o.after??40,before:o.before||0,line:o.line||240},alignment:o.align});}

const CHK="☐ ";
function cell(children,o={}){
  return new TableCell({
    width:{size:o.w,type:WidthType.DXA},
    columnSpan:o.span,
    verticalAlign:VerticalAlign.CENTER,
    margins:{top:40,bottom:40,left:90,right:90},
    shading:o.head?{type:ShadingType.CLEAR,fill:HEADBG,color:"auto"}:undefined,
    children:Array.isArray(children)?children:[children]});
}
function label(x){return cell(p(t(x,{bold:true,size:17,color:BROWN}),{after:0}),{w:o=>o,head:true});}

// helper: label cell w/ width, value cell w/ width
function LC(x,w){return cell(p(t(x,{bold:true,size:17,color:BROWN}),{after:0}),{w,head:true});}
function VC(x,w,span){return cell(p(t(x||" ",{size:17,color:x?INK:SUB}),{after:0}),{w,span});}

const TW=9360; // table width (DXA) — content area for A4 w/ 1440 margins
const rowH=(cells)=>new TableRow({children:cells});

function fieldTable(rows){
  return new Table({width:{size:TW,type:WidthType.DXA},columnWidths:rows.cw,
    borders:{top:{style:BorderStyle.SINGLE,size:4,color:LINE},bottom:{style:BorderStyle.SINGLE,size:4,color:LINE},
      left:{style:BorderStyle.SINGLE,size:4,color:LINE},right:{style:BorderStyle.SINGLE,size:4,color:LINE},
      insideHorizontal:{style:BorderStyle.SINGLE,size:4,color:LINE},insideVertical:{style:BorderStyle.SINGLE,size:4,color:LINE}},
    rows:rows.rows});
}

const kids=[];

// 제목
kids.push(new Paragraph({children:[t("AX 플랫폼 구축 참가 신청서",{bold:true,size:36,color:BROWN})],
  alignment:AlignmentType.CENTER,spacing:{before:60,after:60}}));
kids.push(p(t("AI ERP 통합 플랫폼(odooaierp.com) 도입 · 파일럿 · 구축 참가 신청",{size:18,color:SUB}),
  {align:AlignmentType.CENTER,after:200}));

// ── 1. 신청기업 정보
kids.push(p(t("1. 신청기업 정보",{bold:true,size:20,color:GOLD}),{after:60,before:40}));
{
  const cw=[1900,2780,1900,2780];
  const rows=[
    rowH([LC("기업명",cw[0]),VC("",cw[1]),LC("대표자",cw[2]),VC("",cw[3])]),
    rowH([LC("사업자등록번호",cw[0]),VC("",cw[1]),LC("업종/업태",cw[2]),VC("",cw[3])]),
    rowH([LC("소재지",cw[0]),VC("",cw[1]+cw[2]+cw[3],3)]),
    rowH([LC("담당자",cw[0]),VC("",cw[1]),LC("직위/부서",cw[2]),VC("",cw[3])]),
    rowH([LC("연락처",cw[0]),VC("",cw[1]),LC("이메일",cw[2]),VC("",cw[3])]),
  ];
  kids.push(fieldTable({cw,rows}));
}

// ── 2. 참가 구분
kids.push(p(t("2. 참가 구분  (해당 항목에 ☑ 표시)",{bold:true,size:20,color:GOLD}),{after:60,before:140}));
{
  const cw=[3120,3120,3120];
  const rows=[
    rowH([
      cell(p([t(CHK,{bold:true}),t("체험판 (무료)",{size:17})],{after:0}),{w:cw[0]}),
      cell(p([t(CHK,{bold:true}),t("파일럿 (본점/1개 라인)",{size:17})],{after:0}),{w:cw[1]}),
      cell(p([t(CHK,{bold:true}),t("정식 구축 (전사)",{size:17})],{after:0}),{w:cw[2]}),
    ]),
  ];
  kids.push(fieldTable({cw,rows}));
}

// ── 3. 관심 모듈 / 목표
kids.push(p(t("3. 관심 모듈 · 목표",{bold:true,size:20,color:GOLD}),{after:60,before:140}));
{
  const cw=[4680,4680];
  const rows=[
    rowH([LC("관심 모듈",1560),cell([
      p([t(CHK),t("수요예측  ",{size:16}),t(CHK),t("재고 최적화  ",{size:16}),t(CHK),t("발주·회계 연동",{size:16})],{after:20}),
      p([t(CHK),t("설비 예지보전  ",{size:16}),t(CHK),t("생산계획  ",{size:16}),t(CHK),t("성과·KPI 관리",{size:16})],{after:0}),
    ],{w:cw[1]+cw[0]-1560,span:1})]),
    rowH([LC("목표 KPI",1560),VC("예) 결품률 30% 개선 · 폐기율 절감 · 납기 단축 · 재고회전 향상",cw[1]+cw[0]-1560)]),
  ];
  kids.push(fieldTable({cw:[1560,7800],rows}));
}

// ── 4. 신청 내용 / 요청사항
kids.push(p(t("4. 신청 내용 · 요청사항",{bold:true,size:20,color:GOLD}),{after:60,before:140}));
{
  const rows=[
    rowH([cell([p(t(" ",{size:16}),{after:60}),p(t(" ",{size:16}),{after:60}),p(t(" ",{size:16}),{after:0})],{w:TW})]),
  ];
  kids.push(fieldTable({cw:[TW],rows}));
}

// ── 5. 개인정보 수집·이용 동의
kids.push(p(t("5. 개인정보 수집·이용 동의",{bold:true,size:20,color:GOLD}),{after:40,before:140}));
kids.push(p(t("에이에스씨(ASC)는 본 신청서에 기재된 기업·담당자 정보를 AX 플랫폼 도입 상담·구축 목적에 한하여 수집·이용하며, 목적 달성 후 지체 없이 파기합니다. 보유기간: 상담 종료 후 1년.",{size:15,color:SUB}),{after:40,line:220}));
kids.push(p([t(CHK,{bold:true}),t("위 개인정보 수집·이용에 동의합니다.  ",{size:16,bold:true}),
  t("(미동의 시 상담 진행이 제한될 수 있습니다.)",{size:14,color:SUB})],{after:120}));

// ── 서명란
kids.push(p([t("작성일 :  ",{size:17}),t("20      년        월        일",{size:17,color:SUB})],
  {align:AlignmentType.RIGHT,after:40,before:60}));
kids.push(p([t("신청기업 :  ",{size:17}),t("                                    ",{size:17}),
  t("   대표자 :  ",{size:17}),t("                       ",{size:17}),t("(서명 또는 인)",{size:14,color:SUB})],
  {align:AlignmentType.RIGHT,after:160}));

// ── 접수처
{
  const cw=[TW];
  const rows=[
    rowH([cell([
      p(t("접수처 · 문의",{bold:true,size:17,color:BROWN}),{after:30}),
      p([t("에이에스씨(ASC)  ·  AX 플랫폼 사업팀",{size:15})],{after:20}),
      p([t("웹 : odooaierp.com     ",{size:15}),t("이메일 : asclhg@gmail.com",{size:15})],{after:0}),
    ],{w:TW,head:true})]),
  ];
  kids.push(fieldTable({cw,rows}));
}

const doc=new Document({
  styles:{default:{document:{run:{font:F,size:18,color:INK}}}},
  sections:[{properties:{page:{margin:{top:1000,bottom:800,left:1040,right:1040}}},children:kids}]});

Packer.toBuffer(doc).then(b=>{
  const out="/home/user/thirdbrain-web/docs/presentations/AX_플랫폼_구축_참가신청서.docx";
  fs.writeFileSync(out,b); console.log("FORM",out,b.length);
});
