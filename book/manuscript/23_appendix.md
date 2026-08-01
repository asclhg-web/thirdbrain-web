# 부록

## 부록 A. 용어집

본문에 등장하는 핵심 용어를 가나다·알파벳 순이 아닌 주제 묶음으로 정리했다. 각 용어의 본문 상세 논의는 해당 장을 참조하라.

### A-1. 지식·AI 계층

- **온톨로지(ontology)** — "개념화의 명시적 명세"(Gruber, 1993). 기업이 다루는 객체(품목·고객·설비 등)와 그들 사이의 관계, 속성을 형식적으로 정의한 어휘 체계다. 이 책에서는 코드체계가 곧 온톨로지의 어휘이며, 서드브레인의 골격이다(6장).
- **지식그래프(knowledge graph)** — 객체를 노드로, 관계를 엣지로, 사실을 속성으로 표현한 그래프 형태의 지식 저장 구조(Hogan et al., 2021). 온톨로지가 스키마라면 지식그래프는 그 스키마를 따르는 데이터의 총체다.
- **RAG(Retrieval-Augmented Generation, 검색증강생성)** — LLM이 답변을 생성하기 전에 외부 저장소에서 관련 문서를 검색해 근거로 삼게 하는 기법. 환각을 줄이고 사내 지식 기반 응답을 가능하게 한다(14장).
- **GraphRAG** — 벡터 검색 대신 지식그래프를 검색 기반으로 쓰는 RAG(Edge et al., 2024). 다중 홉 질의와 전역 요약에 강하며, "이 불량의 원인은 어느 자재·설비와 연결되는가" 같은 관계 질문에 답할 수 있다(6장).
- **LLM(Large Language Model, 대형 언어 모델)** — 대규모 텍스트로 학습되어 자연어의 이해·생성·추론을 수행하는 AI 모델. 서드브레인에서는 질의 해석, 암묵지의 구조화 추출, 근거 기반 서술을 담당한다.
- **sLLM(소형 언어 모델)** — 온프레미스 서버나 공동 클라우드 GPU에서 자체 호스팅 가능한 경량 LLM. 민감 데이터를 외부 API로 내보내지 않는 데이터 주권 확보 수단이다(15장).
- **벡터 임베딩(vector embedding)** — 텍스트·이미지의 의미를 고차원 수치 벡터로 변환한 표현. 의미 유사도 검색(벡터 RAG)의 기반이나, 관계 추론에는 그래프의 보완이 필요하다.
- **Neo4j** — 대표적인 속성 그래프(property graph) 데이터베이스. 이 책의 아키텍처에서 온톨로지 지식그래프와 GraphRAG의 저장·질의 계층을 맡는 지식 부스터다(15장).
- **Cypher** — Neo4j의 그래프 질의 언어. `(불량)-[:발생공정]->(공정)` 같은 패턴 매칭으로 그래프 경로를 탐색한다. SQL이 표의 언어라면 Cypher는 관계의 언어다.
- **디지털 트윈(digital twin)** — 물리 대상, 가상 모델, 양방향 데이터 연결의 3요소로 구성되는 가상 복제(Grieves, 2014; Glaessgen & Stargel, 2012). 데이터 흐름이 양방향 자동일 때만 트윈이며, 수동이면 디지털 모델·섀도로 구분한다(Kritzinger et al., 2018). ISO 23247이 제조 분야 표준 프레임워크다(6장).
- **AX(AI Transformation, AI 전환)** — 판단의 지능화. 기록의 디지털화인 DX의 다음 단계로, AI가 예측·시뮬레이션·처방으로 경영 판단을 지원하는 전환이다(3장).
- **DX(Digital Transformation, 디지털 전환)** — 업무와 기록의 디지털화. ERP·스마트공장 구축이 대표적이며, 이 책의 관점에서 DX는 AX의 전제 조건이다.
- **Human-in-the-Loop(AI-Human-in-the-Loop)** — AI의 판단·제안에 사람의 승인과 피드백을 개입시키고, 그 피드백을 다시 학습 데이터로 쓰는 협업 루프(5장). 판단의 최종 권한을 사람에게 두는 안전장치다.
- **PTGDA(Progressive Tacit Graph Discovery Algorithm)** — 파편화된 데이터에서 숨은 노드와 관계를 단계적으로 복구·재생하여 경영 사각지대의 암묵 프로세스를 가시화하는 접근(정인호, i7 제안, 2026)(6장).
- **환류 루프** — 데이터는 위로(현장→ETL→지식그래프), 판단은 아래로(AI 판단→작업지시·Odoo 액션) 흐르는 서드브레인의 순환 구조. 이 책의 핵심 아키텍처 원리다.
- **경영 사각지대** — 시스템에 기록되지 않고 담당자의 암묵지와 파편화된 파일로만 운영되는 업무 영역. AX의 첫 과제는 이 사각지대의 가시화다(3장).

### A-2. 지식경영·데이터 이론

- **암묵지(tacit knowledge)** — 언어로 형식화되지 않은 채 개인의 경험과 몸에 체화된 지식(Polanyi, 1966). "우리는 말할 수 있는 것보다 더 많이 안다." 베테랑의 노하우가 대표적이다.
- **형식지(explicit knowledge)** — 문서·데이터·코드로 표현되어 공유·저장 가능한 지식. ERP의 기록은 기업 형식지의 총체다.
- **SECI 모델** — 암묵지와 형식지의 상호변환 나선: 사회화(공동체험)→표출화(암묵지의 형식화)→연결화(형식지의 결합)→내면화(체득)(Nonaka, 1994; Nonaka & Takeuchi, 1995). LLM은 표출화를 상시화하는 도구다(2장).
- **DIKW 계층** — 데이터→정보→지식→지혜의 계층(Ackoff, 1989; Zeleny, 1987). 기존 ERP는 데이터·정보까지, AI ERP는 지식·지혜의 계층을 지향한다. 단, 데이터에서 지혜가 자동 증류된다는 가정은 비판의 대상이다(Frické, 2009).
- **ETL(Extract-Transform-Load)** — 원천 시스템에서 데이터를 추출·변환·적재하는 파이프라인. 이 책에서는 Odoo에서 지식그래프로 데이터를 올리는 통로이며 n8n이 수행한다(5장).
- **KGI(Key Goal Indicator)** — 최종 목표의 달성 여부를 재는 지표(예: 영업이익). KPI 트리의 뿌리 노드다(21장).
- **KPI(Key Performance Indicator)** — 목표에 이르는 과정의 성과를 재는 핵심 지표. KGI로부터 인과 트리로 분해되어야 관리 가능하다(21장).
- **선행지표/후행지표** — 결과를 예고하는 지표(파이프라인, Cp/Cpk)와 결과를 확인하는 지표(매출, 불량률). 성과관리 성숙도는 선행지표 비중으로 잰다(21장).
- **GQM(Goal-Question-Metric)** — 목표에서 질문을, 질문에서 측정 지표를 도출하는 목표지향 측정 방법론(Basili et al., 1994). 이 책의 KGI→KPI→데이터 역방향 설계의 원형이다(4장).

### A-3. 생산·공급망 시스템

- **MRP(Material Requirements Planning, 자재소요계획)** — BOM과 재고·주문 정보로 자재의 소요량과 발주 시점을 계산하는 기법(Orlicky, 1975). ERP 계보의 출발점이다(1장).
- **MRP II(Manufacturing Resource Planning, 제조자원계획)** — MRP에 생산능력·재무를 통합해 제조 자원 전체를 계획하는 체계(Wight, 1981).
- **ERP(Enterprise Resource Planning, 전사적 자원관리)** — 재무·인사·생산·판매 등 전사 업무를 단일 데이터베이스로 통합한 정보시스템. 용어는 1990년경 Gartner에서 비롯되었다(Jacobs & Weston, 2007).
- **APS(Advanced Planning & Scheduling, 고급 계획·일정)** — 유한한 생산능력 제약을 고려해 실행 가능한 생산계획·일정을 수립하는 시스템. 무한능력을 가정하는 MRP의 한계를 보완한다. 이 책에서는 frePPLe가 담당한다.
- **MES(Manufacturing Execution System, 제조실행시스템)** — 작업지시, 실적 수집, 추적성 등 공장 현장의 실행을 관리하는 시스템. Odoo에서는 제조 관리의 작업현장(Shop Floor) 기능이 이 역할을 한다(12장).
- **PLM(Product Lifecycle Management, 제품수명주기관리)** — 제품의 설계 변경(ECO)·도면·BOM 버전을 수명주기 전체에서 관리하는 체계(12장).
- **WMS(Warehouse Management System, 창고관리시스템)** — 입고·적치·피킹·출고 등 창고 운영을 최적화하는 시스템. Odoo 재고 관리는 경량 WMS 기능을 포함한다(11장).
- **SCM(Supply Chain Management, 공급망관리)** — 공급업체에서 고객까지 자재·정보·자금의 흐름을 통합 관리하는 경영 방식.
- **S&OP(Sales & Operations Planning, 판매·운영계획)** — 수요(판매) 계획과 공급(생산) 계획을 월 단위로 정렬하는 전사 계획 프로세스(12장).
- **BOM(Bill of Materials, 자재명세서)** — 제품 한 단위를 만드는 데 필요한 부품·자재의 구조화된 목록. 제품-부품 관계의 온톨로지다(12장).
- **MPS(Master Production Schedule, 기준생산계획)** — 완제품 수준에서 무엇을 언제 얼마나 만들 것인가를 정한 계획. MRP 전개의 입력이 된다.
- **리드타임(lead time)** — 발주·착수에서 입고·완성까지 걸리는 시간. 구매·제조·배송 리드타임으로 나뉘며, 안전재고 산정의 핵심 변수다(17장).
- **안전재고(safety stock)** — 수요와 리드타임의 변동에 대비해 보유하는 완충 재고. 서비스 수준 목표와 변동성의 함수로 동적으로 산정해야 한다(17장).
- **재주문점(reorder point)** — 재고가 이 수준에 도달하면 발주를 내는 기준점. 리드타임 수요 + 안전재고로 계산된다.
- **ABC-XYZ 분석** — 품목을 금액 기여도(A/B/C)와 수요 변동성(X/Y/Z)의 2축으로 분류해 재고 정책을 차등화하는 기법(17장).

### A-4. 품질·설비 지표

- **OEE(Overall Equipment Effectiveness, 설비종합효율)** — 가동률×성능×품질의 곱으로 설비 활용의 종합 수준을 재는 지표. 세계적 수준의 기준으로 85%가 흔히 인용된다(18장).
- **Cp/Cpk(공정능력지수)** — 공정의 산포가 규격 한계 안에 들어오는 능력을 재는 지표. Cp는 산포만, Cpk는 중심 치우침까지 반영한다. 1.33 이상이 통상적 관리 기준이다(19장).
- **PPM(Parts Per Million)** — 백만 개당 불량 수로 표현하는 불량률 단위. 정밀 제조업의 표준 불량 지표다.
- **COPQ(Cost of Poor Quality, 품질실패비용)** — 불량·재작업·폐기·클레임 등 품질 실패로 발생하는 총비용. 품질 문제를 경영 언어(돈)로 번역하는 지표다(19장).
- **FPY(First Pass Yield, 초도수율)** — 재작업 없이 첫 공정 통과로 합격한 비율. 숨은 재작업 공장을 드러내는 지표다.
- **SPC(Statistical Process Control, 통계적 공정관리)** — 관리도로 공정의 이상 변동을 조기 감지하는 기법. Quality 4.0에서는 ML 기반 예측 품질로 확장된다(Zonnenshain & Kenett, 2020)(19장).
- **4M** — 사람(Man)·설비(Machine)·자재(Material)·방법(Method). 공정 변경점 관리와 불량 원인 분류의 기본 축이다(19장).
- **예지보전(Predictive Maintenance, PdM)** — 설비 데이터로 고장을 사전에 예측해 정비하는 방식. 사후보전→예방보전→상태기반보전의 다음 단계다(Ran et al., 2019)(18장).
- **RUL(Remaining Useful Life, 잔여수명)** — 설비·부품이 고장까지 사용 가능한 잔여 시간의 예측치. PHM(건전성 예지 관리) 연구의 중심 지표다(Lei et al., 2018).

### A-5. 도구·플랫폼

- **n8n** — 오픈소스 워크플로 자동화 도구. 시스템 간 연동, ETL, 알림 등 서드브레인의 AX 계층에서 워크플로 허브를 맡는다(15장).
- **Dify** — 오픈소스 LLM 애플리케이션 개발 플랫폼. 사내 문서 기반 RAG 챗봇과 AI 앱을 코드 없이 구성하는 AX 부스터다(15장).
- **frePPLe** — Odoo 공식 커넥터를 갖춘 오픈소스 APS. 유한능력 스케줄링과 수요예측으로 Odoo의 계획 기능을 보강한다(15장).
- **Ollama** — LLM을 로컬 서버에서 실행하게 해주는 오픈소스 런타임. 온프레미스 소형 모델과 클라우드 프론티어 모델의 이중화 구성에 쓰인다(15장).
- **온프레미스(on-premise)** — 자사 서버에 시스템을 설치·운영하는 방식. 클라우드(SaaS)와 대비되며, 데이터 주권과 운영 부담을 맞바꾼다.
- **TCO(Total Cost of Ownership, 총소유비용)** — 라이선스뿐 아니라 구축·교육·운영·업그레이드를 포함한 시스템의 전체 비용. ERP에서는 구축비가 5년 TCO의 35~55%를 차지한다는 분석이 있다(20장).
- **CSF(Critical Success Factors, 핵심성공요인)** — 프로젝트 성패를 좌우하는 소수의 결정 요인. ERP CSF 연구의 고전은 Umble 등(2003), Holland & Light(1999)다(4장, 20장).

## 부록 B. Odoo 모듈-부문-KPI 매핑표

각 부문의 경영 질문이 어느 Odoo 모듈의 데이터에서 답을 얻고, 어떤 KPI로 관리되는지의 총괄표다. 부문별 상세는 16~19장, KPI 트리는 21장을 참조하라.

| Odoo 모듈 | 담당 부문 | 축적되는 핵심 데이터 | 대표 KPI |
|---|---|---|---|
| 웹사이트 빌더·이커머스 | 마케팅·영업 | 방문·장바구니·주문 행동 데이터 | 전환율, 객단가, 장바구니 이탈률 |
| CRM | 영업 | 리드·기회·활동 이력, 단계 전환 | 파이프라인 총액, 수주전환율, 리드 응답시간 |
| 판매 | 영업 | 견적·수주·청구 조건 | 매출액, 견적 응답 리드타임, 재구매율 |
| 매입 | 구매 | 발주·입고·단가·공급업체 이력 | 구매단가 절감률, 공급업체 납기준수율 |
| 재고 관리 | 물류·재고 | 입출고 이동, 로트/시리얼, 재고 평가 | 재고회전율, DIO, 결품률, 오출고율 |
| 제조 관리(MRP·작업현장) | 제조 | BOM, MO/WO 실적, 가동 기록 | OEE, 생산 리드타임, 계획 준수율, 재공재고 |
| 품질(Quality) | 품질 | QCP 검사 결과, 불량 코드 | 불량률(PPM), FPY, Cp/Cpk |
| 유지보수(Maintenance) | 설비 | 고장·정비 이력, 예방정비 일정 | MTBF, MTTR, 예방정비 준수율 |
| 회계 | 재무 | 원장·채권채무·원가 배부 | 영업이익, COPQ, 현금전환주기(CCC) |
| 지식센터(Knowledge) | 전사 | 업무 표준·노하우 문서 | 문서화율, 검색 활용도(운영 지표) |
| frePPLe(부스터) | 계획 | 유한능력 계획, 수요예측 | 계획 준수율, 예측 정확도(MAPE) |
| n8n·Dify·Neo4j(부스터) | 서드브레인 | ETL 파이프라인, 지식그래프 | 질의 응답률, 판단 환류 건수(운영 지표) |

## 부록 C. AX 프로젝트 단계별 체크리스트 총괄표

4장에서 제시한 5단계 로드맵의 단계별 핵심 활동·산출물·성공 판정 기준의 총괄표다. 각 단계는 이전 단계의 성공 판정을 통과한 뒤 진입하는 것을 원칙으로 한다.

| 단계 | 핵심 활동 | 산출물 | 성공 판정 기준 |
|---|---|---|---|
| 1. 진단 | 경영 질문 정의, KGI→KPI 트리 도출, 데이터·사각지대 진단, 스폰서·챔피언 지정 | 경영 질문 목록, KPI 트리 초안, 현행 데이터 지도, 프로젝트 헌장 | 경영진이 승인한 경영 질문 10개 내외와 KPI 트리가 문서로 존재하는가 |
| 2. 기반 | Odoo 단일 플랫폼 구축, 코드체계(품목·공정·불량·고장) 정비, 기준정보 이관, 표준 프로세스 정착 | 가동 중인 Odoo 인스턴스, 코드체계 정의서, 기준정보 정합성 리포트 | 견적→수주→생산→출고→청구가 시스템 안에서 단절 없이 흐르는가, 이중 장부가 사라졌는가 |
| 3. 적재 | 트랜잭션 데이터 축적, 현장 데이터(바코드·IoT·음성·사진) 수집 정착, 암묵지 수집(노트·인터뷰의 LLM 구조화) | 데이터 파이프라인(n8n), 암묵지 형식지화 문서, 데이터 품질 리포트 | KPI 트리의 지표들이 수작업 없이 자동 집계되는가, 현장 기록 누락률이 목표 이하인가 |
| 4. 지능화 | 온톨로지 스키마 설계, 지식그래프 구축, GraphRAG·예측 모델·에이전트 구성, 자연어 질의 개통 | 온톨로지 정의서, Neo4j 지식그래프, 부문별 예측 모델, AI 브리핑·질의 서비스 | 대표 경영 질문에 근거 경로가 첨부된 답변이 나오는가, 예측 정확도가 기준선을 상회하는가 |
| 5. 환류 | AI 판단의 현장 환류(작업지시·발주안·검사 지시), 승인·피드백의 학습 루프화, 운영 리듬(일·주·월) 정착 | 환류 워크플로, Human-in-the-Loop 승인 체계, 운영 리듬 캘린더 | AI 제안의 채택률과 채택 후 KPI 개선이 측정되는가, 브리핑이 회의체에서 실제 소비되는가 |

여기에 15장의 경량 모델 — 초소형 기업의 3주 도입(1주 온보딩, 2주 지식적재, 3주 현장적용) — 은 위 5단계를 관리형 클라우드 위에서 압축 수행하는 변형임을 덧붙인다. 규모와 무관하게 판정의 원칙은 같다. 각 단계의 완료는 기능의 설치가 아니라 산출물과 판정 기준의 충족으로 선언한다.

## 부록 D. 참고문헌 안내

이 책의 참고문헌은 통합 목록 대신 각 장 말미의 "이 장의 참고문헌" 절에 분산 수록하는 방식을 택했다. 본문 인용은 (저자, 연도) 형식이며, 해당 서지사항은 인용이 이루어진 장의 말미에서 찾으면 된다. 같은 문헌이 여러 장에서 인용된 경우 각 장에 반복 수록했다. Odoo 공식 고객 사례와 국내 통계·보도 자료는 URL과 확인 시점을 함께 밝혔으며, 수치를 재인용할 독자는 원출처의 조사 시점과 모집단을 반드시 확인하기 바란다.

책 전체를 관통하는 대표 문헌 15선은 다음과 같다.

1. Davenport, T. H. (1998). Putting the Enterprise into the Enterprise System. *Harvard Business Review*, 76(4), 121–131. — ERP 도입을 경영 문제로 정의한 고전 (1·20장)
2. Jacobs, F. R., & Weston, F. C. (2007). Enterprise resource planning (ERP): A brief history. *Journal of Operations Management*, 25(2), 357–363. — MRP에서 ERP까지의 계보 (1장)
3. Umble, E. J., Haft, R. R., & Umble, M. M. (2003). Enterprise resource planning: Implementation procedures and critical success factors. *European Journal of Operational Research*, 146(2), 241–257. — ERP CSF 연구의 대표 (4·20장)
4. Polanyi, M. (1966). *The Tacit Dimension*. Routledge & Kegan Paul. — 암묵지 개념의 철학적 원전 (2장)
5. Nonaka, I., & Takeuchi, H. (1995). *The Knowledge-Creating Company*. Oxford University Press. — SECI 모델과 조직적 지식창조 (2·21장)
6. Ackoff, R. L. (1989). From Data to Wisdom. *Journal of Applied Systems Analysis*, 16, 3–9. — DIKW 계층의 표준 출처 (2·21장)
7. Gruber, T. R. (1993). A translation approach to portable ontology specifications. *Knowledge Acquisition*, 5(2), 199–220. — 온톨로지 정의의 기념비적 논문 (6장)
8. Uschold, M., King, M., Moralee, S., & Zorgios, Y. (1998). The Enterprise Ontology. *The Knowledge Engineering Review*, 13(1), 31–89. — 기업 온톨로지의 고전 (6장)
9. Hogan, A., et al. (2021). Knowledge Graphs. *ACM Computing Surveys*, 54(4), 1–37. — 지식그래프 표준 서베이 (6장)
10. Edge, D., et al. (2024). From Local to Global: A Graph RAG Approach to Query-Focused Summarization. arXiv:2404.16130. — GraphRAG를 대중화한 논문 (6·21장)
11. Pan, S., et al. (2024). Unifying Large Language Models and Knowledge Graphs: A Roadmap. *IEEE TKDE*, 36(7). — LLM과 지식그래프의 상호보완 프레임 (6·21장)
12. Glaessgen, E., & Stargel, D. (2012). The Digital Twin Paradigm for Future NASA and U.S. Air Force Vehicles. AIAA 2012-1818. — 디지털 트윈의 초기 공식 정의 (6장)
13. Tao, F., et al. (2018). Digital twin-driven product design, manufacturing and service with big data. *IJAMT*, 94, 3563–3576. — 제조 디지털 트윈의 표준 프레임워크 (6·18장)
14. Makridakis, S., Spiliotis, E., & Assimakopoulos, V. (2022). M5 accuracy competition: Results, findings, and conclusions. *International Journal of Forecasting*, 38(4). — ML 수요예측의 우위를 실증한 M5 대회 분석 (16장)
15. Kaplan, R. S., & Norton, D. P. (1992). The Balanced Scorecard — Measures That Drive Performance. *Harvard Business Review*, 70(1), 71–79. — 전략과 성과지표를 연결한 고전 (21장)
