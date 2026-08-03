#!/usr/bin/env python3
"""3순위 보조 도해 — 3부 18~23장 담당분 12점 (fig_182 ~ fig_233)."""
from figlib import *

TEAL_MID = "#7FB8C0"   # 보조 활성 칸(옅은 틸)


# ── 그림 18-2. 3부 전체 지도 ───────────────────────────────────
def fig_182():
    W, H = 980, 415
    steps = [
        ("18장", "경영 사각지대", "문제의 정의 — 손실은", "비추지 않는 곳에서 발생"),
        ("19장", "아키텍처", "5 Space × 6 Station", "워크벤치의 좌표계"),
        ("20장", "발굴", "TA 분류 · PTGDA", "암묵지 발굴 알고리즘"),
        ("21장", "실행", "Agent Workflow", "War Room · SCM Backbone"),
        ("22장", "방법론", "관통 5단계 · 로드맵", "도입 시나리오 2경로"),
        ("23장", "사례", "안전재고 · 조립 병목", "실측 성과의 실증"),
    ]
    b = [text(W/2, 40, "3부 전체 지도 — 사각지대에서 성과까지", 24, NAVY, "bold"),
         text(W/2, 66, "여섯 장이 하나의 여정을 이룬다: 문제를 정의하고, 기계를 해부하고, 방법론으로 일반화해, 사례로 실증한다", 12.5, GRAY)]
    bw, gap, y0, bh = 148, 12, 120, 150
    x0 = (W - (bw*6 + gap*5)) / 2
    for i, (ch, t, s1, s2) in enumerate(steps):
        X = x0 + i*(bw+gap)
        hl = i in (0, 5)            # 출발(문제)과 도착(성과) 강조
        b.append(rrect(X, y0, bw, bh, ICE if not hl else TEALBG, NAVY if not hl else TEAL, 1.6, 10))
        b.append(circle(X+bw/2, y0-14, 17, NAVY if not hl else TEAL))
        b.append(text(X+bw/2, y0-9, ch, 11.5, WHITE, "bold"))
        b.append(text(X+bw/2, y0+46, t, 15.5, NAVY if not hl else TEAL, "bold"))
        b.append(multi(X+bw/2, y0+84, [s1, s2], 11, GRAY, 19))
        if i < 5:
            b.append(arrow(X+bw+1, y0+bh/2, X+bw+gap-1, y0+bh/2, TEAL, 2.4, "ahT"))
    # 하단 구간 묶음 표시
    gy = y0 + bh + 34
    groups = [(0, 0, "왜 필요한가 — 문제"), (1, 3, "기계의 해부 — 좌표계·발굴·실행"), (4, 5, "어떻게 도입하고 무엇을 얻는가")]
    for s, e, label in groups:
        x1 = x0 + s*(bw+gap)
        x2 = x0 + e*(bw+gap) + bw
        b.append(line(x1+4, gy, x2-4, gy, TEAL, 2))
        b.append(line(x1+4, gy-6, x1+4, gy, TEAL, 2))
        b.append(line(x2-4, gy-6, x2-4, gy, TEAL, 2))
        b.append(text((x1+x2)/2, gy+22, label, 12, NAVY, "bold"))
    b.append(text(W/2, H-16, "3부 18장 — 온톨로지 메커니즘(JEDAIX)이 채우는 자리 (정인호, 2026)", 11.5, GRAY))
    svg("fig_182_part3_map", W, H, "".join(b))


# ── 그림 19-2. 5 Space × 6 Station 매트릭스 ────────────────────
def fig_192():
    W, H = 980, 640
    stations = ["진단", "분석", "보고서", "정책", "규칙", "업무논리"]
    spaces = [("GovernSpace", "경영·의사결정"), ("FlowSpace", "물리적 흐름"),
              ("QualitySpace", "검증·품질"), ("ResourceSpace", "자원·재고·조달"),
              ("ValueSpace", "손익·재무 환류")]
    # 2=주 활성(짙은 틸), 1=보조 활성(옅은 틸), 0=드문 조합(회색)
    act = [
        [0, 0, 1, 2, 0, 0],   # Govern: 정책·의사결정
        [1, 0, 0, 0, 1, 2],   # Flow: 진단·규칙·업무논리
        [2, 2, 0, 0, 1, 0],   # Quality: 진단·분석
        [0, 1, 0, 0, 2, 1],   # Resource: 규칙(재고 정책)·실행
        [0, 0, 2, 1, 0, 1],   # Value: 가치증명·환류(보고서)
    ]
    b = [text(W/2, 40, "5 Space × 6 Station 매트릭스 — 워크벤치의 좌표 프레임", 22, NAVY, "bold"),
         text(W/2, 66, "세로축은 업무가 일어나는 공간, 가로축은 문제가 흘러가는 단계 — 색칠된 칸이 활성 조합이다", 12.5, GRAY)]
    x0, y0, cw, chh = 250, 152, 116, 62
    # 열 머리
    b.append(text(x0+3, y0-52, "문제의 흐름", 11, TEAL, "bold", anchor="start"))
    b.append(arrow(x0+92, y0-56, x0+6*cw-6, y0-56, TEAL, 1.8, "ahT"))
    for j, st in enumerate(stations):
        X = x0 + j*cw
        b.append(rrect(X+3, y0-38, cw-6, 32, NAVY, NAVY, 1, 6))
        b.append(text(X+cw/2, y0-17, st, 12.5, WHITE, "bold"))
    # 행 머리 + 칸
    for i, (sp, mean) in enumerate(spaces):
        Y = y0 + i*chh
        b.append(rrect(40, Y+3, 200, chh-6, ICE, NAVY, 1.2, 6))
        b.append(text(56, Y+27, sp, 13, NAVY, "bold", anchor="start"))
        b.append(text(56, Y+46, mean, 10.8, GRAY, anchor="start"))
        for j in range(6):
            X = x0 + j*cw
            v = act[i][j]
            fill = TEAL if v == 2 else (TEAL_MID if v == 1 else LGRAY)
            b.append(rrect(X+3, Y+3, cw-6, chh-6, fill, WHITE, 1.5, 4))
            if v == 2:
                b.append(circle(X+cw/2, Y+chh/2, 5, WHITE))
    gy = y0 + 5*chh + 26
    # 범례
    lx = 60
    b.append(rrect(lx, gy, 20, 14, TEAL, WHITE, 1, 3))
    b.append(text(lx+28, gy+12, "주 활성 조합", 11.5, DARK, anchor="start"))
    b.append(rrect(lx+130, gy, 20, 14, TEAL_MID, WHITE, 1, 3))
    b.append(text(lx+158, gy+12, "보조 활성", 11.5, DARK, anchor="start"))
    b.append(rrect(lx+240, gy, 20, 14, LGRAY, GRAY, 1, 3))
    b.append(text(lx+268, gy+12, "드물게 일어나는 조합", 11.5, DARK, anchor="start"))
    b.append(multi(W/2, gy+46, [
        "회색 칸에서 반복되는 사건이 발견되면 “표준 프로세스가 미처 예상 못 한 숨은 문제”의 신호다",
        "— 좌표 프레임 밖의 반복으로 이상을 알리는, 의미의 관리도",
    ], 12.5, ACC, 20, w="bold"))
    b.append(text(W/2, H-16, "칸 배치는 개념 예시 — JEDAIX 운영 매뉴얼 v9 3.2절의 좌표 프레임을 6 Station 표기로 재구성 (정인호, 2026)", 11, GRAY))
    svg("fig_192_space_station", W, H, "".join(b))


# ── 그림 19-3. 확률적 상태 관리 스펙트럼 ───────────────────────
def fig_193():
    W, H = 960, 560
    b = [text(W/2, 40, "“맞다/틀리다”에서 “점점 그럴듯해지는”으로", 22, NAVY, "bold"),
         text(W/2, 66, "전통 시스템의 이분법 vs JEDAIX의 확률적 상태 관리 (wave/particle 이중 표현)", 12.5, GRAY)]
    # 상단: 이분법
    b.append(rrect(50, 92, 860, 150, LGRAY, GRAY, 1.4, 12))
    b.append(text(70, 120, "전통 시스템 — 이분법 상태 관리", 14, DARK, "bold", anchor="start"))
    b.append(rrect(170, 140, 240, 74, WHITE, GRAY, 1.6, 8))
    b.append(text(290, 172, "맞다", 16, DARK, "bold"))
    b.append(text(290, 196, "승인 · 합격 · 확정", 11.5, GRAY))
    b.append(rrect(550, 140, 240, 74, WHITE, GRAY, 1.6, 8))
    b.append(text(670, 172, "틀리다", 16, DARK, "bold"))
    b.append(text(670, 196, "반려 · 불합격 · 기각", 11.5, GRAY))
    b.append(line(440, 177, 520, 177, ACC, 2, "6,4"))
    b.append(text(480, 160, "중간 상태 없음", 11.5, ACC, "bold"))
    b.append(text(480, 232, "“아직 확실하지 않은” 정보가 소실된다", 12, ACC))
    # 하단: 스펙트럼
    b.append(rrect(50, 268, 860, 220, ICE, NAVY, 1.4, 12))
    b.append(text(70, 296, "JEDAIX — 확률적 상태 관리", 14, NAVY, "bold", anchor="start"))
    shades = ["#E3EDF8", "#CFE0F1", "#B6D2E8", "#9AC2DC", "#7BB0CE", "#589CBE", "#3B88AC", "#1F7396"]
    sx, sy, sw2, sh = 100, 322, 68, 56
    for i, c in enumerate(shades):
        b.append(rrect(sx + i*sw2, sy, sw2-4, sh, c, NAVY, 0.8, 4))
    b.append(text(sx, sy+sh+20, "0%", 11.5, GRAY, anchor="start"))
    b.append(text(sx+8*sw2-8, sy+sh+20, "100%", 11.5, GRAY, anchor="end"))
    b.append(text(sx+4*sw2, sy+sh+20, "연속 확신도 wave — 반복 확인마다 상승, 엇갈린 응답이면 하락", 11.5, GRAY))
    # 임계선 (70%)
    tx = sx + 8*sw2*0.7
    b.append(line(tx, sy-16, tx, sy+sh+8, ACC, 2.2, "5,4"))
    b.append(text(tx, sy-24, "임계값 70% · 최소 3회", 11.5, ACC, "bold"))
    # 확정 박스
    b.append(arrow(sx+8*sw2+4, sy+sh/2, 682, sy+sh/2, TEAL, 2.4, "ahT"))
    b.append(rrect(688, sy-6, 190, sh+12, NAVY, NAVY, 1.5, 8))
    b.append(text(783, sy+20, "확정 (particle)", 14, WHITE, "bold"))
    b.append(text(783, sy+42, "사람의 승인 순간에만", 10.8, ICE2))
    b.append(text(720, sy+sh+22, "HITL 승인 게이트", 11, ACC, "bold", anchor="start"))
    b.append(f'<rect x="{700}" y="{sy+sh+8}" width="14" height="18" rx="3" fill="{ACC}"/>')
    b.append(multi(W/2, 452, ["“아직 확실하지 않지만 점점 그럴듯해지는” 중간 상태를 숫자(0~100%)로 계속 보여주고,",
                              "사람이 최종 승인하는 순간에만 이분법적 ‘확정’으로 전환한다"], 12.2, NAVY, 20))
    b.append(text(W/2, H-16, "3부 19장 — JEDAIX 운영 매뉴얼 v9, 3.4절 (정인호, 2026)", 11.5, GRAY))
    svg("fig_193_spectrum", W, H, "".join(b))


# ── 그림 20-2. PTGDA 상태 전이도 ───────────────────────────────
def fig_202():
    W, H = 1000, 525
    states = [
        ("seed", "씨앗", ["seeds 테이블에", "TA 코드와 신호 축적"]),
        ("hypothesis", "가설", ["SEED_HYPOTHESIS", "triggered 전환"]),
        ("verify", "검증", ["6 Station 인터뷰", "confirm/refute 누적"]),
        ("confirmed", "확정", ["임계 70%·최소 3회", "GL 계정·손실 산출"]),
        ("governed", "통치", ["Station8 Agent 승격", "Loop·DTF 기한 추적"]),
    ]
    b = [text(W/2, 40, "PTGDA 상태 전이 — 씨앗에서 통치까지", 23, NAVY, "bold"),
         text(W/2, 66, "Progressive Tacit-to-Governed Discovery & Adoption: 반복 확인이 확신을 만들고, 사람의 승인이 확정을 만든다", 12.2, GRAY)]
    bw, gap, y0, bh = 168, 32, 170, 108
    x0 = (W - (bw*5 + gap*4)) / 2
    cx = []
    for i, (en, ko, sub) in enumerate(states):
        X = x0 + i*(bw+gap)
        cx.append(X + bw/2)
        last = i >= 3
        b.append(rrect(X, y0, bw, bh, TEALBG if last else ICE, TEAL if last else NAVY, 1.8, 10))
        b.append(text(X+bw/2, y0+30, ko, 16, TEAL if last else NAVY, "bold"))
        b.append(text(X+bw/2, y0+50, en, 11, GRAY))
        b.append(multi(X+bw/2, y0+74, sub, 10.8, GRAY, 16))
        if i < 4:
            b.append(arrow(X+bw+2, y0+bh/2, X+bw+gap-2, y0+bh/2, TEAL, 2.6, "ahT"))
    # HITL 게이트 (검증→확정 사이)
    gx = (cx[2]+cx[3])/2 + (0)  # 화살표 중간
    gx = x0 + 3*(bw+gap) - gap/2
    b.append(f'<rect x="{gx-9}" y="{y0-40}" width="18" height="24" rx="3" fill="{ACC}"/>')
    b.append(f'<circle cx="{gx}" cy="{y0-46}" r="6" fill="{ACC}"/>')
    b.append(text(gx, y0-58, "HITL 승인", 11.5, ACC, "bold"))
    b.append(line(gx, y0-14, gx, y0+18, ACC, 1.6, "4,3"))
    # 반려(엇갈린 응답) 경로: 검증 → 가설
    b.append(curve(cx[2]-20, y0+bh+4, (cx[1]+cx[2])/2, y0+bh+66, cx[1]+20, y0+bh+6, ACC, 2.2, "ahA", "6,4"))
    b.append(text((cx[1]+cx[2])/2, y0+bh+52, "엇갈린 응답 → 확신도 하락(반려)", 11.5, ACC, "bold"))
    # 소멸 경로: 가설 → 소멸
    dx = cx[0]
    b.append(curve(cx[1]-40, y0+bh+4, (dx+cx[1])/2+10, y0+bh+50, dx+62, y0+bh+76, ACC, 2.2, "ahA", "6,4"))
    b.append(rrect(dx-70, y0+bh+82, 150, 44, "none", ACC, 1.4, 8, dash="6,5"))
    b.append(text(dx+5, y0+bh+102, "소멸", 12.5, ACC, "bold"))
    b.append(text(dx+5, y0+bh+118, "반복 확인 없음 · 신호 사그라짐", 10.5, GRAY))
    # wave / particle 구간 표시
    wy = y0 - 24
    b.append(line(cx[0]-70, wy, cx[2]+70, wy, TEAL, 1.6))
    b.append(text((cx[0]+cx[2])/2, wy-8, "연속 확신도 wave (0~100%)", 11.5, TEAL, "bold"))
    b.append(line(cx[3]-70, wy, cx[4]+70, wy, NAVY, 1.6))
    b.append(text((cx[3]+cx[4])/2, wy-8, "이진 확정 particle", 11.5, NAVY, "bold"))
    b.append(multi(W/2, y0+bh+170, [
        "확정(입자화)의 순간, 발굴된 암묵지는 품질손실비 등 GL 계정과 연환산 손실 추정치로 물질화되고",
        "채택된 개선활동은 DTF 기한(긴급 3일·보통 7일·여유 14일)을 가진 Loop 인스턴스로 추적된다",
    ], 12, GRAY, 20))
    b.append(text(W/2, H-16, "3부 20장 — JEDAIX 운영 매뉴얼 v9, 부록 D의 상태 전이를 재구성 (정인호, 2026)", 11.5, GRAY))
    svg("fig_202_ptgda_states", W, H, "".join(b))


# ── 그림 20-3. 한 문장의 여정 스토리보드 ───────────────────────
def fig_203():
    W, H = 1000, 540
    b = [text(W/2, 40, "“지난달 C라인에서 그런 적이 두 번 있었습니다” — 한 문장의 여정", 20, NAVY, "bold"),
         text(W/2, 66, "발화 한 줄이 온톨로지 Class가 되기까지의 다섯 장면", 12.5, GRAY)]
    pw, gap, y0, ph = 180, 15, 100, 300
    x0 = (W - (pw*5 + gap*4)) / 2
    heads = ["발화", "Chunk 분해", "TA 분류", "공명·반복 확인", "OWL 확정"]
    for i in range(5):
        X = x0 + i*(pw+gap)
        last = i == 4
        b.append(rrect(X, y0, pw, ph, WHITE, TEAL if last else NAVY, 1.6, 10))
        b.append(rrect(X, y0, pw, 34, TEAL if last else NAVY, TEAL if last else NAVY, 1.6, 10))
        b.append(f'<rect x="{X}" y="{y0+18}" width="{pw}" height="16" fill="{TEAL if last else NAVY}"/>')
        b.append(text(X+pw/2, y0+23, f"①②③④⑤"[i] + " " + heads[i], 12.5, WHITE, "bold"))
        cxx = X + pw/2
        if i == 0:   # 발화: 말풍선
            b.append(f'<path d="M{X+18},{y0+60} h{pw-36} a8,8 0 0 1 8,8 v70 a8,8 0 0 1 -8,8 h-{pw-70} l-14,18 v-18 h-12 a8,8 0 0 1 -8,-8 v-70 a8,8 0 0 1 8,-8 z" '
                     f'transform="translate(-8,0)" fill="{ICE}" stroke="{NAVY}" stroke-width="1.3"/>')
            b.append(multi(cxx, y0+86, ["“지난달 C라인에서", "그런 적이", "두 번 있었습니다”"], 11.5, NAVY, 20, w="bold"))
            b.append(multi(cxx, y0+210, ["6 Station 진단 화면", "품질관리 담당자의 증언"], 10.8, GRAY, 16))
        elif i == 1: # Chunk 태깅
            tags = [("시간", "지난달"), ("장소", "C라인"), ("빈도", "두 번"), ("행위", "출하 강행")]
            for k, (kk, vv) in enumerate(tags):
                yy = y0 + 52 + k*38
                b.append(rrect(X+14, yy, 62, 28, ICE2, NAVY, 1, 6))
                b.append(text(X+45, yy+19, kk, 11, NAVY, "bold"))
                b.append(rrect(X+82, yy, 84, 28, LGRAY, GRAY, 1, 6))
                b.append(text(X+124, yy+19, vv, 11, DARK))
            b.append(multi(cxx, y0+218, ["NLP Chunk 분해·태깅", "= Linguistic Seed"], 10.8, GRAY, 16))
        elif i == 2: # TA 분류
            b.append(rrect(X+22, y0+56, pw-44, 56, NAVY, NAVY, 1.4, 8))
            b.append(text(cxx, y0+80, "TA06", 15, WHITE, "bold"))
            b.append(text(cxx, y0+100, "KPI 충돌", 11.5, ICE2))
            b.append(arrow(cxx, y0+118, cxx, y0+140, TEAL, 2, "ahT"))
            b.append(rrect(X+22, y0+144, pw-44, 48, ICE, NAVY, 1.2, 8))
            b.append(multi(cxx, y0+164, ["seeds 테이블에", "후보로 축적"], 10.8, NAVY, 16))
            b.append(multi(cxx, y0+218, ["“품질 이의를 누르고", "출하 강행” 유형으로 분류"], 10.8, GRAY, 16))
        elif i == 3: # 공명 신호
            b.append(circle(cxx, y0+96, 40, ACC, ACC, 0, 0.15))
            b.append(circle(cxx, y0+96, 28, ACC, ACC, 0, 0.35))
            b.append(circle(cxx, y0+96, 16, ACC))
            b.append(multi(cxx, y0+160, ["“반응이 뚜렷해지고", "있습니다” — 공명 신호"], 10.8, ACC, 16, w="bold"))
            b.append(multi(cxx, y0+210, ["3라운드 반복 확인", "wave 임계 70% 돌파"], 10.8, GRAY, 16))
        else:        # OWL 확정
            b.append(f'<rect x="{cxx-9}" y="{y0+50}" width="18" height="22" rx="3" fill="{ACC}"/>')
            b.append(text(cxx+16, y0+66, "HITL 승인", 10.5, ACC, "bold", anchor="start"))
            b.append(rrect(X+18, y0+84, pw-36, 60, TEALBG, TEAL, 1.5, 8))
            b.append(multi(cxx, y0+108, ["OWL Class 등록", "InventoryRisk 유형"], 11.5, TEAL, 18, w="bold"))
            b.append(rrect(X+18, y0+156, pw-36, 52, ICE, NAVY, 1.2, 8))
            b.append(multi(cxx, y0+176, ["품질손실비 계정 반영", "연 약 6천만 원 추정"], 10.8, NAVY, 16))
            b.append(multi(cxx, y0+236, ["Agent 실행 제안으로", "승격(Station8)"], 10.8, GRAY, 16))
        if i < 4:
            b.append(arrow(X+pw+2, y0+ph/2, X+pw+gap-2, y0+ph/2, TEAL, 2.4, "ahT"))
    b.append(text(W/2, y0+ph+40, "사람이 개입한 곳은 대화(증언)와 승인뿐 — 나머지 변환은 파이프라인의 일이다", 12.5, NAVY, "bold"))
    b.append(text(W/2, H-16, "3부 20장 — JEDAIX 운영 매뉴얼 v9 4장의 가상 사례(A정밀부품㈜) 재구성 (정인호, 2026)", 11.5, GRAY))
    svg("fig_203_sentence_journey", W, H, "".join(b))


# ── 그림 21-1. Workflow 운영 사이클 ────────────────────────────
def fig_211():
    W, H = 940, 660
    CX, CY, R = 430, 340, 200
    nodes = [
        ("① Workflow 빌더", "6단계 슬롯 설계", -90),
        ("② 등록·배포", "통합 레지스트리", -18),
        ("③ Workspace 실행", "재고 차감·전표·회계", 54),
        ("④ War Room", "운영 모니터링·지연 감시", 126),
        ("⑤ Skill-Loop-Harness", "권한·기한·실행 관리", 198),
    ]
    b = [text(W/2, 40, "Workflow 운영 사이클 — 설계에서 환류까지", 23, NAVY, "bold"),
         text(W/2, 66, "다섯 단계는 한 번 돌고 끝나지 않는다 — 반복될수록 표준 프로세스가 현장에 가까워진다", 12.5, GRAY)]
    import math as m
    pos = []
    for t, s, deg in nodes:
        a = m.radians(deg)
        pos.append((CX + R*m.cos(a), CY + R*m.sin(a)))
    # 순환 화살표(틸 원호)
    for i in range(5):
        x1, y1 = pos[i]
        x2, y2 = pos[(i+1) % 5]
        mx, my = (x1+x2)/2, (y1+y2)/2
        vx, vy = mx-CX, my-CY
        L = (vx*vx+vy*vy) ** .5
        k = (R+56)/L
        # 마지막 화살표(⑤→①)는 재설계 회귀 — 테라코타 파선
        col, mk, ds = (ACC, "ahA", "7,5") if i == 4 else (TEAL, "ahT", "")
        sx1, sy1 = x1 + (x2-x1)*0.24, y1 + (y2-y1)*0.24
        sx2, sy2 = x1 + (x2-x1)*0.76, y1 + (y2-y1)*0.76
        b.append(curve(sx1 + (CX-sx1)*-0.10, sy1 + (CY-sy1)*-0.10, CX+vx*k/ (1), CY+vy*k/(1), sx2 + (CX-sx2)*-0.10, sy2 + (CY-sy2)*-0.10, col, 2.6, mk, ds))
    b.append(text(238, 222, "개선사항의 재설계 회귀", 11.5, ACC, "bold"))
    # 노드 박스
    for i, (t, s, deg) in enumerate(nodes):
        x, y = pos[i]
        bw2, bh2 = 190, 62
        hl = i == 3
        b.append(rrect(x-bw2/2, y-bh2/2, bw2, bh2, NAVY if hl else ICE, NAVY, 1.6, 10))
        b.append(text(x, y-6, t, 13.5, WHITE if hl else NAVY, "bold"))
        b.append(text(x, y+16, s, 10.8, ICE2 if hl else GRAY))
    # 중앙
    b.append(circle(CX, CY, 76, TEALBG, TEAL, 1.6))
    b.append(multi(CX, CY-10, ["운영", "사이클"], 15, TEAL, 24, w="bold"))
    # War Room → 6 Station 재진단 환류
    wx, wy = pos[3]
    b.append(curve(wx-98, wy-8, 175, wy+5, 130, 470, ACC, 2.6, "ahA", "7,5"))
    b.append(rrect(40, 400, 196, 64, "none", ACC, 1.5, 10, dash="6,5"))
    b.append(multi(138, 426, ["이상 신호 →", "6 Station 재진단"], 12.5, ACC, 20, w="bold"))
    b.append(text(W/2, H-40, "War Room의 이상 신호는 다시 진단의 입력이 된다 — 1부 5장 무한 루프의 JEDAIX 구현", 12.2, NAVY, "bold"))
    b.append(text(W/2, H-16, "3부 21장 — JEDAIX 운영 매뉴얼 v9, 3장의 운영 사이클 재구성 (정인호, 2026)", 11.5, GRAY))
    svg("fig_211_workflow_cycle", W, H, "".join(b))


# ── 그림 21-2. InventoryBufferAgent 실행 순서도 ────────────────
def fig_212():
    W, H = 980, 480
    steps = [
        ("문제 확정", ["TA06 (KPI 충돌)", "PTGDA 임계 돌파"], ICE2, NAVY),
        ("① 증거 정량화", ["신호의 최근 발생", "빈도를 수치화"], ICE, NAVY),
        ("② 보정계수 계산", ["안전재고 100→115", "ROP 150→173 제안"], ICE, NAVY),
        ("③ Digital Twin", ["재고 소진 예측 비교", "실제 값은 불변"], ICE, NAVY),
        ("④ HITL 승인", ["담당자가 성적표", "확인 후 승인·반려"], "#F6E8E5", ACC),
        ("O2C 반영", ["모든 표준 프로세스에", "새 값 자동 적용"], TEALBG, TEAL),
    ]
    b = [text(W/2, 40, "InventoryBufferAgent — 알림으로 끝나지 않는 실행", 22, NAVY, "bold"),
         text(W/2, 66, "확정된 사각지대가 재고 파라미터 갱신으로 이어지는 네 단계와 두 관문", 12.5, GRAY)]
    bw, gap, y0, bh = 148, 12, 130, 110
    x0 = (W - (bw*6 + gap*5)) / 2
    for i, (t, sub, fill, sc) in enumerate(steps):
        X = x0 + i*(bw+gap)
        b.append(rrect(X, y0, bw, bh, fill, sc, 1.6, 10))
        b.append(text(X+bw/2, y0+32, t, 12.8, sc if sc != ICE2 else NAVY, "bold"))
        b.append(multi(X+bw/2, y0+58, sub, 10.6, GRAY, 17))
        if i < 5:
            b.append(arrow(X+bw+1, y0+bh/2, X+bw+gap-1, y0+bh/2, TEAL, 2.3, "ahT"))
    # Agent 묶음 표시(①~③)
    ax1 = x0 + 1*(bw+gap)
    ax2 = x0 + 3*(bw+gap) + bw
    b.append(line(ax1+4, y0-18, ax2-4, y0-18, NAVY, 1.8))
    b.append(line(ax1+4, y0-18, ax1+4, y0-10, NAVY, 1.8))
    b.append(line(ax2-4, y0-18, ax2-4, y0-10, NAVY, 1.8))
    b.append(text((ax1+ax2)/2, y0-26, "Agent(Skill)의 자동 수행 — 여기까지 시스템은 바뀌지 않는다", 12, NAVY, "bold"))
    # HITL 강조
    hx = x0 + 4*(bw+gap) + bw/2
    b.append(f'<rect x="{hx-9}" y="{y0+bh+12}" width="18" height="22" rx="3" fill="{ACC}"/>')
    b.append(text(hx, y0+bh+52, "승인의 순간에만", 11, ACC, "bold"))
    b.append(text(hx, y0+bh+68, "실제 값이 바뀐다", 11, ACC, "bold"))
    b.append(multi(W/2, y0+bh+110, [
        "발굴된 지식이 문서가 아니라 파라미터가 되므로, 지키는 데 별도의 의지가 필요 없다",
        "— 출하 때마다 새 재주문점 기준으로 부족 여부가 자동 판단된다",
    ], 12.2, NAVY, 20, w="bold"))
    b.append(text(W/2, H-16, "3부 21장 — JEDAIX 운영 매뉴얼 v9 4~5장의 가상 사례(A정밀부품㈜) 재구성 (정인호, 2026)", 11.5, GRAY))
    svg("fig_212_buffer_agent", W, H, "".join(b))


# ── 그림 22-1. 관통 문제해결 5단계 ─────────────────────────────
def fig_221():
    W, H = 980, 440
    steps = [
        ("① 6 Station 진단", "위화감의 언어화", "Linguistic Seed·TA 후보"),
        ("② 문제 확정", "PTGDA 반복 검증", "GL 반영·손실 추정"),
        ("③ 실행 가능한 대안", "Agent 계산·시뮬레이션", "제안+성적표/경영 안건"),
        ("④ 사람의 결정", "HITL 승인·반려", "근거 있는 승인 기록"),
        ("⑤ 표준 흐름 반영", "O2C 등 자동 반영", "갱신된 실행변수"),
    ]
    b = [text(W/2, 40, "관통 문제해결 5단계 — 문제의 성격과 무관하게 같은 순서", 21, NAVY, "bold"),
         text(W/2, 66, "재고든 병목이든 품질이든, 같은 좌표계·같은 분류·같은 검증·같은 실행 계층을 통과한다", 12.5, GRAY)]
    y0, ch, bw, tip = 120, 64, 184, 20
    x0 = (W - (bw*5 - tip*0)) / 2 - 8
    x0 = 30
    for i, (t, s1, s2) in enumerate(steps):
        X = x0 + i*bw
        fill = [TEAL, TEAL, TEAL, NAVY, TEAL][i]
        b.append(chevron(X, y0, bw+tip, ch, fill, tip))
        b.append(text(X+tip+ (bw)/2, y0+28, t, 13, WHITE, "bold"))
        b.append(text(X+tip+(bw)/2, y0+48, s1, 10.8, ICE2))
        b.append(rrect(X+tip/2+8, y0+ch+16, bw-20, 44, ICE, NAVY, 1.2, 8))
        b.append(text(X+tip/2+8+(bw-20)/2, y0+ch+34, "산출물", 10, GRAY))
        b.append(text(X+tip/2+8+(bw-20)/2, y0+ch+51, s2, 10.8, NAVY, "bold"))
    # 사이클 회귀
    b.append(curve(x0+5*bw-30, y0+ch+76, W/2, y0+ch+150, x0+70, y0+ch+80, ACC, 2.4, "ahA", "7,5"))
    b.append(text(W/2, y0+ch+158, "War Room 이상 신호 → 다시 ①의 진단 대상으로 — 프로젝트가 아니라 사이클", 12.2, ACC, "bold"))
    b.append(text(W/2, y0+ch+192, "④에서 갈라지는 분기: 계산 가능한 사안은 담당자 승인으로, 계산할 수 없는 사안(설비·인력·납기)은 경영진 안건으로", 11.8, GRAY))
    b.append(text(W/2, H-16, "3부 22장 — JEDAIX 운영 매뉴얼 v9의 관통 방법론 (정인호, 2026)", 11.5, GRAY))
    svg("fig_221_five_steps", W, H, "".join(b))


# ── 그림 22-2. 도입 유형 2경로 분기도 ──────────────────────────
def fig_222():
    W, H = 960, 640
    b = [text(W/2, 40, "도입 유형 2경로 — 두 개의 출발점, 같은 온톨로지", 22, NAVY, "bold"),
         text(W/2, 66, "방향은 반대지만 도구는 같다 — 사람의 말에서 시작해 시스템의 값으로 끝나는 하나의 파이프라인", 12.2, GRAY)]
    # 시작 노드
    b.append(rrect(330, 92, 300, 54, NAVY, NAVY, 1.6, 12))
    b.append(text(480, 114, "도입의 출발점", 14.5, WHITE, "bold"))
    b.append(text(480, 134, "우리 회사에 ERP가 있는가?", 11.5, ICE2))
    b.append(curve(400, 150, 300, 180, 245, 208, NAVY, 2.4))
    b.append(curve(560, 150, 660, 180, 715, 208, NAVY, 2.4))
    b.append(text(280, 178, "없다", 12.5, NAVY, "bold"))
    b.append(text(680, 178, "있다", 12.5, NAVY, "bold"))
    # 좌: 시나리오 1
    Lx, Ly, Lw = 60, 214, 375
    b.append(rrect(Lx, Ly, Lw, 320, ICE, NAVY, 1.6, 12))
    b.append(text(Lx+Lw/2, Ly+28, "시나리오 1 — ERP 없는 소상공인·소기업", 13.5, NAVY, "bold"))
    b.append(text(Lx+Lw/2, Ly+48, "JEDAIX 단독 시작 → 성장 후 Odoo 확장", 11.5, TEAL, "bold"))
    l_steps = ["① 엑셀 편입 — 데이터 매핑 마법사 (1~2주)",
               "② 표준 템플릿으로 O2C·P2P 가동 (2~4주)",
               "③ 6 Station 대화 축적 — 첫 TA 확정 (1~3개월)",
               "④ Agent 첫 승인·실행 연결 (3~6개월)"]
    for k, s in enumerate(l_steps):
        yy = Ly + 66 + k*44
        b.append(rrect(Lx+18, yy, Lw-36, 34, WHITE, NAVY, 1.1, 7))
        b.append(text(Lx+30, yy+22, s, 10.8, DARK, anchor="start"))
        if k < 3:
            b.append(arrow(Lx+Lw/2, yy+35, Lx+Lw/2, yy+43, TEAL, 1.8, "ahT"))
    b.append(arrow(Lx+Lw/2, Ly+66+3*44+35, Lx+Lw/2, Ly+66+3*44+50, TEAL, 2.2, "ahT"))
    b.append(rrect(Lx+18, Ly+246, Lw-36, 40, TEALBG, TEAL, 1.4, 8))
    b.append(text(Lx+Lw/2, Ly+263, "⑤ 성장 시 Odoo 확장 — 같은 온톨로지 위의 이행", 10.8, TEAL, "bold"))
    b.append(text(Lx+Lw/2, Ly+279, "축적된 코드·프로세스 자산의 승계 (이중 입력 없음)", 10.2, GRAY))
    b.append(text(Lx+Lw/2, Ly+306, "상시 인력 2명 이내 · 암묵지의 형식지화가 곧 기반 구축", 10.8, NAVY))
    # 우: 시나리오 2
    Rx, Ry, Rw = 525, 214, 375
    b.append(rrect(Rx, Ry, Rw, 320, ICE, NAVY, 1.6, 12))
    b.append(text(Rx+Rw/2, Ry+28, "시나리오 2 — ERP 보유 중소기업", 13.5, NAVY, "bold"))
    b.append(text(Rx+Rw/2, Ry+48, "Odoo(원장·실행) × JEDAIX(발굴·판단) 병행", 11.5, TEAL, "bold"))
    r_steps = ["① 진단 결합 — 6 Station 파일럿 인터뷰 (2~4주)",
               "② 데이터 연계 — 명시 이벤트 자동 등록 (1~2개월)",
               "③ 발굴 사이클 — 확정 3건·GL 반영 (2~3개월)",
               "④ 실행·통치 — Agent·War Room 가동 (3~6개월)"]
    for k, s in enumerate(r_steps):
        yy = Ry + 66 + k*44
        b.append(rrect(Rx+18, yy, Rw-36, 34, WHITE, NAVY, 1.1, 7))
        b.append(text(Rx+30, yy+22, s, 10.8, DARK, anchor="start"))
        if k < 3:
            b.append(arrow(Rx+Rw/2, yy+35, Rx+Rw/2, yy+43, TEAL, 1.8, "ahT"))
    b.append(rrect(Rx+18, Ry+246, Rw-36, 40, ICE2, NAVY, 1.4, 8))
    b.append(text(Rx+Rw/2, Ry+263, "데이터는 위로(기록→신호) · 판단은 아래로(확정→파라미터)", 10.5, NAVY, "bold"))
    b.append(text(Rx+Rw/2, Ry+279, "JEDAIX는 ERP를 대체하지 않고 연결한다", 10.2, GRAY))
    b.append(text(Rx+Rw/2, Ry+306, "4역할 체제(6~12개월) · KGI 개선이 성공 판정", 10.8, NAVY))
    b.append(text(W/2, H-42, "공통 원칙: 작게 시작해 얇게 완주한다 — 부서 두 곳·질문 몇 개로 시작해 첫 확정과 첫 승인까지 6개월 이내", 12, NAVY, "bold"))
    b.append(text(W/2, H-16, "3부 22장 — 도입 유형별 시나리오 (JEDAIX 운영 매뉴얼 v9 · 정인호, 2026)", 11.5, GRAY))
    svg("fig_222_two_paths", W, H, "".join(b))


# ── 그림 23-1. 안전재고 사례 타임라인 ──────────────────────────
def fig_231():
    W, H = 980, 520
    events = [
        ("증언", ["“지난달 C라인에서", "두 번 있었습니다”", "6 Station 대화"], False),
        ("공명·반복 확인", ["공명 신호 점등", "3라운드에 걸쳐", "wave 상승"], True),
        ("TA06 확정", ["임계 70% 돌파(입자화)", "품질손실비 계정 반영", "연 약 6천만 원 추정"], False),
        ("Agent 실행", ["정량화·보정계수 계산", "안전재고 100→115", "ROP 150→173 · 승인"], True),
        ("O2C 반영", ["모든 수주→수금 흐름에", "새 값 자동 적용", "BPMN 위 실시간 추적"], False),
    ]
    b = [text(W/2, 40, "안전재고 사례 타임라인 — 증언에서 O2C 반영까지", 22, NAVY, "bold"),
         text(W/2, 66, "관통 5단계가 한 회전을 완주한 기록: 위화감의 언어화 → 확정 → 대안 → 승인 → 표준 반영", 12.2, GRAY)]
    ty = 260
    x0, dx = 110, 190
    b.append(line(60, ty, 920, ty, NAVY, 2.5))
    b.append(arrow(918, ty, 934, ty, NAVY, 2.5))
    for i, (t, sub, below) in enumerate(events):
        X = x0 + i*dx
        b.append(circle(X, ty, 9, TEAL if i not in (2,) else NAVY, WHITE, 2))
        if below:
            yb = ty + 28
            b.append(line(X, ty+9, X, yb-4, GRAY, 1.2))
            b.append(rrect(X-86, yb, 172, 92, ICE, NAVY, 1.3, 9))
            b.append(text(X, yb+22, t, 12.5, NAVY, "bold"))
            b.append(multi(X, yb+42, sub, 10.4, GRAY, 16))
        else:
            yb = ty - 120
            b.append(line(X, ty-9, X, yb+96, GRAY, 1.2))
            hl = i == 2
            b.append(rrect(X-86, yb, 172, 92, TEALBG if hl else ICE, TEAL if hl else NAVY, 1.4, 9))
            b.append(text(X, yb+22, t, 12.5, TEAL if hl else NAVY, "bold"))
            b.append(multi(X, yb+42, sub, 10.4, GRAY, 16))
        b.append(text(X, ty + (118 if not below else -18), "", 10, GRAY))
    # 단계 라벨(관통 5단계 대응)
    labels = ["① 진단", "② 확정으로 가는 검증", "③ 확정·근거", "④ 대안·HITL", "⑤ 표준 반영"]
    for i, lb in enumerate(labels):
        X = x0 + i*dx
        b.append(text(X, ty+ (140 if events[i][2] else -140), lb, 11, TEAL, "bold"))
    b.append(multi(W/2, 448, [
        "사람이 개입한 지점은 대화와 승인뿐 — 전 과정(발화·확인·근거·승인)이 재구성 가능한 기록으로 남는다",
    ], 12.2, NAVY, 20, w="bold"))
    b.append(text(W/2, H-16, "※ A정밀부품㈜는 JEDAIX 운영 매뉴얼 v9가 예시로 쓰는 가상의 제조회사다 — 방법론 작동의 기록이지 실측 성과가 아니다", 11, GRAY))
    svg("fig_231_case_timeline", W, H, "".join(b))


# ── 그림 23-2. 조립 병목 사례 TOC 전후 비교 ────────────────────
def fig_232():
    W, H = 960, 620
    procs = ["재단", "조립", "품질검사", "포장"]
    b = [text(W/2, 40, "조립 병목 사례 — 계획의 기준을 바꾸다 (TOC 전후)", 21, NAVY, "bold"),
         text(W/2, 66, "전체 라인의 실제 처리능력은 병목 공정(조립, 100개/일)을 절대 넘을 수 없다 — Goldratt의 제약이론", 12.2, GRAY)]

    def band(y, title, cap, heights, bottleneck_note, plan, result, result_col, after):
        b.append(rrect(40, y, 880, 214, LGRAY if not after else ICE, GRAY if not after else NAVY, 1.4, 12))
        b.append(text(60, y+28, title, 14, NAVY, "bold", anchor="start"))
        b.append(text(60, y+48, cap, 11.5, GRAY, anchor="start"))
        bx, bw2 = 90, 150
        for i, p in enumerate(procs):
            X = bx + i*(bw2+40)
            hh = heights[i]
            yy = y + 160 - hh
            hl = i == 1
            b.append(rrect(X, yy, bw2, hh, (ACC if hl and not after else (TEAL if hl else ICE2)), NAVY, 1.2, 6))
            tc = WHITE if hl else NAVY
            b.append(text(X+bw2/2, yy+hh/2+5, p, 12.5, tc, "bold"))
            b.append(text(X+bw2/2, y+180, f"{[160,100,130,150][i]}개/일", 10.8, GRAY))
            if i < 3:
                b.append(arrow(X+bw2+4, y+130, X+bw2+36, y+130, NAVY, 2.2))
        b.append(multi(864, y+92, bottleneck_note, 10.6, ACC if not after else TEAL, 16, w="bold"))
        b.append(text(60, y+204, plan, 11.2, DARK, anchor="start"))
        b.append(text(900, y+204, result, 11.5, result_col, "bold", anchor="end"))

    band(92, "도입 전 — 재단 속도 기준 계획", "계획은 가장 빠른 공정(재단 160개/일)의 속도로 짜인다",
         [96, 60, 78, 90], ["조립 앞에", "재공 적체", "(병목 방치)"],
         "계획 160개/일 — 병목 능력(100개/일)의 160%를 요구하는 달성 불가능한 계획",
         "→ 상습 납기 지연", ACC, False)
    band(330, "도입 후 — 병목 기준 계획", "경영진 결정(임시 인력 배치)으로 병목 능력을 갱신하고, MPS는 병목 기준으로 재산출",
         [96, 74, 78, 90], ["병목이 전체", "흐름의 북(drum)", "이 된다"],
         "계획 = 병목의 실제 처리능력 기준 — 불량률은 6 Station 확인 이력에서 자동 산출",
         "→ 납기 준수", TEAL, True)
    b.append(text(W/2, 572, "발견과 정량화는 시스템이, 설비·인력·납기의 판단은 경영진이 — 자동화의 경계선이 방법론에 내장되어 있다", 12.2, NAVY, "bold"))
    b.append(text(W/2, H-16, "※ A정밀부품㈜ 가상 사례(JEDAIX 운영 매뉴얼 v9) — 수치는 설명용 · Goldratt & Cox (1984)", 11, GRAY))
    svg("fig_232_toc_before_after", W, H, "".join(b))


# ── 그림 23-3. 성과 수치 종합 막대 차트 ────────────────────────
def fig_233():
    W, H = 960, 620
    # (라벨, 지표, 값(표시), 막대 크기, 그룹) 그룹0=중기부 5,003개사, 그룹1=개별 기업
    rows = [
        ("생산성", "+30%", 30, 0),
        ("품질", "+43.5%", 43.5, 0),
        ("원가", "-15.9%", 15.9, 0),
        ("납기준수율", "+15.5%", 15.5, 0),
        ("솔젠트 — 생산성", "+73%", 73, 1),
        ("Kompass — 생산성", "+50%", 50, 1),
        ("대성종합열처리 — 불량률", "-50%", 50, 1),
    ]
    b = [text(W/2, 40, "성과 수치 한눈에 — 기록 통합이 만든 실측 개선", 22, NAVY, "bold"),
         text(W/2, 66, "막대는 개선 폭(%)의 크기 — 원가·불량률은 감소(-)가 곧 개선이다", 12.2, GRAY)]
    x0, bh, gap = 330, 34, 14
    y = 130
    scale = 6.6      # 1% -> px
    b.append(text(60, y-14, "중소벤처기업부 — 스마트공장 도입 5,003개사 평균", 12.5, NAVY, "bold", anchor="start"))
    for label, disp, v, g in rows:
        if g == 1 and label.startswith("솔젠트"):
            y += 26
            b.append(text(60, y-14+6, "개별 기업 사례", 12.5, TEAL, "bold", anchor="start"))
        col = NAVY if g == 0 else TEAL
        b.append(text(x0-12, y+bh/2+4, label, 11.5, DARK, anchor="end"))
        b.append(rrect(x0, y, v*scale, bh, col, col, 0, 4))
        b.append(text(x0 + v*scale + 10, y+bh/2+5, disp, 12.5, col, "bold", anchor="start"))
        y += bh + gap
    # 눈금
    axis_y = y + 6
    for tick in (0, 20, 40, 60, 80):
        tx = x0 + tick*scale
        b.append(line(tx, 124, tx, axis_y, "#D5DAE2", 1, "3,3"))
        b.append(text(tx, axis_y+16, f"{tick}", 10.5, GRAY))
    b.append(text(x0 + 40*scale, axis_y+34, "개선 폭 (%)", 10.8, GRAY))
    b.append(multi(W/2, axis_y+64, [
        "이 수치들은 데이터 통합·스마트공장화의 실측 성과다 — 온톨로지 계층은 그 기록 위에 판단을 얹는 다음 단계이며,",
        "10인 미만 소기업의 생산성 향상은 +39%로 평균(+30%)을 웃돈다",
    ], 11.8, NAVY, 19))
    b.append(multi(W/2, axis_y+112, [
        "출처: 중소벤처기업부(2019) 스마트공장 보급사업 성과분석(2014~2017년 도입 5,003개사 — 생산성·품질·원가·납기준수율)",
        "중소벤처기업부 보도자료(솔젠트 주당 생산량 +73%) · 경상남도 보도(대성종합열처리 불량률 −50%) · Odoo 공식 고객 사례(Kompass GmbH 생산성 최대 +50%)",
    ], 10.2, GRAY, 16))
    svg("fig_233_results_chart", W, H, "".join(b))


fig_182(); fig_192(); fig_193(); fig_202(); fig_203()
fig_211(); fig_212(); fig_221(); fig_222(); fig_231(); fig_232(); fig_233()
print("완료")
