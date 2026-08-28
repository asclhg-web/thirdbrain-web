#!/usr/bin/env python3
"""본문의 모든 마크다운 표를 책 디자인 스타일의 고해상도 그림(PNG)으로 렌더링하고,
원고의 표를 그림 참조로 교체한다. (표의 그림화 — 출판 디자인 품질)"""
import re, os, glob, html
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # book/v2
FIG = os.path.join(BASE, "figures")
NAVY = "#1E2761"; TEAL = "#028090"; ICE = "#E8F0FB"; INK = "#222222"

CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#ffffff; font-family:'NanumGothic'; padding:6px; display:inline-block; }}
table {{ border-collapse:collapse; max-width:980px; }}
th {{ background:{NAVY}; color:#ffffff; font-weight:700; font-size:15px;
     padding:7px 10px; border:1px solid {NAVY}; text-align:center; line-height:1.45; }}
td {{ font-family:'NanumMyeongjo'; font-size:14.5px; color:{INK}; padding:6px 10px;
     border:1px solid #b9c4d8; line-height:1.5; vertical-align:top; }}
tr:nth-child(even) td {{ background:{ICE}; }}
td b, td strong {{ font-family:'NanumGothic'; }}
"""

def md_inline(s):
    s = html.escape(s.strip())
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', s)
    s = s.replace('\\~', '~').replace('\\', '')
    return s

def table_html(block):
    lines = [l for l in block if l.strip().startswith('|')]
    rows = []
    for l in lines:
        if re.match(r'^\s*\|[\s:\-|]+\|\s*$', l):  # 구분선
            continue
        cells = [c for c in l.strip().strip('|').split('|')]
        rows.append([md_inline(c) for c in cells])
    if not rows:
        return None
    head, body = rows[0], rows[1:]
    h = '<tr>' + ''.join(f'<th>{c}</th>' for c in head) + '</tr>'
    b = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in body)
    return f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body><table>{h}{b}</table></body></html>'

def process():
    files = sorted(glob.glob(os.path.join(BASE, 'manuscript/*.md')) +
                   glob.glob(os.path.join(BASE, 'manuscript2/*.md')) +
                   glob.glob(os.path.join(BASE, 'manuscript3/*.md')) +
                   glob.glob(os.path.join(BASE, 'full/*.md')))
    jobs = []  # (png_path, html, md_file, start, end)
    for f in files:
        lines = open(f).read().split('\n')
        i = 0; idx = 0; spans = []
        while i < len(lines):
            if lines[i].strip().startswith('|') and i+1 < len(lines) and re.match(r'^\s*\|[\s:\-|]+\|\s*$', lines[i+1]):
                j = i
                while j < len(lines) and lines[j].strip().startswith('|'):
                    j += 1
                idx += 1
                stem = os.path.splitext(os.path.basename(f))[0]
                png = f'tbl_{stem}_{idx}.png'
                h = table_html(lines[i:j])
                if h:
                    spans.append((i, j, png, h))
                i = j
            else:
                i += 1
        if spans:
            jobs.append((f, lines, spans))

    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--no-sandbox'])
        page = browser.new_page(device_scale_factor=3)
        for f, lines, spans in jobs:
            for (i, j, png, h) in spans:
                page.set_content(h)
                el = page.locator('table')
                el.wait_for()
                path = os.path.join(FIG, png)
                el.screenshot(path=path)
                box = el.bounding_box()
                results[png] = (box['width'], box['height'])
        browser.close()

    # 원고 교체 (뒤에서부터)
    total = 0
    for f, lines, spans in jobs:
        for (i, j, png, h) in reversed(spans):
            w, hh = results[png]
            win = min(4.4, w / 96 * 1.0)           # CSS px → in (96dpi 기준)
            win = min(win, max(2.2, 6.8 * w / hh)) # 페이지 높이 초과 방지
            ref = f'![](figures/{png}){{width={win:.2f}in}}'
            lines[i:j] = [ref]
            total += 1
        open(f, 'w').write('\n'.join(lines))
    print(f'표 {total}개를 그림으로 교체 완료')

process()
