"""M1-3 장표 태블릿 폼 3종 — 일보·점검·폐기.

현장 어휘 그대로, 타이핑 최소(선택지·숫자). 메모 칸은 지식센터의 원료 —
원문 그대로 보존한다. OCR 보조 플로는 사람 확정 필수(ocr_draft → confirm).
"""
from __future__ import annotations

import json

from .. import common, db
from . import staging

# 폼 필드 설계서 — required, choices(선택지), type
FORM_SPECS: dict[str, dict] = {
    "daily_report": {   # 생산 일보
        "title": "생산 일보",
        "fields": {
            "line_id":      {"type": "choice", "required": True, "label": "라인"},
            "product_id":   {"type": "choice", "required": True, "label": "제품"},
            "shift":        {"type": "choice", "required": True, "label": "근무조",
                             "choices": ["주간", "야간"]},
            "worker_id":    {"type": "choice", "required": True, "label": "작업자"},
            "equipment_id": {"type": "choice", "required": True, "label": "설비"},
            "qty_produced": {"type": "number", "required": True, "label": "생산 수량", "min": 0},
            "qty_defect":   {"type": "number", "required": False, "label": "불량 수량", "min": 0},
            "memo":         {"type": "text",   "required": False, "label": "특이사항(자유 기술)"},
        },
    },
    "inspection": {     # 설비 점검표
        "title": "설비 점검표",
        "fields": {
            "equipment_id": {"type": "choice", "required": True, "label": "설비"},
            "item":         {"type": "choice", "required": True, "label": "점검 항목",
                             "choices": ["온도계 교정", "벨트 장력", "청소 상태", "이음·진동", "윤활"]},
            "result":       {"type": "choice", "required": True, "label": "판정",
                             "choices": ["정상", "주의", "이상"]},
            "value":        {"type": "number", "required": False, "label": "측정값"},
            "memo":         {"type": "text",   "required": False, "label": "소견(자유 기술)"},
        },
    },
    "scrap": {          # 폐기 기록
        "title": "폐기 기록",
        "fields": {
            "line_id":    {"type": "choice", "required": True, "label": "라인/매장"},
            "product_id": {"type": "choice", "required": True, "label": "제품"},
            "qty":        {"type": "number", "required": True, "label": "폐기 수량", "min": 0},
            "reason":     {"type": "choice", "required": True, "label": "사유",
                           "choices": ["유통기한", "파손", "품질 불량", "주문 취소", "기타"]},
            "memo":       {"type": "text", "required": False, "label": "비고(자유 기술)"},
        },
    },
}


class FormError(Exception):
    pass


def validate(form_type: str, payload: dict) -> list[str]:
    spec = FORM_SPECS.get(form_type)
    if spec is None:
        raise FormError(f"알 수 없는 폼: {form_type}")
    errs = []
    for name, f in spec["fields"].items():
        val = payload.get(name)
        if f["required"] and (val is None or str(val).strip() == ""):
            errs.append(f"'{f['label']}'은(는) 필수입니다")
            continue
        if val is None or str(val).strip() == "":
            continue
        if f["type"] == "number":
            try:
                v = float(val)
                if "min" in f and v < f["min"]:
                    errs.append(f"'{f['label']}'은(는) {f['min']} 이상이어야 합니다")
            except (TypeError, ValueError):
                errs.append(f"'{f['label']}'은(는) 숫자여야 합니다 ({val})")
        if f["type"] == "choice" and "choices" in f and val not in f["choices"]:
            errs.append(f"'{f['label']}'의 값 '{val}'이(가) 선택지에 없습니다")
    return errs


def submit(form_type: str, form_date: str, submitted_by: str, line_id: str,
           payload: dict, source: str = "tablet") -> int:
    """폼 제출 — 검증 후 스테이징 적재. 작성자·시각 자동 기입."""
    staging.init()
    errs = validate(form_type, payload)
    if errs:
        raise FormError("; ".join(errs))
    memo = str(payload.get("memo") or "")
    with db.conn() as c:
        cur = c.execute(
            "INSERT INTO staging_forms (form_type, submitted_by, line_id, form_date, "
            "payload, memo, _ingested_at, _source) VALUES (?,?,?,?,?,?,?,?)",
            (form_type, submitted_by, line_id, form_date,
             json.dumps(payload, ensure_ascii=False), memo, common.now_iso(), source),
        )
        return cur.lastrowid


def submit_ocr_draft(form_type: str, form_date: str, line_id: str, payload: dict) -> int:
    """종이 스캔 OCR 초안 — 사람 확정 전에는 스테이징에 들어가지 않는다."""
    db.executescript(
        "CREATE TABLE IF NOT EXISTS ocr_drafts (draft_id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " form_type TEXT, form_date TEXT, line_id TEXT, payload TEXT,"
        " status TEXT DEFAULT 'draft', created_at TEXT)")
    with db.conn() as c:
        cur = c.execute(
            "INSERT INTO ocr_drafts (form_type, form_date, line_id, payload, created_at) "
            "VALUES (?,?,?,?,?)",
            (form_type, form_date, line_id, json.dumps(payload, ensure_ascii=False),
             common.now_iso()),
        )
        return cur.lastrowid


def confirm_ocr(draft_id: int, confirmed_by: str, corrections: dict | None = None) -> int:
    """사람 확정 — 수정값 반영 후 정식 제출로 전환."""
    row = db.one("SELECT * FROM ocr_drafts WHERE draft_id=? AND status='draft'", (draft_id,))
    if row is None:
        raise FormError(f"확정 대기 초안 {draft_id} 없음")
    payload = json.loads(row["payload"])
    payload.update(corrections or {})
    form_id = submit(row["form_type"], row["form_date"], confirmed_by,
                     row["line_id"], payload, source="ocr_confirmed")
    db.execute("UPDATE ocr_drafts SET status='confirmed' WHERE draft_id=?", (draft_id,))
    return form_id
