// AX 플랫폼 데모 시연 시나리오 (진행자용 런북) — Word
const fs = require("fs");
const D = require("docx");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, BorderStyle, ShadingType, HeadingLevel, VerticalAlign } = D;

const F = "맑은 고딕";
const BROWN="6E3A1C", GOLD="C07F1E", TEAL="0E8F86", RED="B03A2E", INK="2E241C", SUB="76675A", LINE="D9C7B0", HEADBG="F3E9DA", TINT="FBF6EE";
function t(x,o={}){return new TextRun({text:x,font:F,size:o.size||21,bold:o.bold,color:o.color||INK,italics:o.i});}
function p(runs,o={}){return new Paragraph({children:Array.isArray(runs)?runs:[runs],spacing:{after:o.after??100,before:o.before||0,line:o.line||276},alignment:o.align});}
function h1(x,o={}){return new Paragraph({heading:HeadingLevel.HEADING_1,pageBreakBefore:o.br,spacing:{before:o.br?0:260,after:130},border:{bottom:{color:"E7D9C6",size:8,space:4,style:BorderStyle.SINGLE}},children:[t(x,{bold:true,size:28,color:BROWN})]});}
function h2(x){return new Paragraph({heading:HeadingLevel.HEADING_2,spacing:{before:180,after:90},children:[t(x,{bold:true,size:23,color:GOLD})]});}
function bul(x,o={}){return new Paragraph({spacing:{after:o.after??64,line:270},indent:{left:340,hanging:190},children:[t("• ",{bold:true,color:GOLD}),...(Array.isArray(x)?x:[t(x)])]});}
function num(n,x){return new Paragraph({spacing:{after:70,line:272},indent:{left:360,hanging:230},children:[t(n+". ",{bold:true,color:TEAL}),...(Array.isArray(x)?x:[t(x)])]});}

// 멘트 박스(대사) — 인용 스타일
function say(txt){
  return new Table({width:{size:9360,type:WidthType.DXA},columnWidths:[9360],
    borders:{top:{style:BorderStyle.NONE},bottom:{style:BorderStyle.NONE},right:{style:BorderStyle.NONE},insideHorizontal:{style:BorderStyle.NONE},insideVertical:{style:BorderStyle.NONE},
      left:{style:BorderStyle.SINGLE,size:24,color:TEAL}},
    rows:[new TableRow({children:[new TableCell({shading:{type:ShadingType.CLEAR,fill:TINT,color:"auto"},margins:{top:70,bottom:70,left:200,right:160},
      children:[p([t("💬 멘트   ",{bold:true,color:TEAL,size:19}),t(txt,{i:true,size:21})],{after:0})]})]})]});
}

// 표 유틸
function tbl(cw,header,rows){
  const b=()=>({style:BorderStyle.SINGLE,size:6,color:LINE});
  const hc=header.map((h,i)=>new TableCell({width:{size:cw[i],type:WidthType.DXA},shading:{type:ShadingType.CLEAR,fill:HEADBG,color:"auto"},margins:{top:60,bottom:60,left:100,right:100},verticalAlign:VerticalAlign.CENTER,children:[p(t(h,{bold:true,size:19,color:BROWN}),{after:0})]}));
  const rr=rows.map(r=>new TableRow({children:r.map((c,i)=>new TableCell({width:{size:cw[i],type:WidthType.DXA},margins:{top:56,bottom:56,left:100,right:100},verticalAlign:VerticalAlign.CENTER,children:[p(Array.isArray(c)?c:t(c,{size:19,color:(typeof c==='string'&&(c.includes('미달'))?RED:INK)}),{after:0})]}))}));
  return new Table({width:{size:cw.reduce((a,b)=>a+b,0),type:WidthType.DXA},columnWidths:cw,
    borders:{top:b(),bottom:b(),left:b(),right:b(),insideHorizontal:b(),insideVertical:b()},
    rows:[new TableRow({tableHeader:true,children:hc}),...rr]});
}
function spacer(){return p(t("",{size:8}),{after:40});}

const kids=[];

// 표지
kids.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:200,after:60},children:[t("AX 플랫폼 데모 시연 시나리오",{bold:true,size:42,color:BROWN})]}));
kids.push(p(t("진행자용 런북 — 화면 동선 · 멘트 · 예상 결과 · Q&A · 돌발 대응",{size:22,color:SUB}),{align:AlignmentType.CENTER,after:60}));
kids.push(p(t("AI ERP 통합 플랫폼(app.odooaierp.com) · 라이브 시연",{size:19,color:SUB}),{align:AlignmentType.CENTER,after:40}));
kids.push(p(t("2026. 9 · 에이에스씨(ASC)",{size:18,color:SUB}),{align:AlignmentType.CENTER,after:200}));

// 0. 한눈에
kids.push(h1("0. 데모 한눈에"));
kids.push(tbl([2200,7160],["항목","내용"],[
  ["소요 시간","약 10–12분 (Q&A 별도)"],
  ["접속","https://app.odooaierp.com  ·  로그인 admin / Demo!2026"],
  ["핵심 메시지","「숫자는 그래프가 계산, LLM은 서술만. 결정은 언제나 사람. 문서가 아니라 구조가 규칙을 지킨다.」"],
  ["시연 데이터","합성 샘플 — 실데이터 연결 즉시 같은 화면이 실수치로 동작"],
  ["동선(5장면)","① 오늘 → ② 판단·승인함 → ③ 성과·KPI → ④ 질문 → ⑤ War Room"],
]));
kids.push(spacer());
kids.push(p([t("준비물: ",{bold:true}),t("노트북(크롬)·화면공유·인터넷. 백업으로 발표영상(AX_베이커리T사_통합_발표영상.mp4)을 열어 두면 네트워크 문제 시 즉시 전환 가능.",{color:SUB})],{after:60}));

// 1. 사전 점검
kids.push(h1("1. 시연 전 사전 점검 (5분 전)"));
kids.push(p(t("서버1에서 재시딩이 끝났는지, 화면이 꽉 찼는지 먼저 확인합니다. 하나라도 어긋나면 아래 재시딩을 다시 돌립니다.",{color:SUB}),{after:80}));
kids.push(tbl([620,5340,3400],["#","확인 항목","기대값"],[
  ["1","로그인 (admin / Demo!2026)","성공 → '오늘' 화면"],
  ["2","판단 → 승인함 카드 수","11건"],
  ["3","성과 → 프로젝트·KPI 지표 수","13개 전부 값 표시(빈칸 없음)"],
  ["4","달성 / 미달","달성 11 · 미달 2(원가절감·MTTR)"],
  ["5","질문 화면 응답","근거 인용 답변 생성"],
]));
kids.push(spacer());
kids.push(h2("재시딩이 필요할 때 (서버1에서)"));
kids.push(p([t("cd ~/thirdbrain-web && git pull",{size:19}),],{after:20}));
kids.push(p([t("sudo DEMO_PW='Demo!2026' bash ax-platform/deploy/seed-demo.sh",{size:19})],{after:60}));
kids.push(p([t("끝줄에 ",{color:SUB}),t("「자동 측정: 실측 6건 · 측정 전 3건 / 달성 11건 · 판단 카드 11건」",{bold:true,color:TEAL}),t(" 이 나오면 정상.",{color:SUB})],{after:60}));

// 2. 장면별 시나리오
kids.push(h1("2. 장면별 시연 시나리오",{br:true}));

// 장면 1
kids.push(h2("장면 ① 오늘 — 로그인 직후 첫 화면 (약 1분)"));
kids.push(num(1,[t("브라우저에서 "),t("app.odooaierp.com",{bold:true}),t(" 접속 → admin / Demo!2026 로그인.")]));
kids.push(num(2,"첫 화면 '오늘'에서 상단의 '할 일'과 '승인 대기 카드'를 손으로 가리킨다."));
kids.push(say("아침에 로그인하면, 오늘 무엇을 결정해야 하는지가 한 화면에 모입니다. 사람이 찾아다니는 게 아니라, 플랫폼이 먼저 가져다줍니다."));
kids.push(bul([t("포인트: ",{bold:true}),t("‘승인 대기’가 곧바로 다음 장면(승인함)으로 이어지는 자연스러운 동선.")]));

// 장면 2
kids.push(h2("장면 ② 판단 · 승인함 — 근거 있는 판단 카드 11건 (약 3분)"));
kids.push(num(1,[t("좌측 메뉴 "),t("판단 → 승인함",{bold:true}),t(" 클릭. 카드 "),t("11건",{bold:true}),t("이 목록으로 뜬다.")]));
kids.push(num(2,"카드 종류를 훑는다: 수요예측 · 생산계획 · 재고 · 설비예지 · 규칙."));
kids.push(num(3,[t("설비예지 카드 한 장을 연다 → "),t("OVEN-2 고장 13일 선행 신호",{bold:true}),t(" 를 강조.")]));
kids.push(num(4,"카드 하단의 '근거(Evidence)'를 펼쳐 그래프·데이터 출처가 인용된 것을 보여준다."));
kids.push(num(5,"카드 한 장을 실제로 '승인'해 상태가 바뀌는 것을 시연(되돌리기 가능 안내)."));
kids.push(say("모든 판단에는 근거가 붙습니다. LLM이 지어낸 숫자가 아니라, 그래프가 계산한 값을 인용합니다. 그리고 최종 승인 버튼은 언제나 사람이 누릅니다."));
kids.push(bul([t("Q&A 대비: ",{bold:true,color:RED}),t("‘AI가 틀리면?’ → 근거가 카드에 남고, 규칙이 반증되면 자동 강등(회귀 30선 상시 점검)됩니다.")]));

// 장면 3
kids.push(h2("장면 ③ 성과 · 프로젝트 · KPI — 달성도 13종 (약 3분)"));
kids.push(num(1,[t("성과 → 프로젝트·KPI → "),t("‘AX 통합 성과 시연 1차’",{bold:true}),t(" 열기.")]));
kids.push(num(2,"경영 목표 4종(수기 실적)과 기술 4영역 9종이 한 화면에서 달성도로 보인다."));
kids.push(num(3,"달성 11 · 미달 2를 짚는다 — 미달도 그대로 보여 '정직한 관제'임을 강조."));
kids.push(p(t("주요 지표(시연 데이터 기준):",{bold:true,size:20}),{before:60,after:60}));
kids.push(tbl([3060,1500,1500,3300],["KPI","목표","실적","판정 · 근거"],[
  ["생산성 향상","20%","22.5%","달성 · 현장보고"],
  ["원가 절감","10%","8%","미달 · 개선 과제"],
  ["납기 단축","15%","18%","달성"],
  ["품질 향상","30%","34%","달성"],
  ["예측 오차(WAPE)","12%","7%","달성 · 홀드아웃"],
  ["결품 일수","3일","2일","달성"],
  ["계획 준수율","95%","98.4%","달성"],
  ["정비 평균 소요","60분","300분","미달 · 예지보전 과제"],
]));
kids.push(spacer());
kids.push(say("성과는 프로젝트 정의부터 KPI 달성도까지 한 줄로 연결됩니다. 잘된 것만 보여주지 않습니다 — 원가와 정비 소요는 아직 목표 미달이고, 플랫폼이 그걸 숨기지 않고 개선 과제로 띄웁니다."));
kids.push(bul([t("포인트: ",{bold:true}),t("경영 목표는 수기 입력, 기술 KPI는 데이터에서 자동 측정 — 원천이 연결되면 자동값이 수기값을 대체.")]));

// 장면 4
kids.push(h2("장면 ④ 질문 — 자연어로 묻고 근거로 답한다 (약 2분)"));
kids.push(num(1,[t("질문 화면에서 입력: "),t("“왜 폐기율이 높았나요?”",{bold:true})]));
kids.push(num(2,"답변에 데이터 출처·그래프 근거가 사다리처럼 인용되는 것을 보여준다."));
kids.push(say("현장 담당자가 SQL을 몰라도, 자연어로 묻고 근거까지 확인합니다. 답의 출처가 늘 함께 옵니다."));

// 장면 5
kids.push(h2("장면 ⑤ War Room — 관제탑 (약 1분)"));
kids.push(num(1,[t("War Room",{bold:true}),t(" 열어 에이전트 상태·경보·처리 현황을 한눈에 보여준다.")]));
kids.push(say("다섯 일꾼(에이전트)이 밤새 일하고, 아침에 관제탑에서 결과를 받아 봅니다. 사람은 판단과 승인에 집중합니다."));

// 3. 마무리
kids.push(h1("3. 마무리 멘트 & 다음 단계",{br:true}));
kids.push(bul([t("닫는 한 문장: ",{bold:true}),t("“귀사를 위해 설계했고, 그 설계는 이미 동작합니다. 문서가 아니라 구조가 규칙을 지킵니다.”",{i:true})]));
kids.push(bul([t("다음 단계: ",{bold:true}),t("① 실데이터 1개 라인 연결(파일럿) → ② 같은 화면이 실수치로 전환 → ③ KPI 달성도로 효과 측정.")]));
kids.push(bul([t("합성 데모 고지: ",{bold:true}),t("현재 수치는 합성 샘플임을 자연스럽게 밝히고, 연결 즉시 실수치로 동작함을 강조.")]));

// 4. 돌발 대응
kids.push(h1("4. 돌발 상황 대응 (체크리스트)"));
kids.push(tbl([3200,6160],["증상","즉시 조치"],[
  ["로그인 실패","비밀번호 Demo!2026 재확인 → 서버1에서 seed-demo.sh 재시딩(계정 비번 고정 단계 포함)"],
  ["KPI가 '측정 전'으로 빈칸","git pull 후 seed-demo.sh 재시딩(측정식·수기표본 최신 반영). 13개 전부 값이 떠야 정상"],
  ["카드가 0건","seed-demo.sh 재시딩 → '판단 카드 11건' 확인"],
  ["사이트 접속 불가","백업 발표영상(mp4) 재생으로 전환 — 동일 화면·내레이션 그대로 진행"],
  ["숫자 질문받음","‘숫자는 그래프가 계산, LLM은 서술만’ 원칙으로 답변"],
]));
kids.push(spacer());
kids.push(p([t("문의 · 지원: ",{bold:true,color:BROWN}),t("에이에스씨(ASC) · AX 플랫폼 사업팀 · asclhg@gmail.com · odooaierp.com",{color:SUB})],{after:40}));

const doc=new Document({styles:{default:{document:{run:{font:F,size:21,color:INK}}}},
  sections:[{properties:{page:{margin:{top:1000,bottom:900,left:1040,right:1040}}},children:kids}]});
Packer.toBuffer(doc).then(b=>{
  const out="/home/user/thirdbrain-web/docs/presentations/AX_데모_시연_시나리오.docx";
  fs.writeFileSync(out,b); console.log("RUNBOOK",out,b.length);
});
