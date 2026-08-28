#!/usr/bin/env python3
"""POD 최종본: 빈 TOC 필드를 실제 쪽번호가 인쇄된 고정 목차로 교체 (2-pass)."""
import zipfile, shutil, re, subprocess, sys, os
import fitz

DOCX = "AI_ERP혁명_POD_본문_최종.docx"
PDF = "AI_ERP혁명_POD_본문_최종.pdf"
RIGHT = 6578  # 본문 폭(twips): 8618 - 1020*2

ENTRIES = [
    ("일러두기", 0),
    ("프롤로그. 왜 지금, 지능형 AI ERP인가 — 3정5S에서 LLM 무한 루프까지", 0),
    ("제1부. 현장에서 플랫폼으로 — 지능형 ERP 컨설팅 방법론", 1),
    ("제1장. ERP 50년과 지능형 ERP: 동기ERP에서 AI ERP까지", 2),
    ("제2장. 컨설팅의 출발: 현장 진단과 3정5S — 데이터 품질의 원점", 2),
    ("제3장. 눈으로 보는 관리에서 데이터로 보는 관리로", 2),
    ("제4장. 부품전개와 일정계획: 제번·추번에서 MRP·APS까지", 2),
    ("제5장. DMAIC 데이터 루프: 수집·학습·추론의 무한 사이클", 2),
    ("제6장. AX 컨설팅 5단계 로드맵: 진단에서 환류까지", 2),
    ("제7장. 공정편성의 재구축과 예측 플랫폼의 완성", 2),
    ("제2부. Odoo 플랫폼과 지능형 ERP의 적용 — 모듈별 경영컨설팅", 1),
    ("제8장. Odoo 플랫폼 총론: 왜 단일 플랫폼인가 — 그리고 컨설팅 구조", 2),
    ("제9장. 웹사이트·이커머스: 고객 접점의 컨설팅", 2),
    ("제10장. CRM·판매: 영업 파이프라인의 컨설팅", 2),
    ("제11장. 매입(구매): 조달의 컨설팅", 2),
    ("제12장. 재고 관리: 물류의 컨설팅", 2),
    ("제13장. 제조 관리: 생산의 컨설팅", 2),
    ("제14장. 회계: 재무의 컨설팅", 2),
    ("제15장. Odoo AI·지식센터: 지능의 내장과 그 너머", 2),
    ("제16장. 확장 부스터: 서드브레인 아키텍처 구축", 2),
    ("제17장. 2부 결산: 모듈 도입 우선순위와 전사 컨설팅 로드맵", 2),
    ("제3부. 온톨로지 메커니즘으로 완성하는 AX — JEDAIX 방법론과 성공사례", 1),
    ("제18장. 경영 사각지대 — ERP가 보지 못하는 곳", 2),
    ("제19장. JEDAIX 온톨로지 — 말이 시스템이 되는 길", 2),
    ("제20장. 실행하는 온톨로지 — Agent Workflow와 Odoo 통합", 2),
    ("제21장. 증명 — 성공사례와 첫 90일", 2),
    ("에필로그. 두 개의 뇌, 하나의 기업", 0),
]

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def toc_xml(pages):
    ps = []
    for (title, kind), pg in zip(ENTRIES, pages):
        bold = "<w:b/>" if kind in (0, 1) else ""
        ind = '<w:ind w:left="240"/>' if kind == 2 else ""
        before = '<w:spacing w:before="120"/>' if kind == 1 else ""
        ps.append(
            '<w:p><w:pPr><w:pStyle w:val="BodyText"/>'
            f'{before}{ind}'
            f'<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="{RIGHT}"/></w:tabs>'
            f'<w:rPr>{bold}</w:rPr></w:pPr>'
            f'<w:r><w:rPr>{bold}</w:rPr><w:t xml:space="preserve">{esc(title)}</w:t></w:r>'
            '<w:r><w:tab/></w:r>'
            f'<w:r><w:rPr>{bold}</w:rPr><w:t>{pg}</w:t></w:r></w:p>'
        )
    return "".join(ps)

FIELD_RE = re.compile(
    r'<w:p><w:r><w:fldChar w:fldCharType="begin"[^>]*/>'
    r'<w:instrText[^>]*>TOC[^<]*</w:instrText>'
    r'<w:fldChar w:fldCharType="separate" ?/>'
    r'(.*?)<w:fldChar w:fldCharType="end" ?/></w:r></w:p>', re.S)
MARK_RE = re.compile(r'<!--TOCSTART-->.*?<!--TOCEND-->', re.S)

def patch(pages):
    tmp = DOCX + ".tmp"
    zin = zipfile.ZipFile(DOCX)
    zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    body = "<!--TOCSTART-->" + toc_xml(pages) + "<!--TOCEND-->"
    for item in zin.namelist():
        data = zin.read(item)
        if item == "word/document.xml":
            xml = data.decode("utf-8")
            if MARK_RE.search(xml):
                xml = MARK_RE.sub(body, xml, count=1)
            else:
                xml, n = FIELD_RE.subn(body, xml, count=1)
                assert n == 1, "TOC 필드를 찾지 못함"
            data = xml.encode("utf-8")
        zout.writestr(item, data)
    zin.close(); zout.close()
    shutil.move(tmp, DOCX)

def convert():
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", ".", DOCX],
                   check=True, capture_output=True)
    src = DOCX[:-5] + ".pdf"
    if src != PDF and os.path.exists(src):
        shutil.move(src, PDF)

def measure():
    d = fitz.open(PDF)
    texts = [d[i].get_text().replace(" ", "").replace("\n", "") for i in range(d.page_count)]
    frags = [t.replace(" ", "")[:14] for t, _ in ENTRIES]
    # 항목 제목이 5개 이상 모여 있는 페이지 = 목차 페이지 → 탐색에서 제외
    toc_pages = {i for i, t in enumerate(texts) if sum(1 for f in frags if f in t) >= 5}
    pages = []
    for frag in frags:
        found = 0
        for i, t in enumerate(texts):
            if i in toc_pages:
                continue
            if frag in t:
                found = i + 1
                break
        pages.append(found)
    return pages, d.page_count

# pass 1: 자리 숫자로 삽입 → 변환 → 실측
patch([0] * len(ENTRIES))
convert()
pages, total = measure()
print("1차 실측:", pages, "총", total)
# pass 2: 실측 쪽번호로 교체 → 재변환 → 재검증
patch(pages)
convert()
pages2, total2 = measure()
print("2차 검증:", pages2, "총", total2)
assert pages == pages2, "쪽번호가 흔들림 — 재조정 필요"
print(f"완료: {PDF} ({total2}쪽)")
