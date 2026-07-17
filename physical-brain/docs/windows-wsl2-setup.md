# Windows GPU 서버 셋업 런북 (DESKTOP-ACK17CB용)

## 확인된 사양 (2026-07-17 점검 완료)

- GPU: **RTX 5080 16GB** (블랙웰) / 드라이버 610.62 ✅
- WSL2: 미설치 → 1단계 / Docker: 미설치 → 2단계

## 진행 상황 (2026-07-17 저녁 중단 — 여기서 재개)

- 메인보드 ASUS / UEFI / CPU 가상화 **사용 안 함** → BIOS에서 켜야 함
- BIOS 진입 시도 이력: Del 연타 실패(원인: 블루투스 키보드 → **유선 키보드 연결 완료**),
  `shutdown /r /fw` 실패, 설정의 "지금 다시 시작" 실패
- **내일 첫 단계**: 관리자 PowerShell에서 `powercfg /h off` → `shutdown /s /t 0`
  (빠른 시작 끄고 완전 종료) → 전원 켜자마자 유선 키보드로 **Del 연타**
  → 실패 시 Shift 누른 채 시작메뉴 "다시 시작" → 문제 해결 → 고급 옵션 → UEFI 펌웨어 설정
- BIOS 진입 후: F7(Advanced Mode) → Advanced → CPU Configuration →
  Intel (VMX) Virtualization Technology 또는 SVM Mode → **Enabled** → F10 저장
- 이후: `wsl.exe --install --no-distribution` → 재부팅 → `wsl --install -d Ubuntu-22.04`

**블랙웰(RTX 50번대) 주의**: PyTorch는 반드시 CUDA 12.8 이상 빌드로 설치
(`pip install torch --index-url https://download.pytorch.org/whl/cu128`).
구버전(cu121 등)은 GPU를 인식하지 못한다. Ollama·faster-whisper 도커 이미지는
최신 태그면 문제 없음.

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
3. 확인: `docker run --rm --gpus all nvidia/cuda:12.8.0-base-ubuntu22.04 nvidia-smi`

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
