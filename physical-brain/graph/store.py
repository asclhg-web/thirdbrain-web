"""개인 팩 저장소 파사드 (G01 분리 후).

범용 그래프 연산은 graph_core.store가 담당하고, 이 모듈은
① 기존 임포트 경로(from graph import store)의 하위 호환
② 개인 도메인 질의(측정·활동·복약규칙·이벤트·삼각)만 유지한다.
지식 수정의 원본은 볼트(마크다운)이며 그래프는 그 거울이다.
"""
import json
from datetime import datetime, timedelta

from graph import schema  # Frame 등록(personal-v2)을 보장
from graph_core.store import (  # noqa: F401 — 하위 호환 재수출
    archive_node, counts, db_path, get_conn, get_node, init_tables,
    neighbors, nodes_by_type, register_ddl, reset_conn, upsert_edge, upsert_node,
)

# 복약 태스크는 개인 팩의 부속 테이블 — 코어에 DDL 주입
register_ddl(
    """
    CREATE TABLE IF NOT EXISTS tasks(
      id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, person TEXT, med TEXT,
      time TEXT, condition TEXT, caution TEXT,
      status TEXT DEFAULT 'pending', announced_at TEXT, reminded INTEGER DEFAULT 0,
      UNIQUE(date, person, med, time));
    """
)


# ---------- 도메인 질의 (사서·안전망이 사용하는 'Cypher 템플릿'의 SQLite 판) ----------

def person_id(name: str) -> str:
    return f"person:{name}"


def measurements(person: str, mtype: str, days: int = 7, now: datetime | None = None) -> list[dict]:
    now = now or datetime.now()
    since = (now - timedelta(days=days)).isoformat()
    rows = get_conn().execute(
        "SELECT n.props FROM nodes n JOIN edges e ON e.dst=n.id AND e.rel='MEASURED' "
        "WHERE e.src=? AND n.type='Measurement' AND n.archived=0",
        (person_id(person),),
    ).fetchall()
    out = [json.loads(r["props"]) for r in rows]
    out = [m for m in out if m.get("type") == mtype and m.get("measured_at", "") >= since
           and m.get("measured_at", "") <= now.isoformat()]
    return sorted(out, key=lambda m: m["measured_at"])


def activities(person: str, kind: str, days: int = 7, now: datetime | None = None) -> list[dict]:
    now = now or datetime.now()
    since = (now - timedelta(days=days)).isoformat()
    rows = get_conn().execute(
        "SELECT n.props FROM nodes n JOIN edges e ON e.dst=n.id AND e.rel='PERFORMED' "
        "WHERE e.src=? AND n.type='Activity' AND n.archived=0",
        (person_id(person),),
    ).fetchall()
    out = [json.loads(r["props"]) for r in rows]
    return sorted([a for a in out if a.get("kind") == kind and since <= a.get("at", "") <= now.isoformat()],
                  key=lambda a: a["at"])


def regimens_for(person: str) -> list[dict]:
    """사람 -[TAKES]-> 약 -[HAS_RULE]-> 규칙 전개."""
    out = []
    for _, med in neighbors(person_id(person), "TAKES"):
        for _, rule in neighbors(med["id"], "HAS_RULE"):
            out.append({"person": person, "med": med["props"].get("name", med["id"]),
                        "med_id": med["id"], **rule["props"]})
    return sorted(out, key=lambda r: r.get("time", ""))


def events(person: str, days: int = 7, kind: str | None = None, now: datetime | None = None) -> list[dict]:
    now = now or datetime.now()
    since = (now - timedelta(days=days)).isoformat()
    rows = get_conn().execute(
        "SELECT n.props FROM nodes n JOIN edges e ON e.dst=n.id AND e.rel='OCCURRED' "
        "WHERE e.src=? AND n.type='Event' AND n.archived=0",
        (person_id(person),),
    ).fetchall()
    out = [json.loads(r["props"]) for r in rows]
    out = [ev for ev in out if since <= ev.get("at", "") <= now.isoformat()
           and (kind is None or ev.get("kind") == kind)]
    return sorted(out, key=lambda ev: ev["at"])


BODY_KINDS = {"walk", "sleep", "exercise", "운동", "수면", "걷기"}


def triangle_week(person: str, now: datetime | None = None) -> dict:
    """v2 삼각(몸·학습·프로젝트): 최근 7일 활동의 영역별 기여와 교차기여율(일석삼조 비중)."""
    now = now or datetime.now()
    since = (now - timedelta(days=7)).isoformat()
    conn = get_conn()
    rows = conn.execute(
        "SELECT n.id, n.props FROM nodes n JOIN edges e ON e.dst=n.id AND e.rel='PERFORMED' "
        "WHERE e.src=? AND n.type='Activity' AND n.archived=0", (person_id(person),)).fetchall()
    tally = {"몸": 0, "학습": 0, "프로젝트": 0}
    total = multi = 0
    for r in rows:
        pr = json.loads(r["props"])
        at = str(pr.get("at", ""))
        if not (since <= at <= now.isoformat()):
            continue
        total += 1
        domains = set()
        if pr.get("kind") in BODY_KINDS or pr.get("body"):
            domains.add("몸")
        for _rel, n in neighbors(r["id"], "CONTRIBUTES_TO"):
            if n["type"] == "Skill":
                domains.add("학습")
            elif n["type"] == "Project":
                domains.add("프로젝트")
        for d in domains:
            tally[d] += 1
        multi += 1 if len(domains) >= 2 else 0
    return {"total": total, **tally,
            "cross_rate": round(multi / total * 100) if total else None}
