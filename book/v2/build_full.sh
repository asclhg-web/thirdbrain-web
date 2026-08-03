#!/usr/bin/env bash
# 합본 완전판: 프롤로그 + 1~3부 + 에필로그 → 신국판(152×225mm) 워드
set -euo pipefail
export LC_ALL=C.UTF-8 LANG=C.UTF-8
cd "$(dirname "$0")"

OUT="AI_ERP_혁명_Odoo와_지능형ERP_합본완전판.docx"

# 합본 파일 순서: 통합 표지 → 프롤로그 → 1부 → 2부 → 3부 → 에필로그
# (각 권의 개별 표지 00_cover*.md 는 제외)
FILES="full/00_cover_full.md \
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
manuscript3/22_ch22.md manuscript3/23_ch23.md \
manuscript3/24_epilogue.md"

pandoc $FILES \
  --from markdown+pipe_tables+smart \
  --toc --toc-depth=1 \
  --metadata toc-title="목차" \
  --metadata title="AI ERP 혁명 — Odoo와 지능형 ERP" \
  --metadata author="이형근 · 정인호" \
  --metadata lang=ko-KR \
  -o "$OUT"

# 후처리: 한글 폰트 / 신국판 판형·여백 / 본문 10pt / 쪽번호 푸터
python3 - "$OUT" <<'PYEOF'
import sys, zipfile, shutil, re

path = sys.argv[1]
tmp = path + ".tmp"
zin = zipfile.ZipFile(path)
zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
FONT = "Malgun Gothic"

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

names = zin.namelist()
for item in names:
    data = zin.read(item)
    if item == "word/styles.xml":
        xml = data.decode("utf-8")
        def fix(m):
            attrs = m.group(1)
            attrs = re.sub(r'w:(ascii|hAnsi|cs|eastAsia)="[^"]*"', "", attrs)
            attrs = " ".join(attrs.split())
            extra = (f' w:ascii="{FONT}" w:hAnsi="{FONT}"'
                     f' w:eastAsia="{FONT}" w:cs="{FONT}"')
            return f"<w:rFonts {attrs}{extra}/>" if attrs else f"<w:rFonts{extra}/>"
        xml = re.sub(r"<w:rFonts\s+([^/>]*)/>", fix, xml)
        # 본문 기본 글자 크기 11pt→10pt (docDefaults만)
        xml = xml.replace('<w:sz w:val="22"/>', '<w:sz w:val="20"/>', 1)
        xml = xml.replace('<w:szCs w:val="22"/>', '<w:szCs w:val="20"/>', 1)
        data = xml.encode("utf-8")
    elif item.startswith("word/theme/") and item.endswith(".xml"):
        xml = data.decode("utf-8")
        xml = re.sub(r'(<a:latin typeface=")[^"]*(")', rf"\g<1>{FONT}\g<2>", xml)
        xml = re.sub(r'(<a:ea typeface=")[^"]*(")', rf"\g<1>{FONT}\g<2>", xml)
        data = xml.encode("utf-8")
    elif item == "word/document.xml":
        xml = data.decode("utf-8")
        # pandoc은 빈 <w:sectPr />를 출력 — 신국판 152×225mm(8618×12756 twips),
        # 여백 상하 20mm(1134)·좌우 18mm(1020), 쪽번호 푸터를 담은 sectPr로 통째로 교체
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
print("후처리 완료: 폰트/신국판 판형/본문 10pt/쪽번호")
PYEOF

echo "빌드 완료: $OUT"
python3 - <<'PYEOF'
import zipfile, re
z = zipfile.ZipFile("AI_ERP_혁명_Odoo와_지능형ERP_합본완전판.docx")
xml = z.read("word/document.xml").decode("utf-8")
text = re.sub(r"<[^>]+>", "", xml)
print(f"본문 문자 수(태그 제외): {len(text):,}")
PYEOF
