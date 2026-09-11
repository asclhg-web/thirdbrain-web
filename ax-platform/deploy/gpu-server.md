# GPU 서버 구성 — 2노드 배치 (앱 서버 + GPU/LLM 서버)

보유 장비 전제: 앱 서버 1대(PG·플랫폼) + GPU 서버 1대(Ollama LLM).
원칙: GPU 서버는 **내부망 전용** — 판단 자료가 게이트 밖으로 나가지 않는다.
OllamaBackend가 사설망이 아닌 호스트를 거부하도록 코드로 강제되어 있다
(judge/assembler.py `_check_gate`).

## 네트워크

```
[현장 태블릿/PC] ── 내부망 ── [앱 서버 :443(Caddy)/:5432(PG,내부만)]
                                   │ 내부망 (11434)
                              [GPU 서버 :11434(Ollama, 내부만)]
```

- GPU 서버 방화벽: 11434 포트를 **앱 서버 IP에만** 허용. 외부 인바운드 전부 차단.
- 앱 서버 → GPU 서버 외에는 어떤 아웃바운드도 불필요.

## GPU 서버 설치 (Ubuntu 기준)

```bash
# 1) NVIDIA 드라이버 + CUDA 확인
nvidia-smi

# 2) Ollama 설치
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable --now ollama
# 내부망 바인딩 (기본 127.0.0.1 → 앱 서버가 접속하도록)
sudo systemctl edit ollama   # → Environment="OLLAMA_HOST=0.0.0.0:11434"
sudo systemctl restart ollama

# 3) 한국어 후보 모델 내려받기 (VRAM 16GB 기준)
ollama pull qwen2.5:14b-instruct     # 1순위 — 한국어·지시 이행 균형
ollama pull exaone3.5:7.8b           # 2순위 — 국산, 가볍고 한국어 자연스러움
ollama pull llama3.1:8b              # 3순위 — 예비
```

## 앱 서버 설정

```bash
# /etc/axp/env (systemd EnvironmentFile 또는 compose env)
AXP_LLM=ollama
AXP_OLLAMA_URL=http://<GPU서버-내부IP>:11434
AXP_OLLAMA_MODEL=qwen2.5:14b-instruct
```

## 모델 선정 절차 (P-03 — 반나절)

같은 회귀 30선(judge/regression.py)을 각 모델로 실행해 표로 비교한다:

| 항목 | 측정 |
|---|---|
| 회귀 30선 통과율 | `AXP_LLM=ollama AXP_OLLAMA_MODEL=<m> python -m axp.judge.regression` |
| 인용 위반→재생성 비율 | 로그의 재생성 횟수 / 총 질의 |
| 응답 시간 p95 | 30선 실행 시간 분포 |
| 한국어 자연스러움 | 브리핑 문장 5건 사람 평가(1~5) |

**선정 기준: 통과율 동률이면 재생성 비율 낮은 쪽, 그다음 속도.**
어떤 모델도 30선 만점이 아니면 결정적 조립기 유지가 기본값이다 —
LLM은 서술 유연성을 더할 뿐, 정확성의 원천은 그래프 검색이다.

## 안전 동작 (코드로 보장)

- GPU 서버 불통 → 결정적 조립기 자동 폴백(파이프라인 무중단)
- 인용 규칙 위반 → 1회 재생성 → 그래도 위반이면 '근거 부족 보류' 응답
- 비사설망 호스트 지정 → PermissionError (반출 게이트)
