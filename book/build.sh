#!/usr/bin/env bash
# 원고(markdown) → 워드(docx) 빌드 스크립트
set -euo pipefail
cd "$(dirname "$0")"

OUT="Odoo_AI_ERP_서드브레인.docx"
FILES=$(ls manuscript/*.md | sort)

# 1) 기본 reference doc 생성 후 한글 폰트로 패치
if [ ! -f reference.docx ]; then
  pandoc -o reference.docx --print-default-data-file reference.docx > /dev/null 2>&1 || pandoc -o reference.docx /dev/null
  mkdir -p _ref && (cd _ref && unzip -qo ../reference.docx)
  # 본문/제목 폰트를 한글 폰트로 교체 (맑은 고딕 계열)
  sed -i 's/w:ascii="[^"]*"/w:ascii="Malgun Gothic"/g; s/w:hAnsi="[^"]*"/w:hAnsi="Malgun Gothic"/g; s/w:cs="[^"]*"/w:cs="Malgun Gothic"/g' _ref/word/styles.xml || true
  # eastAsia 폰트 지정 추가
  sed -i 's|<w:rFonts \([^/]*\)/>|<w:rFonts \1 w:eastAsia="Malgun Gothic"/>|g' _ref/word/styles.xml || true
  (cd _ref && rm -f ../reference.docx && zip -qXr ../reference.docx .)
  rm -rf _ref
fi

# 2) pandoc 변환 (목차 포함, 장 시작마다 새 페이지)
pandoc $FILES \
  --from markdown+pipe_tables+smart \
  --reference-doc=reference.docx \
  --toc --toc-depth=2 \
  --metadata title="AI ERP 혁명" \
  --metadata author="서드브레인 연구소" \
  --metadata lang=ko-KR \
  -o "$OUT"

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
