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
                text = h["text"] or confidence.rule_text(h.get("dims", {}))
                lines.append(f"{kind}: {text} (확신도 {conf}) [근거: Rule:{h['rule_key']}]")
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
        elif qt == "memo":
            for h in retrieved["hits"]:
                lines.append(f"{h['date']} 현장 기록: \"{h['memo']}\" [근거: {h['src']} {h['ref']}]")
            if not retrieved["hits"]:
                lines.append("관련 현장 기록이 없습니다. [근거: 메모 검색 0건]")
        return "\n".join(lines)


class OllamaBackend:
    """GPU 서버 어댑터 (P2-C5) — 검색 사실만 컨텍스트로 넣고 인용 형식을 강제.

    접속: AXP_OLLAMA_URL(기본 http://localhost:11434) · AXP_OLLAMA_MODEL.
    보안: 대상 호스트가 사설망(내부 GPU 서버)이 아니면 반출 게이트 허용
    목록에 있어야 한다 — 판단 자료가 게이트 밖으로 나가지 않는다.
    안전: 인용 검증 실패 시 1회 재생성, 그래도 실패·불통이면 호출측이
    결정적 조립기로 폴백한다(파이프라인은 LLM 없이도 완주).
    """

    RETRY_SUFFIX = ("\n\n주의: 직전 응답이 규칙 위반으로 차단되었다. 오직 한국어로만, "
                    "부연·번역·해설 없이, 모든 문장을 '[근거: <참조>]'로 끝내고 "
                    "검색된 사실에 있는 숫자만 사용해 다시 답하라.")

    def __init__(self, url: str | None = None, model: str | None = None):
        import os
        self.url = (url or os.environ.get("AXP_OLLAMA_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.environ.get("AXP_OLLAMA_MODEL", "qwen2.5:14b-instruct")
        self._check_gate()

    def _check_gate(self) -> None:
        import ipaddress
        import socket
        import urllib.parse
        from .. import config
        host = urllib.parse.urlparse(self.url).hostname or "localhost"
        if host in ("localhost",) or host in config.EXPORT_ALLOWED_HOSTS:
            return
        try:
            ip = ipaddress.ip_address(socket.gethostbyname(host))
            if ip.is_private or ip.is_loopback:
                return
        except OSError:
            return  # 해석 불가 — 접속 시점에 실패로 드러난다
        raise PermissionError(
            f"반출 게이트: LLM 호스트 {host}는 사설망도 허용 목록도 아니다")

    # P8-I2(서버1 실측): qwen2.5는 한국어 프롬프트에도 중국어 부연·메타설명을
    # 덧붙이는 경향이 있다 — system으로 한국어만·부연 금지를 강제한다.
    SYSTEM = ("당신은 한국어로만 답합니다. 다른 언어(중국어·영어)나 번역·해설·"
              "메타설명을 절대 넣지 않습니다. 주어진 사실만 근거로 간결히 답하고, "
              "각 문장은 반드시 '[근거: <참조>]' 형식으로 끝냅니다.")

    def _generate(self, prompt: str) -> str:
        import urllib.request
        req = urllib.request.Request(
            f"{self.url}/api/generate",
            json.dumps({"model": self.model, "prompt": prompt, "system": self.SYSTEM,
                        "stream": False, "options": {"temperature": 0.1}}).encode(),
            {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())["response"]

    def answer(self, question: str, retrieved: dict) -> str:
        prompt = (
            "다음 '검색된 사실'만으로 한국어로 답하라. 사실 밖 내용·새 숫자 생성 금지, "
            "부연·번역·해설 금지. 모든 문장은 '[근거: <참조>]'로 끝나야 한다.\n"
            f"질문: {question}\n검색된 사실: {json.dumps(retrieved, ensure_ascii=False)}")
        text = self._generate(prompt)
        for _ in range(2):                       # 최대 2회 재생성 후 폴백에 맡긴다
            try:
                verify_citations(text, retrieved)
                return text
            except CitationError:
                text = self._generate(prompt + self.RETRY_SUFFIX)
        verify_citations(text, retrieved)         # 마지막도 실패면 CitationError→폴백
        return text


class ClaudeBackend:
    """Anthropic Claude 어댑터 (P8-GPU2) — Ollama 대신 클라우드 LLM으로 서술.

    같은 인터페이스(answer)로 OllamaBackend를 대체한다. 한국어 강제·인용 강제·
    수치 생성 금지 원칙은 동일하며, 인용 검증 실패 시 2회 재생성 후 폴백.

    반출 주의(정직 고지): Claude는 외부(api.anthropic.com)이므로 프롬프트에
    담기는 '검색된 사실'(그래프에서 뽑은 근거)이 Anthropic API로 전송된다 —
    사설망 반출 게이트(_check_gate)를 적용하지 않는 유일한 백엔드다. 그래서
    명시적 옵트인(AXP_LLM=claude + ANTHROPIC_API_KEY)일 때만 활성화된다.
    모델은 AXP_CLAUDE_MODEL(기본 claude-opus-5) — 서술은 가벼운 작업이라
    비용을 낮추려면 claude-haiku-4-5로 지정할 수 있다.
    """

    SYSTEM = ("당신은 한국어로만 답합니다. 다른 언어나 번역·해설·메타설명을 넣지 "
              "않습니다. 주어진 '검색된 사실'만 근거로 간결히 답하고, 사실에 없는 "
              "새 숫자를 만들지 않으며, 각 문장은 반드시 '[근거: <참조>]'로 끝냅니다.")

    def __init__(self, model: str | None = None):
        import os
        from anthropic import Anthropic   # 미설치면 make_backend가 폴백 처리
        if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
            raise RuntimeError("ANTHROPIC_API_KEY 미설정 — Claude 백엔드 사용 불가")
        self.model = model or os.environ.get("AXP_CLAUDE_MODEL", "claude-opus-5")
        self.client = Anthropic()

    def _generate(self, prompt: str) -> str:
        kw = dict(model=self.model, max_tokens=2048, system=self.SYSTEM,
                  messages=[{"role": "user", "content": prompt}])
        try:                                           # 서술은 가벼운 작업 → effort low
            msg = self.client.messages.create(output_config={"effort": "low"}, **kw)
        except TypeError:                              # 구 SDK는 output_config 모름 → 생략
            msg = self.client.messages.create(**kw)
        return "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")

    def answer(self, question: str, retrieved: dict) -> str:
        prompt = (
            "다음 '검색된 사실'만으로 한국어로 답하라. 사실 밖 내용·새 숫자 생성 금지, "
            "부연·번역·해설 금지. 모든 문장은 '[근거: <참조>]'로 끝나야 한다.\n"
            f"질문: {question}\n검색된 사실: {json.dumps(retrieved, ensure_ascii=False)}")
        text = self._generate(prompt)
        for _ in range(2):
            try:
                verify_citations(text, retrieved)
                return text
            except CitationError:
                text = self._generate(
                    prompt + "\n\n주의: 직전 응답이 규칙 위반으로 차단되었다. "
                    "오직 한국어로만, 부연 없이, 모든 문장을 '[근거: <참조>]'로 끝내라.")
        verify_citations(text, retrieved)
        return text


def make_backend():
    """환경변수로 백엔드 선택 — AXP_LLM=claude | ollama | deterministic(기본)."""
    import os
    mode = os.environ.get("AXP_LLM", "deterministic").lower()
    if mode == "claude":
        try:
            return ClaudeBackend()
        except Exception as e:  # noqa: BLE001 — 키 없음·SDK 미설치 등: 판단은 계속된다
            print(f"[M6] Claude 백엔드 사용 불가({e}) — 결정적 조립기로 폴백")
    elif mode == "ollama":
        try:
            return OllamaBackend()
        except Exception as e:  # noqa: BLE001 — LLM 불가여도 판단은 계속된다
            print(f"[M6] Ollama 백엔드 사용 불가({e}) — 결정적 조립기로 폴백")
    return DeterministicBackend()


_backend = make_backend()


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
    """조립 + 검증 — LLM 장애 시 결정적 조립기로 폴백, 검증 실패 시 보류."""
    try:
        text = _backend.answer(question, retrieved)
    except Exception as e:  # noqa: BLE001 — GPU 서버 불통 등: 판단은 멈추지 않는다
        if isinstance(_backend, DeterministicBackend):
            raise
        print(f"[M6] LLM 백엔드 장애({e}) — 결정적 조립기 폴백")
        text = DeterministicBackend().answer(question, retrieved)
    try:
        verify_citations(text, retrieved)
    except CitationError as e:
        return f"근거 부족으로 답변을 보류합니다 — {e} [근거: 인용 검증기]"
    return text
