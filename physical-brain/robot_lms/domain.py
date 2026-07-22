"""R03+R04 분야지능(L2) — 분야팩 인제스트 + 자기시험 루프.

분야팩 = 로봇이 추가로 공부하는 지식 영역. 지식의 원본은 그래프(볼트의 거울)이고,
팩 빌더가 그래프에서 '검정 문항'을 자동 생성한다 — 그래프가 자라면 시험도 자란다.

자기시험(PTGDA 이식): 로봇(사서 파이프라인 = LLM+그래프)이 문항에 답하고,
① 정답 핵심어 포함 ② 근거 인용 여부를 함께 채점한다.
인증 게이트(제안서 v2 CTQ): 정답률 90% 이상 그리고 근거 인용률 100%.
근거 없는 정답은 통과가 아니다 — 지어낸 정답과 구분할 수 없기 때문이다(헌장 제2원칙).

인증된 분야만 대화가 열린다(open_domains → R05 대화 개방 게이트의 재료).
"""
import re
from datetime import datetime

from graph_core import store

CERT_MIN_RATE = 90        # 분야 인증 정답률 하한 (%)
CERT_EVIDENCE_RATE = 100  # 근거 인용률 — 전 문항 필수

store.register_ddl(
    """
    CREATE TABLE IF NOT EXISTS robot_packs(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL,
      kind TEXT NOT NULL, created_at TEXT NOT NULL,
      certified INTEGER NOT NULL DEFAULT 0,
      last_rate INTEGER, last_evidence_rate INTEGER, last_tested_at TEXT);
    CREATE TABLE IF NOT EXISTS robot_pack_tests(
      id INTEGER PRIMARY KEY AUTOINCREMENT, pack_id INTEGER NOT NULL,
      taken_at TEXT NOT NULL, total INTEGER NOT NULL, passed INTEGER NOT NULL,
      with_evidence INTEGER NOT NULL, rate INTEGER NOT NULL,
      evidence_rate INTEGER NOT NULL, certified INTEGER NOT NULL DEFAULT 0);
    CREATE TABLE IF NOT EXISTS robot_pack_items(
      test_id INTEGER NOT NULL, question TEXT, expect TEXT,
      response TEXT, evidence_n INTEGER, status TEXT);
    """
)

_BUILDERS: dict[str, callable] = {}
KINDS = {"care": "건강 돌봄"}


def register_builder(kind: str, fn) -> None:
    """팩 빌더 등록 — 그래프에서 문항 리스트를 만든다 (어댑터 패턴)."""
    _BUILDERS[kind] = fn


def _norm(s: str) -> str:
    return (s or "").lower().replace(",", "").replace(" ", "")


# ── 건강 돌봄 팩 빌더: 복약 규칙·주의사항·복용자 관계를 문항으로 ──

def _care_items() -> list[dict]:
    from graph import store as gstore
    items = []
    for p in store.nodes_by_type("Person"):
        name = p["props"].get("name", "")
        for r in gstore.regimens_for(name):
            items.append({"question": f"오늘 {name}의 약 일정 알려줘",
                          "expect": f"{r['med']} 포함", "keys": [r["med"]]})
            if r.get("caution"):
                items.append({"question": f"오늘 {name}의 약 일정과 주의사항 알려줘",
                              "expect": r["caution"], "keys": [r["caution"]]})
            # 복용자 관계 (그래프 폴백 경로) — 사서 의도 패턴과 충돌하는
            # 약 이름(혈압·혈당·수면 포함)과 한 글자 인물은 제외
            if len(name) >= 2 and not re.search(r"혈압|혈당|수면|잠|준수", r["med"]):
                items.append({"question": f"{r['med']}은 누가 먹고 있어?",
                              "expect": name, "keys": [name]})
    return items


register_builder("care", _care_items)


# ── 팩 관리 ──

def create_pack(name: str, kind: str = "care", now: datetime | None = None) -> dict:
    """분야팩 등록 (멱등 — 같은 이름이면 기존 팩)."""
    assert kind in _BUILDERS, f"unknown pack kind {kind}"
    now = now or datetime.now()
    conn = store.get_conn()
    conn.execute("INSERT OR IGNORE INTO robot_packs(name,kind,created_at) VALUES(?,?,?)",
                 (name, kind, now.isoformat()))
    conn.commit()
    row = conn.execute("SELECT * FROM robot_packs WHERE name=?", (name,)).fetchone()
    return dict(row)


def packs() -> list[dict]:
    return [dict(r) for r in store.get_conn().execute(
        "SELECT * FROM robot_packs ORDER BY id").fetchall()]


def build_items(pack: dict) -> list[dict]:
    """팩의 현재 문항 — 그래프에서 매번 새로 만든다 (그래프가 자라면 시험도 자란다)."""
    return _BUILDERS[pack["kind"]]()


# ── R04 자기시험 ──

def _unpack(res) -> tuple[str, list]:
    if isinstance(res, dict):
        return str(res.get("answer", "")), list(res.get("evidence") or [])
    return str(res), []


def self_test(pack_id: int, answer_fn, now: datetime | None = None) -> dict:
    """전 문항 응답 → 정답+근거 이중 채점 → 인증 판정·기록."""
    now = now or datetime.now()
    conn = store.get_conn()
    pack = conn.execute("SELECT * FROM robot_packs WHERE id=?", (pack_id,)).fetchone()
    assert pack, f"no pack {pack_id}"
    items = build_items(dict(pack))

    results = []
    for it in items:
        text, evid = _unpack(answer_fn(it["question"]))
        correct = any(_norm(k) in _norm(text) for k in it["keys"])
        status = ("pass" if correct and evid
                  else "no_evidence" if correct else "fail")
        results.append((it, text, len(evid), status))

    total = len(results)
    passed = sum(1 for *_x, s in results if s == "pass")
    with_ev = sum(1 for _i, _t, n, _s in results if n > 0)
    rate = round(passed / total * 100) if total else 0
    ev_rate = round(with_ev / total * 100) if total else 0
    certified = 1 if (total > 0 and rate >= CERT_MIN_RATE
                      and ev_rate >= CERT_EVIDENCE_RATE) else 0

    cur = conn.execute(
        "INSERT INTO robot_pack_tests(pack_id,taken_at,total,passed,with_evidence,"
        "rate,evidence_rate,certified) VALUES(?,?,?,?,?,?,?,?)",
        (pack_id, now.isoformat(), total, passed, with_ev, rate, ev_rate, certified))
    test_id = cur.lastrowid
    for it, text, ev_n, status in results:
        conn.execute(
            "INSERT INTO robot_pack_items(test_id,question,expect,response,evidence_n,status) "
            "VALUES(?,?,?,?,?,?)",
            (test_id, it["question"], it["expect"], text, ev_n, status))
    conn.execute(
        "UPDATE robot_packs SET certified=?, last_rate=?, last_evidence_rate=?, last_tested_at=? "
        "WHERE id=?", (certified, rate, ev_rate, now.isoformat(), pack_id))
    conn.commit()
    return {"test_id": test_id, "pack": pack["name"], "total": total, "passed": passed,
            "rate": rate, "evidence_rate": ev_rate, "certified": bool(certified)}


def latest_test_detail() -> dict | None:
    """가장 최근 자기시험의 문항별 상세 — 성적표 화면용."""
    conn = store.get_conn()
    t = conn.execute("SELECT t.*, p.name AS pack_name FROM robot_pack_tests t "
                     "JOIN robot_packs p ON p.id=t.pack_id "
                     "ORDER BY t.id DESC LIMIT 1").fetchone()
    if not t:
        return None
    items = [dict(r) for r in conn.execute(
        "SELECT * FROM robot_pack_items WHERE test_id=?", (t["id"],)).fetchall()]
    return {**dict(t), "items": items}


def open_domains() -> list[str]:
    """대화가 열린(인증된) 분야 이름들 — R05 대화 개방 게이트의 판정 재료."""
    return [p["name"] for p in packs() if p["certified"]]
