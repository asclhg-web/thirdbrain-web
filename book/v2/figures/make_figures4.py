#!/usr/bin/env python3
"""그림 21-4. 근거 UI 화면 목업 — 설명 가능한 AI"""
from figlib import *

def fig_214():
    W, H = 1000, 780
    b = [text(W/2, 36, "근거 UI 화면 목업 — 판단과 함께 근거를 보여준다", 22, NAVY, "bold"),
         text(W/2, 60, "설명 가능한 AI: 그래프 경로·규칙 체인·데이터 계보가 곧 설명이다", 13, GRAY)]

    # ── 창 프레임 ──
    b.append(rrect(40, 80, W-80, 620, WHITE, NAVY, 2, 12))
    b.append(rrect(40, 80, W-80, 40, NAVY, NAVY, 2, 12))
    b.append(f'<rect x="40" y="100" width="{W-80}" height="20" fill="{NAVY}"/>')
    b.append(text(W/2, 105, "지능형 ERP — 판단 검토 (Human-in-the-Loop)", 14.5, WHITE, "bold"))
    b.append(circle(66, 100, 5, ACC)); b.append(circle(84, 100, 5, "#C8860A")); b.append(circle(102, 100, 5, TEAL))

    # ── 좌: AI 판단 제안 카드 ──
    b.append(rrect(60, 138, 360, 250, ICE, NAVY, 1.6, 10))
    b.append(text(240, 164, "AI 판단 제안", 14, NAVY, "bold"))
    b.append(line(80, 176, 400, 176, ICE2, 1.2))
    b.append(multi(240, 200, ["A사 긴급 수주 5,000개", "조건부 수락 권고", "(납기 +3일 조정안)"], 14, NAVY, 22, w="bold"))
    # 신뢰도 게이지
    b.append(text(120, 286, "종합 확신도", 11.5, GRAY, anchor="start"))
    b.append(rrect(120, 294, 240, 14, LGRAY, GRAY, 1, 7))
    b.append(f'<rect x="120" y="294" width="{240*0.87}" height="14" rx="7" fill="{TEAL}"/>')
    b.append(text(365, 306, "87%", 12, TEAL, "bold"))
    # 버튼
    b.append(rrect(80, 330, 96, 34, TEAL, TEAL, 1.5, 8))
    b.append(text(128, 352, "승인", 13.5, WHITE, "bold"))
    b.append(rrect(192, 330, 96, 34, WHITE, ACC, 1.5, 8))
    b.append(text(240, 352, "반려", 13.5, ACC, "bold"))
    b.append(rrect(304, 330, 96, 34, WHITE, GRAY, 1.5, 8))
    b.append(text(352, 352, "수정", 13.5, GRAY, "bold"))

    # ── 좌 하단: 추론 경로 (그래프) ──
    b.append(rrect(60, 404, 360, 272, WHITE, TEAL, 1.6, 10))
    b.append(text(240, 430, "① 추론 경로 — 지식그래프", 13.5, TEAL, "bold"))
    b.append(line(80, 442, 400, 442, TEALBG, 1.2))
    nodes = [("수주 SO-2031", 140, 478, ICE2), ("품목 브래킷", 320, 478, ICE2),
             ("BOM 레벨2", 140, 548, ICE2), ("CNC 워크센터", 320, 548, "#F5DDD8"),
             ("병목 (부하 96%)", 230, 622, ACC)]
    for t, x, y, c in nodes:
        tc = WHITE if c == ACC else NAVY
        b.append(rrect(x-72, y-20, 144, 40, c, NAVY if c != ACC else ACC, 1.3, 20))
        b.append(text(x, y+5, t, 11.5, tc, "bold"))
    b.append(arrow(212, 478, 246, 478, TEAL, 2, "ahT"))
    b.append(arrow(140, 500, 140, 526, TEAL, 2, "ahT"))
    b.append(arrow(300, 500, 300, 526, TEAL, 2, "ahT"))
    b.append(arrow(160, 570, 200, 600, TEAL, 2, "ahT"))
    b.append(arrow(300, 570, 260, 600, TEAL, 2, "ahT"))
    b.append(text(240, 662, "판단의 원인이 된 노드·관계가 경로로 표시된다", 10.5, GRAY))

    # ── 우: 규칙·제약 검증 (심볼릭) ──
    b.append(rrect(440, 138, 520, 250, WHITE, NAVY, 1.6, 10))
    b.append(text(700, 164, "② 적용된 규칙·제약 — 심볼릭 검증", 13.5, NAVY, "bold"))
    b.append(line(460, 176, 940, 176, ICE2, 1.2))
    rules = [
        ("✓", TEAL, "여신 한도 검증 통과", "규칙 R-021: 미수금+신규수주 ≤ 여신 한도"),
        ("✓", TEAL, "자재 가용성 제약 통과", "SHACL: 필수 자재 3종 재고·입고 예정 충족"),
        ("!", ACC, "표준 납기 규칙 위반 감지", "규칙 R-105: 리드타임 7일 미만 불가 → 대안 생성"),
        ("✓", TEAL, "대안(납기 +3일) 재검증 통과", "전 규칙·제약 충족 — 실행 후보로 승격"),
    ]
    for i, (mark, c, t, sub) in enumerate(rules):
        y = 196 + i*47
        b.append(circle(478, y, 11, c))
        if mark == "✓":
            b.append(f'<path d="M{472},{y} l4,5 l9,-10" stroke="{WHITE}" stroke-width="2.6" fill="none"/>')
        else:
            b.append(text(478, y+5, mark, 13, WHITE, "bold"))
        b.append(text(500, y, t, 12.5, NAVY, "bold", anchor="start"))
        b.append(text(500, y+18, sub, 10.5, GRAY, anchor="start"))

    # ── 우 하단: 데이터 근거·계보 ──
    b.append(rrect(440, 404, 520, 272, WHITE, GRAY, 1.6, 10))
    b.append(text(700, 430, "③ 데이터 근거와 계보(lineage)", 13.5, NAVY, "bold"))
    b.append(line(460, 442, 940, 442, LGRAY, 1.2))
    data = [
        ("수주 이력 24건", "Odoo 판매(SO) · 최근 18개월", "원장"),
        ("CNC 부하율 96%", "frePPLe 유한능력 계획 · 오늘 06:00 산출", "계획"),
        ("유사 사례 3건", "그래프 검색 · 2025.11 긴급수주 대응 이력", "그래프"),
        ("수요예측 모델 v12", "학습 2026.07 · 검증 오차 ±8%", "뉴럴"),
    ]
    for i, (t, src, tag) in enumerate(data):
        y = 458 + i*46
        b.append(rrect(460, y, 372, 38, LGRAY, GRAY, 1, 7))
        b.append(text(474, y+16, t, 12, NAVY, "bold", anchor="start"))
        b.append(text(474, y+31, src, 10, GRAY, anchor="start"))
        b.append(rrect(844, y+4, 96, 30, ICE2, NAVY, 1, 15))
        b.append(text(892, y+23, tag, 11, NAVY, "bold"))
    b.append(text(700, 662, "모든 근거는 클릭하면 원본 레코드로 이동한다", 10.5, GRAY))

    b.append(multi(W/2, 726, [
        "승인·반려·수정의 모든 결정은 근거와 함께 감사 로그에 기록되고, 다음 루프의 학습 데이터가 된다",
        "(화면은 개념 목업 — 3부 21.8절 · 부속 보고서 「의사결정을 위한 Neuro-Symbolic AI」)",
    ], 12, GRAY, 20))
    svg("fig_214_evidence_ui", W, H, "".join(b))

fig_214()
