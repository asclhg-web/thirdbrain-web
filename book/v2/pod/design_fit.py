#!/usr/bin/env python3
"""목차 글자 축소 + 그림·표 크기 조정으로 빈 공간을 줄이고 총 210쪽에 맞춘다.
사용법: python3 design_fit.py <전역배율> [저장된 개별배율 json]
- 전역배율 g: 모든 드로잉에 곱함 (원본 크기 기준)
- extra.json: {드로잉인덱스: 추가배율} — 빈 공간 유발 그림 개별 축소
결과: design.docx / design.pdf, 빈공간·쪽수 리포트, extra.json 갱신 제안
"""
import zipfile, re, subprocess, sys, os, json
import fitz

SRC = "본문최종신규.docx"
OUT = "design.docx"
H_FOOT = 57      # 하단 마진+쪽번호(pt)
CUSHION = 34     # 그림을 끌어올릴 때 캡션 여유(pt)
MIN_EXTRA = 0.55

g = float(sys.argv[1])
extra = {}
if os.path.exists('extra.json'):
    extra = {int(k): v for k, v in json.load(open('extra.json')).items()}

zin = zipfile.ZipFile(SRC)
doc = zin.read('word/document.xml').decode('utf-8')
sty = zin.read('word/styles.xml').decode('utf-8')

# ── 1) 목차 서식: toc 1 스타일(sz 32) → 21 half-pt(10.5pt), 문단 간격 압축 ──
m = re.search(r'(<w:style [^>]*w:styleId="10".*?</w:style>)', sty, re.S)
blk = m.group(1)
blk2 = re.sub(r'<w:sz w:val="\d+"/>', '<w:sz w:val="21"/>', blk)
blk2 = re.sub(r'<w:szCs w:val="\d+"/>', '<w:szCs w:val="21"/>', blk2)
if '<w:spacing' not in blk2:
    blk2 = blk2.replace('<w:pPr>', '<w:pPr><w:spacing w:before="50" w:after="0" w:line="276" w:lineRule="auto"/>', 1)
sty = sty.replace(blk, blk2)

# 목차 구간의 직접 지정 sz 28 → 21
i0 = doc.find('TOC \\')
last = None
for mm in re.finditer(r'PAGEREF\s+_Toc\d+', doc):
    last = mm
i1 = doc.find('fldCharType="end"', last.end()) + 40
seg = doc[i0:i1]
seg2 = seg.replace('<w:sz w:val="28"/>', '<w:sz w:val="21"/>').replace('<w:szCs w:val="28"/>', '<w:szCs w:val="21"/>')
doc = doc[:i0] + seg2 + doc[i1:]

# ── 2) 드로잉 배율 적용 (원본 EMU × g × extra[idx]) ──
def scale_drawings(xml):
    out, pos, idx = [], 0, 0
    while True:
        s = xml.find('<w:drawing', pos)
        if s < 0:
            out.append(xml[pos:]); break
        e = xml.find('</w:drawing>', s) + len('</w:drawing>')
        out.append(xml[pos:s])
        f = g * extra.get(idx, 1.0)
        block = re.sub(r'(cx|cy)="(\d+)"',
                       lambda m: f'{m.group(1)}="{max(1, int(int(m.group(2))*f))}"',
                       xml[s:e])
        out.append(block)
        idx += 1
        pos = e
    return ''.join(out), idx

doc, ndraw = scale_drawings(doc)

# ── 3) 저장·변환 ──
if os.path.exists(OUT): os.remove(OUT)
zout = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
for item in zin.namelist():
    data = zin.read(item)
    if item == 'word/document.xml': data = doc.encode('utf-8')
    elif item == 'word/styles.xml': data = sty.encode('utf-8')
    zout.writestr(item, data)
zout.close()
subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', OUT],
               check=True, capture_output=True)

# ── 4) 분석: 쪽수, 빈 공간, 다음 쪽 첫 그림의 문서 내 인덱스 ──
d = fitz.open(OUT[:-5] + '.pdf')
H = d[0].rect.height
img_index = []          # 페이지별 (누적 인덱스, bbox) 목록
cum = 0
per_page = []
for p in range(d.page_count):
    infos = d[p].get_image_info()
    infos.sort(key=lambda im: im['bbox'][1])
    lst = [(cum + j, im['bbox']) for j, im in enumerate(infos)]
    cum += len(infos)
    per_page.append(lst)
print(f'전역배율 {g} | 드로잉 {ndraw} | PDF 그림 {cum} | 총 {d.page_count}쪽')

suggest = {}
report = []
for p in range(4, d.page_count - 1):
    pg = d[p]
    blocks = [b for b in pg.get_text('blocks') if b[4].strip() and b[4].strip() != str(p+1)]
    ymax = max([b[3] for b in blocks] + [bb[3] for _, bb in per_page[p]] + [0])
    avail = H - H_FOOT - ymax
    if avail / H <= 0.24:
        continue
    nxt = per_page[p+1]
    ntext = [b for b in d[p+1].get_text('blocks') if b[4].strip() and b[4].strip() != str(p+2)]
    first_text_top = min((b[1] for b in ntext), default=9e9)
    tag = ''
    if nxt and nxt[0][1][1] < min(first_text_top + 5, 120):
        idx, bb = nxt[0]
        h_img = bb[3] - bb[1]
        need = (avail - CUSHION) / h_img
        cur = extra.get(idx, 1.0)
        if need < 1.0 and cur * need >= MIN_EXTRA:
            suggest[idx] = round(cur * need * 0.985, 3)
            tag = f'그림#{idx} h={h_img:.0f} → extra {suggest[idx]}'
        elif need >= 1.0:
            if cur * 0.88 >= MIN_EXTRA:
                suggest[idx] = round(cur * 0.88, 3)
                tag = f'그림#{idx} keep 규칙 → 미세 축소 extra {suggest[idx]}'
            else:
                tag = f'그림#{idx} 이미 공간보다 작음(keep 규칙)'
        else:
            tag = f'그림#{idx} 축소 한계'
    report.append((p+1, round(avail/H*100), tag))

for r in report: print(r)
if '--apply' in sys.argv and suggest:
    extra.update(suggest)
    json.dump({str(k): v for k, v in extra.items()}, open('extra.json', 'w'))
    print('extra.json 갱신:', suggest)
