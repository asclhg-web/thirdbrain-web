#!/usr/bin/env bash
# P9-2: apex(odooaierp.com)=메인 플랫폼 원스텝 반영 — 서버1에서 1회 실행.
#   ① 최신 코드 반영(웹앱 재설치: 메인 랜딩 / + 데모 /demo)
#   ② 터널 재구성(apex·www·app·try·status → 127.0.0.1:8900)
# 사용: cd ~/thirdbrain-web && git pull && sudo bash ax-platform/deploy/apex-golive.sh
#
# ⚠ Cloudflare 대시보드 사전 조건(대표님 1회, 계정 소유자만 가능):
#    odooaierp.com 존 → DNS 에서 apex(@)가 Netlify를 가리키던 A/CNAME 레코드를
#    삭제하세요. 그래야 아래 터널 route가 apex를 잡습니다(충돌 방지).
#    데모는 이제 웹앱이 /demo 로 직접 서빙하므로 Netlify 이전은 불필요합니다.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

echo "════════ 1/2 웹앱 재설치 (메인 랜딩 / + 데모 /demo) ════════"
bash "${HERE}/install-app-server.sh"

echo
echo "════════ 2/2 터널 재구성 (apex=메인 플랫폼) ════════"
bash "${HERE}/install-tunnel.sh"

echo
echo "════════ 확인 ════════"
sleep 2
echo -n "  로컬 웹앱  : "; curl -s http://127.0.0.1:8900/health || echo "(응답 없음)"
echo
echo -n "  apex 공개  : "; curl -s https://odooaierp.com/health || echo "(아직 — Cloudflare apex 레코드 정리/전파 대기)"
echo
echo "브라우저에서 https://odooaierp.com → 메인 랜딩('제안은 AI가, 결정은 사람이')"
echo "상단 [데모 보기] → https://odooaierp.com/demo (승인함 체험)"
echo "apex가 아직 옛 데모면: Cloudflare에서 apex의 Netlify 레코드 삭제 후 재실행."
