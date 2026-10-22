# 방글라데시 제약산업 및 국영 제약사(EDCL) 조사 보고서
### ERP/GMP 디지털화 제안을 위한 사실 기반 리서치 (작성일: 2026-10-22)

> **범례**: **[확인]** = 복수 또는 신뢰도 높은 출처로 확인된 사실 · **[단일출처]** = 한 출처에만 근거 · **[추정]** = 조사자 추론 · **[불확실]** = 출처 간 상충 또는 날짜 불명
>
> **조사 방법상의 한계**: 본 세션에서는 WebFetch(개별 페이지 열기)가 전 도메인에서 DNS 오류로 실패하고, 프록시가 curl CONNECT를 403으로 차단해 1차 문서(EDCL 포털, BPPA 공고 원문, Wikipedia, 신문 원문 등)를 직접 열 수 없었습니다. 모든 내용은 **검색엔진 결과 요약**에 의존하므로, 숫자·날짜는 제안서 확정 전 원문 재확인을 권합니다. 또한 검색 할당량(200회/턴)이 소진되어 일부 보조 항목(EDCL 정확한 인력 규모, Thailand GPO·Bio Farma ERP 세부 등)은 추가 확인하지 못했습니다.

---

## 0. 핵심 요약 (Executive Summary)

1. **방글라데시의 유일한 국영 제약사는 Essential Drugs Company Limited(EDCL)** — 보건가족복지부(MoHFW) 산하 100% 국영. 다카 Tejgaon 본공장 + Bogura + Gopalganj 공장, Khulna 라텍스(콘돔) 공장. 약 140개 품목 생산, 공공병원 의약품 수요의 약 80%를 공급(단일출처). **[확인]**
2. **EDCL은 2026년 5월 17일 ERP 설계·개발·구축을 위한 EOI(관심표명서)를 공고**했다(Ref. EDCL/Dhaka/EOI/Tender/2026/168, QCBS, 자체 자금, **"national consulting firm" 대상**, 마감 2026-06-10). 모듈: 재무회계, HR/급여, 조달, 계획, 재고/창고, 판매/유통, **QC·제조**, 프로젝트관리. 낙찰/숏리스트 공개 여부는 확인되지 않음. **[확인 — 결과는 불확실]** → 한국 벤더에게 가장 중요한 단일 사실.
3. **GMP 현황**: EDCL은 과거 노후 설비로 cGMP 미준수 → WHO 등 국제기관 인증 철회 이력(TBS). Gopalganj 3공장(Tk 800 crore, 2.5배 초과)·Tejgaon 이전(Manikganj, Tk 1,905 crore, ECNEC 승인) 등 현대화 프로젝트가 있으나 2025.8 보건자문관이 **Munshiganj Sirajdikhan에 40에이커 신규 통합단지(의약품+백신+항독소)**를 발표하면서 입지 계획이 바뀌었을 가능성. **[불확실]**
4. **ADB $336.5M 차관(2023.11 서명) "Vaccines, Therapeutics & Diagnostics Manufacturing and Regulatory Strengthening Project"**: EDCL 백신공장(연 5,800만 바이알, WHO GMP 인증 목표, 생산 개시 목표 2032) + DGDA의 WHO ML3 달성 지원. **[확인]**
5. **규제기관 DGDA**는 WHO 성숙도 ML2 단계이며 ML3 미달(2027년 5월 WHA 전 달성 목표). PIC/S는 "pre-applicant"로 알려져 있으나 현황 미확인. **[확인/불확실]**
6. **산업 규모**: 내수 시장 약 Tk 40,885 crore(≈US$3.3B, IQVIA MAT Q2 2026, +10.6%), 상위 10사가 약 75% 점유(Square 17%, Incepta 12.6%, Beximco 9.8%, Renata 5.7%, Eskayef 4.9%). 수출 FY2025-26 US$238.5M. 내수 자급률 약 98%, API는 약 85% 수입 의존. **[확인, 단 LinkedIn 2차 인용 다수]**
7. **LDC 졸업 2026년 11월(24일 또는 26일)** → TRIPS 의약품 특허 유예 종료(최대 3년 연장 가능). Patent Act 2023이 의약품을 졸업 시까지 특허 제외. **[확인]**
8. **ERP 환경 변수**: PPR 2025(2025-09-28 시행, e-GP 전면 의무화), Finance Bill 2026(Mushak 6.3 VAT 챌런의 ERP 전자발행 허용), 개인정보보호령 2025(데이터 현지화 조항; 2026.1 완화 보도—미검증), 정부 소버린 클라우드(Kaliakoir Tier-IV NDC + Oracle Dedicated Region), 2026년 7~10월 가스·전력 위기(산업용 정전 3~4시간/일). **[확인/일부 미검증]**
9. **벤치마크 교훈**: Kimia Farma(인도네시아, SAP 2015-16 → 모듈 일부만 사용, 2024 자회사 회계조작·Rp 8.7조 부채 구조조정), EIPICO(이집트, SAP+53라인 추적시스템), Vinapharm(베트남, GMP-EU 라인 투자로 2025 사상 최대 이익), SPMC(스리랑카, JICA 공장 → 2025 사상 최대 생산), Nepal Drugs(10년 가동 중단 후 ORS로 재가동), 인도 PSU(HAL/IDPL 장기 회생 실패, KAPL만 흑자). **공통 교훈: 거버넌스·내부통제 모듈과 GMP 데이터 무결성이 ERP 성공의 전제.** **[확인]**
10. **한국 연계**: EDCF 프레임워크 US$3B(2023-27), KOICA 2026-28 US$96M 신규 패키지(간호교육·통계 DW 등). **제약 분야 한-방 공식 협력 사례는 확인되지 않음**(2021 백신공장 협력 논의 수준). 한국 IT기업(SDS/LG CNS/KT)의 방글라데시 정부 프로젝트 수행 사례도 미확인. 반면 **베트남 FPT IS가 SAP 기반으로 EGCB(US$8.8M), GTCL(US$9.1M) 등 국영기업 ERP를 수주**한 전례가 있어 "외국 SI + 국영기업 ERP" 모델 자체는 선례 존재. **[확인]**

---

## 1. 방글라데시 국영 제약사: Essential Drugs Company Limited (EDCL)

### 1.1 기본 프로필
| 항목 | 내용 | 신뢰도 |
|---|---|---|
| 법적 지위 | 100% 국영 유한회사, 보건가족복지부(MoHFW) 산하. 방글라데시 **유일의** 국영 제약 제조사(TBS "lone state-owned drugmaker") | [확인] |
| 연혁 | 1962년 (동)파키스탄 정부 Government Pharmaceuticals Laboratory로 출발 → 1983년 현 EDCL 체제 | [확인-Wikipedia 요약] |
| 사명 | 양질의 의약품을 저가로 생산해 정부병원·보건기관에 공급 | [확인-EDCL 포털] |
| 경영진 | MD & CEO **Md. A. Samad Mridha** (2025-01-01 MoHFW 임명). 전임 MD Prof. Dr. Ehsanul Kabir(Dyadic MoU 서명자) | [확인] |
| 인력 | "2,500명 이상"(MCCI/DevelopmentAid 프로필) vs "201~500명"(다른 디렉토리). Prothom Alo는 "3,000명 이상 초과 인력" 보도 제목 확인(본문 미열람) | [불확실] |
| 품목 수 | 약 140개 품목(2025 Bangla 보도) / 123종(2016) | [확인] |
| 재무 | **매출·이익 공식 수치 미확보.** 2016년 보도: 연간 공급액 약 Tk 450 crore. 2025.8: 33개 필수의약품 가격 최대 50% 인하 → 정부 연 약 Tk 116 crore 절감 | [단일출처/구자료] |
| 공공공급 역할 | 공공병원 의약품 수요의 **약 80%** 충당(TBS); 자체 생산 부족분 최소 30%는 민간 조달(toll/구매)에 의존. 공공병원은 EDCL 생산 품목에 대해 **입찰 없이 EDCL에서 의무 구매**(2014 Dhaka Tribune 사설). 정부 수요 충당률을 70%→90%로 높이고 toll manufacturing 중단 계획(Financial Express, 약 2026.1) | [확인/단일출처] |
| 산업계 관계 | 2026.8 BAPI(제약협회)가 "민간에 비경제적인 필수의약품은 EDCL이 생산하도록" 정부에 요청 — EDCL이 "전국 5개 생산시설" 보유 언급 | [확인] |

### 1.2 공장·시설
| 시설 | 위치 | 내용 | 신뢰도 |
|---|---|---|---|
| Plant 1 (본공장) | Tejgaon, Dhaka (1.75 acre) | 노후, 확장 불가 → 이전 대상. IV 수액, 철분제, 호르몬제, 페니실린계 생산(EDCL 포털). 2025.10 공장 옆 신축 다층건물 공사 진행(연 Tk 13 crore 창고임차 절감 목표) | [확인] |
| Plant 2 | Bogura(Bogra) | 세부 용량 미확인 | [확인-존재만] |
| Plant 3 | Gopalganj (10 acre) | 2015.3 착공, 2018 완공·가동 예정 보도. 목표: 피임주사 3,300만, 피임약 3,200만, 페니실린 정 1.81억, 캡슐 2.17억, 항생제 12종/년. 비용 Tk 315 crore → **Tk 800 crore(2.5배 초과)**. 백신 생산 유닛 존재(2025 보도) | [확인] |
| Khulna Essential Latex Plant (KELP/ELPP) | Khulna | 라텍스 콘돔 | [확인] |
| 백신 복합단지 | Gopalganj(원안, 7~8 acre, Dyadic MoU) → **Sirajdikhan, Munshiganj(2025.8 발표, 40+ acre)** | ADB 차관, 연 5,800만 바이알, WHO GMP 인증 목표. 2026.5 BSS: 뎅기·광견병·홍역 백신 및 항독소 생산 추진, **생산 개시 목표 2032**, 약 10 acre에 건설 중(입지 미명시) | [불확실-입지 상충] |
| Tejgaon 이전 신공장 | Manikganj Sadar (Dhaleshwari 강변, Dhaka-Aricha 고속도로) | ECNEC 승인 **Tk 1,905 crore**, 5년 내 완공 목표, cGMP 기준. Hasina 정부 시기 승인. 2025.8 "Manikganj 공장도 Sirajdikhan으로 이전" 발언 → 계획 변경 가능성 | [불확실] |

### 1.3 GMP 상태 및 품질 이력
- **[확인]** TBS(2021): 노후 설비로 **cGMP 준수 불가 → WHO 포함 국제 보건기관이 인증 철회**. 이것이 Gopalganj 3공장·Tejgaon 이전 프로젝트의 핵심 명분.
- **[확인]** 2025.8 Observer: 과거 입찰 담합(tender syndicate), 비투명 고가 원료 구매, 설비 유휴, 과잉 인력, **입찰 분쟁으로 항생제 생산 장기 중단**. 신경영진(2025~)이 입찰 투명성 회복·인력 감축·초과근무 축소·가격 인하 추진.
- **[확인]** 정부 감사(CAG) 2019-20/2020-21: **32건 부정, Tk 477 crore 손실** 적발(입찰 장사, 채용 장사, 피크닉 위장 출장, 저품질 생산 등). 고등법원이 ACC(반부패위) 조사 명령; 2025.2 ACC가 EDCL 압수수색. EDCL은 Daily Star 보도에 반론(rejoinder) 제출.
- **[추정]** 위 사실은 ERP 제안에서 **내부통제·조달 투명성(e-GP 연동, 승인 워크플로, 감사추적)**이 재무/생산 모듈과 동등한 셀링포인트임을 시사.

### 1.4 IT/ERP 현황 — 핵심 발견
- **[확인]** BPPA 포털 공고: **"Design, Development, Implementation of an Enterprise Resource Planning (ERP) for Essential Drugs Company Limited"**
  - Ref: **EDCL/Dhaka/EOI/Tender/2026/168**, 공고일 2026-05-17(포털 게재 05-19), **마감 2026-06-10 12:00**
  - 발주: Managing Director, EDCL / 조달방식: **QCBS(Quality and Cost Based Selection)** / 재원: **자체 자금(Own Funds), 개발파트너 없음** / 대상: **National consulting firm**
  - 목적: 전 부서의 운영효율·투명성·데이터 기반 의사결정; EDCL 전략목표·규제 프레임워크에 맞춘 **맞춤 설계(custom-designed)**
  - 모듈(비한정): 재무회계, HR·급여, 조달, 계획, 재고·창고, 판매·유통, **품질관리·제조**, 프로젝트관리
  - **낙찰·숏리스트 정보는 검색에서 확인되지 않음**(2026-10-22 기준).
- **[추정]** "national firm" 한정 + 자체자금 + QCBS는 (a) 외국 벤더 단독 참여가 어렵고, (b) 현지 컨설팅/SI 파트너와의 컨소시엄 또는 **기술 서브컨트랙터/제품 공급자** 포지션이 현실적임을 의미. (c) 이미 EOI가 진행된 만큼, 제안 전 BPPA/e-GP에서 RFP 발행·낙찰 여부를 반드시 확인해야 함. (d) 백신공장(ADB 재원)은 별개 조달 트랙 — **ADB 조달규정(국제경쟁입찰, ADB 회원국 적격)**이 적용되므로 외국 벤더에게 더 열려 있음 → GMP 계층(MES/EBR/LIMS/QMS/시리얼라이제이션)을 ADB 트랙으로 제안하는 전략 검토 가치.
- **[단일출처]** ADB 자료(2024): DGDA의 "electronic information management system" 활용도 낮음, 등록 SOP 불명확 → 규제기관 측 디지털 역량도 취약.

### 1.5 정부 예산·조달 프로그램
- **[확인]** 2025.8 EDCL 33품목 가격 인하(정부 Tk 116 crore/년 절감). EDCL은 BPPA 포털에 원료 구매 입찰(예: details-97089, 81614) 상시 공고.
- **[확인]** 5차 보건부문프로그램(HNPSP 5th, 2024-2029, 약 Tk 1.06조): World Bank PforR P180283(IDA $379M+GFF $25M, Chattogram·Sylhet), ADB $500M 예정(CPD 인용). 2025.4 WB $570M 승인(보건 $515M + 디지털 모니터링·공공조달 $55M).
- **[추정]** CMSD(Central Medical Stores Depot)와 EDCL의 역할 분담은 본 조사에서 확인 못함.

---

## 2. 방글라데시 제약산업 개요

### 2.1 시장 규모·성장
| 지표 | 수치 | 출처/신뢰도 |
|---|---|---|
| 내수 시장 | **Tk 40,885 crore(≈US$3.32B), MAT Q2 2026, +10.6% YoY**; 4년 CAGR 11.4% | IQVIA(LinkedIn 2차인용) [확인-2차] |
| GDP 비중 | 약 0.7% (GDP ≈US$475B 기준) | [2차] |
| 자급률 | 내수 약 **98%** 국내 생산 | [확인] |
| 수출 | **FY2025-26 US$238.5M**(EPB, 16년간 5.5배); FY2026-27 7~9월 US$76.6M(+40%) | bdnews24 [확인] |
| 수출국 수 | 132~166개국(출처별 상이; 통상 "150+") | [불확실] |
| API 의존 | **약 85% 수입**(인도·중국), 연 US$1.2~1.3B | Daily Star/TBS [확인] |
| 제조사 수 | DGDA: 295 allopathic 제조사; BAPI: 307 등록, **약 150 실가동** | TBS [확인-날짜불명] |

### 2.2 상위 기업 (IQVIA MAT Q2 2026, 2차 인용)
| 순위 | 기업 | 점유율 | 매출(Tk crore) | 국제 인증(요약) |
|---|---|---|---|---|
| 1 | Square | 17.0% | 6,936 | US FDA(OSD, 483 없음) |
| 2 | Incepta | 12.6% | 5,139 | EMEA(Austria) 2008, WHO-PQ 품목 보유(2020, 2026 보고서), **2021 SAP ERP 도입(방글라데시 최초 주장)**, DGDA WHO-format GMP 인증 2025 |
| 3 | Beximco | 9.8% | — | **2015 미 FDA 승인 1호**, EU·TGA·Canada·Brazil; WHO-PQ lamivudine(2019); **Oracle EBS R12(KPMG India/DHC) + GxP 검증** |
| 4 | Renata | 5.7% | 2,334 | MHRA(2007), FDA(Rajendrapur 2022), TGA, WHO; **Antares Vision 시리얼라이제이션(2018~)** |
| 5 | Eskayef(SK+F) | 4.9% | — | — |
| 기타 | ACI(WHO-PQ azithromycin 2024), ACME(WHO-PQ zinc 2021, Gazaria API 공장) | | | |
| 집중도 | **Top 10 ≈ 75%** | | | |

### 2.3 규제기관 DGDA 및 정책
- **[확인]** DGDA(Directorate General of Drug Administration), MoHFW 산하, 전국 55개 지방사무소. **Drugs and Cosmetics Act 2023(Act No.29, 2023.9)**이 Drugs Act 1940·Drugs (Control) Ordinance 1982 대체.
- **[확인]** **National Drug Policy 2016**: WHO 인증 및 **PIC/S 가입** 목표 명시.
- **[확인]** **WHO GBT 성숙도: ML2**(2023 기준). 2016년부터 ML3 추진, 2021.7 공식 벤치마킹, 2026.7 TBS: 여전히 미달(규제 프레임워크·감독·과학적 평가·QA·통합시스템 격차), **2027.5 WHA 전 달성 목표**. ADB 결과프레임워크 문서에 "ML3 달성" 표기가 있으나 목표치일 가능성 → **[불확실]**.
- **[단일출처/구자료]** PIC/S: Parexel(≈2020)이 DGDA를 5개 **pre-applicant** 중 하나로 열거. 현 상태 미확인.
- **[확인]** API Park(Gazaria, Munshiganj, 200 acre, 2008 승인): 27개 유닛 분양, 2025.7 양도 규정 고시(2025-12-30 양도 마감), ACME 등 3사 가동 준비(가스 공급 미비). "20년간 진전 미미"(TBS).
- **[확인]** FY2026-27 예산(2026-06-11): API 원료 51종 수입관세 철폐, 항암제 원료 9종 관세·VAT 0%, 17종 추가 감면 — 총 77개 원료; LDC 졸업 대비 세제지원 지속.

### 2.4 LDC 졸업과 TRIPS
- **[확인]** 졸업일: **2026년 11월 24일**(RAPID, Ittefaq) 또는 26일(tralac) → [불확실-날짜].
- **[확인]** **Patent Act 2023**(2023-11-13 관보, 2022법 대체): 의약품은 LDC 졸업까지 특허 제외, **졸업 후 3년 연장 가능**(WTO 각료결정 근거); 강제실시, 병행수입, 연구예외 포함.
- **[확인]** 영향 전망 상충: RAPID 연구 "졸업만으로 약가 상승 가능성 낮음, 수출 최대 6.9% 감소"; 업계는 신규 특허 분자 제네릭 생산 불가·수출경쟁력 저하 우려. 2026년 이후 신규 분자는 특허 필요.
- **[추정]** EDCL은 필수의약품(대부분 특허만료) 중심이므로 직접 영향은 제한적이나, **백신·바이오시밀러 신사업**은 특허·기술이전 조건 검토 필요.

---

## 3. GMP·규제 환경

### 3.1 DGDA GMP 요건
- **[확인]** DGDA는 WHO GMP 기반 검사·인증(Incepta 2025 WHO-format GMP 인증서 예시). 2016 WHO 주도 검사관 교육에서 "공장 검사·GMP 준수 프로세스 격차" 확인. ICH M4 기반 백신 CTD 가이드라인 발간.
- **[불확실]** **DGDA 자체 데이터 무결성/CSV(컴퓨터화 시스템 밸리데이션) 가이드라인은 검색에서 확인되지 않음.** 업계는 PIC/S PI 041-1(2021), EU Annex 11, 21 CFR Part 11, ALCOA+를 참조하는 것으로 보임 → ERP/MES 제안 시 **PIC/S PI 041 + Annex 11 기준 설계**가 안전.
- **[확인]** ADB(2024): National Control Laboratory(NCL) GLP 미달, 검사관 부족, 전자정보시스템 활용 저조, 약물감시 취약, GAVI 지원 2029 종료 예정.

### 3.2 집행 이력·공통 결함(간접)
- **[확인]** 2014.8 국회 보건위 결정으로 전문가위원회(Prof. ABM Faruque)가 **84개 제조사 GMP 평가** → 2016.2 보고: 20개사 면허취소 권고, 특정 공장의 페니실린·세팔로스포린·항암·호르몬 제조 허가 취소 권고. 고등법원(Writ 6969/2016) 20→28→34개사 생산중단, WHO GMP 준수 감시위원회 구성, DGDA 3개월마다 법원 보고. 2009~2023 **45개사 면허 취소**(보건장관, 2023).
- **[추정]** 공개된 상세 결함 목록은 없으나, 위 사례와 WHO/ADB 지적을 종합하면 방글라데시 공장의 전형적 격차는 (i) 페니실린/세팔로스포린 전용시설·교차오염 관리, (ii) QC 실험실·미생물 역량, (iii) 문서화·배치기록 신뢰성, (iv) 노후 설비·유틸리티(HVAC/수처리)로 추정됨. **EDCL의 "WHO 인증 철회"도 같은 범주일 가능성이 높으나 1차 자료 미확인.**
- **[확인]** 방글라데시 공장에 대한 미 FDA 경고서한은 검색되지 않음(인도·중국 사례만). Square·Beximco FDA 검사 "483 없음".

### 3.3 시리얼라이제이션/추적
- **[확인]** **DGDA의 2D 바코드·시리얼라이제이션 의무화 규정은 확인되지 않음.** Renata가 Antares Vision과 2018년부터 자발적 시리얼라이제이션(수출 대응). 비교: 인도 2026 Drugs Rules 개정(백신·항암·마약류 QR 2027.7, 항균제 2028.7), 파키스탄 DRAP 2026-10-09부터 2D DataMatrix 1단계.
- **[추정]** 인도·파키스탄 선례 + WHO ML3 추진 + 백신 수출 야망을 고려하면 DGDA 차원의 track-and-trace 도입 가능성이 중기적으로 높음 → ERP에 GS1 배치/시리얼 데이터 모델과 애그리게이션 확장성을 선제 반영하는 것이 차별점.

---

## 4. 디지털화·ERP 도입 환경

### 4.1 민간 제약사 ERP 현황
| 기업 | ERP | 근거/신뢰도 |
|---|---|---|
| Incepta | **SAP ERP(2021)** — PP·QM 모듈 포함 | Wikipedia+LinkedIn [확인-2차] |
| Beximco | **Oracle EBS R12**, KPMG India·DHC Switzerland 구현, GxP 밸리데이션 | LinkedIn [단일출처] |
| Renata | HRIS 논문 외 ERP 공개정보 없음; Antares Vision 시리얼라이제이션 | [불확실] |
| Square | ERP 공개정보 없음 | [불확실] |
| 산업 전반 | 22개사 조사(BAUET 2024): **약 55% Industry 4.0 기술 도입, 50% 창고·SCM 자동화**(QMS 미보유 기업 제외한 샘플 → 상향 편향) | [확인-학술] |
| 장애요인 | 비용·자원 제약, IT 인프라 부족, 조직 저항, 커스터마이징, 벤더 종속(Sarker 2024) | [확인-학술] |

### 4.2 공공부문 ERP 선례
- **[확인]** **FPT IS(베트남)**: EGCB(발전공사) ERP/EAM **SAP** US$8.8M(2016.10, 18개월, 본사+3발전소 가동 — BPDB 14개 자회사 확산 파일럿), GTCL(Petrobangla 가스수송) ERP/EAM US$9.1M(2016.4). FPT는 NBR의 VAT/소득세 시스템도 구축. → **외국 SI가 국영기업 ERP를 수주한 선례**.
- **[확인]** KOICA: e-Government Master Plan·Digital Municipality Service(US$3.2M, 2014~, BCC), e-File(US$1.3M, 2010-12), BBS 통계 DW(US$9.65M).
- **[확인]** e-GP: PPR 2025로 **전면 의무화**; 입찰 수 평균 2.7→8.5건(2025.12). WB $55M "Digitizing Implementation Monitoring and Public Procurement" 프로젝트(2025.4).

### 4.3 국가 디지털 정책
- **[확인]** 전 정부의 "Smart Bangladesh 2041"(4대 축) → 과도정부(2024.8~) 이후: 국가디지털전환전략 초안(2025.2, UNDP), **개인정보보호령 2025·국가데이터관리(거버넌스)령 2025·사이버보호령 2025**(Cyber Security Act 2023 대체), AI 정책 초안 2026-2030, 클라우드·블록체인 정책 초안. FY2026-27 ICT Division 예산 Tk 2,049 crore; "One Citizen, One ID, One Digital Wallet"(에스토니아 X-Road 기반). a2i 현 지위는 미확인.
- **[불확실]** 개인정보보호령 2025는 **데이터 현지화 의무** 포함(2025-11-06 발효 보도) → 2026.1 개정으로 광범위 현지화 요건 대부분 삭제·징역형 폐지 보도(Daily Star) — **단일출처, 미검증**. 보수적으로 **국영기업 데이터는 국내 호스팅** 전제가 안전.

### 4.4 인프라 현실
- **[확인]** **국가데이터센터(Kaliakoir, Bangabandhu Hi-Tech City)**: Uptime Tier IV 인증(99.995%, 2N+1), BDCCL 운영(2020 설립), **Oracle Dedicated Region Cloud@Customer 기반 정부 소버린 클라우드**(보건 워크로드 명시). 하이퍼스케일러(AWS/Azure/GCP) 국내 리전 없음(검색상 미확인).
- **[확인]** 전력·가스: 2026-07-21 Moheshkhali FSRU 고장 → 8월 부하차단 사상 최대 3,757MW(실제 4,000MW+), 10월 초 35개 발전소 정지·2,500MW 부하차단; Dhaka·Gazipur·Chattogram 산업벨트 **근무시간 3~4시간 정전**, 디젤 발전기 의존. → **온프레미스/하이브리드 설계 시 UPS·발전기·오프라인 내성(배치기록 캐싱) 필수.**
- **[확인]** 인터넷: 이용자 8,280만(47%, 2025말, DataReportal) / 가입 1.336억(모바일 1.193억, 유선 1,432만, 2025.6). 모바일 4G 중심, 5G 2026 계획; 가장 저렴한 가정용 10Mbps.

### 4.5 ERP 로컬라이제이션 요구사항 (세무·언어·회계)
| 항목 | 요구사항 | 신뢰도 |
|---|---|---|
| 통화 | BDT(Taka), 단위 관행 **lakh/crore**(1 crore = 1천만) | [확인] |
| 회계연도 | **7월 1일 ~ 6월 30일**(정부·대부분 기업) | [확인-일반지식] |
| 언어 | 공식 Bangla(벵골어), 비즈니스·규제 문서는 영어 병용. 정부기관 UI/보고서 **Bangla Unicode 지원** 필요(벵골력 날짜 표기 관행 포함) | [확인/추정] |
| VAT | VAT & SD Act 2012 체계, 표준 15%. 의약품 **거래단계 2.4%(매입세액 공제 없음)**(상업 블로그-미검증). 수입 의약품 15%. 지역 VAT 공제원천징수(VDS) 규칙 2025 | [불확실-공식 미확인] |
| Mushak 양식 | **Mushak 6.3(세금계산서/챌런)**, 6.1/6.2(매입·매출장), 9.1(월 신고). **Finance Bill 2026: Mushak 6.3을 ERP/지정 VAT 소프트웨어로 전자 발행·보존 허용, 디지털 기록 증거력 인정.** e-invoicing 의무화 일정 미정(대기업 우선 예정), 구조화 XML/UBL 미규정, EFD/SDC는 소매용 | [확인] |
| 조달 연동 | **e-GP 전면 의무**(PPR 2025) → ERP 조달모듈–e-GP 데이터 정합성(수기 재입력 최소화) | [확인] |
| 데이터 | 개인정보보호령 2025(현지화 조항 변동 중) → 국내 호스팅 권장 | [불확실] |
| 공공회계 | 정부 iBAS++와의 연계 요구 가능성(국영기업 보고) | [추정] |

### 4.6 현지 파트너 후보(Odoo·로컬 ERP)
- **[확인-벤더 자료]** Odoo 파트너: **Metamorphosis Ltd**(Dhaka Mirpur, "최초 Odoo Country Partner", 제약 장비·물류사 Pasteur Pharmatech 프로젝트), **VS ONE Bangladesh**(Gulshan, 제약 산업 커버 명시), **Xsellence Bangladesh**(Gold/Silver 티어 상충), **Ogroni Informatix**(Hoque Pharmacy 구현). Odoo 고객사례: Alchem Enterprise(API·부형제 공급사).
- **[확인-벤더 자료]** 로컬 ERP: **PrismERP(Divine IT, 400+ 고객)**, Southtech, Datasoft(MyERP), ERPNext 커스텀(ECOSIRE: Mushak 6.3/9.1 앱). 제약 제조 특화 레퍼런스는 확인 안 됨.
- **[추정]** EDCL EOI가 "national consulting firm"을 요구하므로, 위 업체 중 하나 또는 Big4 방글라데시 법인(KPMG·PwC 등)이 주계약자가 되고 한국 벤더가 **GMP 특화 솔루션(MES/EBR/LIMS/QMS/시리얼라이제이션) + 밸리데이션(CSV) 공급자**로 참여하는 구조가 현실적.

---

## 5. 비교 벤치마크: 개도국·국영 제약사의 ERP/GMP 현대화

| 사례 | 무엇을 했나 | 결과/교훈 | 신뢰도 |
|---|---|---|---|
| **Kimia Farma (인도네시아, SOE)** | SAP ERP 2015(유통)·2016(그룹) — 라이선스·HW·구현·MSP 일괄; 자회사 재무 통합 목적 | 약국 유닛은 9모듈 중 **4개만 사용**, "복잡해 최적 활용 못함"; 재무 투명성은 개선. **2024 자회사 KFA 2021-22 회계조작(매출 과대·손실→이익) 적발, 2022 재무제표 재작성, 2024 Rp 8.7조 부채 구조조정**, 2026 Danantara가 Bio Farma 홀딩에서 분리. 교훈: ERP ≠ 통제; 재고·채권 통제·감사추적·변경관리가 핵심 | [확인] |
| **Bio Farma (인도네시아, 백신 SOE)** | 2020 제약 SOE 홀딩 모회사; 디지털전환 전담 이사회 신설, Google Cloud MoU(2021), AI/ML R&D·생산 적용; end-to-end 헬스 생태계 | SAP 구현 여부 미확인. 2026 홀딩 재편으로 **백신 R&D·생산에 집중** | [확인/불확실] |
| **EIPICO (이집트, ACDIMA 51% 범아랍 공영)** | 2021 연차보고: **SAP 구현 착수 + 53개 생산라인 제약 추적(serialization) 시스템**; QM 모듈에서 배치 유효기간·격리 재고 통제 | 2026 Arab API JV(US$165M) 등 확장. 교훈: ERP와 라인 레벨 추적을 병행 | [확인-연차보고+LinkedIn] |
| **Vinapharm (베트남, 국가 65%)** | 회원사 100+ GMP 라인 중 26개 **GMP-EU/PIC-S/Japan** 업그레이드; Sanofi Vietnam 지분 15→30%; 2026-30 바이오·하이테크 전환 | 2025 세전이익 8,250억 VND(+62%, 사상 최대), CAGR 37%(2021-25). 교훈: 고규격 GMP 라인이 수익성·수출 견인 | [확인] |
| **Genfarma (베트남, 민간 — 참고)** | FPT와 **SAP S/4HANA Public Cloud 2개월 가동(2026.3→5)**; GMP-WHO/GSP/GLP, 배치 추적, FEFO | 클라우드 ERP의 신속 구현 사례(단, 민간·소규모) | [확인-벤더] |
| **SPMC (스리랑카, 국영)** | JICA 자금 Ratmalana 복합단지(2018) 용량 19.2→33.4억정; 2026 Ratmalana 창고(3월 개장 예정), Millewa/Horana 신규 제조·포장·창고 | **2025 사상 최대 36.25억 정·캡슐 생산**, 2026 목표 40억·신제품 10개. ERP 정보 없음. 교훈: 양자 ODA(JICA)로 GMP 공장 → 생산성 도약 | [확인] |
| **Thailand GPO (국영)** | Rangsit 2단계 공장(56억 바트, 2019 계약, "Smart Industry" 목표), PIC/S GMP 운영·WHO GMP 지향, 신규 API 공장 | ERP/SAP 공개정보 미확인 | [확인/불확실] |
| **Nepal Drugs Ltd (국영)** | 10년 가동중단 → 2016 내각 회생 승인(Rs 1.465억 대출), 전문경영진 채용, ORS부터 재가동 | 소규모 단계적 재가동 모델; 현 상태 미확인 | [확인-구자료] |
| **인도 제약 PSU (IDPL/HAL/KAPL/RDPL/BCPL)** | HAL 1997 BIFR, 2007 회생패키지, 2014 Rs 525 crore 추가 요청 — 여전히 "회생 모드"; IDPL Rs 2,862 crore 채무면제; **KAPL만 WHO-GMP 세팔로스포린 공장(Rs 7.1 crore) 투자 후 흑자** | 교훈: 설비 투자 없는 재무 구제는 실패; 소규모 흑자 PSU(KAPL)는 GMP 특화 투자로 생존. KAPL ERP 정보 없음 | [확인-구자료] |
| **Ethiopia (EPHARM/Kilinto)** | 국영 EPHARM(1964)을 Medtech Ethiopia가 US$25M에 인수(민영화); Kilinto 제약산업단지(WB 재원, 279ha) | 공공 수요 60%; 로컬 생산 15~20%. 교훈: 국영사 민영화 + 산업단지 모델 | [확인/날짜불명] |
| **Pakistan / Kenya** | 국영 제조사 부재(파키스탄 DRAP 2026.10 track-and-trace 시작; 케냐 KEMSA는 조달기관) | 제조사 벤치마크로 부적합 | [추정] |

**종합 교훈(추정)**: (1) 국영 제약사 ERP는 **재무 통합**으로 시작하지만 **조달·재고·배치 추적의 내부통제**가 없으면 부정·손실(Kimia Farma, EDCL 감사)이 재발; (2) **GMP 하드웨어(공장) + 소프트웨어(ERP/MES/LIMS)를 동일 로드맵**에 두어야 WHO GMP·수출이 가능(Vinapharm, SPMC, EIPICO); (3) 모듈 과다 도입은 미사용으로 끝남(Kimia Farma 4/9) → **단계적 범위, 현지어 교육, 변화관리** 필수; (4) 양자 ODA(JICA→SPMC, ADB→EDCL)가 국영사 현대화의 실질 재원.

---

## 6. 한국(외국) 벤더의 실무 고려사항

### 6.1 조달 규범
- **[확인]** 법령: Public Procurement Act 2006 + **Public Procurement Rules 2025**(2025-09-28 시행, 154개 규칙·21개 부속서; PPR 2008 대체). 주요 변경: **e-GP 전면 의무**(ICT 역량 부족 기관은 BPPA 승인 하 한시적 수기), 공사입찰 ±10% 가격밴드 폐지, 조달전략 수립 의무, 프레임워크 계약·협상 확대, **제재(debarment) 위원회**, **낙찰자 실소유자(beneficial owner) 공개 의무**, 지속가능조달, NGO 참여 허용.
- **[확인]** e-GP Guidelines (Revised) 2025 존재; 국제입찰/컨설턴트 등록·갱신 수수료 개정 고시; 2024.12 BPPA 자료에 **ICB(국제경쟁입찰) e-GP 탑재**가 신규 이니셔티브로 열거(가동 여부 미확인). 과거(2018 논문) e-GP는 Tk 5억 초과·국제입찰·지적서비스 처리 불가였음.
- **[불확실]** 외국 기업의 **현지 에이전트 의무**·국내우대(domestic preference) 마진은 확인 못함(WB/ADB 재원 사업은 각 기관 규정 적용, 국내우대 "Not Applicable"). JV는 PPR 54(4) 연대책임 원칙(2008 규칙 기준).
- **[확인]** EDCL ERP EOI는 **QCBS·national firm·자체자금** → 외국 벤더는 현지 컨설팅사 컨소시엄/하도급 또는 **제품(라이선스) 공급자**로 참여하는 것이 현실적.
- **[추정]** 제안서 체크리스트: (a) e-GP 등록(외국기업 등록 수수료 체계), (b) 현지 파트너의 QCBS 기술점수 확보용 레퍼런스(제약 ERP·GxP 밸리데이션), (c) Bangla UI·Mushak 6.3 전자발행·회계연도 7-6월·BDT lakh/crore 표기, (d) 국내 호스팅(NDC Kaliakoir 또는 온프레미스) 옵션, (e) 정전 대응 아키텍처, (f) PIC/S PI 041 기반 데이터무결성·CSV 패키지(IQ/OQ/PQ, 감사추적, 전자서명), (g) WHO ML3·GMP 인증 지원 KPI.

### 6.2 ODA·개발금융 트랙
| 재원 | 내용 | 시사점 |
|---|---|---|
| **ADB Loan 4388-BAN(US$336.5M, 2023-11-28)** | EDCL 백신·치료제·진단 제조 + DGDA ML3; 2026.6 마감 입찰(다카 관리실험실·훈련센터 설계·감리, GTAI 게재) | **ADB 조달(국제경쟁) 적용 → 외국 벤더 참여 가능.** GMP 디지털(MES/LIMS/QMS/EDMS/시리얼) 패키지가 포함될 가능성 → ADB 조달계획 모니터링 필수 | [확인/추정] |
| **World Bank** P180283 HNP PforR($379M+$25M, ~2029.6), 2025.4 $570M(보건 $515M + 조달 디지털 $55M) | 공공조달 디지털화·보건 PforR | 간접(EDCL 직접 수혜 미확인) |
| **Korea EDCF** 프레임워크 **US$3B(2023-27)**, 40년 상환·15년 거치·0.01~0.05% | 서명 당시 CNG버스·철도신호, MRT-4 MoU; 2단계 BSMMU 초전문병원($200M) 후보; EDCF는 **한국 기업 참여 조건**(tied) | **보건·제약 EDCF 사업은 아직 없음** → "EDCL GMP 공장/디지털화"를 EDCF 후보사업으로 ERD에 제안하는 것이 장기 전략 옵션 | [확인/추정] |
| **KOICA** 누적 $172M+; **2026-28 신규 $96M(5개 사업: 간호교육연구원 $5.9M, 통계 DW·빅데이터 $9.65M, 디지털보안 등)**; Rangpur 모자보건 $10M; 2014 e-Gov 마스터플랜 | 보건·디지털 역량 사업 경험 → DGDA 규제 IT/EDCL 디지털 역량 TA(기술협력) 제안 소재 | [확인] |
| **EDPF(경협증진자금) US$3B(2023, 5년)** | 시장성 재원, 대형 인프라 중심 | 제약 적합성 낮음 | [확인] |

### 6.3 한-방글라데시 제약 협력 현황
- **[확인]** 2021.6 Hasina 총리–한국: 백신 생산시설 협력 논의(3개 현지사 검증); 2021 주한 방글라데시대사관 주최 회의에서 제약·바이오·ICT를 우선 협력분야로 지정; 한국 투자단 중 1인이 API 공장 관심 표명(후속 미확인).
- **[불확실]** **한국 제약사의 방글라데시 법인·공장·공식 MoU, KPBMA·KHIDI 협력 사례는 검색에서 확인되지 않음.** 한국 IT기업(삼성SDS·LG CNS·KT)의 방글라데시 정부 프로젝트도 미확인. 외국 벤더 선례는 베트남 FPT IS(SAP)가 가장 가까움.
- **[확인]** 외국 제약사의 DGDA 제품등록은 **현지 공인 에이전트 지정** 필요(컨설팅사 자료, 공식 미확인), 등록 12~36개월.

### 6.4 리스크·유의사항(추정 포함)
1. **정치 일정**: 2024.8 과도정부 수립 이후 정책 재검토(Smart Bangladesh, a2i 조사, ICT 백서 삭제 등). 2026년 선거 이후 정부에서 EDCL 입지·투자계획 재변경 가능.
2. **거버넌스 리스크**: EDCL의 Tk 477 crore 감사지적·ACC 조사 → 투명성 기능이 제안의 핵심이자, 계약 상대방 리스크 관리(실소유자 공개, 제재위원회) 필요.
3. **재원 리스크**: ERP는 자체자금(EDCL 수익성 불명) → 단계적 결제·결과 연동 설계 권장; 백신 트랙은 ADB 재원으로 안정적.
4. **인프라**: 정전·가스위기 → 하이브리드/오프라인 내성; 국내 호스팅 선호.
5. **규제 변동**: DGDA ML3 추진(2027.5), LDC 졸업(2026.11), Finance Bill 2026 e-invoicing, 데이터보호령 개정 — ERP 설계에 변경관리 여지 확보.

---

## 7. 제안서 반영을 위한 핵심 포인트 (조사자 추정)
- **포지셔닝**: "EDCL ERP(진행 중 EOI)의 GMP 계층 보완 파트너" + "ADB 백신공장의 디지털 GMP(MES/EBR/LIMS/QMS/시리얼) 공급자" + "DGDA ML3·WHO GMP 인증 달성 지원" 3축.
- **차별화 요소**: PIC/S PI 041 데이터무결성 패키지, GS1 시리얼라이제이션 준비, Mushak 6.3 전자발행·e-GP 연계, Bangla UI, 정전 내성 아키텍처, 국내 소버린 클라우드(Oracle Dedicated Region) 호환, 조달 투명성 대시보드(감사 대응).
- **파트너링**: Odoo/로컬 ERP 파트너(Metamorphosis, VS ONE 등) 또는 Big4 현지법인과 컨소시엄; 한국 측은 EDCF/KOICA 후보사업화(ERD·MoHFW 협의) 병행.
- **검증 필요 사항(원문 확인 리스트)**: EDCL ERP EOI 결과(BPPA details-10604 및 후속 RFP), ADB 4388-BAN 조달계획, PPR 2025의 ICB·외국기업 조항, DGDA 최신 GMP/CSV 가이드라인, 개인정보보호령 2026.1 개정 원문, EDCL 연차보고서(매출·인력).

---

## Sources (URL 목록)

### EDCL
- https://en.wikipedia.org/wiki/Essential_Drugs_Company
- https://www.tbsnews.net/node/397750 (Lone state-owned drugmaker gets Tk1,905cr revamp)
- https://www.tbsnews.net/node/192190 (An essential drug supplier in neglect for a decade)
- https://edcl.portal.gov.bd/site/page/da45deea-a211-4804-8996-f6db8c327006/-
- https://edcl.portal.gov.bd/site/project/f8ddef2b-6236-40bc-9e7c-9e9a671218b8/nolink/-
- https://mccibd.org/?p=5506
- https://www.developmentaid.org/organizations/view/5188/essential-drugs-company-limited
- https://thefinancialexpress.com.bd/print/edcl-to-be-largest-medicine-manufacturer-in-south-asia-1535815798
- https://old.thefinancialexpress.com.bd/print/new-factory-of-essential-drugs-to-open-in-july-1528286962
- https://www.jagonews24.com/special-reports/news/116599
- https://observerbd.com/news/589801 (BAPI asks govt to let EDCL produce essential medicines, Aug 2026)
- https://www.observerbd.com/news/540728 (EDCL irregularities / new management, 2025-26)
- https://www.banglanews24.com/english/health/news/bd/183269.details (Sirajdikhan site, Aug 2025)
- https://www.dhakatribune.com/bangladesh/389167/nurjahan-edcl-to-set-up-vaccine-anti-venom
- https://thefinancialexpress.com.bd/health/edcl-to-set-up-vaccine-and-anti-venom-plant-in-munshiganj
- https://www.tbsnews.net/bangladesh/mou-signed-us-company-set-first-ever-vaccine-producing-plant-country-654034
- https://www.dhakatribune.com/bangladesh/314018/mou-signed-with-us-company-to-set-up-first-ever
- https://thesun.my/world-news/bangladesh-to-set-up-1st-ever-vaccine-manufacturing-facility-IC11136781
- https://www.bssnews.net/special-stories/385756/print (EDCL to produce measles, dengue vaccines, May 2026)
- https://en.ittefaq.com.bd/16491/edcl-to-produce-measles-dengue-vaccines
- https://thefinancialexpress.com.bd/health/prices-of-33-essential-medicines-reduced-by-up-to-50pc
- https://bangla.thedailystar.net/news/bangladesh/news-692891
- https://www.prothomalo.com/bangladesh/18bo57bbin
- https://www.khoborsangjog.com/95884 (এসেনসিয়াল ড্রাগসে পরিবর্তনের ছোঁয়া)
- https://www.jagonews24.com/special-reports/news/115597
- https://www.dhakatribune.com/opinion/editorial/73103/stop-abuse-of-govt-drug-monopoly
- https://thefinancialexpress.com.bd/national/hc-orders-acc-to-inquire-anomalies-of-tk-477b-in-essential-drugs
- https://en.prothomalo.com/bangladesh/govt-drug-company-edcl-rife-with-irregularities-and-corruption
- https://bangla.thedailystar.net/news/bangladesh/crime-justice/news-459671
- https://bangla.thedailystar.net/news/bangladesh/news-491881
- https://www.prothomalo.com/bangladesh/pss85fwp3k
- https://www.thedailystar.net/news/bangladesh/news/rejoinder-our-reply-3365886

### EDCL ERP EOI (BPPA)
- https://www.bppa.gov.bd/advertisement-services/details-10604.html
- https://bangla.bppa.gov.bd/advertisement-services/details-10604.html
- https://bidsfactory.com/en/tenders/design-development-implementation-of-an-enterprise-bppa-39c0162cb946909f
- https://www.bppa.gov.bd/advertisement-goods/details-97089.html
- https://www.bppa.gov.bd/advertisement-goods/details-81614.html

### ADB 백신·규제 프로젝트 / DGDA
- https://www.dhakatribune.com/bangladesh/health/332386/adb-to-lend-336.5-million-to-bangladesh-to-help
- https://www.observerbd.com/news/448283
- https://events.development.asia/system/files/materials/2024/10/202410-adbs-initiatives-support-vaccine-manufacturing_0.pdf
- https://www.adb.org/sites/default/files/linked-documents/56289-001-ld-01.pdf
- https://www.adb.org/publications/regulatory-ecosystem-vaccines-bangladesh
- https://www.adb.org/sites/default/files/publication/972451/adb-brief-302-regulatory-ecosystem-vaccines-bangladesh.pdf
- https://www.gtai.de/de/trade/bangladesch/ausschreibungen-projekte/consulting-planung-bauueberwachung-medizin--2002182
- https://www.tbsnews.net/node/1304981 (Bangladesh's vaccine export dreams on hold over WHO certification)
- https://www.who.int/bangladesh/activities/strengthening-national-regulatory-authority
- https://www.who.int/bangladesh/news/detail/01-11-2021-coalition-of-interested-partners-for-medicines-regulatory-affairs-meeting
- https://www.who.int/bangladesh/news/detail/08-11-2016-training-workshop-concludes-on-regulatory-inspections-to-ensure-good-manufacturing-practices-(gmp)-in-medicine-and-vaccine-production-in-bangladesh
- https://www.who.int/publications/m/item/list-of-nras-operating-at-ml3-and-ml4
- https://www.parexel.com/insights/blog/pics-expansion-continues-what-does-mean-manufacturers-those-countries-seeking-join
- https://leap.unep.org/en/countries/bd/national-legislation/drugs-and-cosmetics-act-2023-act-no-29-2023
- https://www.tbsnews.net/node/1271906 (pharma industry moves from import dependence to global prominence)
- https://www.pmda.go.jp/files/000229073.pdf
- https://storage.mtender.gov.md/get/0435b701-3a58-4bb3-a823-b6fb126819a8-1756898257558 (Incepta WHO-format GMP certificate 2025)

### 산업 개요·수출·API·LDC
- https://bdnews24.com/business/515zckldx9 (exports $238.5M FY2025-26)
- https://www.tbsnews.net/features/panorama/can-bangladeshs-pharma-sector-close-its-api-amid-supply-chain-shock-1401956
- https://www.thedailystar.net/business/news/big-duty-cuts-power-api-supply-chain-pharma-leaders-4207406
- https://www.thedailystar.net/business/news/govt-finalise-handover-api-park-plots-3938846
- https://www.tbsnews.net/node/953121
- https://bd.linkedin.com/in/rafsun-hasmy (IQVIA 1Q 2026 summary)
- https://bd.linkedin.com/in/nasrat-bin-shawkat-65008867
- https://www.thedailystar.net/business/news/the-end-exemption-3953556
- https://tralac.org/publications/article/16326-bangladesh-s-upcoming-graduation-from-ldc-status-ongoing-use-of-the-wto-trips-flexibilities.html
- https://rapidbd.org/wp-content/uploads/2025/01/Final_Policy-Brief-LDC-Graduation-Impact-on-Pharmaceutical_110125-1.pdf
- https://www.tbsnews.net/bangladesh/health/medicine-prices-wont-rise-after-ldc-graduation-rapid-1000541
- https://en.ittefaq.com.bd/11935/ldc-graduation-achievements-amidst-emerging
- https://www.tbsnews.net/node/1028586
- https://www.tbsnews.net/node/494706
- https://unb.com.bd/category/Bangladesh/post-ldc-bangladesh-pharmaceutical-experts-for-amendment-of-patent-act-2022/98603
- https://www.jagonews24.com/en/biz-econ/news/93336 (FY2026-27 budget)
- https://bdnews24.com/budget2026-27/6a1dcac6ad7d
- https://lightcastlepartners.com/insights/2025/07/bangladesh-fy26-budget-analysis/

### 상위 기업 인증·ERP
- https://en.wikipedia.org/wiki/Incepta_Pharmaceuticals
- https://www.beximco.com/news/beximco-pharma-gets-us-fda-approval
- https://www.biospace.com/beximco-pharmaceuticals-receives-us-fda-approval-to-manufacture-blood-pressure-drug-carvedilol
- https://www.thedailystar.net/node/101971
- https://www.observerbd.com/news.php?id=467371
- https://intuitionlabs.ai/companies/pharma/renata-plc
- https://antaresvisiongroup.com/lifescience/2024/09/24/renata-plc-and-antares-vision-group-revolutionizing-pharma-traceability-in-bangladesh/
- https://usp.org/node/190971 (ACI WHO PQ azithromycin)
- https://extranet.who.int/prequal/sites/default/files/whopar_files/HA668part7v3.pdf
- https://extranet.who.int/prequal/sites/default/files/whopar_files/DI013part7v2.pdf
- https://bd.linkedin.com/in/shamimsarwar ; https://bd.linkedin.com/in/palash-mallik-b9b38b2b ; https://bd.linkedin.com/in/m-a-arshad-bhuiyan (Beximco Oracle EBS / Incepta SAP, 2차)
- https://journal.bauet.ac.bd/exploring-the-adoption-and-challenges-of-industry-4-0-in-pharmaceutical-industries-of-bangladesh/
- https://ideas.repec.org/a/aif/journl/v42y2024i1p71-83.html
- https://ideas.repec.org/a/ibn/ijbmjn/v16y2023i11p1.html

### GMP 집행 이력
- https://www.thedailystar.net/frontpage/low-quality-drug-production-ban-stays-20-drug-companies-1360867
- https://www.thedailystar.net/frontpage/govt-revokes-licences-11-companies-1239745
- https://www.thedailystar.net/backpage/substandard-antibiotics-hc-upholds-ban-production-28-companies-1386043
- https://www.outsourcing-pharma.com/Article/2016/08/08/Bangladesh-Court-orders-34-drug-firms-to-halt-production-again
- https://mail.hrpb.org.bd/public/images/judgement/writ-petition-no.-6969-of-2016---stop-operation-of-producing-antibiotic-by--20-pharmaceuticals.pdf
- https://www.dhakatribune.com/bangladesh/314037/health-minister-licenses-of-45-pharmaceutical
- https://picscheme.org/users_uploads/news_news_documents/PI_041_1_Draft_2_Guidance_on_Data_Integrity_2.pdf

### 디지털 정책·데이터·인프라·세무
- https://www.dhakatribune.com/amp/opinion/op-ed/412581/the-fy2026-27-digital-agenda
- https://dig.watch/countries/Bangladesh
- https://meatechwatch.com/2025/04/14/bangladesh-to-revamp-ict-and-telecom-policies-to-drive-digital-growth-by-june/
- https://ppc.land/bangladesh-finalizes-comprehensive-data-protection-ordinance-draft/
- https://itif.org/publications/2025/05/16/bangladesh-cross-border-data-transfer-regulation/
- https://www.thedailystar.net/opinion/views/news/new-data-regulations-warrant-urgent-rethinking-4016156
- https://www.thedailystar.net/news/data-frontiers-where-does-bangladesh-fit-the-global-privacy-debate-4085556
- https://www.tbsnews.net/node/642186
- https://www.datacenterdynamics.com/en/news/bangladeshs-first-cloud-data-center-starts-operations/
- https://bdccl.portal.gov.bd/site/page/67840a7f-f0b4-49e3-be1c-5c9c6e7e5e4e/-
- https://unb.com.bd/category/Bangladesh/oracle-to-provide-sovereign-hosted-cloud-services-to-government/84534
- https://www.datacentermap.com/bangladesh/dhaka/iv-tier-national-data-center/
- https://asianews.network/bangladesh-gas-crisis-ripples-across-economy/
- https://en.ittefaq.com.bd/17599/worsening-gas-shortage-threatens-exports-disrupts
- https://www.dhakatribune.com/bangladesh/power-energy/421625/thirty-five-power-plants-shut-load-shedding-hits
- https://today.thefinancialexpress.com.bd/print/counting-the-cost-of-load-shedding-1786978533
- https://datareportal.com/reports/digital-2026-bangladesh
- https://www.trade.gov/country-commercial-guides/bangladesh-digital-economy
- https://blog.apnic.net/2025/11/03/bangladeshs-internet-transformation-from-satellite-shadows-to-digital-highways/
- https://www.vatupdate.com/2026/08/28/bangladesh-e-invoicing-e-reporting-country-booklet/
- https://ecosire.com/apps/erpnext/erpnext-bangladesh-vat-mushak
- https://rakibhassan.eu/vat-on-medicine-bangladesh/

### 조달(PPR 2025, e-GP)
- https://today.thefinancialexpress.com.bd/print/government-issues-ppr-2025-1759258813
- https://bppa.gov.bd/media-communication/news-1517.html
- https://bppa.gov.bd/media-communication/news-1531.html
- https://www.thedailystar.net/business/news/procurement-law-revised-cut-graft-boost-transparency-3902466
- https://www.thedailystar.net/business/news/competition-govt-purchase-rises-after-new-rules-4073306
- https://www.tbsnews.net/node/1305721
- https://today.thefinancialexpress.com.bd/print/use-of-e-gp-made-mandatory-1763574795
- https://www.bssnews.net/business/347805
- https://events.development.asia/system/files/materials/2024/12/202412-recent-updates-e-gp-system-bangladesh.pdf
- https://www.bppa.gov.bd/media-communication/news-1303.html
- https://www.cptu.gov.bd/faq.html
- https://cdn3.ogrlegal.com/files/public-procurement/other/Public-Procurement-Rules-2008-English.pdf
- https://supremecourt.gov.bd/resources/documents/2583875_W.P.No.8501of2023(CPTU-Matter-do).pdf
- https://dspace.bracu.ac.bd/items/23f459cf-47c7-438d-b070-9b2d5d3b2840

### 공공부문 ERP 선례 / 현지 파트너
- https://fpt.com/en/news/fpt-news/fpt-is-wins-another-usd-8-8-million-erp-contract-in-bangladesh
- https://fpt-is.com/en/customers/providing-and-installation-of-erp-eam-software-for-power-generation-company-of-bangladesh-egcb/
- https://fpt.com/en/news/fpt-news/signing-the-biggest-overseas-erp-contract-for-vietnam
- https://fpt.com/en/news/fpt-is-operates-the-largest-erp-project-in-the-foreign-market
- https://www.odoo.com/partners/metamorphosis-ltd-1132898
- https://odoo.com/partners/vs-one-bangladesh-ltd-15116171
- https://www.erpresearch.com/odoo-partners/xsellence-bangladesh-limited
- https://www.odoo.com/customers/alchem-enterprise-15601563
- https://www.prismerp.net/about
- https://ibos.io/top-10-best-performing-erp-software-in-bangladesh

### 벤치마크
- https://repository.telkomuniversity.ac.id/pustaka/files/197694/bab1/analysis-successfull-factor-of-implementation-enterprise-resource-planning-using-tam-study-case-pt-kimia-farma-persero-.pdf
- https://ojs3.unismuh.ac.id/index.php/invoice/article/view/14362
- https://finansial.bisnis.com/read/20240708/90/1780488/anggota-dpr-soroti-rencana-restrukturisasi-kimia-farma-kaef-bni-beri-tanggapan
- https://biofarma.co.id/media/file/originals/undefined/2024/09/12/peraturan-keputusan-kebijakan.pdf
- https://market.bisnis.com/read/20260129/192/1948220/danantara-rombak-holding-farmasi-kimia-farma-kaef-dilepas-dari-bio-farma
- https://biofarma.co.id/en/latest-news/download/bio-farma-and-google-cloud-indonesia-agree-on-the-mou-for-cooperation-in-healthcare-digital-transformation
- https://www.sbm.itb.ac.id/?p=53853
- https://www.sustainabilityreports.com/egyptian-international-pharmaceutical-industries/2021/annual-report
- https://www.forbesmiddleeast.com/lists/egypts-50-most-valuable-companies-2026/egyptian-international-pharmaceutical-industries-company-eipico/
- https://vneconomy.vn/dai-hoi-co-dong-vinapharm-tra-co-tuc-10-len-ke-hoach-niem-yet-tren-hose.htm
- https://baodautu.vn/doi-moi-sang-tao---hanh-trinh-moi-cua-vinapharm-d201709.html
- https://fpt.com/en/news/genfarma-and-fpt-go-live-with-sap-s4hana-public-cloud-in-just-two-months
- https://newsfirst.lk/2026/01/04/state-pharmaceuticals-to-introduce-10-new-drugs-this-year
- https://dailymirror.lk/other/spmc-an-asset-to-the-pharmaceutical-industry-of-sri-lanka/117-87829
- https://www.naewna.com/lady/427857 ; https://www.matichon.co.th/local/news_1552609 (Thailand GPO Rangsit)
- https://kathmandupost.com/money/2016/09/20/work-begins-to-revive-nepal-drug-limited
- https://thehimalayantimes.com/opinion/editorial-new-lease-life-nepal-drugs-ltd/
- https://medicaldialogues.in/government-will-make-efforts-to-revive-the-pharma-psu
- https://theprint.in/economy/indias-drug-maker-help-modi-govt-revive-penicillin-production/302164/
- https://www.pharma-dept.gov.in/karnataka-antibiotics-pharmaceuticals-limited
- https://www.howwemadeitinafrica.com/p/doctor-turned-entrepreneur-bullish-about-ethiopia-039-s-healthcare-sec
- https://ethiopianembassy.be/?p=13225
- https://arynews.tv/pakistan-to-launch-track-trace-system-to-combat-fake-medicines
- https://newsonair.gov.in/health-ministry-expands-qr-code-based-track-and-trace-framework-for-medicines/

### 한국·ODA·개발금융
- https://www.dhakatribune.com/amp/bangladesh/foreign-affairs/310379/bangladesh-s-korea-sign-3bn-edcf-deal-for
- https://www.tbsnews.net/node/626242
- https://www.thedailystar.net/news/bangladesh/diplomacy/news/bangladesh-get-3b-concessional-loans-south-korea-3311091
- https://www.thedailystar.net/business/economy/news/s-korea-offers-700m-development-projects-2205546
- https://en.prothomalo.com/bangladesh/korea-to-provide-700m-of-edcf-loan-to-bangladesh
- https://www.tbsnews.net/node/563850
- https://www.tbsnews.net/node/1215296
- https://www.tbsnews.net/node/1300496 (KOICA $96M, 2026-28)
- https://www.banglanews24.com/english/national/news/bd/186137.details
- https://www.tbsnews.net/node/232801
- https://thefinancialexpress.com.bd/views/30-years-of-koica-in-bangladesh-1618065342
- https://en.prothomalo.com/science-technology/it/E-govt-master-plan-digital-municipality-service
- https://www.tbsnews.net/node/1043041
- https://www.asianews.it/en/south-asia/bangladesh/hasina-s-korea-to-help-bangladesh-build-a-vaccine-production-facility
- https://unb.com.bd/category/bangladesh/dhaka-seoul-take-stock-of-bilateral-relations-3-sectors-identified-for-more-focused-cooperation/73972
- https://www.jagonews24.com/en/biz-econ/news/81762
- https://dealsite.co.kr/articles/100875 (EDPF US$3B)
- https://projects.worldbank.org/en/projects-operations/project-detail/P180283
- https://www.globalfinancingfacility.org/fr/news/press-release/world-bank-provides-570-million-improve-bangladeshs-health-sector-and-public
- https://cpd.org.bd/dr-fahmida-recommends-increasing-domestic-funding-for-health-services/
- https://taevasglobal.com/bangladesh/pharmaceuticals/legal-representation
