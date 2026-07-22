"""R10 검증: 월간 로봇 지능 리포트 — 지표 수집, 전월 대비, 볼트 저장, 자동 생성."""
from datetime import datetime

from robot_lms import domain, exam, report
from server.librarian import answer

JUN = datetime(2026, 6, 15, 10)
JUL = datetime(2026, 7, 22, 10)


def _perfect(question: str) -> str:
    for _id, _lv, _sj, q, keys in exam.BANK:
        if q == question:
            return ("모르겠습니다. 존재하지 않는 정보입니다." if keys is None
                    else f"정답은 {keys[0]} 입니다.")
    return "모르겠습니다."


def _train(now):
    exam.run_exam(_perfect, now, model="fake")
    domain.create_pack("건강 돌봄", "care")
    domain.self_test(1, lambda q: answer(q, now), now)


def test_build_report_contains_three_layers(fresh_db, tmp_path):
    _train(JUL)
    r = report.build_report("2026-07", JUL, vault_dir=str(tmp_path))
    assert "L1 기반지능" in r["body"] and "✅ 인증" in r["body"]
    assert "건강 돌봄" in r["body"] and "L3 주인지능" in r["body"]
    assert r["metrics"]["l1"]["hallucination"] == 0
    assert (tmp_path / "로봇리포트" / "로봇지능리포트_2026-07.md").exists(), "볼트에도 남는다(유산)"


def test_month_over_month_delta(fresh_db):
    """전월 리포트가 있으면 그래프 성장(노드 증가)이 표시된다."""
    report.build_report("2026-06", JUN)
    _train(JUL)
    from server.events import record_event
    record_event("나", "과업완료", "7월의 성장", JUL)  # 그래프 노드 증가
    r = report.build_report("2026-07", JUL)
    assert "(+" in r["body"], "전월 대비 증가가 본문에 보인다"
    assert len(report.reports()) == 2


def test_auto_if_due_builds_prev_month_once(fresh_db, tmp_path):
    _train(JUL)
    r = report.auto_if_due(JUL, str(tmp_path))          # 6월 리포트 없음 → 생성
    assert r and r["month"] == "2026-06"
    assert report.auto_if_due(JUL, str(tmp_path)) is None, "이미 있으면 조용히"
    from graph import store
    assert any("로봇 지능 리포트" in e["payload"]
               for e in store.events("나", 60, "알림발송", JUL)), "생성 시 요약 알림"


def test_report_page_renders(fresh_db, tmp_path, monkeypatch):
    monkeypatch.setenv("VAULT_PATH", str(tmp_path))  # 샘플 볼트(저장소 파일) 오염 방지
    from fastapi.testclient import TestClient
    from server.main import app
    c = TestClient(app)
    assert "월간 로봇 지능 리포트" in c.get("/robot/report").text
    c.post("/robot/report/build")
    page = c.get("/robot/report").text
    assert "L1 기반지능" in page
