# 피지컬브레인 서버 종합 점검 (GPU 서버용)
# 사용: powershell -ExecutionPolicy Bypass -File C:\Users\ASC\thirdbrain-web\physical-brain\scripts\windows\check.ps1
# 출력 전체를 복사해서 Claude에게 붙여넣으면 판독해 드립니다.

Write-Host "`n== 1. 피지컬브레인 앱 (포트 8810) ==" -ForegroundColor Cyan
try { $h = Invoke-RestMethod http://localhost:8810/health -TimeoutSec 5; Write-Host "  [OK] 서버 응답: $($h.status) v$($h.version)" }
catch { Write-Host "  [X] 서버 무응답 - run.ps1이 꺼져 있음" -ForegroundColor Red }

Write-Host "`n== 2. 심장박동 최근 활동 (그래프의 최근 이벤트) ==" -ForegroundColor Cyan
Set-Location "$env:USERPROFILE\thirdbrain-web\physical-brain"
python -c "from graph import store; ev=store.events('나',2); print('  최근 이벤트', len(ev), '건 / 마지막:', ev[-1]['at'] if ev else '없음', ev[-1]['kind'] if ev else '')"

Write-Host "`n== 3. 오늘의 복약 태스크 ==" -ForegroundColor Cyan
python -c "from datetime import datetime; from server.tasks_today import expand_today, today; expand_today(datetime.now()); [print('  ', t['time'], t['med'], '->', t['status']) for t in today(datetime.now())]"

Write-Host "`n== 4. 삼성헬스 인박스 처리 상태 ==" -ForegroundColor Cyan
$inbox = "$env:USERPROFILE\OneDrive - AI솔루션\obsidian valt\피지컬브레인\인박스"
if (Test-Path $inbox) {
  Write-Host "  인박스 대기:" (dir $inbox -File -ErrorAction SilentlyContinue).Count "개"
  if (Test-Path "$inbox\처리됨") { Write-Host "  처리됨:" (dir "$inbox\처리됨" -File).Count "개" }
  python -c "from graph import store; m=store.measurements('나','rhr',30); a=store.activities('나','sleep',30); w=store.activities('나','walk',30); print('  실데이터: 심박', len(m), '일 / 수면', len(a), '일 / 걸음', len(w), '일')"
} else { Write-Host "  [!] 인박스 폴더 없음 (아직 동기화 전이거나 미생성)" }

Write-Host "`n== 5. GPU / LLM ==" -ForegroundColor Cyan
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader
try { $t = ollama ps 2>$null; Write-Host "  ollama:" ($t -join ' | ') } catch { Write-Host "  ollama 명령 없음/미가동" }

Write-Host "`n== 6. 디스크 여유 ==" -ForegroundColor Cyan
Get-PSDrive C | ForEach-Object { Write-Host ("  C: 사용 {0:N0}GB / 여유 {1:N0}GB" -f ($_.Used/1GB), ($_.Free/1GB)) }

Write-Host "`n== 점검 끝 - 전체 출력을 복사해 주세요 ==" -ForegroundColor Green
