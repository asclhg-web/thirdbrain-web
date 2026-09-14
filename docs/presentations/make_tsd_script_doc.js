// 베이커리 T사 통합 발표 대본 (Word) — 3막 시나리오
const fs = require("fs"), path = require("path");
const D = require("docx");
const { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel, BorderStyle } = D;
const SP = __dirname;
const NARR = JSON.parse(fs.readFileSync(path.join(SP, "tsd_narration.json"), "utf8"));
const F = "맑은 고딕";
const BROWN="6E3A1C", GOLD="C07F1E", TEAL="0E8F86", SUB="76675A", INK="2E241C";
function t(x,o={}){return new TextRun({text:x,font:F,size:o.size||22,bold:o.bold,color:o.color||INK,italics:o.i});}
function p(runs,o={}){return new Paragraph({children:Array.isArray(runs)?runs:[runs],spacing:{after:o.after??140,before:o.before||0,line:300},alignment:o.align});}
function h1(x){return new Paragraph({children:[t(x,{bold:true,size:26,color:BROWN})],spacing:{before:240,after:120},heading:HeadingLevel.HEADING_1,border:{bottom:{color:"E7D9C6",size:8,space:4,style:BorderStyle.SINGLE}}});}
function act(x,sub){return new Paragraph({children:[t(x,{bold:true,size:32,color:GOLD})],spacing:{before:360,after:sub?40:160},alignment:AlignmentType.CENTER,pageBreakBefore:true});}

const kids=[];
kids.push(new Paragraph({children:[t("베이커리 T사 · AX 통합 발표 대본",{bold:true,size:38,color:BROWN})],spacing:{before:300,after:120},alignment:AlignmentType.CENTER}));
kids.push(p(t("맞춤 제안 + AX 플랫폼 · 슬라이드 34장 · 약 14분",{size:22,color:SUB}),{align:AlignmentType.CENTER,after:60}));
kids.push(p(t("아나운서 톤 내레이션 · 동영상(AX_베이커리T사_통합_발표영상.mp4) 음성과 동일 대본",{size:20,color:SUB}),{align:AlignmentType.CENTER,after:60}));
kids.push(p(t("2026. 9 · 에이에스씨(ASC) · 발표자용",{size:18,color:SUB}),{align:AlignmentType.CENTER,after:260}));

kids.push(h1("발표 시나리오 — 3막 구성"));
[["1막 · 귀사를 이해합니다 (슬라이드 1–4)","고객사의 70년 업력과 세 채널·세 도시 현황, 다섯 가지 특수성을 짚고, 성심당 벤치마크로 '왜 지금 AX인가'를 공감으로 엽니다."],
 ["2막 · 이렇게 설계합니다 (슬라이드 5–17)","To-Be 아키텍처를 축으로 재고·발주·회계·AI 3종·데이터 파이프라인·온톨로지·에이전트·로드맵·기대효과까지, 귀사 맞춤 설계를 그림으로 설명합니다."],
 ["3막 · 이미 동작합니다 (슬라이드 18–34)","제안이 개념에 그치지 않음을 증명합니다. 이미 구축·실운영 중인 AX 플랫폼의 여덟 모듈·판단 카드·화면·데모 결과를 실물로 보여주고 마무리합니다."]
].forEach(([a,b])=>{kids.push(p([t("■ ",{color:GOLD,bold:true}),t(a,{bold:true,color:BROWN})],{after:40}));kids.push(p(t(b,{color:SUB}),{after:120}));});

kids.push(h1("발표 팁"));
["각 슬라이드의 내레이션을 그대로 읽으시면 됩니다 — 동영상의 음성과 동일한 대본입니다.",
 "숫자는 또렷하게, 쉼표에서 살짝 쉬면 아나운서 톤이 됩니다. 굵은 문장은 강조점입니다.",
 "1·2막(1–17)은 '귀사를 위한 설계', 3막(18–34)은 '이미 만든 증거' — 이 전환을 목소리로 분명히 하세요.",
 "합성 데모 고지: 거래 수치는 합성 샘플이며, 실데이터 연결 즉시 같은 화면이 실수치로 동작한다는 점을 자연스럽게 언급하세요.",
 "질문이 나오면 '결정은 언제나 사람', '숫자는 그래프가 계산, LLM은 서술만'을 기억하세요."
].forEach(x=>kids.push(p([t("· ",{bold:true,color:GOLD}),t(x)])));

let curAct=null;
const ACTMETA={"1":["제1막 · 귀사를 이해합니다","공감으로 엽니다 — 70년 업력, 세 채널, 다섯 특수성"],
 "2":["제2막 · 이렇게 설계합니다","귀사 맞춤 To-Be — 재고·발주·AI·에이전트·로드맵"],
 "3":["제3막 · 이미 동작합니다","증거를 보입니다 — 구축 완료된 AX 플랫폼 실물"]};
NARR.forEach(s=>{
  const a=String(s.act).trim()[0];
  if(a!==curAct){curAct=a;const m=ACTMETA[a];kids.push(act(m[0]));kids.push(p(t(m[1],{size:22,color:SUB,i:true}),{align:AlignmentType.CENTER,after:180}));}
  kids.push(h1(`슬라이드 ${s.n} · ${s.title}`));
  kids.push(p([t("[내레이션] ",{bold:true,color:TEAL}),t(s.text)],{after:80}));
});

kids.push(h1("마무리 한 문장"));
kids.push(p([t("\"귀사를 위해 설계했고, 그 설계는 이미 동작합니다.\" ",{bold:true}),t("— 1·2막의 '맞춤 제안'과 3막의 '실물 플랫폼'을 하나로 묶는 닫는 문장입니다.",{color:SUB})]));

const doc=new Document({styles:{default:{document:{run:{font:F,size:22}}}},
  sections:[{properties:{page:{margin:{top:900,bottom:800,left:1000,right:1000}}},children:kids}]});
Packer.toBuffer(doc).then(b=>{
  const out="/home/user/thirdbrain-web/docs/presentations/AX_베이커리T사_통합_발표대본.docx";
  fs.writeFileSync(out,b); console.log("SCRIPT",out,b.length);
});
