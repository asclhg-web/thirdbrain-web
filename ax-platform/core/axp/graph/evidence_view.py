"""M5-3 역추적 화면 — 근거 경로를 사람이 읽는 HTML로.

demo: 정적 파일 생성 + API(/cards/{id}/why.html)에서 사용.
경로의 각 층(규칙→조합→사실→원장)이 사다리처럼 내려간다.
"""
from __future__ import annotations

from .. import config
from . import confidence, evidence

CSS = """<style>
body{font-family:'Noto Sans CJK KR',sans-serif;margin:24px;background:#F8F2EA;color:#2E241C;max-width:860px}
h1{color:#6E3A1C;font-size:22px}
.step{background:#fff;border:1px solid #DCCDBB;border-left:6px solid #9C5227;
border-radius:8px;padding:12px 18px;margin:0 0 4px 0}
.step h3{margin:0 0 6px 0;font-size:14px;color:#0E8F86;letter-spacing:1px}
.arrow{margin:2px 0 6px 24px;color:#C07F1E;font-size:18px}
.ref{font-family:monospace;background:#EFE5D8;border-radius:4px;padding:1px 6px;font-size:12px}
table{border-collapse:collapse;margin-top:6px}
td,th{border:1px solid #DCCDBB;padding:4px 10px;font-size:13px}
th{background:#6E3A1C;color:#fff}
small{color:#76675A}</style>"""


def render_rule(rule_key: str) -> str:
    res = evidence.evidence_for_rule(rule_key)
    parts = [f'<!doctype html><meta charset="utf-8"><title>근거 역추적</title>{CSS}',
             f"<h1>왜? — {rule_key} 근거 역추적</h1>"]
    for step in res["path"]:
        if step["step"] == "rule":
            conf = step.get("confidence")
            parts.append(
                f'<div class="step"><h3>① 규칙</h3>{step["text"]}<br>'
                f'<small>확신도 {conf:.0%} · 노드 <span class="ref">{step["node"]}</span></small></div>'
                f'<div class="arrow">↓ 이 규칙은 어떤 조합에서 왔나</div>')
        elif step["step"] == "pattern":
            dims = " × ".join(f"<b>{k}</b>={v}" for k, v in step["dims"].items())
            parts.append(f'<div class="step"><h3>② 조합</h3>{dims}</div>'
                         f'<div class="arrow">↓ 이 조합을 지지하는 사실은</div>')
        elif step["step"] == "facts":
            parts.append(
                f'<div class="step"><h3>③ 사실</h3>불량 이벤트 {step["n_events"]:,}건 · '
                f'불량 {step["qty_defect"]:,.0f}개 ({step["first_seen"]} ~ {step["last_seen"]})</div>'
                f'<div class="arrow">↓ 원장의 실제 기록 표본</div>')
        elif step["step"] == "ledger":
            rows = "".join(
                f"<tr><td><span class=ref>#{s['defect_id']}</span></td>"
                f"<td>{s['mo_ref']}</td><td>{s['date']}</td><td>{s['type']}</td>"
                f"<td>{s['qty']:.0f}</td></tr>" for s in step["samples"])
            parts.append(
                f'<div class="step"><h3>④ 원장</h3>'
                f'<table><tr><th>불량ID</th><th>제조오더</th><th>일자</th><th>유형</th><th>수량</th></tr>'
                f'{rows}</table></div>')
    parts.append(f'<p><small>응답 {res["elapsed_ms"]}ms · 경로에 없는 주장 없음 — '
                 f'이 화면의 모든 층은 원장으로 내려간다</small></p>')
    return "".join(parts)


def save_rule(rule_key: str) -> str:
    out = config.ARTIFACTS / "evidence"
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"why_{rule_key}.html"
    p.write_text(render_rule(rule_key), encoding="utf-8")
    return str(p)


def save_all_rules() -> list[str]:
    return [save_rule(r["rule_id"]) for r in confidence.rules("promoted")]
