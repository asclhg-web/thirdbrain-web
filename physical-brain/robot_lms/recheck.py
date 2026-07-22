"""R09 지속 재검 (Drift Check) — 로봇 지능이 '검증된 상태'를 유지하는지 자동 감시.

볼트가 자라고, 모델이 바뀌고, 데이터가 이사해도 인증은 과거의 것이다.
그래서 심장박동이 주기적으로 재검한다 (Control 없는 기능은 미완성 — KG-DMAIC).

- L2 분야팩: 주 1회 자기시험 재응시 (사서 파이프라인 — 오프라인에서도 동작).
  인증 상실 또는 정답률 10%p 이상 하락 → 주인에게 알림 + 이벤트 기록.
- L1 기반 검정: 주 1회, LLM이 살아 있고 주간(06~18시)일 때만 —
  주식 학습(19:00~05:30)과의 GPU 동거 원칙을 지킨다.
  인증 상실 또는 환각 발생 → 알림.
결과는 어느 쪽이든 '로봇재검' 이벤트로 남는다 (관리도 재료).
"""
import os
from datetime import datetime, timedelta

from graph_core import store
from robot_lms import domain, exam

RECHECK_DAYS = 7
DROP_ALERT_PP = 10          # 정답률 하락 경보 문턱 (%p)
L1_HOURS = range(6, 18)     # L1 재검 허용 시간대 (GPU 동거)


def _l1_last_at() -> str | None:
    r = store.get_conn().execute(
        "SELECT taken_at FROM robot_exams ORDER BY id DESC LIMIT 1").fetchone()
    return r["taken_at"] if r else None


def due(now: datetime | None = None) -> dict:
    """재검 대상 — {packs: [pack], l1: bool}. 응시 이력이 없는 것은 재검 대상이 아니다."""
    now = now or datetime.now()
    cutoff = (now - timedelta(days=RECHECK_DAYS)).isoformat()
    packs = [p for p in domain.packs()
             if p["last_tested_at"] and p["last_tested_at"] < cutoff]
    last = _l1_last_at()
    return {"packs": packs, "l1": bool(last and last < cutoff)}


def run_recheck(now: datetime | None = None, l2_answer_fn=None,
                l1_ask_fn=None) -> dict:
    """재검 실행 + 하락 감지 + 알림. 반환: {l2: [...], l1: ...} 보고서."""
    from server import llm, notify
    from server.events import record_event
    now = now or datetime.now()
    d = due(now)
    report: dict = {"l2": [], "l1": None}

    for p in d["packs"]:
        prev_rate, prev_cert = p["last_rate"] or 0, p["certified"]
        if l2_answer_fn is None:
            from server import librarian
            l2_answer_fn = librarian.answer
        r = domain.self_test(p["id"], l2_answer_fn, now)
        dropped = (prev_cert and not r["certified"]) or \
                  (prev_rate - r["rate"] >= DROP_ALERT_PP)
        report["l2"].append({**r, "prev_rate": prev_rate, "dropped": dropped})
        record_event("나", "로봇재검",
                     f"분야 '{p['name']}' {prev_rate}%→{r['rate']}%"
                     f"{' ⚠하락' if dropped else ''}", now)
        if dropped:
            notify.send("나", f"🤖 로봇 재검 경보: '{p['name']}' 분야가 "
                              f"{prev_rate}%→{r['rate']}%로 내려갔어요. "
                              "볼트 지식이 바뀌었거나 파이프라인에 문제가 있을 수 있어요 — "
                              "로봇 화면에서 자기시험 상세를 확인해 주세요.", "robot", now)

    if d["l1"]:
        can_run = (l1_ask_fn is not None) or (llm.available() and now.hour in L1_HOURS)
        if not can_run:
            report["l1"] = {"skipped": "LLM 불가 또는 야간(주식 학습 시간대) — 다음 주기에 재시도"}
        else:
            prev = exam.report_card()["latest"]
            r = exam.run_exam(l1_ask_fn or exam.llm_ask, now,
                              model=os.environ.get("LLM_MODEL", ""))
            dropped = (prev["certified"] and not r["certified"]) or r["hallucination"] > 0
            report["l1"] = {**{k: r[k] for k in ("rate", "hallucination", "certified")},
                            "prev_rate": prev["rate"], "dropped": dropped}
            record_event("나", "로봇재검",
                         f"기반검정 {prev['rate']}%→{r['rate']}% 환각 {r['hallucination']}건"
                         f"{' ⚠하락' if dropped else ''}", now)
            if dropped:
                notify.send("나", f"🤖 로봇 재검 경보: 기반 검정이 {prev['rate']}%→{r['rate']}%"
                                  f"(환각 {r['hallucination']}건)입니다. 모델이 바뀌었는지 확인해 주세요.",
                            "robot", now)
    return report


def auto_if_due(now: datetime | None = None) -> dict | None:
    """심장박동용 — 재검 대상이 있을 때만 돌린다 (없으면 None, 조용히)."""
    now = now or datetime.now()
    d = due(now)
    if not d["packs"] and not d["l1"]:
        return None
    return run_recheck(now)
