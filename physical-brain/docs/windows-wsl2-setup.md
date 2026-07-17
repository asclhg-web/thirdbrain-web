# Windows GPU 서버 셋업 런북 (DESKTOP-ACK17CB용)

홈 서버가 Windows인 경우의 T21 절차. 리눅스 재설치 없이 **WSL2**(Windows 안의
우분투)로 기존 런북을 그대로 쓴다. 드라이버는 Windows 것을 WSL이 물려받으므로
리눅스 드라이버 설치는 필요 없다.

## 0. 점검 (5분)

PowerShell(관리자)에서 `physical-brain/docker/gpu-check.ps1` 실행 →
출력 전체를 Claude에게 붙여넣기. 아래 1~3은 [X]가 나온 항목만 하면 된다.

## 1. WSL2 + 우분투 (최초 1회, 재부팅 1번)

```powershell
wsl --install -d Ubuntu-22.04
wsl --update
```

## 2. Docker Desktop

1. https://docker.com 에서 Docker Desktop 설치 (WSL2 backend 기본값 유지)
2. Settings → Resources → WSL integration → Ubuntu-22.04 켜기
3. 확인: `docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi`

## 3. 앱 배포 (WSL 우분투 셸에서 — 기존 런북과 동일)

```bash
git clone -b claude/physical-ai-book-yrzi3h https://github.com/asclhg-web/thirdbrain-web.git
cd thirdbrain-web/physical-brain
pip install -r requirements.txt
cp .env.example .env        # STT medium·piper 기본값 포함(D-07·D-08)
make init && make test      # 23개 테스트 통과 확인
docker compose --profile gpu up -d   # Ollama(11434) + STT(8801)
make dev                    # 앱(8800)
```

Windows 브라우저에서 그대로 열린다: http://localhost:8800

## 4. LLM 모델 받기 (Ollama)

```bash
docker exec -it $(docker ps -qf name=ollama) ollama pull qwen2.5:14b   # 시작용
# VRAM 24GB면: ollama pull qwen2.5:32b
# .env: LLM_MODEL=qwen2.5:14b 로 지정 후 앱 재시작
```

## 5. 음성·학습

- 음성: `python3 -m robot.voice_client --text` 로 먼저 확인 → 마이크는
  WSL에서 제약이 있어 **음성 클라이언트는 Windows 쪽 파이썬**에서 실행 권장
  (`pip install requests sounddevice numpy`).
- LeRobot 학습: `docs/lerobot-training-runbook.md` (WSL 셸에서 동일 적용,
  USB 시리얼은 usbipd-win으로 WSL에 연결: `winget install usbipd`).

## 주의 — 절전 설정

상시 비서로 쓰려면: 설정 → 시스템 → 전원 → **절전 모드 '안 함'**.
Windows 업데이트 자동 재부팅은 '사용 시간' 설정으로 방지.
