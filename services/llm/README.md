# LLM Gateway (dev)

GPU 서버에서 로컬 Ollama 모델을 OpenAI 호환 API로 노출하는 LiteLLM 게이트웨이 개발 설정입니다.

## 구성

- **Ollama** — 로컬에서 모델 서빙 (외부 노출 안 함, `OLLAMA_HOST` 미변경)
- **LiteLLM** — `:4000`에서 OpenAI 호환 게이트웨이 제공
- 설정: [`litellm-config.dev.yaml`](./litellm-config.dev.yaml)

| 별칭(API의 `model`) | 실제 모델       | 용도   |
| ------------------- | --------------- | ------ |
| `openbrain-llm`     | `qwen2.5:7b`    | 생성   |
| `openbrain-embed`   | `bge-m3`        | 임베딩 |

## 실행 (GPU 서버 PowerShell)

```powershell
# 1) Ollama 모델 준비 + GPU 동작 확인
ollama pull qwen2.5:7b
ollama pull bge-m3
ollama run qwen2.5:7b "재고 부족 알림 한 줄"   # GPU 동작 확인
ollama ps                                       # PROCESSOR=GPU 확인

# 2) LiteLLM 게이트웨이 (네이티브)
pip install "litellm[proxy]"
$env:LITELLM_MASTER_KEY = "<직접 생성한 키>"     # 시크릿: 커밋 금지
$env:OLLAMA_BASE = "http://localhost:11434"
litellm --config services/llm/litellm-config.dev.yaml --port 4000
```

## 검증 (다른 터미널)

```powershell
# 채팅
curl http://localhost:4000/v1/chat/completions `
  -H "Authorization: Bearer $env:LITELLM_MASTER_KEY" `
  -H "Content-Type: application/json" `
  -d '{\"model\":\"openbrain-llm\",\"messages\":[{\"role\":\"user\",\"content\":\"안녕\"}]}'

# 임베딩
curl http://localhost:4000/v1/embeddings `
  -H "Authorization: Bearer $env:LITELLM_MASTER_KEY" `
  -d '{\"model\":\"openbrain-embed\",\"input\":\"이어폰\"}'
```

## 보안 메모

- `LITELLM_MASTER_KEY`는 **환경변수로만** 주입하고 저장소에 커밋하지 않습니다.
- 게이트웨이(`:4000`)와 Ollama(`:11434`)는 외부에 노출하지 않습니다. 원격 접근은 Tailscale 등 사설 네트워크로 제한하세요.
