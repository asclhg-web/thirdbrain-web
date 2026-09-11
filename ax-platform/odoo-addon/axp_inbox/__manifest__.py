# AX 판단 카드 승인함 — Odoo 화면 내장 (M7-1, P-06)
{
    "name": "AX 판단 카드 승인함",
    "version": "17.0.0.2",
    "category": "Productivity",
    "summary": "AX 플랫폼 판단 카드의 검토·승인/반려 — 담당자가 쓰던 Odoo 화면에서",
    "description": """
판단 카드 = {제안, 수치, 구간, 근거 경로, 대안, 승인자, 상태}.
카드는 AX 플랫폼(axp-api)이 만들고, 이 모듈은 승인함 화면과 권한을 제공한다.
승인 시 플랫폼 API를 호출해 환류(파라미터 기록·감사 로그)가 일어난다 —
Odoo 원장 값 변경은 플랫폼의 감사 로그와 함께만.
""",
    "depends": ["base", "web"],
    "data": [
        "security/axp_security.xml",
        "security/ir.model.access.csv",
        "views/judgment_card_views.xml",
    ],
    "application": True,
    "license": "LGPL-3",
}
