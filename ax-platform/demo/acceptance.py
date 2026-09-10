"""G4 수용 시험 — 계획서 제7장 6영역 자동 점검. run_e2e 후 실행.

  정합 · 품질 · 모델 · 판단 · 커스터디 · 자립
사람 시연이 필요한 항목은 [현장]으로 표시하고 자동 점검을 대신하지 않는다.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))

from axp import config, db  # noqa: E402


def check(name: str, ok: bool, detail: str) -> dict:
    mark = "✅" if ok else "❌"
    print(f"{mark} {name}: {detail}")
    return {"area": name, "ok": bool(ok), "detail": detail}


def main() -> bool:
    results = []

    # 1. 정합 — Odoo 원장 대비 표준 데이터셋 일 정합 오차 0건(6계열)
    from axp.ingest import odoo_cdc
    r = odoo_cdc.reconcile()
    results.append(check("정합", r["ok"],
                         f"6계열 원장 대조 {'오차 0건' if r['ok'] else '오차 있음'}"))

    # 2. 품질 — 미매핑률 5% 미만, 일일 품질 리포트 자동 발행
    q = db.one("SELECT * FROM quality_reports ORDER BY report_date DESC LIMIT 1")
    ok = q is not None and q["ok"] == 1 and q["unmapped_rate"] < 0.05
    results.append(check("품질", ok,
                         f"게이트 {'통과' if q and q['ok'] else '위반'} · "
                         f"미매핑 {q['unmapped_rate']:.2%} (기준 5%)" if q else "리포트 없음"))

    # 3. 모델 — 합의 기준선 달성 + 모델 카드 완비
    from axp.learn import cards as mcards
    fc = mcards.get_card("demand_forecast")
    ok = (fc is not None
          and fc["metrics"]["wape"] < fc["metrics"]["baseline_ewm_wape"]
          and all(k in fc for k in mcards.REQUIRED))
    results.append(check("모델", ok,
                         f"WAPE {fc['metrics']['wape']:.1%} < 출발선 "
                         f"{fc['metrics']['baseline_ewm_wape']:.1%} · 카드 필수 항목 완비"
                         if fc else "모델 카드 없음"))

    # 4. 판단 — 카드 생성→승인→환류→감사 로그 전 구간 추적
    exec_card = db.one("SELECT * FROM judgment_cards WHERE status='executed' LIMIT 1")
    ok = False
    detail = "실행된 카드 없음"
    if exec_card:
        cid = exec_card["card_id"]
        actions = {a["action"] for a in db.query(
            "SELECT action FROM audit_log WHERE card_id=?", (cid,))}
        param = db.one("SELECT * FROM odoo_params WHERE card_id=?", (cid,))
        ok = "approve" in actions and "feedback" in actions and param is not None
        detail = (f"카드 {cid}: 감사 로그 {sorted(actions)} · "
                  f"파라미터 {param['param_key'] if param else '-'}")
    results.append(check("판단", ok, detail))

    # 5. 커스터디 — 자산 대장 최신 · 반출 로그-승인 일치 · 계약 유효
    from axp.custody import export_gate, contracts, ledger
    rec = export_gate.reconcile()
    n_assets = len(ledger.listing())
    n_contracts = len(contracts.load_all())
    ok = rec["ok"] and n_assets >= 3 and n_contracts >= 7
    results.append(check("커스터디", ok,
                         f"반출 로그-승인 {'일치' if rec['ok'] else '불일치'} · "
                         f"자산 {n_assets}건 · 계약 {n_contracts}건 "
                         f"[현장] 복구 시험은 restore-drill.md 절차로 별도 수행"))

    # 6. 자립 — 스튜어드 단독 수행 가능 항목의 실기록
    conf = db.scalar("SELECT COUNT(*) FROM quarantine_queue WHERE status='confirmed'") or 0
    ocr = db.scalar("SELECT COUNT(*) FROM ocr_drafts WHERE status='confirmed'") or 0
    rules_ok = db.scalar("SELECT COUNT(*) FROM causal_candidates WHERE status='promoted'") or 0
    ok = conf >= 1 and ocr >= 1 and rules_ok >= 1
    results.append(check("자립", ok,
                         f"격리 확정 {conf}건 · OCR 확정 {ocr}건 · Rule 승격 {rules_ok}건 "
                         f"(스튜어드 실기록) [현장] 재학습·백업 복구 단독 수행은 W9에서 검수"))

    n_ok = sum(r["ok"] for r in results)
    print(f"\nG4 수용 시험: {n_ok}/6 영역 통과"
          + ("" if n_ok == 6 else " — 미달 영역 보완 후 재시험"))
    import json
    (config.ARTIFACTS / "acceptance_g4.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return n_ok == 6


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
