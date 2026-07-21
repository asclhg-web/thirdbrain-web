"""GraphRAG (G03) — 질문 → 시드 노드 탐색 → N-hop 서브그래프 → 근거 팩.

유산 헌장 제2원칙의 구현: 답은 그래프에 실재하는 것만, 근거는 항상 붙인다.
벡터 검색 없이도 동작한다(이름 기반 시드) — 임베딩은 후순위 강화.
"""
from graph_core import store

# 이름이 의미를 갖는 유형만 시드 후보 (측정·활동·이벤트는 시드가 아니라 근거)
NAMED_TYPES = ("Person", "Medication", "Place", "Skill", "Project")


def find_nodes(question: str, limit: int = 5) -> list[dict]:
    """질문 문장 안에 '이름이 포함된' 노드를 찾는다 — 조사(은/는/이/가)에 강건."""
    conn = store.get_conn()
    q_marks = ",".join("?" * len(NAMED_TYPES))
    rows = conn.execute(
        f"SELECT id FROM nodes WHERE archived=0 AND type IN ({q_marks})", NAMED_TYPES).fetchall()
    hits = []
    for r in rows:
        n = store.get_node(r["id"])
        name = str(n["props"].get("name", ""))
        if len(name) >= 2 and name in question:
            hits.append(n)
    hits.sort(key=lambda n: -len(str(n["props"].get("name", ""))))  # 긴 이름(구체적) 우선
    return hits[:limit]


def subgraph(seed_ids: list[str], hops: int = 2, max_nodes: int = 30) -> dict:
    """시드에서 양방향 N-hop 확장 — {nodes: {id: node}, edges: [(src, rel, dst)]}."""
    nodes: dict[str, dict] = {}
    edges: set[tuple[str, str, str]] = set()
    frontier = list(seed_ids)
    for _ in range(hops):
        nxt = []
        for nid in frontier:
            if nid not in nodes:
                n = store.get_node(nid)
                if not n:
                    continue
                nodes[nid] = n
            if len(nodes) >= max_nodes:
                break
            for rel, other in store.neighbors(nid, None, "out"):
                edges.add((nid, rel, other["id"]))
                if other["id"] not in nodes and len(nodes) < max_nodes:
                    nodes[other["id"]] = other
                    nxt.append(other["id"])
            for rel, other in store.neighbors(nid, None, "in"):
                edges.add((other["id"], rel, nid))
                if other["id"] not in nodes and len(nodes) < max_nodes:
                    nodes[other["id"]] = other
                    nxt.append(other["id"])
        frontier = nxt
        if not frontier:
            break
    return {"nodes": nodes, "edges": sorted(edges)}


def label(node: dict) -> str:
    p = node["props"]
    return str(p.get("name") or p.get("kind") or p.get("type") or node["id"])


def facts(sub: dict, limit: int = 12) -> list[str]:
    """서브그래프의 엣지를 사람이 읽는 사실 문장으로."""
    out = []
    for src, rel, dst in sub["edges"][:limit]:
        s, d = sub["nodes"].get(src), sub["nodes"].get(dst)
        if not (s and d):
            continue
        extra = ""
        if d["type"] == "Regimen":
            extra = f" ({d['props'].get('time', '')} {d['props'].get('condition', '')})".rstrip()
        out.append(f"{label(s)} -[{rel}]-> {label(d)}{extra}")
    return out


def evidence(nodes: list[dict], limit: int = 8) -> list[dict]:
    """근거 팩 — id·유형·라벨·출처(볼트 노트 파일명 등)."""
    out = []
    for n in nodes[:limit]:
        e = {"id": n["id"], "type": n["type"], "label": label(n)}
        if n["props"].get("source"):
            e["source"] = n["props"]["source"]
        if n["props"].get("src"):
            e["adapter"] = n["props"]["src"]
        out.append(e)
    return out
