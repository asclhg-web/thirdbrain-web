#!/usr/bin/env bash
# AX 플랫폼 — GPU 서버 원커맨드 설치 (Ollama + 한국어 후보 모델 3종)
# 사용: sudo bash install-gpu-server.sh <앱서버-내부IP>
set -euo pipefail
APP_IP="${1:?사용법: install-gpu-server.sh <앱서버-내부IP>}"

echo "== 1/4 GPU 확인 =="
nvidia-smi | head -4 || { echo "NVIDIA 드라이버가 없습니다 — 드라이버 설치 후 재실행"; exit 1; }

echo "== 2/4 Ollama 설치 =="
command -v ollama >/dev/null || curl -fsSL https://ollama.com/install.sh | sh
mkdir -p /etc/systemd/system/ollama.service.d
cat > /etc/systemd/system/ollama.service.d/override.conf <<EOF
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF
systemctl daemon-reload
systemctl enable --now ollama
systemctl restart ollama

echo "== 3/4 방화벽 — 11434는 앱 서버에만 =="
if command -v ufw >/dev/null; then
  ufw allow from "$APP_IP" to any port 11434 proto tcp
  ufw deny 11434/tcp || true
  echo "  ufw: ${APP_IP} → 11434 허용, 그 외 차단"
else
  echo "  (ufw 없음 — 방화벽에서 11434를 ${APP_IP}에만 허용하도록 수동 설정)"
fi

echo "== 4/4 한국어 후보 모델 =="
ollama pull qwen2.5:14b-instruct
ollama pull exaone3.5:7.8b
ollama pull llama3.1:8b
ollama list

echo
echo "완료. 앱 서버 /etc/axp/env에서 AXP_LLM=ollama, AXP_OLLAMA_URL=http://$(hostname -I | awk '{print $1}'):11434 활성화."
echo "모델 선정: 앱 서버에서  python3 deploy/llm_bench.py  실행 → 비교표 출력."
