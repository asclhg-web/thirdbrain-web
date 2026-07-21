"""그래프 RAG 사서 — 질문 → 의도 분류 → 사전 정의 질의 템플릿 → 근거 기반 답변.

안전 설계: 자유 질의 생성 금지(의도별 템플릿만). 모든 수치는 그래프 조회값.
LLM은 '의도 분류 보조'와 '문장 다듬기'에만 사용 — 없어도 규칙 기반으로 완전 동작.
"""
import re
from datetime import datetime

from graph import store
from graph_core import graphrag
from server import llm
from server.events import adherence


def _measurement_evidence(person: str, mtype: str, items: list[dict], limit: int = 5) -> list[dict]:
    """측정 props → 근거 팩 (id 규약 measurement:{person}:{type}:{at} 재구성)."""
    out = []
    for m in items[-limit:]:
        out.append({"id": f"measurement:{person}:{mtype}:{m['measured_at']}",
                    "type": "Measurement", "label": f"{mtype} {m['value']}{m.get('unit', '')}",
                    "at": m["measured_at"], **({"adapter": m["src"]} if m.get("src") else {})})
    return out

INTENTS = ["bp_trend", "adherence", "meds_today", "gaps", "sleep", "glucose", "hrv", "events"]

_PATTERNS = [
    ("bp_trend", r"혈압"),
    ("adherence", r"준수율|복약.*(률|율|현황)"),
    ("meds_today", r"오늘.*약|약.*(뭐|목록|일정)"),
    ("gaps", r"결측|빠진|누락된?\s*데이터"),
    ("sleep", r"수면|잠"),
    ("glucose", r"혈당|스파이크"),
    ("hrv", r"HRV|심박변이|스트레스"),
    ("events", r"이벤트|기록|무슨 일"),
]
_FORBIDDEN = r"무슨\s*병|진단|병명|약.*(끊|늘려|줄여|바꿔)"


def detect(question: str) -> dict:
    person = "아버지" if "아버지" in question else "나"
    m = re.search(r"(\d+)\s*일", question)
    days = int(m.group(1)) if m else 7
    if re.search(_FORBIDDEN, question):
        return {"intent": "forbidden", "person": person, "days": days}
    for intent, pat in _PATTERNS:
        if re.search(pat, question):
            return {"intent": intent, "person": person, "days": days}
    return {"intent": "unknown", "person": person, "days": days}


def _fmt_avg(vals):
    return round(sum(vals) / len(vals), 1) if vals else None


def answer(question: str, now: datetime | None = None) -> dict:
    now = now or datetime.now()
    q = detect(question)
    person, days = q["person"], q["days"]
    intent = q["intent"]

    if intent == "forbidden":
        text = ("그 판단은 제 영역이 아니에요. 다만 기록은 준비되어 있으니, "
                "진료 시 최근 측정 기록을 의사 선생님께 보여주세요. (기록·알림·준비·보고까지가 제 일입니다)")
        return {"intent": intent, "person": person, "answer": text, "data": {}, "evidence": []}

    data: dict = {}
    evid: list[dict] = []
    if intent == "bp_trend":
        raw = store.measurements(person, "bp_sys", days, now)
        evid = _measurement_evidence(person, "bp_sys", raw)
        sys_v = [m["value"] for m in raw]
        dia_v = [m["value"] for m in store.measurements(person, "bp_dia", days, now)]
        prev_s = [m["value"] for m in store.measurements(person, "bp_sys", days * 2, now)][: len(sys_v) or None]
        data = {"avg_sys": _fmt_avg(sys_v), "avg_dia": _fmt_avg(dia_v), "n": len(sys_v),
                "prev_avg_sys": _fmt_avg(prev_s)}
        if not sys_v:
            fb = f"최근 {days}일 {person}의 혈압 기록이 없어요. 측정을 시작해 볼까요?"
        else:
            fb = (f"최근 {days}일 {person}의 혈압 평균은 {data['avg_sys']}/{data['avg_dia']} mmHg입니다 "
                  f"(측정 {data['n']}회). ")
            if data["avg_sys"] and data["avg_sys"] >= 135:
                fb += "가정혈압 기준(135/85)을 넘고 있어요 — 진료 시 이 기록을 보여주세요."
            else:
                fb += "안정적인 흐름이에요."
    elif intent == "adherence":
        data = adherence(person, days, now)
        fb = (f"최근 {days}일 {person}의 복약 준수율은 "
              f"{data['rate']}% (완료 {data['done']}, 미확인 {data['unconfirmed']}, 누락 {data['missed']})입니다."
              if data["rate"] is not None else f"최근 {days}일 복약 기록이 아직 없어요.")
    elif intent == "meds_today":
        rs = store.regimens_for(person)
        data = {"regimens": rs}
        evid = graphrag.evidence([n for r in rs if (n := store.get_node(r["med_id"]))])
        if rs:
            parts = []
            for r in rs:
                s = f"{r['med']} {r.get('time', '')} ({r.get('condition', '')})"
                if r.get("caution"):
                    s += f" ⚠{r['caution']}"
                parts.append(s)
            fb = f"오늘 {person}의 약: " + " / ".join(parts)
        else:
            fb = f"{person}에게 등록된 복약 규칙이 없어요."
    elif intent == "gaps":
        bp = store.measurements(person, "bp_sys", days, now)
        dates = {m["measured_at"][:10] for m in bp}
        all_days = {(now.date().fromordinal(now.date().toordinal() - i)).isoformat() for i in range(days)}
        gaps = sorted(all_days - dates)
        data = {"gap_days": gaps}
        fb = (f"최근 {days}일 중 혈압 기록이 없는 날: {', '.join(g[5:] for g in gaps)}"
              if gaps else f"최근 {days}일 혈압 기록에 빠진 날이 없어요. 훌륭합니다!")
    elif intent == "sleep":
        raw_a = store.activities(person, "sleep", days, now)
        evid = [{"id": f"activity:{person}:sleep:{a['at']}", "type": "Activity",
                 "label": f"수면 {a['value']}h", "at": a["at"]} for a in raw_a[-5:]]
        sl = [a["value"] for a in raw_a]
        data = {"avg": _fmt_avg(sl), "min": min(sl) if sl else None, "n": len(sl)}
        fb = (f"최근 {days}일 {person}의 평균 수면은 {data['avg']}시간, 최소 {data['min']}시간입니다."
              if sl else "수면 기록이 없어요.")
    elif intent == "glucose":
        raw_g = store.measurements(person, "glucose_spikes", days, now)
        evid = _measurement_evidence(person, "glucose_spikes", raw_g)
        sp = [m["value"] for m in raw_g]
        data = {"total_spikes": int(sum(sp)), "n_days": len(sp)}
        fb = f"최근 {days}일 식후 혈당 스파이크는 총 {data['total_spikes']}회 기록됐어요."
    elif intent == "hrv":
        raw_h = store.measurements(person, "hrv", days, now)
        evid = _measurement_evidence(person, "hrv", raw_h)
        hv = [m["value"] for m in raw_h]
        prev = [m["value"] for m in store.measurements(person, "hrv", days * 2, now)]
        data = {"avg": _fmt_avg(hv), "prev_avg": _fmt_avg(prev)}
        fb = (f"최근 {days}일 HRV 평균은 {data['avg']}ms입니다"
              + (f" ({days*2}일 평균 {data['prev_avg']}ms 대비)." if data["prev_avg"] else ".")
              if hv else "HRV 기록이 없어요.")
    elif intent == "events":
        evs = store.events(person, days, None, now)[-10:]
        data = {"events": evs}
        fb = ("최근 기록: " + " / ".join(f"{e['at'][5:16]} {e['kind']}" for e in evs)
              if evs else "최근 이벤트가 없어요.")
    else:
        # ── G03 GraphRAG 폴백: 의도 템플릿 밖 질문은 그래프 순회로 답한다 ──
        seeds = graphrag.find_nodes(question)
        if seeds:
            sub = graphrag.subgraph([s["id"] for s in seeds], hops=2)
            fact_list = graphrag.facts(sub)
            data = {"seeds": [s["id"] for s in seeds], "facts": fact_list}
            evid = graphrag.evidence(list(sub["nodes"].values()))
            intent = "graph"
            fb = ("그래프에서 찾은 사실입니다: " + " / ".join(fact_list)
                  if fact_list else f"'{graphrag.label(seeds[0])}'은(는) 알고 있지만 연결된 기록이 아직 없어요.")
        else:
            fb = ("질문을 이해하지 못했어요. 혈압·복약·수면·혈당·HRV·결측·이벤트, 또는 "
                  "그래프에 있는 이름(사람·약·장소·스킬·프로젝트)으로 물어보실 수 있어요. "
                  "예: '이번 주 아버지 혈압 어때?'")
            data = {}

    text = llm.compose(llm.LIBRARIAN_SYSTEM,
                       f"다음 사실만 사용해 한국어로 자연스럽게 2~3문장으로 답해줘. 질문: {question} / 사실: {fb}",
                       fallback=fb)
    return {"intent": intent, "person": person, "days": days, "answer": text,
            "data": data, "evidence": evid}
