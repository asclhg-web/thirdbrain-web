#!/usr/bin/env python3
"""Odoo 본사 미팅용 슬라이드 5~8 (표지 4대 키워드) 풀슬라이드 그래픽 생성.
덱 판형 10.84x7.5in → 1301x900 px."""
import os, cairosvg

OUT = os.path.dirname(os.path.abspath(__file__))
F = "NanumGothic"
NAVY = "#1E2761"; BLUE = "#1CA5E5"; ICE = "#E8F0FB"; ICE2 = "#CADCFC"
TEAL = "#028090"; TEALBG = "#E5F4F3"; GRAY = "#5A6472"; LGRAY = "#EEF1F5"
ACC = "#B85042"; YELLOW = "#FFDD2D"; WHITE = "#FFFFFF"; INK = "#111111"
W, H = 1301, 900

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def text(x, y, s, size=15, fill=NAVY, w="normal", anchor="middle"):
    return (f'<text x="{x}" y="{y}" font-family="{F}" font-size="{size}" '
            f'font-weight="{w}" fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>')

def multi(x, y, lines, size=13, fill=GRAY, lh=None, anchor="middle", w="normal"):
    lh = lh or size + 5
    return "".join(text(x, y + i*lh, s, size, fill, w, anchor) for i, s in enumerate(lines))

def rrect(x, y, w, h, fill, stroke=NAVY, sw=1.5, r=10, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

DEFS = (f'<defs><marker id="ah" markerWidth="10" markerHeight="8" refX="8" refY="4" orient="auto">'
        f'<path d="M0,0 L9,4 L0,8 z" fill="{NAVY}"/></marker>'
        f'<marker id="ahT" markerWidth="10" markerHeight="8" refX="8" refY="4" orient="auto">'
        f'<path d="M0,0 L9,4 L0,8 z" fill="{TEAL}"/></marker>'
        f'<marker id="ahA" markerWidth="10" markerHeight="8" refX="8" refY="4" orient="auto">'
        f'<path d="M0,0 L9,4 L0,8 z" fill="{ACC}"/></marker></defs>')

def arrow(x1, y1, x2, y2, color=NAVY, sw=2, marker="ah", dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{sw}" marker-end="url(#{marker})"{d}/>')

def header(num, title, en):
    b = [text(60, 74, f"{num}. {title}", 34, INK, "bold", anchor="start"),
         text(62, 104, en, 16, BLUE, anchor="start"),
         f'<line x1="60" y1="122" x2="{W-60}" y2="122" stroke="{BLUE}" stroke-width="3"/>',
         # ASC 워드마크
         text(W-60, 66, "ASC", 40, BLUE, "bold", anchor="end"),
         f'<path d="M{W-166},72 q50,14 106,2" stroke="{ACC}" stroke-width="3" fill="none"/>',
         text(W-63, 92, "AI System Creator", 12, ACC, anchor="end")]
    return "".join(b)

def kpi_row(items, y=826):
    b = []
    bw = 270; gap = 24
    x0 = (W - (bw*len(items) + gap*(len(items)-1))) / 2
    for i, t in enumerate(items):
        X = x0 + i*(bw+gap)
        b.append(rrect(X, y, bw, 46, NAVY, NAVY, 1, 23))
        b.append(text(X+bw/2, y+29, t, 15.5, WHITE, "bold"))
    return "".join(b)

def agentchain(x, y, w, labels, note):
    """에이전트 5종 미니 체인"""
    b = [text(x+w/2, y-10, "AI 에이전트 파이프라인 (상시 루프)", 15.5, TEAL, "bold")]
    bw = (w - 4*14) / 5
    for i, l in enumerate(labels):
        X = x + i*(bw+14)
        b.append(rrect(X, y, bw, 52, TEALBG, TEAL, 1.5, 10))
        b.append(multi(X+bw/2, y+22, l.split("|"), 13, NAVY, 18, w="bold"))
        if i < 4:
            b.append(arrow(X+bw+1, y+26, X+bw+13, y+26, TEAL, 2.2, "ahT"))
    b.append(rrect(x+w-118, y-32, 118, 24, ACC, ACC, 1, 12))
    b.append(text(x+w-59, y-16, "HITL 승인 게이트", 12, WHITE, "bold"))
    b.append(text(x+w/2, y+72, note, 12.5, GRAY))
    return "".join(b)

def slide(name, body):
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<rect width="{W}" height="{H}" fill="{WHITE}"/>' + DEFS + body + "</svg>")
    p = os.path.join(OUT, name + ".svg")
    open(p, "w").write(doc)
    cairosvg.svg2png(url=p, write_to=os.path.join(OUT, name + ".png"), scale=2.0)
    print("생성:", name)

# ── 슬라이드 5. 수요예측을 통한 영업 지능화 ─────────────────────
def s5():
    b = [header("1", "수요예측을 통한 영업 지능화", "Sales Intelligence via AI Demand Forecasting")]
    # 좌: 음성 RFM 시나리오
    b.append(rrect(60, 150, 560, 420, ICE, NAVY, 1.8, 14))
    b.append(text(340, 184, "현장 시나리오 — 말하면 5초 안에 예측까지", 19, NAVY, "bold"))
    steps = [("음성 주문 (마이크)", "“OO상사, 브래킷 A” — 거래처·상품명을 말한다"),
             ("문자 변환(STT)", "음성이 텍스트 데이터로 자동 변환"),
             ("자동 매칭", "거래처·제품 마스터에서 해당 레코드 탐색"),
             ("RFM 분석 (5초 이내)", "최근구매일 · 구매빈도 · 누적구매금액"),
             ("판매 예측·주문 제안", "RFM+이력 결합 예측 → 주문 명세 지시")]
    for i, (t, sub) in enumerate(steps):
        y = 208 + i*70
        b.append(rrect(88, y, 504, 56, WHITE, BLUE if i != 3 else ACC, 1.6, 10))
        b.append(text(110, y+24, t, 16.5, NAVY, "bold", anchor="start"))
        b.append(text(110, y+45, sub, 13, GRAY, anchor="start"))
        if i < 4:
            b.append(arrow(340, y+57, 340, y+69, BLUE, 2.2))
    # 우: Odoo 프로세스
    b.append(rrect(660, 150, 581, 420, WHITE, NAVY, 1.8, 14))
    b.append(text(950, 184, "Odoo 표준 프로세스 — 파이프라인이 예측이 된다", 19, NAVY, "bold"))
    rows = [("CRM 파이프라인", "기회 카드 — 예상 수익 · AI 성공 확률"),
            ("예측 보고서", "예상 수익 × 확률 = 가중 수익(월별 전망)"),
            ("구간 예측 결합", "제품군 계층 ML 예측 + 파이프라인 신호"),
            ("공급 연계", "재주문 규칙 · MPS/MRP로 수요 신호 전달"),
            ("실적 검증", "MAPE 점검 → 다음 회전의 학습 재료")]
    for i, (t, sub) in enumerate(rows):
        y = 208 + i*70
        b.append(rrect(688, y, 524, 56, LGRAY, GRAY, 1.2, 10))
        b.append(text(710, y+24, t, 16, NAVY, "bold", anchor="start"))
        b.append(text(710, y+45, sub, 13, GRAY, anchor="start"))
        if i < 4:
            b.append(arrow(950, y+57, 950, y+69, GRAY, 2, "ah"))
    b.append(agentchain(120, 640, 1060,
        ["수집|Odoo·CRM", "예측|ML·구간", "검증|MAPE·규칙", "영업 액션|리드·판촉", "환류|오차 학습"],
        "M5 대회 실증: 외부 변수를 결합한 ML이 통계 기법 대비 22.4% 더 정확 (Makridakis et al., 2022)"))
    b.append(kpi_row(["예측 오차(MAPE) 20%↓", "예측 커버리지 확대", "지목 기회 전환율 ↑"]))
    slide("slide5_forecast", "".join(b))

# ── 슬라이드 6. 재고 최적화 및 생산계획 자동화 ──────────────────
def s6():
    b = [header("2", "재고 최적화 및 생산계획 자동화", "Inventory Optimization & Automated Production Planning")]
    # 좌: 계획 계층
    b.append(rrect(60, 150, 560, 420, ICE, NAVY, 1.8, 14))
    b.append(text(340, 184, "계획의 계층 — 수요에서 작업지시까지", 19, NAVY, "bold"))
    plan = [("판매계획 (년/분기/월)", "Mgmt Level"),
            ("수요예측 — 실적+파이프라인", "10.9 예측 신호"),
            ("생산계획 (월/주간) · 출하계획", "Planning Level — 조정 합의"),
            ("우선순위 결정 프로세스", "납기·여신·부하 규칙"),
            ("작업지시 자동 발행 (D, D+1, D+2)", "설비별 · 작업자별 — Execution")]
    for i, (t, sub) in enumerate(plan):
        y = 208 + i*70
        b.append(rrect(88, y, 504, 56, WHITE, BLUE if i != 4 else TEAL, 1.6, 10))
        b.append(text(110, y+24, t, 16, NAVY, "bold", anchor="start"))
        b.append(text(110, y+45, sub, 13, GRAY, anchor="start"))
        if i < 4:
            b.append(arrow(340, y+57, 340, y+69, BLUE, 2.2))
    # 우: 재고 정책 루프
    b.append(rrect(660, 150, 581, 420, WHITE, NAVY, 1.8, 14))
    b.append(text(950, 184, "재고 정책의 월간 회전 — 공식과 데이터의 결합", 19, NAVY, "bold"))
    inv = [("ABC-XYZ 자동 분류", "금액 × 수요 변동성의 9분면"),
           ("동적 안전재고·ROP 재계산", "수요 분포·리드타임 실적 기반 (구간 예측)"),
           ("검증 게이트", "재고 예산 상한 · 서비스 수준 · ±50% 급변 차단"),
           ("재주문 규칙·MPS 반영", "frePPLe 유한능력 시뮬레이션 비교 후 승인"),
           ("환류", "결품·과잉 실적 → 다음 달 재계산의 교사")]
    for i, (t, sub) in enumerate(inv):
        y = 208 + i*70
        b.append(rrect(688, y, 524, 56, LGRAY, GRAY if i != 2 else ACC, 1.4, 10))
        b.append(text(710, y+24, t, 16, NAVY, "bold", anchor="start"))
        b.append(text(710, y+45, sub, 13, GRAY, anchor="start"))
        if i < 4:
            b.append(arrow(950, y+57, 950, y+69, GRAY, 2))
    b.append(agentchain(120, 640, 1060,
        ["수요 신호|예측·수주", "정책 최적화|안전재고·ROP", "검증|예산·서비스", "계획 실행|MPS·frePPLe", "환류|결품·과잉"],
        "안정 품목은 재주문 규칙으로, 변동 품목은 MPS로 — 이원 운영이 정석 (EOQ·안전재고 공식 + M5 구간 예측)"))
    b.append(kpi_row(["재고회전율 ↑ · DIO ↓", "결품률 ↓ (서비스 유지)", "계획 준수율 ↑"]))
    slide("slide6_inventory", "".join(b))

# ── 슬라이드 7. IoT를 이용한 설비예지 지능화 ────────────────────
def s7():
    b = [header("3", "IoT를 이용한 설비예지 지능화", "Predictive Maintenance Intelligence with IoT")]
    # 좌: P-F 곡선
    b.append(rrect(60, 150, 560, 420, ICE, NAVY, 1.8, 14))
    b.append(text(340, 184, "P-F 곡선 — 예지의 시간 창", 19, NAVY, "bold"))
    b.append(f'<line x1="120" y1="500" x2="560" y2="500" stroke="{GRAY}" stroke-width="2"/>')
    b.append(f'<line x1="120" y1="220" x2="120" y2="500" stroke="{GRAY}" stroke-width="2"/>')
    b.append(f'<path d="M130,240 q180,10 250,120 q60,90 160,130" stroke="{NAVY}" stroke-width="4" fill="none"/>')
    b.append(f'<circle cx="330" cy="310" r="9" fill="{BLUE}"/>')
    b.append(text(330, 288, "P — 잠재 고장(징후 감지)", 14.5, BLUE, "bold"))
    b.append(f'<circle cx="540" cy="490" r="9" fill="{ACC}"/>')
    b.append(text(492, 522, "F — 기능 고장(정지)", 14.5, ACC, "bold"))
    b.append(rrect(330, 330, 200, 34, YELLOW, INK, 1.2, 8))
    b.append(text(430, 352, "예지 정비의 무대 (P→F 구간)", 13.5, INK, "bold"))
    b.append(arrow(345, 364, 480, 470, ACC, 2.5, "ahA", "6,4"))
    b.append(text(340, 420, "센서가 P를 앞당겨 잡을수록", 13.5, GRAY))
    b.append(text(340, 440, "정비를 계획할 시간 창이 넓어진다", 13.5, GRAY))
    b.append(multi(340, 545, ["사후 정비: 정지 손실 감수  ·  예방 정비: 과잉 교체 감수  ·  예지 정비: 최적점"],
                   13, NAVY, w="bold"))
    # 우: 예지 파이프라인
    b.append(rrect(660, 150, 581, 420, WHITE, NAVY, 1.8, 14))
    b.append(text(950, 184, "Odoo 유지보수·IoT 프로세스", 19, NAVY, "bold"))
    rows = [("설비 대장·정비 이력", "MTBF·MTTR 자동 산출 — 5축 고장코드가 라벨"),
            ("IoT 박스 수집", "진동·온도·전류·가동 시계열 (PLC·센서)"),
            ("이상 감지", "관리도 이탈 + ML 이상 점수 랭킹"),
            ("진단·예지", "고장 코드 후보 + 유사 사례·베테랑 조치 제시"),
            ("정비 오더 자동 생성", "생산 부하 낮은 시간대 제안 (frePPLe 조율)")]
    for i, (t, sub) in enumerate(rows):
        y = 208 + i*70
        b.append(rrect(688, y, 524, 56, LGRAY, GRAY if i != 4 else TEAL, 1.4, 10))
        b.append(text(710, y+24, t, 16, NAVY, "bold", anchor="start"))
        b.append(text(710, y+45, sub, 13, GRAY, anchor="start"))
        if i < 4:
            b.append(arrow(950, y+57, 950, y+69, GRAY, 2))
    b.append(agentchain(120, 640, 1060,
        ["센서 수집|IoT 박스", "이상 탐지|관리도·ML", "진단·예지|고장코드·RUL", "정비 액션|오더·일정", "환류|오탐도 라벨"],
        "병목·고액 설비부터 단계 도입 — 적중률 낮은 경보는 늑대 소년이 된다 (CBM: Jardine et al., 2006)"))
    b.append(kpi_row(["계획외 정지 시간 ↓", "MTBF ↑ · 예지 적중률", "OEE 가동률 회복"]))
    slide("slide7_pdm", "".join(b))

# ── 슬라이드 8. 기업의 노하우를 지식센터 지능화 ─────────────────
def s8():
    b = [header("4", "기업의 노하우를 지식센터 지능화", "Turning Corporate Know-how into Intelligent Knowledge")]
    # 좌: SECI 사이클
    b.append(rrect(60, 150, 560, 420, ICE, NAVY, 1.8, 14))
    b.append(text(340, 184, "SECI 나선 — 암묵지가 조직의 자산이 되는 길", 19, NAVY, "bold"))
    q = [("공동화", "현장의 경험 공유", 205, 250), ("표출화", "말이 문서가 된다", 475, 250),
         ("연결화", "문서가 지식망이 된다", 475, 420), ("내면화", "지식이 몸에 밴다", 205, 420)]
    for t, sub, x, y in q:
        hl = t == "표출화"
        b.append(rrect(x-105, y-48, 210, 96, WHITE if not hl else YELLOW, NAVY, 1.8, 12))
        b.append(text(x, y-10, t, 19, NAVY, "bold"))
        b.append(text(x, y+18, sub, 13.5, GRAY))
    b.append(arrow(315, 250, 365, 250, TEAL, 2.5, "ahT"))
    b.append(arrow(475, 303, 475, 367, TEAL, 2.5, "ahT"))
    b.append(arrow(365, 420, 315, 420, TEAL, 2.5, "ahT"))
    b.append(arrow(205, 367, 205, 303, TEAL, 2.5, "ahT"))
    b.append(multi(340, 500, ["최대 장벽: “쓸 시간이 없다”", "→ 초안은 AI가, 승인은 베테랑이 — “고칠 시간만 있으면 된다”"],
                   14.5, ACC, 23, w="bold"))
    b.append(text(340, 550, "(Nonaka & Takeuchi, 1995 — 표출화의 자동화가 지능화의 요체)", 12.5, GRAY))
    # 우: 지식 파이프라인
    b.append(rrect(660, 150, 581, 420, WHITE, NAVY, 1.8, 14))
    b.append(text(950, 184, "Odoo 지식센터 + RAG 프로세스", 19, NAVY, "bold"))
    rows = [("지식 수집", "회의 음성 AI 요약 · 현장 메모 · 메일 · CS 이력"),
            ("구조화·정돈", "문서 트리·템플릿 = 지식의 정위치·정품"),
            ("RAG 색인", "사내문서 검색증강 — 출처 병기 답변"),
            ("맥락 활용", "도면 열면 과거 불량 포인트·베테랑 메모 표시"),
            ("갱신·정리", "사용 통계 · 미사용 문서 빨간 패 → 온톨로지 씨앗")]
    for i, (t, sub) in enumerate(rows):
        y = 208 + i*70
        b.append(rrect(688, y, 524, 56, LGRAY, GRAY if i != 3 else BLUE, 1.4, 10))
        b.append(text(710, y+24, t, 16, NAVY, "bold", anchor="start"))
        b.append(text(710, y+45, sub, 13, GRAY, anchor="start"))
        if i < 4:
            b.append(arrow(950, y+57, 950, y+69, GRAY, 2))
    b.append(agentchain(120, 640, 1060,
        ["수집|녹취·메모", "구조화|AI 초안", "검증|중복·출처", "활용|RAG·push", "환류|통계·정리"],
        "읽히지 않는 천 건보다 매일 읽히는 백 건이 지능이다 — 축적은 온톨로지(PTGDA)의 텃밭이 된다"))
    b.append(kpi_row(["핵심 표준 문서화율 ↑", "RAG 답변 채택률", "신입 온보딩 기간 ↓"]))
    slide("slide8_knowledge", "".join(b))

s5(); s6(); s7(); s8()
print("완료")
