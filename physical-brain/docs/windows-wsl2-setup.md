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

## GPU 공유 원칙 (동일 서버의 주식예측시스템과 동거)

이 서버에는 주식예측시스템이 함께 산다 — 상시 약 2.2GB, **학습 19:00~05:30**.

- LLM은 **7~8b급 소형 모델**로 시작 (VRAM ~5GB): `ollama pull qwen2.5:7b`, `.env LLM_MODEL=qwen2.5:7b`
- Ollama `OLLAMA_KEEP_ALIVE=2m` (compose에 반영됨) — 응답 후 2분 뒤 VRAM 자동 반납
- 아침 브리핑 07:00은 학습 종료(05:30) 후라 충돌 없음. 저녁 리포트 21:30은 학습과
  겹치지만 GPU 사용이 수십 초 + 실패 시 규칙 기반 폴백으로 리포트는 항상 나간다
- 14b 승격 판단: 학습 도중 `nvidia-smi`로 학습 피크 VRAM 확인 후
  (2.2GB 상시 + 학습 피크 + 10GB) < 15GB 면 가능

## Plan B — BIOS/가상화 없이 먼저 시작하는 길 (✅ 2026-07-18 채택)

가상화는 WSL2·도커용이며, 당장의 LLM+앱+STT는 Windows 네이티브로 충분하다.
**자동 설치 스크립트 1개로 끝**: `scripts/windows/setup.ps1`
(Git·Ollama 자동 설치 → qwen2.5:7b 다운로드 → 소스 클론 → 패키지·DB 초기화 → 테스트)

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1     # 설치 (재실행 안전)
powershell -ExecutionPolicy Bypass -File .\run.ps1       # 서버 시작 → localhost:8810
```

주의: 이 서버(Windows)에서는 앱 포트가 **8810**이다. 8800은 주식예측시스템의
클라이언트가 로그인을 시도하는 포트라 충돌을 피해 옮겼다 (2026-07-18).
음성 클라이언트를 쓸 때는 `$env:APP_URL="http://localhost:8810"` 설정.

- STT: 도커 서버 없이 `pip install faster-whisper` 로 로컬 인식
  (voice_client가 서버 연결 실패 시 자동으로 로컬 엔진 사용)
- LLM 연동 경로는 모의 Ollama 서버로 사전 검증 완료 (available→/api/tags, chat→/api/chat)
- 가상화가 꼭 필요해지는 시점은 LeRobot 학습(4단계)부터 — 그때 BIOS 작업 재개.

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
