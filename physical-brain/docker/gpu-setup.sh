#!/usr/bin/env bash
# T21 — GPU 서버(우분투) 셋업 점검·설치 스크립트
# 사용: bash docker/gpu-setup.sh          (점검만)
#       bash docker/gpu-setup.sh --install (미설치 항목 설치 시도)
set -u
INSTALL=${1:-}

ok()   { echo "  ✅ $1"; }
bad()  { echo "  ❌ $1"; }
step() { echo; echo "── $1"; }

step "1. NVIDIA 드라이버"
if command -v nvidia-smi >/dev/null; then
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader | sed 's/^/  /'
  ok "드라이버 정상"
else
  bad "nvidia-smi 없음 → 드라이버 설치 필요"
  [ "$INSTALL" = "--install" ] && sudo ubuntu-drivers autoinstall
fi

step "2. Docker"
if command -v docker >/dev/null && docker info >/dev/null 2>&1; then
  ok "docker 데몬 정상"
else
  bad "docker 미설치/미가동"
  [ "$INSTALL" = "--install" ] && curl -fsSL https://get.docker.com | sudo sh
fi

step "3. NVIDIA Container Toolkit"
if docker info 2>/dev/null | grep -qi nvidia; then
  ok "toolkit 연동됨"
else
  bad "toolkit 미연동"
  if [ "$INSTALL" = "--install" ]; then
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-ctk.gpg
    curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
      | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-ctk.gpg] https://#' \
      | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
    sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker
  fi
fi

step "4. GPU 컨테이너 스모크 테스트"
if docker run --rm --gpus all nvidia/cuda:12.8.0-base-ubuntu22.04 nvidia-smi >/dev/null 2>&1; then
  ok "컨테이너에서 GPU 인식"
else
  bad "GPU 컨테이너 실패 (1~3 확인 후 재시도)"
fi

step "5. 방화벽 원칙 (로컬 퍼스트)"
echo "  외부 포트 개방 금지. 원격 접근은 테일스케일 VPN 권장:"
echo "    curl -fsSL https://tailscale.com/install.sh | sh && sudo tailscale up"
echo "  앱(8800)·Ollama(11434)는 VPN/사설망 인터페이스에만 바인딩할 것."

step "6. 앱 배포"
echo "  git clone -b claude/physical-ai-book-yrzi3h https://github.com/asclhg-web/thirdbrain-web.git"
echo "  cd thirdbrain-web/physical-brain && pip install -r requirements.txt && make init && make test"
echo "  GPU 프로파일 실행: docker compose --profile gpu up -d"
