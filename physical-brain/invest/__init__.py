"""투자 팩 (G13) — 주식 온톨로지 그래프: OpenBrain 전략 문서의 코어 이식.

Frame: Company·Sector·MarketEvent + BELONGS_TO·SUPPLIES·IMPACTS.
용도: '왜 움직이는가'의 관계 질의 — 충격전파 경로를 근거와 함께 추적한다.
원칙: 점수와 경로는 시스템이, 매매 판단은 사람이 (투자 조언 아님 — 근거 제시까지).

실전 연결: OpenBrain 수집기(뉴스→LLM 추출)가 record_market_event()를 호출하면 된다.
여기서는 수동/CSV 입력과 시드 가치사슬로 구조를 가동한다.
"""
from datetime import datetime

from graph_core import registry, store

FRAME = "investment-v1"
registry.register_frame(FRAME, ["Company", "Sector", "MarketEvent"], {
    "BELONGS_TO": ("Company", "Sector"),
    "SUPPLIES": ("Company", "Company"),      # 공급자 → 고객
    "IMPACTS": [("MarketEvent", "Company"), ("MarketEvent", "Sector")],
}, version="1.0")

# 반도체 가치사슬 시드 (전략 문서의 예시 — 회사/관계는 공개 상식 수준)
CHAIN = {
    "sectors": ["반도체", "메모리", "AI인프라"],
    "companies": [("삼성전자", "메모리"), ("SK하이닉스", "메모리"), ("마이크론", "메모리"),
                  ("TSMC", "반도체"), ("엔비디아", "AI인프라"), ("한미반도체", "반도체")],
    "supplies": [("SK하이닉스", "엔비디아"), ("삼성전자", "엔비디아"),
                 ("TSMC", "엔비디아"), ("한미반도체", "SK하이닉스")],
}


def _cid(name: str) -> str:
    return f"company:{name}"


def seed_chain() -> dict:
    for s in CHAIN["sectors"]:
        store.upsert_node(f"sector:{s}", "Sector", {"name": s, "source": "seed_chain"})
    for c, s in CHAIN["companies"]:
        store.upsert_node(_cid(c), "Company", {"name": c, "source": "seed_chain"})
        store.upsert_edge(_cid(c), "BELONGS_TO", f"sector:{s}")
    for sup, cust in CHAIN["supplies"]:
        store.upsert_edge(_cid(sup), "SUPPLIES", _cid(cust))
    return store.counts()


def record_market_event(title: str, impacts: list[tuple[str, str, float]],
                        at: datetime | None = None, source: str = "") -> str:
    """시장 이벤트 기록. impacts: [(대상명, '+'|'-', 강도 0~1)]. 근거(source)는 항상 남긴다."""
    at = at or datetime.now()
    eid = f"mevent:{title.replace(' ', '_')}:{at.date().isoformat()}"
    store.upsert_node(eid, "MarketEvent", {"name": title, "at": at.isoformat(), "source": source})
    for target, sign, weight in impacts:
        tid = _cid(target) if store.get_node(_cid(target)) else f"sector:{target}"
        if store.get_node(tid):
            store.upsert_edge(eid, "IMPACTS", tid, {"sign": sign, "weight": float(weight)})
    return eid


def impact_query(event_id: str, decay: float = 0.5) -> list[dict]:
    """충격전파: 이벤트 → 직접 영향 → 공급망 1홉 전파(감쇠). 경로가 곧 근거다."""
    out = []
    ev = store.get_node(event_id)
    if not ev:
        return out
    for _r, target in store.neighbors(event_id, "IMPACTS"):
        e = store.get_edge(event_id, "IMPACTS", target["id"]) or {}
        sign, w = e.get("sign", "+"), float(e.get("weight", 0.5))
        name = target["props"]["name"]
        out.append({"target": name, "score": round(w, 2), "sign": sign,
                    "path": f"{ev['props']['name']} -[IMPACTS{sign}]-> {name}"})
        if target["type"] == "Company":
            # 공급망 전파: 이 회사의 '고객'(하류)에게 절반 강도로
            for _r2, cust in store.neighbors(target["id"], "SUPPLIES"):
                out.append({"target": cust["props"]["name"], "score": round(w * decay, 2),
                            "sign": sign,
                            "path": f"{ev['props']['name']} -[IMPACTS{sign}]-> {name} "
                                    f"-[SUPPLIES]-> {cust['props']['name']}"})
    # 대상별 최대 점수로 합치고 내림차순
    best: dict[str, dict] = {}
    for r in out:
        if r["target"] not in best or r["score"] > best[r["target"]]["score"]:
            best[r["target"]] = r
    return sorted(best.values(), key=lambda r: -r["score"])


def latest_events(days: int = 7, now: datetime | None = None) -> list[dict]:
    from datetime import timedelta
    now = now or datetime.now()
    since = (now - timedelta(days=days)).isoformat()
    evs = [n for n in store.nodes_by_type("MarketEvent")
           if since <= n["props"].get("at", "") <= now.isoformat()]
    return sorted(evs, key=lambda n: n["props"].get("at", ""), reverse=True)[:10]
