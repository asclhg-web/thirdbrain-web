#!/usr/bin/env bash
# 원고(markdown) → 워드(docx) 빌드 스크립트
set -euo pipefail
export LC_ALL=C.UTF-8 LANG=C.UTF-8
cd "$(dirname "$0")"

OUT="Odoo_AI_ERP_서드브레인.docx"
FILES=$(ls manuscript/*.md | sort)

# 1) pandoc 변환 (목차 포함)
pandoc $FILES \
  --from markdown+pipe_tables+smart \
  --toc --toc-depth=2 \
  --metadata toc-title="목차" \
  --metadata title="AI ERP 혁명" \
  --metadata author="서드브레인 연구소" \
  --metadata lang=ko-KR \
  -o "$OUT"

# 2) 한글 폰트 패치: 산출물의 styles.xml에서 기본 폰트를 맑은 고딕으로 교체
python3 - "$OUT" <<'EOF'
import sys, zipfile, shutil, re, os

path = sys.argv[1]
tmp = path + ".tmp"
zin = zipfile.ZipFile(path)
zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
FONT = "Malgun Gothic"
for item in zin.namelist():
    data = zin.read(item)
    if item == "word/styles.xml":
        xml = data.decode("utf-8")
        # rFonts 요소의 ascii/hAnsi/cs 값을 교체하고 eastAsia를 지정
        def fix(m):
            attrs = m.group(1)
            attrs = re.sub(r'w:(ascii|hAnsi|cs|eastAsia)="[^"]*"', "", attrs)
            attrs = " ".join(attrs.split())
            extra = (f' w:ascii="{FONT}" w:hAnsi="{FONT}"'
                     f' w:eastAsia="{FONT}" w:cs="{FONT}"')
            return f"<w:rFonts {attrs}{extra}/>" if attrs else f"<w:rFonts{extra}/>"
        xml = re.sub(r"<w:rFonts\s+([^/>]*)/>", fix, xml)
        data = xml.encode("utf-8")
    elif item.startswith("word/theme/") and item.endswith(".xml"):
        # 테마 폰트(제목 스타일이 참조)도 한글 폰트로 교체
        xml = data.decode("utf-8")
        xml = re.sub(r'(<a:latin typeface=")[^"]*(")', rf"\g<1>{FONT}\g<2>", xml)
        xml = re.sub(r'(<a:ea typeface=")[^"]*(")', rf"\g<1>{FONT}\g<2>", xml)
        data = xml.encode("utf-8")
    zout.writestr(item, data)
zin.close(); zout.close()
shutil.move(tmp, path)
print("폰트 패치 완료:", FONT)
EOF

echo "빌드 완료: $OUT"
python3 - <<'EOF'
import zipfile, re
z = zipfile.ZipFile("Odoo_AI_ERP_서드브레인.docx")
xml = z.read("word/document.xml").decode("utf-8")
text = re.sub(r"<[^>]+>", "", xml)
chars = len(text)
print(f"본문 문자 수(태그 제외): {chars:,}")
print(f"추정 페이지 수(1,400자/페이지): {chars//1400}")
EOF
