"""Frame 레지스트리 (G01/G02 기초) — 어떤 노드·관계가 '표준'인지의 단일 출처.

도메인 팩(개인·기업·투자)은 register_frame()으로 자기 온톨로지를 등록한다.
검증은 등록된 모든 Frame의 합집합으로 동작한다 — 팩들이 한 그래프에서 공존하되,
등록되지 않은 유형은 거부된다('스키마 없는 자유 그래프'로의 부패 방지).
"""
_FRAMES: dict[str, dict] = {}
FREE_RELS = {"RELATES_TO"}  # 모든 Frame 공통의 자유 관계


def register_frame(name: str, node_types: list[str], rel_rules: dict) -> None:
    """rel_rules 값은 (src,dst) 튜플 또는 그 리스트."""
    rules: dict[str, list[tuple[str, str]]] = {}
    for rel, rule in rel_rules.items():
        pairs = rule if isinstance(rule, list) else [rule]
        rules[rel] = [tuple(p) for p in pairs]
    _FRAMES[name] = {"node_types": list(node_types), "rel_rules": rules}


def frames() -> list[str]:
    return list(_FRAMES)


def node_types() -> set[str]:
    out: set[str] = set()
    for f in _FRAMES.values():
        out.update(f["node_types"])
    return out


def rel_pairs(rel: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for f in _FRAMES.values():
        out.extend(f["rel_rules"].get(rel, []))
    return out


def validate_edge(rel: str, src_type: str, dst_type: str) -> bool:
    if rel in FREE_RELS:
        return True
    return (src_type, dst_type) in rel_pairs(rel)
