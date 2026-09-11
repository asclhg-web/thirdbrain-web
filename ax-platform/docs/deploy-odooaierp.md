# odooaierp.com 웹앱 공개 가이드 — 보유 서버 + Cloudflare Tunnel (P4-7)

> 사용자 결정(2026-09-11): 체험 서버는 **보유 서버**, 체험 신청은 **초기 승인제**.
> 이 가이드는 그 결정에 맞춘 실행 순서다. 소요: 처음부터 약 반나절.

## 0. 준비물

- 보유 앱 서버(Ubuntu 22.04+/Debian 12+), 인터넷 아웃바운드 가능(인바운드 개방 불필요)
- Cloudflare 계정 로그인 정보 — odooaierp.com 존이 보이는 계정(asc.kr과 동일)
- 이 저장소 체크아웃: `/opt/ax-platform` 권장

## 1. 플랫폼 스택 설치 (이미 했다면 건너뜀)

```bash
cd /opt/ax-platform && sudo bash deploy/install-app-server.sh
# → PG16 + axp-web.service(8900) + axp-scheduler.service 가동
```

## 2. 체험 테넌트 생성 (합성 데이터 — 실데이터 아님)

```bash
cd /opt/ax-platform/core
python3 -m axp.cli tenant create trial-demo --company "체험"
# 출력의 initial-credentials.txt 에 체험 계정 비밀번호가 있다 (0600)
```

`/etc/axp/axp.env` 에 웹앱 데이터 루트를 체험 테넌트로 지정:

```
AXP_DATA=/opt/ax-platform/tenants/trial-demo/out
AXP_SECRET=<긴 무작위 문자열>
```

`sudo systemctl restart axp-web` 후 `curl -s localhost:8900/health` → `{"ok": true}`.

## 3. Cloudflare Tunnel 결선

```bash
sudo bash deploy/install-tunnel.sh
# 중간에 나오는 URL을 브라우저로 열어 Cloudflare 로그인 → odooaierp.com 존 선택
```

스크립트가 하는 일: cloudflared 설치 → 터널 `axp` 생성 →
try/app/status.odooaierp.com DNS 자동 등록 → systemd 상시 기동.
**공인 IP·방화벽 인바운드 개방이 필요 없다** — 서버가 Cloudflare로
아웃바운드 연결을 유지하고, TLS·DDoS 방어는 Cloudflare가 앞단에서 한다.

확인:

```bash
curl -s https://try.odooaierp.com/health     # {"ok": true}
curl -s https://status.odooaierp.com/status | grep 정상
```

## 4. 운영 크론 3종

```cron
# 체험 데이터 매일 0시 리셋 (KST 0시 = UTC 15시)
0 15 * * * cd /opt/ax-platform/core && python3 -m axp.cli tenant reset trial-demo
# 체험 업로드 파일 24시간 시효 파기 (정직 조항)
0 * * * * cd /opt/ax-platform/core && python3 -m axp.cli tenant purge-uploads trial-demo
# 하트비트는 systemd 타이머로:
#   sudo cp deploy/systemd/axp-heartbeat.* /etc/systemd/system/
#   sudo systemctl enable --now axp-heartbeat.timer
```

알림 채널(텔레그램/웹훅)은 `/etc/axp/axp.env` 의 AXP_NOTIFY_* 값으로 —
다운 감지·복구가 휴대폰으로 온다(5분 주기, 연속 2회 실패 시 1회 발화).

## 5. 체험 신청 — 초기 승인제 흐름

1. 랜딩(odooaierp.com)의 '체험 신청' 폼(P4-5)에서 회사·이메일 접수
2. 관리자가 확인 후: `tenant create <고객명>` → credentials 파일의 계정을
   이메일로 안내 (승인제 — 사용자 결정 ③)
3. 고객은 try.odooaierp.com 에 로그인 — 헤더에 '체험판 · 합성 데이터' 상시 표시
4. 고객이 자기 엑셀/POS 파일을 '자료 반입'에서 올려 보면(24h 후 자동 파기)
   자기 데이터 기준 브리핑을 체험

## 6. 문제가 생기면

- `systemctl status cloudflared axp-web` / `journalctl -u cloudflared -n 50`
- Tunnel은 살아 있는데 502: axp-web이 죽은 것 — heartbeat 경보 확인
- DNS가 안 잡히면 Cloudflare 대시보드 → odooaierp.com → DNS에서
  try/app/status CNAME(터널 ID) 존재 확인
- 롤백: `cloudflared tunnel route dns` 로 만든 CNAME 삭제 + `systemctl stop cloudflared`
  — 기존 정적 사이트(odooaierp.com/www)는 영향 없다(Workers 그대로).
