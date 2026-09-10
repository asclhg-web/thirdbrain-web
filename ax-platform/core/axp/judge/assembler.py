"""M6-1 GraphRAG 조립기 — 질문 → 그래프 검색 → 검색된 사실만으로 답변.

demo 기본값은 결정적 조립기(DeterministicBackend): 템플릿+그래프 근거 —
"창작이 아니라 조립"의 극단형이며 환각이 구조적으로 불가능하다.
OllamaBackend는 같은 인터페이스의 어댑터: 프롬프트에 검색 사실만 넣고,
출력은 인용 검증기를 통과해야만 반환된다.

인용 규칙: 모든 문장은 '[근거: <참조>]' 태그로 끝난다. 태그 없는 문장 차단.
수치 규칙: 답변의 모든 숫자는 검색 결과에 존재하는 값이어야 한다.
"""
from __future__ import annotations

import json
import re

from .. import db
from ..graph import confidence, evidence, store

CITE_RE = re.compile(r"\[근거: [^\]]+\]\s*$")


class CitationError(Exception):
    pass


# ── 질의 유형별 검색 템플릿 (Cypher 대응 — demo는 SQL/스토어 질의) ─────
def search_cause(entity: str) -> dict:
    """원인 조회 — '<설비/제품/로트>의 불량, 왜?'"""
    hits = []
    for label in ("Equipment", "Product", "Vendor", "Worker", "MaterialLot"):
        n = store.node(store.nid(label, entity))
        if n:
            for e in store.neighbors(n["node_id"], rel="CAUSAL_CANDIDATE") \
                    + store.neighbors(n["node_id"], rel="GOVERNED_BY"):
                rule = store.node(e["other"])
                if rule:
                    hits.append({"kind": rule["props"].get("kind"),
                                 "rule_key": rule["node_id"].split(":", 1)[1],
                                 "text": rule["props"].get("text", ""),
                                 "dims": rule["props"].get("dims", {}),
                                 "confidence": rule["props"].get("confidence")})
    return {"query_type": "cause", "entity": entity, "hits": hits}


def search_history(equipment_id: str) -> dict:
    """이력 조회 — 설비의 정비 이력."""
    n = store.nid("Equipment", equipment_id)
    events = []
    for e in store.neighbors(n, rel="MAINTAINED"):
        m = store.node(e["other"])
        if m:
            events.append(m["props"] | {"ref": m["ledger_ref"]})
    events.sort(key=lambda x: x.get("date", ""))
    return {"query_type": "history", "entity": equipment_id, "hits": events}


def search_rules() -> dict:
    """규칙 조회 — 승격된 Rule 전체."""
    rules = confidence.rules("promoted")
    return {"query_type": "rules",
            "hits": [{"rule_id": r["rule_id"], "dims": r["dims"],
                      "confidence": r["confidence"],
                      "text": confidence.rule_text(r["dims"])} for r in rules]}


def search_numeric(metric: str, dims: dict, start: str, end: str) -> dict:
    """수치 조회 — 원장 집계값(여기서 나온 숫자만 답변에 쓸 수 있다)."""
    if metric == "defect_qty":
        where, params = evidence._dims_filter_sql(dims)
        v = db.scalar(f"SELECT COALESCE(SUM(qty_defect),0) FROM fact_defect "
                      f"WHERE {where} AND date_key BETWEEN ? AND ?",
                      params + [start, end])
        ref = f"fact_defect {start}~{end}"
    elif metric == "sales_qty":
        v = db.scalar("SELECT COALESCE(SUM(qty),0) FROM fact_sales "
                      "WHERE product_id=? AND date_key BETWEEN ? AND ?",
                      (dims.get("product_id"), start, end))
        ref = f"fact_sales {start}~{end}"
    elif metric == "scrap_qty":
        v = db.scalar("SELECT COALESCE(SUM(qty),0) FROM fact_inventory_move "
                      "WHERE move_type='scrap' AND date_key BETWEEN ? AND ?",
                      (start, end))
        ref = f"fact_inventory_move {start}~{end}"
    else:
        raise ValueError(metric)
    return {"query_type": "numeric", "metric": metric, "value": float(v),
            "ref": ref, "hits": [{"metric": metric, "value": float(v), "ref": ref}]}


# ── 백엔드 ───────────────────────────────────────────────────────
class DeterministicBackend:
    """템플릿 조립 — 검색 결과만으로 문장을 만든다."""

    def answer(self, question: str, retrieved: dict) -> str:
        qt = retrieved["query_type"]
        lines: list[str] = []
        if qt == "cause":
            ent = retrieved["entity"]
            if not retrieved["hits"]:
                lines.append(f"{ent} 관련 승격 규칙·원인 후보가 그래프에 없습니다. [근거: kg_nodes 검색 0건]")
            for h in retrieved["hits"]:
                kind = "승격 규칙" if h["kind"] == "rule" else "원인 후보(미승격)"
                conf = f"{h['confidence']:.0%}" if h.get("confidence") else "-"
                lines.append(f"{kind}: {h['text']} (확신도 {conf}) [근거: Rule:{h['rule_key']}]")
        elif qt == "history":
            for h in retrieved["hits"]:
                lines.append(f"{h['date']} {h['type']} — {h.get('note','')} "
                             f"({h['duration_min']:.0f}분) [근거: {h['ref']}]")
            if not retrieved["hits"]:
                lines.append("정비 이력이 없습니다. [근거: MAINTAINED 간선 0건]")
        elif qt == "rules":
            for h in retrieved["hits"]:
                lines.append(f"{h['rule_id']}: {h['text']} (확신도 {h['confidence']:.0%}) "
                             f"[근거: Rule:{h['rule_id']}]")
        elif qt == "numeric":
            lines.append(f"{retrieved['metric']} = {retrieved['value']:.0f} "
                         f"[근거: {retrieved['ref']}]")
        return "\n".join(lines)


class OllamaBackend:
    """prod 어댑터 — 검색 사실만 컨텍스트로 넣고 인용 형식을 강제한다."""

    def __init__(self, url: str = "http://localhost:11434", model: str = "llama3.1"):
        self.url, self.model = url, model

    def answer(self, question: str, retrieved: dict) -> str:
        import urllib.request
        prompt = (
            "다음 '검색된 사실'만으로 질문에 답하라. 사실 밖 내용·새 숫자 생성 금지. "
            "모든 문장은 '[근거: <참조>]'로 끝나야 한다.\n"
            f"질문: {question}\n검색된 사실: {json.dumps(retrieved, ensure_ascii=False)}")
        req = urllib.request.Request(
            f"{self.url}/api/generate",
            json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode(),
            {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())["response"]


_backend = DeterministicBackend()


def set_backend(b) -> None:
    global _backend
    _backend = b


def verify_citations(text: str, retrieved: dict) -> None:
    """인용 검증기 — ① 전 문장 인용 태그 ② 모든 숫자가 검색 결과에 존재."""
    for line in [l for l in text.splitlines() if l.strip()]:
        if not CITE_RE.search(line):
            raise CitationError(f"인용 없는 문장 차단: {line[:60]}")
    raw = {float(a) for a in
           re.findall(r"\d+(?:\.\d+)?", json.dumps(retrieved, ensure_ascii=False))}
    allowed = raw | {round(a * 100, 1) for a in raw if a <= 1.0}   # 백분율 표기 허용
    for num in re.findall(r"\d+(?:\.\d+)?", re.sub(r"\[근거: [^\]]+\]", "", text)):
        if not any(abs(float(num) - a) < 1.0 for a in allowed):
            raise CitationError(f"검색 결과에 없는 수치 차단: {num}")


def answer(question: str, retrieved: dict) -> str:
    """조립 + 검증 — 검증 실패 시 '근거 부족' 응답(재생성은 백엔드 몫)."""
    text = _backend.answer(question, retrieved)
    try:
        verify_citations(text, retrieved)
    except CitationError as e:
        return f"근거 부족으로 답변을 보류합니다 — {e} [근거: 인용 검증기]"
    return text
