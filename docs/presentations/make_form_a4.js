// Odoo ERP 및 AX 플랫폼 제안 참가 신청서 — A4 한 장 꽉 채움
const fs = require("fs");
const D = require("docx");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, BorderStyle, ShadingType, VerticalAlign, HeightRule } = D;

const F = "맑은 고딕";
const BROWN="6E3A1C", GOLD="C07F1E", INK="2E241C", SUB="76675A", LINE="D9C7B0", HEADBG="F3E9DA";
const CHK="☐ ";

function t(x,o={}){return new TextRun({text:x,font:F,size:o.size||22,bold:o.bold,color:o.color||INK,italics:o.i});}
function p(runs,o={}){return new Paragraph({children:Array.isArray(runs)?runs:[runs],
  spacing:{after:o.after??60,before:o.before||0,line:o.line||280},alignment:o.align});}
function sec(x){return p(t(x,{bold:true,size:26,color:GOLD}),{after:90,before:220});}

const TW=9360, RH=560;           // 표 폭, 기본 행 높이(키움)
function row(cells,h){return new TableRow({height:{value:h||RH,rule:HeightRule.ATLEAST},children:cells});}
function cell(children,o={}){
  return new TableCell({width:{size:o.w,type:WidthType.DXA},columnSpan:o.span,
    verticalAlign:VerticalAlign.CENTER,margins:{top:70,bottom:70,left:120,right:120},
    shading:o.head?{type:ShadingType.CLEAR,fill:HEADBG,color:"auto"}:undefined,
    children:Array.isArray(children)?children:[children]});
}
const LC=(x,w)=>cell(p(t(x,{bold:true,size:21,color:BROWN}),{after:0}),{w,head:true});
const VC=(x,w,span)=>cell(p(t(x||" ",{size:21,color:x?INK:SUB}),{after:0}),{w,span});
function tbl(cw,rows){
  const b=(s)=>({style:BorderStyle.SINGLE,size:6,color:LINE});
  return new Table({width:{size:TW,type:WidthType.DXA},columnWidths:cw,
    borders:{top:b(),bottom:b(),left:b(),right:b(),insideHorizontal:b(),insideVertical:b()},rows});
}

const kids=[];

// 제목
kids.push(new Paragraph({children:[t("Odoo ERP 및 AX 플랫폼 제안 참가 신청서",{bold:true,size:40,color:BROWN})],
  alignment:AlignmentType.CENTER,spacing:{before:120,after:80}}));
kids.push(new Paragraph({border:{bottom:{style:BorderStyle.SINGLE,size:12,color:GOLD,space:6}},
  children:[t("",{size:2})],spacing:{after:140}}));

// 1. 신청기업 정보
kids.push(sec("1. 신청기업 정보"));
{
  const cw=[1900,2780,1900,2780];
  kids.push(tbl(cw,[
    row([LC("기업명",cw[0]),VC("",cw[1]),LC("대표자",cw[2]),VC("",cw[3])]),
    row([LC("업종",cw[0]),VC("",cw[1]+cw[2]+cw[3],3)]),
    row([LC("담당자",cw[0]),VC("",cw[1]),LC("직위/부서",cw[2]),VC("",cw[3])]),
    row([LC("연락처",cw[0]),VC("",cw[1]),LC("이메일",cw[2]),VC("",cw[3])]),
  ]));
}

// 2. 신청 구분
kids.push(sec("2. 신청 구분  (해당 항목에 ☑ 표시)"));
{
  const cw=[3120,3120,3120];
  kids.push(tbl(cw,[ row([
    cell(p([t(CHK,{bold:true,size:22}),t("Odoo ERP 구축 제안서",{size:21,bold:true})],{after:0}),{w:cw[0]}),
    cell(p([t(CHK,{bold:true,size:22}),t("Odoo-AX 구축 제안서",{size:21,bold:true})],{after:0}),{w:cw[1]}),
    cell(p([t(CHK,{bold:true,size:22}),t("AX 구축 방법론 책자(PDF본)",{size:21,bold:true})],{after:0}),{w:cw[2]}),
  ],640) ]));
}

// 3. AX 관심 모듈 · 목표
kids.push(sec("3. AX 관심 모듈 · 목표"));
{
  const cw=[1700,7660];
  kids.push(tbl(cw,[
    row([LC("관심 모듈",cw[0]),cell([
      p([t(CHK,{size:22}),t("수요예측     ",{size:21}),t(CHK,{size:22}),t("재고 최적화     ",{size:21}),t(CHK,{size:22}),t("발주·회계 연동",{size:21})],{after:60}),
      p([t(CHK,{size:22}),t("설비 예지보전     ",{size:21}),t(CHK,{size:22}),t("생산계획     ",{size:21}),t(CHK,{size:22}),t("성과·KPI 관리",{size:21})],{after:0}),
    ],{w:cw[1]})],820),
    row([LC("목표 KPI",cw[0]),VC("예) 결품률 30% 개선 · 폐기율 절감 · 납기 단축 · 재고회전 향상",cw[1])]),
  ]));
}

// 4. 신청 내용 · 요청사항  (큰 박스)
kids.push(sec("4. 신청 내용 · 요청사항"));
kids.push(tbl([TW],[ row([cell([
  p(t(" ",{size:22}),{after:180}),p(t(" ",{size:22}),{after:180}),
  p(t(" ",{size:22}),{after:180}),p(t(" ",{size:22}),{after:0}),
],{w:TW})],1900) ]));

// 5. 개인정보 수집·이용 동의
kids.push(sec("5. 개인정보 수집·이용 동의"));
kids.push(p(t("에이에스씨(ASC)는 본 신청서에 기재된 기업·담당자 정보를 AX 플랫폼 도입 상담·구축 목적에 한하여 수집·이용하며, 목적 달성 후 지체 없이 파기합니다. 보유기간: 상담 종료 후 1년.",{size:18,color:SUB}),{after:60,line:300}));
kids.push(p([t(CHK,{bold:true,size:22}),t("위 개인정보 수집·이용에 동의합니다.  ",{size:20,bold:true}),
  t("(미동의 시 상담 진행이 제한될 수 있습니다.)",{size:16,color:SUB})],{after:200}));

// 서명란
kids.push(p([t("작성일 :   ",{size:22}),t("20        년          월          일",{size:22,color:SUB})],
  {align:AlignmentType.RIGHT,after:80,before:80}));
kids.push(p([t("신청기업 :  ",{size:22}),t("                                         ",{size:22}),
  t("   신청자 :  ",{size:22}),t("                        ",{size:22}),t("(서명 또는 인)",{size:16,color:SUB})],
  {align:AlignmentType.RIGHT,after:260}));

// 접수처
kids.push(tbl([TW],[ row([cell([
  p(t("접수처 · 문의",{bold:true,size:21,color:BROWN}),{after:50}),
  p(t("에이에스씨(ASC)  ·  AX 플랫폼 사업팀",{size:19}),{after:36}),
  p([t("웹 : odooaierp.com · asc.kr        ",{size:19}),t("이메일 : asclhg@gmail.com",{size:19})],{after:0}),
],{w:TW,head:true})],1000) ]));

const doc=new Document({styles:{default:{document:{run:{font:F,size:22,color:INK}}}},
  sections:[{properties:{page:{size:{width:11906,height:16838},margin:{top:1000,bottom:900,left:1040,right:1040}}},children:kids}]});

Packer.toBuffer(doc).then(b=>{
  const out="/home/user/thirdbrain-web/docs/presentations/AX_플랫폼_구축_참가신청서.docx";
  fs.writeFileSync(out,b); console.log("FORM",out,b.length);
});
