#!/usr/bin/env python3
"""교보 POD 표지 스프레드: 뒤표지 + 책등 + 앞표지 (재단 여분 3mm 포함).
본문 210쪽·백색모조 100g 기준 책등 12mm. 단위: mm (SVG viewBox=mm)."""
import os, base64, cairosvg

OUT = os.path.dirname(os.path.abspath(__file__))
POD = os.path.join(OUT, "..", "pod")
os.makedirs(POD, exist_ok=True)

BLEED, PW, PH, SPINE = 3, 152, 225, 12
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
b.append(spinetext(18, "AI ERP 혁명", 5.6, WHITE))
b.append(spinetext(58, "Odoo와 지능형 ERP", 4.2, YELLOW))
b.append(spinetext(H-18, "이형근 · 정인호", 3.8, WHITE, "normal", "end"))

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
    "몸체로, JEDAIX 온톨로지를 판단의 층위로 — 기업의 사각지대가",
    "성과로 바뀌는 길을 그림과 사례로 안내한다.",
]
for i, ln in enumerate(blurb):
    b.append(text(bx, 66 + i*7.2, ln, 3.9, INK, "normal", "middle", FM))

# 4대 키워드 박스
ky = 118
b.append(f'<rect x="20" y="{ky}" width="{SX-40}" height="46" rx="3" fill="{WHITE}" fill-opacity="0.92"/>')
b.append(text(bx, ky+9.5, "이 책이 안내하는 네 가지 지능화", 4.4, DBLUE, "bold"))
kws = ["수요예측을 통한 영업 지능화", "재고 최적화 및 생산계획 자동화",
       "IoT를 이용한 설비예지 지능화", "기업의 노하우를 지식센터 지능화"]
for i, k in enumerate(kws):
    yy = ky + 18 + i*8
    b.append(f'<circle cx="30" cy="{yy-1.4}" r="1.1" fill="{BLUE}"/>')
    b.append(text(34, yy, k, 4.1, INK, "bold", "start"))

# 저자
b.append(text(20, 180, "이형근", 4.6, INK, "bold", "start"))
b.append(text(20, 186, "ERP·MES·SCM 30년, 제조 현장의 데이터 컨설턴트 (에이에스씨)", 3.4, INK, "normal", "start", FM))
b.append(text(20, 194, "정인호", 4.6, INK, "bold", "start"))
b.append(text(20, 200, "JEDAIX 온톨로지 AX 방법론 설계자 (i7)", 3.4, INK, "normal", "start", FM))

# ISBN·바코드 자리 (입고 시 발급 바코드로 교체)
b.append(f'<rect x="20" y="{H-26}" width="42" height="17" rx="1.5" fill="{WHITE}"/>')
b.append(text(41, H-17.5, "ISBN", 3.6, "#888888", "bold"))
b.append(text(41, H-12.5, "(바코드 자리)", 2.8, "#888888", "normal"))
b.append(text(SX-20, H-13, "값 00,000원", 3.8, WHITE, "bold", "end"))
b.append(text(SX-20, H-20, "에이에스씨", 3.8, WHITE, "bold", "end"))

doc = (f'<svg xmlns="http://www.w3.org/2000/svg" '
       f'xmlns:xlink="http://www.w3.org/1999/xlink" '
       f'width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">' + "".join(b) + "</svg>")
svg_path = os.path.join(POD, "AI_ERP_혁명_POD_표지.svg")
open(svg_path, "w").write(doc)
cairosvg.svg2pdf(url=svg_path, write_to=os.path.join(POD, "AI_ERP_혁명_POD_표지.pdf"))
cairosvg.svg2png(url=svg_path, write_to=os.path.join(POD, "표지_미리보기.png"), scale=3.2)
print(f"표지 완료: {W}x{H}mm (뒤표지 152 + 책등 {SPINE} + 앞표지 152, 재단여분 {BLEED}mm)")
