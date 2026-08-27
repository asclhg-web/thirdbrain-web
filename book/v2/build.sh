#!/usr/bin/env bash
# v2: 프롤로그+1부 → 워드(docx) 빌드
set -euo pipefail
export LC_ALL=C.UTF-8 LANG=C.UTF-8
cd "$(dirname "$0")"

OUT="AI_ERP_혁명_Odoo와_지능형ERP_프롤로그_1부.docx"
FILES=$(ls manuscript/*.md | sort)

pandoc $FILES \
  --from markdown+pipe_tables+smart \
  --toc --toc-depth=2 \
  --metadata toc-title="목차" \
  --metadata title="AI ERP 혁명 — Odoo와 지능형 ERP" \
  --metadata author="이형근 · 정인호 · 송무준" \
  --metadata lang=ko-KR \
  -o "$OUT"

python3 - "$OUT" <<'PYEOF'
import sys, zipfile, shutil, re

path = sys.argv[1]
tmp = path + ".tmp"
zin = zipfile.ZipFile(path)
zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
FONT = "Malgun Gothic"
for item in zin.namelist():
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
        data = xml.encode("utf-8")
    elif item.startswith("word/theme/") and item.endswith(".xml"):
        xml = data.decode("utf-8")
        xml = re.sub(r'(<a:latin typeface=")[^"]*(")', rf"\g<1>{FONT}\g<2>", xml)
        xml = re.sub(r'(<a:ea typeface=")[^"]*(")', rf"\g<1>{FONT}\g<2>", xml)
        data = xml.encode("utf-8")
    zout.writestr(item, data)
zin.close(); zout.close()
shutil.move(tmp, path)
print("폰트 패치 완료:", FONT)
PYEOF

echo "빌드 완료: $OUT"
python3 - <<'PYEOF'
import zipfile, re
z = zipfile.ZipFile("AI_ERP_혁명_Odoo와_지능형ERP_프롤로그_1부.docx")
xml = z.read("word/document.xml").decode("utf-8")
text = re.sub(r"<[^>]+>", "", xml)
print(f"본문 문자 수(태그 제외): {len(text):,}")
print(f"추정 페이지 수(1,400자/페이지): {len(text)//1400}")
PYEOF
