// AX 구축 플랫폼 발표자료 (16:9) — 발표용 프레젠테이션 덱
const pptxgen = require("pptxgenjs");
const path = require("path");
const S = __dirname;
const SHOT = path.join(S, "p9shots");
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
p.layout = "W";
p.author = "ASC"; p.company = "에이에스씨";
p.title = "AX 구축 플랫폼 발표자료";

// ── 색 토큰
const DEEP="2B1D12", DARK="6E3A1C", BRAND="9C5227", GOLD="E8A33D", GOLDD="C07F1E",
      TEAL="0E8F86", CREAM="F8F2EA", INK="2E241C", SUB="76675A", LINE="DCCDBB",
      RED="A8493B", CARD="FFFFFF", TINT="FDF3E0";
const F="Noto Sans KR";

function bg(s,c){ s.background={color:c}; }
function foot(s,dark){
  s.addText("AX 구축 플랫폼 · 에이에스씨(ASC) · 2026.09",
    {x:0.5,y:7.06,w:9,h:0.3,fontFace:F,fontSize:9,color:dark?"B9A78F":SUB});
}
function pageno(s,n,dark){
  s.addText(String(n),{x:12.5,y:7.02,w:0.6,h:0.32,align:"right",fontFace:F,
    fontSize:10,color:dark?"B9A78F":SUB});
}
// 표준 콘텐츠 슬라이드 헤더
function head(s,kicker,title,color){
  s.addText(kicker,{x:0.55,y:0.45,w:12,h:0.35,fontFace:F,fontSize:12,bold:true,
    color:GOLDD,charSpacing:3});
  s.addText(title,{x:0.5,y:0.78,w:12.3,h:0.75,fontFace:F,fontSize:28,bold:true,
    color:color||DARK});
  s.addShape(p.ShapeType.line,{x:0.55,y:1.62,w:2.2,h:0,line:{color:GOLD,width:3}});
}

// ═══ 1. 타이틀 (dark)
let s=p.addSlide(); bg(s,DEEP);
s.addShape(p.ShapeType.rect,{x:0,y:0,w:13.333,h:0.18,fill:{color:GOLD}});
s.addText("TAESUNGDANG × ASC — AI ERP PLATFORM",
  {x:0.9,y:1.5,w:11,h:0.5,fontFace:F,fontSize:15,bold:true,color:GOLD,charSpacing:5});
s.addText("AX 구축 플랫폼",{x:0.85,y:2.15,w:11.6,h:1.2,fontFace:F,fontSize:60,bold:true,color:CREAM});
s.addText("근거 있는 판단의 공장",{x:0.9,y:3.35,w:11.6,h:0.9,fontFace:F,fontSize:34,bold:true,color:GOLD});
s.addText([
  {text:"데이터가 모이고 · ",options:{color:"D8C6B2"}},
  {text:"AI가 근거와 함께 제안하고 · ",options:{color:"D8C6B2"}},
  {text:"사람이 승인하면 · ",options:{color:GOLD,bold:true}},
  {text:"시스템이 기록합니다",options:{color:"D8C6B2"}},
],{x:0.9,y:4.5,w:11.6,h:0.6,fontFace:F,fontSize:19});
s.addText("서버1 실운영 · odooaierp.com 공개 · Claude Opus 서술 · 테스트 149 그린",
  {x:0.9,y:5.5,w:11.6,h:0.5,fontFace:F,fontSize:15,color:TEAL,bold:true});
s.addText("2026. 9 · 에이에스씨(ASC)",{x:0.9,y:6.4,w:11,h:0.4,fontFace:F,fontSize:13,color:"B9A78F"});

// ═══ 2. 문제의식
s=p.addSlide(); bg(s,CREAM); head(s,"WHY AX","왜 AX인가 — 데이터는 있지만, 판단으로 이어지지 않는다");
const probs=[
  ["흩어진 데이터","엑셀·POS·장부·Odoo — 자료는 넘치지만 한곳에 서지 않는다"],
  ["감(感)에 의존한 결정","발주·생산·재고를 경험과 직관으로 — 근거는 사후에 찾는다"],
  ["'대시보드'의 한계","숫자는 보이지만 '왜'와 '무엇을 할지'가 없다"],
  ["떠나면 남지 않는 지식","담당자의 머릿속 노하우가 조직 자산으로 축적되지 않는다"],
];
probs.forEach((pr,i)=>{
  const x=0.55+(i%2)*6.25, y=2.0+Math.floor(i/2)*2.35;
  s.addShape(p.ShapeType.roundRect,{x,y,w:5.95,h:2.05,rectRadius:0.12,
    fill:{color:CARD},line:{color:LINE,width:1}});
  s.addShape(p.ShapeType.rect,{x,y,w:0.11,h:2.05,fill:{color:RED}});
  s.addText(pr[0],{x:x+0.3,y:y+0.22,w:5.4,h:0.5,fontFace:F,fontSize:19,bold:true,color:DARK});
  s.addText(pr[1],{x:x+0.3,y:y+0.85,w:5.45,h:1.0,fontFace:F,fontSize:14.5,color:INK,lineSpacingMultiple:1.15});
});
foot(s); pageno(s,2);

// ═══ 3. 한 줄 흐름 (chevron)
s=p.addSlide(); bg(s,CREAM); head(s,"THE FLOW","한 줄로 — 데이터에서 사람의 승인까지");
const steps=[["엑셀·장부·Odoo","M1 수집"],["표준 데이터셋","M2"],["분석·예측","M3·M4"],
  ["지식그래프","M5"],["판단 카드","M6·M7"],["사람의 승인","결정"]];
let cx=0.55;
const cw=1.95, gap=0.13;
steps.forEach((st,i)=>{
  const last=i===steps.length-1;
  s.addShape(p.ShapeType.roundRect,{x:cx,y:2.5,w:cw,h:1.5,rectRadius:0.1,
    fill:{color:last?TEAL:DARK}});
  s.addText(st[0],{x:cx,y:2.75,w:cw,h:0.7,align:"center",fontFace:F,fontSize:13.5,
    bold:true,color:"FFFFFF"});
  s.addText(st[1],{x:cx,y:3.42,w:cw,h:0.4,align:"center",fontFace:F,fontSize:11,
    color:last?"D8F3F0":GOLD});
  if(!last) s.addText("▶",{x:cx+cw-0.02,y:2.95,w:gap+0.12,h:0.6,align:"center",
    fontFace:F,fontSize:13,color:GOLDD,bold:true});
  cx+=cw+gap;
});
s.addShape(p.ShapeType.roundRect,{x:0.55,y:4.6,w:12.25,h:1.0,rectRadius:0.1,
  fill:{color:TINT},line:{color:LINE,width:1}});
s.addText([
  {text:"제안은 AI가, ",options:{color:INK}},
  {text:"결정은 언제나 사람이 ",options:{color:GOLDD,bold:true}},
  {text:"— 승인 순간에만 시스템 값이 바뀌고, 전 과정이 감사 기록으로 남습니다",options:{color:INK}},
],{x:0.85,y:4.78,w:11.6,h:0.65,fontFace:F,fontSize:16,valign:"middle"});
foot(s); pageno(s,3);

// ═══ 4. 모듈 아키텍처
s=p.addSlide(); bg(s,CREAM); head(s,"ARCHITECTURE","모듈 구성 — M0~M7 + 프로젝트·KPI 센터");
const rows=[
  ["M0","공통 기반","SSO·백업·레지스트리·감사 대장·반출 게이트"],
  ["M1","수집·인제스트","Odoo CDC·엑셀 업로더·현장 장표·IoT 센서"],
  ["M2","표준 데이터셋","스키마 6계열·매핑·품질 게이트·특징량"],
  ["M3","분석 스튜디오","EDA 6종·층별·관리도·야간 마이닝"],
  ["M4","학습 엔진","수요예측·이상탐지·모델 카드·RL 파일럿"],
  ["M5","지식그래프","4M 스키마·FACT 적재·확신도 루프·근거 API"],
  ["M6","LLM 판단","GraphRAG·판단 카드 생성·인용 강제·반출 폴백"],
  ["M7","에이전트·관제","런타임·승인함·5종 에이전트·War Room"],
];
const tRows=[[
  {text:"모듈",options:{fill:{color:DARK},color:"FFFFFF",bold:true,fontSize:13,align:"center"}},
  {text:"이름",options:{fill:{color:DARK},color:"FFFFFF",bold:true,fontSize:13}},
  {text:"핵심 구성요소",options:{fill:{color:DARK},color:"FFFFFF",bold:true,fontSize:13}},
]];
rows.forEach((r,i)=>{
  const f=i%2?"FBF6EE":"FFFFFF";
  tRows.push([
    {text:r[0],options:{fill:{color:f},color:GOLDD,bold:true,align:"center",fontSize:13}},
    {text:r[1],options:{fill:{color:f},color:DARK,bold:true,fontSize:13}},
    {text:r[2],options:{fill:{color:f},color:INK,fontSize:12.5}},
  ]);
});
s.addTable(tRows,{x:0.55,y:1.85,w:12.25,colW:[1.3,3.0,7.95],
  border:{type:"solid",color:LINE,pt:1},fontFace:F,rowH:0.56,valign:"middle"});
s.addText("코어(M1~M7·측정 엔진·보안)는 불변 — 화면 계층만 P8·P9로 재편했습니다",
  {x:0.55,y:6.75,w:12,h:0.4,fontFace:F,fontSize:12.5,italic:true,color:SUB});
pageno(s,4);

// ═══ 5. 차별점 (3 pillars)
s=p.addSlide(); bg(s,CREAM); head(s,"WHAT MAKES IT DIFFERENT","'예쁜 대시보드'가 아니라 '근거의 공장'");
const pil=[
  [GOLDD,"모든 문장에 근거","화면의 모든 수치·주장에 [근거:] 출처가 붙습니다. 인용 없는 문장은 시스템이 차단합니다."],
  [TEAL,"AI는 숫자를 못 만든다","LLM은 서술만 — 수치는 그래프·측정 엔진이 계산합니다. 환각으로 만든 숫자가 원천 차단됩니다."],
  [RED,"결정은 언제나 사람","승인 순간에만 값이 바뀝니다. 권한은 문서가 아니라 구조가 지키고, 전 과정이 감사로 남습니다."],
];
pil.forEach((c,i)=>{
  const x=0.55+i*4.15;
  s.addShape(p.ShapeType.roundRect,{x,y:2.0,w:3.9,h:4.2,rectRadius:0.12,
    fill:{color:CARD},line:{color:LINE,width:1}});
  s.addShape(p.ShapeType.roundRect,{x,y:2.0,w:3.9,h:0.9,rectRadius:0.12,fill:{color:c[0]}});
  s.addShape(p.ShapeType.rect,{x,y:2.45,w:3.9,h:0.45,fill:{color:c[0]}});
  s.addText(String(i+1),{x:x+0.25,y:2.1,w:0.7,h:0.7,fontFace:F,fontSize:30,bold:true,color:"FFFFFF"});
  s.addText(c[1],{x:x+1.0,y:2.15,w:2.8,h:0.65,fontFace:F,fontSize:17,bold:true,color:"FFFFFF",valign:"middle"});
  s.addText(c[2],{x:x+0.3,y:3.2,w:3.3,h:2.7,fontFace:F,fontSize:14.5,color:INK,lineSpacingMultiple:1.25});
});
foot(s); pageno(s,5);

// ── UI 쇼케이스 헬퍼
function uiSlide(n,kicker,title,img,caption,notes){
  const s=p.addSlide(); bg(s,CREAM); head(s,kicker,title);
  s.addShape(p.ShapeType.roundRect,{x:0.55,y:1.85,w:8.55,h:5.0,rectRadius:0.08,
    fill:{color:CARD},line:{color:LINE,width:1}});
  s.addImage({path:img,x:0.7,y:2.0,w:8.25,h:4.7,sizing:{type:"contain",w:8.25,h:4.7}});
  // 우측 설명 패널
  s.addShape(p.ShapeType.roundRect,{x:9.35,y:1.85,w:3.45,h:5.0,rectRadius:0.1,
    fill:{color:TINT},line:{color:LINE,width:1}});
  s.addText(caption,{x:9.6,y:2.1,w:2.95,h:0.9,fontFace:F,fontSize:16,bold:true,color:DARK});
  let yy=3.15;
  notes.forEach(nt=>{
    s.addText("•",{x:9.6,y:yy,w:0.3,h:0.4,fontFace:F,fontSize:14,bold:true,color:GOLDD});
    s.addText(nt,{x:9.9,y:yy,w:2.7,h:0.9,fontFace:F,fontSize:13,color:INK,lineSpacingMultiple:1.1});
    yy+=0.95;
  });
  pageno(s,n);
  return s;
}

// ═══ 6~10. UI
uiSlide(6,"UI · 오늘","① 오늘 — 하루가 이 한 화면에서 시작",
  path.join(SHOT,"today.png"),"역할별 홈 화면",
  ["로그인하면 역할에 맞는 '오늘' 화면","승인 대기·확인할 이름·미달 KPI를 할 일 카드로","무엇이든 물어보세요 — 상시 질문창"]);
uiSlide(7,"UI · 판단","② 승인함 — 오늘의 제안이 기다립니다",
  path.join(SHOT,"inbox.png"),"판단 카드 승인함",
  ["카드마다 수치 + 구간 + 근거 + 대안","'왜?' 버튼으로 원장까지 근거 역추적","승인 → 감사 로그·파라미터 즉시 기록"]);
uiSlide(8,"UI · 성과","③ 프로젝트·KPI — 무한 개선 루프",
  path.join(SHOT,"kpi.png"),"KPI 대시보드",
  ["프로젝트별 KPI 목표·기준선·측정","야간 배치 자동 측정 + [지금 측정]","측정 전은 정직하게 '측정 전' 표기"]);
uiSlide(9,"UI · 질문","④ 질문 — 근거를 인용해 답합니다",
  path.join(SHOT,"ask.png"),"자연어 질문",
  ["'왜 폐기율이 올랐어?' 자연어로","Claude Opus가 서술, 수치는 그래프에서","모든 답변 문장에 [근거:] 인용"]);
uiSlide(10,"UI · 데이터","⑤ 자료 반입 — 형식 그대로 올리면 됩니다",
  path.join(SHOT,"upload.png"),"업로드 파이프라인",
  ["엑셀·POS 파일 드래그","①업로드→②매핑→③확인할 이름→④반영","처음 보는 양식도 화면에서 매핑"]);

// ═══ 11. 구축 여정
s=p.addSlide(); bg(s,CREAM); head(s,"BUILD JOURNEY","구축 여정 — 데모에서 실운영까지");
const jr=[
  ["P2","이중 DB·CI·웹앱 v1","PostgreSQL 이중 백엔드·승인함·GPU Ollama 백엔드"],
  ["P3","실 Odoo 결선","실 인스턴스·CDC 검증·부하 시험·SLA 초안"],
  ["P4","공개 서비스화","체험 테넌트·업로드 UI·Cloudflare Tunnel·랜딩"],
  ["P5","공개 전 보안·정합","세션·CSRF·야간 정합 배치·2차 범위 실증"],
  ["P6","유료 준비","과금·자동 발급(기본 꺼짐)·저장 쿼터"],
  ["P7","프로젝트·KPI","측정 엔진·대시보드·개선 루프 에이전트"],
  ["P8","화면 재구성","14개 평면 메뉴 → 4허브·역할별 홈·용어 정리"],
  ["P9","시각 디자인","벤치마킹 기반 디자인 토큰·그림자·그라디언트"],
];
const jRows=[[
  {text:"단계",options:{fill:{color:DARK},color:"FFFFFF",bold:true,align:"center",fontSize:13}},
  {text:"핵심",options:{fill:{color:DARK},color:"FFFFFF",bold:true,fontSize:13}},
  {text:"내용",options:{fill:{color:DARK},color:"FFFFFF",bold:true,fontSize:13}},
]];
jr.forEach((r,i)=>{
  const f=i%2?"FBF6EE":"FFFFFF";
  jRows.push([
    {text:r[0],options:{fill:{color:f},color:GOLDD,bold:true,align:"center",fontSize:13}},
    {text:r[1],options:{fill:{color:f},color:DARK,bold:true,fontSize:12.5}},
    {text:r[2],options:{fill:{color:f},color:INK,fontSize:12}},
  ]);
});
s.addTable(jRows,{x:0.55,y:1.85,w:12.25,colW:[1.2,3.3,7.75],
  border:{type:"solid",color:LINE,pt:1},fontFace:F,rowH:0.55,valign:"middle"});
s.addText("각 단계는 [구현 → 양쪽 DB 테스트 → 커밋]으로 완결 — 실사용에서 나온 문제는 P#-I 번호로 기록·수정",
  {x:0.55,y:6.75,w:12.2,h:0.4,fontFace:F,fontSize:12,italic:true,color:SUB});
pageno(s,11);

// ═══ 12. 벤치마킹
s=p.addSlide(); bg(s,CREAM); head(s,"BENCHMARKING","벤치마킹 — 흡수한 강점, 지킨 원칙");
const bh=[{text:"제품",o:{}},{text:"강점(흡수)",o:{}},{text:"AX의 차이",o:{}}];
const br=[
  ["Odoo","통합 ERP·승인 워크플로","승인함을 카드로 — 수치·구간·근거·대안 한 장에"],
  ["더존 ERP","국내 회계·세무 친화","판단까지 — '무엇을 할지'를 근거와 함께 제안"],
  ["삼성SDS","대규모 AI·MLOps","중소 제조에 맞춘 경량·2서버 협업 구성"],
  ["Palantir","온톨로지·근거 추적","지식그래프 4M + 원장까지 내려가는 근거 사다리"],
  ["Power BI","KPI 카드·자연어 질문","수치 생성 금지·인용 강제로 환각 원천 차단"],
];
const bRows=[bh.map(h=>({text:h.text,options:{fill:{color:DARK},color:"FFFFFF",bold:true,fontSize:13}}))];
br.forEach((r,i)=>{
  const f=i%2?"FBF6EE":"FFFFFF";
  bRows.push([
    {text:r[0],options:{fill:{color:f},color:DARK,bold:true,fontSize:13}},
    {text:r[1],options:{fill:{color:f},color:INK,fontSize:12.5}},
    {text:r[2],options:{fill:{color:f},color:TEAL,bold:true,fontSize:12.5}},
  ]);
});
s.addTable(bRows,{x:0.55,y:1.85,w:12.25,colW:[2.0,4.6,5.65],
  border:{type:"solid",color:LINE,pt:1},fontFace:F,rowH:0.72,valign:"middle"});
s.addShape(p.ShapeType.roundRect,{x:0.55,y:6.35,w:12.25,h:0.75,rectRadius:0.08,fill:{color:TINT},line:{color:LINE,width:1}});
s.addText([
  {text:"차별점 한 줄: ",options:{bold:true,color:DARK}},
  {text:"성공한 제품의 화면 문법을 흡수하되, '근거 강제·수치 생성 금지·사람 결정'을 코어로 지켰다.",options:{color:INK}},
],{x:0.8,y:6.45,w:11.7,h:0.55,fontFace:F,fontSize:13.5,valign:"middle"});
pageno(s,12);

// ═══ 13. 지금 살아있는 시스템
s=p.addSlide(); bg(s,DEEP);
s.addText("LIVE NOW",{x:0.55,y:0.5,w:12,h:0.35,fontFace:F,fontSize:12,bold:true,color:GOLD,charSpacing:3});
s.addText("지금, 살아있는 시스템",{x:0.5,y:0.85,w:12,h:0.8,fontFace:F,fontSize:30,bold:true,color:CREAM});
s.addShape(p.ShapeType.line,{x:0.55,y:1.7,w:2.2,h:0,line:{color:GOLD,width:3}});
const live=[
  ["서버1 24시간 가동","업무 PC WSL2 — 로그인·화면·측정 실동작"],
  ["odooaierp.com 공개","Cloudflare Tunnel — 폰으로 접속 확인"],
  ["Claude Opus 서술","GPU Ollama → Claude 전환, 인용 강제 유지"],
  ["복제 소크 52사이클","CDC 정합 무결(all_ok) 지속 관찰"],
  ["테스트 149 그린","PG 149 · SQLite 144+5skip 회귀 0"],
  ["데모 시나리오 통과","M1→M7 완주·G4 6/6·웹 워크스루"],
];
live.forEach((c,i)=>{
  const x=0.55+(i%3)*4.15, y=2.15+Math.floor(i/3)*2.15;
  s.addShape(p.ShapeType.roundRect,{x,y,w:3.9,h:1.9,rectRadius:0.1,fill:{color:"3A2A1B"},line:{color:"55402A",width:1}});
  s.addText("●",{x:x+0.28,y:y+0.28,w:0.4,h:0.4,fontFace:F,fontSize:13,color:TEAL});
  s.addText(c[0],{x:x+0.72,y:y+0.25,w:3.0,h:0.55,fontFace:F,fontSize:16,bold:true,color:GOLD});
  s.addText(c[1],{x:x+0.3,y:y+0.9,w:3.35,h:0.9,fontFace:F,fontSize:13,color:"EDE3D5",lineSpacingMultiple:1.15});
});
s.addText("남은 것은 규모(데이터·고객)의 문제이지, 구축의 문제가 아닙니다",
  {x:0.55,y:6.65,w:12.2,h:0.45,fontFace:F,fontSize:15,bold:true,italic:true,color:GOLD});
pageno(s,13,true);

// ═══ 14. 디자인 개선 (P9) + 모바일
s=p.addSlide(); bg(s,CREAM); head(s,"P9 · DESIGN","더 쉽고, 더 아름답게 — P8·P9 개선");
s.addText("정보구조와 시각을 함께 손봤습니다",{x:0.55,y:1.75,w:8.3,h:0.4,fontFace:F,fontSize:15,color:SUB});
const ch=[
  ["14개 평면 메뉴 → 4허브","오늘·데이터·판단·성과 + 관리 — 길을 잃지 않습니다"],
  ["역할별 홈","관리자·스튜어드·승인자·뷰어가 각자의 첫 화면으로"],
  ["할 일 중심","할 일 카드 1클릭 이동 — 무엇을 할지 화면이 안내"],
  ["디자인 토큰·그림자·그라디언트","따뜻한 색·부드러운 카드·명료한 버튼 (P9)"],
  ["모바일 최적화","640px 이하 탭 타깃·표 스크롤 — 폰 승인 실사용"],
];
let yy=2.25;
ch.forEach(c=>{
  s.addShape(p.ShapeType.roundRect,{x:0.55,y:yy,w:8.3,h:0.82,rectRadius:0.08,fill:{color:CARD},line:{color:LINE,width:1}});
  s.addShape(p.ShapeType.rect,{x:0.55,y:yy,w:0.1,h:0.82,fill:{color:TEAL}});
  s.addText(c[0],{x:0.8,y:yy+0.08,w:8.0,h:0.35,fontFace:F,fontSize:14.5,bold:true,color:DARK});
  s.addText(c[1],{x:0.8,y:yy+0.42,w:8.0,h:0.35,fontFace:F,fontSize:12.5,color:INK});
  yy+=0.94;
});
// 모바일 캡처
s.addShape(p.ShapeType.roundRect,{x:9.3,y:2.0,w:3.5,h:4.85,rectRadius:0.12,fill:{color:DEEP}});
s.addImage({path:path.join(SHOT,"today_mobile.png"),x:9.55,y:2.2,w:3.0,h:4.45,sizing:{type:"contain",w:3.0,h:4.45}});
s.addText("모바일 '오늘'",{x:9.3,y:6.85,w:3.5,h:0.3,align:"center",fontFace:F,fontSize:11,color:SUB});
pageno(s,14);

// ═══ 15. 로드맵
s=p.addSlide(); bg(s,CREAM); head(s,"ROADMAP","다음 — 실데이터가 들어오면, 판단이 나갑니다");
const rm=[
  [GOLDD,"1  실데이터 온보딩","Odoo 읽기 전용 접속 + 24개월 판매 엑셀 — 형식 그대로, 정리는 저희 몫"],
  [TEAL,"2  파일럿 12주","파이만쥬 수요예측·발주 완주 — 결품과 폐기를 함께 줄입니다(숫자로 증명)"],
  [BRAND,"3  유료 단계","과금·자동 발급 스위치 on · 겸용 → 전용 장비 분리"],
  [DARK,"4  자산 이관","모든 산출물은 고객 자산 — 반출 통제·반환 검수까지"],
];
let ry=2.05;
rm.forEach(c=>{
  s.addShape(p.ShapeType.roundRect,{x:0.55,y:ry,w:12.25,h:1.05,rectRadius:0.1,fill:{color:CARD},line:{color:LINE,width:1}});
  s.addShape(p.ShapeType.roundRect,{x:0.55,y:ry,w:0.14,h:1.05,rectRadius:0.05,fill:{color:c[0]}});
  s.addText(c[1],{x:0.9,y:ry+0.15,w:4.0,h:0.75,fontFace:F,fontSize:18,bold:true,color:c[0],valign:"middle"});
  s.addText(c[2],{x:5.0,y:ry+0.15,w:7.6,h:0.75,fontFace:F,fontSize:14,color:INK,valign:"middle",lineSpacingMultiple:1.1});
  ry+=1.18;
});
foot(s); pageno(s,15);

// ═══ 16. 클로징 (dark)
s=p.addSlide(); bg(s,DEEP);
s.addShape(p.ShapeType.rect,{x:0,y:7.32,w:13.333,h:0.18,fill:{color:GOLD}});
s.addText("THANK YOU",{x:0.9,y:1.6,w:11,h:0.5,fontFace:F,fontSize:15,bold:true,color:GOLD,charSpacing:5});
s.addText("문서에 있으면 사람이 지켜야 하지만,",{x:0.9,y:2.4,w:11.6,h:0.8,fontFace:F,fontSize:32,bold:true,color:CREAM});
s.addText("플랫폼이 되면 구조가 지킵니다",{x:0.9,y:3.25,w:11.6,h:0.8,fontFace:F,fontSize:32,bold:true,color:GOLD});
s.addText("AX 구축 플랫폼은 '만들었다'를 넘어, 대표 장비에서 실제로 운영되고, 전 세계에 공개되고, 실데이터로 KPI를 측정하는 단계에 도달했습니다.",
  {x:0.9,y:4.5,w:11.6,h:1.0,fontFace:F,fontSize:17,color:"D8C6B2",lineSpacingMultiple:1.3});
s.addText("에이에스씨(ASC) · odooaierp.com",{x:0.9,y:6.2,w:11,h:0.4,fontFace:F,fontSize:14,color:GOLD,bold:true});

p.writeFile({ fileName: path.join("/home/user/thirdbrain-web/docs/presentations","AX_구축_플랫폼_발표자료.pptx") })
 .then(fn=>console.log("DECK", fn));
