"""책 도해 공용 드로잉 라이브러리 — 모든 그림 생성 스크립트가 import하여 사용.

스타일 규칙(FIGURES_SPEC.md 준수):
- 팔레트: NAVY 지배, TEAL=흐름/진행, ACC(테라코타)=환류·경고·루프 전용, ICE/LGRAY=박스 배경
- 폰트: NanumGothic (시스템 설치됨)
- 캔버스: 폭 900~1000px 권장, svg(name, w, h, body)가 PNG(scale 2.5)까지 생성
- 본문 삽입 시 {width=4.6in} 이므로 글자 최소 크기 11px 이상 유지
"""
import os, math, cairosvg

OUT = os.path.dirname(os.path.abspath(__file__))
F = "NanumGothic"
NAVY = "#1E2761"; ICE = "#E8F0FB"; ICE2 = "#CADCFC"; TEAL = "#028090"
GRAY = "#5A6472"; LGRAY = "#EEF1F5"; ACC = "#B85042"; WHITE = "#FFFFFF"
DARK = "#454C57"; TEALBG = "#E5F4F3"

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
              f'<path d="M0,0 L9,4 L0,8 z" fill="{ACC}"/></marker>'
              f'<marker id="ahG" markerWidth="10" markerHeight="8" refX="8" refY="4" orient="auto">'
              f'<path d="M0,0 L9,4 L0,8 z" fill="{GRAY}"/></marker></defs>')

def arrow(x1, y1, x2, y2, color=NAVY, sw=2, marker="ah", dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{sw}" marker-end="url(#{marker})"{d}/>')

def curve(x1, y1, cx, cy, x2, y2, color=NAVY, sw=2, marker="ah", dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M{x1},{y1} Q{cx},{cy} {x2},{y2}" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" marker-end="url(#{marker})"{d}/>')

def line(x1, y1, x2, y2, color=GRAY, sw=1, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}/>'

def circle(x, y, r, fill, stroke="none", sw=0, opacity=1):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke != "none" else ""
    o = f' fill-opacity="{opacity}"' if opacity != 1 else ""
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"{s}{o}/>'

def chevron(x, y, w, h, fill, tip=18):
    """오른쪽 화살촉형 단계 띠"""
    return (f'<path d="M{x},{y} h{w-tip} l{tip},{h/2} l-{tip},{h/2} h-{w-tip} '
            f'l{tip},-{h/2} z" fill="{fill}"/>')

def svg(name, w, h, body):
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
           f'viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="{WHITE}"/>'
           + ARROW_DEFS + body + "</svg>")
    p = os.path.join(OUT, name + ".svg")
    open(p, "w").write(doc)
    cairosvg.svg2png(url=p, write_to=os.path.join(OUT, name + ".png"), scale=2.5)
    print("생성:", name)
