#!/usr/bin/env python3
"""2순위 그림 8점 SVG 생성 + PNG 변환."""
import os, cairosvg

OUT = os.path.dirname(os.path.abspath(__file__))
F = "NanumGothic"
NAVY = "#1E2761"; ICE = "#E8F0FB"; ICE2 = "#CADCFC"; TEAL = "#028090"
GRAY = "#5A6472"; LGRAY = "#EEF1F5"; ACC = "#B85042"; WHITE = "#FFFFFF"
DARK = "#454C57"

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def text(x, y, s, size=15, fill=NAVY, w="normal", anchor="middle"):
    return (f'<text x="{x}" y="{y}" font-family="{F}" font-size="{size}" '
            f'font-weight="{w}" fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>')

def multi(x, y, lines, size=13, fill=GRAY, lh=None, anchor="middle", w="normal"):
    lh = lh or size + 5
    return "".join(text(x, y + i * lh, s, size, fill, w, anchor) for i, s in enumerate(lines))

def rrect(x, y, w, h, fill, stroke=NAVY, sw=1.5, r=10, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

ARROW_DEFS = (f'<defs><marker id="ah" markerWidth="10" markerHeight="8" refX="8" refY="4" orient="auto">'
              f'<path d="M0,0 L9,4 L0,8 z" fill="{NAVY}"/></marker>'
              f'<marker id="ahT" markerWidth="10" markerHeight="8" refX="8" refY="4" orient="auto">'
              f'<path d="M0,0 L9,4 L0,8 z" fill="{TEAL}"/></marker>'
              f'<marker id="ahA" markerWidth="10" markerHeight="8" refX="8" refY="4" orient="auto">'
              f'<path d="M0,0 L9,4 L0,8 z" fill="{ACC}"/></marker></defs>')

def arrow(x1, y1, x2, y2, color=NAVY, sw=2, marker="ah", dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{sw}" marker-end="url(#{marker})"{d}/>')

def curve(x1, y1, cx, cy, x2, y2, color=NAVY, sw=2, marker="ah", dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M{x1},{y1} Q{cx},{cy} {x2},{y2}" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" marker-end="url(#{marker})"{d}/>')

def svg(name, w, h, body):
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
           f'viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="{WHITE}"/>'
           + ARROW_DEFS + body + "</svg>")
    p = os.path.join(OUT, name + ".svg")
    open(p, "w").write(doc)
    cairosvg.svg2png(url=p, write_to=os.path.join(OUT, name + ".png"), scale=2.5)
    print("생성:", name)

# ── 그림 P-2. 물리 3정5S ↔ 데이터 3정5S 대응도 ─────────────────
def fig_p2():
    W, H = 920, 700
    rows = [
        ("정위치", "정해진 자리에 보관한다", "코드체계 — 품목 하나에 코드 하나"),
        ("정품", "그 자리에는 정해진 물건만", "입력 규칙 — 필드에 정해진 값만"),
        ("정량", "정해진 양만큼 둔다", "실시간 수집·실사 — 장부 = 실물"),
        ("정리", "필요 없는 것을 버린다", "불용 코드·중복 코드 폐기"),
        ("정돈", "주소를 주고 표찰을 단다", "기준정보·코드체계 정비"),
        ("청소", "닦아내며 이상을 드러낸다", "오류·결측 데이터 클렌징"),
        ("청결", "오염을 예방하는 상태 유지", "검증 규칙·입력 통제"),
        ("습관화", "몸에 배게 한다", "현장이 데이터를 지키는 문화"),
    ]
    b = [text(W/2, 40, "물리의 3정5S ↔ 데이터의 3정5S", 24, NAVY, "bold"),
         text(W/2, 66, "한 세대 전 공장 바닥의 규율이 그대로 데이터 품질의 규율이 된다", 13.5, GRAY)]
    colL, colR, cw = 60, 530, 330
    b.append(rrect(colL, 92, cw, 40, NAVY, NAVY, 1.5, 8))
    b.append(text(colL+cw/2, 118, "물리적 현장 — 공장 바닥", 15, WHITE, "bold"))
    b.append(rrect(colR, 92, cw, 40, TEAL, TEAL, 1.5, 8))
    b.append(text(colR+cw/2, 118, "데이터의 세계 — 데이터베이스", 15, WHITE, "bold"))
    y0, rh = 150, 60
    for i, (k, l, r) in enumerate(rows):
        y = y0 + i*rh
        fill = ICE if i < 3 else LGRAY
        b.append(rrect(colL, y, cw, rh-10, fill, NAVY if i < 3 else GRAY, 1.3, 8))
        b.append(text(colL+52, y+31, k, 15, NAVY, "bold"))
        b.append(text(colL+72, y+31, l, 12, GRAY, anchor="start"))
        b.append(rrect(colR, y, cw, rh-10, fill, TEAL if i < 3 else GRAY, 1.3, 8))
        b.append(text(colR+18, y+31, r, 12, GRAY, anchor="start"))
        b.append(arrow(colL+cw+12, y+rh/2-5, colR-12, y+rh/2-5, TEAL, 2.2, "ahT"))
    b.append(text(W/2, y0+8*rh+22, "3정(위)은 상태의 기준, 5S(아래)는 그 상태에 이르는 다섯 걸음이다 — 5S 없이 AI 없다", 12.5, GRAY))
    svg("fig_P2_3jung5s", W, H, "".join(b))

# ── 그림 3-1. 관리판 → 칸반 보드 대응도 ────────────────────────
def fig_31():
    W, H = 960, 620
    b = [text(W/2, 40, "관리판에서 칸반 보드로 — 같은 원리, 다른 매체", 23, NAVY, "bold"),
         text(W/2, 66, "카드의 정보 구조(제번·도번·수량·납기)는 30년 전 그대로다", 13.5, GRAY)]
    # 좌: 벽걸이 관리판
    b.append(rrect(50, 95, 400, 400, "#F7F3EA", "#8B7D5A", 2.5, 6))
    b.append(text(250, 122, "벽걸이 관리판 (아날로그)", 15, "#6B5D3A", "bold"))
    cols = ["절단", "가공", "조립"]
    for i, c in enumerate(cols):
        x = 80 + i*115
        b.append(rrect(x, 140, 105, 30, "#EDE5D0", "#8B7D5A", 1.2, 4))
        b.append(text(x+52, 160, c + " 공정", 12.5, "#6B5D3A", "bold"))
        b.append(f'<line x1="{x}" y1="180" x2="{x}" y2="480" stroke="#C9BC9C" stroke-width="1"/>')
    cards = [(80, 185, "제번 A-102", "수량 50 · 납기 8.12"), (80, 250, "제번 A-105", "수량 30 · 납기 8.14"),
             (195, 185, "제번 A-098", "수량 120 · 납기 8.10"), (310, 315, "제번 A-091", "수량 80 · 납기 8.08")]
    for x, y, l1, l2 in cards:
        b.append(rrect(x+5, y, 95, 52, WHITE, "#8B7D5A", 1.3, 3))
        b.append(f'<circle cx="{x+14}" cy="{y+9}" r="4" fill="#8B7D5A"/>')
        b.append(text(x+52, y+24, l1, 11.5, NAVY, "bold"))
        b.append(text(x+52, y+42, l2, 10, GRAY))
    # 우: Odoo 칸반
    b.append(rrect(510, 95, 400, 400, WHITE, NAVY, 2, 10))
    b.append(rrect(510, 95, 400, 40, NAVY, NAVY, 2, 10))
    b.append(f'<rect x="510" y="115" width="400" height="20" fill="{NAVY}"/>')
    b.append(text(710, 121, "Odoo 칸반 보드 (디지털 관리판)", 14.5, WHITE, "bold"))
    kcols = ["대기", "진행 중", "완료"]
    for i, c in enumerate(kcols):
        x = 530 + i*122
        b.append(rrect(x, 150, 112, 26, ICE2, NAVY, 1, 6))
        b.append(text(x+56, 167, c, 12, NAVY, "bold"))
    kcards = [(530, 186, "WO/A-102", "50 EA · 8.12", TEAL), (530, 252, "WO/A-105", "30 EA · 8.14", TEAL),
              (652, 186, "WO/A-098", "120 EA · 8.10", "#C8860A"), (774, 318, "WO/A-091", "80 EA · 8.08", GRAY)]
    for x, y, l1, l2, cc in kcards:
        b.append(rrect(x, y, 112, 58, LGRAY, GRAY, 1, 6))
        b.append(f'<rect x="{x}" y="{y}" width="5" height="58" rx="2.5" fill="{cc}"/>')
        b.append(text(x+60, y+22, l1, 11.5, NAVY, "bold"))
        b.append(text(x+60, y+40, l2, 10, GRAY))
    b.append(curve(455, 215, 480, 195, 526, 212, TEAL, 2.2, "ahT", "6,4"))
    b.append(curve(455, 345, 480, 330, 770, 345, TEAL, 2.2, "ahT", "6,4"))
    b.append(text(W/2, 530, "달라진 것: 실시간 갱신 · 이력 자동 기록 · 어디서나 열람 · 경보와 연동", 12.5, TEAL, "bold"))
    b.append(text(W/2, 556, "“판이 곧 보고서였다 — 이제 화면이 곧 관리판이다”", 14, NAVY, "bold"))
    b.append(text(W/2, H-16, "1부 3장 — 눈으로 보는 관리에서 데이터로 보는 관리로", 11.5, GRAY))
    svg("fig_31_kanban", W, H, "".join(b))

# ── 그림 4-2. 대·중·소 일정계획 3층 구조 ───────────────────────
def fig_42():
    W, H = 960, 560
    layers = [
        ("대일정계획", "월 단위 · 1년", "수주~출하의 큰 흐름 · 능력·설비·인원의 대강", "경영·영업·생산관리", "Odoo MPS"),
        ("중일정계획", "주 단위 · 1~3개월", "공정별 부하·능력 조정 · 자재 수배 · 변경 흡수", "생산관리", "frePPLe APS"),
        ("소일정계획", "일 단위 · 1~3일", "작업자·설비 배정 · 작업 순서 · 발송(디스패칭)", "현장 직장", "작업현장 태블릿"),
    ]
    b = [text(W/2, 40, "대·중·소 일정계획의 3층 구조", 24, NAVY, "bold"),
         text(W/2, 66, "수주 변경은 중일정이 흡수하고, 소일정과 발송으로 즉시 전달된다", 13.5, GRAY)]
    y0, lh, gap = 100, 100, 16
    fills = [NAVY, TEAL, ICE2]
    for i, (t, cyc, desc, who, tool) in enumerate(layers):
        y = y0 + i*(lh+gap)
        tc = WHITE if i < 2 else NAVY
        sc = ICE2 if i < 2 else GRAY
        b.append(rrect(150, y, 620, lh, fills[i], NAVY, 1.6, 10))
        b.append(text(200, y+40, t, 17, tc, "bold", anchor="start"))
        b.append(text(200, y+66, desc, 12.5, sc, anchor="start"))
        b.append(rrect(40, y+22, 92, 56, LGRAY, GRAY, 1.2, 8))
        b.append(multi(86, y+45, cyc.split(" · "), 11.5, GRAY, 18))
        b.append(rrect(790, y+22, 130, 56, ICE, TEAL, 1.3, 8))
        b.append(text(855, y+44, who, 11.5, NAVY, "bold"))
        b.append(text(855, y+64, tool, 11, TEAL))
        if i < 2:
            b.append(arrow(460, y+lh+2, 460, y+lh+gap-2, NAVY, 2.5))
    ly = y0 + lh + gap + lh/2
    b.append(text(700, y0-12, "⚡ 수주 변경·특급 오더", 13, ACC, "bold"))
    b.append(curve(700, y0-4, 730, y0+60, 705, ly-18, ACC, 2.5, "ahA", "6,4"))
    b.append(curve(705, ly+18, 720, ly+80, 690, y0+2*(lh+gap)+18, ACC, 2.5, "ahA", "6,4"))
    b.append(text(W/2, H-20, "원칙: 변경은 위층을 다시 짜지 않고 중일정의 유연 수정으로 흡수한다 — 생산관리 고전 · 1부 4장", 12, GRAY))
    svg("fig_42_schedule3", W, H, "".join(b))

# ── 그림 12-1. 이중 기록 재고 개념 ─────────────────────────────
def fig_121():
    W, H = 920, 600
    b = [text(W/2, 40, "이중 기록 재고 — 재고는 사라지지 않는다, 위치를 바꿀 뿐이다", 21, NAVY, "bold"),
         text(W/2, 66, "복식부기가 돈의 흐름을 기록하듯, 하나의 이동이 두 위치에 동시에 기록된다", 13, GRAY)]
    b.append(rrect(120, 100, 280, 120, ICE, NAVY, 1.8, 10))
    b.append(text(260, 128, "위치 A — 자재창고", 14.5, NAVY, "bold"))
    b.append(f'<line x1="150" y1="145" x2="370" y2="145" stroke="{NAVY}" stroke-width="1"/>')
    b.append(text(260, 172, "출고  −100 EA", 16, ACC, "bold"))
    b.append(text(260, 198, "장부 잔량 400 → 300", 12, GRAY))
    b.append(rrect(520, 100, 280, 120, "#E5F4F3", TEAL, 1.8, 10))
    b.append(text(660, 128, "위치 B — 생산라인", 14.5, TEAL, "bold"))
    b.append(f'<line x1="550" y1="145" x2="770" y2="145" stroke="{TEAL}" stroke-width="1"/>')
    b.append(text(660, 172, "입고  +100 EA", 16, TEAL, "bold"))
    b.append(text(660, 198, "장부 잔량 0 → 100", 12, GRAY))
    b.append(arrow(404, 160, 516, 160, NAVY, 3))
    b.append(text(460, 145, "이동 전표 1건", 12, NAVY, "bold"))
    b.append(text(460, 246, "하나의 이동 = 두 위치의 동시 기록 → 수량은 시스템 안에서 보존된다", 13.5, NAVY, "bold"))
    chain = ["공급업체", "입고 구역", "자재창고", "생산라인", "출하 구역", "고객"]
    y, bw = 300, 128
    x0 = (W - (bw*6 + 10*5)) / 2
    for i, c in enumerate(chain):
        X = x0 + i*(bw+10)
        virt = i in (0, 5)
        b.append(rrect(X, y, bw, 64, LGRAY if virt else ICE, GRAY if virt else NAVY,
                       1.3, 8, dash="5,4" if virt else ""))
        b.append(text(X+bw/2, y+28, c, 13, GRAY if virt else NAVY, "bold"))
        b.append(text(X+bw/2, y+48, "가상 위치" if virt else "실물 위치", 10.5, GRAY))
        if i < 5:
            b.append(arrow(X+bw+1, y+32, X+bw+9, y+32, TEAL, 2, "ahT"))
    b.append(multi(W/2, 420, [
        "구매 입고 = (공급업체) → (입고 구역) 이동  ·  판매 출하 = (출하 구역) → (고객) 이동",
        "모든 증감이 '어디서 와서 어디로 갔는가'로 기록되므로, 수불부가 곧 추적 이력이 된다",
    ], 12.5, GRAY, 24))
    b.append(rrect(180, 480, 560, 60, ICE, NAVY, 1.4, 10))
    b.append(multi(W/2, 505, ["기대 효과: 재고 정확도의 구조적 보장 · 로트 추적성 · 실사 차이의 원인 규명"],
                   12.5, NAVY, w="bold"))
    b.append(text(W/2, H-16, "2부 12장 — 재고 관리: 물류의 컨설팅", 11.5, GRAY))
    svg("fig_121_double_entry", W, H, "".join(b))

# ── 그림 13-1. OEE 폭포 차트 ───────────────────────────────────
def fig_131():
    W, H = 960, 620
    b = [text(W/2, 40, "OEE 폭포 — 100%는 어디서 깎여 나가는가", 23, NAVY, "bold"),
         text(W/2, 66, "OEE = 가동률(A) × 성능(P) × 품질(Q) — 손실을 보이게 만드는 것이 개선의 출발", 13, GRAY)]
    x0, y0, bw, gap = 56, 110, 98, 14
    base, scale = 470, 3.2
    vals = [("총가용시간", 100, NAVY, None), ("계획 정지", -8, ACC, None), ("고장·준비교체", -14, ACC, None),
            ("가동시간", 78, ICE2, "가동률 A=78%"), ("속도 손실·소정지", -16, ACC, None),
            ("정미가동", 62, ICE2, "성능 P=79%"), ("불량·재작업", -7, ACC, None),
            ("OEE", 55, TEAL, "품질 Q=89%")]
    cum = 0; tops = {}
    for i, (label, v, color, note) in enumerate(vals):
        X = x0 + i*(bw+gap)
        if v > 0 and i > 0:
            cum = v
        prev = cum if i == 0 else cum
        if i == 0:
            cum = v
        h = abs(v)*scale
        if v > 0:
            top = base - v*scale
            b.append(rrect(X, top, bw, v*scale, color, NAVY, 1.2, 4))
            tc = WHITE if color in (NAVY, TEAL) else NAVY
            b.append(text(X+bw/2, top+22, f"{v}%", 14, tc, "bold"))
            tops[i] = top
        else:
            start_top = tops[max(k for k in tops)]
            top = start_top
            b.append(rrect(X, top, bw, h, color, "#8B3A30", 1.2, 4))
            b.append(text(X+bw/2, top+h/2+5, f"{v}%", 12.5, WHITE, "bold"))
            cum = cum + v
            tops[i] = top + h
        b.append(multi(X+bw/2, base+22, label.split("·"), 11.5, GRAY, 16))
        if note:
            b.append(text(X+bw/2, base+62, note, 11, TEAL, "bold"))
        if i < len(vals)-1:
            yy = tops[i]
            b.append(f'<line x1="{X+bw}" y1="{yy}" x2="{X+bw+gap}" y2="{yy}" stroke="{GRAY}" stroke-width="1" stroke-dasharray="3,3"/>')
    b.append(text(W/2, 560, "세계 수준 OEE는 85%, 국내 중소 제조 평균은 50~60%대 — 손실 구간이 곧 개선 과제 목록이다", 12.5, GRAY))
    b.append(text(W/2, H-16, "2부 13장 — 제조 관리: 생산의 컨설팅 (수치는 예시)", 11.5, GRAY))
    svg("fig_131_oee", W, H, "".join(b))

# ── 그림 18-1. ERP의 조명과 사각지대 ───────────────────────────
def fig_181():
    W, H = 940, 620
    b = [text(W/2, 40, "ERP의 조명과 경영 사각지대", 24, NAVY, "bold"),
         text(W/2, 66, "손실은 시스템이 비추지 않는 곳에서 발생한다", 14, ACC, "bold")]
    b.append(rrect(40, 95, 860, 430, DARK, DARK, 0, 14))
    b.append(f'<path d="M120,110 L60,510 L560,510 L420,110 z" fill="{ICE}" fill-opacity="0.95"/>')
    b.append(f'<circle cx="270" cy="122" r="18" fill="{NAVY}"/>')
    b.append(text(270, 88, "ERP의 조명 — 등록된 것만 비춘다", 13.5, NAVY, "bold"))
    lit = [("수주·발주 전표", 200, 200), ("재고 수불", 330, 260), ("BOM·작업지시", 190, 320), ("회계 분개", 320, 390)]
    for t, x, y in lit:
        b.append(rrect(x-85, y-22, 170, 44, WHITE, NAVY, 1.5, 8))
        b.append(text(x, y+5, t, 13, NAVY, "bold"))
    b.append(text(300, 470, "형식지 — 기록된 세계", 13, NAVY, "bold"))
    dark = [("베테랑의 감(感)", 700, 170), ("부서 사이의 관행", 740, 250), ("구두 결정·예외 처리", 690, 330), ("“원래 그렇게 해 왔다”", 730, 410)]
    for t, x, y in dark:
        b.append(rrect(x-105, y-22, 210, 44, "none", "#9AA3AE", 1.3, 8, dash="6,5"))
        b.append(text(x, y+5, t, 12.5, "#B8C0CA"))
    b.append(text(715, 470, "암묵지 — 사각지대", 13, "#B8C0CA", "bold"))
    leaks = [("결품·과잉재고", 620), ("중복 발주", 750), ("납기 지연·불량 재발", 870)]
    for t, x in leaks:
        b.append(arrow(x, 528, x, 560, ACC, 2.5, "ahA"))
        b.append(text(x, 580, t, 12, ACC, "bold"))
    b.append(text(W/2, H-14, "3부 18장 — 사각지대의 암묵지를 온톨로지로 발굴·통치하는 것이 AX의 마지막 관문이다", 12, GRAY))
    svg("fig_181_blindspot", W, H, "".join(b))

# ── 그림 19-1. JEDAIX 전체 파이프라인 ──────────────────────────
def fig_191():
    W, H = 940, 760
    layers = [
        ("입력 데이터", "ERP 트랜잭션 · 엑셀 · 현장의 대화 · 문서", LGRAY, None),
        ("Frame", "모든 회사에 공통인 메타데이터 스키마 — Universal Metadata 9속성", ICE2, None),
        ("6 Station 대화", "진단 → 분석 → 보고서 → 정책 → 규칙 → 업무논리 — 암묵지가 발화되는 場", ICE, None),
        ("PTGDA", "씨앗 → 가설 → 검증 → 확정 → 통치 — 점진적 암묵지 발굴 알고리즘", ICE, None),
        ("온톨로지 (OWL)", "확정된 Class·Property — 회사의 의미 구조", TEAL, WHITE),
        ("Agent Workflow", "슬롯 설계 · BPMN · 자동 검증 · 승인/반려 — 온톨로지가 실행 코드로", ICE2, None),
        ("Workspace 운영", "표준 프로세스 실행 · War Room 감시", NAVY, WHITE),
    ]
    b = [text(W/2, 40, "JEDAIX 전체 파이프라인 — 대화가 온톨로지가 되고, 온톨로지가 실행이 된다", 20, NAVY, "bold"),
         text(W/2, 66, "(정인호, 2026 — JEDAIX 운영 매뉴얼 v9)", 12.5, GRAY)]
    y0, lh, gap = 92, 76, 10
    for i, (t, sub, fill, tcol) in enumerate(layers):
        y = y0 + i*(lh+gap)
        tc = tcol or NAVY
        b.append(rrect(140, y, W-330, lh, fill, NAVY, 1.5, 10))
        b.append(text(W/2-95, y+32, t, 16, tc, "bold"))
        b.append(text(W/2-95, y+56, sub, 11.8, (ICE2 if tcol else GRAY)))
        if i < 6:
            b.append(arrow(W/2-95, y+lh+1, W/2-95, y+lh+gap-1, NAVY, 2.2))
    top, bot = y0, y0 + 7*lh + 6*gap
    b.append(curve(W-180, bot-30, W-95, (top+bot)/2, W-180, top+2*(lh+gap)+30, ACC, 2.8, "ahA", "7,5"))
    b.append(multi(W-92, (top+bot)/2 - 30, ["War Room", "이상 신호", "→ 6 Station", "재진단", "(환류 루프)"], 12, ACC, 18, w="bold"))
    b.append(text(W/2, H-16, "3부 19장 — 확정의 매 단계에 HITL 승인이 있다: 기계가 발굴하고, 사람이 통치한다", 12, GRAY))
    svg("fig_191_jedaix_pipeline", W, H, "".join(b))

# ── 그림 20-1. Seed 성장 사슬 ──────────────────────────────────
def fig_201():
    W, H = 1000, 560
    steps = [
        ("현장의 발화", "“지난달 C라인에서” “그런 적이 두 번…”", 10),
        ("Linguistic Seed", "문장을 Chunk로 분해", 16),
        ("Semantic Seed", "TA 코드 분류 (경계 유형)", 22),
        ("SEED_HYPOTHESIS", "공명 신호로 가설 강화", 28),
        ("Ontological Seed", "HITL 승인으로 확정", 34),
        ("OWL Class·Property", "실행 가능한 의미 구조", 40),
    ]
    b = [text(W/2, 40, "Seed 성장 사슬 — 한 문장이 온톨로지가 되기까지", 23, NAVY, "bold"),
         text(W/2, 66, "PTGDA: Progressive Tacit-to-Governed Discovery & Adoption", 13, GRAY)]
    y0, bw, gap = 210, 148, 14
    x0 = (W - (bw*6 + gap*5)) / 2
    for i, (t, sub, r) in enumerate(steps):
        X = x0 + i*(bw+gap)
        cxx = X + bw/2
        shade = ["#D8E4F5", "#BFD3EE", "#9FC2E4", "#7AA8D2", "#3E7CB8", TEAL][i]
        b.append(f'<circle cx="{cxx}" cy="{160-r/2}" r="{r}" fill="{shade}" stroke="{NAVY}" stroke-width="1.2"/>')
        if i == 5:
            b.append(f'<path d="M{cxx-12},{160-r/2} l8,10 l16,-20" stroke="{WHITE}" stroke-width="4" fill="none"/>')
        b.append(rrect(X, y0, bw, 96, ICE if i < 5 else "#E5F4F3", NAVY if i < 5 else TEAL, 1.5, 9))
        b.append(multi(cxx, y0+28, t.split(" "), 12.5, NAVY if i < 5 else TEAL, 17, w="bold") if len(t) > 16
                 else text(cxx, y0+34, t, 12.5, NAVY if i < 5 else TEAL, "bold"))
        b.append(multi(cxx, y0+58, [sub[:14], sub[14:]] if len(sub) > 14 else [sub], 10.5, GRAY, 15))
        if i < 5:
            b.append(arrow(X+bw+1, y0+48, X+bw+gap-1, y0+48, TEAL, 2.2, "ahT"))
    gx = x0 + 4*(bw+gap) + bw + gap/2
    b.append(f'<rect x="{gx-9}" y="{y0-26}" width="18" height="24" rx="3" fill="{ACC}"/>')
    b.append(text(gx, y0-32, "HITL 게이트", 11, ACC, "bold"))
    b.append(multi(W/2, 370, [
        "씨앗이 자랄수록(원이 커질수록) 확신도가 오르고, 확정의 문턱에는 반드시 사람의 승인이 있다",
        "확정된 OWL 클래스는 Agent Workflow의 실행 근거가 되어 표준 업무 흐름에 반영된다",
    ], 13, GRAY, 24))
    b.append(rrect(150, 420, 700, 66, LGRAY, GRAY, 1.3, 10))
    b.append(multi(W/2, 447, ["예시: “지난달 C라인에서 그런 적이 두 번 있었습니다”",
                               "→ TA 분류 → 가설 → HITL 확정 → InventoryRisk 클래스 → 안전재고 재계산 Agent"],
                   12, NAVY, 22))
    b.append(text(W/2, H-16, "3부 20장 — PTGDA와 TA: 암묵지 발굴의 알고리즘 (정인호, 2026)", 11.5, GRAY))
    svg("fig_201_seed_chain", W, H, "".join(b))

fig_p2(); fig_31(); fig_42(); fig_121(); fig_131(); fig_181(); fig_191(); fig_201()
print("완료")
