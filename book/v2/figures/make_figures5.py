#!/usr/bin/env python3
"""3부 개정판 쉬운 개념 그림 6점 — SVG 생성 + PNG 변환 (figlib 공용 라이브러리 사용)."""
from figlib import *

# ── 그림 N3. 3부의 새 지도 — 네 개의 징검돌 ────────────────────
def fig_n3_part3map():
    W, H = 980, 430
    b = [text(W/2, 38, "3부의 지도 — 네 개의 징검돌", 23, NAVY, "bold"),
         text(W/2, 64, "문제를 보고 → 말이 시스템이 되고 → 실행하고 → 증명한다", 13, GRAY)]
    blocks = [
        ("18장", "사각지대", "문제를 본다",
         ["ERP가 비추지 못하는 곳을", "먼저 드러낸다"]),
        ("19장", "JEDAIX 온톨로지", "말이 시스템이 된다",
         ["5 Space × 6 Station으로", "회사의 말을 구조화한다"]),
        ("20장", "실행", "에이전트와 Odoo",
         ["온톨로지가 실행 코드가", "되어 움직인다"]),
        ("21장", "증명", "사례와 첫 90일",
         ["현장 사례와 함께", "첫 90일 로드맵을 제시한다"]),
    ]
    bw, bh, gap = 210, 140, 28
    x0 = (W - (bw*4 + gap*3)) / 2
    ys = [250, 212, 174, 136]
    fills = [ICE, ICE2, "#CFE9E7", TEAL]
    for i, (ch, t, tag, desc) in enumerate(blocks):
        x, y = x0 + i*(bw+gap), ys[i]
        cx = x + bw/2
        tc = NAVY if i < 3 else WHITE
        tagc = TEAL if i < 3 else "#CFF0EC"
        dc = GRAY if i < 3 else ICE2
        b.append(f'<ellipse cx="{cx}" cy="{y+bh+16}" rx="92" ry="9" fill="{LGRAY}"/>')
        b.append(rrect(x, y, bw, bh, fills[i], NAVY if i < 3 else TEAL, 1.6, 12))
        b.append(rrect(x+12, y+12, 52, 24, NAVY, NAVY, 1, 12))
        b.append(text(x+38, y+29, ch, 12.5, WHITE, "bold"))
        b.append(text(cx, y+64, t, 17, tc, "bold"))
        b.append(text(cx, y+88, tag, 13, tagc, "bold"))
        b.append(multi(cx, y+112, desc, 11.5, dc, 16))
        if i < 3:
            b.append(arrow(x+bw+2, y+52, x+bw+gap-2, ys[i+1]+84, NAVY, 2.5))
    b.append(text(W/2, H-16, "3부 — 사각지대에서 시작해 90일의 증명으로 끝난다", 12, GRAY))
    svg("fig_n3_part3map", W, H, "".join(b))

# ── 그림 N18-1. 빙산 — 형식지와 암묵지 ─────────────────────────
def fig_n18_iceberg():
    W, H = 940, 660
    WATER = "#D2E4F6"; WLINE = "#5B8AC7"; BERG_D = "#A9C4E8"
    b = [text(W/2, 38, "빙산 — 기록되는 것과 기록되지 않는 것", 22, NAVY, "bold"),
         text(W/2, 64, "ERP는 수면 위를 기록한다 — 판단의 대부분은 수면 아래에 있다", 13, GRAY)]
    # 물
    b.append(f'<rect x="40" y="270" width="860" height="310" fill="{WATER}"/>')
    b.append(line(40, 270, 900, 270, WLINE, 2, "8,6"))
    b.append(text(58, 262, "수면", 12, WLINE, "bold", anchor="start"))
    # 빙산 위(작은 부분) / 아래(큰 부분)
    b.append(f'<path d="M370,270 L410,180 L448,205 L495,150 L555,270 z" '
             f'fill="{WHITE}" stroke="{NAVY}" stroke-width="2"/>')
    b.append(f'<path d="M370,270 L555,270 L640,350 L668,460 L560,545 L410,558 L318,485 L300,370 z" '
             f'fill="{BERG_D}" stroke="{WLINE}" stroke-width="2"/>')
    # 수면 위 라벨
    b.append(text(185, 200, "형식지 — ERP에 기록되는 것", 15, NAVY, "bold"))
    b.append(text(185, 224, "전표 · 마스터 · 보고서", 12.5, GRAY))
    b.append(line(300, 210, 388, 228, GRAY, 1.2, "4,4"))
    # 수면 아래 라벨
    b.append(text(478, 330, "암묵지 — 기록되지 않는 것", 15, NAVY, "bold"))
    b.append(multi(478, 362, ["베테랑의 판단", "예외 처리", "구두 협의", "감각의 기준"],
                   12.5, "#27406E", 24))
    # 끌어올리는 화살표
    b.append(curve(590, 500, 780, 470, 830, 250, TEAL, 3.5, "ahT"))
    b.append(multi(760, 200, ["온톨로지가", "수면 아래를 끌어올린다"], 13.5, TEAL, 20, w="bold"))
    b.append(text(478, 610, "기록 아래에 훨씬 큰 판단의 세계가 있다 — 그것을 형식지로 끌어올리는 도구가 온톨로지다",
                  13, NAVY, "bold"))
    b.append(text(W/2, H-14, "3부 18장 — 빙산 비유: 형식지와 암묵지", 11.5, GRAY))
    svg("fig_n18_iceberg", W, H, "".join(b))

# ── 그림 N18-2. 지도와 내비게이션 ──────────────────────────────
def fig_n18_nav():
    W, H = 960, 540
    b = [text(W/2, 38, "지도와 내비게이션 — ERP 원장과 온톨로지", 22, NAVY, "bold"),
         text(W/2, 64, "기록은 지도가 하고, 다음 길은 내비게이션이 제안한다", 13, GRAY)]
    # 좌 패널: 지도
    b.append(rrect(55, 95, 400, 370, WHITE, GRAY, 1.6, 12))
    b.append(rrect(55, 95, 400, 44, LGRAY, GRAY, 1.6, 12))
    b.append(f'<rect x="55.8" y="118" width="398.4" height="20.2" fill="{LGRAY}"/>')
    b.append(text(255, 123, "지도 (ERP 원장)", 16, DARK, "bold"))
    # 종이지도 아이콘(접힌 3면)
    b.append(f'<path d="M186,180 L232,168 L232,246 L186,258 z" fill="#FDFDFD" stroke="{GRAY}" stroke-width="1.5"/>')
    b.append(f'<path d="M232,168 L278,180 L278,258 L232,246 z" fill="{LGRAY}" stroke="{GRAY}" stroke-width="1.5"/>')
    b.append(f'<path d="M278,180 L324,168 L324,246 L278,258 z" fill="#FDFDFD" stroke="{GRAY}" stroke-width="1.5"/>')
    b.append(f'<path d="M198,236 Q244,198 310,192" fill="none" stroke="{GRAY}" '
             f'stroke-width="2" stroke-dasharray="5,4"/>')
    b.append(circle(198, 236, 4, GRAY))
    b.append(circle(310, 192, 4, GRAY))
    b.append(text(255, 284, "과거를 담는다", 12, GRAY))
    b.append(multi(85, 316, ["· 지나온 길의 기록이다", "· 조회하면 보여준다", "· 갱신은 사람이 한다"],
                   13.5, DARK, 34, anchor="start"))
    # 우 패널: 내비게이션
    b.append(rrect(505, 95, 400, 370, WHITE, TEAL, 1.8, 12))
    b.append(rrect(505, 95, 400, 44, TEAL, TEAL, 1.8, 12))
    b.append(f'<rect x="505.9" y="118" width="398.2" height="20.1" fill="{TEAL}"/>')
    b.append(text(705, 123, "내비게이션 (온톨로지)", 16, WHITE, "bold"))
    # 경로 재계산 아이콘: 막힌 직행(회색 점선+X) / 다시 계산한 길(청록 실선)
    b.append(f'<path d="M620,240 C680,228 720,224 778,196" fill="none" stroke="{GRAY}" '
             f'stroke-width="2" stroke-dasharray="5,4"/>')
    b.append(line(694, 219, 710, 235, ACC, 3))
    b.append(line(710, 219, 694, 235, ACC, 3))
    b.append(f'<path d="M620,240 C650,262 700,258 728,238 C748,224 760,210 774,199" '
             f'fill="none" stroke="{TEAL}" stroke-width="3.5" marker-end="url(#ahT)"/>')
    b.append(circle(620, 240, 7, NAVY))
    b.append(circle(790, 180, 11, ACC))
    b.append(circle(790, 180, 4, WHITE))
    b.append(f'<path d="M780,187 L790,208 L800,187 z" fill="{ACC}"/>')
    b.append(text(660, 205, "막힘", 11.5, ACC, "bold"))
    b.append(text(705, 284, "다음 길을 제안한다", 12, TEAL, "bold"))
    b.append(multi(535, 316, ["· 관계를 알고 있다", "· 막히면 길을 다시 계산한다", "· 묻기 전에 제안한다"],
                   13.5, DARK, 34, anchor="start"))
    b.append(text(W/2, 497, "같은 데이터 위에서 — 지도는 묻는 사람에게 답하고, 내비게이션은 먼저 말을 건다",
                  13, NAVY, "bold"))
    b.append(text(W/2, H-14, "3부 18장 — 사각지대: ERP가 비추지 못하는 곳", 11.5, GRAY))
    svg("fig_n18_nav", W, H, "".join(b))

# ── 그림 N19. 베이스캠프에서 정상까지 — 5 Space와 6 Station ────
def fig_n19_basecamp():
    W, H = 960, 700
    MTN = "#EDF2F8"; MEDGE = "#9FB3D1"
    b = [text(W/2, 38, "베이스캠프에서 정상까지 — 5 Space와 6 Station", 21, NAVY, "bold"),
         text(W/2, 64, "다섯 캠프(공간)에서 출발한 문제가 여섯 정거장(흐름)을 지나 정상(통치)에 닿는다", 13, GRAY)]
    # 산
    b.append(f'<path d="M100,540 L480,140 L860,540 z" fill="{MTN}" stroke="{MEDGE}" stroke-width="2"/>')
    b.append(f'<path d="M480,140 L521,183 L497,178 L473,196 L452,180 L439,183 z" fill="{WHITE}" stroke="{MEDGE}" stroke-width="1.2"/>')
    # 정상 깃발 = 통치
    b.append(line(480, 140, 480, 86, NAVY, 3))
    b.append(f'<path d="M480,86 L538,86 L524,99 L538,112 L480,112 z" fill="{ACC}"/>')
    b.append(text(548, 104, "정상 = 통치(Governance)", 14, ACC, "bold", anchor="start"))
    # 등반 루트(6 Station)
    pts = [(215, 540), (300, 478), (600, 430), (340, 360), (590, 300), (430, 240), (505, 185), (482, 148)]
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    b.append(f'<path d="{d}" fill="none" stroke="{TEAL}" stroke-width="2.5" stroke-dasharray="7,5"/>')
    b.append(text(118, 510, "등반 루트 = 6 Station", 12.5, TEAL, "bold", anchor="start"))
    stations = [("1", "진단", 300, 478, "above"), ("2", "분석", 600, 430, "right"),
                ("3", "보고서", 340, 360, "left"), ("4", "정책", 590, 300, "right"),
                ("5", "규칙", 430, 240, "left"), ("6", "업무논리", 505, 185, "right")]
    pillw = {"진단": 58, "분석": 58, "정책": 58, "규칙": 58, "보고서": 72, "업무논리": 86}
    for num, name, cx, cy, side in stations:
        pw = pillw[name]
        if side == "right":
            px, py = cx + 16, cy - 13
        elif side == "left":
            px, py = cx - 16 - pw, cy - 13
        else:  # above
            px, py = cx - pw/2, cy - 42
        b.append(rrect(px, py, pw, 26, WHITE, NAVY, 1.2, 13))
        b.append(text(px + pw/2, py + 18, name, 12, NAVY, "bold"))
        b.append(circle(cx, cy, 11, WHITE, NAVY, 2))
        b.append(text(cx, cy + 4.5, num, 11.5, NAVY, "bold"))
    # 지면과 베이스캠프(5 Space)
    b.append(line(60, 560, 900, 560, MEDGE, 1.5))
    camps = [("GovernSpace", "경영·의사결정", 140), ("FlowSpace", "물리적 흐름", 300),
             ("QualitySpace", "검증·품질", 460), ("ResourceSpace", "자원·재고·조달", 620),
             ("ValueSpace", "손익·재무 환류", 780)]
    for name, mean, x in camps:
        b.append(f'<path d="M{x-27},602 L{x},568 L{x+27},602 z" fill="{ICE2}" stroke="{NAVY}" stroke-width="1.6"/>')
        b.append(f'<path d="M{x-8},602 L{x},588 L{x+8},602 z" fill="{NAVY}"/>')
        b.append(text(x, 622, name, 12, NAVY, "bold"))
        b.append(text(x, 640, mean, 11, GRAY))
    b.append(text(W/2, 664, "베이스캠프 = 5 Space (업무가 일어나는 다섯 공간)", 12.5, NAVY, "bold"))
    b.append(text(W/2, H-14, "3부 19장 — JEDAIX 온톨로지 아키텍처: 5 Space × 6 Station", 11.5, GRAY))
    svg("fig_n19_basecamp", W, H, "".join(b))

# ── 그림 N20. 뉴로-심볼릭 쉬운 판 — 두 개의 뇌 ─────────────────
def fig_n20_ns_easy():
    W, H = 940, 600
    b = [text(W/2, 38, "두 개의 뇌 — 뉴로-심볼릭의 쉬운 그림", 22, NAVY, "bold"),
         text(W/2, 64, "하나는 가설을 내고, 하나는 근거로 거른다", 13, GRAY)]
    # 좌: 제안하는 뇌 (둥근 상자)
    b.append(rrect(70, 110, 340, 150, ICE, NAVY, 1.8, 34))
    b.append(text(240, 156, "제안하는 뇌", 17, NAVY, "bold"))
    b.append(text(240, 184, "LLM · 직관", 13.5, GRAY))
    b.append(text(240, 212, "(가설을 낸다)", 12.5, TEAL, "bold"))
    # 우: 검증하는 뇌 (각진 상자)
    b.append(rrect(530, 110, 340, 150, LGRAY, NAVY, 1.8, 2))
    b.append(text(700, 156, "검증하는 뇌", 17, NAVY, "bold"))
    b.append(text(700, 184, "온톨로지 · 규칙", 13.5, GRAY))
    b.append(text(700, 212, "(근거로 거른다)", 12.5, ACC, "bold"))
    b.append(arrow(414, 172, 526, 172, NAVY, 2.2))
    b.append(text(470, 160, "가설", 12, NAVY, "bold"))
    # 두 뇌 → 근거 카드
    b.append(curve(240, 264, 260, 310, 360, 348, TEAL, 2.2, "ahT"))
    b.append(text(238, 316, "제안", 12, TEAL, "bold"))
    b.append(curve(700, 264, 680, 310, 580, 348, TEAL, 2.2, "ahT"))
    b.append(text(716, 316, "검증 근거", 12, TEAL, "bold"))
    # 근거 카드
    b.append(rrect(370, 320, 200, 106, WHITE, TEAL, 2, 10))
    b.append(text(470, 346, "근거 카드", 14.5, TEAL, "bold"))
    b.append(line(392, 356, 548, 356, "#BFE3E0", 1.4))
    b.append(text(470, 380, "제안 내용 + 판단 근거", 11.5, GRAY))
    b.append(text(470, 402, "확신도와 대안", 11.5, GRAY))
    # 카드 → 사람(승인)
    b.append(arrow(470, 428, 470, 462, NAVY, 2.5))
    b.append(circle(470, 486, 13, ICE2, NAVY, 2))
    b.append(f'<path d="M442,532 Q470,498 498,532 z" fill="{ICE2}" stroke="{NAVY}" stroke-width="2"/>')
    # 승인 도장
    b.append(f'<g transform="rotate(-12 546 502)">'
             f'<circle cx="546" cy="502" r="23" fill="{WHITE}" stroke="{ACC}" stroke-width="2.5"/>'
             f'<circle cx="546" cy="502" r="18" fill="none" stroke="{ACC}" stroke-width="1"/>'
             + text(546, 507, "승인", 12.5, ACC, "bold") + "</g>")
    b.append(text(470, 552, "사람이 보고 결정한다 (HITL)", 12.5, NAVY, "bold"))
    b.append(text(W/2, 578, "제안은 자유롭게, 실행은 검증된 것만", 15, NAVY, "bold"))
    b.append(text(W/2, H-4, "3부 20장 — 뉴로-심볼릭: 두 뇌의 분업", 11, GRAY))
    svg("fig_n20_ns_easy", W, H, "".join(b))

# ── 그림 N21. 첫 90일 타임라인 ─────────────────────────────────
def fig_n21_90days():
    W, H = 980, 430
    segs = [
        ("1~30일", "진단 · 데이터 정비", ICE2, NAVY,
         ["· 기준정보·마스터 정비", "· 사각지대 후보 목록화", "· 경영 스폰서 지정"], NAVY),
        ("31~60일", "파일럿 — 사각지대 1개", TEAL, WHITE,
         ["· 현장 대화로 Seed 발굴", "· HITL 승인 절차 정착", "· 워크플로 1개 가동"], TEAL),
        ("61~90일", "실행 · KPI 검증", NAVY, WHITE,
         ["· KPI 전후 비교", "· 확산 대상 업무 선정", "· 운영 조직으로 이관"], NAVY),
    ]
    b = [text(W/2, 38, "첫 90일 — 작게 시작해 빠르게 증명한다", 23, NAVY, "bold"),
         text(W/2, 64, "진단하고, 하나의 사각지대로 파일럿하고, KPI로 증명한다", 13, GRAY)]
    x0, sw_, gap, y0, sh = 45, 290, 10, 100, 66
    for i, (days, label, fill, tc, bullets, edge) in enumerate(segs):
        x = x0 + i*(sw_+gap)
        cx = x + sw_/2 + 9
        b.append(chevron(x, y0, sw_, sh, fill))
        b.append(text(cx, y0+28, days, 15, tc, "bold"))
        b.append(text(cx, y0+50, label, 12.5, tc))
        b.append(rrect(x+9, 190, sw_-9, 128, WHITE, edge, 1.5, 10))
        b.append(multi(x+30, 226, bullets, 12.5, DARK, 36, anchor="start"))
    b.append(text(W/2, 366, "원칙: 전사 빅뱅이 아니라 한 곳에서의 증명 — 90일의 성공이 확산의 근거가 된다",
                  13, NAVY, "bold"))
    b.append(text(W/2, H-16, "3부 21장 — 첫 90일 로드맵", 11.5, GRAY))
    svg("fig_n21_90days", W, H, "".join(b))

if __name__ == "__main__":
    fig_n3_part3map()
    fig_n18_iceberg()
    fig_n18_nav()
    fig_n19_basecamp()
    fig_n20_ns_easy()
    fig_n21_90days()
    print("완료")
