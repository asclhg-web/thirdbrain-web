#!/usr/bin/env python3
"""3순위 보조 도해 — 2부 8~12장 담당분 9점 (fig 8-2, 9-1, 9-2, 10-1, 10-2, 11-1, 11-2, 12-2, 12-3)."""
import math
from figlib import *

# ── 그림 8-2. 단일 PostgreSQL 위 70+ 앱 허브 구조도 ────────────
def fig_82():
    W, H = 940, 560
    b = [text(W/2, 38, "단일 PostgreSQL 위의 70+ 앱", 24, NAVY, "bold"),
         text(W/2, 64, "모든 앱은 하나의 데이터베이스를 공유하는 관점들일 뿐이다", 13.5, GRAY)]
    row1 = [("웹사이트", "9장"), ("이커머스", "9장"), ("CRM", "10장"), ("판매", "10장"),
            ("매입", "11장"), ("재고", "12장"), ("제조", "13장"), ("회계", "14장")]
    cw, ch, gap = 100, 50, 6
    x0 = (W - (cw*8 + gap*7)) / 2
    for i, (name, chap) in enumerate(row1):
        x = x0 + i*(cw+gap)
        b.append(rrect(x, 92, cw, ch, ICE, NAVY, 1.4, 8))
        b.append(text(x+cw/2, 113, name, 12.5, NAVY, "bold"))
        b.append(text(x+cw/2, 132, chap, 11, GRAY))
    row2 = [("인사", ""), ("프로젝트", ""), ("문서", ""), ("마케팅", ""), ("POS", ""), ("지식센터", "15장")]
    x0b = (W - (cw*7 + gap*6)) / 2
    for i, (name, chap) in enumerate(row2):
        x = x0b + i*(cw+gap)
        b.append(rrect(x, 148, cw, ch, LGRAY, GRAY, 1.2, 8))
        b.append(text(x+cw/2, 113-92+148+(0 if chap else 8), name, 12.5, NAVY, "bold"))
        if chap:
            b.append(text(x+cw/2, 188, chap, 11, GRAY))
    # + 새 앱 (점선)
    x = x0b + 6*(cw+gap)
    b.append(rrect(x, 148, cw, ch, WHITE, TEAL, 1.4, 8, dash="5,4"))
    b.append(text(x+cw/2, 169, "+ 새 앱", 12.5, TEAL, "bold"))
    b.append(text(x+cw/2, 188, "60여 개", 11, GRAY))
    # ORM 계층 바
    b.append(rrect(x0, 204, cw*8+gap*7, 38, NAVY, NAVY, 1.5, 8))
    b.append(text(W/2, 228, "파이썬 ORM 계층 — 70+ 앱이 동일한 객체 모델로 접근한다", 13.5, WHITE, "bold"))
    for ax in (W/2-270, W/2-90, W/2+90, W/2+270):
        b.append(arrow(ax, 246, ax, 282, TEAL, 2.4, "ahT"))
    # DB 실린더
    cx, rx, ry = W/2, 290, 24
    ytop, ybot = 314, 428
    b.append(f'<rect x="{cx-rx}" y="{ytop}" width="{rx*2}" height="{ybot-ytop}" fill="{ICE}"/>')
    b.append(f'<ellipse cx="{cx}" cy="{ybot}" rx="{rx}" ry="{ry}" fill="{ICE}" stroke="{NAVY}" stroke-width="1.8"/>')
    b.append(line(cx-rx, ytop, cx-rx, ybot, NAVY, 1.8))
    b.append(line(cx+rx, ytop, cx+rx, ybot, NAVY, 1.8))
    b.append(f'<ellipse cx="{cx}" cy="{ytop}" rx="{rx}" ry="{ry}" fill="{ICE2}" stroke="{NAVY}" stroke-width="1.8"/>')
    b.append(text(cx, 368, "PostgreSQL — 단일 데이터베이스", 17, NAVY, "bold"))
    b.append(text(cx, 393, "고객 res.partner 한 자리 · 품목 마스터 한 자리 · 재고 원장 한 자리", 12, GRAY))
    b.append(text(cx, 416, "새 앱을 설치해도 이미 쌓인 데이터가 그대로 새 앱의 마스터가 된다", 12, TEAL, "bold"))
    b.append(text(W/2, 498, "하나의 사실이 살 수 있는 자리가 아키텍처 수준에서 한 곳뿐이다 — 데이터 정위치의 플랫폼적 보장", 13, NAVY, "bold"))
    b.append(text(W/2, H-16, "2부 8장 — Odoo 플랫폼 총론", 11.5, GRAY))
    svg("fig_82_pg_hub", W, H, "".join(b))

# ── 그림 9-1. 전환 퍼널 ────────────────────────────────────────
def fig_91():
    W, H = 920, 640
    b = [text(W/2, 38, "전환 퍼널 — 방문에서 재구매까지", 24, NAVY, "bold"),
         text(W/2, 64, "어느 단계에서 몇 명이 빠지는가 (수치는 예시)", 13.5, GRAY)]
    cx = 400
    stages = [("방문", "10,000명", "100%", 660, "#CADCFC", NAVY),
              ("장바구니 담기", "850명", "8.5%", 420, "#9FC2E4", NAVY),
              ("결제·주문 완료", "400명", "4.0%", 260, "#3E7CB8", WHITE),
              ("재구매", "120명", "1.2%", 156, TEAL, WHITE)]
    sh, sgap, y0 = 82, 34, 108
    trans = [("전환율 8.5%", "이탈 91.5% — 9,150명"),
             ("결제 전환 47%", "이탈 53% — 450명"),
             ("재구매율 30%", "미재구매 70% — 280명")]
    for i, (name, cnt, pct, w, fill, tc) in enumerate(stages):
        y = y0 + i*(sh+sgap)
        wn = stages[i+1][3] + 40 if i < 3 else w - 36
        b.append(f'<path d="M{cx-w/2},{y} L{cx+w/2},{y} L{cx+wn/2},{y+sh} L{cx-wn/2},{y+sh} z" '
                 f'fill="{fill}" stroke="{NAVY}" stroke-width="1.2"/>')
        b.append(text(cx, y+36, f"{name}  {cnt}", 14.5, tc, "bold"))
        b.append(text(cx, y+60, f"방문 대비 {pct}", 11.5, tc if tc == WHITE else GRAY))
        if i < 3:
            gy = y + sh + sgap/2
            wn2 = stages[i+1][3]
            b.append(arrow(cx, y+sh+4, cx, y+sh+sgap-4, TEAL, 2.4, "ahT"))
            b.append(text(cx + wn2/2 + 46, gy+5, trans[i][0], 13, TEAL, "bold", anchor="start"))
            b.append(arrow(cx - wn2/2 - 8, gy-4, cx - wn2/2 - 40, gy+8, ACC, 2, "ahA"))
            b.append(text(cx - wn2/2 - 48, gy+9, trans[i][1], 12, ACC, anchor="end"))
    b.append(text(W/2, 578, "단계별 통과율에 관리 한계(최근 4주 관리 범위)를 정의하면 정상과 이상의 경계가 화면에 새겨진다", 12.5, GRAY))
    b.append(text(W/2, H-16, "2부 9장 — 웹사이트·이커머스", 11.5, GRAY))
    svg("fig_91_funnel", W, H, "".join(b))

# ── 그림 9-2. 주문 한 건의 자동 연쇄 ───────────────────────────
def fig_92():
    W, H = 960, 500
    b = [text(W/2, 38, "주문 한 건의 자동 연쇄 — 사람 손 없이", 24, NAVY, "bold"),
         text(W/2, 64, "온라인 주문이 확정되는 순간, 네 개의 기록이 한 사건에서 이어진다", 13.5, GRAY)]
    steps = [("웹 주문 확정", ["고객 결제 완료"]),
             ("판매 주문(SO)", ["주문 즉시", "자동 생성"]),
             ("재고 예약", ["가용 재고에서", "즉시 분리"]),
             ("출고·배송", ["출고 지시가", "창고 화면에"]),
             ("청구서·회계 분개", ["결제 확인과", "함께 자동 기표"])]
    bw, bh, gap, y = 164, 88, 25, 96
    x0 = (W - (bw*5 + gap*4)) / 2
    for i, (t, sub) in enumerate(steps):
        x = x0 + i*(bw+gap)
        b.append(rrect(x, y, bw, bh, ICE if i > 0 else TEALBG, NAVY if i > 0 else TEAL, 1.5, 9))
        b.append(text(x+bw/2, y+30, t, 13, NAVY if i > 0 else TEAL, "bold"))
        b.append(multi(x+bw/2, y+53, sub, 11, GRAY, 17))
        if i < 4:
            b.append(arrow(x+bw+2, y+bh/2, x+bw+gap-2, y+bh/2, TEAL, 2.4, "ahT"))
            b.append(text(x+bw+gap/2, y+bh/2-10, "자동", 11, TEAL, "bold"))
    # 존재하지 않는 공정
    ox, oy, ow, oh = (W-660)/2, 232, 660, 56
    b.append(rrect(ox, oy, ow, oh, WHITE, ACC, 1.5, 9, dash="6,5"))
    b.append(text(W/2, oy+34, "별도 쇼핑몰의 공정: 주문 엑셀 다운로드 → ERP 재입력 → 오류와 지연", 12.5, GRAY))
    b.append(line(ox+56, oy+30, ox+ow-56, oy+30, ACC, 2))
    b.append(line(ox+22, oy+18, ox+42, oy+38, ACC, 2.5))
    b.append(line(ox+22, oy+38, ox+42, oy+18, ACC, 2.5))
    b.append(line(ox+ow-42, oy+18, ox+ow-22, oy+38, ACC, 2.5))
    b.append(line(ox+ow-42, oy+38, ox+ow-22, oy+18, ACC, 2.5))
    b.append(text(W/2, oy+oh+24, "이 공정 자체가 존재하지 않는다", 13, ACC, "bold"))
    b.append(rrect((W-700)/2, 348, 700, 52, ICE, NAVY, 1.4, 10))
    b.append(text(W/2, 380, "하나의 데이터베이스 위에서 주문·재고·물류·회계는 한 사건의 네 기록이 된다", 13.5, NAVY, "bold"))
    b.append(text(W/2, 438, "판매와 동시에 재고·회계 데이터가 즉시 반영되는 완전 자동화 (Odoo 공식 소개자료)", 12, GRAY))
    b.append(text(W/2, H-16, "2부 9장 — 웹사이트·이커머스", 11.5, GRAY))
    svg("fig_92_order_chain", W, H, "".join(b))

# ── 그림 10-1. 영업 파이프라인 칸반 목업 ───────────────────────
def fig_101():
    W, H = 960, 600
    b = [text(W/2, 38, "영업 파이프라인 — 디지털 관리판", 24, NAVY, "bold"),
         text(W/2, 64, "단계 열 = 공정 구획, 기회 카드 = 마그넷 명찰, 드래그 = 명찰 옮기기", 13.5, GRAY)]
    # 프레임
    fx, fy, fw, fh = 30, 88, 900, 396
    b.append(rrect(fx, fy, fw, fh, WHITE, NAVY, 2, 10))
    b.append(rrect(fx, fy, fw, 38, NAVY, NAVY, 2, 10))
    b.append(f'<rect x="{fx}" y="{fy+19}" width="{fw}" height="19" fill="{NAVY}"/>')
    b.append(text(fx+fw/2, fy+25, "CRM 파이프라인 — 이번 분기", 14, WHITE, "bold"))
    cols = [("신규", "3건 · 4,400만"), ("검토", "2건 · 5,300만"), ("제안", "2건 · 8,100만"), ("협상", "1건 · 7,800만")]
    cards = [
        [("가나상사", "1,200만 · 20%", 2, None), ("한빛산업", "800만 · 15%", 1, None), ("대성테크", "2,400만 · 25%", 3, None)],
        [("두리정밀", "3,500만 · 40%", 3, None), ("세운금속", "1,800만 · 35%", 2, None)],
        [("미래기계", "5,200만 · 60%", 4, None), ("동아전자", "2,900만 · 55%", 3, None)],
        [("한결중공업", "7,800만 · 75%", 5, "체류 21일 — 표준 15일 초과")],
    ]
    colw, colgap = 212, 10
    x0 = fx + (fw - (colw*4 + colgap*3)) / 2
    for i, (cn, csum) in enumerate(cols):
        x = x0 + i*(colw+colgap)
        b.append(rrect(x, fy+50, colw, 42, ICE2, NAVY, 1.1, 7))
        b.append(text(x+colw/2, fy+68, cn, 12.5, NAVY, "bold"))
        b.append(text(x+colw/2, fy+85, csum, 11, GRAY))
        cy = fy + 104
        for (name, amt, score, warn) in cards[i]:
            ch = 92 if warn else 78
            bar = ACC if warn else TEAL
            b.append(rrect(x, cy, colw, ch, LGRAY, GRAY, 1, 6))
            b.append(f'<rect x="{x}" y="{cy}" width="5" height="{ch}" rx="2.5" fill="{bar}"/>')
            b.append(text(x+16, cy+22, name, 12.5, NAVY, "bold", anchor="start"))
            b.append(text(x+16, cy+42, amt, 11.5, GRAY, anchor="start"))
            b.append(text(x+16, cy+62, "AI", 11, TEAL, "bold", anchor="start"))
            for k in range(5):
                fill = TEAL if k < score else WHITE
                b.append(circle(x+40+k*13, cy+58, 4.2, fill, TEAL, 1.2))
            if warn:
                b.append(text(x+16, cy+82, warn, 10.8, ACC, "bold", anchor="start"))
            cy += ch + 9
    b.append(text(W/2, 516, "가중 파이프라인 Σ(금액 × 확률) = 2.1억 → 월별 수주 예측의 입력", 13, TEAL, "bold"))
    b.append(text(W/2, 542, "열마다 쌓인 카드 수와 금액 합이 곧 단계별 재공 — 표준 체류 일수를 벗어난 카드가 '이상'으로 드러난다", 12, GRAY))
    b.append(text(W/2, H-16, "2부 10장 — CRM·판매 (수치는 예시)", 11.5, GRAY))
    svg("fig_101_pipeline_kanban", W, H, "".join(b))

# ── 그림 10-2. 리드 스코어링 개념도 ────────────────────────────
def fig_102():
    W, H = 940, 560
    b = [text(W/2, 38, "AI 리드 스코어링 — 감이 아니라 확률로 줄을 세운다", 22, NAVY, "bold"),
         text(W/2, 64, "리드 속성 입력 → AI 확률 점수 → 우선순위 정렬", 13.5, GRAY)]
    inputs = [("유입 경로", "전시회 · 웹 · 소개"), ("고객 속성", "업종 · 규모 · 지역"),
              ("활동 이력", "접촉 빈도 · 응답 속도"), ("과거 데이터", "유사 기회의 수주·실주")]
    ix, iw, ih = 60, 228, 58
    cy0 = 118
    ccx, ccy, cr = 468, 268, 88
    for i, (t, sub) in enumerate(inputs):
        y = cy0 + i*(ih+16)
        b.append(rrect(ix, y, iw, ih, ICE, NAVY, 1.4, 8))
        b.append(text(ix+iw/2, y+24, t, 12.5, NAVY, "bold"))
        b.append(text(ix+iw/2, y+44, sub, 11, GRAY))
        b.append(arrow(ix+iw+6, y+ih/2, ccx-cr-6, ccy + (y+ih/2-ccy)*0.25, TEAL, 1.8, "ahT"))
    b.append(circle(ccx, ccy, cr, NAVY))
    b.append(text(ccx, ccy-14, "AI 리드", 17, WHITE, "bold"))
    b.append(text(ccx, ccy+10, "스코어링", 17, WHITE, "bold"))
    b.append(text(ccx, ccy+34, "수주 확률 계산", 11.5, ICE2))
    b.append(multi(ccx, ccy+cr+24, ["과거 수주·실주 데이터에서", "학습한 확률 모델"], 11.5, GRAY, 17))
    # 우선순위 패널
    px, py, pw, ph = 650, 118, 260, 316
    b.append(rrect(px, py, pw, ph, LGRAY, GRAY, 1.3, 10))
    b.append(text(px+pw/2, py+28, "우선순위 정렬", 14, NAVY, "bold"))
    leads = [("A사", 87, TEAL, True), ("B사", 62, TEAL, False), ("C사", 34, "#9AA3AE", False), ("D사", 12, "#9AA3AE", False)]
    for i, (name, pct, color, focus) in enumerate(leads):
        y = py + 52 + i*62
        b.append(rrect(px+14, y, pw-28, 50, WHITE, GRAY if not focus else TEAL, 1.6 if focus else 1, 6))
        b.append(text(px+28, y+21, name, 12.5, NAVY, "bold", anchor="start"))
        b.append(text(px+pw-26, y+21, f"{pct}%", 12.5, NAVY if pct > 50 else GRAY, "bold", anchor="end"))
        b.append(f'<rect x="{px+28}" y="{y+30}" width="{(pw-56)}" height="10" rx="5" fill="{ICE}"/>')
        b.append(f'<rect x="{px+28}" y="{y+30}" width="{(pw-56)*pct/100}" height="10" rx="5" fill="{color}"/>')
        if focus:
            b.append(rrect(px+pw-98, y-14, 84, 22, TEAL, TEAL, 1, 11))
            b.append(text(px+pw-56, y+1, "오늘 집중", 11, WHITE, "bold"))
    b.append(arrow(ccx+cr+8, ccy, px-8, py+ph/2, TEAL, 2.4, "ahT"))
    b.append(text(W/2, 496, "성공률 높은 리드에 집중하게 한다 (Odoo 공식 소개자료) — 학습의 재료는 실패 데이터, 실주 기회도 반드시 기록한다", 12, GRAY))
    b.append(text(W/2, H-16, "2부 10장 — CRM·판매 (수치는 예시)", 11.5, GRAY))
    svg("fig_102_lead_scoring", W, H, "".join(b))

# ── 그림 11-1. 발주 자동화 사이클 ──────────────────────────────
def fig_111():
    W, H = 920, 760
    b = [text(W/2, 36, "발주 자동화 사이클", 24, NAVY, "bold"),
         text(W/2, 62, "재주문 규칙이 발주서 초안을 만들고, 사람은 승인과 예외 처리에 집중한다", 13.5, GRAY)]
    cx, cy, R = 460, 396, 235
    nodes = [
        ("재고 하한 감지", "예측 재고 < 최소치", False),
        ("RFQ 자동 생성", "복수 업체 동시 발송", False),
        ("업체 비교", "가격·납기 회신 대조", False),
        ("발주 확정(PO)", "사람의 승인 게이트", True),
        ("입고·3단계 대조", "PO·입고·청구서 검증", False),
        ("재고·회계 반영", "리드타임 실적 축적", False),
    ]
    bw, bh = 170, 58
    pos = []
    for i in range(6):
        a = math.radians(-90 + 60*i)
        pos.append((cx + R*math.cos(a), cy + R*math.sin(a)))
    # 화살표 (박스 바깥 원호)
    for i in range(6):
        a1 = math.radians(-90 + 60*i + 17)
        a2 = math.radians(-90 + 60*(i+1) - 17)
        am = math.radians(-90 + 60*i + 30)
        r1 = R + 54
        x1, y1 = cx + r1*math.cos(a1), cy + r1*math.sin(a1)
        x2, y2 = cx + r1*math.cos(a2), cy + r1*math.sin(a2)
        qx, qy = cx + (r1+24)*math.cos(am), cy + (r1+24)*math.sin(am)
        b.append(curve(x1, y1, qx, qy, x2, y2, TEAL, 2.6, "ahT"))
    for i, (t, sub, hitl) in enumerate(nodes):
        x, y = pos[i]
        stroke = ACC if hitl else NAVY
        b.append(rrect(x-bw/2, y-bh/2, bw, bh, ICE if not hitl else WHITE, stroke, 2 if hitl else 1.5, 9))
        b.append(text(x, y-5, t, 13, ACC if hitl else NAVY, "bold"))
        b.append(text(x, y+17, sub, 11, GRAY))
        if hitl:
            b.append(rrect(x-46, y+bh/2+10, 92, 26, ACC, ACC, 1, 13))
            b.append(text(x, y+bh/2+28, "HITL 승인", 11.5, WHITE, "bold"))
    b.append(circle(cx, cy, 96, NAVY))
    b.append(text(cx, cy-22, "발주 자동화", 17, WHITE, "bold"))
    b.append(text(cx, cy+2, "사이클", 17, WHITE, "bold"))
    b.append(multi(cx, cy+28, ["규칙은 집행하고", "사람은 판단한다"], 11.5, ICE2, 17))
    b.append(text(W/2, H-40, "한 회전마다 단가·리드타임·납기준수율의 실적이 쌓여, 다음 발주가 더 정확해진다", 12.5, GRAY))
    b.append(text(W/2, H-16, "2부 11장 — 매입(구매)", 11.5, GRAY))
    svg("fig_111_procure_cycle", W, H, "".join(b))

# ── 그림 11-2. 단일 소싱 리스크 네트워크도 ─────────────────────
def fig_112():
    W, H = 920, 620
    b = [text(W/2, 38, "단일 소싱 리스크 — 한 업체에만 이어진 품목", 23, NAVY, "bold"),
         text(W/2, 64, "품목-공급업체 연결망에서 대체 공급선이 없는 품목이 위험 노드다", 13.5, GRAY)]
    sup = [("업체 A", "납기준수율 94%", 186), ("업체 B", "납기준수율 88%", 326), ("업체 C", "납기준수율 76% · 하락", 466)]
    sx, sw, sh = 110, 168, 58
    b.append(text(sx+sw/2, 116, "공급업체", 13, GRAY, "bold"))
    for name, kpi, y in sup:
        warn = "76%" in kpi
        b.append(rrect(sx, y-sh/2, sw, sh, ICE2 if not warn else WHITE, NAVY if not warn else ACC, 1.5, 8))
        b.append(text(sx+sw/2, y-4, name, 13, NAVY, "bold"))
        b.append(text(sx+sw/2, y+16, kpi, 10.8, GRAY if not warn else ACC))
    items = [("P-101", 132, True, 0), ("P-102", 204, False, None), ("P-103", 276, False, None),
             ("P-104", 348, False, None), ("P-105", 420, True, 2), ("P-106", 492, True, 2)]
    ix, ir = 596, 30
    b.append(text(ix, 92, "품목", 13, GRAY, "bold"))
    edges = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (1, 3), (2, 3), (2, 4), (2, 5)]
    single = {(0, 0), (2, 4), (2, 5)}
    for s, t in edges:
        sy = sup[s][2]
        ty = items[t][1]
        risk = (s, t) in single
        b.append(line(sx+sw, sy, ix-ir-2, ty, ACC if risk else "#9AA3AE", 3 if risk else 1.4,
                      dash="" if risk else ""))
    for name, y, risk, _ in items:
        b.append(circle(ix, y, ir, ACC if risk else ICE, ACC if risk else NAVY, 1.6))
        b.append(text(ix, y+4.5, name, 11.5, WHITE if risk else NAVY, "bold"))
    # 콜아웃
    b.append(rrect(700, 384, 200, 118, WHITE, ACC, 1.5, 9, dash="6,5"))
    b.append(multi(800, 414, ["P-105 · P-106은", "업체 C가 멈추면", "함께 멈춘다", "— 결품 직결"], 12, ACC, 20, w="bold"))
    b.append(curve(696, 430, 668, 440, 634, 454, ACC, 1.8, "ahA", "4,3"))
    # 범례
    ly = 560
    b.append(circle(300, ly-4, 9, ACC))
    b.append(text(316, ly, "단일 소싱 품목 (위험 노드)", 12, GRAY, anchor="start"))
    b.append(circle(560, ly-4, 9, ICE, NAVY, 1.5))
    b.append(text(576, ly, "복수 소싱 품목", 12, GRAY, anchor="start"))
    b.append(text(W/2, 592, "납기준수율 추세 악화 + 리드타임 분산 확대 + 단일 소싱이 겹치면 '의존도를 낮춰야 한다'는 선제 경고가 된다", 12, GRAY))
    svg("fig_112_sourcing_risk", W, H, "".join(b))

# ── 그림 12-2. 로케이션 체계 창고 평면도 ───────────────────────
def fig_122():
    W, H = 960, 620
    b = [text(W/2, 38, "로케이션 체계 — 실물의 번지와 시스템의 번지는 하나다", 22, NAVY, "bold"),
         text(W/2, 64, "선반의 번지 라벨과 위치 마스터의 레코드가 같은 체계를 쓴다", 13.5, GRAY)]
    # 좌: 창고 평면도
    lx, ly, lw, lh = 40, 92, 560, 440
    b.append(rrect(lx, ly, lw, lh, WHITE, NAVY, 2, 6))
    b.append(text(lx+lw/2, ly+26, "실물 창고 — 선반의 번지", 14, NAVY, "bold"))
    b.append(rrect(lx+20, ly+60, 88, 130, LGRAY, GRAY, 1.2, 6, dash="5,4"))
    b.append(text(lx+64, ly+130, "입고장", 12, GRAY))
    b.append(rrect(lx+20, ly+250, 88, 130, LGRAY, GRAY, 1.2, 6, dash="5,4"))
    b.append(text(lx+64, ly+320, "출하장", 12, GRAY))
    rows = [("A", ly+62), ("B", ly+186), ("C", ly+310)]
    for rn, ry in rows:
        b.append(text(lx+128, ry+44, rn+"열", 12, GRAY, "bold"))
        for c in range(3):
            x = lx + 150 + c*136
            code = f"{rn}-0{c+1}"
            hot = (rn == "A" and c == 2)
            if hot:
                b.append(rrect(x, ry, 128, 76, WHITE, TEAL, 2.5, 4))
                for lvl in range(3):
                    yy = ry + 4 + lvl*23
                    if lvl == 1:
                        b.append(rrect(x+4, yy, 120, 21, TEAL, TEAL, 0.5, 2))
                        b.append(text(x+40, yy+15, "A-03-2", 12, WHITE, "bold"))
                        for k in range(7):
                            b.append(line(x+78+k*5, yy+5, x+78+k*5, yy+16, WHITE, 1.6 if k % 2 else 0.8))
                    else:
                        b.append(rrect(x+4, yy, 120, 21, LGRAY, GRAY, 0.5, 2))
                        b.append(text(x+64, yy+15, f"A-03-{3-lvl}", 10.8, GRAY))
            else:
                b.append(rrect(x, ry, 128, 76, ICE, NAVY, 1.2, 4))
                b.append(text(x+64, ry+44, code, 12.5, NAVY, "bold"))
    b.append(text(lx+lw/2, ly+426, "선반마다 번지 라벨(바코드) 부착", 11.5, GRAY))
    # 우: 위치 마스터 트리
    rx0, ry0, rw, rh = 630, 92, 290, 440
    b.append(rrect(rx0, ry0, rw, rh, LGRAY, GRAY, 1.4, 8))
    b.append(text(rx0+rw/2, ry0+26, "Odoo 위치 마스터", 14, NAVY, "bold"))
    tree = [("WH — 창고", 0, False), ("WH/스톡 — 보관 구역", 1, False), ("A열 — 랙 구역", 2, False),
            ("A-03 — 랙", 3, False), ("A-03-2 — 칸", 4, True)]
    ty0 = ry0 + 52
    prev = None
    for i, (label, depth, hot) in enumerate(tree):
        x = rx0 + 16 + depth*13
        y = ty0 + i*62
        w = rw - 32 - depth*13
        if prev:
            b.append(line(x-7, prev[1]+44, x-7, y+22, GRAY, 1.2))
            b.append(line(x-7, y+22, x-1, y+22, GRAY, 1.2))
        if hot:
            b.append(rrect(x, y, w, 46, TEAL, TEAL, 1.5, 7))
            b.append(text(x+12, y+20, label, 12.5, WHITE, "bold", anchor="start"))
            b.append(text(x+12, y+38, "바코드 라벨 = 위치 레코드", 10.8, "#D9F0EE", anchor="start"))
        else:
            b.append(rrect(x, y, w, 44, WHITE, NAVY, 1.2, 7))
            b.append(text(x+12, y+27, label, 12, NAVY, anchor="start"))
        prev = (x, y)
    # 1:1 대응
    hotx, hoty = lx+150+2*136+124, rows[0][1]+38
    b.append(curve(hotx+4, hoty, 614, 260, rx0+16+4*13-10, ty0+4*62+23, TEAL, 2.4, "ahT", "7,5"))
    b.append(rrect(556, 236, 116, 30, WHITE, TEAL, 1.4, 15))
    b.append(text(614, 256, "1 : 1 대응", 12.5, TEAL, "bold"))
    b.append(text(W/2, 566, "구획선 없는 바닥에 위치 코드를 부여하는 것은 주소 없는 골목에 우편번호를 붙이는 일이다", 12.5, GRAY))
    b.append(text(W/2, H-16, "2부 12장 — 재고 관리: 물리·디지털 정위치의 통합", 11.5, GRAY))
    svg("fig_122_location", W, H, "".join(b))

# ── 그림 12-3. 피킹 전략 3종 동선 비교 ─────────────────────────
def fig_123():
    W, H = 980, 640
    b = [text(W/2, 38, "피킹 전략 3종의 동선 비교", 24, NAVY, "bold"),
         text(W/2, 64, "원리는 하나 — 한 번의 창고 왕복으로 처리하는 주문 수를 늘린다 (동선은 개념 예시)", 13.5, GRAY)]
    panels = [("① 단일 주문 피킹", "주문 1건씩 별도 왕복 × 3회"),
              ("② 클러스터 피킹", "카트 칸별 3주문 동시 · 왕복 1회"),
              ("③ 웨이브 피킹", "구역 분할 · 작업자 2명 병렬")]
    pw, ph, gap, py = 296, 310, 16, 100
    x0 = (W - (pw*3 + gap*2)) / 2
    dists = [("100%", 236, ACC), ("약 65%", 154, TEAL), ("약 70%", 165, TEAL)]
    for p, (t, sub) in enumerate(panels):
        px = x0 + p*(pw+gap)
        b.append(rrect(px, py, pw, ph, WHITE, NAVY, 1.6, 8))
        b.append(text(px+pw/2, py+26, t, 13.5, NAVY, "bold"))
        b.append(text(px+pw/2, py+46, sub, 11, GRAY))
        # 랙 3열
        for r in range(3):
            ry = py + 70 + r*58
            b.append(rrect(px+58, ry, 180, 22, LGRAY, GRAY, 1, 3))
            b.append(text(px+48, ry+16, f"랙{r+1}", 10.8, GRAY, anchor="end"))
        # 패킹 스테이션
        sx, sy = px+pw/2, py+262
        b.append(rrect(sx-34, sy-14, 68, 28, ICE2, NAVY, 1.2, 5))
        b.append(text(sx, sy+5, "패킹", 11.5, NAVY, "bold"))
        rack_y = [py+70+r*58+11 for r in range(3)]
        if p == 0:  # 단일: 3회 왕복
            for k in range(3):
                dx = (k-1)*16
                yr = rack_y[k]
                b.append(f'<path d="M{sx+dx},{sy-16} L{sx+dx},{yr+18} L{px+70+k*30},{yr+18}" '
                         f'fill="none" stroke="#8A93A0" stroke-width="1.8"/>')
                b.append(f'<path d="M{px+70+k*30},{yr+24} L{sx+dx+6},{yr+24} L{sx+dx+6},{sy-16}" '
                         f'fill="none" stroke="#8A93A0" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#ahG)"/>')
            b.append(text(px+pw-30, py+250, "왕복 3회", 11.5, ACC, "bold", anchor="end"))
        elif p == 1:  # 클러스터: 한 번의 S자 순회
            path = (f'M{sx+10},{sy-16} L{px+244},{sy-16} L{px+244},{rack_y[2]+22} '
                    f'L{px+44},{rack_y[2]+22} L{px+44},{rack_y[1]+22} L{px+244},{rack_y[1]+22} '
                    f'L{px+244},{rack_y[0]+22} L{px+44},{rack_y[0]+22} '
                    f'L{px+30},{rack_y[0]+22} L{px+30},{sy-16} L{sx-46},{sy-16}')
            b.append(f'<path d="{path}" fill="none" stroke="{TEAL}" stroke-width="2.6" marker-end="url(#ahT)"/>')
            midy = (rack_y[0]+rack_y[1])/2 + 22
            b.append(rrect(px+241, midy-10, 42, 20, TEAL, TEAL, 1, 4))
            b.append(text(px+262, midy+4, "카트", 10.8, WHITE, "bold"))
            b.append(text(px+36, py+276, "왕복 1회", 11.5, TEAL, "bold", anchor="start"))
        else:  # 웨이브: 구역 분할 2인
            b.append(line(px+pw/2, py+74, px+pw/2, py+238, GRAY, 1.2, "6,5"))
            b.append(text(px+pw/2-46, py+68, "1구역", 11, GRAY))
            b.append(text(px+pw/2+46, py+68, "2구역", 11, GRAY))
            p1 = (f'M{sx-20},{sy-16} L{px+80},{rack_y[2]+22} L{px+80},{rack_y[0]+22} '
                  f'L{px+128},{rack_y[0]+22} L{px+128},{sy-24}')
            p2 = (f'M{sx+20},{sy-16} L{px+216},{rack_y[2]+22} L{px+216},{rack_y[0]+22} '
                  f'L{px+168},{rack_y[0]+22} L{px+168},{sy-24}')
            b.append(f'<path d="{p1}" fill="none" stroke="{TEAL}" stroke-width="2.4" marker-end="url(#ahT)"/>')
            b.append(f'<path d="{p2}" fill="none" stroke="{TEAL}" stroke-width="2.4" marker-end="url(#ahT)"/>')
            b.append(circle(px+80, rack_y[2]+22, 6, NAVY))
            b.append(circle(px+216, rack_y[2]+22, 6, NAVY))
        # 이동 거리 바
        by = py + ph + 22
        dtxt, dw, dc = dists[p]
        b.append(text(px+30, by+13, "이동 거리", 11.5, GRAY, anchor="start"))
        b.append(f'<rect x="{px+30}" y="{by+22}" width="236" height="14" rx="7" fill="{LGRAY}"/>')
        b.append(f'<rect x="{px+30}" y="{by+22}" width="{dw}" height="14" rx="7" fill="{dc}"/>')
        b.append(text(px+30+dw+8, by+34, dtxt, 11.5, dc, "bold", anchor="start"))
    b.append(rrect((W-720)/2, 500, 720, 52, ICE, NAVY, 1.4, 10))
    b.append(text(W/2, 526, "올바른 전략을 쓰면 같은 인원으로 피킹·포장 효율 최대 30% 향상", 14, NAVY, "bold"))
    b.append(text(W/2, 544, "(Odoo 공식 소개자료)", 11, GRAY))
    b.append(text(W/2, 582, "피킹은 창고 운영 비용의 절반 이상, 그 대부분이 이동 시간이다 (de Koster et al., 2007)", 12, GRAY))
    b.append(text(W/2, H-16, "2부 12장 — 재고 관리", 11.5, GRAY))
    svg("fig_123_picking", W, H, "".join(b))

fig_82(); fig_91(); fig_92(); fig_101(); fig_102(); fig_111(); fig_112(); fig_122(); fig_123()
print("완료")
