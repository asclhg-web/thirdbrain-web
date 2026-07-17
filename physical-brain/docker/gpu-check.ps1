# 피지컬브레인 GPU 서버 점검 (Windows용) — T21의 Windows판
# 사용: PowerShell을 열고  cd 스크립트폴더  →  .\gpu-check.ps1
# 결과 전체를 복사해서 Claude에게 붙여넣으면 다음 단계를 안내받을 수 있습니다.

Write-Host "`n== 1. GPU / NVIDIA 드라이버 =="
try { nvidia-smi } catch { Write-Host "  [X] nvidia-smi 없음 - NVIDIA 드라이버 설치 필요 (https://www.nvidia.com/drivers)" }

Write-Host "`n== 2. WSL2 (리눅스 환경) =="
wsl --status
wsl -l -v

Write-Host "`n== 3. Docker Desktop =="
try { docker --version } catch { Write-Host "  [X] docker 없음 - Docker Desktop 설치 필요 (https://docker.com)" }
docker info 2>$null | Select-String -Pattern "Server Version"

Write-Host "`n== 4. WSL 내부에서 GPU 인식 =="
wsl -e nvidia-smi 2>$null
if (-not $?) { Write-Host "  [X] WSL 안에서 GPU 미인식 - 드라이버 최신화 + 'wsl --update' 필요" }

Write-Host "`n== 5. GPU 컨테이너 스모크 테스트 (최초 1회 이미지 다운로드 수 분) =="
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
if (-not $?) { Write-Host "  [X] 컨테이너에서 GPU 실패 - Docker Desktop 설정 > Resources > WSL integration 확인" }

Write-Host "`n== 점검 끝 - 위 출력 전체를 복사해 주세요 =="
