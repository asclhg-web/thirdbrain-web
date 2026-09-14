// AX 플랫폼 최종 발표자료 — 제안 덱 계승 + 구축 완료·실운영 결과 (16:9)
const pptxgen = require("pptxgenjs");
const path = require("path"); const fs = require("fs");
const SP = __dirname;
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 }); p.layout = "W";
p.author = "ASC"; p.title = "AX 플랫폼 최종 발표자료";

const DEEP="2B1D12", DARK="6E3A1C", BRAND="9C5227", GOLD="E8A33D", GOLDD="C07F1E",
      TEAL="0E8F86", CREAM="F8F2EA", INK="2E241C", SUB="76675A", LINE="DCCDBB",
      RED="A8493B", CARD="FFFFFF", TINT="FDF3E0";
const F="Noto Sans KR";
const img = n => path.join(SP, n);
let N=0;
function bg(s,c){ s.background={color:c}; }
function pageno(s,dark){ N++; s.addText(String(N),{x:12.5,y:7.02,w:0.6,h:0.32,align:"right",fontFace:F,fontSize:10,color:dark?"B9A78F":SUB}); }
function head(s,kicker,title,color){
  s.addText(kicker,{x:0.55,y:0.42,w:12,h:0.35,fontFace:F,fontSize:12.5,bold:true,color:GOLDD,charSpacing:3});
  s.addText(title,{x:0.5,y:0.76,w:12.4,h:0.8,fontFace:F,fontSize:26,bold:true,color:color||DARK});
  s.addShape(p.ShapeType.line,{x:0.55,y:1.6,w:2.2,h:0,line:{color:GOLD,width:3}});
}
function tbl(rows,ws){
  return rows;
}
function makeTable(s,x,y,ws,header,rows){
  const T=[header.map(h=>({text:h,options:{fill:{color:DARK},color:"FFFFFF",bold:true,fontSize:12.5,align:"center"}}))];
  rows.forEach((r,i)=>{ const f=i%2?"FBF6EE":"FFFFFF";
    T.push(r.map((c,j)=>({text:String(c.t!=null?c.t:c),options:{fill:{color:f},
      color:(c.c||(j===0?DARK:INK)),bold:!!c.b||j===0,fontSize:12,align:c.a}})));});
  s.addTable(T,{x,y,w:ws.reduce((a,b)=>a+b,0),colW:ws,border:{type:"solid",color:LINE,pt:1},fontFace:F,rowH:0.42,valign:"middle"});
}
// UI 쇼케이스
function uiSlide(kicker,title,imgFile,caption,notes){
  const s=p.addSlide(); bg(s,CREAM); head(s,kicker,title);
  s.addShape(p.ShapeType.roundRect,{x:0.55,y:1.8,w:8.5,h:5.05,rectRadius:0.08,fill:{color:CARD},line:{color:LINE,width:1}});
  if(fs.existsSync(img(imgFile))) s.addImage({path:img(imgFile),x:0.7,y:1.95,w:8.2,h:4.75,sizing:{type:"contain",w:8.2,h:4.75}});
  s.addShape(p.ShapeType.roundRect,{x:9.3,y:1.8,w:3.5,h:5.05,rectRadius:0.1,fill:{color:TINT},line:{color:LINE,width:1}});
  s.addText(caption,{x:9.55,y:2.05,w:3.0,h:0.9,fontFace:F,fontSize:15.5,bold:true,color:DARK});
  let yy=3.05; notes.forEach(nt=>{
    s.addText("•",{x:9.55,y:yy,w:0.3,h:0.4,fontFace:F,fontSize:14,bold:true,color:GOLDD});
    s.addText(nt,{x:9.85,y:yy,w:2.75,h:0.95,fontFace:F,fontSize:12.5,color:INK,lineSpacingMultiple:1.1});
    yy+=1.0; });
  pageno(s);
}
// 큰 다이어그램 이미지 슬라이드
function diagSlide(kicker,title,imgFile,foot){
  const s=p.addSlide(); bg(s,CREAM); head(s,kicker,title);
  s.addImage({path:img(imgFile),x:0.7,y:1.75,w:11.95,h:4.95,sizing:{type:"contain",w:11.95,h:4.95}});
  if(foot) s.addText(foot,{x:0.6,y:6.8,w:12,h:0.4,align:"center",fontFace:F,fontSize:12.5,italic:true,color:SUB});
  pageno(s);
}

// ═══ 1 표지
let s=p.addSlide(); bg(s,DEEP);
s.addShape(p.ShapeType.rect,{x:0,y:0,w:13.333,h:0.18,fill:{color:GOLD}});
s.addText("BUILT & LIVE — FINAL",{x:0.9,y:1.4,w:11,h:0.5,fontFace:F,fontSize:15,bold:true,color:GOLD,charSpacing:5});
s.addText("AX 플랫폼",{x:0.85,y:1.95,w:11.6,h:1.1,fontFace:F,fontSize:58,bold:true,color:CREAM});
s.addText("제안에서 구축 완료, 그리고 실운영까지",{x:0.9,y:3.2,w:11.6,h:0.8,fontFace:F,fontSize:30,bold:true,color:GOLD});
s.addText("모듈 단위 설계 M0~M7 — 오픈소스로 지은 '근거 있는 판단의 공장'",
  {x:0.9,y:4.15,w:11.6,h:0.5,fontFace:F,fontSize:17,color:"D8C6B2"});
s.addText([{text:"서버1 실운영 · ",options:{color:"D8C6B2"}},{text:"odooaierp.com 공개 · ",options:{color:"D8C6B2"}},
  {text:"Claude Opus 서술 · ",options:{color:GOLD,bold:true}},{text:"테스트 155 그린 · WAPE 7.0%",options:{color:"D8C6B2"}}],
  {x:0.9,y:5.15,w:11.6,h:0.5,fontFace:F,fontSize:15,bold:true});
s.addText("2026. 9 · 에이에스씨(ASC)",{x:0.9,y:6.4,w:11,h:0.4,fontFace:F,fontSize:13,color:"B9A78F"});
pageno(s,true);

// ═══ 2 개요
s=p.addSlide(); bg(s,CREAM); head(s,"OVERVIEW","방법론을 소프트웨어로 굳혔다 — 제안이 구축이 되다");
s.addText([{text:"질문에서 출발해 ",options:{}},{text:"— 엑셀·수작업 장표·Odoo 원장을 표준 데이터셋으로 모으고, 여러 알고리즘으로 마이닝하며, 지식그래프에 의미로 연결해, LLM이 근거와 함께 추론하고, 에이전트가 제안하되 사람이 승인한다.",options:{}}],
  {x:0.55,y:1.75,w:12.2,h:0.9,fontFace:F,fontSize:15,color:INK,lineSpacingMultiple:1.3});
const flow=[["엑셀·장부·Odoo","M1"],["표준 데이터셋","M2"],["분석·예측","M3·M4"],["지식그래프","M5"],["판단 카드","M6·M7"],["사람의 승인","결정"]];
let cx=0.55; const cw=1.95, gp=0.13;
flow.forEach((f,i)=>{ const last=i===flow.length-1;
  s.addShape(p.ShapeType.roundRect,{x:cx,y:2.9,w:cw,h:1.4,rectRadius:0.1,fill:{color:last?TEAL:DARK}});
  s.addText(f[0],{x:cx,y:3.1,w:cw,h:0.7,align:"center",fontFace:F,fontSize:13,bold:true,color:"FFFFFF"});
  s.addText(f[1],{x:cx,y:3.75,w:cw,h:0.35,align:"center",fontFace:F,fontSize:11,color:last?"D8F3F0":GOLD});
  if(!last) s.addText("▶",{x:cx+cw-0.02,y:3.25,w:gp+0.12,h:0.5,align:"center",fontFace:F,fontSize:13,color:GOLDD,bold:true});
  cx+=cw+gp; });
s.addShape(p.ShapeType.roundRect,{x:0.55,y:4.75,w:12.25,h:1.9,rectRadius:0.1,fill:{color:TINT},line:{color:LINE,width:1}});
s.addText("이 방법론을 여덟 모듈(M0~M7)로 굳혔고 — 지금은 제안이 아니라 결과입니다:",{x:0.85,y:4.95,w:11.6,h:0.4,fontFace:F,fontSize:14,bold:true,color:DARK});
const bullets=[["서버1 24시간 실운영","odooaierp.com 공개"],["전 파이프라인 데모 완주","WAPE 7.0%·이상탐지 13일 선행"],["판단 카드·근거 인용","규칙 승격·SOP 개정"],["프로젝트·KPI 달성도","경영목표 3/4 달성"]];
bullets.forEach((b,i)=>{ const bx=0.9+(i%2)*6.0, by=5.45+Math.floor(i/2)*0.6;
  s.addText([{text:"✓ ",options:{color:TEAL,bold:true}},{text:b[0]+" — ",options:{bold:true,color:INK}},{text:b[1],options:{color:SUB}}],
    {x:bx,y:by,w:5.9,h:0.5,fontFace:F,fontSize:12.5}); });
pageno(s);

// ═══ 3 벤치마크
s=p.addSlide(); bg(s,CREAM); head(s,"BENCHMARK","다섯 거인에게 배운 것 — 가져올 것과 AX가 지킨 원칙");
makeTable(s,0.55,1.85,[2.3,4.5,5.45],["제품","가져온 것","AX가 실제 지킨 것"],[
  [{t:"Palantir",b:1},"온톨로지 객체 + 운영 액션 결합",{t:"지식그래프 4M + 원장까지 근거 사다리",c:TEAL,b:1}],
  [{t:"삼성SDS",b:1},"분석 라이프사이클 통합(UX)",{t:"중소 제조 경량·2서버 협업(서버1+GPU)",c:TEAL,b:1}],
  [{t:"Power BI",b:1},"KPI 카드·자연어 질문",{t:"수치 생성 금지·인용 강제로 환각 차단",c:TEAL,b:1}],
  [{t:"Odoo",b:1},"통합 ERP·승인 워크플로",{t:"승인함 카드 — 수치·구간·근거·대안 한 장",c:TEAL,b:1}],
  [{t:"마키나락스",b:1},"제조 버티컬 MLOps",{t:"모델 카드·확신도 승격 루프·재학습 자동",c:TEAL,b:1}],
]);
s.addShape(p.ShapeType.roundRect,{x:0.55,y:6.15,w:12.25,h:0.85,rectRadius:0.08,fill:{color:TINT},line:{color:LINE,width:1}});
s.addText([{text:"버릴 것: ",options:{bold:true,color:RED}},{text:"폐쇄 생태계·고비용 종속. ",options:{color:INK}},
  {text:"지킨 원칙: ",options:{bold:true,color:DARK}},{text:"근거 강제 · 수치 생성 금지 · 결정은 사람 — 오픈소스로.",options:{color:INK}}],
  {x:0.8,y:6.28,w:11.7,h:0.6,fontFace:F,fontSize:13.5,valign:"middle"});
pageno(s);

// ═══ 4 아키텍처 다이어그램
diagSlide("ARCHITECTURE","여덟 모듈의 지도 — 데이터는 흐르고, 판단은 올라간다","diag_arch.png",
  "판단은 위로(모듈이 앱에 판단 카드 공급), 데이터는 아래로(앱의 실적·승인이 재학습 재료) — M0가 전부를 받친다");

// ═══ 5 M0·M1·M2
s=p.addSlide(); bg(s,CREAM); head(s,"MODULES 1/3 · 구축 완료","기반과 입구 — M0 공통기반 · M1 수집 · M2 표준 데이터셋");
makeTable(s,0.55,1.85,[1.2,3.0,6.0,2.05],["모듈","이름","구현 내용","상태"],[
  [{t:"M0",c:GOLDD},"공통 기반","SSO·권한·3-2-1 백업·복구 시험·커스터디 3장치(레지스트리·대장·반출게이트)",{t:"완료",c:TEAL,a:"center",b:1}],
  [{t:"M1",c:GOLDD},"수집·인제스트","엑셀 업로더·현장 장표·Odoo CDC·IoT — 개인정보 차단 목록",{t:"완료",c:TEAL,a:"center",b:1}],
  [{t:"M2",c:GOLDD},"표준 데이터셋","스키마 6계열·매핑·품질 게이트·특징량 저장소(미매핑률 0.1%)",{t:"완료",c:TEAL,a:"center",b:1}],
]);
s.addText("실측: 복제 소크 무결(all_ok) 지속 · 미매핑률 0.1% · 백업/복구 리허설 통과",{x:0.55,y:3.6,w:12,h:0.4,fontFace:F,fontSize:13,italic:true,color:SUB});
s.addShape(p.ShapeType.roundRect,{x:0.55,y:4.15,w:12.25,h:2.5,rectRadius:0.1,fill:{color:TINT},line:{color:LINE,width:1}});
s.addText("커스터디 3장치 — '반출 게이트'가 사설망을 지킨다",{x:0.85,y:4.35,w:11.6,h:0.4,fontFace:F,fontSize:15,bold:true,color:DARK});
["레지스트리 — 어떤 스키마·모델이 있는지 대장으로 관리","자산 대장 — 데이터·산출물의 출처·이동을 기록(감사)","반출 게이트 — 사설망 밖으로 나가는 것을 통제(Claude 서술만 옵트인 반출)"].forEach((t,i)=>{
  s.addText([{text:"• ",options:{color:GOLDD,bold:true}},{text:t,options:{color:INK}}],{x:0.9,y:4.85+i*0.5,w:11.5,h:0.45,fontFace:F,fontSize:13}); });
pageno(s);

// ═══ 6 M3·M4
s=p.addSlide(); bg(s,CREAM); head(s,"MODULES 2/3 · 구축 완료","작업대와 서랍장 — M3 분석 스튜디오 · M4 학습 엔진");
makeTable(s,0.55,1.85,[1.2,3.0,6.0,2.05],["모듈","이름","구현 내용","실측"],[
  [{t:"M3",c:GOLDD},"분석 스튜디오","EDA 팩(층별·파레토·관리도)·야간 마이닝→아침 브리핑·보드",{t:"완료",c:TEAL,a:"center",b:1}],
  [{t:"M4",c:GOLDD},"학습 엔진","수요예측(GBM 분위수)·이상탐지·모델 카드·RL 파일럿",{t:"완료",c:TEAL,a:"center",b:1}],
]);
const stat=[["WAPE 7.0%","수요예측 — 출발선 19.4% 대비 64% 개선",TEAL],["13일 선행","OVEN-2 고장 예지 — 재현율 100%",GOLDD],["오경보 2.8%","정상 설비 오경보율 — 낮게 유지",BRAND],["Twin 검증","디지털 트윈 재생 검증 통과",DARK]];
stat.forEach((c,i)=>{ const x=0.55+(i%2)*6.15, y=3.65+Math.floor(i/2)*1.5;
  s.addShape(p.ShapeType.roundRect,{x,y,w:5.9,h:1.35,rectRadius:0.1,fill:{color:CARD},line:{color:LINE,width:1}});
  s.addShape(p.ShapeType.rect,{x,y,w:0.11,h:1.35,fill:{color:c[2]}});
  s.addText(c[0],{x:x+0.3,y:y+0.2,w:5.4,h:0.5,fontFace:F,fontSize:22,bold:true,color:c[2]});
  s.addText(c[1],{x:x+0.3,y:y+0.78,w:5.4,h:0.5,fontFace:F,fontSize:12.5,color:INK}); });
pageno(s);

// ═══ 7 알고리즘 지도
diagSlide("ALGORITHM MAP","알고리즘 선택 지도 — 문제의 질문이 서랍을 고른다","diag_algo.png",
  "수요예측·이상탐지·최적화·인과추론 — 문제 유형마다 검증된 알고리즘을 배치, 모델 카드로 관리");

// ═══ 8 M5·M6·M7
s=p.addSlide(); bg(s,CREAM); head(s,"MODULES 3/3 · 구축 완료","의미와 실행 — M5 지식그래프 · M6 LLM 판단 · M7 에이전트");
makeTable(s,0.55,1.85,[1.2,3.0,6.0,2.05],["모듈","이름","구현 내용","실측"],[
  [{t:"M5",c:GOLDD},"지식그래프","4M 스키마·FACT 적재·확신도 루프(70%·3회→승격)·근거 API",{t:"규칙 2건 승격",c:TEAL,a:"center",b:1}],
  [{t:"M6",c:GOLDD},"LLM 판단","GraphRAG·판단 카드 조립·인용 강제·반출 폴백(Claude/Ollama)",{t:"회귀 30/30",c:TEAL,a:"center",b:1}],
  [{t:"M7",c:GOLDD},"에이전트·관제","런타임·승인함·5종 에이전트·War Room·HITL",{t:"카드 11건",c:TEAL,a:"center",b:1}],
]);
s.addShape(p.ShapeType.roundRect,{x:0.55,y:3.7,w:12.25,h:2.95,rectRadius:0.1,fill:{color:TINT},line:{color:LINE,width:1}});
s.addText("실증된 근거 사다리 (데모에서 실제로 나온 규칙)",{x:0.85,y:3.9,w:11.6,h:0.4,fontFace:F,fontSize:15,bold:true,color:DARK});
["① 규칙 — 설비 OVEN-2 × 공급사 V2 조합에서 불량률이 유의하게 높다 (확신도 88%)","② 조합 — equipment_id=OVEN-2 × vendor=V2 (이 규칙이 가리키는 4M 조합)","③ 사실 — 불량 이벤트 1,470건 · 불량 12,992개 (집계 구간)","④ 원장 — 불량ID·제조오더 번호·일자·유형까지 (응답 7.6ms)"].forEach((t,i)=>{
  s.addText([{text:t.split(" — ")[0]+" — ",options:{color:GOLDD,bold:true}},{text:t.split(" — ")[1],options:{color:INK}}],
    {x:0.9,y:4.4+i*0.52,w:11.6,h:0.48,fontFace:F,fontSize:12.5}); });
pageno(s);

// ═══ 9 판단 카드 다이어그램
diagSlide("JUDGMENT CARD","플랫폼의 최종 산출 — 판단 카드와 다섯 박자","diag_card.png",
  "모든 모듈의 산출이 한 형식으로 수렴 — {제안·수치·구간·근거 경로·대안·승인자·상태}. M7만이 원장 파라미터를 쓴다");

// ═══ 10 3대 차별점
s=p.addSlide(); bg(s,CREAM); head(s,"WHAT MAKES IT DIFFERENT","'예쁜 대시보드'가 아니라 '근거의 공장'");
const pil=[[GOLDD,"모든 문장에 근거","화면의 모든 수치·주장에 [근거:] 출처. 인용 없는 문장은 시스템이 차단."],
  [TEAL,"AI는 숫자를 못 만든다","LLM은 서술만 — 수치는 그래프·측정 엔진이 계산. 환각 원천 차단."],
  [RED,"결정은 언제나 사람","승인 순간에만 값이 바뀐다. 권한은 구조가 지키고 전 과정이 감사로 남는다."]];
pil.forEach((c,i)=>{ const x=0.55+i*4.15;
  s.addShape(p.ShapeType.roundRect,{x,y:2.0,w:3.9,h:4.3,rectRadius:0.12,fill:{color:CARD},line:{color:LINE,width:1}});
  s.addShape(p.ShapeType.roundRect,{x,y:2.0,w:3.9,h:0.95,rectRadius:0.12,fill:{color:c[0]}});
  s.addShape(p.ShapeType.rect,{x,y:2.5,w:3.9,h:0.45,fill:{color:c[0]}});
  s.addText(String(i+1),{x:x+0.25,y:2.12,w:0.7,h:0.7,fontFace:F,fontSize:30,bold:true,color:"FFFFFF"});
  s.addText(c[1],{x:x+1.0,y:2.15,w:2.8,h:0.7,fontFace:F,fontSize:17,bold:true,color:"FFFFFF",valign:"middle"});
  s.addText(c[2],{x:x+0.3,y:3.25,w:3.3,h:2.9,fontFace:F,fontSize:14.5,color:INK,lineSpacingMultiple:1.25}); });
pageno(s);

// ═══ 11~14 UI
uiSlide("UI · 오늘","① 오늘 — 하루가 이 한 화면에서","demo_today.png","역할별 홈",
  ["로그인하면 역할에 맞는 '오늘'","승인 대기·확인할 이름·미달 KPI를 할 일로","상시 질문창"]);
uiSlide("UI · 판단","② 승인함 — 오늘의 제안이 기다립니다","demo_inbox.png","판단 카드 승인함",
  ["카드마다 수치+구간+근거+대안","'왜?'로 원장까지 역추적","승인→감사 로그 즉시 기록"]);
uiSlide("UI · 성과","③ 프로젝트·KPI — 달성도를 숫자로","kpi_dash_run.png","KPI 달성도",
  ["경영목표 3/4 달성(생산성·납기·품질)","원가 미달 → 개선 카드 안내","무한 개선 루프"]);
uiSlide("UI · 질문","④ 질문 — 근거를 인용해 답합니다","scn_ask.png","자연어 질문",
  ["'OVEN-2 왜 불량?' 자연어로","Claude Opus 서술·수치는 그래프","모든 답변에 [근거:] 인용"]);

// ═══ 15 데모 실행 결과
s=p.addSlide(); bg(s,DEEP);
s.addText("DEMO RESULT",{x:0.55,y:0.5,w:12,h:0.35,fontFace:F,fontSize:12.5,bold:true,color:GOLD,charSpacing:3});
s.addText("전 파이프라인 실행 결과 — 합성 데모, 67초 완주",{x:0.5,y:0.85,w:12,h:0.8,fontFace:F,fontSize:26,bold:true,color:CREAM});
s.addShape(p.ShapeType.line,{x:0.55,y:1.7,w:2.2,h:0,line:{color:GOLD,width:3}});
const res=[["WAPE 7.0%","수요예측(출발선 19.4%)"],["13일 선행","OVEN-2 고장 예지"],["카드 11건","5종 에이전트 제안"],["규칙 2건","확신도 승격→SOP 개정"],["회귀 30/30","판단 정합성 시험"],["KPI 3/4 달성","경영목표 달성도"]];
res.forEach((c,i)=>{ const x=0.55+(i%3)*4.15, y=2.1+Math.floor(i/3)*2.2;
  s.addShape(p.ShapeType.roundRect,{x,y,w:3.9,h:1.95,rectRadius:0.1,fill:{color:"3A2A1B"},line:{color:"55402A",width:1}});
  s.addText(c[0],{x:x+0.3,y:y+0.28,w:3.35,h:0.7,fontFace:F,fontSize:26,bold:true,color:GOLD});
  s.addText(c[1],{x:x+0.3,y:y+1.05,w:3.35,h:0.7,fontFace:F,fontSize:13.5,color:"EDE3D5"}); });
s.addText("합성 샘플 위에서 완전히 동작 — 실데이터 연결 즉시 같은 계산이 실수치로 돕니다",{x:0.55,y:6.7,w:12.2,h:0.4,fontFace:F,fontSize:13,italic:true,color:"B9A78F"});
pageno(s,true);

// ═══ 16 구축 여정
s=p.addSlide(); bg(s,CREAM); head(s,"BUILD JOURNEY","구축 여정 — 제안(P1) 이후 실제로 걸어온 길");
makeTable(s,0.55,1.8,[1.3,3.4,7.55],["단계","핵심","내용"],[
  [{t:"P2",c:GOLDD},"이중 DB·CI·웹앱","PostgreSQL 이중 백엔드·승인함·GPU Ollama 백엔드"],
  [{t:"P3",c:GOLDD},"실 Odoo 결선","실 인스턴스·CDC 검증·부하 시험·SLA"],
  [{t:"P4",c:GOLDD},"공개 서비스화","체험 테넌트·업로드 UI·Cloudflare Tunnel"],
  [{t:"P5",c:GOLDD},"보안·정합","세션·CSRF·야간 정합 배치·2차 범위 실증"],
  [{t:"P6",c:GOLDD},"유료 준비","과금·자동 발급·저장 쿼터"],
  [{t:"P7",c:GOLDD},"프로젝트·KPI","측정 엔진·대시보드·개선 루프"],
  [{t:"P8",c:GOLDD},"화면 재구성","4허브·역할별 홈·용어 정리"],
  [{t:"P9",c:GOLDD},"디자인·데모","시각 폴리시·메인 랜딩·KPI 정의·데모 시딩"],
]);
pageno(s);

// ═══ 17 실행계획
s=p.addSlide(); bg(s,CREAM); head(s,"EXECUTION PLAN","작업실행 계획 — 세 단계, 32주 (현재 위치)");
const ph=[[TEAL,"1단계 · 수직 완주 (12주) — 완료·실증","M0 지반 + 수요예측이 M1→M7을 얇게 관통 · 첫 판단 카드 승인·환류 완료"],
  [GOLDD,"2단계 · 수평 확장 (12주) — 코어 구현 완료, 실데이터 대기","재고·생산 + 설비예지 앱, RL·이상탐지 가동 · 4대 중 3앱 카드 가동"],
  [BRAND,"3단계 · 지능 심화 (8주) — 설계·일부 선행","확신도 루프 심화·자동실행 승급·KPI 자동 계산(지식센터)"]];
let py=2.0;
ph.forEach(c=>{ s.addShape(p.ShapeType.roundRect,{x:0.55,y:py,w:12.25,h:1.35,rectRadius:0.1,fill:{color:CARD},line:{color:LINE,width:1}});
  s.addShape(p.ShapeType.roundRect,{x:0.55,y:py,w:0.14,h:1.35,rectRadius:0.05,fill:{color:c[0]}});
  s.addText(c[1],{x:0.9,y:py+0.15,w:11.9,h:0.5,fontFace:F,fontSize:16,bold:true,color:c[0]});
  s.addText(c[2],{x:0.9,y:py+0.68,w:11.9,h:0.55,fontFace:F,fontSize:13,color:INK,lineSpacingMultiple:1.1});
  py+=1.5; });
s.addText("현재: 1단계 완주·실증 + 2단계 코어 구현 완료 → 실데이터 온보딩 시 파일럿 12주 진입",{x:0.55,y:6.75,w:12.2,h:0.4,fontFace:F,fontSize:13,bold:true,italic:true,color:DARK});
pageno(s);

// ═══ 18 지금 살아있는 시스템
s=p.addSlide(); bg(s,DEEP);
s.addText("LIVE NOW",{x:0.55,y:0.5,w:12,h:0.35,fontFace:F,fontSize:12.5,bold:true,color:GOLD,charSpacing:3});
s.addText("지금, 살아있는 시스템",{x:0.5,y:0.85,w:12,h:0.8,fontFace:F,fontSize:26,bold:true,color:CREAM});
s.addShape(p.ShapeType.line,{x:0.55,y:1.7,w:2.2,h:0,line:{color:GOLD,width:3}});
const live=[["서버1 24시간 가동","업무 PC WSL2 — 로그인·화면·측정"],["odooaierp.com 공개","Cloudflare Tunnel — 폰 접속 확인"],["Claude Opus 서술","인용 강제 유지·반출 옵트인"],["복제 소크 무결","CDC 정합 all_ok 지속"],["테스트 155 그린","PG 155 · SQLite 150+5skip"],["데모 시나리오 통과","M1→M7·KPI 달성·웹 워크스루"]];
live.forEach((c,i)=>{ const x=0.55+(i%3)*4.15, y=2.15+Math.floor(i/3)*2.15;
  s.addShape(p.ShapeType.roundRect,{x,y,w:3.9,h:1.9,rectRadius:0.1,fill:{color:"3A2A1B"},line:{color:"55402A",width:1}});
  s.addText("●",{x:x+0.28,y:y+0.28,w:0.4,h:0.4,fontFace:F,fontSize:13,color:TEAL});
  s.addText(c[0],{x:x+0.72,y:y+0.25,w:3.0,h:0.55,fontFace:F,fontSize:15.5,bold:true,color:GOLD});
  s.addText(c[1],{x:x+0.3,y:y+0.9,w:3.35,h:0.9,fontFace:F,fontSize:12.5,color:"EDE3D5",lineSpacingMultiple:1.15}); });
s.addText("남은 것은 규모(데이터·고객)의 문제이지, 구축의 문제가 아닙니다",{x:0.55,y:6.65,w:12.2,h:0.45,fontFace:F,fontSize:15,bold:true,italic:true,color:GOLD});
pageno(s,true);

// ═══ 19 로드맵
s=p.addSlide(); bg(s,CREAM); head(s,"ROADMAP","다음 — 실데이터가 들어오면, 판단이 나갑니다");
const rm=[[GOLDD,"1  실데이터 온보딩","Odoo 읽기전용 접속 + 24개월 판매 엑셀 — 형식 그대로, 정리는 저희 몫"],
  [TEAL,"2  파일럿 12주","수요예측·발주 완주 — 결품과 폐기를 함께 줄입니다(숫자로 증명)"],
  [BRAND,"3  KPI 자동 계산","계산식을 지식센터에 등록 — 수기에서 Odoo 자동 측정으로"],
  [DARK,"4  유료·자산 이관","과금 on · 겸용→전용 장비 · 모든 산출물은 고객 자산"]];
let ry=2.05;
rm.forEach(c=>{ s.addShape(p.ShapeType.roundRect,{x:0.55,y:ry,w:12.25,h:1.05,rectRadius:0.1,fill:{color:CARD},line:{color:LINE,width:1}});
  s.addShape(p.ShapeType.roundRect,{x:0.55,y:ry,w:0.14,h:1.05,rectRadius:0.05,fill:{color:c[0]}});
  s.addText(c[1],{x:0.9,y:ry+0.15,w:4.0,h:0.75,fontFace:F,fontSize:18,bold:true,color:c[0],valign:"middle"});
  s.addText(c[2],{x:5.0,y:ry+0.15,w:7.6,h:0.75,fontFace:F,fontSize:13.5,color:INK,valign:"middle",lineSpacingMultiple:1.1});
  ry+=1.18; });
pageno(s);

// ═══ 20 클로징
s=p.addSlide(); bg(s,DEEP);
s.addShape(p.ShapeType.rect,{x:0,y:7.32,w:13.333,h:0.18,fill:{color:GOLD}});
s.addText("CLOSING",{x:0.9,y:1.5,w:11,h:0.5,fontFace:F,fontSize:15,bold:true,color:GOLD,charSpacing:5});
s.addText("방법론이 제품이 될 때",{x:0.9,y:2.2,w:11.6,h:0.8,fontFace:F,fontSize:34,bold:true,color:CREAM});
s.addText("DMAIC는 M3와 게이트로, 3정5S는 M2의 품질 게이트로, 커스터디 헌장은 M0의 반출 게이트로, 판단 카드는 M6·M7의 스키마로 — 문서의 방법론이 구조로 굳었습니다.",
  {x:0.9,y:3.2,w:11.6,h:1.0,fontFace:F,fontSize:16,color:"D8C6B2",lineSpacingMultiple:1.3});
s.addText("\"문서에 있으면 사람이 지켜야 하지만, 플랫폼이 되면 구조가 지킵니다.\"",{x:0.9,y:4.5,w:11.6,h:0.6,fontFace:F,fontSize:22,bold:true,color:GOLD});
s.addText("구조가 지키는 회사는 — 담당자가 바뀌어도, 지원이 끝나도, 축적을 잃지 않습니다.",{x:0.9,y:5.3,w:11.6,h:0.5,fontFace:F,fontSize:15,color:"D8C6B2"});
s.addText("에이에스씨(ASC) · odooaierp.com",{x:0.9,y:6.4,w:11,h:0.4,fontFace:F,fontSize:14,bold:true,color:GOLD});
pageno(s,true);

p.writeFile({ fileName: path.join("/home/user/thirdbrain-web/docs/presentations","AX_플랫폼_최종_발표자료.pptx") })
 .then(fn=>console.log("FINAL DECK", fn, "slides", N));
