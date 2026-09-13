# AX 플랫폼 — GPU 서버 Ollama 원커맨드 설치 (Windows, 192.168.0.5)
# 실행: GPU 서버에서 "관리자 권한" PowerShell을 열고
#       powershell -ExecutionPolicy Bypass -File gpu-ollama-setup.ps1
# 하는 일: Ollama 설치 확인 → 모델 pull → LAN 공개(OLLAMA_HOST) → 방화벽 개방
#          → 자기 점검(로컬 생성 1회) → 서버1에서 붙일 주소 출력
# 안전: 주식예측시스템과 GPU 공유 — 이 스크립트는 Ollama만 다룬다.

$ErrorActionPreference = "Stop"
$Model = "qwen2.5:14b-instruct"
$Port  = 11434

Write-Host "== 1/5 Ollama 설치 확인" -ForegroundColor Cyan
$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
  Write-Host "!! Ollama가 없습니다 — https://ollama.com/download 에서 Windows용을 먼저 설치한 뒤" -ForegroundColor Yellow
  Write-Host "   이 창을 닫고 새 관리자 PowerShell에서 다시 실행하세요." -ForegroundColor Yellow
  exit 1
}
ollama --version

Write-Host "== 2/5 모델 내려받기 ($Model, 약 9GB — 처음이면 시간이 걸립니다)" -ForegroundColor Cyan
ollama pull $Model

Write-Host "== 3/5 LAN 공개 — OLLAMA_HOST=0.0.0.0 (시스템 환경변수, 영구)" -ForegroundColor Cyan
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0", "Machine")
Write-Host "   설정됨 — 적용을 위해 트레이의 Ollama 아이콘 → Quit 후 재실행(아래 5절에서 안내)"

Write-Host "== 4/5 방화벽 개방 — TCP $Port 인바운드 허용" -ForegroundColor Cyan
if (-not (Get-NetFirewallRule -DisplayName "Ollama $Port" -ErrorAction SilentlyContinue)) {
  New-NetFirewallRule -DisplayName "Ollama $Port" -Direction Inbound -Action Allow `
    -Protocol TCP -LocalPort $Port | Out-Null
  Write-Host "   방화벽 규칙 생성됨"
} else {
  Write-Host "   방화벽 규칙 이미 있음(유지)"
}

Write-Host "== 5/5 자기 점검 — 로컬 생성 1회" -ForegroundColor Cyan
try {
  $r = ollama run $Model "한 문장으로 자기소개해줘"
  Write-Host "   모델 응답: $r" -ForegroundColor Green
} catch {
  Write-Host "   (점검 생성은 건너뜀 — 서버1 연결 후 실측)" -ForegroundColor Yellow
}

$ip = (Get-NetIPAddress -AddressFamily IPv4 |
       Where-Object { $_.IPAddress -like "192.168.*" } |
       Select-Object -First 1).IPAddress
Write-Host ""
Write-Host "완료. 남은 일 두 가지:" -ForegroundColor Cyan
Write-Host "  (1) 작업표시줄 트레이의 Ollama 아이콘 → Quit → 다시 실행 (OLLAMA_HOST 적용)"
Write-Host "  (2) 서버1 우분투에서:  sudo bash deploy/connect-gpu.sh $ip"
Write-Host ""
Write-Host "이 GPU 서버 주소: http://$ip`:$Port   (서버1이 여기로 붙습니다)"
