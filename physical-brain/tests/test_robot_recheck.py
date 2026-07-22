"""R09 검증: 지속 재검 — 주기 판정, 하락 감지·경보, GPU 동거 시간대 존중."""
from datetime import datetime, timedelta

from robot_lms import domain, exam, recheck
from server.librarian import answer

T0 = datetime(2026, 7, 10, 10)          # 첫 인증 시점
T1 = datetime(2026, 7, 22, 10)          # 12일 뒤 — 재검 주기(7일) 경과


def _perfect(question: str) -> str:
    for _id, _lv, _sj, q, keys in exam.BANK:
        if q == question:
            return ("모르겠습니다. 존재하지 않는 정보입니다." if keys is None
                    else f"정답은 {keys[0]} 입니다.")
    return "모르겠습니다."


def test_due_only_after_interval(fresh_db):
    domain.create_pack("건강 돌봄", "care")
    assert recheck.due(T1) == {"packs": [], "l1": False}, "응시 이력 없으면 재검 대상 아님"
    domain.self_test(1, lambda q: answer(q, T0), T0)
    exam.run_exam(_perfect, T0, model="fake")
    d = recheck.due(T0 + timedelta(days=1))
    assert d["packs"] == [] and d["l1"] is False, "주기 전에는 조용히"
    d2 = recheck.due(T1)
    assert len(d2["packs"]) == 1 and d2["l1"] is True


def test_recheck_stable_no_alert(fresh_db):
    """지식이 그대로면 재검은 조용히 지나간다 — 이벤트만 남긴다."""
    domain.create_pack("건강 돌봄", "care")
    domain.self_test(1, lambda q: answer(q, T0), T0)
    r = recheck.run_recheck(T1, l2_answer_fn=lambda q: answer(q, T1))
    assert len(r["l2"]) == 1 and r["l2"][0]["dropped"] is False
    assert r["l2"][0]["certified"] is True
    from graph import store
    evs = store.events("나", 30, "로봇재검", T1)
    assert len(evs) == 1 and "⚠" not in evs[0]["payload"]


def test_recheck_detects_drift_and_alerts(fresh_db):
    """성적 하락(파이프라인 고장 등) → 인증 회수 + 경보 알림."""
    domain.create_pack("건강 돌봄", "care")
    domain.self_test(1, lambda q: answer(q, T0), T0)
    assert domain.packs()[0]["certified"] == 1
    r = recheck.run_recheck(T1, l2_answer_fn=lambda q: {"answer": "모르겠습니다.", "evidence": []})
    assert r["l2"][0]["dropped"] is True
    assert domain.packs()[0]["certified"] == 0, "인증은 현재 상태를 따라간다"
    from graph import store
    alerts = [e for e in store.events("나", 30, "알림발송", T1) if "재검 경보" in e["payload"]]
    assert alerts, "하락은 주인에게 알린다"


def test_l1_recheck_respects_gpu_hours(fresh_db):
    """야간(주식 학습 시간대)·LLM 부재 시 L1 재검은 건너뛰고 다음 주기로."""
    exam.run_exam(_perfect, T0, model="fake")
    night = datetime(2026, 7, 22, 21)   # 21시 — 주식 학습 시간대
    r = recheck.run_recheck(night)      # LLM 없음(테스트) + 야간
    assert r["l1"] and "skipped" in r["l1"]
    r2 = recheck.run_recheck(T1, l1_ask_fn=_perfect)  # 주입하면 실행
    assert r2["l1"]["certified"] is True and r2["l1"]["dropped"] is False


def test_auto_if_due_quiet_when_fresh(fresh_db):
    domain.create_pack("건강 돌봄", "care")
    domain.self_test(1, lambda q: answer(q, T1), T1)
    assert recheck.auto_if_due(T1 + timedelta(days=1)) is None, "재검 대상 없으면 None"
