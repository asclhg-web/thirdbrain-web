#!/usr/bin/env python3
"""3순위 보조 도해 — 2부 13~17장 담당분 10점 (FIGURES_PLAN.md / FIGURES_SPEC.md 준수)."""
import math
from figlib import *

def ring_pos(cx, cy, R, n):
    return [(cx + R*math.cos(-math.pi/2 + i*2*math.pi/n),
             cy + R*math.sin(-math.pi/2 + i*2*math.pi/n)) for i in range(n)]

def ring_arrows(b, cx, cy, pos, off=95, bulge=38, color=TEAL, sw=3, marker="ahT"):
    n = len(pos)
    for i in range(n):
        x, y = pos[i]; nx, ny = pos[(i+1) % n]
        vx, vy = nx-x, ny-y; L = math.hypot(vx, vy)
        sx, sy = x + vx/L*off, y + vy/L*off
        ex, ey = nx - vx/L*off, ny - vy/L*off
        mx, my = (sx+ex)/2, (sy+ey)/2
        ox, oy = mx-cx, my-cy; OL = math.hypot(ox, oy)
        b.append(curve(sx, sy, mx+ox/OL*bulge, my+oy/OL*bulge, ex, ey, color, sw, marker))

# ── 그림 13-2. 제조 데이터 흐름 ────────────────────────────────
def fig_132():
    W, H = 980, 400
    steps = [
        ("수주", "판매 주문 확정", ["고객·품목·수량", "납기·수주 단가"]),
        ("MPS", "기준 생산 일정", ["기간별 생산 수량", "S&OP 합의 숫자"]),
        ("MRP", "소요량 전개", ["제조 주문·구매 제안", "자재 예약·부족 경보"]),
        ("작업 지시", "작업 주문 발행", ["공정별 지시·표준서", "라우팅·표준시간"]),
        ("태블릿 실적", "POP 실시간 수집", ["착수·완료 타임스탬프", "자재 소진·불량 코드"]),
        ("원가 확정", "로트 원가 산출", ["재료비+노무비+경비", "표준원가 대비 차이"]),
    ]
    b = [text(W/2, 40, "제조 데이터 흐름 — 수주에서 원가까지", 22, NAVY, "bold"),
         text(W/2, 66, "계획-실행-원가가 다섯 개의 섬이 아니라 하나의 흐름이 된다", 13, GRAY)]
    bw, gap, y0 = 142, 20, 96
    x0 = (W - (bw*6 + gap*5)) / 2
    for i, (t, sub, data) in enumerate(steps):
        X = x0 + i*(bw+gap); cx = X + bw/2
        fill = NAVY if i == 5 else (TEALBG if i == 4 else ICE)
        tc = WHITE if i == 5 else NAVY
        sc = ICE2 if i == 5 else GRAY
        b.append(rrect(X, y0, bw, 64, fill, TEAL if i == 4 else NAVY, 1.6, 9))
        b.append(text(cx, y0+26, t, 14, tc, "bold"))
        b.append(text(cx, y0+46, sub, 11, sc))
        if i < 5:
            b.append(arrow(X+bw+1, y0+32, X+bw+gap-1, y0+32, TEAL, 2.4, "ahT"))
        b.append(line(cx, y0+64, cx, y0+80, GRAY, 1))
        b.append(rrect(X, 176, bw, 60, ICE, TEAL, 1.1, 6))
        b.append(text(cx, 192, "발생 데이터", 11, TEAL, "bold"))
        b.append(multi(cx, 210, data, 11, GRAY, 16))
    c0, c5 = x0+bw/2, x0+5*(bw+gap)+bw/2
    b.append(curve(c5, 242, W/2, 300, c0, 244, ACC, 2.2, "ahA", "6,4"))
    b.append(text(W/2, 296, "실제 원가 → 다음 견적·계획의 환류", 12, ACC, "bold"))
    b.append(rrect(x0, 314, bw*6+gap*5, 40, NAVY, NAVY, 1.5, 8))
    b.append(text(W/2, 339, "단일 PostgreSQL — 여섯 지점 모두 같은 원장에 기록된다 (재입력·대사 없음)", 13.5, WHITE, "bold"))
    b.append(text(W/2, 384, "2부 13장 — 태블릿 터치 하나가 재공·원가·납기 예측을 동시에 갱신한다", 11.5, GRAY))
    svg("fig_132_mfg_flow", W, H, "".join(b))

# ── 그림 13-3. 간트 + 병목 하이라이트 ──────────────────────────
def fig_133():
    W, H = 960, 500
    b = [text(W/2, 38, "frePPLe 유한능력 일정 — 병목 워크센터가 리듬을 정한다", 21, NAVY, "bold"),
         text(W/2, 62, "무한능력 가정을 벗어나, 워크센터의 능력을 제약으로 놓고 작업을 배치한다 (화면 도식)", 12.5, GRAY)]
    x0, x1 = 190, 845; dw = (x1-x0)/5
    y0, rh = 118, 54
    days = ["월", "화", "수", "목", "금"]
    for i, d in enumerate(days):
        b.append(text(x0+dw*(i+0.5), 104, d, 12.5, GRAY, "bold"))
    b.append(line(x0, 112, x1, 112, GRAY, 1.2))
    rows = [
        ("절단", [(0.05, 0.85, "WO-311"), (1.1, 1.9, "WO-314"), (3.0, 3.75, "WO-318")], "64%", False),
        ("용접", [(0.35, 1.25, "WO-312"), (1.5, 2.3, "WO-315"), (3.4, 4.25, "WO-319")], "71%", False),
        ("CNC 가공", [(0.02, 0.98, "WO-301"), (1.02, 1.98, "WO-302"), (2.02, 2.98, "WO-303"),
                      (3.02, 3.98, "WO-304"), (4.02, 4.95, "WO-305")], "96%", True),
        ("조립", [(0.9, 1.55, "WO-313"), (2.25, 3.05, "WO-316"), (4.0, 4.65, "WO-320")], "58%", False),
        ("검사", [(1.3, 1.75, ""), (3.0, 3.45, ""), (4.35, 4.8, "")], "45%", False),
    ]
    b.append(multi(898, 96, ["주간", "부하율"], 11, GRAY, 14))
    for r, (name, bars, util, neck) in enumerate(rows):
        Y = y0 + r*rh
        if neck:
            b.append(rrect(x0, Y, x1-x0, rh, "#F9EAE7", ACC, 1.5, 4))
        b.append(line(x0, Y+rh, x1, Y+rh, "#D5DAE1", 1))
        if neck:
            b.append(text(50, Y+22, name, 13, NAVY, "bold", "start"))
            b.append(text(50, Y+40, "★ 병목", 11, ACC, "bold", "start"))
        else:
            b.append(text(50, Y+32, name, 13, NAVY, "bold", "start"))
        for s, e, lab in bars:
            bx, bw2 = x0+s*dw, (e-s)*dw
            b.append(rrect(bx, Y+13, bw2, 28, ACC if neck else TEAL,
                           "#8B3A30" if neck else "#01677A", 1, 5))
            if lab and bw2 >= 62:
                b.append(text(bx+bw2/2, Y+31, lab, 11, WHITE, "bold"))
        b.append(text(898, Y+33, util, 13.5, ACC if neck else TEAL, "bold"))
    for i in range(6):
        b.append(line(x0+i*dw, 112, x0+i*dw, y0+5*rh, "#C6CCD5", 0.8, "2,3"))
    b.append(text(W/2, 412, "병목 CNC 가공: 부하율 96% — 병목의 1시간이 공장 전체의 1시간이다 (TOC)", 13, ACC, "bold"))
    b.append(rrect(292, 428, 16, 12, TEAL, TEAL, 0, 2))
    b.append(text(316, 438, "일반 워크센터 작업", 11.5, GRAY, anchor="start"))
    b.append(rrect(510, 428, 16, 12, ACC, ACC, 0, 2))
    b.append(text(534, 438, "병목 워크센터 작업", 11.5, GRAY, anchor="start"))
    b.append(text(W/2, H-14, "frePPLe는 셋업 그룹·능력 제약을 반영해 작업 순서를 최적화한다 — 2부 13장·16장", 11.5, GRAY))
    svg("fig_133_gantt_neck", W, H, "".join(b))

# ── 그림 14-1. "입력 없는 회계" 자동화 파이프라인 ──────────────
def fig_141():
    W, H = 940, 480
    b = [text(W/2, 40, "“입력 없는 회계” — 자동화 파이프라인", 22, NAVY, "bold"),
         text(W/2, 66, "입력은 AI가, 승인은 사람이 — 기록 노동이 판단 노동으로 바뀐다", 13.5, GRAY)]
    b.append(rrect(250, 95, 440, 56, ICE, NAVY, 1.5, 10))
    b.append(text(W/2, 118, "사람의 일 = 승인·판단", 14, NAVY, "bold"))
    b.append(text(W/2, 140, "자동 생성된 전표·대사 결과를 검토하고 승인만 한다", 11.5, GRAY))
    stages = [
        ("증빙 발생", "현장·수신함", ["청구서 스캔·사진", "이메일 수신"], LGRAY, GRAY),
        ("AI 캡처", "인식률 98%", ["공급업체·금액·세액 추출", "전표 초안 0.1초"], TEALBG, TEAL),
        ("은행 자동 대사", "자동 매칭 95%", ["28,000개 은행 연동", "입출금 ↔ 청구서 대조"], TEALBG, TEAL),
        ("실시간 보고", "마감 대기 없음", ["손익·현금·채권 연령", "드릴다운 즉시 조회"], NAVY, NAVY),
    ]
    bw, gap, y0 = 196, 36, 200
    x0 = (W - (bw*4 + gap*3)) / 2
    for i, (t, badge, lines, fill, stroke) in enumerate(stages):
        X = x0 + i*(bw+gap); cx = X + bw/2
        solid = (fill == NAVY)
        b.append(rrect(X, y0, bw, 112, fill, stroke, 1.6, 10))
        b.append(text(cx, y0+26, t, 14, WHITE if solid else NAVY, "bold"))
        b.append(text(cx, y0+48, badge, 12, ICE2 if solid else TEAL, "bold"))
        b.append(multi(cx, y0+72, lines, 11.5, ICE2 if solid else GRAY, 20))
        if i < 3:
            b.append(arrow(X+bw+2, y0+56, X+bw+gap-2, y0+56, TEAL, 2.6, "ahT"))
    c2, c3 = x0+bw+gap+bw/2, x0+2*(bw+gap)+bw/2
    b.append(arrow(c2, 153, c2, y0-4, NAVY, 1.8, "ah", "5,4"))
    b.append(arrow(c3, 153, c3, y0-4, NAVY, 1.8, "ah", "5,4"))
    b.append(text((c2+c3)/2, 178, "승인 게이트", 11.5, NAVY, "bold"))
    b.append(rrect(140, 350, 660, 58, ICE, NAVY, 1.4, 10))
    b.append(text(W/2, 374, "KPMG: 부가세 결산 4일 → 3시간", 13.5, NAVY, "bold"))
    b.append(text(W/2, 396, "절감된 시간은 인력 감축이 아니라 판단 노동으로 재투자된다 (Odoo 공식 소개자료)", 11.5, GRAY))
    b.append(text(W/2, 440, "AI 캡처의 전표 초안도 승인 게이트를 반드시 거친다 — 98%는 2%의 오류를 뜻한다", 12, GRAY))
    b.append(text(W/2, H-14, "2부 14장 — 회계: 재무의 컨설팅", 11.5, GRAY))
    svg("fig_141_no_input_acct", W, H, "".join(b))

# ── 그림 14-2. 현금전환주기(CCC) 타임라인 ──────────────────────
def fig_142():
    W, H = 920, 480
    b = [text(W/2, 40, "현금전환주기(CCC) — 현금은 며칠 잠겨 있는가", 22, NAVY, "bold"),
         text(W/2, 66, "CCC = 재고일수(DIO) + 채권일수(DSO) − 채무일수(DPO)", 14, TEAL, "bold")]
    def X(d): return 80 + d*7.0
    events = [(0, "원자재 매입·입고"), (23, "매입 대금 지급"), (52, "제품 판매(출하)"), (110, "판매 대금 회수")]
    b.append(line(X(0), 140, X(110)+18, 140, GRAY, 1.4))
    for d, lab in events:
        b.append(text(X(d), 108, lab, 11.5, NAVY, "bold"))
        b.append(text(X(d), 124, f"Day {d}", 11, GRAY))
        b.append(circle(X(d), 140, 4, NAVY))
        b.append(line(X(d), 144, X(d), 330, "#C6CCD5", 1, "3,3"))
    b.append(rrect(X(0), 170, X(52)-X(0), 46, ICE2, NAVY, 1.5, 6))
    b.append(text((X(0)+X(52))/2, 198, "재고일수 DIO 52일", 13, NAVY, "bold"))
    b.append(rrect(X(52), 170, X(110)-X(52), 46, TEALBG, TEAL, 1.5, 6))
    b.append(text((X(52)+X(110))/2, 198, "채권일수 DSO 58일", 13, TEAL, "bold"))
    b.append(rrect(X(0), 240, X(23)-X(0), 46, NAVY, NAVY, 1.5, 6))
    b.append(text((X(0)+X(23))/2, 268, "채무 DPO 23일", 12, WHITE, "bold"))
    b.append(text(X(23)+14, 268, "← 공급업체 외상이 현금 지출을 미룬다", 11.5, GRAY, anchor="start"))
    yb = 322
    b.append(line(X(23), yb, X(110), yb, ACC, 2.5))
    b.append(line(X(23), yb-9, X(23), yb+9, ACC, 2.5))
    b.append(line(X(110), yb-9, X(110), yb+9, ACC, 2.5))
    b.append(text((X(23)+X(110))/2, 352, "현금전환주기 CCC = 52 + 58 − 23 = 87일", 14, ACC, "bold"))
    b.append(text((X(23)+X(110))/2, 374, "Day 23(현금 지출)부터 Day 110(현금 회수)까지 — 현금이 잠겨 있는 기간", 11.5, GRAY))
    b.append(text(W/2, 412, "루프의 목표: 87일 → 70일 — 채권 회수 강화(DSO)와 안전재고 하향(DIO)으로 단축한다", 12, GRAY))
    b.append(text(W/2, H-14, "2부 14장 — 수치는 14.5절 DMAIC 시나리오 예시", 11.5, GRAY))
    svg("fig_142_ccc", W, H, "".join(b))

# ── 그림 15-1. SECI 나선과 지식센터 ────────────────────────────
def fig_151():
    W, H = 940, 640
    b = [text(W/2, 40, "SECI 나선과 지식센터 — 암묵지와 형식지의 변환 사이클", 21, NAVY, "bold"),
         text(W/2, 66, "조직 지식은 네 가지 변환의 나선으로 자란다 (Nonaka, 1994)", 13, GRAY)]
    quads = [
        (80, 100, "공동화 Socialization", "암묵지 → 암묵지",
         ["디스커스 채팅 · 현장 동행", "(시스템 밖 영역이 아직 크다)"], LGRAY, GRAY, "사람의 영역 — 시스템 밖", GRAY, "6,5"),
        (500, 100, "표출화 Externalization", "암묵지 → 형식지",
         ["음성 기록·요약 · AI Fields", "지식센터 아티클 작성"], ICE, NAVY, "지식센터가 담당하는 장(場)", TEAL, ""),
        (500, 390, "연결화 Combination", "형식지 → 형식지",
         ["아티클 트리 체계화 · 템플릿", "업무 레코드-문서 연결"], ICE, NAVY, "지식센터가 담당하는 장(場)", TEAL, ""),
        (80, 390, "내면화 Internalization", "형식지 → 암묵지",
         ["AI 질의응답 · 에이전트 안내", "온보딩 교육"], TEALBG, TEAL, "AI 질의응답의 통로", NAVY, ""),
    ]
    for x, y, t, tr, lines, fill, stroke, tag, tagc, dash in quads:
        cx = x + 180
        b.append(rrect(x, y, 360, 170, fill, stroke, 1.8, 12, dash))
        b.append(text(cx, y+34, t, 15, NAVY, "bold"))
        b.append(text(cx, y+58, tr, 12, TEAL, "bold"))
        b.append(multi(cx, y+86, lines, 11.5, GRAY, 20))
        b.append(text(cx, y+148, tag, 11, tagc, "bold"))
    b.append(arrow(444, 150, 496, 150, TEAL, 3, "ahT"))
    b.append(arrow(680, 274, 680, 386, TEAL, 3, "ahT"))
    b.append(arrow(496, 510, 444, 510, TEAL, 3, "ahT"))
    b.append(arrow(260, 386, 260, 274, TEAL, 3, "ahT"))
    b.append(circle(470, 330, 56, NAVY))
    b.append(multi(470, 324, ["지식의", "나선"], 15, WHITE, 20, w="bold"))
    b.append(text(W/2, 596, "지식센터는 표출화·연결화의 장(場), AI 질의응답은 내면화의 통로 — 회전할수록 조직지식이 두터워진다", 12, NAVY, "bold"))
    b.append(text(W/2, H-14, "2부 15장 — 지식센터: 암묵지의 형식지화 거점", 11.5, GRAY))
    svg("fig_151_seci", W, H, "".join(b))

# ── 그림 15-2. 지식의 3정5S 문서 체계도 ────────────────────────
def fig_152():
    W, H = 960, 545
    b = [text(W/2, 40, "지식의 3정 — 문서 체계의 정위치·정품·정량", 22, NAVY, "bold"),
         text(W/2, 66, "그릇이 있다고 지식이 고이지는 않는다 — 위키의 실패를 막는 세 개의 기준", 13, GRAY)]
    # 정위치 패널
    b.append(rrect(40, 100, 285, 380, WHITE, NAVY, 1.6, 10))
    b.append(rrect(40, 100, 285, 36, NAVY, NAVY, 1.6, 10))
    b.append(f'<rect x="40" y="118" width="285" height="18" fill="{NAVY}"/>')
    b.append(text(182, 123, "정위치 — 문서의 주소", 13.5, WHITE, "bold"))
    b.append(rrect(58, 152, 112, 28, ICE2, NAVY, 1.3, 6))
    b.append(text(114, 170, "지식센터", 12.5, NAVY, "bold"))
    b.append(line(76, 180, 76, 349, GRAY, 1.2))
    kids = [("제품", 196), ("고객 응대", 234), ("설비", 272), ("규정", 336)]
    for name, y in kids:
        b.append(line(76, y+13, 94, y+13, GRAY, 1.2))
        b.append(rrect(94, y, 118, 26, ICE, NAVY, 1.1, 5))
        b.append(text(153, y+17, name, 12, NAVY, "bold"))
    b.append(line(112, 298, 112, 316, GRAY, 1.2))
    b.append(line(112, 316, 130, 316, GRAY, 1.2))
    b.append(rrect(130, 304, 152, 24, WHITE, TEAL, 1.1, 5))
    b.append(text(206, 320, "설비 E-42 조치 절차", 11, TEAL))
    b.append(multi(182, 398, ["한 주제 = 한 아티클, 트리의 단 한 곳", "1층은 조직도가 아니라 질문 유형으로"], 11, GRAY, 17))
    # 정품 패널
    b.append(rrect(350, 100, 285, 380, WHITE, TEAL, 1.6, 10))
    b.append(rrect(350, 100, 285, 36, TEAL, TEAL, 1.6, 10))
    b.append(f'<rect x="350" y="118" width="285" height="18" fill="{TEAL}"/>')
    b.append(text(492, 123, "정품 — 검증된 내용만", 13.5, WHITE, "bold"))
    b.append(rrect(375, 150, 235, 215, WHITE, NAVY, 1.3, 6))
    b.append(f'<rect x="375" y="150" width="235" height="30" rx="6" fill="{ICE2}"/>')
    b.append(f'<rect x="375" y="168" width="235" height="12" fill="{ICE2}"/>')
    b.append(text(492, 170, "표준 템플릿", 12.5, NAVY, "bold"))
    for i, row in enumerate(["목적", "적용 범위", "절차", "예외", "개정 이력"]):
        y = 180 + i*37
        if i > 0:
            b.append(line(375, y, 610, y, "#D5DAE1", 1))
        b.append(text(390, y+23, row, 11.5, NAVY, "bold", "start"))
        b.append(line(470, y+19, 595, y+19, "#C6CCD5", 1.4))
    b.append(multi(492, 398, ["소유자 검증을 통과한 문서만", "AI 학습 소스로 지정한다"], 11, GRAY, 17))
    b.append(text(492, 445, "구버전·오류는 발견 즉시 교정", 11, ACC, "bold"))
    # 정량 패널
    b.append(rrect(660, 100, 285, 380, WHITE, NAVY, 1.6, 10))
    b.append(rrect(660, 100, 285, 36, NAVY, NAVY, 1.6, 10))
    b.append(f'<rect x="660" y="118" width="285" height="18" fill="{NAVY}"/>')
    b.append(text(802, 123, "정량 — 최신성의 관리", 13.5, WHITE, "bold"))
    items = [
        ("소유자·차기 검토일", "모든 아티클에 지정", NAVY, ""),
        ("참조 수 진단(분기)", "상위·하위 아티클 점검", NAVY, ""),
        ("오답 신고 → 원인 문서 교정", "AI가 틀리면 문서를 고친다", NAVY, ""),
        ("빨간 패 — 보관 처리", "2년 무참조·담당 변경 문서", ACC, "6,5"),
    ]
    for i, (t, sub, c, dash) in enumerate(items):
        y = 152 + i*66
        b.append(rrect(676, y, 253, 56, ICE if not dash else WHITE, c, 1.2, 7, dash))
        b.append(text(690, y+23, t, 12, c, "bold", "start"))
        b.append(text(690, y+42, sub, 11, GRAY, anchor="start"))
    b.append(multi(802, 432, ["중복도 공백도 없이 —", "필요한 문서가 필요한 만큼만"], 11, GRAY, 17))
    b.append(text(W/2, 508, "죽은 문서가 AI 답변을 오염시키기 전에 — 문서의 3정은 AI 도입의 전제 조건이다", 12.5, NAVY, "bold"))
    b.append(text(W/2, 531, "2부 15장 — 지식센터: 트리의 정위치 · 템플릿의 정품 · 최신성의 정량", 11.5, GRAY))
    svg("fig_152_knowledge_5s", W, H, "".join(b))

# ── 그림 16-2. 무한 루프의 기술 스택 배치 ──────────────────────
def fig_162():
    W, H = 940, 690
    cx, cy, R = W/2, 390, 210
    steps = [
        ("Define", "정의", "n8n + Dify", "관리도 감시·문제정의 초안"),
        ("Measure", "수집", "Odoo + n8n", "트랜잭션·POP·외부 수집"),
        ("Analyze", "학습", "Neo4j + LLM", "경로 역추적·가설 생성"),
        ("Improve", "추론", "LLM + frePPLe", "대책 초안·What-if 성적표"),
        ("Control", "환류", "Odoo + n8n", "마스터·규칙 반영"),
    ]
    b = [text(W/2, 40, "무한 루프의 기술 스택 배치 — 배관·작업대·기억·두뇌·손발", 21, NAVY, "bold"),
         text(W/2, 66, "1부 5장의 DMAIC 방법론이 오픈소스 스택 위에 실장된다 (16.3절)", 13, GRAY)]
    pos = ring_pos(cx, cy, R, 5)
    ring_arrows(b, cx, cy, pos, off=100, bulge=38)
    for (x, y), (en, ko, stack, sub) in zip(pos, steps):
        b.append(rrect(x-88, y-48, 176, 96, ICE, NAVY, 2, 14))
        b.append(text(x, y-24, en, 15, NAVY, "bold"))
        b.append(text(x, y-5, ko, 13, TEAL, "bold"))
        b.append(text(x, y+16, stack, 12.5, NAVY, "bold"))
        b.append(text(x, y+35, sub, 11, GRAY))
    # HITL 승인 게이트 (Improve→Control 경로 위)
    b.append(rrect(252, 441, 20, 26, ACC, ACC, 0, 4))
    b.append(f'<path d="M256,454 l5,6 l9,-11" stroke="{WHITE}" stroke-width="2.5" fill="none"/>')
    b.append(multi(180, 448, ["HITL", "승인 게이트"], 11, ACC, 16, w="bold"))
    b.append(circle(cx, cy, 86, NAVY))
    b.append(text(cx, cy-14, "LLM = 두뇌", 18, WHITE, "bold"))
    b.append(multi(cx, cy+12, ["가설과 서사 생성 —", "사실·검정 위에서만"], 11.5, ICE2, 16))
    b.append(text(W/2, 642, "역할: n8n=배관 · Dify=작업대 · Neo4j=기억 · LLM=두뇌 · Odoo=손발", 12.5, NAVY, "bold"))
    b.append(text(W/2, 668, "지능은 교체 가능하게, 기억과 배관은 안정되게 — 루프의 가치는 두뇌가 아니라 기억에 쌓인다", 11.5, GRAY))
    svg("fig_162_loop_stack", W, H, "".join(b))

# ── 그림 16-3. 하이브리드 보안 2층 구조 ────────────────────────
def fig_163():
    W, H = 920, 530
    b = [text(W/2, 38, "하이브리드 보안 모델 — 공동 발전소와 전용 금고의 2층 구조", 21, NAVY, "bold"),
         text(W/2, 62, "내 데이터는 내 금고에, 무거운 AI는 공동 발전소에서 (이형근, 2026)", 13, GRAY)]
    # 상층: 관리형 공동 계층
    b.append(rrect(60, 90, 800, 130, TEALBG, TEAL, 1.8, 12))
    b.append(text(80, 116, "관리형 공동 계층 — 무거운 AI는 공동 발전소에서", 15, NAVY, "bold", "start"))
    b.append(text(840, 116, "다수의 비용 분담", 11.5, TEAL, "bold", "end"))
    chips = [
        ("자체 LLM 추론", ["GPU 공동 운영", "오픈 LLM(Ollama)"]),
        ("공통 지식", ["상품분류·택배·세무 상식", "공통 템플릿"]),
        ("자동화 엔진", ["n8n 워크플로", "이벤트·ETL 배관"]),
        ("보안·백업", ["자동 스냅샷·격리 보관", "무중단 자동 패치"]),
    ]
    cw, cgap = 186, 12
    x0 = (W - (cw*4 + cgap*3)) / 2
    for i, (t, lines) in enumerate(chips):
        X = x0 + i*(cw+cgap)
        b.append(rrect(X, 132, cw, 74, WHITE, TEAL, 1.3, 8))
        b.append(text(X+cw/2, 152, t, 12.5, NAVY, "bold"))
        b.append(multi(X+cw/2, 172, lines, 11, GRAY, 16))
    # 계층 간 화살표
    b.append(arrow(350, 226, 350, 300, TEAL, 3, "ahT"))
    b.append(text(336, 266, "AI 추론·자동화·백업 서비스", 11.5, TEAL, "bold", "end"))
    b.append(arrow(590, 300, 590, 226, NAVY, 3))
    b.append(text(604, 266, "질의·이벤트 — 외부 API로 나가지 않는다", 11.5, NAVY, "bold", "start"))
    # 하층: 고객 격리 계층
    b.append(rrect(60, 306, 800, 158, ICE, NAVY, 1.8, 12))
    b.append(text(80, 332, "고객 격리 계층 — 내 데이터는 내 금고에", 15, NAVY, "bold", "start"))
    b.append(text(840, 332, "분리·암호화 — 유출·혼입 차단", 11.5, NAVY, "bold", "end"))
    for i, name in enumerate(["고객 A", "고객 B", "고객 C"]):
        X = 72 + i*(246+18)
        b.append(rrect(X, 348, 246, 100, WHITE, NAVY, 1.5, 8))
        b.append(text(X+16, 370, f"{name} — 전용 금고", 12.5, NAVY, "bold", "start"))
        lx = X + 218
        b.append(f'<path d="M{lx-5},368 a5,5 0 0 1 10,0 v4" stroke="{NAVY}" stroke-width="1.8" fill="none"/>')
        b.append(rrect(lx-8, 372, 16, 12, NAVY, NAVY, 0, 2))
        b.append(multi(X+123, 392, ["매출·정산 · 고객 개인정보", "거래처·원가 · 사업자 노트"], 11, GRAY, 16))
        b.append(text(X+123, 434, "전용 암호화 DB", 11, TEAL, "bold"))
    b.append(text(W/2, 486, "Passkey 생체 로그인 · 종단간 암호화 · 자동 스냅샷 백업 · 랜섬웨어 격리 보관 · 무중단 자동 패치", 11.5, GRAY))
    b.append(text(W/2, H-14, "2부 16장 — 1인 기업도 구독료로 자체 LLM과 데이터 주권을 갖는다", 11.5, GRAY))
    svg("fig_163_hybrid_security", W, H, "".join(b))

# ── 그림 17-1. 단일 원장의 데이터 순환 ─────────────────────────
def fig_171():
    W, H = 900, 630
    cx, cy, R = W/2, 340, 195
    nodes = [
        ("주문", "9~10장", "견적→수주·이커머스"),
        ("재고", "11~12장", "출고 예약·발주·입고"),
        ("제조", "13장", "MRP·작업지시·실적"),
        ("회계", "14장", "자동 분개·실시간 원가"),
        ("분석·AI", "15~16장", "브리핑·예측·환류"),
    ]
    b = [text(W/2, 40, "단일 원장의 데이터 순환 — 주문에서 결산까지", 22, NAVY, "bold"),
         text(W/2, 66, "모듈은 기능의 묶음이 아니라 단일 원장 위의 관점들이다", 13, GRAY)]
    pos = ring_pos(cx, cy, R, 5)
    for x, y in pos:
        a = math.atan2(y-cy, x-cx)
        b.append(line(cx+100*math.cos(a), cy+100*math.sin(a),
                      cx+150*math.cos(a), cy+150*math.sin(a), GRAY, 1.2, "3,3"))
    ring_arrows(b, cx, cy, pos, off=90, bulge=36)
    for (x, y), (t, ch, sub) in zip(pos, nodes):
        b.append(rrect(x-75, y-40, 150, 80, ICE, NAVY, 1.8, 12))
        b.append(text(x, y-14, t, 14.5, NAVY, "bold"))
        b.append(text(x, y+5, ch, 11.5, TEAL, "bold"))
        b.append(text(x, y+25, sub, 11, GRAY))
    b.append(circle(cx, cy, 92, NAVY))
    b.append(text(cx, cy-18, "단일 PostgreSQL", 16, WHITE, "bold"))
    b.append(text(cx, cy+6, "하나의 원장", 13, ICE2, "bold"))
    b.append(text(cx, cy+28, "같은 품목·거래처 코드", 11, ICE2))
    b.append(text(W/2, 598, "사건은 발생 지점에서 한 번 기록되고, 관점으로 다르게 조회될 뿐 복제되지 않는다 (17.3절)", 12, NAVY, "bold"))
    b.append(text(W/2, H-12, "2부 17장 — 이 단일성이 온톨로지 역추적과 DMAIC 루프의 성립 전제다", 11.5, GRAY))
    svg("fig_171_single_ledger", W, H, "".join(b))

# ── 그림 17-2. 전사 컨설팅 마스터플랜 로드맵 ───────────────────
def fig_172():
    W, H = 1000, 610
    b = [text(W/2, 40, "전사 컨설팅 마스터플랜 — AX 5단계 로드맵 × 모듈 도입 순서", 21, NAVY, "bold"),
         text(W/2, 66, "시간 축(1부 6장 로드맵)과 공간 축(2부 모듈 순서)의 결합 — 시나리오 B(5~50인 제조) 기준", 12.5, GRAY)]
    x0, x1 = 200, 960
    mw = (x1-x0)/12
    def X(m): return x0 + m*mw
    for m in range(13):
        b.append(line(X(m), 114, X(m), 120, GRAY, 1))
        if m > 0:
            b.append(text(X(m), 108, str(m), 11, GRAY))
    b.append(line(x0, 120, x1, 120, GRAY, 1.4))
    b.append(text(x1+22, 108, "개월", 11, GRAY))
    rows = [
        ("1 진단", "2~4주", 0, 1, TEAL, "매트릭스 채점 · KGI-질문-KPI 트리 · 현장 5S 진단", "right"),
        ("2 기반", "2~3개월", 1, 3.5, TEAL, "판매·매입·재고 + 회계 기초 · 코드체계 정의", "right"),
        ("3 적재", "2~3개월", 3.5, 6, TEAL, "제조 POP 정착 · 회계 분석 차원 · 지식센터", "right"),
        ("4 지능화", "3~6개월", 6, 10.5, NAVY, "Neo4j → GraphRAG → frePPLe → 루프 시범", "in"),
        ("5 환류", "상시", 10.5, 12, ACC, "브리핑·액션 환류", "below"),
    ]
    y0, rh = 132, 68
    for r, (name, dur, s, e, color, lab, mode) in enumerate(rows):
        Y = y0 + r*rh
        b.append(line(x0, Y+rh, x1, Y+rh, "#D5DAE1", 1))
        b.append(text(45, Y+26, name, 13.5, NAVY, "bold", "start"))
        b.append(text(45, Y+45, dur, 11.5, GRAY, anchor="start"))
        bx, bw2 = X(s), X(e)-X(s)
        b.append(rrect(bx, Y+17, bw2, 34, color, color, 0, 7))
        if mode == "in":
            b.append(text(bx+bw2/2, Y+39, lab, 11.5, WHITE, "bold"))
        elif mode == "below":
            b.append(text(bx+bw2/2, Y+39, lab, 11, WHITE, "bold"))
            b.append(text(x1, Y+62, "승인 성적표 기반 위임 확대 — 상시 운영", 11, GRAY, anchor="end"))
        else:
            b.append(text(bx+bw2+12, Y+39, lab, 11.5, GRAY, anchor="start"))
        if mode == "below":
            b.append(arrow(X(12)+2, Y+34, X(12)+26, Y+34, ACC, 2.5, "ahA", "5,4"))
    gates = [(3.5, "관문① 시스템 월 마감 · 이중 입력 제거", 505),
             (6, "관문② 재고 정확도 95% · 실적 24시간 이내", 527),
             (10.5, "관문③ 질문 커버리지 70% · 루프 1회전 완주", 505)]
    for m, lab, ly in gates:
        b.append(line(X(m), 124, X(m), 490, ACC, 1.4, "6,4"))
        b.append(f'<path d="M{X(m)-6},490 l6,9 l6,-9 z" fill="{ACC}"/>')
        b.append(text(X(m), ly, lab, 11.5, ACC, "bold"))
    b.append(text(W/2, 560, "관문 미달 시의 표준 대응은 일정 연기가 아니라 범위 축소 — 모듈 수를 줄여서라도 관문을 먼저 통과한다", 12, GRAY))
    b.append(text(W/2, H-14, "2부 17장 — 관문은 일정의 장식이 아니라 다음 투자의 조건이다 (17.5절)", 11.5, GRAY))
    svg("fig_172_masterplan", W, H, "".join(b))

fig_132(); fig_133(); fig_141(); fig_142(); fig_151()
fig_152(); fig_162(); fig_163(); fig_171(); fig_172()
print("완료")
