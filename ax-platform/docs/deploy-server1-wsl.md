# 서버1(WSL2) 설치 절차 — Windows 겸용 장비 전용 (server-map.md 기준)

전제: Windows 11에 `wsl --install -d Ubuntu-24.04` 완료(재부팅 포함),
우분투 사용자 생성 완료. 아래 명령은 프롬프트로 구분한다 —
`PS>` = Windows PowerShell, `$` = 우분투(WSL) 안.

## 0. systemd 켜기 (WSL은 기본 꺼짐 — 딱 한 번)

```bash
$ printf '[boot]\nsystemd=true\n' | sudo tee /etc/wsl.conf
```
```powershell
PS> wsl --shutdown
PS> wsl        # 재진입
```
확인: `$ ps -p 1 -o comm=` → `systemd` 가 나와야 한다.

## 1. 저장소 내려받기

```bash
$ sudo apt-get update -q && sudo apt-get install -y git
$ git clone https://github.com/asclhg-web/thirdbrain-web.git ~/thirdbrain-web
$ cd ~/thirdbrain-web && git checkout claude/odoo-ai-erp-presentation-ymviq8
```
비공개 저장소이므로 로그인을 물으면: 사용자명 = GitHub 계정,
비밀번호 = GitHub Personal Access Token(설정 → Developer settings에서 발급).

## 2. 플랫폼 설치 (약 30분)

```bash
$ cd ~/thirdbrain-web/ax-platform
$ sudo bash deploy/install-app-server.sh
```
스크립트가 WSL을 감지해 systemd 미활성이면 안내 후 중단한다(0절 수행).
끝나면 초기 계정 파일 경로가 출력된다 — 보관.

## 3. 동작 확인 (서버1 안에서)

```bash
$ curl -s http://127.0.0.1:8900/health
```
`{"ok":true...}` 가 나오면 성공. Windows 브라우저에서 http://localhost:8900
을 열어 로그인 화면 확인(WSL2는 localhost가 자동 연결된다).

## 4. GPU 서버 연결 (선택 — server-map.md GPU 절 수행 후)

```bash
$ sudo nano /etc/axp/env      # 아래 두 줄 주석 해제·수정
  AXP_LLM=ollama
  AXP_OLLAMA_URL=http://192.168.0.5:11434
$ sudo systemctl restart axp-web axp-scheduler
```

## 5. 공개 (Cloudflare Tunnel — B6)

```bash
$ sudo bash deploy/install-tunnel.sh
```
중간에 나오는 URL을 브라우저로 열어 Cloudflare 로그인 → odooaierp.com 존
승인(= 서브도메인 3종 결정). 끝나면 휴대폰(사외망)에서
try.odooaierp.com 접속 확인.

## 6. 상시성 (겸용 장비 주의)

- Windows 전원 옵션에서 절전 해제(모니터 끄기만 허용).
- 재부팅 후에는 PowerShell에서 `wsl` 한 번 실행하면 systemd 서비스가
  올라온다. 무인 자동화가 필요하면 작업 스케줄러에 로그온 시
  `wsl -d Ubuntu-24.04 --exec /bin/true` 등록.
- 주식예측시스템과 겸용 — 재부팅은 안전 시간대에, 재부팅 후 주식시스템
  정상 가동을 먼저 확인.

## 문제가 생기면

각 단계의 화면 출력을 그대로 복사해 ASC 세션에 붙여넣는다 — 출력 기준으로
다음 한 줄을 정확히 안내한다.
