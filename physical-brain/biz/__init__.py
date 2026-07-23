"""기업 팩 (G09) — 에이에스씨 개인사업자: 기업 그래프의 뼈대는 Odoo다.

원칙: 진실의 원본은 Odoo(ERP), 그래프는 거울 — 읽기는 자동, 쓰기(발주)는
반드시 승인 큐(HITL)를 거친다. 돈이 나가는 행동은 사람이 결정한다.

1차 범위(사용자 정의): 교보문고 책 판매대금(매출) + 서버 유지보수·로봇 부품(지출)
→ 일일결산(매출·지출·손익)과 로봇 발주 제안.

Frame enterprise-v1: Partner(거래처)·BizDoc(매출/지출 문서), WITH(문서→거래처).
"""
import env_loader

env_loader.load()

from graph_core import registry  # noqa: E402

FRAME = "enterprise-v1"
registry.register_frame(FRAME, ["Partner", "BizDoc"], {
    "WITH": ("BizDoc", "Partner"),
}, version="1.0")
