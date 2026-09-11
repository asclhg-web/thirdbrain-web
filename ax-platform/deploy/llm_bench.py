"""P-03 모델 선정 하네스 — GPU 서버의 후보 모델을 회귀 30선으로 비교.

앱 서버에서 실행(데이터 필요):
  AXP_DATA=<데이터경로> AXP_PROFILE=<프로파일> \\
  AXP_OLLAMA_URL=http://<GPU서버>:11434 python3 deploy/llm_bench.py

모델마다: 회귀 30선 통과율 · 인용 위반→재생성 비율 · 응답시간 p50/p95.
선정 기준(gpu-server.md): 통과율 동률이면 재생성 비율 낮은 쪽, 그다음 속도.
어떤 모델도 만점이 아니면 결정적 조립기 유지가 기본값이다.
"""
from __future__ import annotations

import os
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))

MODELS = os.environ.get(
    "AXP_BENCH_MODELS",
    "qwen2.5:14b-instruct,exaone3.5:7.8b,llama3.1:8b").split(",")


def bench_model(model: str) -> dict:
    from axp.judge import assembler, regression
    retries = {"n": 0}
    orig_gen = assembler.OllamaBackend._generate

    def counting_gen(self, prompt):
        if assembler.OllamaBackend.RETRY_SUFFIX in prompt:
            retries["n"] += 1
        return orig_gen(self, prompt)

    assembler.OllamaBackend._generate = counting_gen
    try:
        backend = assembler.OllamaBackend(model=model.strip())
        assembler.set_backend(backend)
        times: list[float] = []
        t0 = time.time()

        orig_answer = assembler.answer

        def timed_answer(q, r):
            s = time.time()
            try:
                return orig_answer(q, r)
            finally:
                times.append(time.time() - s)

        assembler.answer = timed_answer
        try:
            res = regression.run()
        finally:
            assembler.answer = orig_answer
        return {
            "model": model.strip(),
            "pass": f"{res['n_pass']}/{res['n_total']}",
            "retry_rate": round(retries["n"] / max(len(times), 1), 3),
            "p50_s": round(statistics.median(times), 2) if times else None,
            "p95_s": round(sorted(times)[int(len(times) * 0.95) - 1], 2) if times else None,
            "total_s": round(time.time() - t0, 1),
            "fails": [r["id"] for r in res["results"] if not r["pass"]],
        }
    finally:
        assembler.OllamaBackend._generate = orig_gen
        assembler.set_backend(assembler.DeterministicBackend())


def main() -> None:
    print(f"후보 모델: {MODELS}")
    print(f"Ollama: {os.environ.get('AXP_OLLAMA_URL', 'http://localhost:11434')}")
    rows = []
    for m in MODELS:
        print(f"\n── {m.strip()} — 회귀 30선 실행 중…")
        try:
            r = bench_model(m)
        except Exception as e:  # noqa: BLE001
            r = {"model": m.strip(), "pass": f"실패({e})", "retry_rate": "-",
                 "p50_s": "-", "p95_s": "-", "total_s": "-", "fails": []}
        rows.append(r)
        print(f"   통과 {r['pass']} · 재생성률 {r['retry_rate']} · p95 {r['p95_s']}s"
              + (f" · 실패 질의 {r['fails']}" if r["fails"] else ""))
    print("\n| 모델 | 통과 | 재생성률 | p50(s) | p95(s) | 총(s) |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['model']} | {r['pass']} | {r['retry_rate']} "
              f"| {r['p50_s']} | {r['p95_s']} | {r['total_s']} |")
    print("\n기준: 통과율 → 재생성률 → 속도. 만점 모델이 없으면 결정적 조립기 유지.")


if __name__ == "__main__":
    main()
