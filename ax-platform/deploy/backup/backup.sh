#!/usr/bin/env bash
# 3-2-1 백업 (M0-2): 사본 3 · 매체 2 · 원격 1
# 스케줄: 일 증분(pg WAL은 상시), 주 전체. cron 예: 0 2 * * * /opt/ax/deploy/backup/backup.sh daily
set -euo pipefail
MODE="${1:-daily}"                       # daily | weekly
STAMP="$(date +%Y%m%d_%H%M%S)"
LOCAL=/backup                            # 사본 1 (compose 볼륨, 매체 1)
MEDIA2="${AXP_BACKUP_MEDIA2:-/mnt/nas/axp}"      # 사본 2 (NAS, 매체 2)
REMOTE="${AXP_BACKUP_REMOTE:-}"          # 사본 3 (원격/오프사이트 rsync 대상)
ALERT="${AXP_ALERT_WEBHOOK:-}"           # 실패 경보(사내 메신저 webhook)

fail() { [ -n "$ALERT" ] && curl -fsS -m 10 -X POST "$ALERT" -d "{\"text\":\"[AXP][백업 실패] $1\"}" || true; echo "FAIL: $1" >&2; exit 1; }

mkdir -p "$LOCAL/$MODE" || fail "로컬 백업 경로"

# PostgreSQL — 표준 데이터셋·운영 테이블
docker compose exec -T postgres pg_dump -U axp -Fc axp > "$LOCAL/$MODE/pg_$STAMP.dump" \
  || fail "pg_dump"

# Neo4j — 지식그래프
docker compose exec -T neo4j neo4j-admin database dump neo4j --to-stdout > "$LOCAL/$MODE/neo4j_$STAMP.dump" \
  || fail "neo4j dump"

# MinIO — 원본·Parquet (weekly 전체, daily는 신규만 mirror)
if [ "$MODE" = weekly ]; then
  docker compose exec -T minio mc mirror --overwrite local/raw "$LOCAL/$MODE/minio_raw" || fail "minio mirror"
else
  docker compose exec -T minio mc mirror local/raw "$LOCAL/$MODE/minio_raw" || fail "minio mirror"
fi

# 레지스트리(Git)는 사내 Git 원격이 이미 사본 — bundle 로 스냅샷만 추가
git -C ../../registry bundle create "$LOCAL/$MODE/registry_$STAMP.bundle" --all 2>/dev/null || true

# 사본 2·3 복제
rsync -a --delete "$LOCAL/$MODE/" "$MEDIA2/$MODE/" || fail "매체2 복제"
[ -n "$REMOTE" ] && { rsync -a "$LOCAL/$MODE/" "$REMOTE/$MODE/" || fail "원격 복제"; }

# 보존 정책: daily 14일 · weekly 8주
find "$LOCAL/daily"  -type f -mtime +14 -delete 2>/dev/null || true
find "$LOCAL/weekly" -type f -mtime +56 -delete 2>/dev/null || true

echo "OK $MODE $STAMP"
