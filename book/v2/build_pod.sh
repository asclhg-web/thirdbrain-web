#!/usr/bin/env bash
# 교보문고 POD 입고용 본문: 신국판 152×225mm, 본문 나눔명조 / 제목 나눔고딕
set -euo pipefail
export LC_ALL=C.UTF-8 LANG=C.UTF-8
cd "$(dirname "$0")"

OUT="pod/AI_ERP_혁명_POD_본문.docx"
mkdir -p pod

FILES="full/000_frontcover.md \
full/00_cover_full.md \
manuscript/00a_prologue.md \
manuscript/00z_part1.md \
manuscript/01_ch1.md manuscript/02_ch2.md manuscript/03_ch3.md manuscript/04_ch4.md \
manuscript/05_ch5.md manuscript/06_ch6.md manuscript/07_ch7.md \
manuscript2/00z_part2.md \
manuscript2/08_ch8.md manuscript2/09_ch9.md manuscript2/10_ch10.md manuscript2/11_ch11.md \
manuscript2/12_ch12.md manuscript2/13_ch13.md manuscript2/14_ch14.md manuscript2/15_ch15.md \
manuscript2/16_ch16.md manuscript2/17_ch17.md \
manuscript3/00z_part3.md \
manuscript3/18_ch18.md manuscript3/19_ch19.md manuscript3/20_ch20.md manuscript3/21_ch21.md \
manuscript3/24_epilogue.md"

pandoc $FILES \
  --from markdown+pipe_tables+smart \
  --toc --toc-depth=1 \
  --metadata toc-title="목차" \
  --metadata title="AI ERP 혁명 — Odoo와 지능형 ERP" \
  --metadata author="이형근 · 정인호" \
  --metadata lang=ko-KR \
  -o "$OUT"

python3 - "$OUT" <<'PYEOF'
import sys, zipfile, shutil, re

path = sys.argv[1]
tmp = path + ".tmp"
zin = zipfile.ZipFile(path)
zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
BODY = "NanumMyeongjo"   # 본문 명조
HEAD = "NanumGothic"     # 제목 고딕

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
FOOTER_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    f'<w:ftr xmlns:w="{W}" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
    '<w:p><w:pPr><w:jc w:val="center"/><w:rPr><w:sz w:val="18"/></w:rPr></w:pPr>'
    '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
    '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
    '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>'
)

def set_font(chunk, font):
    tag = (f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}"'
           f' w:eastAsia="{font}" w:cs="{font}"/>')
    def fix(m):
        attrs = m.group(1)
        attrs = re.sub(r'w:(ascii|hAnsi|cs|eastAsia)="[^"]*"', "", attrs)
        attrs = " ".join(attrs.split())
        extra = (f' w:ascii="{font}" w:hAnsi="{font}"'
                 f' w:eastAsia="{font}" w:cs="{font}"')
        return f"<w:rFonts {attrs}{extra}/>" if attrs else f"<w:rFonts{extra}/>"
    if "<w:rFonts" in chunk:
        return re.sub(r"<w:rFonts\s+([^/>]*)/>", fix, chunk)
    # rFonts가 없는 스타일: rPr 첫머리에 주입 (rFonts는 rPr의 첫 자식이어야 함)
    if "<w:rPr>" in chunk:
        return chunk.replace("<w:rPr>", "<w:rPr>" + tag, 1)
    if "</w:pPr>" in chunk:
        return chunk.replace("</w:pPr>", f"</w:pPr><w:rPr>{tag}</w:rPr>", 1)
    return chunk

for item in zin.namelist():
    data = zin.read(item)
    if item == "word/styles.xml":
        xml = data.decode("utf-8")
        # 스타일 블록별 폰트: 제목류는 고딕, 나머지는 명조
        parts = re.split(r'(?=<w:style )', xml)
        out = []
        for p in parts:
            m = re.match(r'<w:style [^>]*w:styleId="([^"]+)"', p)
            if m and re.match(r'(Heading\d|Title|Subtitle|TOCHeading|Author|Date)$', m.group(1)):
                out.append(set_font(p, HEAD))
            else:
                out.append(set_font(p, BODY))
        xml = "".join(out)
        # 본문 기본 11pt→10pt (docDefaults만)
        xml = xml.replace('<w:sz w:val="22"/>', '<w:sz w:val="20"/>', 1)
        xml = xml.replace('<w:szCs w:val="22"/>', '<w:szCs w:val="20"/>', 1)
        data = xml.encode("utf-8")
    elif item.startswith("word/theme/") and item.endswith(".xml"):
        xml = data.decode("utf-8")
        xml = re.sub(r'(<a:latin typeface=")[^"]*(")', rf"\g<1>{BODY}\g<2>", xml)
        xml = re.sub(r'(<a:ea typeface=")[^"]*(")', rf"\g<1>{BODY}\g<2>", xml)
        data = xml.encode("utf-8")
    elif item == "word/document.xml":
        xml = data.decode("utf-8")
        # 표지 이미지 문단을 본문 맨 앞으로
        di = xml.find("<w:drawing")
        if di > 0:
            ps = xml.rfind("<w:p>", 0, di)
            bj = xml.find('<w:br w:type="page"/>', di)
            pe = xml.find("</w:p>", bj) + len("</w:p>")
            if 0 < ps < pe:
                seg = xml[ps:pe]
                xml = xml[:ps] + xml[pe:]
                bi = xml.find("<w:body>") + len("<w:body>")
                xml = xml[:bi] + seg + xml[bi:]
        SECT = ('<w:sectPr>'
                '<w:footerReference w:type="default" r:id="rIdFooterPg"/>'
                '<w:pgSz w:w="8618" w:h="12756"/>'
                '<w:pgMar w:top="1134" w:right="1020" w:bottom="1134" '
                'w:left="1020" w:header="720" w:footer="567" w:gutter="0"/>'
                '</w:sectPr>')
        xml = re.sub(r'<w:sectPr\s*/>', SECT, xml)
        data = xml.encode("utf-8")
    elif item == "word/_rels/document.xml.rels":
        xml = data.decode("utf-8")
        xml = xml.replace('</Relationships>',
            '<Relationship Id="rIdFooterPg" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" '
            'Target="footer1.xml"/></Relationships>')
        data = xml.encode("utf-8")
    elif item == "[Content_Types].xml":
        xml = data.decode("utf-8")
        if "footer+xml" not in xml:
            xml = xml.replace('</Types>',
                '<Override PartName="/word/footer1.xml" '
                'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
        data = xml.encode("utf-8")
    zout.writestr(item, data)

zout.writestr("word/footer1.xml", FOOTER_XML)
zin.close(); zout.close()
shutil.move(tmp, path)
print("후처리 완료: 명조 본문/고딕 제목/신국판/쪽번호")
PYEOF

# PDF 변환 (폰트 임베딩)
soffice --headless --convert-to pdf --outdir pod "$OUT" >/dev/null
echo "POD 본문 PDF 완료: pod/AI_ERP_혁명_POD_본문.pdf"
