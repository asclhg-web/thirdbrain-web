#!/usr/bin/env bash
# P4-7: Cloudflare Tunnel 결선 — 보유 앱 서버에서 실행 (사용자 결정: 보유 서버)
#
# 전제: ① 이 서버에 axp-web이 127.0.0.1:8900으로 떠 있다(axp-web.service)
#       ② Cloudflare 계정이 odooaierp.com 존을 관리한다(asc.kr과 같은 계정)
# 결과(메인=플랫폼): odooaierp.com(=apex, 메인)·www·app(고객)·try(체험)·
#       status(상태) 가 이 서버의 웹앱으로 연결된다. 공인 IP·포트 개방 불필요.
#       데모(정적 Netlify 사이트)는 서브 demo.odooaierp.com 으로 옮긴다.
#
# ⚠ apex(odooaierp.com) 사전 조건 — Cloudflare DNS에서 apex가 Netlify를
#    가리키던 기존 레코드(A/CNAME)를 먼저 지워야 이 스크립트의 route dns가
#    apex를 터널로 연결할 수 있다. 데모는 Netlify 커스텀 도메인을
#    demo.odooaierp.com 으로 바꾸고, Cloudflare에 demo CNAME→Netlify를 둔다.
#
# 사용: sudo bash install-tunnel.sh
#       (중간에 브라우저 로그인 URL이 나오면 Cloudflare 계정으로 승인)
set -euo pipefail

TUNNEL_NAME="${TUNNEL_NAME:-axp}"
ZONE="${ZONE:-odooaierp.com}"
LOCAL="${LOCAL:-http://127.0.0.1:8900}"

echo "── 1/5 cloudflared 설치"
if ! command -v cloudflared >/dev/null; then
  # 공식 저장소 (Debian/Ubuntu)
  mkdir -p --mode=0755 /usr/share/keyrings
  curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg \
    | tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
  echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main" \
    | tee /etc/apt/sources.list.d/cloudflared.list
  apt-get update -qq && apt-get install -y cloudflared
fi
cloudflared --version

echo "── 2/5 Cloudflare 로그인 (브라우저 승인 — ${ZONE} 존 선택)"
if [ ! -f /root/.cloudflared/cert.pem ]; then
  cloudflared tunnel login || true
  # P7-I10(서버1 실측): WSL에서 인증서 자동 전달이 'Failed to fetch
  # resource'로 실패하는 사례 — 승인만 됐다면 브라우저가 cert.pem을
  # 내려받으므로 Windows 다운로드 폴더에서 자동 회수한다.
  if [ ! -f /root/.cloudflared/cert.pem ]; then
    F=$(ls -t /mnt/c/Users/*/Downloads/cert*.pem 2>/dev/null | head -1)
    if [ -n "$F" ]; then
      mkdir -p /root/.cloudflared && cp "$F" /root/.cloudflared/cert.pem
      echo "  자동 회수: $F → /root/.cloudflared/cert.pem"
    else
      echo "!! 인증서가 없습니다 — 화면의 URL을 브라우저로 열어 로그인하고"
      echo "   도메인(${ZONE})을 클릭·선택한 뒤 파란 Authorize(권한 부여)"
      echo "   버튼까지 눌러야 합니다. URL은 몇 분이면 만료 — 완료 후 재실행."
      exit 1
    fi
  fi
fi

echo "── 3/5 터널 생성: ${TUNNEL_NAME}"
cloudflared tunnel list | grep -q " ${TUNNEL_NAME} " || cloudflared tunnel create "${TUNNEL_NAME}"
TUNNEL_ID=$(cloudflared tunnel list | awk -v t="${TUNNEL_NAME}" '$2==t {print $1}')
echo "   tunnel id: ${TUNNEL_ID}"

echo "── 4/5 구성 파일 + DNS 라우트"
mkdir -p /etc/cloudflared
cat > /etc/cloudflared/config.yml <<EOF
tunnel: ${TUNNEL_ID}
credentials-file: /root/.cloudflared/${TUNNEL_ID}.json
ingress:
  # 메인 = 실제 AX 플랫폼 (apex + www)
  - hostname: ${ZONE}
    service: ${LOCAL}
  - hostname: www.${ZONE}
    service: ${LOCAL}
  # 고객·체험 별칭 (같은 플랫폼)
  - hostname: app.${ZONE}
    service: ${LOCAL}
  - hostname: try.${ZONE}
    service: ${LOCAL}
  # 상태 페이지
  - hostname: status.${ZONE}
    service: ${LOCAL}
    path: ^/status.*|^/health$
  - service: http_status:404
EOF
# apex는 CNAME 플래트닝으로 터널에 붙는다. apex에 Netlify 잔여 레코드가
# 남아 있으면 route dns가 실패하므로, 실패해도 나머지는 계속 진행(|| true).
for host in "${ZONE}" "www.${ZONE}" "app.${ZONE}" "try.${ZONE}" "status.${ZONE}"; do
  cloudflared tunnel route dns "${TUNNEL_NAME}" "${host}" \
    || echo "  !! route dns 실패: ${host} — Cloudflare DNS에서 기존(Netlify) 레코드 제거 후 재실행"
done

echo "── 5/5 systemd 상시 기동"
cloudflared service install 2>/dev/null || true
systemctl enable --now cloudflared
sleep 3
systemctl --no-pager --lines=5 status cloudflared || true

echo
echo "완료 — 확인 (메인=플랫폼):"
echo "  curl -s https://${ZONE}/health       → {\"ok\": true}   (apex=플랫폼)"
echo "  브라우저: https://${ZONE}  → P9 로그인 화면이 떠야 함"
echo "  curl -s https://status.${ZONE}/status | grep 정상"
echo
echo "데모(서브)는 Netlify에서 커스텀 도메인을 demo.${ZONE} 으로 바꾸고,"
echo "Cloudflare DNS에 demo CNAME→<네 사이트>.netlify.app 를 추가하세요."
echo "주의: 체험 테넌트는 tenant create 로 만들고, axp-web의 AXP_DATA를"
echo "      해당 테넌트로 지정하세요. 매일 0시 리셋은 크론에:"
echo "      0 0 * * * cd /opt/ax-platform/core && python3 -m axp.cli tenant reset trial-demo"
echo "      0 * * * * cd /opt/ax-platform/core && python3 -m axp.cli tenant purge-uploads trial-demo"
