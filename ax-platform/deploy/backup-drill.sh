#!/usr/bin/env bash
# P5-S5: 백업/복구 드릴 원커맨드 — SLA 4장 "월 1회 복구 리허설"의 자동화.
#
# 하는 일: ① 지금 시점 전체 백업(--no-subscriptions — P2-I9 표준)
#          ② 임시 DB에 복원  ③ 원본과 테이블 건수 전수 대조
#          ④ 결과 리포트 출력·경보(불일치나 실패 시 crit)
# 원본 DB는 읽기만 한다. 임시 DB는 드릴 후 삭제.
#
# 사용: sudo bash deploy/backup-drill.sh [DB이름=axp]
set -uo pipefail

DB="${1:-axp}"
DRILL_DB="${DB}_drill_$(date +%s)"
OUT="${AXP_BACKUP_DIR:-/var/backups/axp}"
STAMP=$(date +%Y%m%d-%H%M%S)
DUMP="$OUT/${DB}-drill-${STAMP}.dump"
mkdir -p "$OUT"
chown postgres:postgres "$OUT" 2>/dev/null || true   # pg_dump는 postgres 계정으로 쓴다

fail() {
  echo "DRILL FAILED: $1"
  # 플랫폼 경보 (가능하면)
  python3 - <<PYEOF 2>/dev/null || true
import sys; sys.path.insert(0, "$(dirname "$0")/../core")
from axp import common
common.alert("crit", "backup-drill", "복구 드릴 실패: $1")
PYEOF
  sudo -u postgres psql -qc "DROP DATABASE IF EXISTS $DRILL_DB" 2>/dev/null
  exit 1
}

echo "── 1/4 백업: $DB → $DUMP"
T0=$(date +%s)
sudo -u postgres pg_dump -d "$DB" --no-subscriptions -Fc -f "$DUMP" \
  || fail "pg_dump 오류"
SIZE=$(du -h "$DUMP" | cut -f1)
T1=$(date +%s)
echo "   완료 ${SIZE} ($((T1-T0))s)"

echo "── 2/4 임시 DB 복원: $DRILL_DB"
sudo -u postgres createdb "$DRILL_DB" || fail "createdb 오류"
sudo -u postgres pg_restore -d "$DRILL_DB" --no-owner "$DUMP" 2>/tmp/drill_restore.err
# pg_restore는 무해한 경고로도 비0 종료 — 치명 오류만 가려낸다
if grep -qiE "could not|fatal|syntax error" /tmp/drill_restore.err; then
  head -5 /tmp/drill_restore.err
  fail "복원 치명 오류"
fi
T2=$(date +%s)
echo "   복원 $((T2-T1))s (경고 $(grep -ci warning /tmp/drill_restore.err 2>/dev/null || echo 0)건 — 무해)"

echo "── 3/4 건수 전수 대조"
COUNT_SQL="SELECT schemaname||'.'||relname||'='||n_live_tup FROM pg_stat_user_tables ORDER BY 1"
# 통계가 아니라 실측 count로 대조 (테이블 목록은 원본 기준)
MISMATCH=0; CHECKED=0
while IFS='|' read -r sch tbl; do
  [ -z "$tbl" ] && continue
  A=$(sudo -u postgres psql -d "$DB" -tAc "SELECT count(*) FROM \"$sch\".\"$tbl\"" 2>/dev/null)
  B=$(sudo -u postgres psql -d "$DRILL_DB" -tAc "SELECT count(*) FROM \"$sch\".\"$tbl\"" 2>/dev/null)
  CHECKED=$((CHECKED+1))
  if [ "$A" != "$B" ]; then
    echo "   불일치: $sch.$tbl 원본=$A 복원=$B"
    MISMATCH=$((MISMATCH+1))
  fi
done < <(sudo -u postgres psql -d "$DB" -tAc \
  "SELECT schemaname||'|'||tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema')")
echo "   대조 ${CHECKED}개 테이블 · 불일치 ${MISMATCH}건"
[ "$MISMATCH" -eq 0 ] || fail "건수 불일치 ${MISMATCH}건"

echo "── 4/4 정리"
sudo -u postgres psql -qc "DROP DATABASE $DRILL_DB"
T3=$(date +%s)

echo
echo "DRILL OK — 백업 ${SIZE} · 백업 $((T1-T0))s · 복원 $((T2-T1))s · 대조 ${CHECKED}테이블 · 총 $((T3-T0))s"
echo "덤프 보존: $DUMP (로테이션은 crontab의 일일 백업이 담당)"
python3 - <<PYEOF 2>/dev/null || true
import sys; sys.path.insert(0, "$(dirname "$0")/../core")
from axp import common
common.alert("info", "backup-drill",
             "복구 드릴 성공 — 백업 ${SIZE}, 복원 $((T2-T1))s, ${CHECKED}테이블 일치")
PYEOF
