#!/usr/bin/env python3
"""교보 POD 표지 스프레드: 뒤표지 + 책등 + 앞표지 (재단 여분 3mm 포함).
본문 220쪽·백색모조 100g 기준 책등 12mm. 단위: mm (SVG viewBox=mm)."""
import os, base64, cairosvg

OUT = os.path.dirname(os.path.abspath(__file__))
POD = os.path.join(OUT, "..", "pod")
os.makedirs(POD, exist_ok=True)

BLEED, PW, PH, SPINE = 3, 152, 225, 12.8
W = BLEED + PW + SPINE + PW + BLEED   # 322
H = BLEED + PH + BLEED                # 231
BX0 = 0.0                 # 뒤표지 시작(블리드 포함)
SX = BLEED + PW           # 책등 시작 155
FX = SX + SPINE           # 앞표지 시작 167

F = "NanumGothic"; FM = "NanumMyeongjo"
BLUE = "#1CA5E5"; DBLUE = "#0F86C0"; INK = "#111111"
YELLOW = "#FFDD2D"; WHITE = "#FFFFFF"

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def text(x, y, s, size, fill=INK, w="bold", anchor="middle", fam=F, sp=None, extra=""):
    spat = f' letter-spacing="{sp}"' if sp else ""
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" '
            f'font-weight="{w}" fill="{fill}" text-anchor="{anchor}"{spat} {extra}>{esc(s)}</text>')

b = [f'<rect width="{W}" height="{H}" fill="{BLUE}"/>']

# ── 앞표지: 기존 표지 아트를 패널에 맞춰 배치 (높이 기준, 중앙 크롭, base64 내장) ──
png64 = base64.b64encode(open(os.path.join(OUT, "book_cover_front.png"), "rb").read()).decode()
b.append(f'<image x="{FX}" y="0" width="{W-FX}" height="{H}" '
         f'preserveAspectRatio="xMidYMid slice" '
         f'xlink:href="data:image/png;base64,{png64}"/>')

# ── 책등 (세로쓰기: 각 텍스트를 자기 앵커 기준 90도 회전) ──
b.append(f'<rect x="{SX}" y="0" width="{SPINE}" height="{H}" fill="{DBLUE}"/>')
scx = SX + SPINE/2
def spinetext(y, s, size, fill, weight="bold", anchor="start"):
    x = scx + size*0.36   # 회전 후 책등 폭 중앙에 오도록 베이스라인 보정
    return text(x, y, s, size, fill, weight, anchor,
                extra=f'transform="rotate(90 {x} {y})"')
b.append(spinetext(16, "Odoo를 중심으로 AI ERP 혁명", 5.0, WHITE))
b.append(spinetext(112, "Odoo와 지능형 ERP", 3.6, YELLOW))
b.append(spinetext(H-18, "이형근 · 정인호 · 송무준", 3.5, WHITE, "normal", "end"))

# ── 뒤표지 ──
bx = BLEED + PW/2   # 뒤표지 중심 79
b.append(f'<rect x="0" y="0" width="{SX}" height="{H}" fill="{BLUE}"/>')
b.append(f'<rect x="0" y="{H-9}" width="{SX}" height="9" fill="{DBLUE}"/>')

b.append(text(bx, 34, "기록하는 ERP에서", 8.6, INK))
b.append(text(bx, 45, "판단하는 ERP로", 8.6, INK))
dots = "".join(f'<circle cx="{18+i*3.4}" cy="53" r="0.7" fill="{INK}"/>' for i in range(37))
b.append(dots)

blurb = [
    "30년 ERP·MES·SCM 컨설턴트와 온톨로지 AX 설계자가 함께 쓴",
    "중소기업 지능형 ERP 실행서. 3정5S와 눈으로 보는 관리라는",
    "현장의 오래된 원칙을 데이터의 세계로 옮기고, 6시그마 DMAIC를",
    "LLM이 상시로 돌리는 무한 루프로 재설계한다. 오픈소스 Odoo를",
    "몸체로, 온톨로지-지식그래프를 판단의 층위로 — 기업의 사각지대가",
    "성과로 바뀌는 길을 그림과 사례로 안내한다.",
]
for i, ln in enumerate(blurb):
    b.append(text(bx, 66 + i*7.2, ln, 3.9, INK, "normal", "middle", FM))

# 저자 소개
authors = [
    ("이형근", ["ERP·MES·SCM 컨설턴트로 제조 현장의 데이터(DX)와 AX 경영을",
                "하고 있다. LGCNS, 스마트 추진단을 거쳐 현재 에이에스씨에서",
                "전라권 Odoo 기반 중소기업 지능형 ERP를 컨설팅하고 있다."]),
    ("정인호", ["ERP·MES·SCM 컨설턴트로 업무에 쓸 수 있는 지식으로 키우는",
                "온톨로지 기반 AX 방법론을 설계·구축했다. 한국IBM, 영림원을",
                "거쳐 현재 에이에스씨에서 서울·경기·충남권 Odoo 기반",
                "중소기업 지능형 ERP를 컨설팅하고 있다."]),
    ("송무준", ["ERP·MES·SCM 컨설턴트로 제조 현장의 전산화와 데이터(DX)",
                "경영을 해왔다. LGCNS, 산업현장교수, 스마트공장 평가위원,",
                "AI코칭 위원을 거쳐 현재 에이에스씨에서 부산 및 영남권",
                "Odoo 기반 중소기업 지능형 ERP를 컨설팅하고 있다."]),
]
ay = 114
for name, bio in authors:
    b.append(text(20, ay, name, 4.4, INK, "bold", "start"))
    for i, ln in enumerate(bio):
        b.append(text(20, ay + 6 + i*4.9, ln, 3.25, INK, "normal", "start", FM))
    ay += 6 + len(bio)*4.9 + 4.2

# ISBN 바코드 (발급본 EPS→PNG, 흰 박스 위 배치)
bar64 = base64.b64encode(open(os.path.join(OUT, "barcode_eb_white.png"), "rb").read()).decode()
BBW, BBH = 34, 24                       # 흰 박스
BIW = 30; BIH = BIW * 103.761 / 155.925  # 바코드 (EPS 종횡비 유지)
bx0, by0 = 20, H - 6 - BBH
b.append(f'<rect x="{bx0}" y="{by0}" width="{BBW}" height="{BBH}" rx="1.5" fill="{WHITE}"/>')
b.append(f'<image x="{bx0 + (BBW-BIW)/2}" y="{by0 + (BBH-BIH)/2}" width="{BIW}" height="{BIH:.2f}" '
         f'xlink:href="data:image/png;base64,{bar64}"/>')
b.append(text(SX-20, H-13, "값 15,000원", 3.8, WHITE, "bold", "end"))
b.append(text(SX-20, H-20, "에이에스씨", 3.8, WHITE, "bold", "end"))

doc = (f'<svg xmlns="http://www.w3.org/2000/svg" '
       f'xmlns:xlink="http://www.w3.org/1999/xlink" '
       f'width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">' + "".join(b) + "</svg>")
svg_path = os.path.join(POD, "AI_ERP_혁명_전자책_표지.svg")
open(svg_path, "w").write(doc)
cairosvg.svg2pdf(url=svg_path, write_to=os.path.join(POD, "AI_ERP_혁명_전자책_표지.pdf"))
cairosvg.svg2png(url=svg_path, write_to=os.path.join(POD, "전자책_표지_미리보기.png"), scale=3.2)
print(f"표지 완료: {W}x{H}mm (뒤표지 152 + 책등 {SPINE} + 앞표지 152, 재단여분 {BLEED}mm)")
