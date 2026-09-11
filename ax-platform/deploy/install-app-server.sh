#!/usr/bin/env bash
# AX 플랫폼 — 앱 서버 원커맨드 설치 (Ubuntu 22.04/24.04, 컨테이너 없이)
# 사용: sudo bash deploy/install-app-server.sh
# 하는 일: PG16 설치·DB 생성 → 파이썬 의존성 → /opt 배치 → env 생성(무작위 비밀)
#          → systemd 유닛 등록 → 테스트 실행 → 기동
set -euo pipefail

AXP_HOME=/opt/ax-platform
AXP_DATA=/var/lib/axp/data
ENV_FILE=/etc/axp/env
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "== 1/7 시스템 패키지 =="
apt-get update -q
apt-get install -y -q postgresql postgresql-contrib python3-pip python3-venv

echo "== 2/7 PostgreSQL 준비 =="
systemctl enable --now postgresql
PGPW="$(openssl rand -hex 16)"
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='axp'" | grep -q 1 \
  || sudo -u postgres psql -c "CREATE USER axp WITH PASSWORD '${PGPW}'"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='axp'" | grep -q 1 \
  || sudo -u postgres createdb -O axp axp
# CDC 수신을 위해 논리 복제 활성화
PGCONF=$(sudo -u postgres psql -tAc "SHOW config_file")
grep -q "^wal_level = logical" "$PGCONF" || {
  sed -i "s/^#\?wal_level.*/wal_level = logical/" "$PGCONF"
  systemctl restart postgresql
}

echo "== 3/7 코드 배치 =="
id -u axp &>/dev/null || useradd -r -m -d /var/lib/axp -s /usr/sbin/nologin axp
mkdir -p "$AXP_HOME" "$AXP_DATA"
rsync -a --delete "$REPO_DIR/core" "$REPO_DIR/deploy" "$AXP_HOME/"
chown -R axp:axp "$AXP_HOME" /var/lib/axp

echo "== 4/7 파이썬 의존성 =="
pip3 install -q --break-system-packages \
  pandas scikit-learn matplotlib pyarrow fastapi "uvicorn[standard]" \
  python-multipart openpyxl defusedxml lxml pytest "psycopg[binary]" httpx

echo "== 5/7 환경 파일 =="
mkdir -p /etc/axp
if [ ! -f "$ENV_FILE" ]; then
  cat > "$ENV_FILE" <<EOF
AXP_MODE=prod
AXP_DB=postgres
AXP_PG_DSN=host=127.0.0.1 port=5432 user=axp password=${PGPW} dbname=axp
AXP_DATA=${AXP_DATA}
AXP_SECRET=$(openssl rand -hex 32)
AXP_API_KEY=$(openssl rand -hex 24)
AXP_NOTIFY=dryrun
# GPU 서버 연결 시 주석 해제:
#AXP_LLM=ollama
#AXP_OLLAMA_URL=http://<GPU서버-내부IP>:11434
#AXP_OLLAMA_MODEL=qwen2.5:14b-instruct
EOF
  chmod 600 "$ENV_FILE"
  echo "  생성: $ENV_FILE (PG 비밀번호·세션 키 무작위)"
else
  echo "  유지: $ENV_FILE (기존 파일 보존)"
fi

echo "== 6/7 검증 (테스트 양쪽 백엔드) =="
cd "$AXP_HOME"
sudo -u axp env AXP_DATA="$AXP_DATA" python3 -m pytest -q core/tests | tail -1
sudo -u axp env $(grep -v '^#' "$ENV_FILE" | xargs) python3 -m pytest -q core/tests | tail -1

echo "== 7/7 systemd 등록·기동 (웹·스케줄러·하트비트) =="
cp "$AXP_HOME/deploy/systemd/axp-web.service" /etc/systemd/system/
cp "$AXP_HOME/deploy/systemd/axp-scheduler.service" /etc/systemd/system/
cp "$AXP_HOME/deploy/systemd/axp-heartbeat.service" /etc/systemd/system/
cp "$AXP_HOME/deploy/systemd/axp-heartbeat.timer" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now axp-web axp-scheduler axp-heartbeat.timer
sleep 2
systemctl --no-pager -l status axp-web | head -5

echo
echo "완료. 초기 계정 비밀번호: ${AXP_DATA}/initial-credentials.txt (전달 후 삭제)"
echo "웹앱: http://127.0.0.1:8900  — 외부 공개는 Caddy(deploy/Caddyfile) 또는"
echo "      Cloudflare Tunnel(deploy/install-tunnel.sh — odooaierp.com 공개용)."
echo "체험 테넌트 운영은 docs/deploy-odooaierp.md 4장(크론 3종)을 따르세요:"
echo "  crontab 예시 → deploy/crontab.example"
