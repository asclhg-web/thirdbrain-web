# 서버 정의서 — ASC 운영 장비 지도 (2026-09-12 확정)

대표 확인으로 확정된 정의. 5단계 B목록·배포 가이드는 이 지도를 기준으로 읽는다.

| 이름 | 위치/IP | OS | 역할 | 비고 |
|---|---|---|---|---|
| **서버1** | 사내 LAN 192.168.0.46 | Windows | AX 플랫폼 서버 + 관리 창구 **겸용** | 주식예측시스템 상주. Tailscale 설치됨 |
| **GPU 서버** | 사내 LAN 192.168.0.5 | Windows | Ollama(LLM 서술)·GPU 연산 | 주식예측시스템과 GPU 공유 |
| 클라우드 컨테이너 | Anthropic (임시) | Linux | ASC 세션의 개발·검증 전용 | 대표 LAN과 분리 — 산출물은 전부 git |
| odooaierp.com | Cloudflare | — | 랜딩(정적) + Tunnel 진입점 | try/app/status 서브도메인 예정 |

## 서버1이 Windows인 데 따른 설치 방식 (결정)

- 우분투 전용 설치 스크립트는 **WSL2(Ubuntu 24.04) 안에서** 실행한다 —
  기존 Windows 프로그램(주식예측시스템)은 건드리지 않는다.
- 플랫폼 PG16은 WSL 내부 전용(Windows 측 5432와 충돌하지 않음).
- 외부 공개는 Cloudflare Tunnel(아웃바운드 전용) — 방화벽 인바운드 불필요.
- WSL 상시성: Windows 재부팅 시 자동 기동 설정 필요(설치 절차에 포함),
  PC 절전은 꺼 둔다. **파일럿·체험 단계 한정** — 유료 고객 단계(6단계)에
  전용 장비 분리.

## GPU 서버 (Windows) — Ollama

- ollama.com Windows 설치 → `ollama pull qwen2.5:14b-instruct`
- LAN 공개: 시스템 환경변수 `OLLAMA_HOST=0.0.0.0` + 방화벽 11434 인바운드 허용
- 플랫폼 연결: 서버1의 `/etc/axp/env`(WSL 내)에
  `AXP_LLM=ollama`, `AXP_OLLAMA_URL=http://192.168.0.5:11434`
- 주식예측시스템과 VRAM 공유 — 공존은 가능 전제이나 첫 가동 주간에 실측 확인.

## 자원 공유 주의

- AX 야간 배치(새벽)와 주식시스템의 무거운 시간대가 겹치지 않는지 확인.
- 서버1 디스크: 플랫폼 데이터 루트는 WSL 내 /var/lib/axp — Windows C: 용량과 공유.

## 관리 경로

- 평시: 서버1에서 직접(같은 장비). 외부에서: Tailscale로 서버1 접속.
- 이 문서의 IP는 사내 사설 대역 — 변경 시 이 문서를 갱신하고 커밋한다.
