#!/usr/bin/env bash
# Neuro-Symbolic AI 보고서 → 워드
set -euo pipefail
export LC_ALL=C.UTF-8 LANG=C.UTF-8
cd "$(dirname "$0")"

OUT="Neuro_Symbolic_AI_의사결정_아키텍처_보고서.docx"
pandoc ns_00_cover.md ns_01_foundations.md ns_02_architecture.md \
  --from markdown+pipe_tables+smart \
  --toc --toc-depth=2 \
  --metadata toc-title="목차" \
  --metadata title="의사결정을 위한 Neuro-Symbolic AI" \
  --metadata author="이형근 · 정인호" \
  --metadata lang=ko-KR \
  -o "$OUT"

python3 - "$OUT" <<'PYEOF'
import sys, zipfile, shutil, re
path = sys.argv[1]; tmp = path + ".tmp"
zin = zipfile.ZipFile(path); zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
FONT = "Malgun Gothic"
for item in zin.namelist():
    data = zin.read(item)
    if item == "word/styles.xml":
        xml = data.decode("utf-8")
        def fix(m):
            attrs = re.sub(r'w:(ascii|hAnsi|cs|eastAsia)="[^"]*"', "", m.group(1))
            attrs = " ".join(attrs.split())
            extra = (f' w:ascii="{FONT}" w:hAnsi="{FONT}" w:eastAsia="{FONT}" w:cs="{FONT}"')
            return f"<w:rFonts {attrs}{extra}/>" if attrs else f"<w:rFonts{extra}/>"
        data = re.sub(r"<w:rFonts\s+([^/>]*)/>", fix, xml).encode("utf-8")
    elif item.startswith("word/theme/") and item.endswith(".xml"):
        xml = data.decode("utf-8")
        xml = re.sub(r'(<a:latin typeface=")[^"]*(")', rf"\g<1>{FONT}\g<2>", xml)
        xml = re.sub(r'(<a:ea typeface=")[^"]*(")', rf"\g<1>{FONT}\g<2>", xml)
        data = xml.encode("utf-8")
    zout.writestr(item, data)
zin.close(); zout.close(); shutil.move(tmp, path)
print("폰트 패치 완료")
PYEOF
echo "빌드 완료: $OUT"
python3 -c "
import zipfile, re
z = zipfile.ZipFile('Neuro_Symbolic_AI_의사결정_아키텍처_보고서.docx')
t = re.sub(r'<[^>]+>', '', z.read('word/document.xml').decode())
print(f'본문: {len(t):,}자 → 추정 {len(t)//1400}페이지')"
