# 『AI ERP 혁명 — Odoo와 지능형 ERP』 제3부·에필로그 구조 설계서

## 기본 정보

| 항목 | 내용 |
|------|------|
| 범위 | 제3부 「온톨로지 메커니즘으로 완성하는 AX — JEDAIX 방법론과 성공사례」 약 60페이지(약 85,000자) + 에필로그 약 7~8페이지(10페이지 미만) |
| 장 번호 | 18장~23장 (2부가 8~17장이므로 이어짐) + 에필로그 |
| 파일 위치 | `book/v2/manuscript3/` (00_cover3.md, 00z_part3.md, 18_ch18.md ~ 23_ch23.md, 24_epilogue.md) |
| 저자 | 이형근(제1저자, ERP·MES·SCM 30년) · **정인호(제2저자, i7/JEDAIX 대표 컨설턴트, 온톨로지 아키텍트)** — 3부는 정인호의 JEDAIX 방법론이 축. 표지·서지에 공저 반영 |
| 성격 | AI ERP의 특징과 활용을 온톨로지 메커니즘 툴(JEDAIX)의 결과로 연결하여 AX를 성공시키는 방법론 + 구체적 성공사례 |

## 3부의 핵심 소스 (모두 인용 허용 — 정인호 제공 자료)

- `book/research/jedaix_manual_v9.txt` — JEDAIX 사용자 운영 매뉴얼 Base Camp 2 (v9): Frame·5Space·6Station·PTGDA·TA 10종·Workflow 빌더·War Room·InventoryBufferAgent 사례·SCM Backbone 8도구·데이터 매핑 마법사·운영환경설정 매트릭스·용어집·부록
- `book/research/jedaix_ontology_agent_v9.txt` — Ontology 기반 AI-Agent Workflow 구축 (v9): Seed 성장 사슬·CoreSpace 좌표 매핑·Universal Metadata 9속성·Skill-Loop-Harness·HITL·OWL Class/Property 생성·전체 파이프라인 사례
- `book/research/jedaix_erp_pptx.md` — 경영 사각지대 가시화 AX: Enterprise Mission Critical Agent 구축 모델링 (발표자료)
- `book/research/seminar_aierp_openbrain.txt` 후반부(i7/JEDAIX 소개)
- 인용 표기: (정인호, 2026) 또는 "JEDAIX 운영 매뉴얼 v9", "JEDAIX 온톨로지 아키텍처 문서 v9"로 명시. blockquote 직접 인용 적극 활용.

## 3부의 관통 논리

```
1부: 방법론(3정5S→DMAIC 루프)  2부: 적용(Odoo 모듈 컨설팅)
                 ↓ 남은 문제
2부 15장의 결론: Odoo AI는 Define·Measure·Control에 유능하나
Analyze·Improve(다중 홉 추론·전사 인과·암묵지)가 결핍 — 온톨로지가 필요
                 ↓ 3부의 답
경영 사각지대(암묵지·파편 데이터)를 온톨로지 메커니즘으로 형식지화·통치(Govern)
= JEDAIX 방법론: 5Space×6Station 워크벤치 → PTGDA로 암묵지 발굴 →
  TA 분류 → Seed 성장 사슬 → OWL 온톨로지 → Agent Workflow 실행 → HITL
                 ↓ 결과
Odoo(형식지의 원장·실행) × JEDAIX(암묵지의 발굴·판단) = AX의 완성
매출·원가·생산성·품질의 구체적 성과 (성공사례)
```

## 장별 구성

- **18장. 경영 사각지대: AX의 마지막 관문** (9p, 12,500자) — `18_ch18.md`
  왜 DX 다음의 AX가 어려운가(pptx: "LLM Prompt로 자동 생성하는 Agent는 결국 부품, 전체 운영 구도는 사람이 설계", AX 표준화·투입비용·DX 대비 편익 증명 문제). 경영 사각지대의 정의: 데이터 없는 객체·관계, 형식지화되지 않은 의사결정, 파편화된 암묵 운영 — ERP가 비추지 못하는 곳에서 손실이 발생한다. JEDAIX 매뉴얼 1장의 "ERP가 있는데 왜 필요한가" 논리와 도입 전/후 비교표, ERP만 있을 때 vs 암묵 영역 통합 시 비교표 인용. 1·2부와의 연결: 2부 15장에서 확인한 Odoo AI의 Analyze·Improve 결핍 → 온톨로지 메커니즘 툴이 채우는 자리. AI ERP의 특징(실시간 수집·자동화·예측)이 사각지대 통합으로 비로소 완성된다는 논증. ERP 없는 소상공인·10인 이하 제조업체에게 갖는 별도의 가치.

- **19장. JEDAIX 온톨로지 아키텍처: 5 Space × 6 Station** (10p, 14,000자) — `19_ch19.md`
  전체 아키텍처(위→아래: 입력 데이터→Frame 공통 메타데이터 스키마→6Station 대화→PTGDA→온톨로지→Agent). Frame과 Universal Metadata 9속성(온톨로지의 정적 뼈대). 5 Space: 업무 공간의 구조화(공간별 의미·대응 부서 표), CoreSpace — 언어 토큰이 좌표로 매핑되는 지점(자연어 환경>문화·사회·심리 판단기준>산업별 메타데이터>암묵 요인의 5 Layer). 6 Station: 진단→분석→보고서→정책→규칙→업무논리의 흐름(워크스테이션), Space×Station 매트릭스(색칠 칸=활성 조합) 해설. 설계 철학: "맞다/틀리다" 이분법이 아닌 확률적 중간 상태("아직 확실하지 않지만 점점 그럴듯해지는")의 관리 — 1부 5장 DMAIC 루프의 통계적 사고와 연결. Gruber·TOVE 등 학술 온톨로지 계보(v1 6장)와 JEDAIX의 실무적 차별점.

- **20장. PTGDA와 TA: 암묵지 발굴의 알고리즘** (10p, 14,000자) — `20_ch20.md`
  3부의 기술적 심장. 폴라니·노나카(1부 계승)의 암묵지 이론이 알고리즘이 되는 과정. TA(Tacit Anomaly) 10종 분류체계(TA01~TA10, boundary_type: RoleBoundary/NormBoundary/SystemBoundary 등 — 부록 A 기반 표). PTGDA(Progressive Tacit-to-Governed Discovery & Adoption)의 상태 전이(seed→가설→검증→확정→통치, 부록 D 기반). Seed 성장 사슬: Linguistic·Semantic Seed가 TA 코드와 함께 축적→SEED_HYPOTHESIS→Ontological Seed 확정→OWL Class·Property 생성. LLM의 역할: 현장의 말("지난달 C라인에서 그런 적이 두 번 있었습니다")을 Chunk로 분해→TA 후보 분류→OWL 확정 — 6Station 대화의 실시간 공명 신호("반응이 뚜렷해지고 있습니다 — 한 단계 더 파고들어보세요") 사례 인용. HITL 원칙: 온톨로지가 아무리 정교해져도 사람의 승인 게이트가 최종 관문. 검증 체계(무결성·승인자 자격·순환 참조·권한 충돌·TA 코드 유효성).

- **21장. 온톨로지에서 실행으로: Agent Workflow와 SCM Backbone** (10p, 14,000자) — `21_ch21.md`
  온톨로지가 실행 코드가 되는 경로. Skill-Loop-Harness(온톨로지를 업무 논리로 보완하는 층). Workflow 빌더: 슬롯 채우기 설계·표준 템플릿 자동 생성·9종 자동 검증·BPMN 다이어그램·승인/반려 경로(반려 시 전 단계 재작업 자동 회귀). War Room: 실행 중 전 프로세스의 진행·지연 감시, 이상 신호→6Station 진단으로 환류(무한 루프의 JEDAIX 구현 — 1부 5장 LLM 무한 루프와 명시적 연결). InventoryBufferAgent 사례: 확정된 문제가 알림으로 끝나지 않고 실행 주체가 4단계 자동 수행→조정된 안전재고가 O2C 프로세스에 자동 반영. SCM Backbone 8 계산 도구(기간손익 프로젝션·안전재고/ROP·EOQ/MOQ·TOC 등)와 JIT·재고·창고·배송 사슬(수요예측→MPS→MRP/ROP→MOQ→안전재고→TOC). **Odoo와의 결합 구도**: Odoo=형식지의 원장·실행 손발(2부), JEDAIX=암묵지의 발굴·의미·판단 계층(3부) — 2부 16장 부스터 아키텍처에 JEDAIX를 위치시키는 통합 아키텍처 다이어그램. 데이터 매핑 마법사(레거시 엑셀·타 시스템 데이터의 온톨로지 편입 — Odoo 데이터 연계 경로).

- **22장. AX 성공 방법론: 진단에서 가치 창출까지** (10p, 14,000자) — `22_ch22.md`
  JEDAIX 관통 문제해결 5단계(①6Station 진단→②문제 확정→③실행 가능한 대안 제시→④HITL 사람의 결정→⑤표준 업무 흐름 반영 — 매뉴얼 5장 "문제의 성격과 무관하게 전체를 관통하는 방법론" 인용)를 전사 AX 방법론으로 일반화. 1부 6장 AX 5단계 로드맵과의 결합: 4단계 지능화에 JEDAIX 도입을 배치한 통합 로드맵(표). 1부 5장 DMAIC와의 대응(6Station 진단=Define·Measure, PTGDA=Analyze, Agent 대안=Improve, 표준 반영·War Room=Control). 도입 유형별 시나리오: ERP 없는 소상공인·10인 이하(JEDAIX 단독 시작→Odoo 확장) vs ERP 보유 중소기업(Odoo+JEDAIX 병행) — 각각 기간·체제·성공판정. 운영환경설정 매트릭스(변수 체계 맞춤, 결정론적 설정 자물쇠)와 대화형 맞춤("산업/업종 무관, 기업 데이터 여건에 맞추어 대화형으로"). 성공 판정 KPI와 정직한 평가(온톨로지 구축의 초기 노력, 조직 수용성, 확정 암묵지가 없을 때의 빈 화면 — "시스템이 멈춘 게 아니라 아직 확정된 암묵지가 없다는 뜻" 인용).

- **23장. 성공사례 연구: 사각지대에서 성과로** (10p, 14,000자) — `23_ch23.md`
  사례연구 장. ①JEDAIX 제조회사 사례 심층 2건(매뉴얼 4장: 안전재고 사례 — 6Station 대화에서 담당자 증언→TA 확정→InventoryBufferAgent 4단계→O2C 반영; 5장: 조립 공정 병목 사례 — "조립 라인이 다른 공정보다 항상 느린데 계획은 재단 공정 속도로" 증언→TOC 분석→경영진 임시 인력 배치 결정→병목 처리능력 수치 반영, 온톨로지 문서 7부 파이프라인) — 각각 배경/대화/발굴/실행/성과 구조로 상세히. ②부문별 성과 메커니즘 요약(v1 3부 압축 계승): 영업 매출증대(리드 스코어링·수요예측), 구매·재고 원가절감(피킹 30%·중기부 원가 -15.9%), 제조 생산성(OEE·중기부 +30%·솔젠트 +73%), 품질 불량률(중기부 품질 +43.5%·대성 -50%) — 각 부문을 "사각지대→온톨로지 발굴→실행→KPI 성과" 프레임으로 재구성, 해외 Odoo 사례(Kompass +50%, Zeitgeist 3배 등) 포함. ③사례 종합: 성공요인 분석(작게 시작·HITL·경영자 관여·코드체계) — 3부작 전체의 실증적 결론.

- **에필로그. 두 개의 뇌, 하나의 기업** (7~8p, 10,000자 — 10페이지 미만 엄수) — `24_epilogue.md`
  두 저자의 목소리로 3부작 결산. ①이형근: 30년 전 관리판 앞에서 시작해 3정5S→DMAIC 루프→Odoo 플랫폼까지 — 형식지의 길(1·2부 회고) ②정인호: 경영 사각지대의 암묵지를 온톨로지로 통치하는 길(3부 회고) — "컴퓨팅 체계에 의미의 씨앗을 심어 업무 지식의 나무로 자라게 하는 줄기세포"(자라고 성장하는 온톨로지) ③두 길의 합류: Odoo(기업의 기록)×온톨로지(기업의 의미)×LLM(기업의 언어)=서드브레인, 기록하는 ERP에서 판단하는 ERP로의 최종 명제 ④독자에게: 작게 시작하되 온톨로지를 첫날부터 심어라, 사람을 루프 안에 남겨두라, "AI가 기업을 대체하지 않는다. 서드브레인을 가진 기업이 그렇지 않은 기업을 대체한다" ⑤감사의 글: 세미나·생산관리 고전·동기ERP 계보에 대한 감사.

## 집필 규칙

- `/home/user/thirdbrain-web/book/STYLE.md` 전 규칙 + v2 1·2부와 동일 문체.
- JEDAIX 자료의 개념·화면·사례·용어를 적극 인용(제2저자 자료이므로 제한 없음). 단 직접 인용은 blockquote + 출처("JEDAIX 운영 매뉴얼 v9" 등), 개념 설명은 본문 서술로 소화.
- JEDAIX 용어 표기 통일: 5 Space, 6 Station, PTGDA, TA(Tacit Anomaly), Frame, CoreSpace, Seed, OWL, Skill-Loop-Harness, War Room, HITL(Human-in-the-Loop), 데이터 매핑 마법사.
- 1·2부 상호 참조 명시("1부 5장의 DMAIC 루프", "2부 15장에서 확인했듯").
- 각 장 끝: "핵심 요약" + "이 장의 참고문헌". 에필로그는 참고문헌 없이 감사의 글로 마무리.
