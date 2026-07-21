"""그래프 닥터 (G02) — Frame(스키마)과 Instance(실데이터)의 건강 점검·마이그레이션 도우미.

사용: python -m graph_core.doctor
점검: ① 미등록 유형 노드(과거 Frame 잔재) ② 규약 위반 엣지 ③ 고아 노드율(CTQ)
원칙: 발견만 하고 고치지 않는다 — 수정은 사람이 승인한다(HITL).
"""
import json

from graph_core import registry, store


def check() -> dict:
    conn = store.get_conn()
    known = registry.node_types()
    unknown_nodes = [r["id"] for r in conn.execute(
        "SELECT id, type FROM nodes WHERE archived=0").fetchall() if r["type"] not in known]

    bad_edges = []
    type_of = {r["id"]: r["type"] for r in conn.execute("SELECT id, type FROM nodes").fetchall()}
    for e in conn.execute("SELECT src, rel, dst FROM edges").fetchall():
        st, dt = type_of.get(e["src"]), type_of.get(e["dst"])
        if st and dt and not registry.validate_edge(e["rel"], st, dt):
            bad_edges.append(f"({st})-[{e['rel']}]->({dt}) {e['src']}→{e['dst']}")

    linked = {r["id"] for r in conn.execute(
        "SELECT DISTINCT src AS id FROM edges UNION SELECT DISTINCT dst FROM edges").fetchall()}
    all_nodes = [r["id"] for r in conn.execute("SELECT id FROM nodes WHERE archived=0").fetchall()]
    orphans = [n for n in all_nodes if n not in linked]

    return {
        "frames": registry.frames_info(),
        "unknown_type_nodes": unknown_nodes[:20],
        "invalid_edges": bad_edges[:20],
        "orphan_rate": round(len(orphans) / len(all_nodes) * 100, 1) if all_nodes else 0.0,
        "orphans": orphans[:20],
        "healthy": not unknown_nodes and not bad_edges,
    }


if __name__ == "__main__":
    print(json.dumps(check(), ensure_ascii=False, indent=2))
