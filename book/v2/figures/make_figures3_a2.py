#!/usr/bin/env python3
"""3순위 보조 도해 — 1부 5~7장 담당분 7점 (SVG+PNG).
그림 5-1, 5-2, 5-3, 6-2, 6-3, 7-1, 7-2
"""
import math
from figlib import *

# ── 그림 5-1. LLM 무한 루프 상세 아키텍처 ───────────────────────
def fig_51():
    W, H = 960, 640
    b = [text(W/2, 38, "LLM 무한 루프 상세 아키텍처", 22, NAVY, "bold"),
         text(W/2, 62, "분기의 사이클에서 상시의 사이클로 — 다섯 단계를 도구가 잇는다", 12.5, GRAY)]
    # 오케스트레이터
    b.append(rrect(170, 80, 690, 52, NAVY, NAVY, 2, 10))
    b.append(text(515, 101, "LLM 에이전트 오케스트레이터", 16, WHITE, "bold"))
    b.append(text(515, 121, "각 단계의 산출을 읽고 다음 도구를 호출하며 전체를 서사로 기록 — Dify 에이전트 · n8n 워크플로", 11.5, ICE2))
    b.append(arrow(245, 134, 245, 162, TEAL, 2.5, "ahT"))
    b.append(text(258, 152, "상시 반복", 11.5, TEAL, "bold", "start"))
    rows = [
        ("Define", "정의", ["관리도 이상·경영 질문을 받아", "문제 정의문·CTQ·판정 기준 작성"],
         ["Odoo 대시보드", "SPC 관리도 알람"]),
        ("Measure", "수집", ["3원천(트랜잭션·현장·암묵지) 수집", "+ 측정 신뢰성 검증"],
         ["Odoo 트랜잭션·태블릿 POP·IoT", "n8n ETL 파이프라인"]),
        ("Analyze", "학습", ["통계 검정 × ML 패턴 × 그래프 역추적", "→ 원인 확정"],
         ["통계·ML 모델", "Neo4j 지식그래프"]),
        ("Improve", "추론", ["개선안 생성 → What-if 시뮬레이션", "→ 대안 비교 성적표"],
         ["LLM(Claude/Ollama) 생성", "frePPLe·디지털 트윈"]),
        ("Control", "환류", ["마스터·규칙 개정을 Odoo로 환류", "+ 관리도 재설정·상시 감시"],
         ["Odoo 마스터·자동화 규칙", "감사 로그"]),
    ]
    ys = [166, 236, 306, 376, 510]   # Control은 게이트 아래
    for (en, ko, desc, tools), y in zip(rows, ys):
        b.append(rrect(170, y, 150, 58, ICE, NAVY, 1.8, 10))
        b.append(text(245, y+25, en, 15, NAVY, "bold"))
        b.append(text(245, y+45, ko, 12.5, TEAL, "bold"))
        b.append(multi(340, y+26, desc, 12, DARK, 19, anchor="start"))
        b.append(rrect(620, y, 240, 58, LGRAY, GRAY, 1.2, 8))
        b.append(multi(740, y+26, tools, 11.5, GRAY, 18))
    for i in range(3):  # Define→Measure→Analyze→Improve
        b.append(arrow(245, ys[i]+60, 245, ys[i+1]-2, NAVY, 2))
    # 승인 게이트 (Improve와 Control 사이)
    b.append(arrow(245, ys[3]+60, 245, 458, ACC, 2, "ahA"))
    b.append(rrect(170, 460, 690, 36, "#F7E6E2", ACC, 1.8, 8, dash="6,4"))
    b.append(text(515, 483, "승인 게이트 — Human-in-the-Loop: 승인 · 수정 · 반려(+이유 기록)", 13, ACC, "bold"))
    b.append(arrow(245, 496, 245, ys[4]-2, ACC, 2, "ahA"))
    # 좌측 학습 환류 루프
    b.append(line(170, ys[4]+29, 118, ys[4]+29, ACC, 2.2, "6,4"))
    b.append(line(118, ys[4]+29, 118, 195, ACC, 2.2, "6,4"))
    b.append(arrow(118, 195, 166, 195, ACC, 2.2, "ahA", "6,4"))
    b.append(multi(58, 300, ["결과 관측 —", "예측 오차·", "개입 기록이", "다음 회전의", "학습 데이터"],
                   11.5, ACC, 17, w="bold"))
    b.append(text(W/2, 620, "사람이 분기 단위로 돌리던 DMAIC를, 에이전트는 문제의 크기에 따라 하루·한 시간 단위로 돌린다 (5.7절)",
                  11.5, GRAY))
    svg("fig_51_llm_loop_detail", W, H, "".join(b))

# ── 그림 5-2. 루프 학습 곡선 ────────────────────────────────────
def fig_52():
    W, H = 900, 540
    b = [text(W/2, 38, "루프 학습 곡선", 22, NAVY, "bold"),
         text(W/2, 62, "루프의 누적 회전수가 경험량, 예측 오차가 단위 비용 — 회전할수록 정확해진다", 12.5, GRAY)]
    x0, x1, yb, yt = 110, 840, 420, 95
    b.append(arrow(x0, yb, x1+8, yb, DARK, 1.6, "ahG"))
    b.append(arrow(x0, yb, x0, yt-8, DARK, 1.6, "ahG"))
    b.append(text((x0+x1)/2, 452, "루프 누적 회전 수", 12.5, DARK))
    b.append(text(x0-8, 84, "예측 오차", 12.5, DARK, "normal", "end"))
    def fx(t): return x0 + 7.3 * t
    def fy(e): return yb - (e) * (300/45)
    base, amp, tau = 9, 33, 18
    pts = []
    for i in range(101):
        t = i
        e = base + amp * math.exp(-t/tau)
        pts.append(f"{fx(t):.1f},{fy(e):.1f}")
    b.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{TEAL}" stroke-width="3"/>')
    # 점근선 = 우연 변동의 한계
    b.append(line(x0, fy(base), x1, fy(base), GRAY, 1, "5,4"))
    b.append(text(x1-4, fy(base)-8, "우연 변동의 한계 (환원 불가능한 오차)", 11.5, GRAY, "normal", "end"))
    # 주석 — 초기 급감
    e10 = base + amp * math.exp(-10/tau)
    b.append(circle(fx(10), fy(e10), 4.5, TEAL))
    b.append(multi(330, 140, ["초기 회전 — 오차 급감 구간", "큰 원인이 먼저 제거된다"], 12.5, NAVY, 18, w="bold"))
    b.append(line(258, 150, fx(10)+8, fy(e10)-6, GRAY, 1))
    # 주석 — 후기 완만
    e70 = base + amp * math.exp(-70/tau)
    b.append(circle(fx(70), fy(e70), 4.5, TEAL))
    b.append(multi(660, 240, ["후기 회전 — 완만한 수렴 구간", "개입 기록·암묵지가 미세 조정"], 12.5, NAVY, 18, w="bold"))
    b.append(line(640, 268, fx(70)+2, fy(e70)-8, GRAY, 1))
    # 회전수 대비 브레이스
    b.append(line(x0, 478, x0+30, 478, ACC, 3.5))
    b.append(text(x0+40, 482, "사람의 DMAIC — 연 3~4회전", 11.5, ACC, "bold", "start"))
    b.append(line(x0, 506, x1, 506, TEAL, 3.5))
    b.append(text((x0+x1)/2, 526, "데이터 루프 — 연 수백 회전, 같은 곡선을 훨씬 빠르게 내려간다", 11.5, TEAL, "bold"))
    svg("fig_52_learning_curve", W, H, "".join(b))

# ── 그림 5-3. 루프의 3중 안전장치 ───────────────────────────────
def fig_53():
    W, H = 940, 470
    b = [text(W/2, 38, "루프의 3중 안전장치", 22, NAVY, "bold"),
         text(W/2, 62, "통계적 검정 · HITL 승인 게이트 · 감사 로그 — 자동화의 범위는 축적된 성적표가 결정한다", 12.5, GRAY)]
    xs = [35, 215, 395, 575, 755]
    # 루프 경로의 단계 박스 3개
    stages = [(0, "Analyze", "원인 확정", "통계·그래프 분석"),
              (2, "Improve", "개선 제안", "LLM 생성·시뮬레이션"),
              (4, "Control", "실행·환류", "Odoo 마스터·규칙 개정")]
    for idx, en, ko, sub in stages:
        x = xs[idx]
        b.append(rrect(x, 150, 150, 96, ICE, NAVY, 1.8, 10))
        b.append(text(x+75, 182, en, 15, NAVY, "bold"))
        b.append(text(x+75, 204, ko, 12.5, TEAL, "bold"))
        b.append(text(x+75, 228, sub, 11, GRAY))
    # 게이트 2개 (경로 위에 세워진 관문)
    gates = [(1, "안전장치 1", "통계적 검정", ["전후 차이의 유의성", "층별 재현·파일럿 확인"]),
             (3, "안전장치 2", "HITL 승인 게이트", ["사람이 승인·수정·반려", "수정·반려 이유 기록"])]
    for idx, no, name, lines in gates:
        x = xs[idx]
        b.append(rrect(x, 130, 150, 136, "#F7E6E2", ACC, 1.8, 10, dash="7,4"))
        b.append(text(x+75, 156, no, 11.5, ACC, "bold"))
        b.append(text(x+75, 180, name, 14, ACC, "bold"))
        b.append(multi(x+75, 208, lines, 11, GRAY, 17))
    # 경로 화살표
    for i in range(4):
        b.append(arrow(xs[i]+152, 198, xs[i+1]-3, 198, TEAL, 2.5, "ahT"))
    # 기각·반려 회귀 화살표
    b.append(curve(270, 126, 180, 92, 115, 146, ACC, 2, "ahA", "6,4"))
    b.append(text(186, 86, "기각 — 재분석", 11, ACC, "bold"))
    b.append(curve(650, 126, 560, 92, 495, 146, ACC, 2, "ahA", "6,4"))
    b.append(text(566, 86, "반려 — 근거 보강", 11, ACC, "bold"))
    # 감사 로그 밴드
    for cx, ytop in [(110, 248), (290, 268), (470, 248), (650, 268), (830, 248)]:
        b.append(line(cx, ytop, cx, 328, GRAY, 1, "3,3"))
    b.append(rrect(35, 330, 870, 76, LGRAY, GRAY, 1.4, 10))
    b.append(text(W/2, 358, "안전장치 3 — 감사 로그 · 폭주 방지", 13.5, NAVY, "bold"))
    b.append(text(W/2, 382, "모든 회전의 데이터→분석→제안→승인→결과 기록  |  회전·변경 한도, 임계 초과 시 사람을 호출하는 서킷 브레이커",
                  11.5, GRAY))
    b.append(text(W/2, 444, "로그가 없는 루프는 반성할 수 없고, 반성하지 못하는 루프는 개선되지 않는다 (5.8절)", 11.5, GRAY))
    svg("fig_53_safeguards", W, H, "".join(b))

# ── 그림 6-2. KGI→KPI→데이터→모델 역방향 설계 깔때기 ────────────
def fig_62():
    W, H = 940, 570
    b = [text(W/2, 38, "KGI→KPI→데이터→모델 — 역방향 설계", 22, NAVY, "bold"),
         text(W/2, 62, "측정 체계는 목표에서 내려가며 설계된다(GQM) — 기술에서 출발하는 상향식은 실패한다", 12.5, GRAY)]
    cx = 320
    b.append(text(cx, 102, "역방향 설계 — 목표에서 데이터로", 14, TEAL, "bold"))
    layers = [
        (420, NAVY, WHITE, ICE2, "KGI — 경영 목표", "예: 2년 내 납기준수율 95% 달성"),
        (360, TEAL, WHITE, ICE2, "경영 질문", "지연의 주된 원인 공정은 어디인가"),
        (300, ICE2, NAVY, GRAY, "KPI — 판정 지표", "공정별 지연 기여도·준수율"),
        (240, ICE, NAVY, GRAY, "필요 데이터", "작업지시·POP 실적·외주 납기"),
        (185, LGRAY, NAVY, GRAY, "모델·온톨로지", "언제나 마지막에 선택된다"),
    ]
    y = 120
    for i, (w, fill, tc, sc, t, sub) in enumerate(layers):
        b.append(rrect(cx-w/2, y, w, 60, fill, NAVY, 1.6, 10))
        b.append(text(cx, y+26, t, 14, tc, "bold"))
        b.append(text(cx, y+47, sub, 11.5, sc))
        if i < 4:
            b.append(arrow(cx, y+62, cx, y+72, NAVY, 2))
        y += 74
    b.append(text(75, 118, "설계 방향", 11, TEAL, "bold"))
    b.append(arrow(75, 128, 75, 470, TEAL, 3, "ahT"))
    # 우측 — 상향식 실패 경로
    b.append(line(590, 95, 590, 490, "#D5DBE3", 1, "4,4"))
    b.append(text(760, 102, "상향식 — 기술에서 출발", 14, GRAY, "bold"))
    b.append(rrect(650, 124, 220, 64, LGRAY, GRAY, 1.5, 10, dash="5,4"))
    b.append(text(760, 150, "경영 목표 달성 …?", 13, GRAY, "bold"))
    b.append(text(760, 170, "질문 없는 지표·모델", 11.5, GRAY))
    b.append(rrect(650, 410, 220, 64, LGRAY, GRAY, 1.5, 10))
    b.append(text(760, 436, "일단 AI·모델부터 도입", 13, DARK, "bold"))
    b.append(text(760, 456, "쓸모는 나중에 찾자", 11.5, GRAY))
    b.append(arrow(760, 406, 760, 192, GRAY, 2.5, "ahG", "6,4"))
    b.append(line(732, 272, 788, 328, ACC, 7))
    b.append(line(788, 272, 732, 328, ACC, 7))
    b.append(text(760, 360, "범위 폭주 · 편익 증명 실패", 12.5, ACC, "bold"))
    b.append(text(W/2, 540, "수집할 데이터와 만들 모델이 질문 목록에서 연역된다 — 범위 통제·사전 편익 정의·자명한 우선순위 (6.2절)",
                  11.5, GRAY))
    svg("fig_62_reverse_funnel", W, H, "".join(b))

# ── 그림 6-3. 경량 모델 3주 간트 ────────────────────────────────
def fig_63():
    W, H = 940, 480
    b = [text(W/2, 38, "경량 모델 — 초소형 기업의 3주 로드맵", 22, NAVY, "bold"),
         text(W/2, 62, "구축은 제공자가 대행하고, 사업자는 노하우 제공과 검증만 담당한다", 12.5, GRAY)]
    x0, cw = 240, 220
    for i, wk in enumerate(["1주차", "2주차", "3주차"]):
        b.append(text(x0 + cw*i + cw/2, 105, wk, 13, NAVY, "bold"))
    for i in range(4):
        b.append(line(x0 + cw*i, 92, x0 + cw*i, 440, "#D5DBE3", 1))
    b.append(text(40, 128, "제공자 측 — 구축 대행", 12.5, NAVY, "bold", "start"))
    bars = [
        (0, 135, "1주. 온보딩", ["테넌트·LLM·운영 앱 배치", "마켓·택배 외부 연동"]),
        (1, 205, "2주. 지식적재", ["상품·FAQ·작업표준 적재", "자동화 구성"]),
        (2, 275, "3주. 현장적용", ["모바일 배치·리허설", "미세조정"]),
    ]
    for col, y, name, tasks in bars:
        X = x0 + cw*col + 4
        b.append(rrect(X, y, cw-8, 60, TEAL, TEAL, 0, 8))
        b.append(text(X + (cw-8)/2, y+22, name, 13, WHITE, "bold"))
        b.append(multi(X + (cw-8)/2, y+40, tasks, 11, "#DFF1EF", 15))
        if col < 2:
            b.append(arrow(X + cw - 10, y + 62, X + cw + 6, y + 76, TEAL, 1.8, "ahT"))
    b.append(line(40, 352, 900, 352, GRAY, 1, "4,4"))
    b.append(text(40, 374, "사업자 측 — 검증·노하우 제공", 12.5, NAVY, "bold", "start"))
    owner = ["기준정보(품목·거래처) 확인", "노하우·자료 제공(대화·음성)", "하루 시범 운영 · 피드백"]
    for i, t in enumerate(owner):
        X = x0 + cw*i + 4
        b.append(rrect(X, 384, cw-8, 44, ICE, TEAL, 1.3, 8))
        b.append(text(X + (cw-8)/2, 410, t, 11.5, DARK))
    b.append(text(W/2, 464, "1~2단계가 표준 템플릿으로 선반영된 5단계 방법론의 축약 — 사업이 자라면 정식 방법론으로 무중단 이행 (6.11절)",
                  11.5, GRAY))
    svg("fig_63_3week_gantt", W, H, "".join(b))

# ── 그림 7-1. PQ 분석 파레토 차트 ───────────────────────────────
def fig_71():
    W, H = 940, 560
    b = [text(W/2, 38, "PQ 분석 — 품종별 생산량의 파레토", 22, NAVY, "bold"),
         text(W/2, 62, "'다품종소량 공장' 안에는 성격이 다른 두 개의 공장이 섞여 있다 — 나누면 각자 살아난다", 12.5, GRAY)]
    x0, yb, yt = 100, 430, 120
    vals = [230, 185, 150, 98, 58, 44, 36, 30, 25, 21, 17, 14, 11, 9, 7]
    total = sum(vals)
    names = "ABCDEFGHIJKLMNO"
    bw, step = 38, 52
    scale = (yb - 145) / max(vals)
    b.append(line(x0, yb, 890, yb, DARK, 1.5))
    b.append(text(60, 108, "생산량", 12, DARK))
    b.append(line(x0, yt, 890, yt, "#D5DBE3", 1, "4,3"))
    b.append(text(894, yt+4, "100%", 10.5, GRAY, "normal", "start"))
    cum = 0; pts = []; split_cum = 0
    for i, v in enumerate(vals):
        X = x0 + 10 + i*step
        h = v * scale
        fill = TEAL if i < 4 else ICE2
        b.append(rrect(X, yb-h, bw, h, fill, NAVY, 0.8, 2))
        b.append(text(X+bw/2, yb+18, names[i], 11, GRAY))
        cum += v
        pct = cum/total*100
        if i == 3: split_cum = pct
        pts.append((X+bw/2, yb - pct*(yb-yt)/100))
    b.append('<polyline points="' + " ".join(f"{px:.1f},{py:.1f}" for px, py in pts) +
             f'" fill="none" stroke="{NAVY}" stroke-width="2"/>')
    for px, py in pts:
        b.append(circle(px, py, 3, NAVY))
    b.append(text(pts[-1][0]-14, pts[-1][1]-12, "누적 구성비", 11.5, NAVY, "bold", "end"))
    # 그룹 분리선
    xs = x0 + 10 + 4*step - 7
    b.append(line(xs, 105, xs, yb, ACC, 2, "7,5"))
    b.append(text(xs, 98, "그룹 분리선", 11.5, ACC, "bold"))
    b.append(text(pts[3][0]-9, pts[3][1]-12, f"{split_cum:.0f}%", 12, NAVY, "bold", "end"))
    # 그룹 브래킷
    b.append(line(x0+10, 468, xs-6, 468, TEAL, 3.5))
    b.append(text(x0+10, 490, f"다량품 그룹 — 품종 27% · 물량 {split_cum:.0f}% → 흐름 라인·전용 편성", 12, TEAL, "bold", "start"))
    b.append(line(xs+6, 468, 886, 468, GRAY, 3.5))
    b.append(text(886, 514, "소량품 그룹 — 그룹 테크놀로지 셀·기능별 편성", 12, GRAY, "bold", "end"))
    b.append(text(W/2, 544, "PQ 분석은 편성 재구축의 첫 도구 — 다량품에는 흐름 생산을, 소량품에는 유연한 그룹별 편성을 (7.2절)",
                  11.5, GRAY))
    svg("fig_71_pq_pareto", W, H, "".join(b))

# ── 그림 7-2. Neck 공정과 리드타임 ──────────────────────────────
def fig_72():
    W, H = 940, 440
    b = [text(W/2, 38, "Neck 공정과 리드타임", 22, NAVY, "bold"),
         text(W/2, 62, "공장 전체의 리드타임은 Neck 공정이 하나만 있어도 그것에 의해 결정된다", 12.5, GRAY)]
    cy = 225
    def seg(x1, x2, hh, fill=ICE, stroke=NAVY, sw=1.6):
        return rrect(x1, cy-hh/2, x2-x1, hh, fill, stroke, sw, 4)
    def conn(x1, h1, x2, h2):
        return (f'<path d="M{x1},{cy-h1/2} L{x2},{cy-h2/2} L{x2},{cy+h2/2} L{x1},{cy+h1/2} z" '
                f'fill="{ICE}" stroke="{NAVY}" stroke-width="1.2"/>')
    # 연결부 먼저, 관 나중
    b.append(conn(205, 90, 235, 80))
    b.append(conn(385, 80, 425, 28))
    b.append(conn(535, 28, 565, 80))
    b.append(conn(715, 80, 745, 90))
    b.append(seg(55, 205, 90))
    b.append(seg(235, 385, 80))
    b.append(seg(565, 715, 80))
    b.append(seg(745, 895, 90))
    b.append(seg(425, 535, 28, "#F7E6E2", ACC, 2.2))
    # 라벨
    labels = [(130, "선반", "능력 100/일"), (310, "밀링", "능력 90/일"),
              (640, "연마", "능력 90/일"), (820, "조립", "능력 100/일")]
    for x, name, cap in labels:
        b.append(text(x, 130, name, 13, NAVY, "bold"))
        b.append(text(x, 150, cap, 11.5, GRAY))
    b.append(text(480, 118, "Neck — 열처리", 14, ACC, "bold"))
    b.append(text(480, 138, "능력 35/일", 12, ACC, "bold"))
    b.append(line(480, 146, 480, 205, ACC, 1, "3,3"))
    # 흐름 밴드 (Neck 이후는 넓은 관에서도 가늘게 흐른다)
    def band(x1, x2, hh):
        return (f'<path d="M{x1},{cy-hh/2} H{x2} L{x2+13},{cy} L{x2},{cy+hh/2} H{x1} z" '
                f'fill="{TEAL}" fill-opacity="0.85"/>')
    b.append(band(75, 172, 26))
    b.append(band(248, 320, 22))
    b.append(band(435, 512, 10))
    b.append(band(578, 690, 10))
    b.append(band(758, 862, 10))
    # 체류품의 산 (Neck 직전 정체)
    dots = [(340, cy-20), (360, cy-20), (380, cy-20), (400, cy-18),
            (340, cy), (360, cy), (380, cy), (400, cy),
            (340, cy+20), (360, cy+20), (380, cy+20), (400, cy+18)]
    for dx, dy in dots:
        b.append(circle(dx, dy, 6, "#9AA4B0"))
    b.append(multi(340, 302, ["체류품의 산", "리드타임의 80~90%는 정체"], 11.5, DARK, 16))
    b.append(line(352, 288, 372, 254, GRAY, 1))
    b.append(text(60, 302, "투입 100/일", 11.5, DARK, "normal", "start"))
    b.append(text(895, 302, "전체 산출 = Neck의 능력(35/일)", 11.5, DARK, "bold", "end"))
    # 하단 메시지
    b.append(rrect(150, 340, 640, 58, ICE, NAVY, 1.5, 10))
    b.append(text(W/2, 364, "병목에서 잃은 한 시간은 시스템 전체가 잃은 한 시간이다 (TOC)", 13, NAVY, "bold"))
    b.append(text(W/2, 386, "Neck 해소의 실상은 '이동' — 대안 평가는 반드시 차기 병목의 위치까지 계산한다 (7.2절)", 11.5, GRAY))
    svg("fig_72_neck_pipe", W, H, "".join(b))

fig_51(); fig_52(); fig_53(); fig_62(); fig_63(); fig_71(); fig_72()
print("완료")
