#!/usr/bin/env bash
# 데모 시딩 — 서버1의 실제 웹앱 DB에 전 파이프라인 샘플 데이터를 적재한다.
# 내일 데모에서 app.odooaierp.com(또는 127.0.0.1:8900) 화면이 그대로 보인다:
#   판단(승인함) 카드 11건 · 성과(프로젝트·KPI) 달성도 · 오늘 할 일 · 브리핑.
#
# 안전: PG·데이터 디렉토리를 먼저 백업하고 복원 힌트를 출력한다. 데모 서버 전용
#       (실고객 데이터가 있으면 실행 금지 — run_e2e 가 데이터 디렉토리를 새로 만든다).
#
# 사용: cd ~/thirdbrain-web && git pull
#       sudo bash ax-platform/deploy/seed-demo.sh
#       (데모 계정 비밀번호를 바꾸려면 DEMO_PW=... 를 앞에 붙인다)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"          # .../ax-platform/deploy
AXROOT="$(cd "$HERE/.." && pwd)"               # .../ax-platform (repo 체크아웃; demo/ 포함)
[ -f /etc/axp/env ] && source /etc/axp/env || true
: "${AXP_DATA:=/var/lib/axp/data}"
: "${AXP_DB:=postgres}"
: "${AXP_PROFILE:=taesungdang}"
DEMO_PW="${DEMO_PW:-Demo!2026}"
export AXP_DATA AXP_DB AXP_PROFILE
[ -n "${AXP_PG_DSN:-}" ] && export AXP_PG_DSN
export PYTHONPATH="$AXROOT/core:$AXROOT"
ts=$(date +%Y%m%d-%H%M%S)
BK=/var/lib/axp

echo "── 0/5 백업 (복원용)"
DB=axp
case "${AXP_PG_DSN:-}" in *dbname=*) DB=$(printf '%s\n' "$AXP_PG_DSN" | sed -n 's/.*dbname=\([^ ]*\).*/\1/p');; esac
: "${DB:=axp}"
# 백업은 실패해도 시딩을 막지 않는다(가동 중 데이터 디렉토리 tar 경고 등) — errexit 일시 해제
set +e
if [ "$AXP_DB" = "postgres" ]; then
  sudo -u postgres pg_dump "$DB" 2>/dev/null | gzip > "$BK/pg-backup-$ts.sql.gz" \
    && echo "  PG($DB) 백업 → $BK/pg-backup-$ts.sql.gz" || echo "  (PG 백업 건너뜀 — 계속 진행)"
fi
if [ -d "$AXP_DATA" ]; then
  tar czf "$BK/data-backup-$ts.tgz" --warning=no-file-changed \
    -C "$(dirname "$AXP_DATA")" "$(basename "$AXP_DATA")" 2>/dev/null \
    && echo "  데이터 백업 → $BK/data-backup-$ts.tgz" || echo "  (데이터 백업 건너뜀 — 계속 진행)"
fi
set -e

echo "── 1/5 전 파이프라인 시딩 (demo.run_e2e · 약 1분)"
cd "$AXROOT"
python3 -m demo.run_e2e

echo "── 2/5 프로젝트·KPI 달성도 시딩"
python3 -m demo.demo_kpi_run

echo "── 3/5 데모 계정 비밀번호 고정(로그인 보장)"
python3 - "$DEMO_PW" <<'PY'
import sys, secrets, hashlib
from axp.webapp import ensure_users
from axp import db
ensure_users()
pw = sys.argv[1]
def h(pw, salt): return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 60_000).hex()
cols = [c["name"] for c in db.query("PRAGMA table_info(axp_users)")] \
       if db.BACKEND != "postgres" else \
       [r["column_name"] for r in db.query(
           "SELECT column_name FROM information_schema.columns WHERE table_name='axp_users'")]
for u in ("admin", "steward", "approver"):
    salt = secrets.token_hex(8)
    if "must_change" in cols:
        db.execute("UPDATE axp_users SET pw_hash=?, salt=?, must_change=0 WHERE username=?", (h(pw, salt), salt, u))
    else:
        db.execute("UPDATE axp_users SET pw_hash=?, salt=? WHERE username=?", (h(pw, salt), salt, u))
print("  데모 계정 비밀번호 설정 완료")
PY

echo "── 4/5 권한 정리 + 서비스 재시작"
chown -R axp:axp "$AXP_DATA" 2>/dev/null || true
systemctl restart axp-web axp-scheduler 2>/dev/null || true
sleep 2

echo "── 5/5 확인"
curl -s http://127.0.0.1:8900/health && echo || echo "(웹앱 응답 확인 필요)"

cat <<EON

════════════════ 데모 준비 완료 ════════════════
로그인:  admin / ${DEMO_PW}   (steward·approver 동일 비밀번호)
공개 주소: https://app.odooaierp.com   (apex 전환 시 https://odooaierp.com)

데모 동선:
  · 오늘              — 할 일·승인 대기 카드
  · 판단 → 승인함      — 판단 카드 11건(수요예측·생산계획·재고·설비·규칙, 근거 인용)
  · 성과 → 프로젝트·KPI — 'AX 통합 성과 시연 1차' 달성도(경영목표 3/4 달성)
  · 질문              — "왜 폐기율이…" 자연어 질문(근거 사다리)

되돌리기(필요 시):
  gunzip -c $BK/pg-backup-$ts.sql.gz | sudo -u postgres psql ${DB:-axp}
  sudo tar xzf $BK/data-backup-$ts.tgz -C $(dirname "$AXP_DATA")
  sudo systemctl restart axp-web axp-scheduler
EON
