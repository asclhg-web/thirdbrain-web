# =====================================================================
#  피지컬브레인 Plan B 자동 설치 (Windows 네이티브, BIOS/가상화 불필요)
#  사용법: 아무 폴더에서  powershell -ExecutionPolicy Bypass -File .\setup.ps1
#  이미 설치된 항목은 건너뛰므로 여러 번 실행해도 안전합니다.
# =====================================================================
$ErrorActionPreference = "Continue"
$RepoUrl = "https://github.com/asclhg-web/thirdbrain-web.git"
$Branch  = "claude/physical-ai-book-yrzi3h"
$Home2   = "$env:USERPROFILE\thirdbrain-web"
$Model   = "qwen2.5:7b"   # GPU 공유 설계: 주식학습(19:00~05:30)과 동거 위한 소형 모델

function Step($msg) { Write-Host "`n== $msg" -ForegroundColor Cyan }

Step "1/7 Python 확인"
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { Write-Host "  [X] python 없음 - https://python.org 에서 3.11+ 설치(Add to PATH 체크) 후 재실행" -ForegroundColor Red; exit 1 }
python --version

Step "2/7 Git 확인 (없으면 자동 설치)"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
  $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
}
git --version

Step "3/7 Ollama 확인 (없으면 자동 설치)"
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
  winget install --id Ollama.Ollama -e --accept-source-agreements --accept-package-agreements
  $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
}
ollama --version
[Environment]::SetEnvironmentVariable("OLLAMA_KEEP_ALIVE", "2m", "User")  # 응답 2분 뒤 VRAM 반납

Step "4/7 LLM 모델 다운로드 ($Model, 최초 1회 약 4.7GB)"
ollama pull $Model

Step "5/7 앱 소스 받기 (github.com 로그인 창이 뜨면 로그인해 주세요)"
if (Test-Path "$Home2\.git") {
  Set-Location $Home2
  git fetch origin $Branch
  git checkout $Branch
  git pull origin $Branch
} else {
  git clone -b $Branch $RepoUrl $Home2
  Set-Location $Home2
}
Set-Location "$Home2\physical-brain"

Step "6/7 파이썬 패키지 + 데이터 초기화"
python -m pip install -q -r requirements.txt
if (-not (Test-Path ".env")) {
  Copy-Item .env.example .env
  (Get-Content .env) -replace '^LLM_MODEL=$', "LLM_MODEL=$Model" | Set-Content .env
}
python -m graph.init_db
python -m graph.seed
python -m pipelines.mock_health --days 30

Step "7/7 테스트 (23개 통과가 정상)"
python -m pytest tests/ -q

Write-Host "`n=====================================================" -ForegroundColor Green
Write-Host " 설치 완료! 서버 시작:" -ForegroundColor Green
Write-Host "   powershell -ExecutionPolicy Bypass -File $Home2\physical-brain\scripts\windows\run.ps1" -ForegroundColor Green
Write-Host " 대시보드: http://localhost:8810" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
