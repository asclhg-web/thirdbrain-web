#!/usr/bin/env python3
"""1순위 그림 6점 SVG 생성 + PNG 변환 (신국판 본문폭 기준)."""
import os, math, cairosvg

OUT = os.path.dirname(os.path.abspath(__file__))
F = "NanumGothic"
FB = "NanumBarunGothic"
NAVY = "#1E2761"; ICE = "#E8F0FB"; ICE2 = "#CADCFC"; TEAL = "#028090"
GRAY = "#5A6472"; LGRAY = "#EEF1F5"; ACC = "#B85042"; WHITE = "#FFFFFF"

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def text(x, y, s, size=15, fill=NAVY, w="normal", anchor="middle", font=F):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
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

# ── 그림 P-3. DMAIC × LLM 무한 루프 ─────────────────────────────
def fig_p3():
    W, H = 900, 640; cx, cy, R = W/2, H/2 + 20, 225
    steps = [
        ("Define", "정의", ["경영 질문·KPI"]),
        ("Measure", "수집", ["Odoo·POP·IoT·암묵지"]),
        ("Analyze", "학습", ["ML·지식그래프·LLM"]),
        ("Improve", "추론", ["예측·What-if·처방"]),
        ("Control", "환류", ["표준화·Odoo 액션"]),
    ]
    b = [text(W/2, 42, "DMAIC × LLM 무한 루프", 24, NAVY, "bold")]
    b.append(text(W/2, 68, "사람이 분기마다 돌리던 사이클을, AI가 상시로 돌린다", 14, GRAY))
    pos = []
    for i in range(5):
        a = -math.pi/2 + i * 2*math.pi/5
        pos.append((cx + R*math.cos(a), cy + R*math.sin(a)))
    for i, (x, y) in enumerate(pos):
        nx, ny = pos[(i+1) % 5]
        vx, vy = nx-x, ny-y; L = math.hypot(vx, vy)
        sx, sy = x + vx/L*95, y + vy/L*95
        ex, ey = nx - vx/L*95, ny - vy/L*95
        mx, my = (sx+ex)/2, (sy+ey)/2
        ox, oy = (mx-cx), (my-cy); OL = math.hypot(ox, oy)
        b.append(curve(sx, sy, mx+ox/OL*38, my+oy/OL*38, ex, ey, TEAL, 3, "ahT"))
    for (x, y), (en, ko, sub) in zip(pos, steps):
        b.append(rrect(x-85, y-44, 170, 88, ICE, NAVY, 2, 14))
        b.append(text(x, y-16, en, 17, NAVY, "bold"))
        b.append(text(x, y+6, ko, 15, TEAL, "bold"))
        b.append(multi(x, y+28, sub, 11.5, GRAY))
    b.append(f'<circle cx="{cx}" cy="{cy}" r="86" fill="{NAVY}"/>')
    b.append(multi(cx, cy-18, ["LLM", "무한 루프"], 19, WHITE, 24, w="bold"))
    b.append(multi(cx, cy+34, ["1회전마다", "예측이 정확해진다"], 11.5, ICE2, 15))
    b.append(text(W/2, H-14, "루프의 안전장치: HITL 승인 게이트 · 통계적 검정 · 감사 로그", 12.5, GRAY))
    svg("fig_P3_dmaic_loop", W, H, "".join(b))

# ── 그림 6-1. AX 컨설팅 5단계 로드맵 ────────────────────────────
def fig_61():
    W, H = 1000, 560
    steps = [
        ("1. 진단", "2~4주", ["경영 질문 정의", "데이터 성숙도 진단", "현장 5S 진단"], ["경영 질문 목록", "KPI 트리 초안"]),
        ("2. 기반", "4~8주", ["Odoo 단일 플랫폼", "코드체계 정비", "기준정보 이관"], ["가동 인스턴스", "코드체계 정의서"]),
        ("3. 적재", "4~8주", ["트랜잭션·현장 수집", "지식문서 적재", "암묵지 인터뷰"], ["데이터 파이프라인", "지식베이스"]),
        ("4. 지능화", "8~12주", ["온톨로지 스키마", "예측 모델·에이전트", "DMAIC 루프 가동"], ["지식그래프", "예측 대시보드"]),
        ("5. 환류", "상시", ["판단의 현장 환류", "HITL 학습 루프", "성과 평가"], ["운영 리듬", "KPI 개선 실적"]),
    ]
    b = [text(W/2, 40, "AX 컨설팅 5단계 로드맵", 24, NAVY, "bold"),
         text(W/2, 66, "진단에서 환류까지 — 목표지향 설계(KGI→KPI→데이터→모델)의 실행 순서", 13.5, GRAY)]
    bw, gap, y0 = 176, 16, 100
    x = (W - (bw*5 + gap*4)) / 2
    for i, (t, dur, acts, outs) in enumerate(steps):
        X = x + i*(bw+gap)
        b.append(f'<path d="M{X},{y0} h{bw-18} l18,26 l-18,26 h-{bw-18} l18,-26 z" '
                 f'fill="{NAVY if i==3 else TEAL}" />')
        b.append(text(X+bw/2, y0+22, t, 16, WHITE, "bold"))
        b.append(text(X+bw/2, y0+41, dur, 12, ICE2))
        b.append(rrect(X, y0+70, bw, 118, ICE, TEAL, 1.4, 8))
        b.append(text(X+bw/2, y0+90, "핵심 활동", 12, TEAL, "bold"))
        b.append(multi(X+bw/2, y0+110, acts, 11.5, GRAY, 18))
        b.append(rrect(X, y0+200, bw, 96, LGRAY, GRAY, 1.2, 8))
        b.append(text(X+bw/2, y0+220, "산출물", 12, NAVY, "bold"))
        b.append(multi(X+bw/2, y0+240, outs, 11.5, GRAY, 18))
    yl = y0 + 330
    b.append(curve(x+bw*5+gap*4-30, yl, W/2, yl+95, x+30, yl, ACC, 2.5, "ahA", "7,5"))
    b.append(text(W/2, yl+72, "학습 루프 — 환류의 결과가 다음 진단의 입력이 된다", 13, ACC, "bold"))
    b.append(text(W/2, H-16, "각 단계의 성공 판정을 통과한 뒤 다음 단계로 진입한다 (1부 6장)", 12, GRAY))
    svg("fig_61_roadmap", W, H, "".join(b))

# ── 그림 7-3. 예측 플랫폼 통합 아키텍처 ─────────────────────────
def fig_73():
    W, H = 940, 700
    layers = [
        ("경영의 질문", "자연어 질의 · 아침 브리핑 · What-if 시뮬레이션", NAVY, WHITE),
        ("지식 계층 — 3rd Brain", "Neo4j 온톨로지 지식그래프 + LLM(Claude/Ollama) · GraphRAG 융합판단", TEAL, WHITE),
        ("AX 계층", "n8n 워크플로 허브·ETL  |  Dify 사내 AI 앱  — DMAIC 루프의 배관과 작업대", ICE2, None),
        ("계획 계층", "frePPLe APS — 유한능력 스케줄링·수요예측", ICE2, None),
        ("실행 원장 — 2nd Brain", "Odoo CE: ERP·MES·SCM 70+ 앱 · 단일 PostgreSQL", ICE, None),
        ("현장 계층 — 1st Brain", "작업자·베테랑의 암묵지 · 바코드·태블릿 POP · IoT 센서", LGRAY, None),
    ]
    b = [text(W/2, 40, "예측 플랫폼 통합 아키텍처", 24, NAVY, "bold"),
         text(W/2, 66, "One Platform + Three Boosters — 1부의 결론 그림", 13.5, GRAY)]
    y0, lh, gap = 95, 82, 10
    for i, (t, sub, fill, tcol) in enumerate(layers):
        y = y0 + i*(lh+gap)
        tc = tcol or NAVY
        b.append(rrect(150, y, W-300, lh, fill, NAVY, 1.6, 10))
        b.append(text(W/2, y+34, t, 16.5, tc, "bold"))
        b.append(text(W/2, y+58, sub, 12.5, (ICE2 if tcol else GRAY)))
    top, bot = y0, y0 + 6*lh + 5*gap
    b.append(arrow(105, bot-14, 105, top+14, TEAL, 3.5, "ahT"))
    b.append(multi(62, (top+bot)/2 - 26, ["데이터는", "위로", "(ETL)"], 13.5, TEAL, 19, w="bold"))
    b.append(arrow(W-105, top+14, W-105, bot-14, ACC, 3.5, "ahA"))
    b.append(multi(W-60, (top+bot)/2 - 26, ["판단은", "아래로", "(환류)"], 13.5, ACC, 19, w="bold"))
    b.append(text(W/2, H-16, "개인의 노트와 기업의 DB가 같은 온톨로지 코드로 만난다 (1부 7장)", 12, GRAY))
    svg("fig_73_platform", W, H, "".join(b))

# ── 그림 8-1. 가치사슬 위의 Odoo 모듈 지도 ──────────────────────
def fig_81():
    W, H = 1000, 560
    chain = [
        ("고객 접점", "웹사이트 빌더\n이커머스", "9장"),
        ("영업", "CRM · 판매", "10장"),
        ("조달", "매입(구매)", "11장"),
        ("물류", "재고 관리", "12장"),
        ("생산", "제조 관리\nMRP·품질·정비", "13장"),
        ("재무", "회계", "14장"),
    ]
    b = [text(W/2, 40, "가치사슬 위의 Odoo 모듈 지도", 24, NAVY, "bold"),
         text(W/2, 66, "제2부(8~17장)를 읽는 안내 지도 — 주문에서 결산까지 단일 원장 위를 흐른다", 13.5, GRAY)]
    bw, gap, y0, bh = 146, 12, 110, 132
    x0 = (W - (bw*6 + gap*5)) / 2
    for i, (t, mod, ch) in enumerate(chain):
        X = x0 + i*(bw+gap)
        b.append(rrect(X, y0, bw, bh, ICE, NAVY, 1.8, 10))
        b.append(rrect(X, y0, bw, 34, NAVY, NAVY, 1.8, 10))
        b.append(f'<rect x="{X}" y="{y0+20}" width="{bw}" height="14" fill="{NAVY}"/>')
        b.append(text(X+bw/2, y0+23, t, 14.5, WHITE, "bold"))
        b.append(multi(X+bw/2, y0+62, mod.split("\n"), 13, NAVY, 19, w="bold"))
        b.append(text(X+bw/2, y0+bh-14, ch, 12.5, TEAL, "bold"))
        if i < 5:
            b.append(arrow(X+bw+1, y0+bh/2, X+bw+gap-1, y0+bh/2, TEAL, 2.5, "ahT"))
    def band(y, h, fill, tcol, title, sub):
        b.append(rrect(x0, y, bw*6+gap*5, h, fill, NAVY, 1.5, 9))
        b.append(text(W/2, y+24, title, 14.5, tcol, "bold"))
        b.append(text(W/2, y+44, sub, 12, tcol if tcol == WHITE else GRAY))
    band(y0+156, 54, ICE2, NAVY, "지능 계층 — Odoo AI · 지식센터 (15장)", "AI Fields · 사내문서 RAG · 에이전트 · 음성 요약 — 전 모듈 공통")
    band(y0+222, 54, TEAL, WHITE, "확장 부스터 — frePPLe · n8n · Dify · Neo4j (16장)", "계획·자동화·AI 앱·지식그래프로 서드브레인을 완성")
    band(y0+288, 46, NAVY, WHITE, "단일 PostgreSQL — 하나의 원장, 데이터 정위치의 플랫폼적 보장 (8장)", "")
    b.append(text(W/2, H-30, "총론 8장 → 모듈 9~16장 → 결산 17장(모듈×데이터×AI 매트릭스·도입 시나리오)", 12.5, GRAY))
    svg("fig_81_module_map", W, H, "".join(b))

# ── 그림 21-3. Odoo × JEDAIX 통합 아키텍처 (3뇌 구조) ───────────
def fig_213():
    W, H = 940, 620
    b = [text(W/2, 40, "Odoo × JEDAIX 통합 아키텍처 — 3뇌 구조", 23, NAVY, "bold"),
         text(W/2, 66, "형식지의 원장과 암묵지의 판단 계층이 하나의 루프로 만난다", 13.5, GRAY)]
    b.append(rrect(300, 95, 340, 92, NAVY, NAVY, 2, 12))
    b.append(text(W/2, 130, "융합 판단 — 3rd Brain의 출력", 16, WHITE, "bold"))
    b.append(text(W/2, 156, "예측 · What-if · 실행 제안 · 자연어 답변", 12.5, ICE2))
    by, bh2 = 235, 190
    b.append(rrect(90, by, 340, bh2, ICE, NAVY, 2, 12))
    b.append(text(260, by+30, "Odoo — 2nd Brain", 17, NAVY, "bold"))
    b.append(text(260, by+52, "형식지의 원장 · 실행의 손발", 13, TEAL, "bold"))
    b.append(multi(260, by+80, ["트랜잭션: 수주·발주·재고·제조·회계", "마스터: 품목·BOM·거래처·코드체계",
                                 "실행: 작업지시·발주서·전표 반영"], 12.5, GRAY, 22))
    b.append(rrect(510, by, 340, bh2, "#E5F4F3", TEAL, 2, 12))
    b.append(text(680, by+30, "JEDAIX — 3rd Brain", 17, TEAL, "bold"))
    b.append(text(680, by+52, "암묵지의 발굴 · 의미와 판단", 13, NAVY, "bold"))
    b.append(multi(680, by+80, ["5 Space × 6 Station 워크벤치", "PTGDA · TA 분류 · OWL 온톨로지",
                                 "Agent Workflow · War Room"], 12.5, GRAY, 22))
    b.append(arrow(430, by+58, 508, by+58, NAVY, 2.5))
    b.append(text(469, by+44, "트랜잭션·이벤트", 11, NAVY))
    b.append(arrow(508, by+134, 430, by+134, TEAL, 2.5, "ahT"))
    b.append(text(469, by+156, "확정 판단·규칙 환류", 11, TEAL))
    b.append(arrow(260, by-2, 400, 190, NAVY, 2))
    b.append(arrow(680, by-2, 540, 190, TEAL, 2, "ahT"))
    fy = 480
    b.append(rrect(200, fy, 540, 92, LGRAY, GRAY, 1.6, 12))
    b.append(text(W/2, fy+30, "현장·사람 — 1st Brain", 15.5, NAVY, "bold"))
    b.append(text(W/2, fy+54, "경험과 발화(암묵지의 원천) · HITL 승인(판단의 최종 서명자)", 12.5, GRAY))
    b.append(arrow(330, fy-2, 235, by+bh2+4, NAVY, 2))
    b.append(arrow(610, fy-2, 705, by+bh2+4, TEAL, 2, "ahT"))
    b.append(text(250, fy-16, "실적·기록", 11, NAVY))
    b.append(text(700, fy-16, "발화·증언·승인", 11, TEAL))
    b.append(text(W/2, H-14, "JEDAIX는 ERP를 대체하지 않는다 — 기록 없는 판단은 맹목, 판단 없는 기록은 미완 (3부 21장)", 12, GRAY))
    svg("fig_213_odoo_jedaix", W, H, "".join(b))

# ── 그림 E-1. 서드브레인 합류도 ─────────────────────────────────
def fig_e1():
    W, H = 900, 640
    b = [text(W/2, 40, "서드브레인 — 세 갈래 길의 합류", 24, NAVY, "bold")]
    cx, cy, r = W/2, 300, 150
    cs = [
        (cx, 190, NAVY, "Odoo", ["기업의 기록", "형식지의 원장 (제2부)"]),
        (cx-130, 390, TEAL, "온톨로지", ["기업의 의미", "암묵지의 통치 (제3부)"]),
        (cx+130, 390, ACC, "LLM 루프", ["기업의 언어", "DMAIC 학습 엔진 (제1부)"]),
    ]
    for x, y, c, t, sub in cs:
        b.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" fill-opacity="0.16" '
                 f'stroke="{c}" stroke-width="2.5"/>')
    for x, y, c, t, sub in cs:
        oy = -62 if y < 300 else 66
        b.append(text(x, y+oy, t, 19, c, "bold"))
        b.append(multi(x, y+oy+22, sub, 12.5, GRAY, 17))
    b.append(f'<circle cx="{cx}" cy="{323}" r="66" fill="{NAVY}"/>')
    b.append(multi(cx, 315, ["서드", "브레인"], 20, WHITE, 26, w="bold"))
    b.append(multi(cx, 560, ["기록을 넘어 판단하는, 기업의 세 번째 뇌"], 15, NAVY, w="bold"))
    b.append(text(cx, 590, "“AI가 기업을 대체하지 않는다. 서드브레인을 가진 기업이, 그렇지 않은 기업을 대체한다.”",
                  13, GRAY))
    svg("fig_E1_thirdbrain", W, H, "".join(b))

fig_p3(); fig_61(); fig_73(); fig_81(); fig_213(); fig_e1()
print("완료")
