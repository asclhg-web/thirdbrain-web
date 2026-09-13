#!/usr/bin/env bash
# AX 플랫폼 — 서버1(WSL)에서 GPU 서버 Ollama에 연결 (P8: GPU 결선 자동화)
# 실행: sudo bash deploy/connect-gpu.sh <GPU서버-IP>    예) sudo bash deploy/connect-gpu.sh 192.168.0.5
# 하는 일: GPU Ollama 도달 확인 → /etc/axp/env에 3줄 반영(멱등) → 서비스 재시작
#          → 판단 백엔드가 실제로 Ollama로 붙었는지 확인
set -euo pipefail

GPU_IP="${1:-}"
PORT="${AXP_OLLAMA_PORT:-11434}"
MODEL="${AXP_OLLAMA_MODEL:-qwen2.5:14b-instruct}"
ENV_FILE=/etc/axp/env

if [ -z "$GPU_IP" ]; then
  echo "!! 사용법: sudo bash deploy/connect-gpu.sh <GPU서버-IP>"
  echo "   예) sudo bash deploy/connect-gpu.sh 192.168.0.5"
  exit 1
fi
URL="http://${GPU_IP}:${PORT}"

echo "== 1/4 GPU Ollama 도달 확인 ($URL)"
if ! curl -fsS --max-time 8 "$URL/api/tags" >/tmp/axp_ollama_tags.json 2>/dev/null; then
  echo "!! $URL 에 닿지 못했습니다. 점검:"
  echo "   - GPU 서버에서 gpu-ollama-setup.ps1 을 실행했고 트레이 Ollama를 Quit→재실행했는가"
  echo "   - GPU 서버 방화벽 11434 인바운드가 열렸는가(스크립트가 규칙 생성)"
  echo "   - 두 PC가 같은 사내망인가(ping ${GPU_IP})"
  exit 1
fi
if grep -q "$MODEL" /tmp/axp_ollama_tags.json; then
  echo "   도달 OK · 모델 $MODEL 확인됨"
else
  echo "   도달 OK — 다만 응답에 $MODEL 이 안 보입니다(GPU에서 'ollama pull $MODEL' 확인). 계속 진행."
fi

echo "== 2/4 /etc/axp/env에 연결 3줄 반영(멱등)"
[ -f "$ENV_FILE" ] || { echo "!! $ENV_FILE 없음 — 먼저 install-app-server.sh를 실행하세요"; exit 1; }
# 기존 줄이 주석이든 값이든 정확한 값으로 정렬(없으면 추가)
set_kv() {  # key value
  local k="$1" v="$2"
  if grep -qE "^#?${k}=" "$ENV_FILE"; then
    sed -i "s|^#\?${k}=.*|${k}=${v}|" "$ENV_FILE"
  else
    echo "${k}=${v}" >> "$ENV_FILE"
  fi
}
set_kv AXP_LLM ollama
set_kv AXP_OLLAMA_URL "$URL"
set_kv AXP_OLLAMA_MODEL "$MODEL"
echo "   반영: AXP_LLM=ollama · AXP_OLLAMA_URL=$URL · AXP_OLLAMA_MODEL=$MODEL"

echo "== 3/4 서비스 재시작(웹·스케줄러)"
systemctl restart axp-web axp-scheduler
sleep 3

echo "== 4/4 판단 백엔드 실측 — 정말 Ollama로 붙었는가"
cd /opt/ax-platform/core 2>/dev/null || cd "$(dirname "$0")/../core"
# env의 공백 있는 값(PG DSN 등)에 안전하게 — LLM 3키만 직접 전달해 판정.
BACKEND=$(sudo -u axp env AXP_LLM=ollama AXP_OLLAMA_URL="$URL" AXP_OLLAMA_MODEL="$MODEL" \
  python3 -c "from axp.judge import assembler as a; print(type(a.make_backend()).__name__)" 2>/dev/null || echo "확인불가")
echo "   현재 판단 백엔드: $BACKEND"
if [ "$BACKEND" = "OllamaBackend" ]; then
  echo ""
  echo "완료 — 이제 브리핑·질문의 서술이 GPU(Ollama)로 생성됩니다."
  echo "확인: 웹앱 [오늘]→[질문]에서 '왜?'를 눌러보세요(문장이 더 자연스러워집니다)."
else
  echo ""
  echo "주의: 백엔드가 아직 Ollama가 아닙니다($BACKEND) — env 반영은 됐으니"
  echo "      'sudo systemctl restart axp-web' 한 번 더, 그래도면 GPU 도달을 재점검하세요."
fi
