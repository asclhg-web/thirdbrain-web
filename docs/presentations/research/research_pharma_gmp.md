# 제약 GMP 공장용 ERP 및 Odoo 적용 조사 보고서
**(Research Report: ERP for Pharmaceutical Manufacturing under GMP, and Odoo in Pharma)**

- 조사일: 2026-10-22
- 용도: 국영 제약회사(GMP 공장 보유) 대상 ERP 제안서 근거 자료
- 표기 규칙
  - **[확인]** = 출처(검색 결과 요약)에서 직접 확인된 사실. 번호는 말미 Sources 목록 참조.
  - **[벤더 주장]** = 벤더/파트너가 자체 발표한 수치. 독립 검증 없음.
  - **[추론]** = 조사자(본 보고서)의 해석·일반 지식. 제안서에 쓸 때는 "일반적 관행" 수준으로 표현 권장.

> **조사 방법 및 한계**
> - 웹 검색(요약형) 결과를 기반으로 작성. 세션의 네트워크 정책상 원문 페이지 직접 열람(WebFetch/curl)은 전부 차단(403)되어, 규제 원문(Annex 11, 21 CFR Part 11, WHO TRS)의 **조항별 축어 인용은 2차 출처 요약에 의존**함. 제안서에 조항을 인용할 경우 EudraLex Vol.4 / eCFR / WHO 원문으로 최종 확인 필요.
> - 검색 쿼터 소진으로 다음 항목은 추가 검색 미실시: ISA-95 기반 ERP/MES/LIMS 역할 경계, 무균·액상 공정 세부, Odoo Approvals/Documents 공식 문서, CAPA 종결기간 벤치마크. 해당 부분은 [추론]으로 표기.
> - Odoo 사례의 상당수는 파트너 마케팅 자료이며 수치는 자체 보고임. 제안서에는 "파트너 발표 기준" 꼬리표를 붙일 것.

---

## 0. 핵심 요약 (Executive Summary)

1. **규제 요구의 핵심은 '데이터 무결성(ALCOA+)'과 '컴퓨터화 시스템 밸리데이션(CSV)'**이다. WHO GMP(TRS 986 Annex 2), WHO 데이터 무결성 가이드라인(TRS 1033 Annex 4, 2021), EU GMP Annex 11/15, FDA 21 CFR Part 11, PIC/S PI 041-1(2021)은 모두 ERP가 (a) 변경 불가·시간기록·사용자 귀속 감사추적, (b) 기록에 영구 결합된 전자서명, (c) 역할기반 접근통제, (d) 위험기반 밸리데이션(IQ/OQ/PQ 또는 GAMP 5 2판·FDA CSA의 'specification & verification'), (e) 보존·백업·아카이빙을 갖출 것을 요구한다. **[확인]** [1][2][3][5][6][7][9][10]
2. **EU Annex 11 개정 초안(2025.7.7 공개, 의견수렴 2025.10.7 마감)**은 분량이 5→19쪽으로 확대되고, 감사추적을 "위험평가 후 고려"에서 "관련 수동 사용자 조작의 자동 기록(누가·무엇을·이전/이후 값·언제·왜)"으로 강화할 전망이다. 신규 도입 ERP는 개정안 기준으로 설계해야 한다. **[확인]** [12]
3. **Odoo는 GMP 공장용 ERP의 '뼈대'(MRP, 로트/유효기한/FEFO, 품질검사, 설비보전, PLM/ECO)를 표준으로 제공**하지만, **GMP 핵심 통제(필드단위 변조방지 감사추적, Part 11급 전자서명·재인증, eBMR, 편차/CAPA/변경관리 QMS, 밸리데이션 패키지)는 표준에 없다**. 이는 OCA 모듈(auditlog, quality_control_oca 등)·마켓플레이스 앱(eBMR, Audit Trail)·파트너 커스터마이징·외부 QMS/LIMS 연계 및 **별도의 CSV 프로젝트**로 보완해야 한다. Odoo 자체는 "GxP 인증"을 받은 제품이 아니며, 적합성은 구성·밸리데이션에 달려 있다. **[확인·추론]** [20][21][22][23][24][25][27][28][29][30][31]
4. **Odoo 제약 적용 사례**는 공식 고객사례(Brand Pharma/이집트, Viomix, Fraver NV/벨기에, Magis Pharma/벨기에, Laboratorio Fito Medic's/콜롬비아 추정, EFA Laboratorios/우루과이 등)와 파트너 사례(Abydos Pharma, Pharmalife Research/이탈리아, Ksolves Odoo 18 16모듈, Qualenica 등)가 있으나, **대부분 중소규모·유통/조제·보조식품에 집중**되어 있고, **대형 GMP 완제 공장에서 Part 11 수준으로 밸리데이션된 공개 사례는 확인되지 않았다**. **[확인]** [32]–[47]
5. **해외 벤치마크(개발국·국영/준국영)**: 베트남 Vinphaco(SAP S/4HANA Cloud, 1차 6개월 가동), Bidiphar(SAP 2014), 인도네시아 Kimia Farma/Bio Farma(국영, SAP·ERP 통합, 활용도 저조 문제), 말레이시아 Pharmaniaga(정부연계기업, S/4HANA 공장 가동), 방글라데시 Incepta(SAP 2021), 사우디 SPIMACO(SAP→Google Cloud) 등. **정량 성과는 대부분 미공개**이며, 성과 수치가 있는 사례는 MES/eBR 영역(Cipla 수기문서 75%↓, Ferring 배치기록 검토 60%↑속도·생산오류 25%↓, Valent 배치검토 20일→1일, Emerson RBE 4주→6시간)이다. **[확인/벤더 주장]** [50]–[66]
6. **KPI**: FDA 품질지표(로트합격률 LAR, 제품품질불만율 PQCR, OOS 무효화율 IOOSR, APR 적시율), 배치출하 사이클타임(베스트 3–5일 vs 업계평균 12–18일), RFT, 편차율(불량률의 4개월 선행지표, r=0.83), CAPA 종결기간, OEE(디지털 사이트 ~60%, 월드클래스 ~70%), 재고정확도·만기폐기, 문서오류율, 배치기록 검토시간 등. **[확인/벤더 주장]** [70]–[76]

---

## 1. GMP·규제 요구사항과 ERP 역량 요건

### 1.1 적용 규제 프레임워크 개요

| 규범 | 발행/상태 | ERP 관련 핵심 내용 | 출처 |
|---|---|---|---|
| **WHO GMP 주요원칙** – TRS 986 Annex 2 (2014) | WHO 인증제도(Certification Scheme)의 GMP 판정 기준, 제조허가 심사·실사 기준, 생산/QC/QA 교육자료 | 15장 문서화(배치제조기록 15.25–15.27, 배치포장기록 15.28–15.30: 제품명·배치번호·이론/실제수량·수율 reconciliation·일시·책임자, "복사 또는 컴퓨터 생성 가능"), 공정 전 구역·설비 적합성 확인 기록 | [1][2] **[확인]** |
| **WHO 데이터 무결성 가이드라인** – TRS 1033 Annex 4 (2021.10.10) | TRS 996 Annex 5(2016, GDRP)를 대체. 배경: GMP/GCP/GLP/GDP 전반에서 데이터무결성 지적 증가, 원인 중 하나로 "규제요건을 충족하지 못하거나 부적절하게 관리·밸리데이션된 컴퓨터화 시스템" 명시. 11장 '컴퓨터화 시스템' 포함(데이터 거버넌스, QRM, 아웃소싱, 데이터 검토·승인, 보안/접근통제/구성통제) | [3] **[확인]** |
| **WHO 밸리데이션 가이드라인** – TRS 1019 Annex 3 (2019.1) | Appendix 5 "컴퓨터화 시스템 밸리데이션" 포함(구 2006 Annex 4 App.5 계승: 시스템/기능 사양, 보안, 백업, HW/SW 검증) | [4] **[확인: 구조만]** |
| **EU GMP Part I Ch.1 제약품질시스템(PQS)** (2013.1.31 시행, ICH Q10 정합) | 계획변경의 통제·사전 영향평가(변경관리), QRM 기반 편차관리와 CAPA, 제품품질검토(PQR, 1.10), 경영검토, 경영진 책임 | [13] **[확인]** |
| **EU GMP Ch.4 문서화** (2011) | 4.11: 배치문서 보존 = **배치 유효기한 후 1년 또는 QP 인증 후 5년 중 긴 기간**; 4.12: 허가 뒷받침 중요문서(밸리데이션·안정성 원자료)는 허가 유효기간 내 보존; 문서는 승인·서명·일자, 각 배치 이력(유통 포함) 추적 가능 | [14][15] **[확인]** |
| **EU GMP Ch.8 불만·품질결함·회수** (전면개정, 약 6쪽) | 품질결함 포함, 조사·근본원인분석·CAPA, CAPA 효과성 모니터링, QP 인지 의무, 회수절차 효과성의 정기 평가(모의회수는 2차출처) | [16] **[확인]** |
| **EU GMP Annex 8** 원료·포장재 샘플링 | 샘플링의 청결 장비·통제 환경·문서화 방법 | [17] **[확인]** |
| **EU GMP Annex 11 컴퓨터화 시스템** (2011) | 아래 1.2 참조. **2025.7.7 개정 초안**(Annex 22 'AI', Ch.4 개정과 동시 공개, 의견 2025.10.7 마감). 5→19쪽, 비중: 보안·IAM > 적격성/밸리데이션 > 감사추적 | [5][12] **[확인]** |
| **EU GMP Annex 15 적격성평가·밸리데이션** | VMP(밸리데이션 마스터플랜) 필수, 프로토콜에 중요 시스템·속성·파라미터·허용기준 정의, IQ/OQ 결합 가능, 벤더 프로토콜은 사이트가 적합성 확인 후 승인·보충 | [6] **[확인]** |
| **FDA 21 CFR Part 11** 전자기록·전자서명 | 아래 1.3 참조 | [7][8] **[확인]** |
| **FDA CSA(Computer Software Assurance) 최종 가이던스** (2025.9.23/24, 2026.2.3 업데이트판 보고) | 생산·품질시스템 소프트웨어 대상, 위험기반(의도된 용도 식별→위험평가→보증활동 결정→객관적 증거), 2002 GPSV의 6장 대체. ※ 의료기기 QS 맥락이나 제약 CSV 실무에서도 참조 | [9] **[확인]** |
| **PIC/S PI 041-1** 데이터 관리·무결성 모범사례 (2021.6.1 채택, 7.1 발효) | 14장: 데이터 거버넌스, 일반원칙, 지면/컴퓨터화 시스템 등. 사찰관용이나 산업계 참고 | [10] **[확인]** |
| **PIC/S PI 011-3** 컴퓨터화 시스템 모범사례 (2007.9.25) | GxP 사찰관용 가이드, 현재 개정 중(Annex 11과 정합 목표). Health Canada는 Annex 11 채택 | [11] **[확인]** |
| **ISPE GAMP 5 (2nd ed. 2022)** | 산업 가이드(규제 아님). 구성형 상용제품=Category 4, 커스텀 코드(리포트·인터페이스·확장)=Category 5. 2판은 3Q 대신 'specification & verification' 프레임. 위험·복잡도에 비례한 검증 깊이 | [6][18] **[확인]** |
| **ALCOA+** | 기본 ALCOA(Attributable, Legible, Contemporaneous, Original, Accurate) + EMA 2010 반영문서에서 추가된 Complete, Consistent, Enduring, Available. TGA 자료에 ALCOA↔PIC/S Part I/II·Annex 11 조항 매핑표 존재 | [19] **[확인]** |

### 1.2 EU GMP Annex 11 주요 조항 (ERP 설계 기준)

> 조항 번호는 공식 Annex 11(2011) 기준: 1 위험관리, 2 인력, 3 공급자·서비스제공자, 4 밸리데이션, 5 데이터, 6 정확성 점검, 7 데이터 저장, 8 출력, **9 감사추적**, 10 변경·구성관리, 11 정기평가, **12 보안**, 13 사고관리, **14 전자서명**, **15 배치출하**, 16 사업연속성, 17 아카이빙. (일부 체크리스트는 번호를 달리 매김—원문 확인 필요) **[확인]** [5]

| 조항 | 요구 요지 | ERP 요건으로 번역 [추론 포함] |
|---|---|---|
| 9 감사추적 | (2011) 위험평가에 근거해 GMP 관련 변경·삭제의 기록 생성을 고려; 변경·삭제 사유 문서화; 감사추적은 이해 가능한 형태로 변환·정기 검토. **(2025 초안)** 관련 수동 조작 자동 기록(누가/무엇/이전·이후 값/언제/왜), 위험기반 문서화된 검토; 일반 사용자가 편집·비활성화 불가 | GMP 관련 모델(로트, 재고이동, 제조지시, 품질검사, BOM, 사양, 공급자 상태 등)에 **필드 단위 old/new 값·UTC 타임스탬프·사용자·사유(reason-for-change) 강제 입력**, 삭제 금지(soft-delete), 감사추적 리포트(사람이 읽을 수 있는 형태)와 **정기 검토 워크플로우**(배치 출하 전 감사추적 검토 체크) |
| 10 변경·구성관리 | 시스템(구성 포함) 변경은 정의된 절차에 따라 통제된 방식으로만 | 설정 변경(품질관리포인트, BOM, 라우팅, 유효기한 규칙, 권한)에 대한 **변경관리 티켓·승인·재검증 영향평가** 연계 |
| 11 정기평가 | 밸리데이션 상태·GMP 준수 유지 확인(기능범위, 편차·사고·업그레이드 이력) | 연 1회 정기검토 보고서, 업그레이드(Odoo 연간 메이저 릴리스)마다 영향평가·회귀테스트 |
| 12 보안 | 역할기반 접근, 사용자 생성·수정·비활성화 통제·기록 | RBAC, 개인 계정(공유계정 금지), 비밀번호 정책/MFA, 계정 라이프사이클 로그, 세션 타임아웃 |
| 14 전자서명 | 회사 내에서 수기서명과 동일한 효력, 기록에 영구 결합, 적용 일시 포함 | 서명 시 **재인증(ID+PW)**, 서명 의미(검토/승인/실행) 표기, 기록에 서명 메타데이터 봉인, 변경 시 서명 무효화 |
| 15 배치출하 | 컴퓨터화 시스템으로 인증·출하 기록 시 **QP(유자격자)만 인증 가능**, 인증자 명확 식별·기록, 전자서명 사용 | QA 출하 권한을 QP/QA 책임자 역할로 한정, 출하 상태 변경은 전자서명 필수, 출하 전 체크리스트(BMR 완결, IPC/QC 결과, 편차 종결, 감사추적 검토) |
| 4 밸리데이션 / 3 공급자 | 라이프사이클 밸리데이션, 공급자 평가 | URS→FS→CS→IQ/OQ/PQ, 추적성 매트릭스, **Odoo SA·구현파트너 공급자 평가**(오픈소스 특성 고려) |
| 7, 16, 17 | 저장·백업 검증, BCP, 아카이빙·판독성 | 백업/복원 테스트 기록, 보존기간(Ch.4: 유효기한+1년 또는 QP 인증+5년) 동안 조회 가능, 버전 업그레이드 후 과거 데이터 가독성 |

### 1.3 FDA 21 CFR Part 11 핵심 요건

- 적용: FDA 규정이 요구하는 기록을 전자적으로 생성·수정·보존·전송하는 시스템. 보존 대상·기간은 21 CFR 211(의약품 cGMP) 등 '선행 규정(predicate rule)'이 정한다. **[확인]** [7]
- **§11.10 폐쇄형 시스템 통제**(11개 항목): (a) 정확성·신뢰성·일관된 의도 성능 및 **무효/변조 기록 식별 능력**을 보장하는 밸리데이션; (b) 사람이 읽을 수 있는 형태와 전자형태의 **정확·완전한 복사본** 생성; (c) 보존기간 내 기록 보호·정확한 검색; (d) 접근 제한; (e) **보안·컴퓨터생성·시간기록 감사추적**(기록 보존기간만큼 보존, FDA 검토 가능); (f) 운영 점검; (g) 권한 점검; (h) 장치 점검; (i) 교육·훈련; (j) 서명 책임성 정책; (k) 시스템 문서 통제. **[확인: (a)(b)(e) 축어, 나머지는 2차 요약]** [7][8]
- **§11.50/11.70**: 서명 표시(서명자 이름, 일시, 의미), 서명과 기록의 결합(복사·위조 방지). **[일반 지식·추론]**
- **§11.100–11.300**: 전자서명은 1인 고유·재사용/재배정 불가(11.100(a)), 발급 전 신원 확인(11.100(b)), 수기서명과 법적 동등성에 대한 FDA 인증서 제출(11.100(c)); 비생체 서명은 ID+비밀번호 등 2요소, 비밀번호 주기 변경·분실 토큰 비활성화 등 통제. **[확인]** [7]
- 감사추적은 "사용자와 독립적(independent of the user)"이어야 하며 사용자가 끄거나 수정할 수 없어야 한다. **[확인(2차)]** [7]

### 1.4 ALCOA+ 정의와 ERP 통제 매핑 **[확인(정의)/추론(매핑)]** [19]

| 속성 | 의미 | ERP 통제 |
|---|---|---|
| Attributable(귀속) | 누가 언제 수행했는지 | 개인계정, 전자서명, 감사추적 |
| Legible(판독) | 영구 판독 가능 | 사람이 읽을 수 있는 출력/리포트, 아카이브 가독성 |
| Contemporaneous(동시성) | 수행 시점에 기록 | 서버 타임스탬프(사용자 수정 불가), 모바일/태블릿 현장 입력, 사후입력 시 사유 |
| Original(원본) | 최초 기록 또는 인증된 사본 | 원천 시스템 기록 유지, 전사 입력 최소화(LIMS/설비 연계) |
| Accurate(정확) | 오류 없음, 수정 이력 | 유효성 검사(허용범위, 단위, 필수값), 계산 자동화, 수정 시 old/new |
| Complete | 재분석·재시험 포함 모든 데이터 | 실패 검사·반복 검사 모두 보존(삭제 금지) |
| Consistent | 시간순 일관성 | 단일 시간원(NTP), 상태 전이 통제 |
| Enduring | 보존기간 내 지속 | 백업·아카이빙·버전 업그레이드 마이그레이션 검증 |
| Available | 요구 시 접근 가능 | 검색·리포트, 사찰 시 조회 권한 |

### 1.5 GMP 기능영역별 ERP 역량 요건 (요구사항 번역표)

| # | 기능영역 | 규제 근거 | 구체적 ERP 역량 요건 [확인 근거 + 추론] |
|---|---|---|---|
| 1 | **배치제조기록 BMR / 배치포장기록 BPR** | WHO TRS 986 §15.25–15.30; EU Ch.4; Part 11 | 마스터 포뮬러/포장지시서(승인본)에서 배치별 기록 자동 생성; 제품명·배치번호·이론/실제 수량·**수율 reconciliation**·일시·작업자·검증자; 공정 전 설비/구역 적합성(라인 클리어런스) 체크; 단계별 전자서명(수행/확인); 편차 발생 시 기록 연계; 완결성 검토 후 QA 승인; 인쇄본과 전자본 동일성 |
| 2 | **로트/배치 및 유효기한 추적(전·후방)** | EU Ch.4 "각 배치 이력(유통 포함)"; Ch.8 회수; WHO | 원료 로트→중간체→완제 배치→출고처까지 **계보(genealogy) 쌍방향 조회**(어떤 원료 로트가 어느 완제 배치에 들어갔고 어디로 출고되었나); 제조일/유효기한/재시험일; 분할·재포장·반품 추적; 회수 시 영향 범위 리포트(수 분 내) |
| 3 | **재료 상태관리(격리/시험중/출하/불합격)** | EU Ch.5·6, WHO; 상태라벨 관행(Approved/Quarantine/Quarantine-HOLD/Rejected/Conditional Release) | 입고 즉시 격리 상태 자동 부여, **QC/QA만 상태 변경 권한**(구매·IT·창고 불가), 격리 재고는 불출·출고 차단(시스템 강제), 조건부 출하, 상태 변경 이력·전자서명 |
| 4 | **QC 샘플링·시험·출하** | WHO §17, EU Ch.6, Annex 8 | 로트별 샘플링 지시·샘플 라벨, 시험항목(사양)·허용기준, 결과 입력(측정값/합부), OOS/OOT 플래그 및 조사 연계, CoA 생성; 공급자 CoA 의존 시 **최소 확인시험(identity test)** 및 연 1회 공급자 결과 확인 기록; LIMS 연계 시 결과 자동 수신 |
| 5 | **QA 배치 출하(certification)** | Annex 11 §15; EU Ch.1; Part 11 | QP/QA 책임자 전용 출하 권한; 출하 전 체크리스트(BMR 완결, IPC/QC 합격, 편차·OOS 종결, 변경 영향, 감사추적 검토); 전자서명; 출하 후 재고 상태 자동 전환 |
| 6 | **편차·CAPA·변경관리** | EU Ch.1(QRM 기반 편차, CAPA, 계획변경 사전 영향평가), Ch.8(CAPA 효과성) | 편차 등록→분류(critical/major/minor)→근본원인→CAPA→효과성 확인 워크플로우; 변경요청→영향평가(밸리데이션/등록/문서)→승인→실행→종결; 배치·로트·설비·문서와 상호 링크; 지표(종결기간, 재발률) |
| 7 | **공급자 적격성** | EU Ch.5(승인 공급자), Ch.7(외주) | 승인공급자 목록(물질×공급자×제조소), 상태(승인/조건부/보류), 감사 주기·만료 알림, 승인 안 된 공급자 발주 차단, 공급자 CoA·성적 이력 |
| 8 | **설비 교정·보전** | EU Ch.3(설비, 정해진 주기의 교정), WHO | 설비 마스터·교정 주기·다음 일자, 교정 만료 설비 사용 차단(작업지시 연계), 예방보전 일정, MTBF/MTTR, 작업 이력; 교정 성적서 첨부 |
| 9 | **감사추적** | Annex 11 §9(+2025 초안), Part 11 §11.10(e), PIC/S PI 041, WHO TRS 1033 | 위 1.2 참조. 변조방지·삭제불가·사용자 독립·old/new·사유·검토 워크플로우·보존기간 동일 |
| 10 | **전자서명** | Annex 11 §14, Part 11 Subpart C | 위 1.2/1.3 참조 |
| 11 | **CSV / CSA (IQ·OQ·PQ)** | Annex 11 §4, Annex 15, Part 11 §11.10(a), WHO TRS 1019 App.5, GAMP 5 | VMP·URS·위험평가(GAMP Cat.4 구성 + Cat.5 커스텀 모듈)·FS/CS·IQ(설치/버전/인프라)·OQ(기능)·PQ(실운영·절차 포함)·추적성 매트릭스·밸리데이션 보고서; 변경·업그레이드 시 재검증; 공급자 평가 |
| 12 | **문서관리(SOP)** | EU Ch.4, WHO §15 | 버전관리, 초안→검토→승인(전자서명)→발효→교육→폐기 라이프사이클, 유효본만 현장 노출, 정기 검토 주기, 통제된 인쇄 |
| 13 | **교육 기록** | EU Ch.2, Part 11 §11.10(i), WHO | 직무별 교육 커리큘럼(SOP 매트릭스), 이수 기록·평가, SOP 개정 시 재교육 자동 과제, 미이수자 공정 수행 차단[추론] |
| 14 | **회수 관리** | EU Ch.8, WHO | 로트 영향범위 즉시 산출(배치→출고처·수량), 회수 통지·회수량 reconciliation, 모의회수 기록, 당국 보고 |
| 15 | **시리얼라이제이션/트랙앤트레이스** | EU FMD(2019 시행), 미국 DSCSA(2025.5.27부터 제조사 EPCIS 전자 전송 요구—벤더 출처), GS1(GTIN+시리얼+로트+유효기한, Data Matrix; SSCC 집합포장) | ERP는 GTIN/로트/유효기한 마스터와 출고 단위 연계, 시리얼 생성·집합(aggregation)·EPCIS 교환은 보통 L3/L4 시리얼라이제이션 시스템이 담당하고 ERP와 인터페이스[확인+추론]. 수출 대상국(EU/미국/한국/중동 등) 규제별 요구 상이 |

출처: [1][2][3][5][7][13][14][15][16][17][48][49]

---

## 2. 제약 제조 공정 흐름과 ERP 매핑

### 2.1 표준 공정 흐름(고형제 OSD 기준) **[확인: 공정단계 / 추론: ERP 매핑]**

공정 단계(출처 [49]): 입고/창고 → 분출(dispensing)/배합 → 과립(습식: 고전단/유동층; 건식) → 건조 → 혼합 → 타정/캡슐충전 → 코팅 → 포장(계수기·블리스터·라벨·검사·시리얼라이제이션). 각 단계에서 **"무엇이 투입되고, 무엇이 일어났고, 무엇이 측정되고, 무엇이 다음으로 넘어가고, 잔량은 어디로 갔는가"**를 기록해 투입량 대비 산출·샘플·불량·손실을 reconciliation 하는 '재료 원장' 관점이 MES/배치기록의 핵심이다. [49]

| 단계 | GMP 요구 포인트 | ERP 기능 매핑 (Odoo 모듈 예시는 §3 참조) |
|---|---|---|
| ① 원료/API·포장재 입고 | 공급자 승인 확인, 로트번호 부여, 기존 상태표시 제거, 즉시 **격리** | 승인공급자 체크 발주, 입고 시 로트·제조일·유효기한·재시험일 필수, 격리 로케이션 자동 입고, 입고 검사 트리거 |
| ② 격리·QC 샘플링 | Annex 8 샘플링, 샘플 라벨, 사양별 시험 | 수입검사 품질관리포인트, 샘플량 차감, 시험 결과(측정/합부), CoA 첨부, OOS 플래그 |
| ③ 원료 출하(release) | QC/QA만 상태 변경, CoA 의존 시 identity 시험 | 상태 전환 전자서명, 격리→합격 로케이션 이동, 불합격→폐기/반품 |
| ④ 분출/칭량(dispensing) | 승인 포뮬러 기준, FEFO/재시험일, 이중 확인, 칭량 기록 | 제조지시(MO) 생성 시 BOM 확정, 로트 예약(FEFO), 칭량값·저울 ID·작업자/확인자 기록, 저울 연동[추론], 교정 만료 저울 차단 |
| ⑤ 과립/혼합/건조 | 공정 파라미터, 설비 로그, 라인 클리어런스 | 작업지시(WO) 단계별 체크리스트·파라미터 입력, 설비 상태(교정/보전) 검증, 중간체 로트 생성 |
| ⑥ 타정/캡슐/코팅 (액상: 조제·여과·충전 / 무균: Annex 1 환경관리) | IPC(중량·경도·두께 등), 수율 | 공정 중 품질검사(측정형, 허용범위 벗어나면 경고·알림), 수율·손실 reconciliation, 편차 등록 |
| ⑦ 포장(1차/2차) | 포장지시서, 라벨 reconciliation, 시리얼라이제이션 | 포장 MO/BPR, 라벨 발행·회수 수량 대조, 시리얼 시스템 인터페이스(GTIN/로트/유효기한 전달·집합 수신) |
| ⑧ 완제 QC | 사양 시험, 안정성 샘플 | 완제 검사 포인트, 보관샘플(retained sample) 차감, LIMS 연계 |
| ⑨ QA 배치 출하 | BMR 검토, 편차 종결, 감사추적 검토, QP 인증 | 출하 체크리스트·전자서명, 상태 "출하가능", CoA 발행 |
| ⑩ 완제 창고·유통 | FEFO 출고, 온도 조건, 유통기록(회수용) | 출고 FEFO 강제, 고객·배송 로트 기록, 유통 추적 리포트, 콜드체인 로그[추론] |
| ⑪ 사후: 불만·회수·PQR | Ch.8, Ch.1 PQR | 불만→조사→CAPA, 회수 시뮬레이션, 연간 PQR 데이터 추출(배치수·불합격·편차·OOS·변경·안정성) |

### 2.2 시스템 역할 경계 **[추론: ISA-95 일반 지식; 추가 검색 미실시]**

- **ERP(L4)**: 마스터데이터(품목·BOM·공급자·고객), 계획(MPS/MRP), 구매·입고·재고(로트/상태/FEFO)·원가·판매·출고, 설비보전, 품질 디스포지션(상태) '기록의 주인'.
- **MES/eBR(L3)**: 작업지시 실행, 단계별 전자배치기록, 설비·PLC 데이터 수집, 라인 클리어런스, 수율 reconciliation. 소규모 공장은 ERP의 작업지시+품질검사+커스텀 eBMR로 대체 가능하나 Part 11 통제 수준은 별도 설계 필요.
- **LIMS**: 샘플·시험법·결과·OOS·안정성. ERP는 결과(합부)와 CoA만 수신.
- **QMS(eQMS)**: 편차·CAPA·변경·문서·교육·감사. Odoo 표준에는 없음 → 커스텀 또는 외부 QMS 연계.
- **시리얼라이제이션(L3/L4 솔루션)**: 시리얼 생성·집합·EPCIS 교환; ERP와 마스터·출고 연계. [48]
- Cipla Patalganga 사례처럼 MES(PAS-X)가 SAP ERP·SCADA·BMS·IPQC·WMS와 통합되는 구조가 대형 사이트의 전형이다. **[확인]** [61]

---

## 3. 제약 산업에서의 Odoo

### 3.1 Odoo 표준 기능(제약 관련) **[확인/부분 확인]**

| 영역 | 표준 기능 | 비고·에디션 |
|---|---|---|
| **Inventory – 로트/시리얼·유효기한·FEFO** | 로트/시리얼 추적; 유효기한 기능 활성화 시 제품별 **Expiration/Best Before/Removal/Alert Date** 4개 날짜; Removal Date 기준 **FEFO 제거전략**(로케이션·제품카테고리 단위 설정); 유효기한 활성화가 FEFO 전제 | [20] **[확인]**. 알림 트리거 동작 세부는 버전별 문서 확인 필요. 만료 로트의 판매/출고 '강제 차단' 수준은 표준에서 제한적이며 서드파티 앱이 "엄격한 강제·만기 중심 제거·감사용 리포트"를 추가 판매 [20] [벤더 주장] |
| **Inventory – 추적성 리포트** | 재고이동 기반 추적성 리포트(참조·제품·일자·로트·From·To·수량); 로트/시리얼로 공급망 추적 → 회수 시 원천 식별 | [26] **[확인]**. 상·하류(upstream/downstream) 전용 리포트는 서드파티(TekGenio, SerpentCS Lot Recall Report, OCA shipment traceability report 12.0) [26] |
| **Manufacturing(MRP)** | BOM·라우팅·MO/WO, 부품 로트 소비 기록, 완제 로트 생성, 작업지시 태블릿 화면, 품질검사 연계 | 표준 MO 출력물은 "규제산업이 요구하는 구조화된 eBMR 형식과 불일치"(파트너 평가) [23] **[확인(2차)]** |
| **Quality**(Enterprise) | 품질관리포인트(입고/제조/출고/작업지시 트리거; 전건/랜덤/주기), 검사유형(지시·사진·**합부(Pass-Fail)**·**측정(Measure, 허용범위 이탈 시 경고 위저드)**·워크시트 등), 실패 시 **품질경보(Quality Alert)** 생성, 부분합격 경고 | [21] **[확인(2차)]**. 편차/CAPA/변경관리 전체 워크플로우는 아님[추론] |
| **Maintenance** | 예방·시정 보전, 요청 칸반, 보전 캘린더, **MTBF/MTTR/다음 고장 예측 자동 산출**, "metrology(계측/교정) 및 예방보전 일정 자동화" | [27] **[확인(마케팅 페이지)]**. 교정 만료 설비의 작업 차단은 커스텀[추론]. 에디션은 출처가 상충(Cybrosys는 Enterprise 전용으로 분류) [28] |
| **PLM**(Enterprise) | ECO(설계변경지시) 단계별 승인(승인자·순서·필수·결정일), BOM/라우팅 버전관리(ECO 내 버전, 특정 일자 활성 버전 추적, 롤백), 다단계 승인 후 '변경 적용' | [29] **[확인(2차)]** → 마스터 포뮬러/BOM 변경관리 기반으로 활용 가능[추론] |
| **Sign**(Enterprise) | **단순 전자서명(SES)**; eIDAS·미국 ESIGN/UETA 하 유효 주장; 증거: 이메일/SMS 인증, itsme® 강력 신원확인(옵션), 타임스탬프 접근 로그, 암호학적 변조 감지. Odoo 문서 자체에 "법적 효력 없음·법률 자문 권고" 고지. **21 CFR Part 11 언급 없음** | [22] **[확인]** |
| **Accounting – 데이터 불변성** | 저널별 "Secure Posted Entries with Hash": SHA-256 체인 해시(이름·일자·저널·회사·차변·대변·계정·거래처), 활성화 후 비활성화 불가, 불변성 검증 리포트 | [24] **[확인]** — **회계 전표 한정**. 재고/제조/품질 모델에는 해당 없음 |
| **Chatter 필드 추적** | tracking=True 필드의 변경을 chatter에 메시지로 기록. Odoo R&D는 `mail.tracking.value`를 HTML 저장으로 이전(DB 증가 억제), 테이블은 선택 모듈로 분리, 필드 그룹 보안 미지원 | [24] **[확인(PR)]**. "경량 메시지 로그, 필드단위 변조방지 감사가 아님"(벤더 평가) [25] |
| Documents / Approvals(Enterprise) | 문서 폴더·태그·워크플로우 액션, 승인 요청 유형 | **[추론/일반지식]**(검색 미실시). SOP 라이프사이클(버전·발효·교육연계)은 커스텀 필요 |
| 에디션 | Quality, Sign, Helpdesk, Studio 등 Enterprise 전용; Maintenance·PLM도 Enterprise로 분류(출처 일부 구버전) | [28] **[확인(2차)]** — 공식 비교표로 재확인 권고 |

### 3.2 GMP 대비 알려진 Gap **[확인(2차)+추론]**

| Gap | 내용 | 근거 |
|---|---|---|
| **G1. 감사추적** | 표준은 chatter 기반 변경 메시지(일부 필드)·회계 해시만 제공. "Odoo Community는 기본적으로 견고한 필드단위 변경 감사 부재", "규제 환경은 더 강한 감사추적 리포팅 필요". 사유(reason-for-change) 강제, 삭제 금지, 사용자 독립성, 검토 워크플로우 없음 | [23][24][25] |
| **G2. 전자서명(Part 11/Annex 11 §14)** | Odoo Sign은 문서 서명용 SES; 레코드(검사·출하·BMR 단계)에 대한 **재인증 기반 서명·서명 의미·영구 결합**은 표준 없음 → 커스텀(ECOSIRE eBMR은 서명 의미 Reviewed/Approved/Rejected·서명 시 재인증 구현 주장) | [22][30] |
| **G3. eBMR/BPR** | MO 출력 ≠ BMR. 단계·파라미터·IPC·라인클리어런스·수율 reconciliation·단계 서명 포함 템플릿은 파트너 빌드 | [23][30] |
| **G4. QMS(편차/CAPA/변경관리/불만/회수)** | Quality Alert는 단순 이슈 티켓 수준; 분류·근본원인·CAPA 효과성·변경 영향평가 워크플로우 미제공[추론]. 파트너 모듈(echoBitz "QC & CAPA" 등) 또는 외부 eQMS | [21][31] |
| **G5. 밸리데이션 패키지 부재** | Odoo SA는 GxP 밸리데이션 문서(IQ/OQ 스크립트, 요구사항 추적)를 제공하지 않음(검색상 미확인). 파트너가 CSV를 수행하며 "전체 Annex 11 준수는 공식 CSV와 지속 변경관리 문서화가 필요한 파트너 주도 프로세스". Odoo는 "인증(certified)된 것이 아니며 GxP 정합 구성을 지원" | [23][31][45] |
| **G6. 연간 메이저 버전·SaaS 자동 업데이트** | Odoo Online(SaaS)은 공급자가 업데이트 주기를 통제 → 재검증 통제 어려움. On-premise/Odoo.sh 권장[추론] | [추론] |
| **G7. 교육기록·SOP 문서관리** | eLearning/Documents로 일부 구성 가능하나 SOP-직무 매트릭스·개정 시 재교육 강제는 커스텀[추론] | [추론] |
| **G8. 시리얼라이제이션** | 표준 미제공; 외부 L3/L4 연계 | [48] |
| **G9. 상·하류 계보 리포트, 만기 강제 차단** | 기본 추적성 리포트 수준; 전용 리포트·강제는 서드파티 | [20][26] |
| **G10. 커스텀 = GAMP Cat.5** | 위 Gap 보완 커스텀 모듈은 모두 Category 5 → 가장 높은 테스트 엄격도 요구 → 밸리데이션 비용 증가 | [18] |

### 3.3 Gap 보완 모듈·버티컬 **[확인(목록)/벤더 주장(기능)]**

**OCA(Odoo Community Association) 모듈**
- `auditlog`(server-tools): 모델별 C/R/U/D·커스텀 메서드 로깅 규칙, 세션/일자/모델/HTTP 요청별 그룹핑. **Beta** 표기, 180일 초과 로그 삭제 크론(기본 비활성), 사용자 범위 제한 불가. 14.0–17.0 확인. → GxP 변조방지·검토 워크플로우는 미검증 [32]
- `tracking_manager`(server-tools, 18.0): o2m/m2m·html·properties 필드까지 추적 확장 [24]
- `quality_control_oca`, `quality_control_stock_oca`, `quality_control_team_oca`(manufacture, AGPL-3; 13.0–18.0): 정성/정량(범위) 시험 프레임워크, 재고이동 완료 시 검사 생성, 피킹·로트 단축 [33]
- `product_expiry_simple`(10–14; 구버전), `stock_production_lot_traceability_shipment_report`(12.0) [20][26]
- `mail_tracking` 등

**Odoo Apps 마켓플레이스/파트너 제품**
- echoBitz `eb_pharma_manufacturing`(17/18, 약 $99): 배치 추적·QC&CAPA·GMP·유효기한 — 기능 상세 미확인 [31]
- ECOSIRE **Odoo Pharma eBMR**(17/18/19, 일회 라이선스 $799~, build-to-order): 로트별 BoM 연계 기록, 단계별 공정, IPC, 변경 시 사용자·old/new·UTC·사유 로깅, append-only 로그, 서명 의미·재인증, WHO/EU Annex 11/Part 11 "대비"; CSV 지원 문서 제공 주장 [30]
- ECOSIRE Audit Trail Log($249~), Inom Audit Trail(17/18/19; 모델별 CRUD 규칙·old/new·전용 관리자 그룹), `se_fields_in_chatter`(16–19) [25]
- Cerevantix Lots/Serial Expiry(17–19: 만기 대시보드·폐기 위저드·FEFO 강제), TekGenio Lot Traceability(17: 상·하류), SerpentCS Lot Recall Report(19) [20][26]
- 파트너 버티컬(기능 주장, 고객명 미공개 다수): SerpentCS "Odoo Pharma ERP for GMP", PySquad(eBMR), HashStudioz("Part 11/EU GMP validated Odoo" 주장), Botspot(eBMR 템플릿), TechUltra("Odoo is not certified, supports GxP-aligned configuration"), Zolute(UAE), Nuva(케냐), Lahore Analytica(파키스탄), Ventor.tech, Ksolves, SDLC Corp, Upstackers [23][45][46]

### 3.4 Odoo 제약 적용 사례(세계) **[출처 신뢰도 표시]**

| 기업 | 국가 | 업종/규모 | 내용·성과 | 출처·신뢰도 |
|---|---|---|---|---|
| **Brand for Pharmaceutical Industries(Brand Pharma)** | 이집트 | 제약그룹(제조 포함) | Excel/이메일→Odoo. 2018 V10 Community 5명(판매·구매·회계·재고)→2019 V13 Enterprise, 2020.1 사용자 급증. 파트너 Semak BI. 모듈: CRM·Sales·Purchase·Inventory·**Manufacturing·Quality**·Accounting·HR·Helpdesk 등 | odoo.com 공식 블로그 [34] **[확인]** |
| **Viomix Pharmaceutical Industries** | (미기재) | 원료·의약품 제조·유통 | 공식 고객 페이지(상세 없음) | odoo.com [35] **[확인]** |
| **Fraver NV** | 벨기에 | 개별맞춤 조제·원료·완제(약국 공급), 직원 30+ | 지면·스프레드시트·이메일→Odoo, 실시간 경영보고 | odoo.com [36] **[확인]** |
| **Magis Pharma Group** (Qualenica 포함) | 벨기에 | 환자 맞춤 치료제 | 그룹 전 법인 회계; Hadron 사례: Qualenica 규제 생산(콜드스토리지·배치추적), 도구 7→1 통합, **2주 내 가동**, 4개사 40+ 사용자 | odoo.com 리스트 [37] **[확인]** / Hadron [38] **[파트너 주장]** |
| **Laboratorio Fito Medic's S.A.S** | 콜롬비아(추정, S.A.S) | 제약·화장품 | 파트너 PETI; CRM·구매·**제조·품질**·WMS; 프랜차이즈 운영효율 +20%, 생산성 +18% | odoo.com [39] **[확인(수치는 고객/파트너 보고)]** |
| **EFA Laboratorios** | 우루과이 | 제약 전문의약품 제조·판매 | 파트너 Nexit | odoo.com [40] **[확인]** |
| **Phytopharma SA** | (유럽) | 건강제품 제조 | Excel→구매·판매·재고·제조·회계; 의약품 코드·예약재고 커스텀; OBS Solutions | odoo-bs.com [41] **[파트너]** |
| **Pharma More**, **Pharmaco (NZ/AU)**, **Esencias GIR** | 다수 | 제약 | odoo.com 고객 리스트(상세 미확인) | [37] |
| **Biocosmetic** | 파키스탄 | 화장품 GMP 제조 | Odoo Enterprise, 구매·생산에 품질검사 통합; RASCO | odoo.com [42] **[확인]**(화장품) |
| **Aquatech Skin Care** / **Laboratoire Cofane** | 캐나다 / 프랑스 | 화장품 GMP(ISO 22716) 제조·수탁 | Captivea; 성과 미기재 | [42] **[파트너]** |
| **SASMAR Healthcare** | 벨기에 | 헬스케어 제조 | HR 100% 페이퍼리스, 시장출시 시간 40%↓ | erpresearch 디렉토리 [43] **[2차/미검증]** |
| **Abydos Pharma** | 유럽 CMO | 수탁제조 | Manufacturing·Inventory·Quality·Documents; **배치출하 40% 단축, 수기문서 오류 85%↓** | SDLC Corp [44] **[파트너 주장]** |
| **Pharmalife Research** | 이탈리아 | 제약·뉴트라슈티컬 | 생산처리량 +30%, QA 지연 감소 | SDLC Corp [44] **[파트너 주장]** |
| **Ksolves – 제약 제조·유통사(익명)** | 캐나다 추정(캐나다 세무 언급) | 제약 제조+유통 | **Odoo 18, 16개 커스텀 모듈**; QuickBooks 동기화로 월 대사 40–50h→5–8h, 급여 80%↓, **작업지시 단위 QC로 재작업 비용 60%↓**, 1년 ROI 77%, 회수 6.8개월($618k/yr 효익 vs $350k) | Ksolves [46] **[파트너 주장]** |
| **Upstackers – 익명 제약 제조사 2건** | 미기재 | 정제·시럽·주사제 | 배치·유효기한 추적, 리콜, 조달효율 +40%, 생산사이클 +20%, QC 표준화로 불합격률 25%↓ | [47] **[파트너 주장]** |
| **Oman 연구소 그룹** | 오만 | 검사실 | 노후 LIMS 교체 + ERP를 Odoo+LIMS 통합 플랫폼으로 4개월 | Dynapps [40] **[파트너]** |
| 유통: **IDC Pharma**(17개 판매거점 단일 인스턴스), **Sudabelt Medical**(나이지리아), 도매업체(일 500–1,000→7,000–10,000 주문) | 다수 | 제약 유통 | | [43][45] **[파트너 주장]** |
| 영양보조: **Genius Nutrition** | 루마니아 추정 | 보조식품 | e-invoicing·Shopify 연동 | VentorTech [43] |

**해석 [추론]**: (i) 공개된 Odoo 제약 사례는 중소 제조·조제·유통에 집중되며, **대규모 GMP 완제 공장에서 Part 11/Annex 11 수준의 CSV를 거쳐 가동한 공개 사례는 확인되지 않음**(Odoo 포럼 "Validation Odoo for Pharmaceutical Industry" 스레드도 명명된 사례 없음 [23]). (ii) 성과 수치는 조달·회계·문서화 효율 중심이며 규제 KPI(감사 지적, 배치출하 시간)는 Abydos(파트너 주장) 외 드묾. (iii) 따라서 제안서에는 "Odoo = 검증된 ERP 코어 + GMP 레이어(커스텀/파트너 모듈) + CSV 프로젝트"로 포지셔닝하고, 레퍼런스는 Brand Pharma·Fito Medic's·Fraver·Magis 등 공식 고객사례를 중심으로 제시하는 것이 안전하다.

---

## 4. 해외 벤치마킹: 제약 제조사의 ERP/디지털화 (개발국·국영·아시아/아프리카 중심)

### 4.1 사례 요약표

| 기업 | 국가·성격 | 솔루션 | 내용 | 성과/교훈 | 출처·신뢰도 |
|---|---|---|---|---|---|
| **Vinphaco** | 베트남, GMP-WHO 제약사 | SAP S/4HANA Cloud Private Edition (FPT IS) | 2012년 ERP 교체. 1차: 2024.4 착수→**6개월여 만에 가동(2024.11.4 전환)**, MM·PP·QM·FICO·SD. 2차: PM(설비보전)+Vietcombank e-banking 연동. 3차(2026 Q1 예정): WM·QR코드 | 단계적 모듈 롤아웃(코어→보전→창고) 모델; 정량 성과 미공개 | FPT [50] **[벤더]** |
| **Bidiphar** | 베트남 | SAP ERP(2014) → DMS·BI·e-learning(2017) → AI 수요예측 | "국내 제약사 최초 SAP" 주장 | 10년 단위 단계적 디지털화 로드맵 | vietnam.vn [51] **[언론/자사]** |
| **Pharmedic** | 베트남 | SAP S/4HANA Cloud (FPT) | 대규모 경영 디지털화 | 상세 미확인 | FPT [52] **[벤더]** |
| **Traphaco / Imexpharm** | 베트남 | ITG 3S ERP / (미기재) | Traphaco CNC는 전통의약 공장 최초 GMP-WHO; Imexpharm 4개 클러스터 중 3개 EU-GMP | "어디서 시작하고 투자 전 효과를 어떻게 입증하나"가 업계 화두 | [53] **[벤더/행사]** |
| **Kimia Farma** | 인도네시아 **국영(BUMN)** | SAP(2015/2016~, 자회사 KFTD·약국 단위 포함) | 재무·생산·HR·물류; 약국 사업단위는 9개 모듈 중 4개만 사용; "복잡해 최적 활용 못함"; 성공요인=사용자 만족·시스템 품질 | **국영기업 교훈**: 모듈 활용도 저조·교육 부족 → 활용도 KPI와 교육 체계 필수 | 학술/학위논문 [54] **[학술(약함)]** |
| **Bio Farma Group**(Kimia Farma·Indofarma·INUKI 모회사) | 인도네시아 국영 | 그룹 ERP 통합, API Factory, People-Process-Technology 프레임 | 디지털 전환 저해요인 탐색 연구(2025) | 그룹사 간 ERP 통합·API 연계가 과제 | ResearchGate [55] **[학술]** |
| **Pharmaniaga** | 말레이시아, 정부연계(GLC) 최대 상장 제약사 | SAP S/4HANA(ABeam) 제조공장 가동; Navision·Macalo 대체 | 2015부터 벤더 검토; 생산오더·**품질관리**·납품·제품원가 효율 목표 | 정량 성과 미공개; 공장 전체 단일 플랫폼 전략 | insidesap.asia/ABeam [56] **[언론/벤더]** |
| **Incepta Pharmaceuticals** | 방글라데시 | SAP ERP(2021, "방글라데시 최초") | Zensar: 5개월 내 운영 효율화 시작 | 짧은 초기 가동 주장(벤더) | Wikipedia/Zensar [57] **[2차/벤더]** |
| **Beximco Pharmaceuticals** | 방글라데시 | ERP(벤더 미상) | 실패원인·성공예측 연구: 레거시 연계용 추가 SW 비용 등 지연 요인 | 레거시 인터페이스 비용 과소추정 주의 | ResearchGate [58] **[학술]** |
| **SPIMACO** | 사우디 | SAP → Google Cloud 이전(2023.4) | 11개 핵심 애플리케이션 이전·통합, 프로비저닝 3–6개월→3–4일, 9개 신시장 확장 계획 | 인프라 민첩성 | Google Cloud [59] **[벤더]** |
| **Pharma Pharmaceutical Industries** | 사우디 | Epicor ERP | 15명 사용자, 10개월; 지면 기반→ERP; "잘못되거나 만기된 원료 사용 위험" 해소가 동기 | 소규모·장기간(10개월/15명) → 변화관리 비용 | Arab News/IntelligentCIO [60] **[언론]** |
| **Med City Pharma(Axantia)**, **KSPICO/Mezzan** | 사우디, 쿠웨이트 | SAP S/4HANA(AWS 그린필드 2022 FPS02) | 세무·보건 규제 대응 | 정량 성과 없음 | [60] **[벤더]** |
| **PLIVA** | 크로아티아(전환경제) | SAP + BPR(2004 ITI 논문) | ERP와 BPR 동시 수행 | 2차 요약: 재고 ≥30% 감소·납기 단축(원문 미확인); "ERP 완전 성공 30%, 실패율 50%↑" 인용 | Bosilj Vukšić & Spremić [62] **[학술/2차]** |
| **Cipla – Patalganga** | 인도 | Werum PAS-X MES(eBR) + SAP ERP·SCADA·BMS·IPQC·WMS 통합 | **수기 문서화 약 75%↓**, 자동 예외처리로 분출→출고 시간 단축 | ERP 단독이 아닌 MES 통합이 배치기록 효과의 원천 | Körber [61] **[벤더]** |
| **Dr. Reddy's – Visakhapatnam** | 인도 | PAS-X MES | Hyderabad 템플릿 재사용으로 **5개월 구축**(2013) | 템플릿·표준화로 다공장 전개 가속 | [61] **[벤더/언론]** |
| **Ferring – Kiel** | 독일 | Körber eBR(Pharma 4.0 페이퍼리스) | 8개 생산영역 중 육안검사부터 시작; 레시피 블록 70–80% 재사용; **생산오류 ~25%↓, 지면 오류 ~100%↓, 배치기록 검토 60% 가속, 생산 중 문서화 시간 25–40%↓** | 파일럿 영역→확산, 모듈화 | Körber [63] **[벤더]** |
| **Valent BioSciences** | 미국 | eBR(Ecolab 발표) | **배치 검토 20일→1일**, 데이터 입력 60%↓(1,800 배치), 30개 공정 페이퍼리스 | | [64] **[벤더]** |
| **글로벌 바이오파마 공장(익명)** | — | Review-by-Exception(Emerson) | 배치출하 3–4주→**6시간**, 배치 50–60% 자동출하, 예외 10분 내 식별·통보, 첫 달 ROI 200% | RBE 전제조건: 전자기록·데이터 통합 | ISA InTech/Emerson [65] **[벤더]** |
| **Chi Pharmaceuticals** | 나이지리아 | (WHO GMP 인증 투자 비용-효익; ERP 아님) | 재정·기술역량 제약이 품질 투자 저해 | 개발국 GMP 투자 정당화 논리 참고 | BMC HSR [66] **[학술]** |
| **에티오피아·EAC 제약사** | 아프리카 | GMP 준수도 연구 | HVAC 요구 67.1% 충족; 탄자니아 EAC GMP 준수 32.9%(전년 50%); 숙련인력·외화 부족 | 개발국 공장 디지털화 시 인력·외화(라이선스) 제약 고려 | PMC/PLOS [66] **[학술]** |

### 4.2 교훈(Lessons Learned) 종합

**[확인]**
- **ERP 후 과제(제약사 연구, IJQRM 2023)**: 가장 큰 사후 문제 = "비효율적 트러블슈팅 체계", "가동 후 교육 부족", "잘못 입력된 데이터 식별 어려움". [67]
- **이집트 50개사(2012)·요르단 5개 제약사 171명(2019)·알제리 SAP 제약사**: 최고경영진 지원, 전사 커뮤니케이션, 조직문화, **교육·훈련**이 성과에 유의한 영향; 사용자 교육이 결정적. [67]
- **Alvarez & Marsal(제약 ERP)**: SI(구현사)의 **실제 규제산업 경험 검증 누락**이 흔한 실패 원인; 중도 SI 교체는 비용·법적 리스크; GxP 영역은 밸리데이션 증거를 문서화해야 감사 통과. [68]
- **GxP ERP 가이드**: 밸리데이션 계획은 **벤더 선정 전**에 시작(밸리데이션 접근이 벤더 적합성을 좌우); URS→FRS→CS→IQ→OQ→PQ를 GMP 기능 가동 전에 완료. [18][68]
- **ERP 일반**: ERP 구현의 60–90%가 승인 단계 ROI 미달(학술 인용); BPR 동시 수행 필요(PLIVA). [62]
- **Kimia Farma**: 국영기업에서 모듈 활용도 저조·복잡성 → 활용도(adoption) 관리 필요. [54]
- **McKinsey QC 디지털화(2018)**: QC랩 리드타임 60–70%↓ 잠재, 수기 문서 최대 80%↓, 조사 업무 최대 90%↓, "일부 사례" 편차 65%↑ 감소·종결 90% 가속; 단, 선투자 규모와 소규모 랩의 투자 정당화가 장애. [69]

**[추론: 국영 GMP 공장 제안에의 시사점]**
1. 코어(재무·구매·재고·생산·품질 디스포지션) → 보전·창고 → eBMR/QMS 고도화의 **단계적 로드맵**(Vinphaco·Bidiphar형).
2. **CSV를 프로젝트 WBS에 1급 산출물로 포함**(VMP, URS, 위험평가, IQ/OQ/PQ, 추적성 매트릭스), 구현사 GxP 경력 증빙 요구.
3. **교육·사후지원(하이퍼케어·헬프데스크·활용도 KPI)** 예산 명시.
4. 성과 KPI를 조달/회계 효율만이 아니라 **규제 KPI(§5)**로 설정.
5. 오픈소스(Odoo) 선택 시 라이선스 외화 부담 완화 장점(개발국 맥락) vs. 밸리데이션·커스텀(Cat.5) 비용 증가를 균형 있게 제시.

---

## 5. 제약 ERP/GMP 디지털화 성과 KPI

| 구분 | KPI | 정의 | 벤치마크/근거 | 출처·신뢰도 |
|---|---|---|---|---|
| **규제 품질지표(FDA Quality Metrics)** | 로트합격률 **LAR** | 기간 내 합격 로트 ÷ 착수 로트(또는 1 − 사양 관련 불합격 비율) | 제조공정 성능 지표 | FDA 가이던스(안) [70] **[확인]** |
| | 제품품질불만율 **PQCR** | 불만 건수 ÷ 유통 투여단위(출처별 분모 상이: 출하 로트 수) | 고객/환자 피드백 지표 | [70] |
| | OOS 무효화율 **IOOSR** | 측정과정 이상으로 무효화된 OOS ÷ 전체 출하·장기안정성 OOS | 실험실 운영 지표 | [70] |
| | APR/PQR 적시율 | 기한 내 완료된 연간제품검토 비율 | | [70] |
| **생산·출하** | 배치출하 사이클타임 | 제조 완료→QA 출하 승인 | **베스트 3–5일(표준 제품) vs 업계평균 12–18일+(중간 복잡도)**; 지연 원인=분산 데이터·수기 QA/QC; 무균주사제 14→6일 사례 | IntuitionLabs/iFactory [71] **[벤더 벤치마크]** |
| | 배치기록 검토 시간 | BMR 검토 소요 | Valent 20일→1일; Ferring 60% 가속; RBE 4주→6시간 | [63][64][65] **[벤더]** |
| | **RFT(Right First Time)** | 편차/부적합 없이 제조된 로트 비율 | | SimplerQMS [72] **[확인(정의)]** |
| | OEE | 가동률×성능×품질 | 디지털 사이트 ~60%, 월드클래스 ~70%; 디지털화로 OEE 약 2배 가능 주장 | [71] **[벤더]** |
| | 수율·손실 reconciliation 편차 | 이론 대비 실제 수율 | WHO BPR 요구 | [1] |
| **품질시스템** | 편차 발생률(배치당) | | **편차율이 불량률의 약 4개월 선행지표(14개 사이트, r=0.83, McKinsey/IPA)** | [73] **[확인(2차)]** |
| | 편차/CAPA 종결기간, 기한 내 종결률, 재발률 | | 디지털화로 종결 90% 가속 "일부 사례"(McKinsey) | [69] **[컨설팅]**; 수치 벤치마크 추가 검색 미실시 |
| | 감사추적 검토 완료율 | 출하 전 검토 비율 | Annex 11 §9 정기 검토 요구 | [5] |
| | 문서 오류율 | 배치기록 기재 오류 | Ferring 지면 오류 ~100%↓, Abydos 85%↓(파트너) | [63][44] |
| | 외부 실사 지적 수(critical/major) | 당국·고객 감사 | EAC 지역 GMP 준수율 32.9% 등 지역 맥락 | [66] |
| **데이터 무결성** | 사후 입력(back-dated) 비율, 공유계정 0건, 권한 검토 주기 준수 | | PIC/S PI 041·WHO TRS 1033 | [3][10] **[추론(지표화)]** |
| **공급망·재고** | 재고 정확도(사이클카운트), 재고회전율, 만기 폐기액, 결품률 | | 벤더 가이드는 범주만 제시, 정량 벤치마크 미확보; PLIVA 재고 ≥30%↓(2차) | VAI/DHL [74] **[벤더]**, [62] |
| | 공급자 OTIF·승인공급자 외 구매 0건 | | EU Ch.5 | [17] |
| **설비** | 교정 적시율, 예방보전 준수율, MTBF/MTTR | | Odoo Maintenance 산출 가능 | [27] |
| **회수** | 모의회수 소요시간(영향 로트·출고처 산출), 회수 reconciliation율 | | EU Ch.8 효과성 평가 | [16] |
| **교육** | SOP 교육 이수율, 개정 후 재교육 적시율 | | EU Ch.2, Part 11 §11.10(i) | [7] |
| **프로젝트/도입** | 모듈 활용도(기능 사용률), 사용자 만족, 가동 후 티켓 종결시간, ROI/회수기간 | | Kimia Farma(9개 중 4개 모듈 사용); Ksolves ROI 77%·6.8개월(파트너) | [54][46] |
| **QC 랩** | 랩 리드타임, 시험당 비용 | 리드타임 60–70%↓ 잠재, 비용 25–45%↓ | McKinsey [69] **[컨설팅]** |

**제안서용 목표치 예시 [추론]** (현장 베이스라인 측정 후 조정): 배치출하 사이클타임 −30~50%(1년), 배치기록 기재오류 −80%, 편차 종결 평균 ≤30일·기한 내 종결률 ≥90%, 재고정확도 ≥99%, 만기 폐기액 −30%, FEFO 준수 100%, 감사추적 검토 완료율 100%(출하 전), 공유계정 0, 모듈 활용도 ≥80%.

---

## 6. 제안서 작성 시 권고 포지셔닝 **[추론]**

1. **아키텍처**: Odoo(Enterprise, on-premise 또는 Odoo.sh) = ERP 코어(재무·구매·재고 로트/FEFO·MRP·품질검사·보전·PLM) + **GMP 레이어**(필드단위 감사추적·사유 강제, 레코드 전자서명·재인증, 재료상태 강제, eBMR/BPR, 편차/CAPA/변경관리, SOP·교육) + 인터페이스(LIMS, 시리얼라이제이션, 저울/라벨). 대형 무균·다제형 공장이면 MES 도입 여지를 로드맵에 남김.
2. **CSV**: GAMP 5 Cat.4(표준 구성)+Cat.5(커스텀) 혼합 전략, VMP·URS·위험평가·IQ/OQ/PQ·추적성 매트릭스를 산출물로 명시; Annex 11 2025 개정안 기준 설계; 연간 버전 업그레이드 재검증 절차(SaaS 자동업데이트 배제).
3. **레퍼런스**: Odoo 공식 고객사례(Brand Pharma, Fito Medic's, Fraver, Magis 등) + 파트너 사례(Abydos, Ksolves 등: "파트너 발표 기준" 표기) + 타 벤더 벤치마크(Vinphaco·Pharmaniaga·Kimia Farma의 단계적 접근·활용도 교훈; Cipla·Ferring·Valent의 eBR 효과).
4. **KPI 체계**: §5 표 기반, 베이스라인 측정(현황 진단 단계) → 가동 6/12개월 목표.
5. **리스크 고지**: Odoo는 GxP 인증 제품이 아님; 적합성은 구성·커스텀·밸리데이션·운영 SOP에 의존; 공개된 대형 GMP 공장 Part 11급 Odoo 사례 부재.

---

## Sources (검색 결과 요약을 통해 확인한 URL)

**규제·표준**
1. WHO TRS 986 Annex 2 (GMP main principles): https://www.who.int/publications/m/item/trs986-annex2
2. WHO GMP training module (TRS 986 documentation 15.25–15.30, 2차): https://moh.gov.sy/public/images/R2Gq8hRLj5hOL4e9rv.pdf ; EU GMP Ch.4 사본: https://translation-centre.am/pdf/Translat/EU_Other/GMP_Rules/GMP_Rules_Chapter_4_en.pdf
3. WHO TRS 1033 Annex 4 (Data integrity, 2021): https://www.who.int/publications/m/item/annex-4-trs-1033 ; PDF 미러: https://www.gmp-navigator.com/files/guidemgr/trs1033-annex4-guideline-on-data-integrity.pdf ; ECA 요약: https://gmp-compliance.org/gmp-news/new-who-guidance-on-data-integrity
4. WHO TRS 1019 Annex 3 (Validation, App.5 computerized systems): https://www.who.int/publications/m/item/trs1019-annex3
5. EU GMP Annex 11 (2011) 원문: https://health.ec.europa.eu/system/files/2016-11/annex11_01-2011_en_0.pdf ; 요약/체크리스트: https://www.scilife.io/hubfs/Scilife_EU%20Annex%2011_Mapping%20Checklist.pdf ; https://docs.seal.run/regulatory-standards/eu-volume-4-annex-11 ; https://sgsystemsglobal.com/?p=15579
6. Annex 15 / IQ-OQ-PQ / GAMP 5: https://www.tga.gov.au/sites/default/files/presentation-pics-guide-gmp-pe009-13-key-changes-annex-15-qualification-and-validation.pdf ; https://casrai.org/guides/computerised-system-validation-eu-gmp-annex-11-annex-15 ; https://www.scilife.io/blog/gxp-computer-system-validation-guide ; https://intuitionlabs.ai/articles/gamp-5-guidelines-system-validation ; https://www.moh.gov.bw/Publications/drug_regulation/Qualification%20and%20Validation%20EMEA%202001.pdf
7. 21 CFR Part 11 해설: https://www.law.cornell.edu/cfr/text/21/11.10 ; https://simplerqms.com/21-cfr-part-11-audit-trail ; https://intuitionlabs.ai/articles/21-cfr-part-11-electronic-records-signatures-overview ; https://pharmtech.com/view/21-cfr-11-overview-final-document-and-its-new-scope-ludwig-huber ; https://www.mddionline.com/business/21-cfr-part-11-how-and-why-to-comply
8. 21 CFR 11.10 원문(GPO): https://www.gpo.gov/fdsys/pkg/CFR-2012-title21-vol1/pdf/CFR-2012-title21-vol1-sec11-10.pdf ; https://www.govinfo.gov/content/pkg/CFR-2018-title21-vol1/pdf/CFR-2018-title21-vol1-sec11-200.pdf
9. FDA CSA 최종 가이던스(2025.9): https://www.nsf.org/life-science-regulatory-news/fda-final-guidance-computer-software-assurance-csa ; https://www.hoganlovells.com/en/publications/fda-finalizes-computer-software-assurance-guidance-for-production-and-quality-system-software ; https://public-inspection.federalregister.gov/2025-18468.pdf
10. PIC/S PI 041-1 (2021): https://gmp-compliance.org/gmp-news/pic-s-publishes-final-document-on-data-integrity ; https://www.dcatvci.org/?p=8897
11. PIC/S PI 011-3 (2007, 개정 중): https://picscheme.org/docview/3444 ; https://picscheme.org/en/pia-pic-s-training-expert-circles-training-computerised-syst ; Health Canada GUI-0050: https://www.canada.ca/en/health-canada/services/drugs-health-products/compliance-enforcement/good-manufacturing-practices/guidance-documents/annex-11-guide-computerized-systems-gui-0050.html
12. Annex 11 개정 초안(2025.7.7): https://gmp-compliance.org/gmp-news/drafts-of-eu-gmp-guideline-annex-11-annex-22-and-chapter-4-released-for-comment ; https://www.nsf.org/life-science-news/revised-eu-pic-s-gmp-on-documentation-computer-systems-and-ai ; https://www.scilife.io/blog/eu-gmp-annex-11-explained-a-practical-guide-to-csv ; https://www.gmp-compliance.org/gmp-news/content-review-of-the-audit-trail-review
13. EU GMP Ch.1 PQS: https://gmp-compliance.org/gmp-news/finally-published-new-eu-gmp-chapter-1-with-comprehensive-changes ; https://www.pharmout.net/eu-guidelines-for-gmp-chapter-1-quality-management-revised-to-align-with-ich-q10/
14. EU GMP Ch.4 (2011) 원문 사본: https://www.gmp-compliance.org/files/guidemgr/chapter4_01-2011_en.pdf
15. EU GMP Ch.4 해설: https://www.gmp-compliance.org/gmp-news/new-eu-gmp-guide-chapter-4-on-documentation ; https://www.gmp-compliance.org/gmp-news/batch-documentation-who-needs-to-review
16. EU GMP Ch.8 불만·회수: https://www.gmp-compliance.org/gmp-news/complaints-and-recalls-new-eu-gmp-chapter-8-published ; https://gmp-compliance.org/guidelines/gmp-guideline/eu-gmp-chapter-8-complaints-quality-defects-and-product-recall
17. 재료 상태·샘플링·공급자: https://www.gmp-compliance.org/guidelines/gmp-guideline/eu-gmp-annex-8-sampling-of-starting-and-packaging-materials ; https://gmpsop.com/?p=7506 ; https://gmpsop.com/?p=302 ; https://sgsystemsglobal.com/glossary/component-release/ ; https://pharmuni.com/2026/03/13/sampling-plan-in-pharma-gmp-fda-ema-expectations-and-qc-workflow/
18. GAMP 5 카테고리·ERP 밸리데이션 가이드(벤더): https://ecosire.com/blog/gxp-validation-erp-rfp-guide ; https://ecosire.com/blog/erp-pharma-implementation-guide
19. ALCOA+: https://intuitionlabs.ai/articles/alcoa-plus-gxp-data-integrity ; https://redica.com/data-integrity-and-alcoa/ ; TGA 매핑표: https://tga.gov.au/sites/default/files/2022-12/raci-seminar-computerised-systems-establishing-and-maintaining-data-integrity.pdf

**Odoo 기능·Gap·모듈**
20. Odoo 유효기한/FEFO: https://github.com/odoo/documentation/pull/7530/files ; https://github.com/odoo/documentation/pull/15692/files ; https://odoo-users.readthedocs.io/en/stable/inventory/routes/strategies/removal.html ; Cerevantix 앱: https://apps.odoo.com/apps/modules/18.0/cerevantix_lots_serial_expiry_date_app ; product_expiry_simple: https://pypi.org/project/odoo10-addon-product-expiry-simple/10.0.1.0.0.99.dev11
21. Odoo Quality(2차): https://www.cybrosys.com/blog/how-does-odoo-help-to-test-the-quality-of-a-product ; https://store.softhealer.com/blog/odoo-store-9/inventory-quality-control-v16-9514 ; https://store.softhealer.com/blog/odoo-store-9/inventory-quality-control-v15-9487
22. Odoo Sign 법적 효력: https://www.odoo.com/documentation/20.0/applications/productivity/sign/validity.html ; https://odoo.com/app/sign-features ; https://www.odoo.com/documentation/13.0/applications/finance/sign.html
23. Odoo 제약 Gap(파트너/포럼): https://www.odoo.com/forum/help-1/validation-odoo-for-pharmaceutical-industry-160352 ; https://www.techvoot.com/blog/is-odoo-erp-right-choice-for-pharma-companies ; https://www.botspotinfoware.com/blog/industry-based-blogs-3/blogindustry-based-blogs-3odoo-erp-for-healthcare-and-pharma-16 ; https://www.techultrasolutions.com/industries/pharma ; https://silentinfotech.com/blog/erp-5/how-odoo-erp-helps-pharma-companies-470 ; https://intuitionlabs.ai/articles/open-source-mes-pharma-gmp-compliance
24. Odoo 데이터 불변성(회계 해시)·chatter 추적: https://www.odoo.com/documentation/17.0/nl/applications/finance/accounting/reporting/data_inalterability.html ; https://mergebot.odoo.com/odoo/enterprise/pull/99500 ; OCA tracking_manager: https://odoo-modules.trobz.com/oca/server-tools/18.0/tracking_manager.html
25. 감사추적 서드파티: https://apps.odoo.com/apps/modules/18.0/inom_audit_trail ; https://ecosire.com/apps/odoo/audit-trail-log ; https://apps.odoo.com/apps/modules/18.0/se_fields_in_chatter
26. Odoo 추적성·리콜: https://cybrosys.com/odoo/odoo-books/community-edition-v16/inventory/product-traceability ; https://www.cybrosys.com/blog/how-to-tracking-components-and-finished-products-with-lot-serial-numbers-in-odoo-17-manufacturing ; https://apps.odoo.com/apps/modules/17.0/tg_lot_traceability_report ; https://apps.odoo.com/apps/modules/19.0/scs_lot_recall_report ; https://pypi.org/project/odoo12-addon-stock-production-lot-traceability-shipment-report
27. Odoo Maintenance: https://www.odoo.com/app/maintenance
28. Odoo 에디션 비교(2차): https://www.cybrosys.com/odoo/compare-odoo-community-vs-enterprise/
29. Odoo PLM/ECO: https://www.cybrosys.com/odoo/odoo-books/v18/plm/changes-menu/ ; https://www.infintor.com/?p=21338 ; https://www.bistasolutions.com/resources/blogs/odoo-plm/ ; https://apps.odoo.com/apps/modules/18.0/engineering_change_order
30. ECOSIRE Odoo Pharma eBMR: https://ecosire.com/apps/odoo/odoo-pharma-ebmr-batch-record ; https://ecosire.com/industries/pharmaceuticals ; https://ecosire.com/blog/pharma-manufacturing-erp
31. echoBitz pharma 앱: https://apps.odoo.com/apps/modules/18.0/eb_pharma_manufacturing ; 파트너 버티컬: https://www.serpentcs.com/industries/odoo-erp-for-pharmaceutical-manufacturing ; https://pysquad.com/solutions/odoo-pharma-manufacturing-software ; https://www.hashstudioz.com/odoo-for-healthcare-and-pharma-solutions.html
32. OCA auditlog: https://apps.odoo.com/apps/modules/14.0/auditlog ; https://pypi.org/project/odoo-addon-auditlog/17.0.1.0.0.6
33. OCA quality_control: https://apps.odoo.com/apps/modules/18.0/quality_control_oca ; https://apps.odoo.com/apps/modules/15.0/quality_control_stock_oca ; https://apps.openerp.com/apps/modules/14.0/quality_control_team_oca

**Odoo 제약 사례**
34. Brand for Pharmaceutical Industries(이집트, 공식): https://www.odoo.com/blog/customer-reviews-6/brand-for-pharmaceutical-industries-ropes-its-businesses-under-odoo-s-umbrella-907
35. Viomix(공식): https://www.odoo.com/customers/viomix-for-pharmaceutical-industry-5633315
36. Fraver NV(공식): https://www.odoo.com/customers/fraver-nv-2249093
37. Magis Pharma 등 공식 고객 리스트: https://www.odoo.com/customers/industry/17/country/20/page/2 ; Pharma More: https://www.odoo.com/customers/pharma-more-15681327 ; Pharmaco: https://www.odoo.com/customers/country/165/page/3 ; 나이지리아 제약 고객: https://www.odoo.com/customers/industry/health-social-welfare-pharmaceutical-17/country/nigeria-157
38. Hadron – Qualenica/Magis Pharma: https://www.hadronforbusiness.com/manufacturing ; FSA NV(Hadron): https://www.odoo.com/customers/fsa-nv-833826
39. Laboratorio Fito Medic's(공식): https://www.odoo.com/customers/laboratorio-fito-medic-s-s-a-s-3854684
40. EFA Laboratorios(Nexit): https://www.odoo.com/accounting-firms/nexit-1269723 ; Dynapps(오만 랩 그룹): https://www.dynapps.es/es/cases?page=2
41. Phytopharma SA(OBS): https://odoo-bs.com/customer-database/4309/details
42. Biocosmetic(파키스탄, 공식): https://odoo.com/customers/biocosmetic-pk-15212986 ; Aquatech Skin Care: https://captivea.com/customers/aquatech-skin-care-332929 ; Laboratoire Cofane: https://www.captivea.com/customers/eurl-laboratoire-cofane-1094592
43. erpresearch Odoo 고객(SASMAR 등): https://www.erpresearch.com/erp-customers/odoo ; VentorTech: https://ventor.tech/industries/healthcare-pharma/ ; Graxi: https://graxitechs.com/case_studies/odoo-erp-for-healthcare-pharma/
44. SDLC Corp(Abydos Pharma, Pharmalife Research): https://sdlccorp.com/post/odoo-for-pharmaceuticals/
45. 파트너 일반(Zolute UAE, Nuva Kenya, Lahore Analytica, Ksolves blog): https://www.zolute.consulting/case-studies/odoo-erp-for-pharmaceutical-manufacturing-in-dubai-ensure-full-traceability-compliance-production-quality-with-confidence ; https://nuva.co.ke/odoo-for-pharmaceutical-manufacturing-in-kenya/ ; https://www.lahoreanalytica.com/blog/our-blog-1/odoo-for-the-pharmaceutical-industry-streamlining-operations-and-ensuring-compliance-7 ; https://www.ksolves.com/blog/odoo/why-odoo-erp-is-the-best-choice-for-the-pharmaceutical-industry
46. Ksolves Odoo 18 제약 제조·유통(16모듈): https://www.ksolves.com/case-studies/odoo/odoo-18-erp-implementation-pharmaceutical-manufacturing-distribution ; https://www.ksolves.com/case-studies/odoo/custom-odoo-solution-for-pharmaceutical-operations ; https://www.ksolves.com/case-studies/odoo/odoo-erp-pharma-trading-management
47. Upstackers: https://upstackers.com/pharma-case-study ; https://upstackers.com/medicine-case-study
48. 시리얼라이제이션: https://intuitionlabs.ai/articles/pharmaceutical-serialization-software-regulations ; https://datexcorp.com/pharma-serialization-aggregation-and-dscsa/ ; https://ifactoryapp.com/article/pharma-serialization-track-trace-dscsa ; https://www.vai.net/resources/blog/how-erp-systems-ensure-dscsa-compliance-and-pharmaceutical-traceability
49. OSD 공정 흐름: https://seal.run/blueprints/oral-solid-dose ; https://ispe.org/training/course/oral-solid-dosage-manufacturing-process ; https://www.chinacanaan.com/blog/pharmaceutical-equipment-blog/osd-manufacturing-process-steps-equipment-guide/ ; https://www.emerson.com/en/corporate/industries/life-sciences/packaging/oral-solid-dose

**해외 벤치마킹**
50. Vinphaco–FPT SAP S/4HANA: https://fpt-is.com/en/vinphaco-and-fpt-successfully-go-live-with-a-comprehensive-digital-enterprise-management-platform/ ; https://fpt-is.com/en/vinphaco-completes-phase-2-go-live-of-sap-s-4hana-accelerating-digital-transformation-journey ; https://fpt-is.com/en/customers/vinphaco-elevates-data-driven-management-with-sap-s-4hana-implemented-by-fpt-is/
51. Bidiphar: https://www.vietnam.vn/en/bidiphar-chuyen-doi-so-de-nang-tam-nang-luc-quan-tri-doanh-nghiep-duoc
52. Pharmedic–FPT: https://fpt.com/en/news/fpt-news/pharmedic-so-hoa-quan-tri-quy-mo-lon-tren-nen-tang-sap-s4hana-cloud-do-fpt-trien-khai
53. Traphaco(ITG), Imexpharm(FPT 행사): https://itgtechnology.vn/en/industries/pharmaceutical/ ; https://fpt-is.com/en/applying-ai-in-operations-and-manufacturing-to-accelerate-competition-in-the-pharmaceutical-sector/
54. Kimia Farma SAP 연구: https://journal.ugm.ac.id/jisph/article/view/34179 ; https://acopen.umsida.ac.id/index.php/acopen/article/view/8062 ; https://openlibrary.telkomuniversity.ac.id/pustaka/197695/analysis-of-erp-successful-factor-implementation-using-utaut-modelstudy-case-pt-kimia-farma-persero-.html ; https://repository.telkomuniversity.ac.id/pustaka/files/155272/abstract/analisis-faktor-faktor-keberhasilan-implementasi-enterprise-resource-planning-erp-menggunakan-model-kesuksesan-sistem-informasi-studi-kasus-pt-kimia-farma-trading-and-distribution-bandung-.pdf ; https://www.itworks.id/22660/top-digital-awards-2019-transformasi-digital-jadikan-pt-kimia-farma-persero-tbk-jadi-pemain-healthcare-terkemuka.html
55. Bio Farma Group 디지털 전환 연구: https://www.researchgate.net/publication/394048265_Exploratory_Analysis_and_Identification_of_Factors_Challenging_Digital_Transformation_in_Bio_Farma_Group ; https://www.biofarma.co.id/en/our-strategy
56. Pharmaniaga S/4HANA: https://insidesap.asia/malaysian-pharma-giant-implements-s4hana-manufacturing-plants/ ; https://www.abeam.com/my/en/case_study/Pharmaniaga2/
57. Incepta SAP: https://en.wikipedia.org/wiki/Incepta_Pharmaceuticals ; https://www.slideshare.net/Zensar/incepta-streamlining-business-with-sap-erp-to-serve-a-dynamic-market
58. Beximco ERP 연구: https://www.researchgate.net/publication/303100797_An_Assessment_to_Identify_Causes_of_ERP_Implementation_Failure_and_to_Predict_Its_Success_A_Case_Study_on_Beximco_Pharmaceuticals_Limited
59. SPIMACO–Google Cloud: https://cloud.google.com/customers/spimaco ; https://www.googlecloudpresscorner.com/2023-04-17-SPIMACO-Taps-Google-Cloud-for-Latest-Digital-Transformation-in-Pharmaceuticals-Sector-in-The-Kingdom-of-Saudi-Arabia
60. 중동 사례: https://www.intelligentcio.com/me/2020/05/07/pharma-group-accelerates-growth-plans-with-epicor-erp/ ; https://www.arabnews.com/node/1693021 ; https://cloudwrxs.com/cs-mezzan/ ; https://www.savictech.com/case-studies/ ; https://www.accely.com/us-en/news/kuwaits-pharma-leader-accelerates-growth-with-sap-s-4hana/
61. Cipla/Dr. Reddy's PAS-X MES: https://www.koerber.com/en/insights-and-events/case-studies/cipla-pas-x-mes-digitization ; https://www.automation.com/en-us/articles/2013-2/dr-reddys-ready-to-run-pas-x-mes
62. PLIVA SAP+BPR: https://www.researchgate.net/publication/4112695_Case_study_of_PLIVA_Pharmaceuticals_Inc_-_aligning_ERP_system_implementation_with_business_process_change ; https://hrcak.srce.hr/44699 ; https://www.researchgate.net/publication/220066116_ERP_System_Implementation_and_Business_Process_Change_Case_Study_of_a_Pharmaceutical_Company
63. Ferring–Körber eBR: https://www.koerber.com/en/insights-and-events/case-studies/ferring-electronic-batch-recording ; https://www.koerber-pharma.com/en/blog/how-ferring-pharmaceuticals-stepped-into-the-future-of-pharmaceutical-manufacturing-with-koerber ; https://service.koerber-pharma.com/hubfs/K%C3%B6rber%20Pharma/Consulting/.pdf/Koerber_con_0026_Case_Study_Ferring_CS_EN.pdf
64. Valent BioSciences eBR(Ecolab): https://law-resources.law.com/free/w_ecol81/ ; https://www.techtarget.com/hub/asset/1781272454_503
65. Review-by-Exception(Emerson/ISA): https://isa.org/intech-home/2020/september-october/features/digital-transformation-of-batch-review-improves-op ; https://emersonexchange365.com/industries/lifesciences/b/life-sciences-blog/posts/digitalizing-and-automating-review-by-exception ; EY eBR: https://www.ey.com/en_us/insights/life-sciences/electronic-batch-records-improve-pharma-manufacturing ; Capgemini eBR PoV: https://www.capgemini.com/wp-content/uploads/2022/09/PoV_eBR-1.pdf
66. 아프리카 GMP 연구: https://link.springer.com/article/10.1186/s12913-017-2610-8 ; https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11646143/ ; https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11407403/ ; https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12484000/ ; https://pubmed.ncbi.nlm.nih.gov/41551240/ ; West Africa ERP(벤더): https://www.ebizframe.com/case-study.php/transforming-pharmaceutical-manufacturing-in-west-africa-with-intelligent-erp
67. ERP 사후 과제 연구: https://emerald.com/insight/content/doi/10.1108/IJQRM-10-2020-0333 ; https://eprints.hud.ac.uk/id/eprint/19205/1/ICIL_Conference_Paper_croatia_2012.pdf ; https://www.zuj.edu.jo/wp-content/uploads/2019/12/abstract-82.pdf ; https://www.em-consulte.com/es/article/1724191/identification-of-utilization-deficiencies-post-sa ; https://www.researchgate.net/publication/362078039_Post-implementation_challenges_of_ERP_system_in_pharmaceutical_companies
68. Alvarez & Marsal 제약 ERP 전략: https://www.alvarezandmarsal.com/sites/default/files/2024-12/Getting%20It%20Right%20Top%20Strategies%20for%20Successful%20ERP%20Implementation%20in%20the%20Highly%20Regulated%20Pharma%20Industry%20-%20Alvarez%20and%20Marsal.pdf ; SAP 밸리데이션: https://www.pharmafocusasia.com/strategy/sap-erp-implementation-strategy-validation-activity ; https://intuitionlabs.ai/articles/sap-s4hana-pharma-gxp-implementation-validation
69. McKinsey QC 디지털화: https://www.mckinsey.de/industries/life-sciences/our-insights/digitization-automation-and-online-testing-the-future-of-pharma-quality-control

**KPI**
70. FDA Quality Metrics: https://fda.gov/media/101522/download ; https://pharmtech.com/view/fda-revises-quality-metrics-guidance-comment ; https://www.fdanews.com/articles/172948-fda-outlines-10-data-points-for-drugmakers-to-calculate-quality-metrics ; https://gmp-compliance.org/gmp-news/fda-publishes-quality-metrics-guidance
71. 제약 KPI 벤치마크(벤더): https://intuitionlabs.ai/articles/pharma-kpi-benchmarks-2026 ; https://ifactoryapp.com/article/pharma-batch-cycle-time-end-to-end ; https://www.griddynamics.com/blog/kpis-for-pharmaceutical-manufacturing-operations
72. 품질 KPI 정의: https://simplerqms.com/quality-kpis-pharmaceutical ; https://leandatapoint.com/blog/pharma-kpis-for-pharmaceutical-success
73. 편차–불량 선행지표(McKinsey via IPA India): https://www.ipa-india.org/wp-content/uploads/2023/03/p201812.pdf ; https://www.ipa-india.org/wp-content/uploads/2020/02/presentation2020-15.pdf
74. 재고/공급망 KPI(벤더): https://www.vai.net/resources/blog/benchmarks-for-erp-success-metrics-for-measuring-roi-in-the-pharmaceutical-industry ; https://lot.dhl.com/the-kpis-driving-pharmaceutical-supply-chains/
75. RFT 문화(Tulip 웨비나): https://tulip.co/webinars/the-right-first-time-factory-building-a-culture-of-proactive-quality-in-pharma/
76. 배치기록 효율(ECA): https://www.gmp-compliance.org/files/eca/userFiles/seminarpdf/ECA_Eff_Batch_Rec_2015.pdf
