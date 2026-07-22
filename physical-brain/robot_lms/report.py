"""R10 월간 로봇 지능 리포트 — 로봇의 성장 일지.

매달 L1(기반 검정)·L2(분야 인증)·L3(주인그래프 축적)의 상태와 전월 대비 변화를
한 장의 마크다운으로 남긴다. 저장은 두 곳:
① robot_reports 테이블(관리도·전월 비교용 지표)
② 볼트의 '로봇리포트' 폴더(원본은 볼트 — 리포트도 유산의 일부가 된다)

생성은 심장박동이 한다: 매달 초, 지난달 리포트가 없으면 만들고 요약을 알린다.
"""
import json
import os
from datetime import datetime

from graph_core import store
from robot_lms import domain, profile

store.register_ddl(
    """
    CREATE TABLE IF NOT EXISTS robot_reports(
      id INTEGER PRIMARY KEY AUTOINCREMENT, month TEXT UNIQUE NOT NULL,
      created_at TEXT NOT NULL, metrics TEXT NOT NULL, body TEXT NOT NULL);
    """
)

EVENT_KINDS = ["로봇재검", "개념숙달", "과업완료", "마음", "복약완료"]


def _month_of(now: datetime) -> str:
    return now.strftime("%Y-%m")


def _prev_month(month: str) -> str:
    y, m = int(month[:4]), int(month[5:7])
    return f"{y - 1}-12" if m == 1 else f"{y}-{m - 1:02d}"


def _metrics(month: str) -> dict:
    conn = store.get_conn()
    exams = [dict(r) for r in conn.execute(
        "SELECT rate, hallucination, certified FROM robot_exams "
        "WHERE taken_at LIKE ? ORDER BY id", (f"{month}%",)).fetchall()]
    tests = [dict(r) for r in conn.execute(
        "SELECT t.rate, t.certified, p.name FROM robot_pack_tests t "
        "JOIN robot_packs p ON p.id=t.pack_id WHERE t.taken_at LIKE ? ORDER BY t.id",
        (f"{month}%",)).fetchall()]
    ev = {k: 0 for k in EVENT_KINDS}
    for e in store.nodes_by_type("Event"):
        if e["props"].get("at", "").startswith(month) and e["props"].get("kind") in ev:
            ev[e["props"]["kind"]] += 1
    p = profile.robot_profile()
    return {"month": month,
            "l1": {"exams": len(exams),
                   "last_rate": exams[-1]["rate"] if exams else None,
                   "hallucination": sum(e["hallucination"] for e in exams),
                   "certified": p["l1"]["certified"]},
            "l2": {"tests": len(tests), "packs_total": p["l2"]["total"],
                   "packs_certified": p["l2"]["certified"], "open": p["l2"]["open"]},
            "l3": {"nodes": p["l3"]["nodes"], "edges": p["l3"]["edges"],
                   "masters": p["l3"]["masters"]},
            "events": ev}


def _delta(cur: int | None, prev: int | None) -> str:
    if cur is None or prev is None:
        return ""
    d = cur - prev
    return f" ({'+' if d >= 0 else ''}{d})" if d else " (변화 없음)"


def _render(m: dict, prev: dict | None, robot_name: str) -> str:
    p3, q3 = m["l3"], (prev or {}).get("l3", {})
    lines = [
        f"# 로봇 지능 리포트 — {m['month']}",
        "",
        f"로봇: **{robot_name}** · 생성: 자동(심장박동)",
        "",
        "## L1 기반지능",
        (f"- 검정 {m['l1']['exams']}회 · 최근 {m['l1']['last_rate']}% · "
         f"환각 누적 {m['l1']['hallucination']}건 · "
         f"{'✅ 인증 유지' if m['l1']['certified'] else '⏳ 미인증'}"
         if m["l1"]["exams"] else "- 이번 달 검정 응시 없음"
         + (" (인증 유지 중)" if m["l1"]["certified"] else "")),
        "",
        "## L2 분야지능",
        f"- 자기시험 {m['l2']['tests']}회 · 분야팩 {m['l2']['packs_total']}개 중 "
        f"{m['l2']['packs_certified']}개 인증",
        f"- 대화 열린 분야: {', '.join(m['l2']['open']) if m['l2']['open'] else '아직 없음'}",
        "",
        "## L3 주인지능 (브레인그래프)",
        f"- 노드 {p3['nodes']}{_delta(p3['nodes'], q3.get('nodes'))} · "
        f"관계 {p3['edges']}{_delta(p3['edges'], q3.get('edges'))}",
        f"- 몸 {p3['masters']['몸']} · 학습 {p3['masters']['학습']} · "
        f"일 {p3['masters']['일']} · 마음 {p3['masters']['마음']}",
        "",
        "## 이번 달의 사건",
        f"- 재검 {m['events']['로봇재검']}회 · 개념 숙달 {m['events']['개념숙달']}건 · "
        f"과업 완료 {m['events']['과업완료']}건 · 마음 기록 {m['events']['마음']}건 · "
        f"복약 완료 {m['events']['복약완료']}건",
        "",
        "> 이 리포트는 로봇 지능의 성장 일지이며, 볼트에 남는 순간 유산의 일부가 된다.",
        "",
    ]
    return "\n".join(lines)


def build_report(month: str, now: datetime | None = None,
                 vault_dir: str | None = None) -> dict:
    """리포트 생성·저장(멱등: 같은 달은 갱신). 볼트 경로를 주면 md 파일도 남긴다."""
    now = now or datetime.now()
    m = _metrics(month)
    conn = store.get_conn()
    prev_row = conn.execute("SELECT metrics FROM robot_reports WHERE month=?",
                            (_prev_month(month),)).fetchone()
    prev = json.loads(prev_row["metrics"]) if prev_row else None
    body = _render(m, prev, os.environ.get("PB_ROBOT_NAME", "피지컬브레인 1호"))
    conn.execute("INSERT INTO robot_reports(month,created_at,metrics,body) VALUES(?,?,?,?) "
                 "ON CONFLICT(month) DO UPDATE SET created_at=excluded.created_at, "
                 "metrics=excluded.metrics, body=excluded.body",
                 (month, now.isoformat(), json.dumps(m, ensure_ascii=False), body))
    conn.commit()
    path = None
    if vault_dir:
        rdir = os.path.join(vault_dir, "로봇리포트")
        os.makedirs(rdir, exist_ok=True)
        path = os.path.join(rdir, f"로봇지능리포트_{month}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
    return {"month": month, "metrics": m, "body": body, "path": path}


def reports() -> list[dict]:
    return [dict(r) for r in store.get_conn().execute(
        "SELECT month, created_at FROM robot_reports ORDER BY month DESC").fetchall()]


def get_report(month: str) -> dict | None:
    r = store.get_conn().execute("SELECT * FROM robot_reports WHERE month=?",
                                 (month,)).fetchone()
    return dict(r) if r else None


def auto_if_due(now: datetime | None = None, vault_dir: str | None = None) -> dict | None:
    """심장박동용 — 지난달 리포트가 없으면 만들고 요약을 알린다 (있으면 None)."""
    now = now or datetime.now()
    target = _prev_month(_month_of(now))
    if get_report(target):
        return None
    r = build_report(target, now, vault_dir)
    from server import notify
    m = r["metrics"]
    notify.send("나", f"📊 {target} 로봇 지능 리포트가 나왔어요 — "
                      f"L1 {'인증' if m['l1']['certified'] else '미인증'}, "
                      f"분야 {m['l2']['packs_certified']}/{m['l2']['packs_total']} 개방, "
                      f"그래프 노드 {m['l3']['nodes']}. 볼트 '로봇리포트' 폴더를 보세요.",
                "robot", now)
    return r
