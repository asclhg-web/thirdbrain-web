#!/usr/bin/env python3
"""3순위 보조 도해 — 프롤로그·1~4장 담당분 11점 (P-1, P-4, 1-1, 1-2, 1-3, 2-1, 2-2, 3-2, 3-3, 4-1, 4-3)."""
from figlib import *

# ── 그림 P-1. 30년의 진화: 관리판에서 예측 플랫폼으로 ──────────
def fig_p1():
    W, H = 960, 440
    eras = [
        ("1990년대", "관리판·3정5S", "현장의 규율", NAVY,
         ["벽의 관리판·작업 카드", "눈으로 보는 관리", "사람이 걸어서 확인"]),
        ("2000년대", "ERP 전산화", "기록의 통합", NAVY,
         ["전표 → 데이터베이스", "월말 결산 며칠 → 하루", "기록은 디지털, 판단은 사람"]),
        ("2010년대", "스마트공장 DX", "실시간 수집", TEAL,
         ["바코드·POP·IoT", "대시보드 가시화", "다수가 기초 수준에 머묾"]),
        ("2020년대~", "LLM 예측 플랫폼 AX", "판단의 지능화", TEAL,
         ["언어를 다루는 AI", "수집→학습→추론→환류", "스스로 정확해지는 예측"]),
    ]
    b = [text(W/2, 40, "30년의 진화 — 관리판에서 예측 플랫폼으로", 24, NAVY, "bold"),
         text(W/2, 66, "원리는 같다: 보이게 만든 자에게만 현장은 말을 건다", 13.5, GRAY)]
    axis_y = 128
    b.append(arrow(50, axis_y, 925, axis_y, GRAY, 2, "ahG"))
    xs = [150, 370, 590, 810]
    for (era, name, essence, col, lines), cx in zip(eras, xs):
        b.append(circle(cx, axis_y, 9, col))
        b.append(text(cx, axis_y - 16, era, 13, col, "bold"))
        bw, bh = 200, 168
        y = axis_y + 30
        b.append(rrect(cx - bw/2, y, bw, bh, ICE if col == NAVY else TEALBG, col, 1.6, 10))
        b.append(line(cx, axis_y + 9, cx, y, col, 1.4))
        b.append(text(cx, y + 30, name, 14.5, col, "bold"))
        b.append(text(cx, y + 52, essence, 12, ACC if name.endswith("AX") else GRAY, "bold"))
        b.append(line(cx - bw/2 + 18, y + 64, cx + bw/2 - 18, y + 64, ICE2, 1))
        b.append(multi(cx, y + 88, lines, 11.5, GRAY, 22))
    b.append(text(W/2, H - 46, "기록의 시대에서 판단의 시대로 — 30년의 원칙을 데이터의 세계로 옮기는 것이 AX다", 12.5, NAVY, "bold"))
    b.append(text(W/2, H - 18, "프롤로그 — 왜 지금, 지능형 AI ERP인가", 11.5, GRAY))
    svg("fig_P1_timeline", W, H, "".join(b))

# ── 그림 P-4. 눈으로 보는 관리 3단계 진화 계단도 ────────────────
def fig_p4():
    W, H = 940, 520
    steps = [
        ("1단계 · 보이는 공장", "상태를 화면에 띄운다", ICE, NAVY,
         ["칸반 보드 = 디지털 관리판", "대시보드 = 디지털 안돈", "단, 사람이 봐야 발견된다"]),
        ("2단계 · 말하는 공장", "데이터가 먼저 말을 건다", ICE2, NAVY,
         ["이상 감지·자동 경보", "아침 한 문장 브리핑", "시선 없이도 즉시 발견"]),
        ("3단계 · 추론하는 공장", "원인을 찾고 미래를 내다본다", TEAL, WHITE,
         ["불량 원인 역추적", "납기 What-if 시뮬레이션", "디지털 트윈에 내일을 묻다"]),
    ]
    b = [text(W/2, 40, "눈으로 보는 관리의 3단계 진화", 24, NAVY, "bold"),
         text(W/2, 66, "목적은 같다 — 이상 발생과 발견 사이의 시간을 최소로 만드는 것", 13.5, GRAY)]
    bw, bh = 268, 150
    xs = [60, 336, 612]
    ys = [330, 235, 140]
    for (t, sub, fill, tc, lines), x, y in zip(steps, xs, ys):
        # 계단 받침
        b.append(rrect(x, y + bh, bw, 490 - (y + bh), LGRAY, LGRAY, 0, 4))
        b.append(rrect(x, y, bw, bh, fill, NAVY if fill != TEAL else TEAL, 1.8, 10))
        b.append(text(x + bw/2, y + 30, t, 16, tc, "bold"))
        b.append(text(x + bw/2, y + 52, sub, 12, ICE2 if fill == TEAL else TEAL, "bold"))
        b.append(multi(x + bw/2, y + 80, lines, 11.5, ICE if tc == WHITE else GRAY, 22))
    b.append(arrow(xs[0] + bw + 4, ys[0] + 40, xs[1] - 6, ys[1] + 110, TEAL, 2.5, "ahT"))
    b.append(arrow(xs[1] + bw + 4, ys[1] + 40, xs[2] - 6, ys[2] + 110, TEAL, 2.5, "ahT"))
    b.append(text(W/2, H - 14, "프롤로그 — '보는 주체'에 AI가 더해지고, '보는 시제'에 미래가 더해진다", 11.5, GRAY))
    svg("fig_P4_3stage", W, H, "".join(b))

# ── 그림 1-1. ERP 진화 연대기 ──────────────────────────────────
def fig_11():
    W, H = 980, 530
    gens = [
        ("MRP", "1960~70년대", ["자재 소요 계산의", "자동화 — 부품전개"], ["무한능력 가정", "데이터 부정확에 취약"]),
        ("MRP II", "1980년대", ["제조 자원의", "폐쇄 루프 계획"], ["제조 바깥 부문과의", "단절 (정보의 섬)"]),
        ("ERP", "1990년대", ["전사 프로세스·데이터", "통합 — 하나의 원장"], ["시스템 논리와", "경영 논리의 충돌"]),
        ("확장·클라우드", "2000~2010년대", ["기업 경계의 확장", "SaaS로 문턱 하락"], ["데이터는 느는데", "판단 능력은 정체"]),
        ("AI ERP", "2020년대~", ["판단의 지능화", "(진행 중)"], ["의미 통합·신뢰성", "— 이 책의 주제"]),
    ]
    b = [text(W/2, 40, "ERP 진화 연대기 — 각 세대가 해결한 문제와 남긴 한계", 23, NAVY, "bold"),
         text(W/2, 66, "각 세대는 앞 세대가 남긴 잔여의 문제를 물려받으며 태어났다", 13.5, GRAY)]
    axis_y = 128
    b.append(arrow(30, axis_y, 955, axis_y, GRAY, 2, "ahG"))
    cw, gap = 176, 12
    x0 = (W - 5*cw - 4*gap) / 2
    for i, (name, period, solved, limit) in enumerate(gens):
        cx = x0 + i*(cw + gap) + cw/2
        col = TEAL if i == 4 else NAVY
        b.append(circle(cx, axis_y, 8, col))
        b.append(text(cx, axis_y - 14, period, 11.5, col, "bold"))
        y1 = axis_y + 32
        b.append(line(cx, axis_y + 8, cx, y1, col, 1.3))
        b.append(rrect(cx - cw/2, y1, cw, 44, col, col, 1.5, 9))
        b.append(text(cx, y1 + 28, name, 15, WHITE, "bold"))
        y2 = y1 + 58
        b.append(rrect(cx - cw/2, y2, cw, 96, ICE, TEAL, 1.4, 9))
        b.append(text(cx, y2 + 24, "해결한 문제", 11.5, TEAL, "bold"))
        b.append(multi(cx, y2 + 50, solved, 11.5, DARK, 21))
        y3 = y2 + 110
        b.append(rrect(cx - cw/2, y3, cw, 96, WHITE, ACC, 1.4, 9, dash="6,4"))
        b.append(text(cx, y3 + 24, "남긴 한계", 11.5, ACC, "bold"))
        b.append(multi(cx, y3 + 50, limit, 11.5, GRAY, 21))
        if i < 4:
            b.append(arrow(cx + cw/2 + 1, y3 + 48, cx + cw/2 + gap - 1, y3 + 48, ACC, 1.8, "ahA", "4,3"))
    b.append(text(W/2, H - 44, "기록 능력은 완성으로 향했으나 판단 능력은 정체되었다 — 한계가 다음 세대를 낳는다", 12.5, NAVY, "bold"))
    b.append(text(W/2, H - 16, "1부 1장 — ERP 50년과 지능형 ERP", 11.5, GRAY))
    svg("fig_11_erp_timeline", W, H, "".join(b))

# ── 그림 1-2. 동기생산(간판) × ERP 역할 분담 ───────────────────
def fig_12():
    W, H = 940, 600
    b = [text(W/2, 40, "동기생산 × ERP — 경쟁이 아니라 역할 분담", 23, NAVY, "bold"),
         text(W/2, 66, "ERP가 큰 계획을 세우고, 현장의 풀(pull)이 그것을 실시간으로 동기화한다", 13.5, GRAY)]
    bx, bw = 130, 620
    # ERP 층
    b.append(rrect(bx, 100, bw, 110, NAVY, NAVY, 1.6, 10))
    b.append(text(bx + bw/2, 132, "ERP — 전사의 계획 (위에서 아래로, push)", 16, WHITE, "bold"))
    b.append(text(bx + bw/2, 160, "수주 관리 · 소요량 전개(MRP) · 조달 · 대일정계획", 12.5, ICE2))
    b.append(text(bx + bw/2, 184, "중앙의 계산 — 전사가 같은 숫자를 본다", 11.5, ICE2))
    # 동기화 지점
    b.append(rrect(bx, 270, bw, 96, ICE, TEAL, 1.8, 10))
    b.append(text(bx + bw/2, 302, "동기화 지점 — 중일정·실행", 15, TEAL, "bold"))
    b.append(text(bx + bw/2, 330, "계획과 현장이 실시간으로 맞물린다 = 동기(同期)생산", 12, GRAY))
    # 현장 풀 층
    b.append(rrect(bx, 426, bw, 110, TEAL, TEAL, 1.6, 10))
    b.append(text(bx + bw/2, 458, "현장 — 풀(pull)의 실행 (아래에서 위로)", 16, WHITE, "bold"))
    b.append(text(bx + bw/2, 486, "간판 · 후공정 인수 · 필요한 것을 필요한 때 필요한 만큼", 12.5, "#D9F0EE"))
    b.append(text(bx + bw/2, 510, "현장의 자율 — 실적·이상이 즉시 신호가 된다", 11.5, "#D9F0EE"))
    # 화살표: 계획은 아래로, 신호는 위로
    b.append(arrow(bx + 150, 214, bx + 150, 264, NAVY, 3))
    b.append(text(bx + 150 - 12, 244, "계획", 12, NAVY, "bold", anchor="end"))
    b.append(arrow(bx + 150, 370, bx + 150, 420, NAVY, 3))
    b.append(arrow(bx + bw - 150, 422, bx + bw - 150, 372, TEAL, 3, "ahT"))
    b.append(text(bx + bw - 150 + 12, 400, "풀 신호·실적", 12, TEAL, "bold", anchor="start"))
    b.append(arrow(bx + bw - 150, 266, bx + bw - 150, 216, TEAL, 3, "ahT"))
    # 우측 도구 태그
    tags = [("Odoo MRP·MPS", 128), ("frePPLe 동기화", 292), ("칸반·POP 태블릿", 454)]
    for t, y in tags:
        b.append(rrect(775, y, 150, 40, LGRAY, GRAY, 1.2, 8))
        b.append(text(850, y + 25, t, 11.5, GRAY, "bold"))
    b.append(text(W/2, H - 42, "중앙의 계산(push)과 현장의 자율(pull)이 층을 나누어 맞물린다 — 후쿠시마 『동기ERP』의 사상", 12.5, NAVY, "bold"))
    b.append(text(W/2, H - 16, "1부 1장 — 다품종소량·수주생산의 정답에 가장 가까운 분업", 11.5, GRAY))
    svg("fig_12_sync_erp", W, H, "".join(b))

# ── 그림 1-3. 지능형 ERP 5대 요건 오각형 ───────────────────────
def fig_13():
    W, H = 940, 660
    cx, cy, R = 470, 350, 158
    reqs = [
        ("① 단일 데이터 원천", "하나의 마스터·하나의 원장(SSOT)", "뿌리: ERP 통합·기준정보"),
        ("② 의미 기반 통합", "코드체계·온톨로지로 의미 연결", "뿌리: 눈으로 보는 관리"),
        ("③ 실시간 수집", "발생한 그 자리·그 순간에 기록", "뿌리: POP 생산시점관리"),
        ("④ 학습·추론 루프", "수집→학습→추론→환류의 상시화", "뿌리: QC 스토리·DMAIC"),
        ("⑤ 인간 협업", "HITL 승인 게이트·경험의 환류", "뿌리: 자율협조 생산방식"),
    ]
    b = [text(W/2, 40, "지능형 ERP의 5대 요건", 24, NAVY, "bold"),
         text(W/2, 66, "어느 것도 신개념이 아니다 — 다섯 모두 한 세대 전 현장 원칙의 디지털 확장이다", 13.5, GRAY)]
    import math as m
    pts = []
    for i in range(5):
        a = m.radians(-90 + i * 72)
        pts.append((cx + R * m.cos(a), cy + R * m.sin(a)))
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    b.append(f'<polygon points="{poly}" fill="{ICE}" fill-opacity="0.55" stroke="{ICE2}" stroke-width="2"/>')
    # 꼭짓점 → 중심 연결선
    for x, y in pts:
        b.append(line(cx, cy, x, y, ICE2, 1.2))
    # 요건 박스 (꼭짓점 바깥쪽)
    boxpos = [(470, 128), (760, 268), (652, 545), (288, 545), (180, 268)]
    bw2, bh2 = 216, 84
    for (t, d, r), (px, py), (vx, vy) in zip(reqs, boxpos, pts):
        b.append(line(vx, vy, px, py, GRAY, 1, "3,3"))
    for (t, d, r), (px, py) in zip(reqs, boxpos):
        b.append(rrect(px - bw2/2, py - bh2/2, bw2, bh2, WHITE, NAVY, 1.6, 10))
        b.append(text(px, py - bh2/2 + 24, t, 13.5, NAVY, "bold"))
        b.append(text(px, py - bh2/2 + 46, d, 11, GRAY))
        b.append(text(px, py - bh2/2 + 68, r, 11, TEAL))
    # 중앙 원
    b.append(circle(cx, cy, 74, NAVY))
    b.append(text(cx, cy - 8, "지능형 ERP", 17, WHITE, "bold"))
    b.append(text(cx, cy + 18, "기록을 넘어 판단으로", 11, ICE2))
    b.append(text(W/2, H - 16, "1부 1장 — 기록하는 시스템(SoR)에서 판단하는 시스템(SoI)으로", 11.5, GRAY))
    svg("fig_13_pentagon", W, H, "".join(b))

# ── 그림 2-1. 5S 다섯 걸음 계단도 ──────────────────────────────
def fig_21():
    W, H = 980, 620
    steps = [
        ("정리", "整理 · 버린다", ["빨간 패 작전", "불용품 폐기"], ["불용·중복 코드", "보관(archive) 처리"]),
        ("정돈", "整頓 · 자리를 준다", ["번지·구획·정위치", "찾기 로스 격감"], ["코드체계 정비", "1품목 1코드"]),
        ("청소", "淸掃 · 닦으며 점검", ["청소는 곧 점검", "미결함을 드러낸다"], ["오류·결측 클렌징", "재고 실사"]),
        ("청결", "淸潔 · 상태를 지킨다", ["발생원 차단", "규정의 활성화"], ["입력 규정·검증 규칙", "승인 게이트"]),
        ("습관화", "예절 · 몸에 배게", ["예외 없이 지킨다", "경영자가 평가"], ["발생 시점 입력", "품질 지표 정례화"]),
    ]
    b = [text(W/2, 40, "5S 다섯 걸음 — 물리 현장과 데이터에 같은 순서로", 23, NAVY, "bold"),
         text(W/2, 66, "버리기 전에 자리 잡을 수 없고, 표준 없이 습관은 생기지 않는다 — 순서가 방법론이다", 13, GRAY)]
    x0, cw, gap = 96, 166, 8
    base = 330
    for i, (name, hanja, phy, dat) in enumerate(steps):
        x = x0 + i*(cw + gap)
        top = 262 - i*38
        fill = TEAL if i == 4 else ICE
        tc = WHITE if i == 4 else NAVY
        b.append(rrect(x, top, cw, base - top, fill, TEAL if i == 4 else NAVY, 1.5, 8))
        b.append(text(x + cw/2, top + 26, f"{i+1}. {name}", 15, tc, "bold"))
        b.append(text(x + cw/2, top + 47, hanja, 11, ICE2 if i == 4 else GRAY))
    b.append(curve(x0 + 30, 236, W/2, 96, x0 + 4*(cw+gap) + cw - 30, 96, TEAL, 2.2, "ahT", "6,4"))
    # 아래 2행: 물리 실행 / 데이터 실행
    rows = [("물리 5S", 356, NAVY, ICE, 2), ("데이터 5S", 448, TEAL, TEALBG, 3)]
    for label, ry, col, fill, idx in rows:
        b.append(rrect(10, ry, 78, 76, col, col, 1.3, 8))
        b.append(multi(49, ry + 32, label.split(" "), 12.5, WHITE, 20, w="bold"))
        for i, st in enumerate(steps):
            x = x0 + i*(cw + gap)
            b.append(rrect(x, ry, cw, 76, fill, col, 1.2, 8))
            b.append(multi(x + cw/2, ry + 30, st[idx], 11.5, DARK, 22))
    b.append(text(W/2, H - 46, "다섯 걸음이 곧 데이터 품질 방법론이다 — 5S 없이 AI 없다", 13, NAVY, "bold"))
    b.append(text(W/2, H - 18, "1부 2장 — 현장 진단과 3정5S: 데이터 품질의 원점", 11.5, GRAY))
    svg("fig_21_5s_steps", W, H, "".join(b))

# ── 그림 2-2. "같은 볼트, 세 개의 코드" 상황도 ─────────────────
def fig_22():
    W, H = 920, 560
    b = [text(W/2, 40, "같은 볼트, 세 개의 코드 — 데이터 정위치의 반례", 23, NAVY, "bold"),
         text(W/2, 66, "하나의 사실이 세 자리에 흩어지는 순간, 그 사실에 관한 진실은 어디에도 없다", 13.5, GRAY)]
    # 볼트 일러스트 (좌측)
    bx, by = 150, 250
    b.append(f'<polygon points="{bx-34},{by-20} {bx},{by-40} {bx+34},{by-20} {bx+34},{by+20} {bx},{by+40} {bx-34},{by+20}" '
             f'fill="{ICE2}" stroke="{NAVY}" stroke-width="2"/>')
    b.append(f'<rect x="{bx-11}" y="{by+38}" width="22" height="86" fill="{ICE}" stroke="{NAVY}" stroke-width="2"/>')
    for i in range(5):
        yy = by + 54 + i*14
        b.append(line(bx - 11, yy, bx + 11, yy, NAVY, 1.4))
    b.append(text(bx, by - 58, "실물은 하나", 14, NAVY, "bold"))
    b.append(text(bx, by + 150, "M8 육각볼트", 12.5, GRAY))
    # 세 개의 코드 카드
    cards = [
        ("자재팀 등록", "BOLT-M8-020", "장부 재고 120 EA", "이 코드로는 재고 과잉", NAVY, 110),
        ("구매팀 등록", "BT-M8-STD", "장부 재고 45 EA", "이 코드로는 어중간", NAVY, 240),
        ("설계 도면 등록", "볼트 M8 아연", "장부 재고 0 EA", "결품! → 긴급 발주", ACC, 370),
    ]
    for team, code, stock, eff, col, y in cards:
        b.append(rrect(380, y, 300, 92, WHITE, col, 1.6, 9))
        b.append(text(398, y + 26, team, 11.5, GRAY, anchor="start"))
        b.append(text(398, y + 50, code, 15, col, "bold", anchor="start"))
        b.append(text(398, y + 74, stock, 12, DARK, anchor="start"))
        b.append(arrow(bx + 70, by + 10, 374, y + 46, GRAY, 1.8, "ahG", "5,4"))
        b.append(text(700, y + 42, eff, 12, col if col == ACC else GRAY,
                      "bold" if col == ACC else "normal", anchor="start"))
    # 하단 결론
    b.append(rrect(70, 486, 780, 0, WHITE, WHITE, 0, 0)) if False else None
    b.append(text(W/2, 500, "장부 합계 165 EA — 그러나 어느 코드도 진실이 아니다. 남는 재고 옆에서 결품 발주가 나간다", 13, ACC, "bold"))
    b.append(text(W/2, 526, "처방: 데이터 정돈 — 1품목 1코드로 통합, 나머지 코드는 보관(archive) 처리 (2장 디지털 3정5S)", 12, TEAL, "bold"))
    b.append(text(W/2, H - 12, "1부 2장 — 정위치·정품·정량이 동시에 무너지는 대표 병리", 11.5, GRAY))
    svg("fig_22_bolt3codes", W, H, "".join(b))

# ── 그림 3-2. 종이 작업표 → 바코드 작업표 → 태블릿 POP ─────────
def fig_32():
    W, H = 960, 600
    panels = [
        ("① 종이 작업일보", LGRAY, GRAY,
         ["퇴근 전에 몰아서 기입", "사후 보고 — 액션 불가", "기억 보정·왜곡이 섞임"],
         "하루 뒤 (일 단위)", ["왜곡·누락 빈발", "— 아무도 보지 않는다"]),
        ("② 바코드 작업표", ICE, NAVY,
         ["착수·완료 시 그 자리에서 스캔", "식별 정보는 바코드에 사전 내장", "입력은 1초 — 수량만 키 입력"],
         "작업 직후 (준실시간)", ["식별 오류 소멸", "집계 자동화"]),
        ("③ 태블릿 POP", TEALBG, TEAL,
         ["작업 그 자체가 기록이 된다", "실적·품질·공수 동시 수집", "IoT로 측정값 입력도 자동"],
         "실시간 (초 단위)", ["공명정대한 공장", "작업일보 폐지"]),
    ]
    b = [text(W/2, 40, "데이터 수집의 3단 진화 — 종이에서 생산 시점 관리로", 23, NAVY, "bold"),
         text(W/2, 66, "입력 비용이 0에 가까워질수록 데이터는 진실에 가까워진다", 13.5, GRAY)]
    pw, gap = 280, 30
    x0 = (W - 3*pw - 2*gap) / 2
    py, ph = 100, 400
    for i, (t, fill, col, lines, timing, qual) in enumerate(panels):
        x = x0 + i*(pw + gap)
        b.append(rrect(x, py, pw, ph, fill, col, 1.8, 12))
        b.append(text(x + pw/2, py + 32, t, 15.5, col, "bold"))
        icx, icy = x + pw/2, py + 96
        if i == 0:  # 종이
            b.append(rrect(icx - 26, icy - 34, 52, 68, WHITE, GRAY, 1.6, 3))
            for k in range(4):
                b.append(line(icx - 16, icy - 18 + k*14, icx + 16, icy - 18 + k*14, GRAY, 1.6))
        elif i == 1:  # 바코드
            b.append(rrect(icx - 40, icy - 26, 80, 52, WHITE, NAVY, 1.6, 3))
            widths = [3, 2, 4, 2, 3, 5, 2, 3, 2, 4]
            xx = icx - 30
            for wbar in widths:
                b.append(f'<rect x="{xx}" y="{icy-16}" width="{wbar}" height="32" fill="{NAVY}"/>')
                xx += wbar + 3
        else:  # 태블릿
            b.append(rrect(icx - 34, icy - 30, 68, 60, DARK, DARK, 1.6, 7))
            b.append(rrect(icx - 27, icy - 23, 54, 40, TEALBG, TEAL, 1, 3))
            b.append(circle(icx, icy + 24, 2.6, WHITE))
        b.append(multi(x + pw/2, py + 172, lines, 11.5, DARK, 23))
        b.append(line(x + 20, py + 252, x + pw - 20, py + 252, col, 1, "3,3"))
        b.append(text(x + 20, py + 282, "입력 시점", 11.5, col, "bold", anchor="start"))
        b.append(text(x + 20, py + 304, timing, 11.5, DARK, anchor="start"))
        b.append(text(x + 20, py + 336, "데이터 특징", 11.5, col, "bold", anchor="start"))
        b.append(multi(x + 20, py + 358, qual, 11.5, DARK, 20, anchor="start"))
        if i < 2:
            b.append(arrow(x + pw + 3, py + ph/2, x + pw + gap - 3, py + ph/2, TEAL, 2.6, "ahT"))
    b.append(text(W/2, H - 46, "원칙: 중요 데이터는 바코드에 미리 넣고, 현장에는 스캔 한 번·터치 한 번만 요구한다", 12.5, NAVY, "bold"))
    b.append(text(W/2, H - 18, "1부 3장 — POP: 작업일보의 폐지와 공명정대한 공장", 11.5, GRAY))
    svg("fig_32_pop_evolution", W, H, "".join(b))

# ── 그림 3-3. '말하는 공장'의 아침 브리핑 모바일 목업 ──────────
def fig_33():
    W, H = 940, 620
    b = [text(W/2, 40, "'말하는 공장'의 아침 브리핑", 24, NAVY, "bold"),
         text(W/2, 66, "시스템이 이상을 먼저 감지하고, 맥락을 붙여, 자연어로 말을 건다", 13.5, GRAY)]
    # 폰 프레임
    px, py, pw, ph = 100, 100, 280, 460
    b.append(rrect(px, py, pw, ph, DARK, DARK, 2, 26))
    b.append(rrect(px + 12, py + 34, pw - 24, ph - 62, WHITE, "#C4CAD3", 1, 8))
    b.append(text(px + pw/2, py + 22, "07:30", 11, WHITE, "bold"))
    b.append(rrect(px + 12, py + 34, pw - 24, 34, NAVY, NAVY, 1, 8))
    b.append(f'<rect x="{px+12}" y="{py+52}" width="{pw-24}" height="16" fill="{NAVY}"/>')
    b.append(text(px + pw/2, py + 56, "아침 브리핑 — 말하는 공장", 12.5, WHITE, "bold"))
    bubbles = [
        ("납기 경보", ACC, ["OO정밀 브래킷 납기 D-2", "— 조립 2공정에서 대기 중"]),
        ("재고 부족", NAVY, ["알루미늄 원자재 가용 3일분", "— 발주 초안 생성해 두었습니다"]),
        ("품질 이상", NAVY, ["5번 품목 불량 2건 — 원인", "후보: 금형 마모(유사 3건)"]),
    ]
    by = py + 84
    for head, col, lines in bubbles:
        b.append(rrect(px + 24, by, 232, 74, ICE, col, 1.3, 10))
        b.append(text(px + 36, by + 22, head, 11.5, col, "bold", anchor="start"))
        b.append(multi(px + 36, by + 44, lines, 11, DARK, 18, anchor="start"))
        by += 88
    b.append(rrect(px + 24, by, 232, 56, TEAL, TEAL, 1.3, 10))
    b.append(text(px + 36, by + 23, "발주를 승인하시겠습니까?", 11.5, WHITE, "bold", anchor="start"))
    b.append(text(px + 36, by + 43, "[승인]  [보류]  [상세 보기]", 11, "#D9F0EE", anchor="start"))
    # 우측 3층 구조 주석
    layers = [
        ("① 이상 감지", "재고·진도·품질 지표가 관리 한계를", "벗어나면 이벤트 발생 (사람을 기다리지 않는다)", py + 100, py + 121),
        ("② 맥락 결합", "관련 수주·자재·과거 이력을 단일 DB와", "지식 계층에서 모아 붙인다 (n8n 워크플로)", py + 230, py + 209),
        ("③ 자연어 브리핑", "LLM이 한 문단으로 요약해 모바일로 발송,", "액션 후보 제시 — 승인(HITL)은 사람의 몫", py + 360, py + 370),
    ]
    for t, l1, l2, ly, ty in layers:
        b.append(rrect(470, ly, 400, 84, WHITE, NAVY, 1.5, 10))
        b.append(text(490, ly + 26, t, 13.5, NAVY, "bold", anchor="start"))
        b.append(multi(490, ly + 50, [l1, l2], 11.5, GRAY, 20, anchor="start"))
        b.append(curve(466, ly + 42, 420, (ly + 42 + ty) / 2, px + pw - 14, ty, TEAL, 1.8, "ahT", "5,4"))
    b.append(text(W/2, H - 16, "1부 3장 — 순찰이 '확인의 시간'에서 '대화의 시간'으로 바뀐다 (문안은 예시)", 11.5, GRAY))
    svg("fig_33_briefing", W, H, "".join(b))

# ── 그림 4-1. 구조형 부품표(BOM) 트리 ──────────────────────────
def fig_41():
    W, H = 960, 620
    b = [text(W/2, 40, "구조형 부품표(BOM) — 계층을 따라 소요량이 전개된다", 23, NAVY, "bold"),
         text(W/2, 66, "부모-자식-손자의 계층과 재고 공제가 '몇 개를, 언제'를 정확하게 만든다", 13.5, GRAY)]
    lvl_y = [110, 230, 350, 470]
    labels = ["완제품", "조립품(반제품)", "부품", "원자재"]
    for y, lab in zip(lvl_y, labels):
        b.append(text(40, y + 30, lab, 12, GRAY, "bold", anchor="start"))
        b.append(line(40, y + 44, 920, y + 44, LGRAY, 1, "2,4"))
    bw2, bh2 = 140, 50
    def node(cx, y, t, fill=ICE, col=NAVY, tc=None):
        b.append(rrect(cx - bw2/2, y, bw2, bh2, fill, col, 1.5, 8))
        b.append(text(cx, y + 31, t, 13, tc or col, "bold"))
    def edge(x1, y1, x2, y2, qty):
        b.append(line(x1, y1, x2, y2, GRAY, 1.5))
        b.append(circle((x1+x2)/2, (y1+y2)/2, 15, WHITE, LGRAY, 1))
        b.append(text((x1+x2)/2, (y1+y2)/2 + 4.5, qty, 11.5, TEAL, "bold"))
    # 노드 좌표
    A = (450, lvl_y[0]); B = (250, lvl_y[1]); C = (650, lvl_y[1])
    D1 = (140, lvl_y[2]); E1 = (360, lvl_y[2]); D2 = (560, lvl_y[2]); F = (760, lvl_y[2])
    R1 = (190, lvl_y[3])
    edge(A[0], A[1] + bh2, B[0], B[1], "×2"); edge(A[0], A[1] + bh2, C[0], C[1], "×1")
    edge(B[0], B[1] + bh2, D1[0], D1[1], "×4"); edge(B[0], B[1] + bh2, E1[0], E1[1], "×2")
    edge(C[0], C[1] + bh2, D2[0], D2[1], "×2"); edge(C[0], C[1] + bh2, F[0], F[1], "×3")
    edge(D1[0], D1[1] + bh2, R1[0], R1[1], "0.3m")
    node(A[0], A[1], "완제품 A", NAVY, NAVY, WHITE)
    node(B[0], B[1], "조립품 B", ICE2); node(C[0], C[1], "조립품 C", ICE2)
    node(D1[0], D1[1], "부품 D", TEALBG, TEAL); node(E1[0], E1[1], "부품 E")
    node(D2[0], D2[1], "부품 D", TEALBG, TEAL); node(F[0], F[1], "부품 F")
    node(R1[0], R1[1], "환봉 소재", LGRAY, GRAY)
    b.append(curve(D1[0] + 40, D1[1] + bh2 + 2, 360, lvl_y[2] + bh2 + 40, D2[0] - 40, D2[1] + bh2 + 2, TEAL, 1.6, "ahT", "5,4"))
    b.append(text(368, lvl_y[2] + bh2 + 68, "공통부품 — 계층이 달라도 합산 전개", 11.5, TEAL, "bold"))
    # 하단 정미소요량 계산
    b.append(rrect(80, 540, 800, 0, WHITE, WHITE, 0, 0)) if False else None
    b.append(rrect(90, 528, 780, 62, ICE, NAVY, 1.5, 10))
    b.append(text(W/2, 552, "정미소요량 계산 — 완제품 A 10대 주문 시 부품 D:  총소요 10×(2×4+1×2) = 100개", 12.5, NAVY, "bold"))
    b.append(text(W/2, 576, "재고 30개·발주잔량 20개 공제  →  정미소요 50개 (이 계산이 MRP의 심장이다)", 12, TEAL, "bold"))
    b.append(text(W/2, H - 10, "1부 4장 — Odoo 다단계 BOM: 반제품의 BOM이 상위 BOM에 중첩되는 구조형 그 자체", 11.5, GRAY))
    svg("fig_41_bom_tree", W, H, "".join(b))

# ── 그림 4-3. 공수 산적표 — 능력선 vs 부하 막대 ────────────────
def fig_43():
    W, H = 940, 580
    b = [text(W/2, 40, "공수 산적표 — 능력과 부하의 검산", 24, NAVY, "bold"),
         text(W/2, 66, "공수계획이 첨부되지 않은 일정계획은 그림의 떡이다 (수치는 예시)", 13.5, GRAY)]
    base, top = 460, 130
    x_axis0, x_axis1 = 110, 880
    cap = 160
    scale = (base - top) / 210.0
    # y축 눈금
    for v in (0, 50, 100, 150, 200):
        yy = base - v*scale
        b.append(line(x_axis0, yy, x_axis1, yy, LGRAY, 1))
        b.append(text(x_axis0 - 10, yy + 4, str(v), 11, GRAY, anchor="end"))
    b.append(text(46, (base+top)/2, "", 11))
    b.append(f'<text x="40" y="{(base+top)/2}" font-family="{F}" font-size="11.5" fill="{GRAY}" '
             f'text-anchor="middle" transform="rotate(-90 40 {(base+top)/2})">부하 공수 (시간/주)</text>')
    wcs = [("선반", 120), ("밀링", 145), ("용접", 195), ("조립", 130), ("도장", 85)]
    bar_w = 86
    xs = [180, 330, 480, 630, 780]
    cap_y = base - cap*scale
    for (name, v), cx in zip(wcs, xs):
        bar_top = base - v*scale
        if v > cap:
            b.append(rrect(cx - bar_w/2, cap_y, bar_w, base - cap_y, TEAL, TEAL, 1, 3))
            b.append(rrect(cx - bar_w/2, bar_top, bar_w, cap_y - bar_top, ACC, ACC, 1, 3))
            b.append(text(cx, bar_top - 10, f"{v}h", 13, ACC, "bold"))
            b.append(text(cx, base + 24, name, 13.5, ACC, "bold"))
            b.append(text(cx, base + 44, "← Neck 공정", 11.5, ACC, "bold"))
        else:
            b.append(rrect(cx - bar_w/2, bar_top, bar_w, base - bar_top, TEAL, TEAL, 1, 3))
            b.append(text(cx, bar_top - 10, f"{v}h", 12.5, GRAY, "bold"))
            b.append(text(cx, base + 24, name, 13.5, NAVY, "bold"))
    # 능력선
    b.append(line(x_axis0, cap_y, x_axis1, cap_y, NAVY, 2.5, "8,5"))
    b.append(text(x_axis0 + 8, cap_y - 10, "능력선 160h/주", 12, NAVY, "bold", anchor="start"))
    b.append(line(x_axis0, base, x_axis1, base, GRAY, 1.5))
    # Neck 주석 박스
    b.append(rrect(600, 116, 300, 96, WHITE, ACC, 1.6, 10))
    b.append(text(620, 142, "넥(Neck) 공정 — 부하 195h > 능력 160h", 12.5, ACC, "bold", anchor="start"))
    b.append(multi(620, 166, ["초과 35h가 전체 산출량과 납기를 결정한다", "대책: 잔업·응원·내외작 전환·로트 분할"],
                   11.5, GRAY, 20, anchor="start"))
    b.append(arrow(596, 170, 530, 150, ACC, 2, "ahA", "5,4"))
    b.append(text(W/2, H - 44, "실전은 중점주의 — 넥 공정의 공수계획만 정밀하면 전체 계획의 실행 가능성이 대략 보증된다", 12.5, NAVY, "bold"))
    b.append(text(W/2, H - 16, "1부 4장 — frePPLe의 자원별 부하 화면이 이 산적표의 디지털 대응물이다", 11.5, GRAY))
    svg("fig_43_load_chart", W, H, "".join(b))

fig_p1(); fig_p4(); fig_11(); fig_12(); fig_13(); fig_21(); fig_22(); fig_32(); fig_33(); fig_41(); fig_43()
print("완료")
