# 피지컬브레인 서버 시작 (Windows)
# 사용법: powershell -ExecutionPolicy Bypass -File .\run.ps1   (중지: Ctrl+C)
$app = "$env:USERPROFILE\thirdbrain-web\physical-brain"
if (Test-Path $app) { Set-Location $app }
Write-Host "피지컬브레인 서버 시작 - 대시보드: http://localhost:8800" -ForegroundColor Green
Start-Process "http://localhost:8800"
python -m uvicorn server.main:app --host 127.0.0.1 --port 8800
