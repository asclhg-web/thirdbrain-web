#!/usr/bin/env bash
# AX 플랫폼 — 서술 백엔드를 Anthropic Claude로 전환 (P8-GPU2)
# 실행: sudo bash deploy/connect-claude.sh sk-ant-...  [모델]
#       예) sudo bash deploy/connect-claude.sh sk-ant-xxxx claude-haiku-4-5
# 하는 일: anthropic SDK 확인·설치 → /etc/axp/env에 키·모델 반영(멱등)
#          → 서비스 재시작 → 판단 백엔드가 실제 ClaudeBackend인지 실측
# 정직 고지: Claude는 외부(api.anthropic.com) — '검색된 사실'이 외부로
#            전송된다(사설망 Ollama와 다름). 회사 방침으로 채택 시 사용.
set -euo pipefail

KEY="${1:-}"
MODEL="${2:-claude-opus-5}"
ENV_FILE=/etc/axp/env

if [ -z "$KEY" ]; then
  echo "!! 사용법: sudo bash deploy/connect-claude.sh <ANTHROPIC_API_KEY> [모델]"
  echo "   예) sudo bash deploy/connect-claude.sh sk-ant-xxxx claude-haiku-4-5"
  exit 1
fi
[ -f "$ENV_FILE" ] || { echo "!! $ENV_FILE 없음 — 먼저 install-app-server.sh 실행"; exit 1; }

echo "== 1/4 anthropic SDK 확인"
if ! sudo -u axp python3 -c "import anthropic" 2>/dev/null; then
  echo "   설치 중(pip)…"
  pip3 install -q --break-system-packages anthropic
fi
sudo -u axp python3 -c "import anthropic; print('   anthropic', anthropic.__version__)"

echo "== 2/4 /etc/axp/env에 반영(멱등)"
set_kv() {
  local k="$1" v="$2"
  if grep -qE "^#?${k}=" "$ENV_FILE"; then
    sed -i "s|^#\?${k}=.*|${k}=${v}|" "$ENV_FILE"
  else
    echo "${k}=${v}" >> "$ENV_FILE"
  fi
  # 다른 백엔드 잔재 주석 처리(중복 활성 방지)
}
# Ollama가 켜져 있었으면 끈다(둘 중 하나만)
sed -i 's|^AXP_LLM=ollama|#AXP_LLM=ollama|' "$ENV_FILE" || true
set_kv AXP_LLM claude
set_kv ANTHROPIC_API_KEY "$KEY"
set_kv AXP_CLAUDE_MODEL "$MODEL"
chmod 600 "$ENV_FILE"
echo "   반영: AXP_LLM=claude · AXP_CLAUDE_MODEL=$MODEL · 키 저장(0600)"

echo "== 3/4 서비스 재시작"
systemctl restart axp-web axp-scheduler
sleep 3

echo "== 4/4 판단 백엔드 실측"
cd /opt/ax-platform/core 2>/dev/null || cd "$(dirname "$0")/../core"
BACKEND=$(sudo -u axp env AXP_LLM=claude ANTHROPIC_API_KEY="$KEY" AXP_CLAUDE_MODEL="$MODEL" \
  python3 -c "from axp.judge import assembler as a; print(type(a.make_backend()).__name__)" 2>/dev/null || echo "확인불가")
echo "   현재 판단 백엔드: $BACKEND"
if [ "$BACKEND" = "ClaudeBackend" ]; then
  echo ""
  echo "완료 — 브리핑·질문 서술이 Claude($MODEL)로 생성됩니다."
  echo "확인: 웹앱 [오늘]→[질문]에서 질문 후 문장을 보세요(끝에 [근거:] 유지)."
  echo "주의: 외부 전송·API 비용 발생 — 비용을 낮추려면 모델을 claude-haiku-4-5로."
else
  echo ""
  echo "주의: 백엔드가 ClaudeBackend가 아닙니다($BACKEND) — 키 유효성/네트워크를"
  echo "      점검하세요. 실패해도 판단은 결정적 조립기로 계속 돕니다."
fi
