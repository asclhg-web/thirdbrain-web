#!/usr/bin/env python3
"""책 표지 재현본 — 사용자 제공 디자인(에이에스씨) 기반 SVG 재현.
원본 이미지 파일 수령 시 figures/book_cover_front.png 를 교체하면 된다."""
import os, math, cairosvg

OUT = os.path.dirname(os.path.abspath(__file__))
F = "NanumGothic"
BLUE = "#1CA5E5"; BLUE2 = "#5BC4F0"; YELLOW = "#FFDD2D"; YELLOW2 = "#FFE566"
INK = "#111111"; WHITE = "#FFFFFF"; DBLUE = "#0F86C0"

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def text(x, y, s, size, fill=INK, w="bold", anchor="middle", spacing=None):
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x}" y="{y}" font-family="{F}" font-size="{size}" '
            f'font-weight="{w}" fill="{fill}" text-anchor="{anchor}"{sp}>{esc(s)}</text>')

def scallop(cx, cy, r, fill, petals=12):
    out = []
    for i in range(petals):
        a = i * 2 * math.pi / petals
        out.append(f'<circle cx="{cx + r*0.88*math.cos(a)}" cy="{cy + r*0.88*math.sin(a)}" '
                   f'r="{r*0.30}" fill="{fill}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>')
    return "".join(out)

def browser(x, y, w, h, header, bar_fill=INK):
    b = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{WHITE}" stroke="{INK}" stroke-width="5"/>',
         f'<rect x="{x}" y="{y}" width="{w}" height="{header}" rx="10" fill="{bar_fill}"/>',
         f'<rect x="{x}" y="{y+header-12}" width="{w}" height="12" fill="{bar_fill}"/>',
         f'<circle cx="{x+22}" cy="{y+header/2}" r="5" fill="{WHITE}"/>',
         f'<circle cx="{x+42}" cy="{y+header/2}" r="5" fill="{WHITE}" fill-opacity="0.6"/>']
    return "".join(b)

W, H = 890, 1260
b = [f'<rect width="{W}" height="{H}" fill="{WHITE}"/>']

# ── 상단 일러스트 영역 ──
b.append(f'<circle cx="330" cy="330" r="215" fill="{YELLOW2}"/>')
b.append(f'<circle cx="660" cy="300" r="120" fill="{YELLOW2}"/>')

# 좌측 브라우저(파이차트+목록)
b.append(browser(125, 235, 260, 155, 36))
b.append(f'<circle cx="192" cy="315" r="38" fill="{YELLOW}" stroke="{INK}" stroke-width="4"/>')
b.append(f'<path d="M192,315 L192,277 A38,38 0 0,1 224,333 z" fill="{BLUE}" stroke="{INK}" stroke-width="3"/>')
for i in range(4):
    b.append(f'<circle cx="252" cy="{288+i*24}" r="6" fill="{YELLOW}"/>')
    b.append(f'<rect x="266" y="{283+i*24}" width="100" height="9" rx="4" fill="{INK}" fill-opacity="{0.85-0.1*i}"/>')

# 우측 브라우저(막대차트)
b.append(browser(578, 225, 175, 170, 30))
bars = [(600, 46), (630, 66), (660, 96), (690, 76), (718, 56)]
for x, hh in bars:
    b.append(f'<rect x="{x}" y="{375-hh}" width="20" height="{hh}" fill="{BLUE}"/>')
b.append(f'<line x1="595" y1="375" x2="740" y2="375" stroke="{INK}" stroke-width="4"/>')

# 중앙 브라우저(파랑 헤더 + 노랑 블록)
b.append(browser(365, 305, 265, 195, 34, BLUE))
b.append(f'<rect x="385" y="352" width="225" height="16" rx="6" fill="{YELLOW}"/>')
b.append(f'<rect x="385" y="380" width="105" height="72" rx="6" fill="{YELLOW}"/>')
b.append(f'<rect x="502" y="380" width="108" height="30" rx="6" fill="{BLUE2}" fill-opacity="0.5"/>')
b.append(f'<rect x="502" y="420" width="108" height="30" rx="6" fill="{BLUE2}" fill-opacity="0.5"/>')
for i in range(3):
    b.append(f'<circle cx="{545+i*28}" cy="472" r="8" fill="{INK}"/>')

# 인물 (모니터 앞)
b.append(f'<path d="M255,395 a48,52 0 1,1 60,8 l-6,40 l-50,-6 z" fill="{WHITE}" stroke="{INK}" stroke-width="5"/>')  # 얼굴
b.append(f'<path d="M247,362 a52,52 0 0,1 74,-18 l6,26 a40,40 0 0,0 -62,10 z" fill="{INK}"/>')  # 머리
b.append(f'<circle cx="296" cy="378" r="3.5" fill="{INK}"/>')
b.append(f'<path d="M300,398 q10,8 20,2" stroke="{INK}" stroke-width="3.5" fill="none"/>')
b.append(f'<path d="M190,640 q-6,-150 76,-190 q60,-24 108,18 l58,52 q16,16 2,32 q-16,16 -32,2 l-46,-40 l-10,126 z" '
         f'fill="{BLUE}" stroke="{INK}" stroke-width="5"/>')  # 몸통·팔
# 모니터
b.append(f'<rect x="440" y="470" width="185" height="130" rx="10" fill="{WHITE}" stroke="{INK}" stroke-width="6"/>')
b.append(f'<path d="M505,600 h56 l10,36 h-76 z" fill="{BLUE}" stroke="{INK}" stroke-width="5"/>')
b.append(f'<rect x="470" y="636" width="130" height="10" rx="5" fill="{INK}"/>')
b.append(f'<path d="M395,600 q30,26 70,20" stroke="{INK}" stroke-width="5" fill="none"/>')  # 키보드 손

# ── 배지 2개 ──
b.append(scallop(196, 170, 96, BLUE2))
b.append(text(196, 148, "Odoo AI ERP", 26, INK))
b.append(text(196, 178, "매출증대", 17, INK, "normal"))
b.append(text(196, 200, "생산성 향상", 17, INK, "normal"))
b.append(text(196, 222, "품질 향상", 17, INK, "normal"))
b.append(scallop(700, 158, 92, YELLOW))
b.append(text(700, 136, "에이전틱 AI", 25, INK))
b.append(text(700, 164, "업무 자동화", 16.5, INK, "normal"))
b.append(text(700, 185, "비용절감 30%", 16.5, INK, "normal"))
b.append(text(700, 206, "지식 노하우 지능화", 16.5, INK, "normal"))

# ── 하단 파랑 패널 ──
b.append(f'<rect x="0" y="655" width="{W}" height="{H-655}" fill="{BLUE}"/>')
b.append(text(W/2, 745, "Odoo를 중심으로", 46, INK))
b.append(text(W/2, 860, "AI ERP", 120, YELLOW, spacing="2"))
b.append(text(W/2, 985, "혁 명", 105, INK, spacing="14"))
# 점선
dots = "".join(f'<circle cx="{90+i*14}" cy="1040" r="3" fill="{INK}"/>' for i in range(int((W-180)/14)+1))
b.append(dots)
# 4대 키워드 (2×2)
kw = [("수요예측을 통한 영업 지능화", 255, 1085), ("재고 최적화 및 생산계획 자동화", 630, 1085),
      ("IoT를 이용 설비예지 지능화", 255, 1122), ("기업의 노하우를 지식센터 지능화", 630, 1122)]
for t, x, y in kw:
    b.append(f'<circle cx="{x-170}" cy="{y-6}" r="4" fill="{INK}"/>')
    b.append(text(x, y, t, 21, INK))
b.append(text(W/2, 1200, "에이에스씨", 30, INK))
b.append(f'<rect x="0" y="{H-24}" width="{W}" height="24" fill="{DBLUE}"/>')

doc = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + "".join(b) + "</svg>"
open(os.path.join(OUT, "book_cover_front.svg"), "w").write(doc)
cairosvg.svg2png(url=os.path.join(OUT, "book_cover_front.svg"),
                 write_to=os.path.join(OUT, "book_cover_front.png"), scale=2.2)
print("표지 생성 완료")
