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

# P7: WSL2(서버1=Windows 겸용, server-map.md) 사전 점검 — WSL 우분투는
# systemd가 꺼진 채 시작될 수 있고, 그러면 아래 systemctl 전부가 실패한다.
# 켜는 법을 안내하고 여기서 멈춘다(반쯤 설치된 상태를 만들지 않기 위해).
if grep -qi microsoft /proc/version 2>/dev/null; then
  if [ "$(ps -p 1 -o comm=)" != "systemd" ]; then
    echo "!! WSL에서 systemd가 꺼져 있습니다 — 아래 두 명령 후 다시 실행하세요:"
    echo "   printf '[boot]\nsystemd=true\n' | sudo tee /etc/wsl.conf"
    echo "   (Windows PowerShell에서)  wsl --shutdown   후 wsl 재진입"
    exit 1
  fi
  echo "== WSL2 감지 — systemd 활성 확인됨 (서버1 겸용 모드)"
fi

echo "== 1/7 시스템 패키지 =="
apt-get update -q
apt-get install -y -q postgresql postgresql-contrib python3-pip python3-venv

echo "== 2/7 PostgreSQL 준비 =="
systemctl enable --now postgresql
# P7-I5(서버1 실설치 적발): 중단→재실행 시 '기존 역할은 옛 비밀번호,
# 새 env는 새 비밀번호'로 어긋나 PG 인증이 전면 실패한다 —
# env 파일이 이미 있으면 그 비밀번호를 재사용하고, 역할 비밀번호를
# 항상 env와 같은 값으로 정렬한다(멱등).
if [ -f "$ENV_FILE" ]; then
  PGPW="$(grep -oP 'password=\K[^ ]+' "$ENV_FILE")"
else
  PGPW="$(openssl rand -hex 16)"
fi
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='axp'" | grep -q 1 \
  || sudo -u postgres psql -c "CREATE USER axp WITH PASSWORD '${PGPW}'"
sudo -u postgres psql -qc "ALTER ROLE axp WITH PASSWORD '${PGPW}'"
# P7-I7(서버1 실설치 적발): FK 일시 해제(PRAGMA→session_replication_role)는
# superuser 전용 파라미터 — 일반 역할 axp에 SET 권한을 위임한다(PG15+).
# 없으면 야간 재구축(transform)과 PG 테스트 14건이 InsufficientPrivilege로 죽는다.
sudo -u postgres psql -qc "GRANT SET ON PARAMETER session_replication_role TO axp"
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
# P7-I4(서버1 실설치 적발): registry(데이터 계약)가 빠지면 품질 게이트가
# '계약 없음'으로 전면 실패한다 — 코드·계약·배포 3종을 함께 배치
rsync -a --delete "$REPO_DIR/core" "$REPO_DIR/deploy" "$REPO_DIR/registry" "$AXP_HOME/"
chown -R axp:axp "$AXP_HOME" /var/lib/axp

echo "== 4/7 파이썬 의존성 =="
# 서버1 실설치 실측(P7): 우분투 24.04 기본 typing_extensions(4.10, deb 설치)를
# pip이 못 지워 중단 — 선제 대체로 우회(RECORD 없는 deb 패키지 충돌 유형)
pip3 install -q --break-system-packages --ignore-installed typing_extensions
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
# P6: 체험 신청 자동 발급 — 승인제가 기본(접수된 결정). 협의 후에만 1로.
#AXP_AUTO_ISSUE=0
# P6: 테넌트 업로드 총량 상한(MB) — 기본 500
#AXP_TENANT_QUOTA_MB=500
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
# P7-I6(서버1 실설치 적발): env를 xargs로 풀면 DSN의 공백에서 끊어져
# 비밀번호 없는 반쪽 DSN으로 접속 — PG 스위트가 전면 거짓 실패한다.
# 검증은 정렬된 PGPW로 DSN을 직접 조립해 통째로 전달한다(따옴표 보존).
sudo -u axp env AXP_DATA="$AXP_DATA" AXP_DB=postgres \
  AXP_PG_DSN="host=127.0.0.1 port=5432 user=axp password=${PGPW} dbname=axp" \
  python3 -m pytest -q core/tests | tail -1

echo "== 7/7 systemd 등록·기동 (웹·스케줄러·하트비트) =="
cp "$AXP_HOME/deploy/systemd/axp-web.service" /etc/systemd/system/
cp "$AXP_HOME/deploy/systemd/axp-scheduler.service" /etc/systemd/system/
cp "$AXP_HOME/deploy/systemd/axp-heartbeat.service" /etc/systemd/system/
cp "$AXP_HOME/deploy/systemd/axp-heartbeat.timer" /etc/systemd/system/
systemctl daemon-reload
# P7-I9와 동행 보강: 재설치(코드 갱신) 시에도 새 코드가 반드시 뜨도록
# enable --now(이미 떠 있으면 무시) 대신 enable + restart(멱등 재기동).
systemctl enable axp-web axp-scheduler axp-heartbeat.timer
systemctl restart axp-web axp-scheduler axp-heartbeat.timer
sleep 2
systemctl --no-pager -l status axp-web | head -5

echo
echo "완료. 초기 계정 비밀번호: ${AXP_DATA}/initial-credentials.txt (전달 후 삭제)"
echo "웹앱: http://127.0.0.1:8900  — 외부 공개는 Caddy(deploy/Caddyfile) 또는"
echo "      Cloudflare Tunnel(deploy/install-tunnel.sh — odooaierp.com 공개용)."
echo "체험 테넌트 운영은 docs/deploy-odooaierp.md 4장(크론 3종)을 따르세요:"
echo "  crontab 예시 → deploy/crontab.example"
