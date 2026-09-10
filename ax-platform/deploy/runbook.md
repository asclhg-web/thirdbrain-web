# 배포 Runbook (M0-1)

신규 서버에서 0부터 기동까지. 이 문서만 보고 제3자가 재배포할 수 있어야 한다.

## 0. 전제

- Ubuntu 22.04+ / RHEL 9+, Docker Engine 26+, Docker Compose v2.
- 서버 사양(권장): 16 vCPU · 64GB RAM · SSD 1TB · (선택) GPU 1장(Ollama·딥러닝).
- 사내 DNS에 `AXP_DOMAIN` 등록, 사내 CA로 서버 인증서 발급.

## 1. 준비

```bash
git clone <사내 미러>/ax-platform && cd ax-platform/deploy
cp .env.example .env                  # 값 채우기
mkdir -p secrets certs
# secrets 4파일 생성(각 한 줄): pg_password, minio_password, superset_key, kc_password
#   openssl rand -base64 24 > secrets/pg_password   식으로 생성
# certs/axp.crt, certs/axp.key — 사내 CA 발급본 배치
chmod 600 secrets/* certs/axp.key
```

## 2. 기동

```bash
docker compose pull
docker compose up -d
docker compose ps          # 전 서비스 healthy 확인 (postgres·minio·neo4j 우선)
```

기동 순서는 compose의 `depends_on`이 강제한다: postgres → (mlflow·keycloak·superset) → axp-api.

## 3. 초기화 (첫 기동 시 1회)

```bash
# 3-1 데이터베이스 스키마 (M2 표준 데이터셋 + 운영 테이블)
docker compose exec axp-api python -m axp.dataset.schema --apply
# 3-2 Keycloak realm·역할 (auth-roles.md의 매트릭스대로)
#     /auth 콘솔에서 realm 'axp' 생성 → 역할 6종 → 그룹 매핑
# 3-3 MinIO 버킷: raw(원본), parquet, mlflow
# 3-4 Ollama 모델 적재(반출 게이트 승인 후 오프라인 반입 권장)
docker compose exec ollama ollama pull <선정 모델>
# 3-5 스키마 레지스트리 원격 등록: registry/ 를 사내 Git에 push
```

## 4. 검증 체크리스트

- [ ] `docker compose ps` 전 서비스 healthy
- [ ] https://AXP_DOMAIN 접속 → SSO 로그인 → War Room 빈 화면
- [ ] `python -m demo.run_e2e --mode prod --smoke` 스모크 통과
- [ ] 서버 재부팅 → 전 서비스 자동 복구
- [ ] backup/backup.sh 수동 1회 → 3본 생성 확인

## 5. 장애 시 재기동

```bash
docker compose logs --tail=100 <service>   # 원인 확인
docker compose restart <service>           # 단일 서비스
docker compose down && docker compose up -d   # 전체 (데이터는 볼륨에 보존)
```

PostgreSQL 볼륨 손상 시: backup/restore.sh (restore-drill.md 절차) — 임의 복구 금지,
반드시 절차서대로. 복구 후 정합 배치(M1) 1회 수동 실행으로 원장 대비 확인.

## 6. 금지

- core 망 컨테이너에 포트 직접 노출 금지(프록시 경유만).
- secrets 파일의 Git 커밋 금지(.gitignore 등록됨).
- `latest` 태그 사용 금지 — 버전 갱신은 compose 파일 수정 + 변경 로그로.
