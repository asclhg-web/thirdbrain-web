# Odoo 20 리서치 리포트 (2026-10-22 기준)

> **조사 방법 및 한계**: 본 세션의 네트워크 정책상 `odoo.com` 직접 접속(WebFetch/curl)이 차단되어, 공식 페이지(릴리스 노트·문서·블로그)의 내용은 검색 엔진이 반환한 공식 페이지 발췌/요약과 이를 인용한 파트너 블로그를 교차 검증해 정리했습니다. 각 항목에 신뢰도 태그를 붙였습니다.
>
> - **[공식]** odoo.com 릴리스 노트 / 공식 문서 / 공식 블로그에서 확인된 내용
> - **[파트너]** Odoo 파트너·컨설팅사 블로그(대부분 공식 릴리스 노트를 인용) — 대체로 신뢰 가능하나 원문 확인 권장
> - **[미확인/상충]** 출처 간 상충하거나 단일 2차 출처만 있는 내용
>
> 제안서에 인용할 때는 반드시 하단 Sources의 공식 URL에서 원문을 재확인하시기 바랍니다.

---

## 1. 릴리스 상태 및 일정

| 항목 | 내용 | 신뢰도 |
|---|---|---|
| **Odoo 20 릴리스 여부** | **정식 출시됨.** Odoo Experience 2026(브뤼셀 엑스포, 2026-09-24~26) 개막 키노트(Fabien Pinckaers CEO)에서 2026-09-24 공개. odoo.com 릴리스 노트 페이지에 "Version 20 — Released September 2026"으로 표기. 공식 블로그 "Meet Odoo 20" 게시. | [공식] |
| 공식 지원 기간 | 20.0: 2026-09 출시, 표준 지원 종료 예정 2029-09 (메이저 버전 3년 표준 지원, 이후 유료 연장 지원). | [공식] (standard_extended_support 문서) |
| Odoo 17 지원 종료 | 2026-09 표준 지원 종료(예정). EOL 후 6개월간 업그레이드 소스 버전으로만 사용 가능. | [공식] |
| Odoo 19 | 2025-09 출시(Braintec 릴리스 노트 기사 2025-09-18). 온라인(SaaS) 포인트 릴리스 19.1~19.4 존재, saas-19.4는 2026-07 출시. **19.4에서 MCP 서버·"Topics→Skills" 명칭 변경이 먼저 도입**되어 Odoo 20에 포함됨. | [공식] |
| 상충 사항 | 일부 소스는 "Odoo 20은 2026년 10월 중순부터 이용 가능"으로 기술(Odoo Online 롤아웃 시점으로 추정). 9월 24일은 공개/정식 발표일, 호스팅별 가용 시점은 다를 수 있음. | [미확인/상충] |
| 기술 요건 | Python ≥ 3.12, PostgreSQL ≥ 16 (설치 문서 기준, 파트너 확인). 일부 블로그의 "Python 3.13 표준" 주장은 단일 출처. | [파트너] |
| 규모 | 파트너 집계: 공식 릴리스 노트 기준 52개 앱 585건 변경(iVentureTeam) / "612개 신기능"(Techultra) — 집계 방식 차이. 상당수가 국가별 로컬라이제이션. | [파트너] |

**결론**: Odoo 20은 루머나 베타가 아닌 **정식 릴리스**이며, 제안서에서는 "Odoo 20 (2026-09 출시, 2029-09까지 표준 지원)"으로 기술 가능.

---

## 2. Odoo 20 주요 신규/강화 기능 (모듈별)

### 2.1 AI (Odoo AI 앱, 에이전트)
Odoo 20의 핵심 테마. 공식 블로그 문구: *"automate any process just by telling your AI agent what to do, in plain language."*

| 기능 | 설명 | 신뢰도 |
|---|---|---|
| **에이전트의 자율 실행** | "Agents can be summoned by automated and scheduled actions." — 자동화 규칙(레코드 생성/수정 트리거) 또는 스케줄(크론)로 에이전트 실행. 기존(19)에는 사용자가 대화로 호출하는 방식이 중심. | [공식] |
| **자동화 채팅 감사(Audit)** | "Check automation chats to see how agents handled them, and ask for changes based on the errors it faced." — 에이전트가 자동 실행한 처리 내역을 채팅 로그로 검토·수정 요청 가능. | [공식] |
| **레코드 생성/수정** | "Ask an AI agent to create anything for you, including by uploading a file of instructions like a PDF." 에이전트가 레코드 생성·갱신 가능(19에서는 기본 Ask AI는 읽기만). | [공식] |
| **자기 개선 에이전트** | "Agents can now update themselves to best serve their use cases." | [공식] |
| **Skills (구 Topics)** | 19.4/20에서 "Topics"→"Skills"로 명칭 변경. 내장 Skill 8종(Create Records, Update Records 포함 — FactoryJet). | [공식: 명칭변경] / [파트너: 8종] |
| **소스 재처리** | 에이전트에게 지식 소스(문서/링크/PDF)의 최신 버전 재수집 요청 가능. (19.1 도입) | [공식] |
| **파일 Q&A** | 파일 미리보기 중 해당 파일에 대해 직접 질문. | [공식] |
| **리포팅 보조** | 에이전트가 뷰 생성 시 기간(주/분기 등) 필터 적용. 파트너 소스는 "자연어로 피벗/그래프/실시간 대시보드 생성"으로 소개 — 공식 노트 원문은 더 보수적. | [공식: 기간필터] / [파트너: 대시보드] |
| **회계 AI 에이전트** | 미수금·현금흐름 등 질의응답, 은행 대사 오류 감사 및 수정 권고(파트너 서술). | [파트너] |
| **웹사이트 AI** | 프롬프트로 페이지 생성. | [공식 블로그] |
| **AI 제공자 선택** | "Select an AI provider and Odoo automatically uses the best AI model for the task at hand." 19에서는 OpenAI(ChatGPT)·Google Gemini 지원; Anthropic Claude 등은 서드파티 모듈. 20의 내장 제공자 확장 여부는 미확인. | [공식: 문구] / [미확인: 20 제공자 목록] |
| **과금: IAP 크레딧** | "All AI features now need credits, which can be bought via IAP." 어떤 플랜에도 크레딧 미포함. 파트너 조사(2026-10-06): Odoo AI 서비스 €1.00/크레딧, 10~1,000개 팩, 20 크레딧 무료, 유효기간 없음, 기능별 소모율은 비공개. **스케줄 에이전트는 실행마다 크레딧 소모** → 사용자당이 아닌 에이전트당 예산 책정 필요. | [공식: 크레딧 필수] / [파트너: 단가] |
| 기술 | 지식 소스 임베딩에 pgvector 사용, AI 관련 모듈 15→51개로 증가(Octura, 프리릴리스 빌드 분석). | [파트너] |

### 2.2 MCP 서버 (신규, 외부 AI 연동) — 상세는 3장

### 2.3 제조 (Manufacturing / MRP / Shop Floor / MPS)
파트너 집계: 공식 노트 기준 24건(신기능 5, 개선 18, 제거 1; Community 22, Enterprise 전용 2).

| 기능 | 설명 | 신뢰도 |
|---|---|---|
| **연속 생산(Continuous Production)** | BoM에 설정 시 일부 수량 완료되면 후속 공정 즉시 시작. 작업지시(Work Order)에 생산 수량 기록 가능. (saas-19.4 선도입) | [공식] |
| **작업지시 Kanban 뷰** | "Visualize and adapt work order planning with the new work order Kanban view." 카드 드래그로 작업장 재계획. | [공식] |
| **Gantt 개선** | 완료된 작업지시 Gantt 기본 표시; MO Gantt 제품별 그룹; 직원 Gantt에 부하(Load) 바. (19.2에서 드래그앤드롭 Gantt·직원별 뷰 도입) | [공식] / [파트너: 부하바] |
| **백오더 자동 계획** | 계획된 생산의 백오더 생성 시 자동 스케줄링. | [공식] |
| **MO 분할(Split MO)** | 제조 오더 분할. | [파트너] |
| **Shop Floor** | 작업장 바코드 스캔으로 작업장 선택; MO 메모 필드 HTML화(작업 지시서 서식 공유); Manufacturing/Shop Floor/Barcode에 단일 "Produce" 버튼. | [공식] |
| **WIP 원가** | 진행 중 MO의 WIP 분개 수동 전기/역분개, MO 예상원가 vs 실제원가 비교(붉은/녹색 강조). 20.0 문서에 존재(20 신규인지 여부 불명). | [공식 문서] |
| **MPS** | Odoo 20 MPS 전용 변경 사항은 **확인되지 않음**. 19.x에서 파트너가 "롤링 호라이즌·what-if" 등을 언급하나 단일 컨설팅 출처. | [미확인] |
| **카메라/하드웨어** | 신규 **OBox** 앱(IoT Box 관리; 기존 iot 모듈과 병존). 프린터·저울·카메라·Android 지원. 카메라는 품질관리점(QCP)에 연결 가능(기존 IoT 문서). | [파트너: 프리릴리스 분석] |
| 개발자 | `mrp.bom.apply_new_version()`이 다른 제품용 리비전일 때 이전 BoM을 더 이상 아카이브하지 않음. | [공식] |

### 2.4 품질 (Quality) — Enterprise 전용
파트너 집계: 공식 노트 기준 2건(모두 Enterprise).

| 기능 | 설명 | 신뢰도 |
|---|---|---|
| **품질검사 우회(Bypass)** | 품질 관리자(admin) 사용자만 품질검사 미완료 상태에서 재고 이동(transfer) 진행 가능. 일반 사용자는 불가 → 긴급 출하 통제 가능. | [공식] |
| **실패 위치(Failure Location)** | 검사 실패 시 검사 폼에서 실패 위치 지정(Fail 버튼 → 대화상자, 후보 위치는 QCP에 설정된 위치). 19.0에서 QCP의 "Failure Locations" 옵션으로 도입(파트너), 20에서 검사 폼 레벨로 확장. | [공식] |
| **공급사 품질률(Vendor Quality Rate)** | 구매 앱: 해당 공급사 납품 품질검사 통과율(%)을 공급사별로 산출, 클릭 시 사전 필터된 Quality Check Analysis 리포트. | [공식] |

### 2.5 재고 / Lot·Serial / 유효기간
| 기능 | 설명 | 신뢰도 |
|---|---|---|
| **Lot/Serial 자동 생성** | "Lots and serial numbers are always automatically generated when closing manufacturing orders." | [공식] |
| **리콜 추적 개선** | Lot/Serial의 "Transfers" 스마트 버튼이 전체 이동이 아닌 **출고 이동 라인(delivery move lines)** 표시 → 타겟 리콜 용이. | [공식] |
| **통합 추적성 리포트** | "The Traceability Report has been improved to display upstream and downstream lot/serial numbers in a single report." | [공식] |
| **재고 평가** | 디버그 모드 "Valuation Adjustments" 메뉴(원가 조정 및 평가 영향 목록); Inventory 앱 없이 재고 수량·회계 평가 관리; 납품 미청구/입고 미청구 가시화. | [공식] |
| 기타 | 재고 에이징(Stock Aging) 리포트, 권장 재주문점(Suggested reorder levels), 예측 리포트에서 입고→출고 "Assign" 링크, CMR 운송장 생성, 회사간 플로우 개선. | [파트너] |
| **유효기간(Expiry)** | Odoo 20 전용 변경 **미확인**. 기존 기능 유지: Lot별 Best before / End of life / Alert / Removal 날짜, 제품 Shelf life 기반 자동 계산, **FEFO** 제거 전략(제품 카테고리/위치 단위). **19.0**: 예측 리포트가 유효기간 만료로 재고에서 제거해야 할 제품 표시. | [공식: 19.0] / [미확인: 20] |
| 19.0 참고 | 패키지 안의 패키지(nested packages), 평가 마감 인터페이스 및 이동 백데이팅. | [공식: 19.0] |

### 2.6 유지보수 (Maintenance) — Community 포함
- 유지보수 요청 **Gantt 뷰** ("Planning by Equipment": 장비별 행, 요청별 바, 월 단위). [공식]
- 유지보수 팀별 **커스텀 단계(stages)**. [공식]
- (19.2) 작업장 개요에서 유지보수 계획 바로가기. [공식]

### 2.7 PLM — Enterprise 전용
- **Compare BoMs** 액션: 2개 이상 BoM 구성품을 피벗 테이블로 병렬 비교. [공식]
- ECO 적용 시 버전 업데이트 선택(optional). [공식]
- Universal ECO 리포트(모든 BoM 변경 + 원가 비교; 19.3 도입). [공식]

### 2.8 회계 (Accounting)
| 기능 | 설명 | 신뢰도 |
|---|---|---|
| **Odoo 내 공급사 청구서 지급** | PISP(결제 개시 서비스) 연동으로 청구서 선택→Pay→은행 승인(단건/배치). 은행·국가별 가용성 상이. 지급 전 중복 결제 경고 위저드. | [공식 블로그] / [파트너: 상세] |
| **은행 대사 재구축** | 은행 계정에 영향을 주는 모든 분개는 은행 거래에서 출발; "Run Auto Reconciliation" 수동 재실행; 한 거래를 여러 계정으로 분할; 대사 요약 리포트. | [파트너] |
| **청구서 라인 자동 제안** | 과거 청구서·라인 라벨 기반 제품/계정/세금/분석배분 제안(수동 입력값 보존). | [파트너(공식 인용)] |
| **PO 매칭 강화** | 수량/가격 불일치 경고, 매칭 요약, 청구서-PO 언매치. 중복 청구서 적색(유력)/황색(가능) 표시. | [파트너] |
| **업그레이드 주의** | 결제 상태명 변경("In Process"→"Paid", "Paid"→"Reconciled"); 계정 그룹→상위 계정(parent accounts) 대체. 기존 필터/연동 점검 필요. | [파트너] |
| 영국 | 회사별 HMRC 인증(UK VAT). | [공식 블로그] |

### 2.9 구매 (Purchase)
- 공급사별 **기본 Incoterm** (Community 포함). [파트너(공식 인용)]
- **대체 견적(Alternatives) 비교 화면 개선**; `purchase_requisition`에서 신규 `purchase_alternative`(+`_stock`, `_sale`) 모듈로 분리 → 커스텀 코드 의존성 수정 필요. [파트너(공식 인용)]
- 공급사 품질률(2.4 참조). [공식]

### 2.10 문서/서명/지식 (Documents / Sign / Knowledge) — Enterprise
- **Documents**: 접근권한 관리(사용자 그룹 단위 Viewer/Editor 부여), 은행명세서 첨부, 브랜치 관리 등 9건. [파트너(공식 인용)]
- **Sign**: 15건. **자동화 규칙/서버 액션에서 Sign 템플릿으로 서명 요청 자동 발송**; 완전 반응형(모바일/터치) 템플릿 편집기; 부분 서명 문서 다운로드(2차). [파트너(공식 인용)]
- Knowledge: 사이드바 우클릭 퀵 메뉴. [파트너]

### 2.11 플랫폼/일반
- **오프라인 모드** [공식 문서]: 단기 연결 중단 대응용(장기 오프라인 아님). 연결 끊기면 "Working offline" 버튼; 이전에 열었던 뷰/레코드 재열람 및 검색 재실행; 오프라인 변경은 로컬 큐 후 자동 동기화; 오프라인 데이터 최대 2GB; 오프라인 레코드 생성은 동일 유형을 온라인에서 생성한 적이 있어야 가능.
- Field Service → Planning 앱에 통합; Phone 앱 콜플로우 디자이너. [공식 블로그]
- **보안 모델 변경**: 레코드 룰(`ir.rule`) 제거, 접근권한(`ir.model.access`)과 통합한 **`ir.access`** 모델 도입 — 접근권한에 도메인 직접 지정. `ir.model.access.csv`/`ir.rule` XML을 쓰는 커스텀 모듈은 설치 실패 → 마이그레이션 필수. CSV 포맷도 변경(`operation` = c/r/u/d 문자열, `domain` 컬럼). [파트너(공식 인용) + Cybrosys 기술 분석]
- OWL 3 프런트엔드 전환: 다수 파트너 주장이나 20.0 공식 문서에서 미확인. [미확인/상충]

---

## 3. AI/에이전트 통합 표면 (외부 AI 에이전트 → Odoo)

### 3.1 외부 API 현황 (19/20)
| 채널 | 상태 | 비고 | 신뢰도 |
|---|---|---|---|
| **External JSON-2 API** (`/json/2/<model>/<method>`) | **Odoo 19 도입, 권장 API** | POST + JSON 바디, **named arguments**(positional 아님). `Authorization: Bearer <API key>`, 선택 헤더 `X-Odoo-Database`. API 키는 Preferences → Account Security에서 생성, 스코프(rpc) 지정. | [공식 문서] |
| XML-RPC (`/xmlrpc`, `/xmlrpc/2`), JSON-RPC (`/jsonrpc`) | **19.0부터 Deprecated** | `db` 서비스는 **Odoo 20에서 제거**(Online 19.1). `common`/`object` 서비스는 **Odoo 22(2028 가을) / Online 21.1(2027 겨울)** 제거 예정. 즉 20에서도 레거시 로그인/모델 호출은 동작하나 신규 연동은 JSON-2 권장. `@route(type='jsonrpc')` 컨트롤러는 해당 안 함. | [공식 20.0 문서] |
| `/doc` 엔드포인트 | DB별 모델·필드·메서드 문서 동적 생성 | 포럼 답변 기반, 신뢰도 낮음. | [미확인] |
| API 키 | 스코프 **RPC 또는 MCP**, 만료 1일/1개월/1년/무기한 선택 | 일부 보고: 신규 키 기본 만료 30일. | [공식: 스코프·만료] / [파트너: 기본값] |
| Odoo Online 플랜 제약 | 외부 API는 **Custom 플랜**에서만 사용 가능(One App Free, Standard 불가). | [공식 문서 인용(2차)] |

### 3.2 네이티브 MCP 서버 (Odoo 20 / Online saas-19.4 신규)
공식 20.0 문서: *"AI MCP server"* — 외부 AI 에이전트가 사용자 워크플로를 통해 DB를 읽고 수정할 수 있게 함. 클라이언트는 세션 시작 시 노출된 툴 목록을 요청·캐시.

| 항목 | 내용 | 신뢰도 |
|---|---|---|
| 엔드포인트 | `<DB URL>/mcp` (모듈 `ai_mcp`) | [공식 문서] / [파트너: 모듈명] |
| **인증** | **OAuth 2.1**(권장, 내부 사용자 전용) 또는 **API 키(MCP 스코프)**. 포털 사용자는 API 키만. OAuth 서버는 `/.well-known` 디스커버리 문서 및 사용자 동의 페이지 제공; 관리는 Settings → Integrations → "MCP OAuth". Dynamic Client Registration은 기본 OFF(관리자 활성화 필요). RPC 스코프 키는 거부됨. | [공식 문서] / [파트너: DCR 기본값] |
| **권한 모델** | AI는 키 소유자/OAuth 사용자의 **접근권한 범위 내에서** 동작("acts as the user"). 최소권한 전용 사용자 생성 권장. | [공식 문서] |
| **툴 = 서버 액션** | **기본 노출 5종(읽기 전용)**: Get Fields, Get Models, MCP Retrieve initial context, Search, Read group. 그 외(쓰기 포함) 툴은 개발자 모드 → Settings → Technical → Server Actions → Usage 탭 "Available in MCP" 체크로 수동 노출. 즉 **커스텀 서버 액션을 MCP 툴로 노출 가능**. | [공식 문서(5종)] / [커뮤니티 포럼: 노출 절차] |
| 검증된 클라이언트 | Claude(Desktop/Code), ChatGPT, Gemini CLI, Codex, Cursor, n8n 등(파트너 테스트). | [파트너] |
| **에디션** | Enterprise **AI 앱**의 일부. Odoo 20 및 Odoo Online saas-19.4+. **Community 미포함**, 16~19 on-premise 미포함(파트너 보고; 공식 에디션 표 미확인). | [파트너] |
| 비용 | MCP 자체 호출이 IAP 크레딧을 소모하는지 명시 자료 없음(LLM은 외부 클라이언트 측에서 실행되므로 크레딧 미소모로 추정 — **추정**). | [미확인] |
| 대안 | Community/구버전용 서드파티 MCP 서버 다수: `ivnvxd/mcp-server-odoo`, `tuanle96/mcp-odoo`(XML-RPC 16~18 / JSON-2 19+), `keboola/odoo-mcp`(OAuth 2.1), Webkul·Cybrosys 유료 모듈. 핵심 Odoo 기능 아님. | [커뮤니티] |

### 3.3 자동화 규칙 / 웹훅 (Studio, Enterprise)
- **인바운드 웹훅 트리거**: 외부 시스템 → Odoo 자동화 규칙 실행. **아웃바운드 웹훅 액션**: 레코드 이벤트 시 외부 URL로 데이터 전송. (20.0 Studio 문서) [공식 문서]
- **에이전트 호출 액션**: 자동화 규칙(생성/수정/시간 기반)이나 스케줄 액션의 액션으로 AI 에이전트에 프롬프트 전달 → 에이전트 실행 결과는 "automation chat"에 기록. [공식 노트 + 파트너]
- **AI 서버 액션**(19~): AI로 필드 값 갱신("AI updating fields in server actions"). [공식 19 노트]
- **AI 필드**(19~): Studio 또는 Property 필드로 추가, 프롬프트가 다른 필드값을 참조해 텍스트 생성; AI 아이콘으로 재생성; 실패 시 경고. [공식 문서]
- 주의: 업데이트 트리거 중복 실행 가능 → 주문 중복 등 멱등성 설계 필요. [파트너]
- Sign 자동 서명 요청, 에이전트 Create/Update Records Skill과 결합 시 "외부 이벤트 → 에이전트 판단 → 레코드 생성 → 전자서명 요청" 체인 구성 가능(설계 가능성; 구현 검증 필요).

### 3.4 Odoo 19 → 20 변화 요약 (AI/통합 관점)
| 영역 | Odoo 19.0 | Odoo 20 (및 saas-19.4) |
|---|---|---|
| 에이전트 | Topics+Sources 구조, 대화형. Topics 없으면 정보 제공만(DB 변경 불가). 내장 Topic: Natural Language Search, Information Retrieval, Create Leads(CRM). | **Skills**로 개명, 8종 내장(Create/Update Records 포함). 자동화·스케줄 액션에서 실행, 자기 개선, 자동화 채팅 감사. |
| 외부 AI 접속 | JSON-2 API(신규), 레거시 RPC. 네이티브 MCP 없음(19.0 문서 404). | **네이티브 MCP 서버**(OAuth 2.1/API 키, 서버 액션 기반 툴). |
| 제공자/과금 | OpenAI, Gemini. Online은 자체 키 불필요, .sh/on-prem은 키 필요(파트너). | 제공자 선택 후 Odoo가 모델 자동 선정; **모든 AI 기능 IAP 크레딧 필수**. |
| 기타 AI | 자연어 검색→도메인 변환, 라이브챗 에이전트 리드 생성, 회의 음성 전사·요약, AI 필드. | 파일 Q&A, 소스 재처리, 회계 에이전트, 웹사이트 페이지 생성. |
| 보안 | `ir.model.access` + `ir.rule` | **`ir.access`** 통합(레코드 룰 제거). |

---

## 4. 제약(GMP) 의약품 제조 관점 유용 기능

> **중요**: Odoo 공식 자료는 **21 CFR Part 11 / EU GMP Annex 11 준수를 주장하지 않습니다.** 아래 기능은 "컴플라이언스를 지원하는 빌딩 블록"이며, 실제 규제 준수는 CSV(IQ/OQ/PQ), SOP, 접근통제, 교육, 정기 검토가 필요합니다(복수 컨설팅 출처 공통 견해).

### 4.1 배치/로트 추적성
- 제품별 Lot/Serial 추적(입고→생산 투입→완제품→출고→반품 전 구간 로트 연계) — 코어 기능. [공식 문서]
- **(20) 통합 추적성 리포트**: 상류(원자재 로트)·하류(완제품 로트/출고) 단일 리포트 — 배치 계보(genealogy)·리콜 범위 산정에 직접 활용. [공식]
- **(20) Lot의 Transfers 버튼 → 출고 라인 단위** 표시: 특정 로트가 어느 고객에게 어떤 수량으로 나갔는지 즉시 식별(타겟 리콜). [공식]
- **(20) MO 종료 시 Lot/Serial 항상 자동 생성** — 로트 미부여 완제품 방지. [공식]
- 19.0: 중첩 패키지(package-in-package) — 2차 포장 단위 추적. [공식]

### 4.2 유효기간 / FEFO
- Lot 단위 4종 날짜(Best before / End of life(Expiration) / Alert / Removal), 제품 Shelf life로 자동 산출. [공식 문서]
- **FEFO** 제거 전략(제품 카테고리/위치 단위 강제 가능). [공식 문서]
- 19.0: 예측 리포트가 만료 임박/만료 제품 제거 대상 표시. [공식]
- 주의(벤더 주장): 표준 Odoo는 근접 만료 재고 출하를 **강제 차단**하지는 않음 → 품질관리점(QCP) 또는 자동화 규칙으로 차단 로직 보완 필요. [미확인/벤더]

### 4.3 품질 검사 / 관리점 (Quality, Enterprise)
- 입고·생산 공정(작업지시 단계)·포장·출고 시점 QCP 설정, 수치/합격불합격/사진/지침 등 검사 유형; 실패 시 Quality Alert. [공식 문서(일반)]
- **(19/20) Failure Location**: 불합격품을 지정 격리(quarantine) 위치로 자동 이동 — 부적합품 격리 요구에 부합. [공식]
- **(20) 검사 우회는 품질 관리자만** — 일반 작업자의 검사 생략 불가(권한 기반 통제). [공식]
- **(20) 공급사 품질률** — 공급업체 평가(Vendor qualification) 근거 데이터. [공식]
- 카메라(IoT/OBox) 연계 검사 사진 기록. [공식(IoT 문서) + 파트너(20 OBox)]
- 19.x: 품질 체크 워크플로가 Shop Floor 작업지시와 통합(파트너). [파트너]

### 4.4 감사 추적(Audit Trail) / 전자서명 / 문서관리
| 영역 | 현황 | 갭/보완 |
|---|---|---|
| 필드 변경 이력 | Chatter가 **tracking 설정된 필드**의 변경을 작성자·시각·이전/이후 값과 함께 기록; `create_uid/write_uid/create_date/write_date` 기본. | 모든 필드가 자동 추적되지는 않음(설정 필요); **읽기 접근 미기록**; 레코드 삭제 시 chatter도 함께 삭제되어 "누가 삭제했나" 추적 불가 → **OCA `auditlog`** 모듈(모델·작업별 로그 규칙) 또는 상용 감사 모듈 필요. |
| 에이전트 작업 이력 | (20) 자동화 채팅으로 에이전트 처리 내역 검토 가능. | GMP 감사증적으로 인정받기 위한 불변성·보존 기간 정책은 별도 검증 필요. |
| 전자서명 | **Odoo Sign**: 문서 변경·서명 전 과정 감사 로그, 공식 페이지는 eIDAS·US ESIGN Act 준수 주장. (20) 자동화 규칙에서 서명 요청 자동 발송, 모바일 반응형. | Part 11 전자서명 요건(서명 의미 표시, 사용자 ID+비밀번호 재인증, 기록과 서명의 연결 등)에 대한 공식 명시 없음 → 검증 필요. Sign은 Enterprise. |
| 문서관리 | **Documents**(Enterprise): (20) 그룹 기반 Viewer/Editor 권한, 폴더/워크플로, 버전. Knowledge로 SOP 문서화. | 통제문서(Controlled Document) 승인 플로우·버전 유효성은 Studio/자동화로 구성 필요. |
| 접근통제 | (20) `ir.access` 도메인 기반 접근권한 단일화 — 권한 매트릭스 단순·명확화. | 업그레이드 시 권한 재검증(OR/AND 의미 변화) 필수. |
| 오프라인 모드 | (20) 단기 오프라인 편집 큐 → 재접속 시 동기화. | 규제 환경에서는 오프라인 변경의 시각·순서 기록 검증 필요(분석 의견). |

### 4.5 제조 실행
- Shop Floor 태블릿 UI, 작업장 바코드 스캔, HTML 작업지시서(서식·이미지 포함 MBR/배치 기록 지침 표시), 작업자별 로그인/시간 기록. [공식]
- 연속 생산·MO 분할·백오더 자동 계획 — 다단계 공정(조립→충전→포장) 흐름 개선. [공식/파트너]
- WIP 원가 분개·예상 vs 실제 원가 — 배치 원가 분석. [공식 문서]
- Maintenance Gantt(장비별) — 설비 예방정비 계획(교정/CIP 일정 포함)의 시각화. [공식]
- PLM: ECO 승인 플로우, BoM 비교, Universal ECO 리포트 — 처방(Recipe)/BoM 변경관리(Change Control) 기록. [공식]

---

## 5. 에디션·가격 (모듈 가용성 관점)

### 5.1 에디션
| 구분 | Community (무료, 오픈소스 LGPL) | Enterprise (유료) |
|---|---|---|
| 포함 모듈(관련) | Inventory, **Manufacturing(기본 MRP, BoM, 작업지시)**, Purchase, **Maintenance**, 기본 Invoicing, (20) 공급사 기본 Incoterm 등 Community 변경 22건(제조) | 위 + **Quality, PLM, Shop Floor(고급), Barcode, MRP II/MPS·작업장 스케줄링, Documents, Sign, Studio(자동화 규칙/웹훅/AI 필드), Helpdesk, IoT/OBox, Full Accounting, AI 앱(에이전트, MCP 서버)**, 모바일 앱 |
| AI/MCP | 미포함(서드파티 MCP·AI 모듈로 대체 가능) | 포함(단, **AI 기능은 IAP 크레딧 별도**) |
| 호스팅 | On-premise | Odoo Online(SaaS, 커스텀 코드 불가), Odoo.sh(PaaS), On-premise |

※ 에디션 경계는 파트너 출처 종합이며 공식 비교표로 재확인 권장. 특히 Quality·PLM·Barcode·Studio·Documents·Sign·AI는 Enterprise 전용으로 일관되게 보고됨. [파트너 다수]

### 5.2 가격 (2026-10, 지역별 상이, 출처 간 상충 — 반드시 odoo.com/pricing 확인)
| 항목 | 보고된 수치 | 신뢰도 |
|---|---|---|
| **Standard** (Online 전용, 전 앱) | 미국 약 **$31.10/사용자/월**(연간, 첫해 할인 $24.90); 유럽 €24.90(첫해 €19.90) | [파트너, 상충] |
| **Custom** (Online/.sh/on-prem, Studio·API·멀티컴퍼니) | 미국 약 **$61.00/사용자/월**(첫해 $49.00); 유럽 €44.90(첫해 €35.90); 2027년 신규고객 약 20~23% 인상 보고 | [파트너, 상충] |
| **Light User (Odoo 20 신규 티어)** | 미국 $8.90 / 유럽 €7.90 / 인도 ₹195 (연간). Sales·Purchase·Project·Accounting 등 핵심 운영 앱 접근 불가; 휴가·경비·출근·POS·바코드 스캔 등 셀프서비스/현장 작업용. 일부 지역은 Advisor 견적. | [파트너 다수] |
| One App Free | 단일 앱 무제한 사용자 무료(Online) | [공식(일반)] |
| **AI 크레딧(IAP)** | €1.00/크레딧, 10~1,000개 팩, 20개 무료, 무기한. 기능별 소모율 비공개. 모든 플랜에 미포함. | [파트너(2026-10-06 확인)] / [공식: 크레딧 필수] |
| 외부 API/MCP 플랜 | Online에서 외부 API는 **Custom 플랜** 필요. MCP는 AI 앱(Enterprise) 필요. | [공식 문서 인용(2차)] |
| IoT Box 구독 | 프로덕션 사용 시 IoT Box 구독 필요(과거 $20/박스/월 보고, 시효 불명). | [미확인] |

**제안서 시사점**: 제약 제조 시나리오(Quality, PLM, Shop Floor, Documents, Sign, Studio 자동화, AI 에이전트/MCP)는 **Enterprise Custom 플랜**(또는 Odoo.sh/on-prem Enterprise)이 사실상 필수. 현장 작업자(바코드/Shop Floor 전용)는 Light User로 비용 절감 가능성 있으나, Shop Floor 포함 여부는 공식 확인 필요. AI 에이전트 운영비는 사용자 라이선스와 별도로 크레딧 예산 책정.

---

## 6. 확인/미확인 요약 (제안서용 체크리스트)

**확인됨 (공식 출처)**
- Odoo 20 정식 출시(2026-09-24, Odoo Experience 2026), 표준 지원 ~2029-09
- 에이전트의 자동화/스케줄 실행, 자동화 채팅 감사, 레코드 생성/수정(PDF 입력), Skills 개명
- 네이티브 MCP 서버(OAuth 2.1/API 키, 기본 읽기 5툴, 서버 액션 노출, 사용자 권한 준수)
- 모든 AI 기능 IAP 크레딧 필수
- JSON-2 API(19) 및 XML-RPC/JSON-RPC deprecation 일정(db 서비스 20 제거, 전체 22 제거)
- 제조: 연속 생산, 작업지시 Kanban, 백오더 자동 계획, Shop Floor 바코드/HTML 메모, 단일 Produce
- 품질: 관리자 전용 검사 우회, 실패 위치, 공급사 품질률
- 재고: MO 종료 시 Lot 자동 생성, Lot Transfers→출고 라인, 상·하류 통합 추적성 리포트, Valuation Adjustments
- 유지보수 Gantt/커스텀 단계, PLM Compare BoMs, 오프라인 모드(2GB, 큐 동기화)
- Python ≥3.12 / PostgreSQL ≥16

**부분 확인 (파트너 인용, 원문 확인 권장)**
- `ir.access` 보안 모델 통합, Sign 자동 서명 요청, Documents 그룹 권한, 회계 은행대사 재구축·PISP 지급, 구매 Alternatives 모듈 분리, OBox, Light User 가격

**미확인/상충**
- OWL 3 전환, Python 3.13, MPS 변경, Odoo 20 전용 유효기간 기능, 20의 내장 AI 제공자 목록, MCP 호출의 크레딧 소모 여부, Odoo 20 "10월 중순 가용" 표현, Enterprise 정확 단가

---

## Sources

### 공식 (odoo.com)
- Odoo Release Notes (버전 목록): https://www.odoo.com/page/release-notes
- Odoo 20 Release Notes: https://www.odoo.com/odoo-20-release-notes
- Odoo 19 Release Notes: https://www.odoo.com/odoo-19-release-notes
- Odoo 19.1 / 19.2 / 19.3 / 19.4 Release Notes: https://www.odoo.com/odoo-19-1-release-notes , https://www.odoo.com/odoo-19-2-release-notes , https://www.odoo.com/odoo-19-3-release-notes , https://www.odoo.com/odoo-19-4-release-notes
- 공식 블로그 "Meet Odoo 20": https://www.odoo.com/blog/odoo-news-5/meet-odoo-20-2439
- 공식 블로그 "Odoo unveils 2027 projects at Odoo Experience": https://www.odoo.com/blog/odoo-news-5/odoo-takes-stock-of-2026-and-unveils-its-ambitions-for-2027-during-odoo-experience-2444
- Standard and extended support (20.0): https://www.odoo.com/documentation/20.0/administration/standard_extended_support.html
- AI MCP server (20.0 docs): https://www.odoo.com/documentation/20.0/applications/productivity/ai/mcp_server.html
- AI fields (20.0 docs): https://www.odoo.com/documentation/20.0/applications/productivity/ai/fields.html
- AI agents (19.0 docs): https://www.odoo.com/documentation/19.0/applications/productivity/ai/agents.html
- AI fields (19.0 docs): https://www.odoo.com/documentation/19.0/applications/productivity/ai/fields.html
- AI in support workflows (19.0 docs): https://www.odoo.com/documentation/19.0/applications/productivity/ai/support_operations.html
- External JSON-2 API (19.0 docs): https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
- External RPC API — Deprecated (20.0 docs): https://www.odoo.com/documentation/20.0/developer/reference/external_rpc_api.html
- Automation rules (20.0 Studio docs): https://www.odoo.com/documentation/20.0/applications/studio/automated_actions.html
- Offline mode (20.0 docs): https://www.odoo.com/documentation/20.0/applications/general/offline_mode.html
- Manufacturing (20.0 docs): https://www.odoo.com/documentation/20.0/applications/inventory_and_mrp/manufacturing.html
- Work-in-progress costs (20.0 docs): https://www.odoo.com/documentation/20.0/applications/inventory_and_mrp/manufacturing/basic_setup/work_in_progress.html
- Lot numbers (20.0 docs): https://www.odoo.com/documentation/20.0/applications/inventory_and_mrp/inventory/product_management/product_tracking/lots.html
- Master production schedule (docs): https://www.odoo.com/documentation/master/applications/inventory_and_mrp/manufacturing/workflows/use_mps.html
- Odoo Sign: https://www.odoo.com/app/sign
- Odoo 포럼 — MCP Server overview: https://www.odoo.com/forum/help-1/odoo-mcp-server-overview-awesome-list-309347
- Odoo 포럼 — Audit logs: https://www.odoo.com/forum/help-1/where-can-i-find-or-activate-the-audit-logs-to-see-all-transactions-history-274717

### 파트너/2차 (릴리스 노트 인용·분석)
- Braintec — Odoo 20 Release Notes: https://braintec.com/en/news/insights/269/odoo-20-release-notes-all-the-new-features
- Braintec — Odoo 19 Release Notes: https://braintec.com/en/news/insights/180/odoo-19-release-notes
- iVentureTeam — Odoo 20 app-by-app: https://iventureteam.com/odoo-20-release-notes/ (Manufacturing: /manufacturing/, Quality: /quality/, PLM: /plm/, Purchase: /purchase/, Inventory: /inventory/, Sign: /sign/, Documents: /documents/)
- Octura — Manufacturing/Quality/Maintenance: https://octurasolutions.com/resources/odoo-20-manufacturing-quality-and-maintenance
- Octura — AI agents skills/sources/triggers: https://octurasolutions.com/resources/odoo-20-ai-agents-skills-triggers-and-ai-in-every-app
- Octura — MCP server: https://octurasolutions.com/resources/odoo-20-mcp-server-connect-claude-chatgpt-any-client
- Octura — OBox IoT: https://octurasolutions.com/resources/odoo-20-obox-iot-printers-scales-cameras-and-android
- Octura — Every app guide: https://octurasolutions.com/resources/whats-new-in-odoo-20-every-app-feature-guide
- Macopedia — Odoo 20 is out: https://macopedia.com/en/blog/news/odoo-20-whats-new
- Much Consulting — Odoo Experience 2026 / Meet Odoo 20: https://muchconsulting.com/blog/odoo-2/odoo-experience-2026-185 , https://muchconsulting.com/blog/odoo-2/odoo-20-186
- Nexuro — Odoo 20 key features / AI in Odoo 20: https://www.nexuro-digital.com/en/blog/the-nexuro-blog-1/odoo-20-the-key-new-features-from-odoo-experience-2026-131 , https://www.nexuro-digital.com/en/blog/the-nexuro-blog-1/ai-in-odoo-20-agents-automation-and-mcp-connection-132
- Maifelz — Odoo 20 Officially Released: https://www.maifelz.com/blog/odoo-20-release-date-features-roadmap-guide
- Obycron — Odoo 20 is here: https://www.obycron.be/en/blog/news-1/odoo-20-is-here-these-are-the-new-features-87
- Solvync — Odoo 20 Readiness Checklist (Python/PG 요건): https://solvync.com/odoo-20-readiness-checklist/
- daily.dev — AI agents in workflow: https://daily.dev/posts/odoo-20-the-release-where-ai-agents-become-part-of-the-workflow-ixkvacrrg
- Aarav Solutions — Odoo 20 release notes/pricing: https://www.aaravsolutions.com/odoo-20-release-notes-whats-new-what-it-costs-and-how-to-upgrade/
- SmartStream ERP — Odoo 20 guide: https://smartstreamerp.com/blog/odoo-20/
- Technext — Odoo 20 what's new: https://technext.asia/blog/odoo-20-whats-new
- Techultra — 612 features: https://www.techultrasolutions.com/odoo-20-features
- Ecosire — What's new in Odoo 20: https://ecosire.com/blog/whats-new-in-odoo-20
- Cybrosys — ir.access replacing ACLs/record rules: https://www.cybrosys.com/blog/how-new-iraccess-model-replacing-acls-and-record-rules-in-odoo-20 , https://www.cybrosys.com/blog/how-to-migrate-irmodelaccesscsv-and-record-rules-to-iraccesscsv-in-odoo-20
- Silverdale — Odoo 20 for Manufacturing: https://www.silverdale.us/blog/our-point-of-view-4/odoo-20-for-manufacturing-4514
- Gritxi — Odoo 20 Manufacturing: https://www.gritxi.com/blog/odoo-20-8/odoo-20-manufacturing-new-features-improvements-68
- Ochre — Odoo 20 Manufacturing/Quality confirmed: https://ochre.digital/blog/odoo-20-manufacturing-inventory-quality-whats-new/
- Contaldia — Odoo 20 accounting: https://www.contaldia.com/en/blog/accounting-4/odoo-20-accounting-reporting-updates-137
- Hadron — Odoo 20 for SMEs (accounting): https://hadron-for-business.odoo.com/blog/aktualnosci-2/odoo-20-is-here-what-s-new-and-what-it-means-for-your-company-105
- FactoryJet — AI agents 19/20: https://factoryjet.com/services/odoo-ai-agents
- Silent Infotech — Native MCP server: https://silentinfotech.com/blog/odoo-1/odoo-20-native-mcp-server-625
- nanti.ai — Odoo 20 MCP / Light User: https://nanti.ai/odoo-20-mcp , https://nanti.ai/odoo-20-light-user
- Pantalytics — Odoo 20 MCP tested: https://www.pantalytics.com/post/odoo-20-mcp-server
- Octivex — MCP / Webhooks vs automated actions: https://octivex.tech/blog/odoo-20-mcp-server , https://octivex.tech/blog/odoo-20-webhooks-vs-automated-actions
- CRM Authority — MCP security: https://www.crm-authority.com/en/odoo/article/odoo-20-serveur-mcp-natif-securite
- HQ GmbH / Auguria / Odin — JSON-2 API: https://www.hqgmbh.de/en/e-commerce-tips/odoo-19-json-2-api/ , https://www.auguria.fr/en/blog/blog-5/odoo-19-the-external-json-2-api-224 , https://www.odin.ist/blog/odoo-json-2-api.html
- Codetrade — Odoo AI 19 & 20 guide: https://www.codetrade.io/blog/odoo-ai-2026-guide/
- Certum — Odoo 19 AI setup: https://www.certumsolutions.com/library/odoo-ai-setup-your-own-agents
- SerpentCS — Odoo 19 Manufacturing (Failure Locations): https://www.serpentcs.com/blog/odoo-19-511/odoo-19-manufacturing-what-s-new-features-a-deep-dive-by-serpentcs-652
- Ecosire — Odoo 19 MRP/MPS/Quality: https://ecosire.com/blog/odoo-19-manufacturing-mps-quality-mrp
- Bista — Odoo 19.4: https://www.bistasolutions.com/resources/blogs/what-odoo-19-4-means-for-businesses/

### 가격/에디션
- Auboros — Odoo 20 AI credits cost: https://www.auboros.com/blog/ai-erp-australia-8/odoo-20-ai-credits-cost-australia
- Willdooit — Odoo pricing 2026 & Light User: https://www.willdooit.com/blog/news-16/odoo-pricing-2026-new-rates-and-light-user-tier-explained-116
- Bobby Bernier — Odoo 20 licensing: https://bobbybernier.co.uk/blog/odoo-20-licensing-pricing/
- iVentureTeam — Pricing / Light User: https://iventureteam.com/blog/odoo-pricing/ , https://iventureteam.com/blog/odoo-20-light-user/
- oec.sh — Odoo pricing / Community vs Enterprise: https://oec.sh/odoo-pricing , https://oec.sh/blog/odoo-community-vs-enterprise
- Pixelmechanics — Odoo pricing 2026 (EU): https://www.pixelmechanics.tech/en-int/blog/digitization-blog-2/odoo-pricing-2026-231
- Silent Infotech — Community vs Enterprise 2026: https://silentinfotech.com/blog/odoo-1/odoo-community-vs-enterprise-true-cost-comparison-2026-461
- Aidoo — Community vs Enterprise 2026: https://aidoo.ai/en/blog/odoo-community-vs-enterprise-comparatif-2026

### 제약/GMP/감사추적
- SerpentCS — Odoo Pharma ERP for GMP: https://www.serpentcs.com/industries/odoo-erp-for-pharmaceutical-manufacturing
- SDLC Corp — 5 Odoo apps for pharma audits: https://sdlccorp.com/post/5-key-odoo-apps-every-pharma-company-needs-for-regulatory-audits/
- Nerithonx — Pharma manufacturing software guide (compliance caveat): https://nerithonx.com/blog/pharma-manufacturing-software/
- Ecosire — Audit trail requirements in ERP: https://ecosire.com/blog/audit-trail-compliance-erp-systems
- Much Consulting — Odoo compliance: https://muchconsulting.com/blog/odoo-2/odoo-compliance-184
- OCA auditlog (참고용, 앱스토어): https://apps.odoo.com/apps/modules/18.0/audit_log_advanced , https://apps.odoo.com/apps/modules/19.0/odoo_document_audit_trail

### 커뮤니티 MCP 서버
- https://github.com/ivnvxd/mcp-server-odoo
- https://github.com/keboola/odoo-mcp
- https://mcp.so/server/odoo-mcp/tuanle96
- https://github.com/yourtechtribe/model-context-protocol-mcp-odoo
- https://webkul.com/blog/odoo-mcp-server/amp/
