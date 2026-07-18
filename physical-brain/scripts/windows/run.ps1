# 피지컬브레인 서버 시작 (Windows)
# 사용법: powershell -ExecutionPolicy Bypass -File .\run.ps1   (중지: Ctrl+C)
# 포트 8810 사용 (8800은 주식예측시스템 클라이언트와 충돌하여 회피)
$app = "$env:USERPROFILE\thirdbrain-web\physical-brain"
if (Test-Path $app) { Set-Location $app }
$env:APP_URL = "http://localhost:8810"
Write-Host "피지컬브레인 서버 시작 - 대시보드: http://localhost:8810" -ForegroundColor Green
Start-Process "http://localhost:8810"
python -m uvicorn server.main:app --host 127.0.0.1 --port 8810
