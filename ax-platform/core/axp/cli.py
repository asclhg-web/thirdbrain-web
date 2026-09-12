"""스튜어드 CLI — 웹 없이 demo 모드에서 일상 운영을 돌리는 명령줄.

  python -m axp.cli cards [--status proposed]        대기/전체 카드 목록
  python -m axp.cli card <id>                        카드 상세 + 근거
  python -m axp.cli approve <id> --by 이름           승인(환류까지)
  python -m axp.cli reject <id> --by 이름 --reason "수치 의문" [--note ...]
  python -m axp.cli quarantine                       격리 큐 목록
  python -m axp.cli confirm <q_id> <표준코드> --by 이름
  python -m axp.cli briefing <날짜>                  아침 브리핑 출력
  python -m axp.cli quality                          최근 품질 리포트
  python -m axp.cli ask "질문" [--entity OVEN-2]     그래프 질의(인용 강제)
승인 명령은 card_approver 역할로 실행된다 — prod에서는 SSO가 이 역할을 준다.
"""
from __future__ import annotations

import argparse
import json
import sys


def main() -> None:
    ap = argparse.ArgumentParser(prog="axp", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("cards"); s.add_argument("--status", default=None)
    s = sub.add_parser("card"); s.add_argument("id", type=int)
    s = sub.add_parser("approve"); s.add_argument("id", type=int)
    s.add_argument("--by", required=True)
    s = sub.add_parser("reject"); s.add_argument("id", type=int)
    s.add_argument("--by", required=True); s.add_argument("--reason", required=True)
    s.add_argument("--note", default="")
    sub.add_parser("quarantine")
    s = sub.add_parser("confirm"); s.add_argument("q_id", type=int)
    s.add_argument("code"); s.add_argument("--by", required=True)
    s = sub.add_parser("briefing"); s.add_argument("date")
    sub.add_parser("quality")
    s = sub.add_parser("ask"); s.add_argument("question")
    s.add_argument("--entity", default=None)
    s = sub.add_parser("backfill",
                       help="자료 정정 후 재처리 — 표준화 재구축→품질→특징량→그래프 소급")
    s.add_argument("start"); s.add_argument("end")
    s = sub.add_parser("pos", help="POS 판매 자료 반입 (P3-5) — 정산/영수증 파일")
    s.add_argument("adapter", choices=["daily", "receipt"],
                   help="daily: 일별 정산 집계 / receipt: 영수증 단위 거래 로그")
    s.add_argument("file"); s.add_argument("--by", required=True)
    s = sub.add_parser("tenant", help="체험/고객 테넌트 관리 (P4-1)")
    s.add_argument("op", choices=["create", "reset", "destroy", "purge-uploads", "list"])
    s.add_argument("name", nargs="?")
    s.add_argument("--company", default=None)
    s.add_argument("--template", default=None)
    s.add_argument("--hours", type=float, default=24.0)
    s = sub.add_parser("billing", help="과금 — 구독·청구·미납 잠금 (P6-1)")
    s.add_argument("op", choices=["status", "set-plan", "issue", "paid", "unlock", "check"])
    s.add_argument("arg", nargs="?", help="set-plan: 플랜명 / paid: 청구번호 / issue: 기간(YYYY-MM)")
    s.add_argument("--fee", type=int, default=0, help="set-plan: 월 요금(원)")
    s.add_argument("--by", default="cli")
    a = ap.parse_args()

    if a.cmd == "cards":
        from .judge import cards
        rows = cards.listing(status=a.status)
        for r in rows:
            print(f"#{r['card_id']:>3} [{r['status']:9s}] {r['kind']:16s} "
                  f"{r['proposal'][:60]}")
        print(f"— {len(rows)}건")
    elif a.cmd == "card":
        from .judge import cards
        from .graph import evidence
        c = cards.get(a.id)
        print(f"카드 #{a.id} [{c['status']}] {c['kind']} / 승인자: {c['approver']}")
        print("제안:", c["proposal"])
        print("구간:", c["range"])
        print("--- 설명 ---"); print(c["narrative"])
        try:
            ev = evidence.why(c["evidence"])
            print("--- 근거 ---")
            print(evidence.render_path_text(ev) if "path" in ev
                  else json.dumps(ev, ensure_ascii=False, indent=1)[:600])
        except Exception as e:  # noqa: BLE001
            print("근거 조회 실패:", e)
    elif a.cmd == "approve":
        from .agents import inbox
        print(inbox.decide(a.id, a.by, "card_approver", True))
    elif a.cmd == "reject":
        from .agents import inbox
        print(inbox.decide(a.id, a.by, "card_approver", False, a.reason, a.note))
    elif a.cmd == "quarantine":
        from .dataset import codemap
        for q in codemap.pending():
            print(f"#{q['q_id']:>3} [{q['domain']}] '{q['alias']}' ×{q['n_rows']} ({q['context']})")
    elif a.cmd == "confirm":
        from .dataset import codemap
        codemap.confirm(a.q_id, a.code, a.by)
        print(f"확정: #{a.q_id} → {a.code} (사전 갱신 — 같은 별칭은 재발하지 않음)")
    elif a.cmd == "briefing":
        from .studio import briefing
        print(briefing.build(a.date))
    elif a.cmd == "quality":
        from . import db
        r = db.one("SELECT * FROM quality_reports ORDER BY report_date DESC LIMIT 1")
        if not r:
            print("리포트 없음"); return
        print(f"{r['report_date']} — {'통과' if r['ok'] else '위반'} · "
              f"미매핑 {r['unmapped_rate']:.2%}")
    elif a.cmd == "ask":
        from .judge import assembler
        from .studio import knowledge
        q = a.question
        if a.entity:
            print(assembler.answer(q, assembler.search_cause(a.entity)))
        elif "기록" in q or "메모" in q:
            print(assembler.answer(q, knowledge.search_memos(q)))
        elif "규칙" in q:
            print(assembler.answer(q, assembler.search_rules()))
        else:
            print("힌트: --entity <설비/공급사> 로 원인 질의, '규칙'/'기록' 포함 질문 지원")
    elif a.cmd == "backfill":
        # P2: 재처리 정식화 — 격리 확정 취소·원천 정정 뒤 하류를 소급 일치시킨다.
        # 전량 재구축(멱등)이므로 어떤 정정도 이 한 명령으로 반영된다.
        from . import common
        from .dataset import transform, quality, features, validation
        from .graph import loader
        print(f"재처리 {a.start} ~ {a.end}")
        print(" 1/5 표준화 전량 재구축:", transform.run_all())
        quality.daily_report(a.end)
        print(" 2/5 품질 리포트: 발행 완료")
        print(" 3/5 교차 원천 검증:", validation.excel_vs_ledger())
        print(" 4/5 특징량 재계산:", features.materialize(a.end, horizon=7), "행")
        loader.load_dimensions()
        print(" 5/5 그래프 사실 소급:", loader.backfill_defects(a.start, a.end))
        common.alert("info", "backfill",
                     f"재처리 완료 {a.start}~{a.end} — 하류 전 구간 소급 일치")
    elif a.cmd == "pos":
        from pathlib import Path as _P
        from .ingest import pos as _pos
        fn = _pos.ingest_daily if a.adapter == "daily" else _pos.ingest_receipt
        res = fn(_P(a.file), by=a.by)
        if res["status"] == "needs_mapping":
            print("양식을 해석하지 못했습니다 —", res["message"])
            print("발견한 열:", ", ".join(res["columns"]))
        elif res["status"] == "duplicate":
            print(res["message"])
        else:
            print(f"반입 완료: {res['rows_ok']}행 (거절 {res['rows_rejected']}행)")
            for e in res["errors"][:10]:
                print("  거절:", e)
            for w in res["double_count_warnings"]:
                print("  경고:", w)
    elif a.cmd == "tenant":
        import json as _json
        from . import tenant as _t
        if a.op == "list":
            for m in _t.listing():
                print(f"{m['name']:20s} {m['company']:24s} "
                      f"{'체험' if m.get('trial') else '정식'} {m['size_mb']}MB "
                      f"생성 {m['created_at'][:10]}")
            if not _t.listing():
                print("테넌트 없음")
        elif a.op == "create":
            r = _t.create(a.name, company=a.company, template=a.template)
            print(_json.dumps(r, ensure_ascii=False, indent=2))
            print(f"→ 웹앱 기동: AXP_DATA={r['data_dir']} (계정: {r['credentials_file']})")
        elif a.op == "reset":
            print(_json.dumps(_t.reset(a.name), ensure_ascii=False))
        elif a.op == "destroy":
            print(_json.dumps(_t.destroy(a.name), ensure_ascii=False))
        elif a.op == "purge-uploads":
            print(_json.dumps(_t.purge_uploads(a.name, hours=a.hours), ensure_ascii=False))
    elif a.cmd == "billing":
        import json as _json
        from . import billing as _b
        if a.op == "status":
            print(_json.dumps({"subscription": _b.get(), "invoices": _b.invoices()},
                              ensure_ascii=False, indent=2))
        elif a.op == "set-plan":
            print(_json.dumps(_b.set_plan(a.arg or "", a.fee, a.by), ensure_ascii=False))
        elif a.op == "issue":
            print(_json.dumps(_b.issue(a.arg), ensure_ascii=False))
        elif a.op == "paid":
            _b.mark_paid(int(a.arg), a.by); print("수납 처리 완료")
        elif a.op == "unlock":
            _b.unlock(a.by); print("잠금 해제")
        elif a.op == "check":
            print(_json.dumps(_b.check_overdue(), ensure_ascii=False))


if __name__ == "__main__":
    main()
