"""P2-C5 — OllamaBackend 통합 검증(모의 HTTP 서버): 정상·재생성·불통 폴백·게이트."""
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from axp import config  # noqa: E402
from axp.judge import assembler  # noqa: E402

RETRIEVED = {"query_type": "rules",
             "hits": [{"rule_id": "RULE-0001", "confidence": 0.88,
                       "text": "설비 OVEN-2 조합", "dims": {}}]}


class _Mock(BaseHTTPRequestHandler):
    responses: list[str] = []
    calls: int = 0

    def do_POST(self):  # noqa: N802
        n = int(self.headers.get("Content-Length", 0))
        self.rfile.read(n)
        _Mock.calls += 1
        body = _Mock.responses[min(_Mock.calls - 1, len(_Mock.responses) - 1)]
        out = json.dumps({"response": body}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *a):  # 소음 제거
        pass


@pytest.fixture()
def mock_ollama():
    srv = HTTPServer(("127.0.0.1", 0), _Mock)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    _Mock.calls = 0
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


GOOD = "규칙은 설비 OVEN-2 조합입니다. 확신도 88%입니다. [근거: Rule:RULE-0001]"
BAD = "제 생각에는 999999개가 문제입니다."   # 인용 없음 + 위조 수치


def test_ollama_good_answer(mock_ollama):
    _Mock.responses = [GOOD]
    b = assembler.OllamaBackend(url=mock_ollama, model="test")
    out = assembler.set_backend(b) or assembler.answer("규칙?", RETRIEVED)
    assert "RULE-0001" in out and "[근거:" in out
    assembler.set_backend(assembler.DeterministicBackend())


def test_ollama_retry_then_good(mock_ollama):
    _Mock.responses = [BAD, GOOD]
    b = assembler.OllamaBackend(url=mock_ollama, model="test")
    out = b.answer("규칙?", RETRIEVED)
    assert _Mock.calls == 2 and "RULE-0001" in out


# P8-I2(서버1 실측): qwen이 한국어 답 끝에 중국어 부연 줄을 덧붙인 사례 —
# 그 줄은 인용이 없어 차단되고 재생성으로 깨끗한 답이 나와야 한다.
CN = ("OVEN-2 설비 문제입니다 [근거: Rule:RULE-0001].\n"
      "看起來您的要求格式中包含了一些需要調整的地方。")


def test_ollama_chinese_filler_retried(mock_ollama):
    _Mock.responses = [CN, GOOD]
    b = assembler.OllamaBackend(url=mock_ollama, model="test")
    out = b.answer("규칙?", RETRIEVED)
    assert _Mock.calls == 2 and "看" not in out and "RULE-0001" in out


def test_ollama_down_falls_back(tmp_db):
    assembler.set_backend(assembler.OllamaBackend(url="http://127.0.0.1:9", model="t"))
    try:
        out = assembler.answer("규칙?", RETRIEVED)
    finally:
        assembler.set_backend(assembler.DeterministicBackend())
    assert "RULE-0001" in out          # 결정적 조립기가 대신 답했다


def test_gate_blocks_public_host(monkeypatch):
    monkeypatch.setattr(config, "EXPORT_ALLOWED_HOSTS", [])
    with pytest.raises(PermissionError):
        assembler.OllamaBackend(url="http://8.8.8.8:11434", model="t")
