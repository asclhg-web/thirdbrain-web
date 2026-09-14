// AX 플랫폼 최종 발표 대본 (Word)
const fs = require("fs"), path = require("path");
const D = require("docx");
const { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel, BorderStyle } = D;
const SP = __dirname;
const NARR = JSON.parse(fs.readFileSync(path.join(SP, "final_narration.json"), "utf8"));
const F = "맑은 고딕";
const BROWN="6E3A1C", GOLD="C07F1E", TEAL="0E8F86", SUB="76675A", INK="2E241C";
function t(x,o={}){return new TextRun({text:x,font:F,size:o.size||22,bold:o.bold,color:o.color||INK,italics:o.i});}
function p(runs,o={}){return new Paragraph({children:Array.isArray(runs)?runs:[runs],spacing:{after:o.after??140,before:o.before||0,line:300},alignment:o.align});}
function h1(x){return new Paragraph({children:[t(x,{bold:true,size:26,color:BROWN})],spacing:{before:240,after:120},heading:HeadingLevel.HEADING_1,border:{bottom:{color:"E7D9C6",size:8,space:4,style:BorderStyle.SINGLE}}});}

const kids=[];
kids.push(new Paragraph({children:[t("AX 플랫폼 최종 발표 대본",{bold:true,size:40,color:BROWN})],spacing:{before:300,after:120},alignment:AlignmentType.CENTER}));
kids.push(p(t("아나운서 톤 내레이션 · 슬라이드 20장 · 약 8분",{size:22,color:SUB}),{align:AlignmentType.CENTER,after:60}));
kids.push(p(t("2026. 9 · 에이에스씨(ASC) · 발표자용",{size:18,color:SUB}),{align:AlignmentType.CENTER,after:260}));

kids.push(h1("발표 팁"));
["각 슬라이드의 내레이션을 그대로 읽으시면 됩니다 — 동영상(AX_플랫폼_최종_발표영상.mp4)의 음성과 동일한 대본입니다.",
 "숫자는 또렷하게, 쉼표에서 살짝 쉬면 아나운서 톤이 됩니다. 굵은 문장은 강조점입니다.",
 "합성 데모 고지: 거래 수치는 합성 샘플이며, 실데이터 연결 즉시 같은 화면이 실수치로 동작한다는 점을 자연스럽게 언급하세요.",
 "질문이 나오면 '결정은 언제나 사람', '숫자는 그래프가 계산, LLM은 서술만'을 기억하세요."
].forEach(x=>kids.push(p([t("· ",{bold:true,color:GOLD}),t(x)])));

NARR.forEach(s=>{
  kids.push(h1(`슬라이드 ${s.n} · ${s.title}`));
  kids.push(p([t("[내레이션] ",{bold:true,color:TEAL}),t(s.text)],{after:80}));
});

kids.push(h1("마무리"));
kids.push(p([t("핵심 한 문장: ",{bold:true,color:TEAL}),t("\"문서에 있으면 사람이 지켜야 하지만, 플랫폼이 되면 구조가 지킵니다.\" — 이 문장으로 열고 닫으면 메시지가 관통합니다.",{bold:true})]));

const doc=new Document({styles:{default:{document:{run:{font:F,size:22}}}},
  sections:[{properties:{page:{margin:{top:900,bottom:800,left:1000,right:1000}}},children:kids}]});
Packer.toBuffer(doc).then(b=>{
  const out="/home/user/thirdbrain-web/docs/presentations/AX_플랫폼_최종_발표대본.docx";
  fs.writeFileSync(out,b); console.log("SCRIPT",out,b.length);
});
