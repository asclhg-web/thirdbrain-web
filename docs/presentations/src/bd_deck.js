// 방글라데시 국영 제약사 — Odoo 20 ERP · GMP · AX 에이전트 구축 제안서 (33장)
const T = require("./bd_theme.js");
const {newDeck,F,C,W,H,MX,titleBar,foot,section,bullets,para,card,table,flow,kpiTiles,note} = T;
const p = newDeck();
let n=0; const pg=()=>++n;

// ───────────────────────── 1. 표지
{ const s=p.addSlide(); n++; s.background={color:C.NAVY};
  s.addShape("rect",{x:0,y:4.62,w:W,h:0.05,fill:{color:C.GREEN}});
  s.addText("PROPOSAL · ODOO 20 ERP + GMP + AX AGENTS",{x:0.9,y:1.55,w:11,h:0.35,fontFace:F,fontSize:12,color:"9FC7BD",bold:true,charSpacing:2});
  s.addText("국영 제약사 GMP 공장 디지털 전환 제안서",{x:0.9,y:1.95,w:11.8,h:0.95,fontFace:F,fontSize:38,bold:true,color:"FFFFFF"});
  s.addText("Odoo 20 ERP  ·  GMP 데이터 무결성 레이어  ·  AX(AI Transformation) 에이전트",{x:0.92,y:2.95,w:11.8,h:0.5,fontFace:F,fontSize:17,color:"E6C9A8",bold:true});
  s.addText("방글라데시 국영 제약사 (Essential Drugs Company Ltd. 추정) 귀중",{x:0.92,y:3.7,w:11.5,h:0.5,fontFace:F,fontSize:16,color:"C9D9E3"});
  s.addText("원료 입고에서 배치 출하까지 — 하나의 원장, 변조 불가 기록, 사람이 승인하는 AI",{x:0.92,y:4.85,w:11.8,h:0.45,fontFace:F,fontSize:14,color:"AEC2DA"});
  s.addText("2026. 10  ·  에이에스씨(ASC) · AX 플랫폼 사업팀  ·  odooaierp.com  ·  asclhg@gmail.com",{x:0.92,y:6.55,w:11.5,h:0.4,fontFace:F,fontSize:11.5,color:"8FA6BF"});
  s.addText("1차 제안(개략) · 세부 범위·일정·비용은 요구사항 분석 후 확정",{x:0.92,y:6.95,w:11.5,h:0.3,fontFace:F,fontSize:9.5,color:"6F8AA6",italic:true});
}

// ───────────────────────── 2. 목차
{ const s=p.addSlide(); titleBar(s,"CONTENTS","목차"); const k=pg();
  const toc=[["1","제안 요약 · 고객 이해 (방글라데시 제약산업 · 국영 제약사)"],["2","제안 배경 — GMP 공장이 지금 디지털 전환을 해야 하는 이유"],
  ["3","GMP 규제 요건 → ERP 요건 (WHO · EU Annex 11 · 21 CFR Part 11 · ALCOA+)"],["4","제약 제조 프로세스와 시스템 역할 (ERP · MES/eBR · LIMS · QMS)"],
  ["5","Odoo 20 — 신기능과 제약·GMP 적용 모듈"],["6","GMP 갭 분석 · GMP 레이어 설계 · CSV 밸리데이션"],
  ["7","AX 아키텍처 — 에이전트 포트폴리오 · Odoo 20 연결 방안 · 온톨로지"],["8","해외 벤치마킹 (Odoo 제약 사례 · 글로벌 eBR · 국영/개도국 교훈)"],
  ["9","요구사항 정의 · 현지화/인프라 · 로드맵 · 리스크 · KPI · 추진체계"]];
  let y=1.45; toc.forEach(([a,b])=>{ s.addShape("roundRect",{x:MX,y,w:0.5,h:0.5,rectRadius:0.06,fill:{color:C.GREEN}});
    s.addText(a,{x:MX,y,w:0.5,h:0.5,fontFace:F,fontSize:17,bold:true,color:"FFFFFF",align:"center",valign:"middle"});
    s.addText(b,{x:MX+0.7,y,w:11,h:0.5,fontFace:F,fontSize:14.5,color:C.INK,valign:"middle"}); y+=0.6; });
  foot(s,k);
}

// ───────────────────────── 3. 제안 요약
{ const s=p.addSlide(); titleBar(s,"EXECUTIVE SUMMARY","제안 한눈에 — Odoo 20 코어 + GMP 레이어 + AX 에이전트"); const k=pg();
  para(s,"귀사의 GMP 공장 운영(원료→생산→QC/QA→출하)을 Odoo 20 단일 원장 위에 통합하고, 규제가 요구하는 데이터 무결성(ALCOA+)·감사추적·전자서명·밸리데이션을 'GMP 레이어'로 보강하며, 그 위에 사람이 승인하는 AX 에이전트를 얹어 결품·편차·출하 지연을 구조적으로 줄입니다.",MX,1.35,12,0.85,{fs:13});
  card(s,MX,2.3,3.9,2.55,"① Odoo 20 ERP 코어",["2026-09 정식 출시 · 2029-09 표준지원","구매·재고(로트/유효기한/FEFO)·제조·품질·보전·PLM·회계","Lot 자동생성·통합 추적성 리포트·리콜 추적(신)","오프라인 모드 — 정전·망 불안정 현장 대응"],C.NAVY2);
  card(s,MX+4.05,2.3,3.9,2.55,"② GMP 데이터 무결성 레이어",["필드단위 변조불가 감사추적 + 사유 강제","레코드 전자서명·재인증(Part 11 / Annex 11 §14)","eBMR/BPR · 편차/CAPA/변경관리 QMS · SOP/교육","CSV(GAMP 5 · IQ/OQ/PQ) 패키지 — WBS 1급 산출물"],C.GREEN);
  card(s,MX+8.1,2.3,3.9,2.55,"③ AX 에이전트 (사람이 승인)",["Odoo 20 네이티브 MCP · JSON-2 API로 연결","수요·생산계획 / 원료보충 / 품질편차 / 설비예지 / 배치릴리즈 / 감사대응 에이전트","판단 카드 → 승인함 → 사람 승인 → Odoo 반영","숫자는 그래프가 계산, LLM은 서술만"],C.GOLD);
  kpiTiles(s,[{v:"−30~50%",l:"배치 출하 사이클타임\n(업계 12~18일 → 3~5일 베스트)"},{v:"−80%",l:"배치기록 문서 오류\n(eBR 벤치마크 기준)"},{v:"≥99%",l:"재고 정확도 ·\nFEFO 준수 100%"},{v:"100%",l:"출하 전 감사추적 검토 ·\n공유계정 0"}],MX,5.05,12,{h:1.45,vfs:20,lfs:10});
  note(s,"※ 목표치는 글로벌 eBR/ERP 벤치마크 기반 예시이며, 착수 시 베이스라인 측정 후 6/12개월 목표로 확정합니다.",6.6);
  foot(s,k);
}

// ───────────────────────── 4. 고객 이해 ① 산업
{ const s=p.addSlide(); titleBar(s,"01. CLIENT UNDERSTANDING","방글라데시 제약산업 — 자급 98%의 성장 시장, 규제 성숙도의 전환기"); const k=pg();
  kpiTiles(s,[{v:"US$ 3.3B",l:"내수 시장 규모\n(MAT Q2 2026, +10.6%)"},{v:"98%",l:"의약품 자급률\n(API는 ~85% 수입)"},{v:"US$ 238M",l:"수출 FY2025-26\n(130여 개국)"},{v:"ML2 → ML3",l:"DGDA WHO 규제 성숙도\n(ML3 목표 2027-05)"},{v:"2026-11",l:"LDC 졸업 →\nTRIPS 의약품 유예 종료"}],MX,1.4,12,{h:1.5,vfs:19,lfs:9.5});
  table(s,["구분","현황 (조사 기준)","제안 시사점"],[
    ["시장 구조","Top 10 ≈ 75% — Square 17%, Incepta 12.6%, Beximco 9.8%, Renata 5.7%, Eskayef 4.9%","민간 선도사는 SAP(Incepta 2021)·Oracle EBS(Beximco) 도입 — 국영사도 동급 통제 필요"],
    ["규제","Drugs & Cosmetics Act 2023 · National Drug Policy 2016(WHO 인증·PIC/S 가입 목표) · DGDA WHO GMP 기반 실사","WHO GMP + PIC/S PI 041 데이터 무결성 기준으로 설계하면 ML3·국제인증 지원"],
    ["GMP 집행","2014-16 84개사 평가 → 20~34개사 생산중단, 2009-23 45개사 면허취소(페니실린·세팔로·항암·호르몬)","배치기록 신뢰성·교차오염·QC 역량이 반복 지적 영역 → eBMR·QC·격리통제 우선"],
    ["인프라·정책","산업벨트 일 3~4h 정전(2026) · 데이터보호령 2025(국내 호스팅) · 국가 소버린 클라우드(NDC Tier-IV) · e-GP 전면 의무","오프라인 내성·온프렘/소버린 클라우드·e-GP 연계가 필수 요건"],
    ["시리얼라이제이션","DGDA 의무화 규정 미확인 · Renata 자발 도입 · 인도·파키스탄 2026~ 의무화","GS1 배치/시리얼 데이터모델을 선반영 — 중기 규제 대비 차별점"],
  ],MX,3.1,12,[1.5,5.7,4.8],{fs:9.5,rowH:0.55,boldCol:0});
  note(s,"출처: IQVIA(2차 인용)·EPB·DGDA·TBS·Daily Star 등 (부록 참조). 수치는 제안 확정 전 원문 재확인 권장.",6.6);
  foot(s,k);
}

// ───────────────────────── 5. 고객 이해 ② EDCL
{ const s=p.addSlide(); titleBar(s,"01. CLIENT UNDERSTANDING","국영 제약사 프로필 — Essential Drugs Company Ltd.(EDCL) 기준"); const k=pg();
  para(s,"방글라데시 유일의 국영 제약 제조사는 보건가족복지부 산하 100% 국영 EDCL입니다(1962 정부제약연구소 → 1983 EDCL). 귀사가 EDCL이 아닐 경우에도 동일 규제·인프라 조건이 적용되므로 본 제안의 설계는 유효합니다.",MX,1.35,12,0.7,{fs:12});
  card(s,MX,2.15,5.9,2.2,"조직·사업",["Tejgaon(다카) 본공장 · Bogura · Gopalganj(3공장, Tk 800 crore) · Khulna 라텍스 공장","약 140개 품목 — IV 수액·철분제·호르몬·페니실린계·피임제·항생제","공공병원 의약품 수요의 약 80% 공급(입찰 없는 의무구매) · 정부수요 충당 70%→90% 목표","신경영진(2025-01) — 입찰 투명성·인력 효율화·33품목 최대 50% 가격 인하"],C.NAVY2,{fs:10});
  card(s,MX+6.1,2.15,5.9,2.2,"GMP·거버넌스 현안",["노후 설비 → cGMP 미준수 → WHO 등 국제기관 인증 철회 이력","CAG 감사(2019-21) 32건 부정·Tk 477 crore 손실 → 고등법원·ACC 조사","입찰 분쟁으로 항생제 생산 장기 중단 사례","→ 내부통제·조달 투명성·감사추적이 ERP의 1순위 가치"],C.RED,{fs:10});
  card(s,MX,4.5,5.9,2.0,"진행 중인 투자·조달 (★ 제안 타이밍)",["★ 2026-05 EDCL 'ERP 설계·개발·구축' EOI 공고(QCBS·자체자금·국내 컨설팅사 대상; 재무·HR·조달·계획·재고·판매·QC·제조·PM)","★ ADB US$336.5M 백신·치료제 제조 및 규제강화 프로젝트(2023-11) — WHO GMP 백신공장(2032 목표) + DGDA ML3","Tejgaon → Manikganj 이전(ECNEC Tk 1,905 crore) / Munshiganj 통합단지 구상"],C.GOLD,{fs:10});
  card(s,MX+6.1,4.5,5.9,2.0,"제안 포지셔닝 3축",["① 진행 중 ERP의 GMP 계층(감사추적·eBMR·QMS·시리얼) 보완 파트너","② ADB 백신공장 디지털 GMP(MES/eBR·LIMS·QMS) 공급자 — 국제경쟁 트랙","③ DGDA ML3·WHO GMP 재인증 지원(데이터 무결성 패키지)"],C.GREEN,{fs:10});
  note(s,"※ EOI 낙찰 결과·귀사 정확한 규모/제품은 미확인 — 착수 전 확인 리스트(마지막 장) 참조.",6.6);
  foot(s,k);
}

// ───────────────────────── 6. 제안 배경
{ const s=p.addSlide(); titleBar(s,"02. BACKGROUND","제안 배경 — GMP 공장이 지금 디지털 전환을 해야 하는 다섯 가지 이유"); const k=pg();
  const items=[["GMP 재인증·ML3","수기 배치기록·분산 데이터로는 WHO/PIC/S 데이터 무결성 요구(ALCOA+)를 입증하기 어려움 → 변조 불가 전자기록이 인증의 전제",C.RED],
   ["진행 중 ERP 조달","2026-05 ERP EOI — 재무·조달·재고·QC·제조를 한 번에 요구. 일반 ERP는 GMP 통제(감사추적·전자서명·CSV)가 비어 있음 → 보완 설계 필요",C.GOLD],
   ["ADB 백신공장","WHO GMP 신공장(2032)은 설계 단계부터 eBR·LIMS·QMS·시리얼라이제이션을 전제 — 기존 공장과 동일 데이터 모델로 확장 가능해야 함",C.TEAL],
   ["거버넌스·투명성","감사 지적(Tk 477 crore)·입찰 분쟁 → 승인 Workflow·e-GP 연계·변경 불가 로그로 '사람이 아니라 구조가 규칙을 지키는' 체계",C.NAVY2],
   ["LDC 졸업·수출","2026-11 TRIPS 유예 종료 → 특허만료 필수약·수출 경쟁력은 원가·품질·추적성 데이터로 결정",C.PURPLE]];
  let y=1.4; items.forEach(([t,b,c],i)=>{ s.addShape("roundRect",{x:MX,y,w:0.55,h:0.9,rectRadius:0.06,fill:{color:c}});
    s.addText(String(i+1),{x:MX,y,w:0.55,h:0.9,fontFace:F,fontSize:20,bold:true,color:"FFFFFF",align:"center",valign:"middle"});
    s.addText(t,{x:MX+0.7,y,w:2.6,h:0.9,fontFace:F,fontSize:13.5,bold:true,color:C.NAVY,valign:"middle"});
    s.addText(b,{x:MX+3.4,y,w:8.6,h:0.9,fontFace:F,fontSize:11,color:C.INK,valign:"middle"}); y+=1.0; });
  s.addShape("roundRect",{x:MX,y:6.45,w:12,h:0.45,rectRadius:0.06,fill:{color:C.LIGHTGREEN}});
  s.addText("결론: 'ERP 도입'이 아니라 'GMP 데이터 무결성 + 통제 + 지능'을 하나의 플랫폼으로 — 그것이 재인증과 수익성을 동시에 여는 길입니다.",{x:MX+0.2,y:6.45,w:11.6,h:0.45,fontFace:F,fontSize:11.5,bold:true,color:C.GREEN,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 7. GMP 규제 → ERP 요건
section(p,"03","GMP 규제 요건 → ERP 요건","WHO · EU GMP Annex 11/15 · FDA 21 CFR Part 11 · PIC/S PI 041 · GAMP 5 · ALCOA+"); n++;
{ const s=p.addSlide(); titleBar(s,"03. GMP → ERP","규제 프레임워크가 ERP에 요구하는 것 — 데이터 무결성과 밸리데이션"); const k=pg();
  table(s,["규범","핵심 요구","ERP 설계 요건 (본 제안 반영)"],[
    ["WHO GMP TRS 986 Annex 2 · TRS 1033 Annex 4(데이터 무결성, 2021)","배치제조/포장기록(이론·실제수량·수율 reconciliation·일시·책임자) · 컴퓨터화 시스템의 적절한 관리·밸리데이션","BMR/BPR 자동 생성 · 수율 reconciliation · 단계별 서명 · 시스템 밸리데이션 문서"],
    ["EU GMP Annex 11 (2011 → 2025.7 개정초안 5→19쪽)","§9 감사추적(누가·무엇·전/후 값·언제·왜 자동 기록) · §12 보안(RBAC) · §14 전자서명(기록 영구결합) · §15 배치출하(QP만)","필드단위 old/new 로그 + 사유 강제 · 개인계정·MFA · 서명 재인증 · QA 전용 출하 권한"],
    ["EU GMP Annex 15 · GAMP 5 (2nd ed.)","위험기반 밸리데이션, VMP·URS·IQ/OQ/PQ, 상용 구성형=Cat.4, 커스텀=Cat.5","CSV 패키지를 WBS 1급 산출물로 · 커스텀 최소화로 Cat.5 범위 축소"],
    ["FDA 21 CFR Part 11","§11.10 폐쇄형 시스템 11개 통제(밸리데이션·정확한 사본·감사추적·권한·교육·서명책임) · Subpart C 전자서명(2요소·고유)","감사추적은 사용자 독립·비활성화 불가 · 전자서명 ID+PW 재인증 · 교육 기록"],
    ["PIC/S PI 041-1 (2021) · ALCOA+","데이터 거버넌스 · Attributable/Legible/Contemporaneous/Original/Accurate + Complete/Consistent/Enduring/Available","다음 장의 ALCOA+ 통제 매핑 적용"],
    ["EU GMP Ch.1/4/8","PQS·CAPA · 배치문서 보존(유효기한+1년 또는 QP인증+5년 중 긴 기간) · 불만·회수·CAPA 효과성","편차/CAPA/변경관리 QMS · 보존정책·아카이빙 · 회수 영향범위 즉시 산출"],
  ],MX,1.4,12,[3.0,4.8,4.2],{fs:9.5,rowH:0.72,boldCol:0});
  note(s,"※ 중요 고지: Odoo는 Part 11/Annex 11 '준수 인증' 제품이 아닙니다. 준수는 구성 + GMP 레이어 + CSV + SOP·교육으로 달성되며, 본 제안은 이를 범위에 포함합니다.",6.5,{h:0.5});
  foot(s,k);
}

// ───────────────────────── 8. ALCOA+
{ const s=p.addSlide(); titleBar(s,"03. GMP → ERP","ALCOA+ 데이터 무결성 → ERP 통제 매핑"); const k=pg();
  table(s,["속성","의미","ERP·GMP 레이어 통제","검증 방법(CSV)"],[
    ["Attributable","누가·언제 수행했는가","개인계정(공유 금지)·전자서명·감사추적 사용자 귀속","OQ: 계정별 로그 확인"],
    ["Legible","영구적으로 판독 가능","가독 리포트·아카이브 판독성·업그레이드 후 가독성","PQ: 과거 배치 조회"],
    ["Contemporaneous","수행 시점에 기록","서버 타임스탬프(NTP 단일 시간원)·현장 태블릿 입력·사후입력 사유","OQ: 시각 동기 검증"],
    ["Original","원본 또는 인증 사본","원천 시스템 기록·전사 최소화(LIMS·저울 연계)","IQ/OQ: 인터페이스"],
    ["Accurate","오류 없음","허용범위·단위·필수값 검증·수정 시 old/new·이중확인","OQ: 경계값 테스트"],
    ["+ Complete","재시험 포함 전부","실패 검사 보존·삭제 금지·append-only","OQ: 삭제 시도 차단"],
    ["+ Consistent","시간순 일관","상태 전이 통제(격리→시험→출하)·워크플로우 강제","OQ: 상태 우회 차단"],
    ["+ Enduring","보존기간 지속","백업/복원 테스트·보존정책(유효기한+1년)·마이그레이션 검증","PQ: 복원 리허설"],
    ["+ Available","요구 시 접근","검색·리포트·사찰관 조회 권한·오프라인 큐 동기화 검증","PQ: 사찰 시나리오"],
  ],MX,1.4,12,[1.6,2.4,5.2,2.8],{fs:9.8,rowH:0.5,boldCol:0});
  note(s,"출처: PIC/S PI 041-1, WHO TRS 1033 Annex 4, TGA ALCOA↔Annex 11 매핑. 통제·검증은 본 제안의 GMP 레이어·CSV 범위.",6.5);
  foot(s,k);
}

// ───────────────────────── 9. 제약 공정 → ERP
section(p,"04","제약 제조 프로세스와 시스템 역할","원료 입고에서 배치 출하까지 — 어떤 기록이 어디에 남는가"); n++;
{ const s=p.addSlide(); titleBar(s,"04. PROCESS","제약 제조 프로세스 11단계 — GMP 포인트와 Odoo 매핑 (OSD 기준)"); const k=pg();
  flow(s,["① 입고·로트","② 격리·QC","③ 원료출하","④ 칭량·분출","⑤ 과립·혼합","⑥ 타정·코팅","⑦ 포장","⑧ 완제QC","⑨ QA출하","⑩ 창고·유통","⑪ 사후"],MX,1.35,12,{h:0.7,fs:9});
  table(s,["단계","GMP 요구 포인트","Odoo 20 + GMP 레이어 매핑"],[
    ["①~③ 원료","승인공급자만 발주·즉시 격리·사양별 QC·QC/QA만 상태 변경","승인공급자 체크 발주 · 로트/제조일/유효기한/재시험일 필수 · 격리 Location 자동 · 수입검사 QCP · 상태전환 전자서명 · 공급사 품질률(신)"],
    ["④ 칭량","승인 포뮬러·FEFO·교정 저울·이중확인","MO 생성 시 BOM 확정 · FEFO 로트 예약 · 저울 ID·작업자/확인자 기록 · 교정 만료 설비 차단(레이어)"],
    ["⑤~⑥ 제조","공정 파라미터·라인 클리어런스·IPC·수율","작업지시 체크리스트·측정형 품질검사(범위 이탈 경고) · 연속 생산(신) · 수율 reconciliation · 편차 등록(QMS)"],
    ["⑦ 포장","포장지시서·라벨 reconciliation·시리얼","포장 MO/BPR · 라벨 발행/회수 대조 · GS1 마스터 + 시리얼 시스템 인터페이스"],
    ["⑧~⑨ QC/QA","사양 시험·보관샘플·BMR 검토·편차 종결·감사추적 검토·QP 인증","완제 QCP · LIMS 연계 · 출하 체크리스트 + 전자서명 · QA 전용 권한 · 통합 추적성 리포트(신)"],
    ["⑩~⑪ 유통·사후","FEFO 출고·유통기록·불만/회수·PQR","FEFO 강제 · Lot→출고라인 리콜 추적(신) · 불만→조사→CAPA · PQR 데이터 추출"],
  ],MX,2.25,12,[1.5,4.3,6.2],{fs:9.5,rowH:0.62,boldCol:0});
  note(s,"핵심 관점: '무엇이 투입되고·일어나고·측정되고·넘어가고·잔량은 어디로 갔는가'를 기록해 reconciliation하는 '재료 원장'이 배치기록의 본질입니다.",6.5);
  foot(s,k);
}

// ───────────────────────── 10. 시스템 역할 경계
{ const s=p.addSlide(); titleBar(s,"04. PROCESS","시스템 역할 경계 — ERP · MES/eBR · LIMS · QMS · 시리얼라이제이션 · AX"); const k=pg();
  const cols=[["Odoo 20 ERP (L4)","기록의 주인",["마스터데이터·BOM/포뮬러","MPS/MRP·구매·재고(로트/상태/FEFO)","제조오더·작업지시·원가","품질 디스포지션·보전·PLM","회계·조달(e-GP)·KPI"],C.NAVY2],
   ["MES / eBR (L3)","실행 기록",["단계별 전자 배치기록","설비 데이터·라인 클리어런스","IPC·reconciliation","소규모: Odoo 작업지시+품질검사+eBMR 모듈로 대체","대형/무균: 전용 MES 로드맵"],C.GREEN],
   ["LIMS · QMS","시험·품질시스템",["샘플·시험·OOS·안정성(LIMS)","편차·CAPA·변경·문서·교육(QMS)","Odoo 표준에 없음 → GMP 레이어 또는 외부 연계","ERP는 합부·CoA·종결 상태 수신"],C.PURPLE],
   ["시리얼라이제이션","추적",["GTIN+시리얼+로트+유효기한","집합(SSCC)·EPCIS","ERP는 마스터·출고 연계","DGDA 의무화 대비 선반영"],C.GOLD],
   ["AX 에이전트 (L5)","지능·판단 보조",["ERP/MES/LIMS 이벤트 → 특징량","지식그래프(온톨로지)","판단 카드 생성 → 사람 승인","쓰기는 승인된 서버액션만"],C.TEAL]];
  const cw=2.3, gap=0.125; cols.forEach((c,i)=>{ const x=MX+i*(cw+gap);
    s.addShape("roundRect",{x,y:1.4,w:cw,h:0.75,rectRadius:0.07,fill:{color:c[3]}});
    s.addText(c[0],{x,y:1.4,w:cw,h:0.45,fontFace:F,fontSize:12,bold:true,color:"FFFFFF",align:"center",valign:"middle"});
    s.addText(c[1],{x,y:1.8,w:cw,h:0.3,fontFace:F,fontSize:9.5,color:"E6EEF3",align:"center"});
    s.addShape("roundRect",{x,y:2.25,w:cw,h:3.5,rectRadius:0.07,fill:{color:C.TINT},line:{color:c[3],width:1}});
    bullets(s,c[2],x+0.08,2.35,cw-0.15,{fs:9.8,sa:4,h:3.3}); });
  s.addShape("roundRect",{x:MX,y:5.95,w:12,h:0.85,rectRadius:0.06,fill:{color:C.HEAD}});
  s.addText([{text:"원칙  ",options:{bold:true,color:C.NAVY}},{text:"① 기록의 주인은 하나(ERP 원장)  ② GMP 기록은 전자서명·감사추적이 붙는 곳에서만 생성  ③ AI는 읽기 우선, 쓰기는 사람이 승인한 서버액션으로만  ④ 인터페이스(LIMS·저울·라벨·시리얼)는 전사(轉寫)를 없애 Original·Accurate 확보",options:{color:C.INK}}],
    {x:MX+0.2,y:5.95,w:11.6,h:0.85,fontFace:F,fontSize:10.5,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 11. Odoo 20 신기능
section(p,"05","Odoo 20 — 신기능과 제약·GMP 적용","2026-09 정식 출시 · AI 에이전트 · 네이티브 MCP · 추적성 강화 · 오프라인 모드"); n++;
{ const s=p.addSlide(); titleBar(s,"05. ODOO 20","Odoo 20 (2026-09-24 출시) — 제안에 직접 관련된 주요 신기능"); const k=pg();
  kpiTiles(s,[{v:"Odoo 20",l:"2026-09-24 정식 출시\n표준지원 ~2029-09"},{v:"MCP",l:"네이티브 MCP 서버\n(OAuth 2.1 · API키)"},{v:"AI Agents",l:"자동화·스케줄 실행\nSkills 8종(레코드 생성/수정)"},{v:"JSON-2 API",l:"권장 외부 API\n(XML/JSON-RPC deprecated)"},{v:"Offline",l:"오프라인 모드\n(로컬 큐 → 동기화, 2GB)"}],MX,1.4,12,{h:1.45,vfs:18,lfs:9.5});
  table(s,["영역","Odoo 20 신규/강화 기능","제약·GMP 가치"],[
    ["AI · 에이전트","에이전트를 자동화 규칙·스케줄로 호출 · 자동화 채팅 감사 로그 · PDF 지시서 업로드로 레코드 생성 · 자기 개선 · AI 제공자 선택 · IAP 크레딧 과금","편차 초안·감사 질의응답·SOP Q&A 자동화 — 단, 모든 실행 이력은 감사 가능"],
    ["MCP 서버","/mcp 엔드포인트 · OAuth 2.1 또는 MCP 스코프 API키 · 기본 읽기 툴 5종 · 서버액션을 MCP 툴로 노출 · 사용자 권한 범위 내 동작","외부 AX 에이전트의 공식 연결 통로 — 최소권한 전용 사용자로 통제"],
    ["제조","연속 생산(일부 수량 완료 시 후속 공정 시작) · 작업지시 Kanban/Gantt · 백오더 자동 계획 · MO 분할 · Shop Floor 단일 'Produce' · WIP 원가","캠페인 생산·라인 밸런싱 · 현장 태블릿 실행 기록"],
    ["재고·추적성","MO 종료 시 Lot 항상 자동 생성 · Lot 'Transfers'에 출고 라인 표시(타겟 리콜) · 상류·하류 통합 추적성 리포트 · 재고 에이징","로트 미부여 방지 · 회수 영향범위 즉시 산출 · 계보(genealogy) 입증"],
    ["품질(Enterprise)","검사 우회는 품질 관리자만 · 실패 시 '실패 위치'로 격리 이동 · 구매 앱 공급사 품질률(%)","권한 기반 통제 강화 · 부적합품 격리 자동화 · 공급자 적격성 근거"],
    ["보전·PLM·문서","Maintenance Gantt(설비별 계획) · PLM Compare BoMs · Documents 그룹 권한 · Sign 자동 서명 요청(자동화 규칙)","교정/예방정비 계획 · 포뮬러 변경관리(ECO) · SOP 승인 자동 서명 요청"],
  ],MX,3.0,12,[1.7,6.0,4.3],{fs:9.3,rowH:0.47,boldCol:0});
  note(s,"출처: odoo.com 릴리스 노트/문서(검색 발췌) + 파트너 블로그 교차검증. 제약 시나리오(Quality·PLM·Shop Floor·Documents·Sign·Studio·AI/MCP)는 Enterprise 필요. 기술요건 Python ≥3.12 · PostgreSQL ≥16.",6.45,{h:0.5});
  foot(s,k);
}

// ───────────────────────── 12. 제약 모듈 맵
{ const s=p.addSlide(); titleBar(s,"05. ODOO 20","제약 맞춤 Odoo 모듈 맵 — 표준으로 되는 것 · 레이어로 보강할 것"); const k=pg();
  const mods=[["구매 (Purchase)","승인공급자·발주 승인 Workflow·공급사 품질률·수입 문서·e-GP 연계",C.NAVY2,"표준+설정"],
   ["재고 (Inventory)","로트/시리얼·유효기한 4종 일자·FEFO·격리 Location·추적성 리포트·바코드",C.NAVY2,"표준+설정"],
   ["제조 (MRP)·Shop Floor","BOM/포뮬러·MPS·작업지시·태블릿 실행·연속생산·수율·WIP",C.NAVY2,"표준+eBMR 레이어"],
   ["품질 (Quality)","QCP(입고/공정/출고)·합부/측정·Quality Alert·실패 위치·관리자 우회",C.GREEN,"표준+QMS 레이어"],
   ["보전 (Maintenance)","예방/시정 보전·Gantt·MTBF/MTTR·교정 주기",C.GREEN,"표준+교정 차단 레이어"],
   ["PLM","ECO 단계별 승인·BOM 버전·Compare BoMs → 포뮬러 변경관리",C.GREEN,"표준+변경관리 연계"],
   ["Documents · Sign · Knowledge","SOP 버전·그룹 권한·전자서명(SES)·사내 지식 Q&A",C.PURPLE,"표준+Part11 서명 레이어"],
   ["회계 (Accounting)","AI 청구서 인식·은행 대사·저널 해시 불변성·Mushak VAT·FY 7-6월",C.PURPLE,"표준+현지화"],
   ["AI · MCP · Studio","AI 에이전트/Skills·AI 필드·MCP 서버·자동화 규칙·웹훅",C.GOLD,"AX 연결 표면"]];
  const cw=3.9, ch=1.45, gx=0.15, gy=0.15;
  mods.forEach((m,i)=>{ const col=i%3,row=Math.floor(i/3); const x=MX+col*(cw+gx), y=1.4+row*(ch+gy);
    s.addShape("roundRect",{x,y,w:cw,h:ch,rectRadius:0.07,fill:{color:C.TINT},line:{color:m[2],width:1.2}});
    s.addShape("rect",{x,y,w:0.08,h:ch,fill:{color:m[2]}});
    s.addText(m[0],{x:x+0.18,y:y+0.08,w:cw-0.3,h:0.35,fontFace:F,fontSize:12,bold:true,color:C.NAVY});
    s.addText(m[1],{x:x+0.18,y:y+0.45,w:cw-0.3,h:0.65,fontFace:F,fontSize:9.8,color:C.INK,valign:"top"});
    s.addText(m[3],{x:x+0.18,y:y+ch-0.33,w:cw-0.3,h:0.28,fontFace:F,fontSize:9,bold:true,color:m[2]}); });
  s.addShape("roundRect",{x:MX,y:6.25,w:12,h:0.6,rectRadius:0.06,fill:{color:C.LIGHTGOLD}});
  s.addText("에디션·호스팅 권고: Odoo Enterprise(Custom) · 온프레미스 또는 Odoo.sh — SaaS 자동 업그레이드는 재검증 통제가 어려워 규제 환경에 부적합. 현장 작업자는 Light User로 비용 절감 검토.",{x:MX+0.2,y:6.25,w:11.6,h:0.6,fontFace:F,fontSize:10.5,color:C.INK,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 13. GMP 갭 분석
section(p,"06","GMP 갭 분석 · GMP 레이어 · CSV","정직한 갭 → 설계된 보강 → 검증 가능한 증거"); n++;
{ const s=p.addSlide(); titleBar(s,"06. GAP ANALYSIS","Odoo 표준 vs GMP 요구 — 갭과 보강 방안 (정직한 평가)"); const k=pg();
  table(s,["#","갭 (Odoo 표준의 한계)","규제 근거","보강 방안 (GMP 레이어)","구분"],[
    ["G1","감사추적: Chatter는 tracking 필드만, 삭제 시 소실, 사유 강제·검토 워크플로우 없음, 회계만 해시 불변","Annex 11 §9 · Part 11 §11.10(e)","OCA auditlog + 커스텀: 필드단위 old/new·UTC·사용자·사유 강제, append-only, 삭제 금지, 출하 전 검토 워크플로우","Cat.5"],
    ["G2","전자서명: Sign은 문서용 SES, 레코드 재인증·서명 의미·영구 결합 없음","Annex 11 §14 · Part 11 Subpart C","레코드 전자서명 모듈: ID+PW 재인증, 서명 의미(실행/검토/승인), 메타데이터 봉인, 변경 시 무효화","Cat.5"],
    ["G3","eBMR/BPR: MO 출력은 구조화 배치기록이 아님","WHO §15.25~30","eBMR 레이어(파트너 모듈 기반): 단계별 공정·IPC·reconciliation·단계 서명·편차 링크·QA 승인","Cat.4/5"],
    ["G4","QMS: Quality Alert는 티켓 수준 — 편차/CAPA/변경관리 워크플로우 부재","EU Ch.1 · Ch.8","QMS 레이어: 편차→분류→RCA→CAPA→효과성 / 변경요청→영향평가→승인→재검증","Cat.5"],
    ["G5","밸리데이션 패키지 부재 — Odoo는 GxP 인증 제품 아님","Annex 11 §4 · Annex 15 · GAMP 5","CSV 프로젝트: VMP·URS·위험평가·FS/CS·IQ/OQ/PQ·추적성 매트릭스 · 공급자(Odoo SA·파트너) 평가","산출물"],
    ["G6","연간 메이저 릴리스·SaaS 자동 업데이트 → 재검증 통제 곤란","Annex 11 §10/§11","온프렘/Odoo.sh · 변경관리 절차 · 릴리스별 영향평가·회귀테스트 · 정기평가(연 1회)","운영"],
    ["G7","SOP 라이프사이클·재교육 강제·교정 만료 설비 사용 차단 없음","EU Ch.2/3/4","Documents+Sign 승인 플로우 · 교육 매트릭스·미이수자 공정 차단 · 교정 만료 차단 규칙","Cat.4/5"],
    ["G8","시리얼라이제이션(시리얼 생성·집합·EPCIS) 미제공","GS1 · 각국 T&T","외부 시리얼라이제이션 시스템 연계(마스터·출고) · GS1 데이터모델 선반영","인터페이스"],
  ],MX,1.4,12,[0.5,4.0,2.0,4.6,0.9],{fs:9,rowH:0.55,center:[0,4]});
  note(s,"※ Cat.4(구성형)/Cat.5(커스텀)는 GAMP 5 분류 — 커스텀을 최소화해 밸리데이션 비용을 통제합니다. 대형 GMP 완제 공장의 Part 11급 Odoo 공개 사례는 확인되지 않아, 본 레이어·CSV가 성공의 열쇠입니다.",6.45,{h:0.5});
  foot(s,k);
}

// ───────────────────────── 14. GMP 레이어 설계
{ const s=p.addSlide(); titleBar(s,"06. GMP LAYER","GMP 데이터 무결성 레이어 설계 — 6개 구성요소"); const k=pg();
  const L=[["감사추적 엔진",["GMP 모델(로트·이동·MO·검사·BOM·사양·공급사)의 모든 변경을 old/new·UTC·사용자·사유로 기록","append-only 테이블 · 삭제/비활성화 불가 · 사용자 독립","출하 전 '감사추적 검토' 체크 · 가독 리포트 · 보존기간 = 기록 보존기간"],C.GREEN],
   ["전자서명",["서명 시 ID+비밀번호 재인증(2요소) · 서명 의미(실행/검토/승인) · 서명 일시","기록에 영구 결합, 기록 변경 시 서명 무효화","배치 출하는 QA/QP 역할만 — Annex 11 §15"],C.NAVY2],
   ["eBMR / BPR",["승인 마스터 포뮬러 → 배치별 전자기록 자동 생성","칭량·IPC·공정 파라미터·수율 reconciliation·라인 클리어런스","단계 서명 · 편차 링크 · QA 검토 · 인쇄본=전자본"],C.TEAL],
   ["QMS (편차·CAPA·변경)",["편차 → 분류 → 근본원인 → CAPA → 효과성 확인","변경요청 → 영향평가(재검증 여부) → 승인 → 실행 → 종결","배치·설비·문서·공급사 링크 · 지표(종결기간·재발률)"],C.PURPLE],
   ["재료 상태·FEFO·교정 강제",["격리/시험중/합격/불합격 상태 — QC/QA만 변경","격리·만료·재시험 초과 로트의 불출·출고 시스템 차단","교정 만료 설비·저울 사용 차단 · 승인공급자 외 발주 차단"],C.GOLD],
   ["SOP·교육·보존",["SOP 초안→검토→승인(전자서명)→발효→교육→폐기 · 유효본만 노출","직무별 교육 매트릭스 · 개정 시 재교육 과제 · 미이수자 공정 차단","백업/복원 테스트 · 아카이빙 · 유효기한+1년/QP인증+5년 보존"],C.RED]];
  L.forEach((l,i)=>{ const col=i%3,row=Math.floor(i/3); card(s,MX+col*4.05,1.4+row*2.5,3.9,2.35,l[0],l[1],l[2],{fs:9.6}); });
  note(s,"구현 원칙: OCA·검증된 파트너 모듈을 우선 활용하고 커스텀은 최소화 — GAMP Cat.5 범위를 줄여 밸리데이션 비용·기간을 통제합니다.",6.45);
  foot(s,k);
}

// ───────────────────────── 15. CSV
{ const s=p.addSlide(); titleBar(s,"06. CSV / CSA","컴퓨터화 시스템 밸리데이션(CSV) 계획 — 가동 전 완료, 업그레이드마다 재검증"); const k=pg();
  flow(s,["VMP\n밸리데이션 마스터플랜","URS\n사용자 요구사양","위험평가\nGAMP Cat.4/5","FS / CS\n기능·구성 사양","IQ\n설치 적격성","OQ\n운영 적격성","PQ\n성능 적격성","추적성 매트릭스\n·밸리데이션 보고서"],MX,1.4,12,{h:0.95,fs:9.5});
  card(s,MX,2.6,3.9,2.3,"범위·분류",["표준 구성(구매·재고·제조·품질·보전·회계) = Cat.4 → 구성 검증 중심","GMP 레이어(감사추적·전자서명·eBMR·QMS) = Cat.5 → 설계·코드 리뷰·전수 테스트","인터페이스(LIMS·저울·라벨·시리얼·e-GP) = 별도 IQ/OQ","공급자 평가: Odoo SA · 구현 파트너 · 모듈 벤더"],C.NAVY2,{fs:9.8});
  card(s,MX+4.05,2.6,3.9,2.3,"기준·방법",["EU Annex 11 2025 개정초안 기준으로 설계(감사추적 강화 반영)","FDA CSA(2025) 위험기반: 의도된 용도→위험→보증활동→객관적 증거","PIC/S PI 041 데이터 무결성 · ALCOA+ 체크리스트","WHO TRS 1019 App.5 컴퓨터화 시스템 밸리데이션"],C.GREEN,{fs:9.8});
  card(s,MX+8.1,2.6,3.9,2.3,"운영 단계 통제",["변경관리: 설정·권한·BOM 규칙 변경 = 티켓·승인·영향평가","릴리스 관리: 온프렘/Odoo.sh 고정 버전 · 연 1회 정기평가 · 메이저 업그레이드 시 회귀테스트·부분 재검증","사고관리·BCP: 백업/복원 리허설·정전 시 오프라인 큐 검증","감사추적 정기 검토 SOP"],C.GOLD,{fs:9.8});
  table(s,["산출물","내용","승인"],[
    ["VMP · URS · 위험평가","범위·접근법·일정 / 기능별 요구(GMP 플래그) / 기능별 위험·테스트 깊이","고객 QA Sign-off"],
    ["FS/CS · 추적성 매트릭스","설계·구성 명세 / URS↔FS↔테스트 케이스 매핑","고객 QA Sign-off"],
    ["IQ/OQ/PQ 프로토콜·보고서","설치 검증 / 기능·경계·보안·감사추적·서명 테스트 / 실업무 시나리오(배치 1사이클)","고객 QA·QP Sign-off"],
    ["밸리데이션 종료 보고서 · SOP 세트","편차·잔여 리스크·가동 승인 / 시스템 운영·변경·백업·감사추적 검토 SOP","경영진·QA Sign-off"],
  ],MX,5.05,12,[3.0,6.6,2.4],{fs:9.3,rowH:0.36,boldCol:0});
  foot(s,k);
}

// ───────────────────────── 16. To-Be 아키텍처 L1~L5
section(p,"07","AX 아키텍처","트랜잭션 → Odoo 20 원장 → 이벤트·특징량 → 온톨로지·지식그래프 → 에이전트 — 사람이 승인하는 지능"); n++;
{ const s=p.addSlide(); titleBar(s,"07. AX ARCHITECTURE","To-Be 총괄 아키텍처 — 다섯 층, 하나의 줄기 (GMP 레이어는 전 층을 관통)"); const k=pg();
  const layers=[["L5  AX 에이전트·관제탑","수요·생산계획 / 원료보충 / 품질편차 / 설비예지 / 배치릴리즈 어시스턴트 / 감사대응 → 판단 카드 → 승인함(사람) → Odoo 반영",C.GOLD],
   ["L4  온톨로지·지식그래프","제품·포뮬러·배치·로트·공정·설비·시험·편차·공급사·SOP를 의미로 연결 — 근거 사다리(evidence ladder)·규칙 승급/강등 루프",C.PURPLE],
   ["L3  이벤트·특징량·학습","입고·검사·작업·편차·출하 이벤트화 → 품목×라인×기간 특징량 → 수요예측·이상탐지·설비예지 모델(모델 카드·회귀 30선)",C.TEAL],
   ["L2  Odoo 20 단일 원장 + GMP 레이어","구매·재고·제조·품질·보전·PLM·회계 — PostgreSQL 단일 기록 + 감사추적·전자서명·eBMR·QMS·상태강제",C.NAVY2],
   ["L1  트랜잭션 원천","입고·QC 결과(LIMS)·칭량(저울)·작업지시(태블릿)·IPC·포장/라벨·시리얼·설비 센서(IoT/OBox)·조달(e-GP)·은행",C.GREEN]];
  let y=1.4; layers.forEach(([t,b,c])=>{ s.addShape("roundRect",{x:MX,y,w:12,h:0.9,rectRadius:0.07,fill:{color:C.TINT},line:{color:c,width:1.3}});
    s.addShape("rect",{x:MX,y,w:0.1,h:0.9,fill:{color:c}});
    s.addText(t,{x:MX+0.25,y,w:3.3,h:0.9,fontFace:F,fontSize:12.5,bold:true,color:c,valign:"middle"});
    s.addText(b,{x:MX+3.6,y,w:8.3,h:0.9,fontFace:F,fontSize:10.3,color:C.INK,valign:"middle"}); y+=0.98; });
  s.addShape("roundRect",{x:MX,y:6.35,w:12,h:0.5,rectRadius:0.06,fill:{color:C.LIGHTGREEN}});
  s.addText("관통 원칙: 숫자는 그래프(DB)가 계산하고 LLM은 서술만 · 결정은 언제나 사람 · 모든 AI 실행은 감사추적에 남는다 · 쓰기는 승인된 서버액션(화이트리스트)으로만",{x:MX+0.2,y:6.35,w:11.6,h:0.5,fontFace:F,fontSize:10.5,bold:true,color:C.GREEN,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 17. 에이전트 포트폴리오
{ const s=p.addSlide(); titleBar(s,"07. AX AGENTS","AX 에이전트 포트폴리오 — 여섯 일꾼, 하나의 승인함"); const k=pg();
  table(s,["에이전트","트리거","실행(초안 생성)","근거·입력","승인자 · Odoo 반영"],[
    ["수요·생산계획 Agent","매일 마감 후 / 주간","공공조달 수요·계절·재고 기반 익월 생산계획(MPS) 초안 + 결품 위험 품목","판매·조달 이력·재고·리드타임·캠페인","생산기획 승인 → MO 초안 생성(서버액션)"],
    ["원료 보충·공급사 Agent","ROP 도달·재시험일 임박·시세 급등","발주 초안(승인공급자·품질률·리드타임 근거) · 재시험/만료 임박 로트 경보","재고·BOM 소요·공급사 품질률·유효기한","구매 승인 → PO 초안 · 격리 유지"],
    ["품질 편차·CAPA Agent","OOS·IPC 이탈·Quality Alert 발생","편차 보고서 초안·유사 사례·근본원인 가설·CAPA 후보(근거 인용)","검사 결과·공정 파라미터·과거 편차·SOP","QA 검토·승인 → QMS 편차 레코드(사람 서명)"],
    ["설비 예지·교정 Agent","센서 이상·교정 만료 D-30","고장 선행 신호(예: 13일 선행) 점검 카드 · 교정 일정 초안","설비 센서·보전 이력·MTBF/MTTR","보전 승인 → 보전요청 생성"],
    ["배치 릴리즈 어시스턴트","배치 완료","출하 체크리스트 자동 점검(BMR 완결·QC·편차 종결·감사추적 검토) 결과 요약 — '판정은 QA/QP'","eBMR·QC·QMS·감사로그","QA/QP 전자서명으로만 출하 (AI 판정 금지)"],
    ["규제 문서·감사 대응 Agent","사찰 질의·PQR 주기","SOP/배치기록/추적성 근거 검색·요약 · PQR 데이터 초안 · DGDA/WHO 질의 응답 초안","Knowledge(SOP)·원장·추적성 리포트","QA 검토 후 제출"],
  ],MX,1.4,12,[2.0,2.0,3.6,2.3,2.1],{fs:9,rowH:0.67,boldCol:0});
  s.addShape("roundRect",{x:MX,y:6.0,w:12,h:0.8,rectRadius:0.06,fill:{color:C.HEAD}});
  s.addText([{text:"관제탑(War Room)·승인함  ",options:{bold:true,color:C.NAVY}},{text:"모든 에이전트 산출은 '판단 카드'(근거 인용·확신도)로 승인함에 모이고, 역할별 승인자가 승인/반려/되돌리기. 거부 사유는 학습 피드백·규칙 강등에 반영. AI 실행 기록(Odoo 20 자동화 채팅 + AX 감사로그)은 보존·검토 대상.",options:{color:C.INK}}],{x:MX+0.2,y:6.0,w:11.6,h:0.8,fontFace:F,fontSize:10,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 18. AX ↔ Odoo 20 연결
{ const s=p.addSlide(); titleBar(s,"07. AX ↔ ODOO 20","AX 에이전트 ↔ Odoo 20 연결 방안 — 네 가지 통로, 하나의 통제 원칙"); const k=pg();
  const ch=[["① MCP 서버 (읽기·질의)","Odoo 20 네이티브 /mcp · OAuth 2.1 또는 MCP 스코프 API키 · 기본 툴: Get Models/Fields·Search·Read group · AX 에이전트가 원장을 '권한 범위 내'로 조회",["최소권한 전용 사용자(ax_reader)","쓰기 툴은 노출하지 않음(기본)","호출 로그 보존"],C.GREEN],
   ["② JSON-2 API + 서버액션 (쓰기)","승인된 판단 카드만 → 화이트리스트 서버액션(MO 초안·PO 초안·보전요청·편차 레코드 생성) 호출 · Bearer API키 · X-Odoo-Database",["쓰기는 '초안' 상태로만 생성","전자서명·상태 전이는 사람이","변경은 감사추적에 사용자=승인자로"],C.NAVY2],
   ["③ 웹훅·자동화 규칙 (이벤트)","Studio 아웃바운드 웹훅/자동화로 입고·검사 실패·OOS·MO 완료·센서 경보를 AX 파이프라인(L3)으로 푸시 · 인바운드 웹훅으로 결과 수신",["멱등성 설계(중복 트리거 대비)","이벤트 스키마 버전관리","PG 논리복제(CDC) 병행 가능"],C.TEAL],
   ["④ Odoo AI 에이전트·Skills (내부)","Odoo 20 내장 에이전트를 SOP Q&A·회계 질의·AI 필드 추출에 활용 · 자동화 채팅 감사 로그 · Sign 자동 서명 요청 체인",["IAP 크레딧 예산(에이전트당)","제공자·데이터 반출 정책 검토(국내 호스팅·데이터보호령)","GMP 레코드 직접 수정 금지"],C.GOLD]];
  ch.forEach((c,i)=>{ const col=i%2,row=Math.floor(i/2); const x=MX+col*6.075, y=1.4+row*2.45;
    s.addShape("roundRect",{x,y,w:5.925,h:2.3,rectRadius:0.07,fill:{color:C.TINT},line:{color:c[3],width:1.2}});
    s.addShape("rect",{x,y,w:0.09,h:2.3,fill:{color:c[3]}});
    s.addText(c[0],{x:x+0.2,y:y+0.08,w:5.6,h:0.36,fontFace:F,fontSize:12.5,bold:true,color:C.NAVY});
    s.addText(c[1],{x:x+0.2,y:y+0.45,w:5.6,h:0.95,fontFace:F,fontSize:9.8,color:C.INK,valign:"top"});
    bullets(s,c[2],x+0.15,y+1.4,5.6,{fs:9.3,sa:2,h:0.9,color:c[3]}); });
  s.addShape("roundRect",{x:MX,y:6.35,w:12,h:0.5,rectRadius:0.06,fill:{color:C.LIGHTGREEN}});
  s.addText("통제 원칙: 읽기는 넓게(MCP), 쓰기는 좁게(승인된 서버액션·초안만), 서명·출하·상태 전이는 사람만, 모든 호출은 감사추적 — 이것이 AX와 GMP가 공존하는 방식입니다.",{x:MX+0.2,y:6.35,w:11.6,h:0.5,fontFace:F,fontSize:10.5,bold:true,color:C.GREEN,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 19. 온톨로지·파이프라인
{ const s=p.addSlide(); titleBar(s,"07. ONTOLOGY · PIPELINE","제약 온톨로지와 데이터 파이프라인 — 어떤 기록이 어떤 지능이 되는가"); const k=pg();
  table(s,["트랜잭션 (L1→L2)","이벤트화 (L3)","특징량·학습 (L3)","쓰는 지능 (L4·L5)"],[
    ["조달·판매(공공병원 의무구매·입찰)","수요 이벤트(품목×기관×월)","계절·캠페인·조달 주기 프로파일","수요예측·생산계획 Agent"],
    ["입고·QC 결과·공급사","입고/합부/OOS 이벤트","공급사 품질률·리드타임·OOS율","원료 보충·공급사 적격 Agent"],
    ["칭량·작업지시·IPC·수율","공정 파라미터·이탈 이벤트","라인×품목 수율·편차 선행지표","품질 편차·CAPA Agent · 설비 예지"],
    ["설비 센서·보전 이력","진동·온도·고장 이벤트","MTBF·열화 추세·교정 만료","설비 예지·교정 Agent"],
    ["eBMR·QMS·감사로그·SOP","배치 완결·편차 종결·서명 이벤트","출하 체크리스트 충족률·검토 시간","배치 릴리즈 어시스턴트 · 감사 대응"],
  ],MX,1.4,12,[3.2,2.9,3.0,2.9],{fs:9.6,rowH:0.5,boldCol:0});
  s.addText("제약 도메인 온톨로지 — 클래스와 관계 (발췌)",{x:MX,y:4.45,w:8,h:0.35,fontFace:F,fontSize:12.5,bold:true,color:C.NAVY});
  const nodes=["제품(SKU)","마스터 포뮬러(BOM)","배치/MO","원료 로트","공정·작업장","설비·저울","QC 시험·사양","편차·CAPA","공급사","SOP·교육"];
  let x=MX; nodes.forEach((t,i)=>{ const w=1.14; s.addShape("roundRect",{x,y:4.85,w,h:0.55,rectRadius:0.1,fill:{color:[C.NAVY2,C.GREEN,C.TEAL,C.PURPLE,C.GOLD][i%5]}});
    s.addText(t,{x,y:4.85,w,h:0.55,fontFace:F,fontSize:9,bold:true,color:"FFFFFF",align:"center",valign:"middle"}); x+=w+0.065; });
  para(s,"관계: hasFormula · consumesLot · producedOn(설비) · testedBy(사양) · deviatesWith · suppliedBy · governedBy(SOP) · releasedBy(QA 서명)  —  근거 사다리: 질문 → 판단 카드 → 규칙/모델 → 이벤트 → 원장 레코드(감사추적)까지 클릭으로 내려감. 반증된 규칙은 자동 강등(회귀 30선 상시 점검).",MX,5.5,12,0.9,{fs:10.3});
  foot(s,k);
}

// ───────────────────────── 20. 벤치마킹 ① Odoo 제약
section(p,"08","해외 벤치마킹","Odoo 제약 적용 사례 · 글로벌 eBR/MES 성과 · 국영·개도국 제약사의 교훈"); n++;
{ const s=p.addSlide(); titleBar(s,"08. BENCHMARK ①","Odoo 제약 적용 사례 — 공식 고객사례와 파트너 발표 성과"); const k=pg();
  table(s,["기업","국가·업종","적용 범위","성과·특징","출처 구분"],[
    ["Brand for Pharmaceutical Industries","이집트 · 제약그룹(제조)","V10 Community(2018) → V13 Enterprise(2019) · 제조·품질 포함 다수 모듈 · BI","단계적 확장, 사용자 급증(2020)","Odoo 공식 고객사례"],
    ["Magis Pharma Group (Qualenica)","벨기에 · 환자 맞춤 치료제","규제 생산(콜드스토리지·배치추적)·그룹 회계","도구 7→1 통합 · 2주 내 가동 · 4개사 40+ 사용자","Odoo 공식 + 파트너(Hadron)"],
    ["Laboratorio Fito Medic's","콜롬비아(추정) · 제약·화장품","제조·품질·WMS","운영효율 +20% · 생산성 +18%(자체보고)","Odoo 공식 고객사례"],
    ["Fraver NV / Viomix / EFA Laboratorios","벨기에 / — / 우루과이","조제·원료·완제 / 원료·의약품 / 전문의약품","지면·스프레드시트 → 실시간 경영보고","Odoo 공식 고객사례"],
    ["Abydos Pharma (CMO)","유럽 · 수탁제조","제조·재고·품질·Documents","배치출하 40%↓ · 수기오류 85%↓","파트너 발표(SDLC)"],
    ["익명 제약 제조·유통","캐나다(추정)","Odoo 18 · 16개 모듈","대사 40~50h→5~8h · WO 단위 QC로 재작업비 60%↓ · ROI 77%(6.8개월)","파트너 발표(Ksolves)"],
    ["Pharmalife Research","이탈리아 · 제약·뉴트라","제조·품질","처리량 +30% · QA 지연 감소","파트너 발표"],
  ],MX,1.4,12,[2.5,2.1,3.0,3.0,1.4],{fs:9,rowH:0.54,boldCol:0});
  s.addShape("roundRect",{x:MX,y:5.75,w:12,h:1.05,rectRadius:0.06,fill:{color:C.LIGHTGOLD}});
  s.addText([{text:"정직한 해석  ",options:{bold:true,color:C.GOLD}},{text:"공개 사례는 중소 제조·조제·유통 중심이며, 대형 GMP 완제 공장에서 Part 11/Annex 11급으로 밸리데이션된 Odoo 공개 사례는 확인되지 않았습니다. 따라서 본 제안은 'Odoo = 검증된 ERP 코어 + GMP 레이어 + CSV 프로젝트'로 포지셔닝하며, 파트너 수치는 '파트너 발표 기준'으로 인용합니다.",options:{color:C.INK}}],{x:MX+0.2,y:5.75,w:11.6,h:1.05,fontFace:F,fontSize:10.3,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 21. 벤치마킹 ② 글로벌
{ const s=p.addSlide(); titleBar(s,"08. BENCHMARK ②","글로벌 제약 디지털화 성과 — ERP 코어보다 'eBR·MES 통합'이 효과의 원천"); const k=pg();
  kpiTiles(s,[{v:"−75%",l:"수기 문서\nCipla Patalganga (PAS-X MES + SAP)"},{v:"20일→1일",l:"배치기록 검토\nValent BioSciences (eBR)"},{v:"−25% / +60%",l:"생산오류 / 검토 속도\nFerring Kiel (eBR)"},{v:"4주→6h",l:"배치 출하 RBE\n글로벌 바이오파마 (Emerson)"},{v:"3~5일",l:"배치출하 베스트\n(업계평균 12~18일)"}],MX,1.4,12,{h:1.5,vfs:17,lfs:9.3});
  table(s,["기업","국가·성격","솔루션·접근","교훈"],[
    ["Vinphaco","베트남 · GMP-WHO","SAP S/4HANA Cloud(FPT) — 1차 6개월(MM·PP·QM·FICO·SD) → 2차 PM·e-banking → 3차 WM·QR","단계적 롤아웃으로 6개월 내 1차 가동"],
    ["Incepta / Beximco","방글라데시 · 민간 선도","SAP(2021, '국내 최초') / Oracle EBS R12 + GxP 검증(KPMG)","국내 선도사도 GxP 검증을 별도 수행 — 레거시 연계 비용 주의(Beximco 사례)"],
    ["Pharmaniaga","말레이시아 · 정부연계기업","S/4HANA 공장 가동(생산오더·QM·납품·원가)","GLC도 글로벌 표준 ERP + QM 통합"],
    ["Cipla · Dr. Reddy's","인도 · 대형","PAS-X MES ↔ SAP·SCADA·BMS·IPQC·WMS 통합 / 템플릿 재사용 5개월 구축","ERP 단독이 아닌 MES/eBR 통합이 효과의 원천 → 본 제안의 L3·eBMR 레이어 근거"],
    ["McKinsey QC 연구","글로벌","디지털·자동화 QC: 리드타임 60~70%↓ · 수기문서 80%↓ · 조사 90%↓ · 편차 65%↓(일부)","QC 랩 디지털화가 출하 리드타임의 병목 해소"],
  ],MX,3.1,12,[1.9,2.1,5.0,3.0],{fs:9.3,rowH:0.6,boldCol:0});
  note(s,"출처: Körber(Cipla·Ferring), Emerson/ISA, FPT IS, Wikipedia/Zensar, ABeam, McKinsey — 벤더 발표 수치는 독립 검증 없음.",6.5);
  foot(s,k);
}

// ───────────────────────── 22. 벤치마킹 ③ 국영·개도국
{ const s=p.addSlide(); titleBar(s,"08. BENCHMARK ③","국영·개도국 제약사의 교훈 — 'ERP ≠ 통제', GMP 투자가 수익성을 만든다"); const k=pg();
  table(s,["사례","국가·성격","무엇을 했나","결과","교훈"],[
    ["Kimia Farma","인도네시아 · 국영","SAP 도입(2015-16)","9개 모듈 중 4개만 사용 → 2024 자회사 회계조작·Rp 8.7조 구조조정","ERP를 깔아도 조달·재고·채권 내부통제와 감사추적이 없으면 부정은 재발 · 활용도 KPI 필수"],
    ["EIPICO","이집트 · 준국영(ACDIMA 51%)","2021 SAP 착수 + 53개 라인 추적시스템 · QM 배치 유효기한·격리 통제","ERP와 라인 추적 병행 구축","ERP + 추적성(시리얼)을 같은 로드맵으로"],
    ["Vinapharm","베트남 · 국가 65%","26개 GMP-EU/PIC-S 라인 투자","2025 세전이익 +62% 사상 최대","고규격 GMP가 수익성과 수출을 견인"],
    ["KAPL vs HAL·IDPL","인도 · 제약 PSU","KAPL만 WHO-GMP 설비 투자 / 나머지는 재무구제만","KAPL 유일 흑자 · HAL/IDPL 회생 실패","설비·품질 투자 없는 재무 구제는 실패"],
    ["SPMC","스리랑카 · 국영","JICA 신공장(2018) + 운영 개선","2025 36억정 사상 최대 생산 · 2026 창고 신규","양자 ODA + 단계적 현대화가 생산성 도약"],
    ["Nepal Drugs","네팔 · 국영","10년 중단 → ORS부터 단계 재가동(2016)","제한 품목부터 회생","핵심 품목·핵심 공정부터 작게 시작"],
  ],MX,1.4,12,[1.6,1.8,3.0,2.9,2.7],{fs:9,rowH:0.66,boldCol:0});
  card(s,MX,5.5,12,1.3,"국영 GMP 공장 제안에 주는 다섯 가지 시사점",["① 재무 통합으로 시작하더라도 조달·재고·배치 내부통제(승인·감사추적)를 1단계에 포함   ② GMP 설비 투자와 소프트웨어(eBMR·QMS)를 같은 로드맵에   ③ 모듈 과다 도입 금지 — 활용도·교육·하이퍼케어 예산 확보   ④ 핵심 품목·핵심 라인 파일럿 → 확산   ⑤ ADB·EDCF 등 양자/다자 재원과 연계"],C.GREEN,{fs:10});
  foot(s,k);
}

// ───────────────────────── 23. 요구사항 ①
section(p,"09","요구사항 · 현지화 · 로드맵 · KPI","1차 요구사항 정의 → 현지 요건 → 단계별 구축 → 성과 측정 → 추진 체계"); n++;
{ const s=p.addSlide(); titleBar(s,"09. REQUIREMENTS ①","요구사항 정의 (1차) — 회사·조달·원료/재고·생산"); const k=pg();
  table(s,["No","분류","세부","요구사항 (세부 수치·프로세스는 분석 단계 확정)","협의"],[
    ["1","회사·IT","규모·거점","다공장(다카·보구라·고팔간지·쿨나) 멀티컴퍼니/멀티창고 · 수백 명 사용자(Light User 포함) 전제",""],
    ["2","회사·IT","호스팅","데이터 국내 호스팅(국가 소버린 클라우드 또는 온프렘) · Odoo Enterprise 고정 버전 · 재검증 통제","협의"],
    ["3","회사·IT","언어·통화","Bangla/English UI · BDT lakh/crore 표기 · 회계연도 7/1~6/30",""],
    ["4","조달","e-GP·승인","PPR 2025/e-GP 연계 · 구매요청→발주→입고→청구 승인 Workflow · 승인공급자 외 발주 차단 · 실소유자 정보",""],
    ["5","조달","공급자 적격","승인공급자 목록(물질×공급자×제조소) · 감사 주기·만료 알림 · 공급사 품질률 · CoA 관리",""],
    ["6","원료·재고","로트·유효기한","로트/제조일/유효기한/재시험일 필수 · FEFO 강제 · 만료·재시험 초과 로트 출고 차단 · 격리 Location 자동",""],
    ["7","원료·재고","상태 통제","격리/시험중/합격/불합격 상태 — QC/QA만 변경(전자서명) · 격리 재고 불출 시스템 차단",""],
    ["8","원료·재고","추적·회수","원료 로트→중간체→완제→출고처 쌍방향 계보 · 리콜 영향범위 즉시 산출 · 모의회수 기록",""],
    ["9","생산","BMR/eBMR","승인 포뮬러에서 배치기록 자동 생성 · 칭량(저울 연계)·IPC·수율 reconciliation · 단계 서명 · 편차 링크","협의"],
    ["10","생산","계획·실행","수요·조달 기반 MPS → 작업지시 → 현장 태블릿 실행 · 연속생산/캠페인 · 교정 만료 설비 사용 차단",""],
    ["11","생산","포장·시리얼","포장지시서·라벨 reconciliation · GS1 GTIN/로트/유효기한 마스터 · 시리얼라이제이션 인터페이스","협의"],
  ],MX,1.4,12,[0.5,1.2,1.5,8.1,0.7],{fs:9,rowH:0.44,center:[0,4]});
  foot(s,k);
}

// ───────────────────────── 24. 요구사항 ②
{ const s=p.addSlide(); titleBar(s,"09. REQUIREMENTS ②","요구사항 정의 (1차) — 품질·회계/현지화·성과·통합·밸리데이션"); const k=pg();
  table(s,["No","분류","세부","요구사항","협의"],[
    ["12","품질","QC·출하","입고/공정/완제 QCP · 합부/측정 · OOS 플래그 · CoA · LIMS 연계 · QA 출하 체크리스트 + QA/QP 전자서명",""],
    ["13","품질","QMS","편차→분류→RCA→CAPA→효과성 · 변경관리(영향평가·재검증) · 불만·회수 · 배치/설비/문서/공급사 링크",""],
    ["14","품질","감사추적·서명","GMP 모델 필드단위 old/new·사유·UTC · 삭제 금지 · 사용자 독립 · 출하 전 검토 · 레코드 전자서명 재인증",""],
    ["15","품질","SOP·교육","SOP 버전·승인(전자서명)·발효·폐기 · 직무별 교육 매트릭스 · 개정 시 재교육 · 미이수자 공정 차단","협의"],
    ["16","설비","보전·교정","예방/시정 보전 · 교정 주기·만료 차단 · MTBF/MTTR · 센서(IoT) 연계",""],
    ["17","회계","현지화","Mushak 6.3 VAT 전자발행·보존(Finance Bill 2026) · VDS · FY 7-6월 · 공공회계(iBAS++) 연계 검토","협의"],
    ["18","회계","통제","AP/AR 승인 · 저널 해시 불변성 · 프로젝트/공장별 원가·손익 · 조달-회계 3-way 매칭",""],
    ["19","성과","KPI","배치출하 사이클타임·RFT·편차율·CAPA 종결·재고정확도·만기폐기·OEE·FDA 품질지표(LAR·PQCR·IOOSR) 대시보드",""],
    ["20","AX","에이전트","6종 에이전트 · 판단 카드·승인함 · MCP 읽기/서버액션 쓰기 · AI 실행 감사로그 · IAP 크레딧 예산","협의"],
    ["21","통합","인터페이스","LIMS · 저울/라벨프린터 · 시리얼라이제이션 · e-GP · 은행 · 기존 시스템 데이터 이관(거래처·품목·BOM·재고·미결)","협의"],
    ["22","밸리데이션","CSV","VMP·URS·위험평가·IQ/OQ/PQ·추적성 매트릭스·종료보고서 · 운영 SOP · 업그레이드 재검증 절차",""],
  ],MX,1.4,12,[0.5,1.2,1.5,8.1,0.7],{fs:9,rowH:0.44,center:[0,4]});
  foot(s,k);
}

// ───────────────────────── 25. 현지화·인프라·보안
{ const s=p.addSlide(); titleBar(s,"09. LOCALIZATION · INFRA","현지화 · 인프라 · 보안 — 방글라데시 현실에 맞춘 설계"); const k=pg();
  card(s,MX,1.4,3.9,2.55,"현지화 요건",["Bangla Unicode UI/리포트 · 영어 병용","BDT · lakh/crore 표기 · 회계연도 7/1~6/30","Mushak 6.3 세금계산서 ERP 전자발행·보존(Finance Bill 2026) · VDS Rules 2025","e-GP 전면 의무(PPR 2025) → 조달 모듈 정합 · 실소유자 공개","공공회계 iBAS++ 연계 가능성(협의)"],C.NAVY2,{fs:9.8});
  card(s,MX+4.05,1.4,3.9,2.55,"인프라·가용성",["데이터 국내 호스팅: 국가 데이터센터(Kaliakoir Tier-IV, 99.995%) / Oracle 소버린 리전 / 온프렘","산업벨트 일 3~4h 정전(2026) → UPS·발전기 + Odoo 20 오프라인 모드(로컬 큐→동기화) + 현장 태블릿","운영/테스트/개발 환경 분리 · 고정 버전 · 백업/복원 리허설(RTO/RPO)","모바일 4G 중심 → 경량 화면·바코드 앱"],C.GREEN,{fs:9.8});
  card(s,MX+8.1,1.4,3.9,2.55,"보안·데이터 거버넌스",["개인정보보호령·데이터관리령·사이버보호령 2025 준수 → 국내 호스팅 전제","RBAC(Odoo 20 ir.access) · 개인계정 · MFA · 세션 정책 · 계정 라이프사이클 로그","AI 데이터 반출 정책: 외부 LLM 사용 범위·마스킹·국내 모델(GPU 서버) 옵션","WAF·네트워크 분리 · DB 접근통제 · 변경관리"],C.RED,{fs:9.8});
  table(s,["구성","역할","권고 사양(안)","비고"],[
    ["운영 App/DB","Odoo 20 Enterprise + PostgreSQL 16","8~16 vCPU · 64GB · SSD · Ubuntu LTS","다공장 사용자 규모에 따라 확장"],
    ["테스트/검증","CSV·업그레이드 회귀 환경","4~8 vCPU · 32GB","운영과 동일 구성(밸리데이션 전제)"],
    ["AX 서버","이벤트 파이프라인·지식그래프·에이전트·승인함","8 vCPU · 32GB (+GPU 옵션: 국내 LLM)","Odoo와 MCP/JSON-2/웹훅 연결"],
    ["현장","태블릿·바코드·저울/라벨·IoT(OBox)","라인별 태블릿 · UPS","오프라인 모드 검증"],
  ],MX,4.15,12,[2.0,4.0,3.3,2.7],{fs:9.5,rowH:0.4,boldCol:0});
  note(s,"※ 호스팅 선택(국가 DC·소버린 클라우드·온프렘)은 데이터보호령 최신 개정과 조달 조건에 따라 착수 시 확정.",6.5);
  foot(s,k);
}

// ───────────────────────── 26. 로드맵
{ const s=p.addSlide(); titleBar(s,"09. ROADMAP","구축 로드맵 — 핵심 라인에서 검증하고 전 공장·백신공장으로 확장 (약 12~18개월)"); const k=pg();
  const ph=[["0  진단·CSV 계획","1~2개월",["현장 진단(공정·데이터 흐름·GMP 갭)","URS·VMP·위험평가 · KPI 베이스라인","EOI/ADB 트랙·호스팅·파트너 확정"],C.SUB],
   ["1  Odoo 20 코어","3~4개월",["구매·재고(로트/FEFO/격리)·제조·품질·보전·회계·현지화","승인 Workflow·e-GP·데이터 이관","IQ/OQ 1차 · 파일럿 라인 가동"],C.NAVY2],
   ["2  GMP 레이어","3~4개월",["감사추적·전자서명·eBMR·QMS·SOP/교육·상태강제","LIMS·저울·라벨 인터페이스","OQ/PQ · 배치 1사이클 PQ · 밸리데이션 종료 · Go-Live"],C.GREEN],
   ["3  AX 지능화","3~4개월",["이벤트 파이프라인·온톨로지·지식그래프","6종 에이전트·승인함·관제탑 · MCP/서버액션 연결","KPI 루프 · 규칙 승급/강등 운영"],C.GOLD],
   ["4  확장·고도화","지속",["전 공장 롤아웃 · 시리얼라이제이션 · MES 검토","ADB 백신공장 디지털 GMP 설계 반영","DGDA ML3·WHO GMP 재인증 지원 · 연 1회 정기평가"],C.PURPLE]];
  const cw=2.3, gap=0.125; ph.forEach((c,i)=>{ const x=MX+i*(cw+gap);
    s.addShape("roundRect",{x,y:1.4,w:cw,h:0.8,rectRadius:0.07,fill:{color:c[3]}});
    s.addText(c[0],{x,y:1.4,w:cw,h:0.5,fontFace:F,fontSize:11.5,bold:true,color:"FFFFFF",align:"center",valign:"middle"});
    s.addText(c[1],{x,y:1.85,w:cw,h:0.3,fontFace:F,fontSize:9.5,color:"E6EEF3",align:"center"});
    s.addShape("roundRect",{x,y:2.3,w:cw,h:2.75,rectRadius:0.07,fill:{color:C.TINT},line:{color:c[3],width:1}});
    bullets(s,c[2],x+0.08,2.4,cw-0.15,{fs:9.6,sa:4,h:2.6});
    if(i<ph.length-1) s.addText("▶",{x:x+cw-0.02,y:1.4,w:gap+0.06,h:0.8,fontFace:F,fontSize:9,color:C.SUB,align:"center",valign:"middle"}); });
  table(s,["게이트","판정 기준(예)"],[
    ["G1 설계 승인","URS·VMP·위험평가 QA Sign-off · 호스팅·조달 트랙 확정"],
    ["G2 코어 가동","파일럿 라인 재고정확도 ≥98% · 승인 Workflow 전 항목 · IQ/OQ 통과"],
    ["G3 GMP Go-Live","PQ(배치 1사이클) · 감사추적·서명 테스트 전수 통과 · 밸리데이션 종료 보고서 · SOP·교육 완료"],
    ["G4 AX 운영","판단 카드 승인률·거부 사유 피드백 · KPI 루프 1사이클 · AI 감사로그 검토"],
  ],MX,5.2,12,[2.2,9.8],{fs:9.5,rowH:0.33,boldCol:0});
  foot(s,k);
}

// ───────────────────────── 27. 사업관리·리스크
{ const s=p.addSlide(); titleBar(s,"09. PROJECT MGMT · RISK","사업관리 · 리스크 — 고객사와 공동 관리하는 일정·범위·품질·규제"); const k=pg();
  table(s,["No","리스크","예상 영향","관리·대응"],[
    ["1","요구사항 변경·범위 확대(EOI 모듈 + GMP + AX)","일정 지연·Cat.5 증가·재검증","분석 종료 시 Requirements Freeze · Change Request · 미완 기능 차기 Phase 이관"],
    ["2","밸리데이션 부담·규제 변동(Annex 11 2025 개정·DGDA ML3·e-invoicing)","Go-Live 지연·재검증","CSV를 WBS 1급 · 개정초안 기준 선설계 · 규제 모니터링 · 릴리스별 영향평가"],
    ["3","사용자 적응·활용도 저조(Kimia Farma 교훈)","모듈 미사용·병행 수기·데이터 이중관리","역할별 교육(Bangla) · Key User · 하이퍼케어 · 모듈 활용도 KPI ≥80%"],
    ["4","전력·망 불안정(일 3~4h 정전)","현장 입력 중단·데이터 공백","UPS·발전기 · 오프라인 모드 큐 검증 · 사후입력 사유 통제"],
    ["5","조달·거버넌스(PPR 2025·e-GP·실소유자·감사 이력)","계약 지연·감사 지적","현지 파트너 컨소시엄 · e-GP 등록 · 투명 조달 대시보드 · 승인 Workflow 1단계 포함"],
    ["6","데이터 현지화·AI 데이터 반출","규정 위반·프로젝트 중단","국내 호스팅 · AI 사용 범위 정책 · 마스킹 · 국내 LLM 옵션"],
    ["7","인터페이스(LIMS·저울·시리얼·레거시) 비용·일정(Beximco 교훈)","예산 초과·지연","Phase 1 최소 연동(MVP) · 범위 명확화 후 개발 · 불확실 항목 옵션 분리"],
  ],MX,1.4,12,[0.5,3.4,2.6,5.5],{fs:9.3,rowH:0.52,center:[0]});
  card(s,MX,5.55,5.9,1.3,"고객사 참여",["전담 PM + 업무별 Key User(QA·QC·생산·창고·구매·회계·IT)","현행 SOP·배치기록·데이터 제공 · 인터뷰(업무별 1~3회)","스프린트 리뷰·UAT·PQ 참여 · QA/QP Sign-off"],C.NAVY2,{fs:9.6});
  card(s,MX+6.1,5.55,5.9,1.3,"수행 방법론",["Discovery → Blueprint → Realization(Agile 3~4 스프린트) → Testing(SIT/UAT+CSV) → Training → Go-Live/MA","단계별 Sign-off 산출물 · 하이퍼케어 · 연 1회 정기평가"],C.GREEN,{fs:9.6});
  foot(s,k);
}

// ───────────────────────── 28. KPI
{ const s=p.addSlide(); titleBar(s,"09. KPI","기대효과 — 판정 KPI와 목표(안): 베이스라인 측정 후 6/12개월 목표 확정"); const k=pg();
  kpiTiles(s,[{v:"−30~50%",l:"배치출하 사이클타임"},{v:"−80%",l:"배치기록 오류"},{v:"≤30일 · ≥90%",l:"편차 종결 · 적시율"},{v:"≥99% · 100%",l:"재고정확도 · FEFO 준수"},{v:"−30%",l:"만기 폐기액"},{v:"100% · 0",l:"감사추적 검토 · 공유계정"}],MX,1.4,12,{h:1.35,vfs:16,lfs:9.5});
  table(s,["구분","KPI","정의·근거","벤치마크"],[
    ["규제·품질","LAR · PQCR · IOOSR · APR 적시율","FDA Quality Metrics(합격로트율·불만율·OOS 무효화율)","FDA 가이던스"],
    ["생산·출하","배치출하 사이클타임 · 배치기록 검토시간 · RFT · OEE","제조완료→QA 출하 / 편차 없는 로트 비율","베스트 3~5일 vs 평균 12~18일 · OEE 60~70%"],
    ["품질시스템","편차 발생률 · CAPA 종결기간·재발률 · 감사추적 검토율 · 사찰 지적 수","편차율은 불량률의 ~4개월 선행지표(r=0.83)","IPA 연구 · Annex 11 §9"],
    ["데이터 무결성","사후입력 비율 · 공유계정 0 · 권한 검토 주기 · 백업 복원 성공률","PI 041 · TRS 1033","—"],
    ["재고·공급","재고정확도 · 회전율 · 만기폐기 · 결품률 · 공급자 OTIF · 미승인 구매 0","FEFO·격리 통제 효과","PLIVA 재고 ≥30%↓(2차)"],
    ["설비·교육·도입","교정 적시율 · PM 준수율 · MTBF/MTTR · SOP 이수율 · 모듈 활용도 · ROI","Odoo Maintenance 산출 · Kimia Farma 교훈","Ksolves ROI 77%(파트너)"],
  ],MX,2.95,12,[1.6,3.9,3.9,2.6],{fs:9.3,rowH:0.52,boldCol:0});
  note(s,"성과는 AX 플랫폼의 '프로젝트·KPI 센터'에서 목표 대비 달성도로 자동 집계·공개되며, 미달 지표는 개선 과제로 에이전트가 제안합니다(정직한 관제).",6.5);
  foot(s,k);
}

// ───────────────────────── 29. 추진체계·파트너링·재원
{ const s=p.addSlide(); titleBar(s,"09. STRUCTURE · FUNDING","추진 체계 · 파트너링 · 재원 트랙 — 국영기업 조달 현실에 맞춘 구조"); const k=pg();
  card(s,MX,1.4,3.9,2.6,"추진 체계(안)",["주계약: 현지 컨소시엄(Odoo 공식 파트너 Metamorphosis/VS ONE 등 또는 현지 컨설팅사) — 국내 컨설팅사 조건·e-GP 대응","ASC: GMP 레이어·CSV·AX 플랫폼 설계·구축 — 기술 서브컨트랙터/솔루션 공급자","고객: 전담 PM·QA/QP·Key User · 운영 조직","선례: 베트남 FPT IS가 SAP 기반으로 방글라데시 국영 EGCB(US$8.8M)·GTCL(US$9.1M) ERP 수주"],C.NAVY2,{fs:9.6});
  card(s,MX+4.05,1.4,3.9,2.6,"재원·조달 트랙",["① EDCL 자체자금 ERP(EOI 2026-05) — 낙찰 결과 확인 후 GMP 계층 보완 제안","② ADB US$336.5M 백신·치료제 제조 프로젝트 — 국제경쟁 조달, 디지털 GMP(MES/eBR·LIMS·QMS) 패키지","③ 한국 EDCF US$3B(2023-27)·KOICA 2026-28 US$96M — 보건·제약 디지털화 후보사업화(ERD 제안)","④ WB 보건 PforR·조달 디지털 $55M — 간접 연계"],C.GOLD,{fs:9.6});
  card(s,MX+8.1,1.4,3.9,2.6,"ASC 차별화",["이미 동작하는 AX 플랫폼(M0~M7 · 판단카드·승인함·KPI 센터) — 개념이 아닌 실물","Odoo 20 MCP/JSON-2/웹훅 연결 설계 보유 · GPU 국내 LLM 옵션","PI 041 데이터 무결성 패키지 · GS1 시리얼 선반영 · Mushak 6.3·e-GP 연계","오프라인 내성·소버린 클라우드 호환 설계"],C.GREEN,{fs:9.6});
  table(s,["단계","고객사 준비·참여","목적"],[
    ["전 단계","전담 PM(의사결정 권한) · QA/QP · 업무별 Key User 지정 · 의사결정 기한 준수","지연 방지·커뮤니케이션 단일화"],
    ["분석~설계","현행 SOP·배치기록·품목/BOM/거래처 데이터 · 공정 인터뷰(업무별 1~3회) · GMP 갭 공동 확인","요구사항 누락 방지"],
    ["구축~검증","스프린트 리뷰 · UAT · PQ(배치 1사이클) 참여 · 밸리데이션 Sign-off","품질 확보·재개발 방지"],
    ["운영 전환","운영 조직·SOP·교육 완료 · 하이퍼케어 · 정기평가 주기 합의","Go-Live 이후 혼선 방지"],
  ],MX,4.2,12,[1.5,7.5,3.0],{fs:9.5,rowH:0.42,boldCol:0});
  note(s,"※ 외국기업 현지 에이전트 의무·국내우대 조항 등 PPR 2025 세부는 착수 전 법률 검토 필요.",6.5);
  foot(s,k);
}

// ───────────────────────── 30. 제안사 소개
{ const s=p.addSlide(); titleBar(s,"ABOUT ASC","제안사 — 에이에스씨(ASC) · AX 플랫폼: 방법론이 아니라 이미 동작하는 시스템"); const k=pg();
  card(s,MX,1.4,5.9,2.5,"AX 플랫폼 (odooaierp.com) — 구축 완료·실운영",["M0 공통기반(SSO·백업·레지스트리·반출게이트) · M1 수집(CDC·엑셀·장표·IoT) · M2 표준데이터셋·품질게이트","M3 분석 스튜디오 · M4 학습엔진(수요예측·이상탐지·설비예지, 모델 카드) · M5 지식그래프(4M·확신도 루프)","M6 LLM 판단(GraphRAG·판단 카드·회귀 30선) · M7 에이전트·관제(승인함·War Room) · 프로젝트·KPI 센터","Odoo 연동: CDC 논리복제·승인 카드→구매발주 초안·Odoo 승인함 애드온 · PostgreSQL 이중 백엔드 · 150+ 자동 테스트"],C.NAVY2,{fs:9.6});
  card(s,MX+6.1,1.4,5.9,2.5,"실증 결과(합성·실데이터 데모)",["수요예측 WAPE 7.0% · 설비 고장 13일 선행 신호(OVEN-2) · 판단 카드 11건 승인 E2E","프로젝트·KPI 센터: 경영목표 4 + 기술 KPI 9 — 달성도 자동 집계·정직한 미달 표시","베이커리 제조사(원자재 로트·FEFO·다지점·B2B) 맞춤 제안 및 데모 수행","운영: Cloudflare 터널·백업/복구 드릴·업타임 감시·과금·테넌트 관리"],C.GREEN,{fs:9.6});
  s.addText("제약 GMP 적용 시 ASC가 추가로 제공하는 것",{x:MX,y:4.05,w:8,h:0.35,fontFace:F,fontSize:12.5,bold:true,color:C.NAVY});
  flow(s,["GMP 레이어\n(감사추적·서명·eBMR·QMS)","CSV 패키지\n(VMP~PQ·추적성)","Odoo 20 연결\n(MCP·JSON-2·웹훅)","6종 제약 에이전트\n+ 승인함·관제탑","현지화\n(Bangla·Mushak·e-GP)","교육·하이퍼케어\n·정기평가"],MX,4.5,12,{h:0.95,fs:9.5});
  s.addShape("roundRect",{x:MX,y:5.7,w:12,h:1.1,rectRadius:0.06,fill:{color:C.HEAD}});
  s.addText([{text:"한 문장  ",options:{bold:true,color:C.NAVY}},{text:"\"문서에 있으면 사람이 지켜야 하지만, 플랫폼이 되면 구조가 지킵니다.\" — GMP의 데이터 무결성도, 조달의 투명성도, AI의 판단도 같은 원리로 설계합니다. 귀사를 위해 설계했고, 그 설계는 이미 동작합니다.",options:{color:C.INK,italic:true}}],{x:MX+0.2,y:5.7,w:11.6,h:1.1,fontFace:F,fontSize:11,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 31. 다음 단계
{ const s=p.addSlide(); titleBar(s,"NEXT STEP","다음 단계 — 확인할 것, 함께 할 것"); const k=pg();
  card(s,MX,1.4,5.9,2.9,"착수 전 확인 리스트 (귀사·조사 필요)",["귀사 정확한 법인·규모·품목·공장(EDCL 여부) · 현행 시스템/수기 범위","2026-05 ERP EOI 결과(낙찰·RFP 단계) 및 모듈 범위 · 주계약 구조","ADB 백신공장 프로젝트 조달계획·디지털 GMP 범위","DGDA 최신 GMP·데이터 무결성/CSV 가이드라인 · 시리얼라이제이션 계획","호스팅(국가 DC/소버린 클라우드/온프렘) · 데이터보호령 최신 개정","PPR 2025 외국기업 참여 조건 · 현지 파트너 후보"],C.RED,{fs:9.8});
  card(s,MX+6.1,1.4,5.9,2.9,"제안 로드맵 (Next 90일)",["1주: 본 1차 제안 검토·피드백 · 확인 리스트 회신","2~4주: 온라인 워크숍(QA·생산·창고·구매·회계) — GMP 갭·요구사항 1차 확정","4~8주: 현장 진단(선택) · URS·VMP 초안 · 범위·일정·견적 · 파트너 구조 확정","8~12주: 파일럿 라인 범위 Sign-off · 착수","병행: AX 플랫폼 라이브 데모(app.odooaierp.com) · 제약 시나리오 데모 데이터 구성"],C.GREEN,{fs:9.8});
  s.addShape("roundRect",{x:MX,y:4.5,w:12,h:1.2,rectRadius:0.07,fill:{color:C.NAVY}});
  s.addText([{text:"제안·문의   ",options:{bold:true,color:"9FC7BD"}},{text:"에이에스씨(ASC) · AX 플랫폼 사업팀   ·   odooaierp.com   ·   asclhg@gmail.com\n",options:{color:"FFFFFF"}},{text:"라이브 데모: app.odooaierp.com (요청 시 계정 발급)  ·  영문 제안서(English version) 별도 제공 가능",options:{color:"C9D9E3",fontSize:10}}],{x:MX+0.3,y:4.5,w:11.4,h:1.2,fontFace:F,fontSize:12.5,valign:"middle"});
  note(s,"본 제안서의 수치·일정·범위는 1차 개략 제안이며, 리서치는 2026-10-22 기준 웹 조사(출처 부록)에 근거합니다. 규제 조항 인용은 EudraLex/eCFR/WHO 원문으로 최종 확인 후 제출본에 반영합니다.",5.9,{h:0.6,fs:9.5});
  foot(s,k);
}

// ───────────────────────── 32. 부록 출처
{ const s=p.addSlide(); titleBar(s,"APPENDIX","부록 — 주요 출처 (2026-10-22 조사)"); const k=pg();
  const cols=[["규제·표준",["WHO TRS 986 Annex 2 · TRS 1033 Annex 4 · TRS 1019 Annex 3","EU GMP Annex 11(2011/2025 초안)·Annex 15·Ch.1/4/8","FDA 21 CFR Part 11 · CSA 가이던스(2025)","PIC/S PI 041-1(2021) · ISPE GAMP 5 2nd ed.","TGA ALCOA+ 매핑"]],
   ["Odoo 20",["odoo.com 릴리스 노트(20·19.x) · Meet Odoo 20 블로그","Odoo 20 문서: MCP 서버·AI 필드·외부 RPC API·Studio 자동화·오프라인 모드·제조/재고","파트너: Braintec·iVentureTeam·Octura·Macopedia·Cybrosys 등","OCA auditlog · quality_control_oca · 파트너 eBMR/Audit Trail 모듈"]],
   ["방글라데시",["BPPA EOI EDCL/Dhaka/EOI/Tender/2026/168 · EDCL 포털·Wikipedia·MCCI","ADB 4388-BAN(US$336.5M)·ADB Brief 302 · WHO Bangladesh NRA","TBS·Daily Star·Dhaka Tribune·FE·Prothom Alo(산업·GMP·정전·PPR 2025·EDCF)","Drugs & Cosmetics Act 2023 · tralac/RAPID(LDC) · DataReportal 2026"]],
   ["벤치마크·KPI",["Odoo 공식 고객사례(Brand Pharma·Magis·Fito Medic's·Fraver 등) · SDLC·Ksolves(파트너)","Körber(Cipla·Ferring) · Emerson/ISA · FPT IS(Vinphaco) · ABeam(Pharmaniaga)","Kimia Farma 연구(UGM/Telkom) · EIPICO AR · Vinapharm · SPMC · India PSU","FDA Quality Metrics · IPA 편차 연구 · McKinsey QC · intuitionlabs KPI"]]];
  cols.forEach((c,i)=>{ card(s,MX+(i%2)*6.075,1.4+Math.floor(i/2)*2.6,5.925,2.45,c[0],c[1],[C.NAVY2,C.GREEN,C.GOLD,C.PURPLE][i],{fs:9.3}); });
  note(s,"전체 URL 목록(약 300건)은 별도 리서치 보고서 3종(research_odoo20 · research_pharma_gmp · research_bangladesh)에 수록 — 요청 시 제공. 조사 환경상 원문 직접 열람이 제한되어 검색 발췌·파트너 교차검증에 근거함.",6.5,{h:0.5});
  foot(s,k);
}

const out="/home/user/thirdbrain-web/docs/presentations/방글라데시_국영제약사_Odoo20_GMP_AX_제안서.pptx";
p.writeFile({fileName:out}).then(()=>console.log("DECK",out,"slides",n));
