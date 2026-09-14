// 태성당 AX 플랫폼 데모 시나리오 (16:9) — 발표자가 그대로 따라 하는 진행 대본
const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");
const SP = __dirname;
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 }); p.layout = "W";
p.author = "ASC"; p.title = "AX 플랫폼 데모 시나리오";

const DEEP="2B1D12", DARK="6E3A1C", BRAND="9C5227", GOLD="E8A33D", GOLDD="C07F1E",
      TEAL="0E8F86", CREAM="F8F2EA", INK="2E241C", SUB="76675A", LINE="DCCDBB",
      RED="A8493B", CARD="FFFFFF", TINT="FDF3E0";
const F="Noto Sans KR";
const img = n => path.join(SP, n);

function bg(s,c){ s.background={color:c}; }
function head(s,kicker,title,color){
  s.addText(kicker,{x:0.55,y:0.42,w:12,h:0.35,fontFace:F,fontSize:13,bold:true,color:GOLDD,charSpacing:3});
  s.addText(title,{x:0.5,y:0.76,w:12.4,h:0.8,fontFace:F,fontSize:27,bold:true,color:color||DARK});
  s.addShape(p.ShapeType.line,{x:0.55,y:1.62,w:2.2,h:0,line:{color:GOLD,width:3}});
}
function pageno(s,n,dark){ s.addText(String(n),{x:12.5,y:7.02,w:0.6,h:0.32,align:"right",fontFace:F,fontSize:10,color:dark?"B9A78F":SUB}); }

// STEP 슬라이드: 좌 스크린샷 + 우 4블록(클릭·화면·멘트·핵심)
function step(n, stepNo, title, imgFile, click, screen, script, key){
  const s=p.addSlide(); bg(s,CREAM); head(s,`STEP ${stepNo}`,title);
  // 좌 스크린샷
  s.addShape(p.ShapeType.roundRect,{x:0.55,y:1.8,w:7.15,h:5.05,rectRadius:0.08,fill:{color:CARD},line:{color:LINE,width:1}});
  if(imgFile && fs.existsSync(img(imgFile)))
    s.addImage({path:img(imgFile),x:0.7,y:1.95,w:6.85,h:4.75,sizing:{type:"contain",w:6.85,h:4.75}});
  // 우 패널
  const blocks=[["📍 클릭",click,GOLDD],["🖥 화면",screen,TEAL],["🗣 멘트(대사)",script,DARK],["✅ 핵심",key,RED]];
  let y=1.8;
  blocks.forEach(([lab,txt,col])=>{
    const isScript = lab.startsWith("🗣");
    const h = isScript ? 1.7 : 1.02;
    s.addShape(p.ShapeType.roundRect,{x:7.95,y,w:4.85,h,rectRadius:0.08,fill:{color:isScript?TINT:CARD},line:{color:LINE,width:1}});
    s.addShape(p.ShapeType.rect,{x:7.95,y,w:0.1,h,fill:{color:col}});
    s.addText(lab,{x:8.18,y:y+0.08,w:4.5,h:0.32,fontFace:F,fontSize:12.5,bold:true,color:col});
    s.addText(isScript?`"${txt}"`:txt,{x:8.18,y:y+0.42,w:4.5,h:h-0.5,fontFace:F,fontSize:isScript?13.5:12.5,
      color:INK,italic:isScript,lineSpacingMultiple:1.12});
    y+=h+0.12;
  });
  pageno(s,n);
}

// ═══ 1 표지
let s=p.addSlide(); bg(s,DEEP);
s.addShape(p.ShapeType.rect,{x:0,y:0,w:13.333,h:0.18,fill:{color:GOLD}});
s.addText("DEMO SCENARIO · 발표 진행 대본",{x:0.9,y:1.7,w:11,h:0.5,fontFace:F,fontSize:15,bold:true,color:GOLD,charSpacing:4});
s.addText("태성당 AX 플랫폼 데모 시나리오",{x:0.85,y:2.35,w:11.6,h:1.1,fontFace:F,fontSize:44,bold:true,color:CREAM});
s.addText("각 단계마다 [어디 클릭 · 보여줄 화면 · 말할 멘트 · 핵심]을 그대로 따라 하시면 됩니다.",
  {x:0.9,y:3.6,w:11.6,h:0.6,fontFace:F,fontSize:18,color:"D8C6B2"});
s.addText([
  {text:"로그인  ",options:{color:GOLD,bold:true}},{text:"admin / Demo!2026",options:{color:CREAM,bold:true}},
  {text:"     주소  ",options:{color:GOLD,bold:true}},{text:"https://app.odooaierp.com",options:{color:CREAM,bold:true}},
],{x:0.9,y:4.7,w:11.6,h:0.5,fontFace:F,fontSize:17});
s.addText("소요 8~10분 · 8단계 · 2026.9 · 에이에스씨(ASC)",{x:0.9,y:6.4,w:11,h:0.4,fontFace:F,fontSize:13,color:"B9A78F"});

// ═══ 2 준비 체크리스트
s=p.addSlide(); bg(s,CREAM); head(s,"준비 (데모 5분 전)","데모 시작 전 체크리스트");
const chk=[
  ["① 데이터 시딩 완료","서버1에서 sudo bash ax-platform/deploy/seed-demo.sh 실행 완료 — '데모 준비 완료' 메시지 확인"],
  ["② 로그인 확인","app.odooaierp.com 접속 → admin / Demo!2026 로그인 → '오늘' 화면이 뜨는지"],
  ["③ 승인함 카드","판단 → 승인함에 카드 11건이 보이는지 (수요예측·생산계획·재고·설비·규칙)"],
  ["④ 성과 KPI","성과 → 프로젝트·KPI에 'AX 통합 성과 시연 1차' 달성도가 보이는지"],
  ["⑤ 인터넷·화면","프로젝터·화면 공유·인터넷 연결 확인. 폰으로도 같은 주소 접속 가능(모바일 시연 대비)"],
];
let yy=2.0;
chk.forEach(c=>{
  s.addShape(p.ShapeType.roundRect,{x:0.55,y:yy,w:12.25,h:0.85,rectRadius:0.08,fill:{color:CARD},line:{color:LINE,width:1}});
  s.addShape(p.ShapeType.rect,{x:0.55,y:yy,w:0.1,h:0.85,fill:{color:TEAL}});
  s.addText(c[0],{x:0.8,y:yy+0.09,w:3.4,h:0.6,fontFace:F,fontSize:15,bold:true,color:DARK,valign:"middle"});
  s.addText(c[1],{x:4.2,y:yy+0.09,w:8.4,h:0.6,fontFace:F,fontSize:13,color:INK,valign:"middle",lineSpacingMultiple:1.05});
  yy+=0.96;
});
s.addText("문제가 있으면 마지막 장 '만약을 위한 대비'를 보세요.",{x:0.55,y:6.85,w:12,h:0.3,fontFace:F,fontSize:12,italic:true,color:SUB});
pageno(s,2);

// ═══ 3 흐름 한눈에
s=p.addSlide(); bg(s,CREAM); head(s,"OVERVIEW","데모 흐름 한눈에 — 8단계");
const flow=[["1","오늘"],["2","아침 브리핑"],["3","승인함"],["4","왜?(근거)"],["5","승인·환류"],["6","성과·KPI"],["7","질문"],["8","클로징"]];
let cx=0.55; const cw=1.45, gp=0.05;
flow.forEach((f,i)=>{
  const last=i===flow.length-1;
  s.addShape(p.ShapeType.roundRect,{x:cx,y:2.6,w:cw,h:1.4,rectRadius:0.1,fill:{color:last?TEAL:DARK}});
  s.addText(f[0],{x:cx,y:2.72,w:cw,h:0.4,align:"center",fontFace:F,fontSize:16,bold:true,color:GOLD});
  s.addText(f[1],{x:cx,y:3.2,w:cw,h:0.7,align:"center",fontFace:F,fontSize:12.5,bold:true,color:"FFFFFF"});
  if(!last) s.addText("▶",{x:cx+cw-0.02,y:3.0,w:gp+0.15,h:0.5,align:"center",fontFace:F,fontSize:11,color:GOLDD,bold:true});
  cx+=cw+gp;
});
s.addShape(p.ShapeType.roundRect,{x:0.55,y:4.7,w:12.25,h:1.5,rectRadius:0.1,fill:{color:TINT},line:{color:LINE,width:1}});
s.addText("한 문장으로 관통하는 메시지",{x:0.85,y:4.9,w:11.6,h:0.4,fontFace:F,fontSize:14,bold:true,color:GOLDD});
s.addText([{text:"\"제안은 AI가, 결정은 사람이. ",options:{bold:true,color:DARK}},
  {text:"근거 없는 문장은 이 시스템이 만들지 못합니다.\"",options:{bold:true,color:TEAL}}],
  {x:0.85,y:5.4,w:11.6,h:0.7,fontFace:F,fontSize:20,valign:"middle"});
pageno(s,3);

// ═══ 4~11 STEP
step(4,"1","로그인 → '오늘' 화면","demo_today.png",
  "app.odooaierp.com 접속 → admin / Demo!2026 로그인",
  "역할에 맞는 '오늘' 화면 — 승인 대기 카드, 무엇이든 물어보는 질문창",
  "하루는 이 한 화면에서 시작합니다. 밤사이 시스템이 만든 오늘 할 일이 카드로 모여 있고, 하나를 누르면 바로 그 화면으로 갑니다.",
  "역할별 홈 · 할 일 중심 · 길을 잃지 않는 화면");
step(5,"2","오늘 → 아침 브리핑","scn_brief.png",
  "상단 '오늘' 탭 → '아침 브리핑'",
  "어제와 달라진 것만 골라 보고 — 모든 수치에 출처(근거) 표기",
  "전부가 아니라 변화만 보고합니다. 폐기가 는 품목, 불량이 튄 라인까지. 원인을 단정하지 않고 함께 나타났다고만 말하며, 모든 숫자에 출처가 붙습니다. 아침 회의가 이 한 장으로 끝납니다.",
  "변화만 · 원인 단정 금지 · 근거 강제");
step(6,"3","판단 → 승인함","demo_inbox.png",
  "상단 '판단' 탭 → '승인함'",
  "AI 에이전트 5종이 만든 판단 카드 11건 — 수치+구간+근거+대안이 한 장에",
  "핵심 화면입니다. 내일 무엇을 몇 개 만들지, 어디에 며칠치를 발주할지. 카드마다 제안 수치와 예측 구간, 왜 그런지의 근거, 그리고 채택하지 않은 대안까지 담겨 있습니다.",
  "제안은 AI · 결정은 사람 · 근거 인용");
step(7,"4","카드의 [왜?] — 근거 사다리","scn_why.png",
  "카드 안의 근거 링크(예: Rule:RULE-0001) 클릭",
  "규칙 → 4M 조합 → 사실 → 원장 기록번호까지 내려가는 근거 사다리",
  "이 시스템의 다른 점은 '왜'에 답한다는 것입니다. 이 규칙이 어디서 왔는지, 조합과 사실을 지나 실제 원장 기록 번호까지 내려갑니다. 근거 없는 주장은 이 시스템에 존재할 수 없습니다.",
  "원장까지 역추적 · 환각 원천 차단");
step(8,"5","승인 → 환류","demo_inbox.png",
  "카드의 [승인 → 환류] 버튼 클릭 (반려 시 사유 선택)",
  "승인 즉시 감사 로그·파라미터에 기록, 이전 값도 보존(토스트 안내)",
  "승인하는 순간 세 가지가 동시에 일어납니다. 누가 언제 무엇을 승인했는지 감사 로그에 남고, 시스템 값이 바뀌고, 이전 값도 보존됩니다. 반려하면 그 사유가 다음 학습의 재료가 됩니다.",
  "사람이 결정 · 전 과정 기록 · 반려도 학습");
step(9,"6","성과 → 프로젝트·KPI","kpi_dash_run.png",
  "상단 '성과' 탭 → '프로젝트·KPI'",
  "'AX 통합 성과 시연 1차' — 경영목표 달성도(생산성 22.5%/목표20 달성, 원가 미달)",
  "우리가 세운 목표가 얼마나 달성됐는지 숫자로 봅니다. 생산성은 목표를 넘어 달성, 원가 절감은 아직 미달이라 화면이 '다음 야간 배치에서 개선 카드가 제안됩니다'로 다음 행동을 안내합니다. 이것이 무한 개선 루프입니다.",
  "성과를 숫자로 · 미달이면 개선 루프");
step(10,"7","질문 — 자연어로 묻기","scn_ask.png",
  "'오늘' 화면 질문창 또는 '판단→질문'에 질문 입력",
  "'OVEN-2 불량이 왜 높아?' → 근거를 인용해 답변",
  "궁금한 것을 그냥 말로 물으면 됩니다. 서술은 인공지능이 하지만, 수치는 반드시 그래프에서 가져오고, 모든 답변 문장에 근거가 인용됩니다. 근거 없는 대답은 나오지 않습니다.",
  "자연어 질문 · 수치 생성 금지 · 인용 강제");

// ═══ 12 클로징 멘트
s=p.addSlide(); bg(s,DEEP);
s.addShape(p.ShapeType.rect,{x:0,y:7.32,w:13.333,h:0.18,fill:{color:GOLD}});
s.addText("STEP 8 · 클로징",{x:0.9,y:1.5,w:11,h:0.5,fontFace:F,fontSize:14,bold:true,color:GOLD,charSpacing:3});
s.addText("이렇게 마무리하세요",{x:0.9,y:2.1,w:11.6,h:0.7,fontFace:F,fontSize:30,bold:true,color:CREAM});
s.addShape(p.ShapeType.roundRect,{x:0.9,y:3.1,w:11.5,h:2.2,rectRadius:0.12,fill:{color:"3A2A1B"}});
s.addText([
  {text:"\"오늘 보신 것은 태성당 구조로 만든 데이터 위에서 완전히 동작하는 판단의 공장입니다. ",options:{color:"EDE3D5"}},
  {text:"제안은 AI가, 결정은 언제나 사람이 하고, 근거 없는 문장은 이 시스템이 만들지 못합니다. ",options:{color:GOLD,bold:true}},
  {text:"실데이터 연결에 필요한 건 오두 접속과 24개월 판매 엑셀 두 가지, 12주 뒤 결품과 폐기가 함께 줄어드는 것을 숫자로 보여드리겠습니다. 감사합니다.\"",options:{color:"EDE3D5"}},
],{x:1.2,y:3.35,w:10.9,h:1.7,fontFace:F,fontSize:17,valign:"middle",lineSpacingMultiple:1.3});
s.addText("합성 샘플 고지: 거래 수치는 합성이며, 실데이터 연결 즉시 같은 화면이 실수치로 동작합니다.",
  {x:0.9,y:5.6,w:11.6,h:0.4,fontFace:F,fontSize:13,italic:true,color:"B9A78F"});
pageno(s,11,true);

// ═══ 13 예상 Q&A
s=p.addSlide(); bg(s,CREAM); head(s,"Q&A","예상 질문과 답변");
const qa=[
  ["합성 데이터인가요?","네, 태성당 구조(초량 본점·별빛샌드·파이만쥬)로 만든 합성 샘플입니다. 실데이터 연결 즉시 같은 화면이 실수치로 돕니다."],
  ["우리 데이터로 하려면?","Odoo 읽기전용 접속 + 24개월 판매 엑셀이면 시작. 형식은 지금 쓰시는 그대로, 표준화는 저희가 합니다. 12주 파일럿."],
  ["AI가 틀리면 어떡하죠?","결정은 언제나 사람이 합니다. 승인 안 하면 아무것도 안 바뀌고, 반려 사유는 다음 학습의 재료가 됩니다."],
  ["숫자를 지어내지 않나요?","LLM은 서술만 합니다. 수치는 그래프·측정 엔진이 계산하고, 인용 없는 문장은 시스템이 차단합니다."],
  ["기존 ERP와 뭐가 다른가요?","대시보드는 숫자를 보여주지만, 이건 '무엇을 할지'를 근거와 함께 제안하고 원장까지 추적됩니다."],
];
let qy=1.9;
qa.forEach(q=>{
  s.addShape(p.ShapeType.roundRect,{x:0.55,y:qy,w:12.25,h:0.94,rectRadius:0.08,fill:{color:CARD},line:{color:LINE,width:1}});
  s.addText([{text:"Q. ",options:{bold:true,color:GOLDD}},{text:q[0],options:{bold:true,color:DARK}}],
    {x:0.8,y:qy+0.08,w:11.8,h:0.35,fontFace:F,fontSize:14});
  s.addText([{text:"A. ",options:{bold:true,color:TEAL}},{text:q[1],options:{color:INK}}],
    {x:0.8,y:qy+0.44,w:11.9,h:0.45,fontFace:F,fontSize:12.5,lineSpacingMultiple:1.05});
  qy+=1.02;
});
pageno(s,12);

// ═══ 14 트러블슈팅
s=p.addSlide(); bg(s,CREAM); head(s,"BACKUP","만약을 위한 대비 (화면이 안 뜰 때)");
const tb=[
  ["화면이 안 열림 / 로그인 실패","서버1에서: sudo systemctl restart axp-web axp-scheduler → 30초 후 재접속. curl -s http://127.0.0.1:8900/health 가 {\"ok\":true}인지."],
  ["카드·KPI가 비어 있음","시딩이 안 된 것. 서버1에서: sudo bash ax-platform/deploy/seed-demo.sh 다시 실행(약 2분)."],
  ["공개 주소(app.odooaierp.com)가 안 됨","서버1 로컬에서 http://127.0.0.1:8900 으로 시연. 또는 폰이 아닌 서버1 브라우저로."],
  ["질문 답변이 느림/비어 있음","LLM 백엔드 이슈 — 결정적 조립기로 자동 폴백되므로 근거 인용 답은 나옴. 승인함·성과 화면 위주로 진행."],
  ["되돌리기(원상복구)","seed-demo.sh가 출력한 백업 파일로 복원: pg-backup-*.sql.gz / data-backup-*.tgz (명령은 스크립트 마지막 출력 참고)."],
];
let ty=1.9;
tb.forEach(x=>{
  s.addShape(p.ShapeType.roundRect,{x:0.55,y:ty,w:12.25,h:0.94,rectRadius:0.08,fill:{color:CARD},line:{color:LINE,width:1}});
  s.addShape(p.ShapeType.rect,{x:0.55,y:ty,w:0.1,h:0.94,fill:{color:RED}});
  s.addText(x[0],{x:0.8,y:ty+0.08,w:11.8,h:0.35,fontFace:F,fontSize:13.5,bold:true,color:RED});
  s.addText(x[1],{x:0.8,y:ty+0.44,w:11.9,h:0.45,fontFace:F,fontSize:12,color:INK,lineSpacingMultiple:1.05});
  ty+=1.02;
});
pageno(s,13);

p.writeFile({ fileName: path.join("/home/user/thirdbrain-web/docs/presentations","AX_데모_시나리오.pptx") })
 .then(fn=>console.log("SCENARIO", fn));
