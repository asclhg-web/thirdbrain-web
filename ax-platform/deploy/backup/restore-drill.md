# 복구 시험 절차서 (M0-2) — 분기 1회

목표: 백업이 "있는 것"이 아니라 "돌아오는 것"임을 분기마다 증명한다.
기록: 매 시험의 RTO(복구 소요)·RPO(유실 구간)를 아래 표에 남긴다.

## 절차 (스테이징 서버에서 — 운영 볼륨을 건드리지 않는다)

1. 최신 weekly + 이후 daily 백업 세트를 스테이징 서버로 복사.
2. `docker compose up -d postgres neo4j minio` (빈 볼륨).
3. 복원:
   ```bash
   docker compose exec -T postgres pg_restore -U axp -d axp --clean --if-exists < pg_<최신>.dump
   docker compose exec -T neo4j neo4j-admin database load neo4j --from-stdin < neo4j_<최신>.dump
   docker compose exec -T minio mc mirror <백업>/minio_raw local/raw
   ```
4. 검증 쿼리 3종:
   - 사실 테이블 6계열 행수가 백업 시점 품질 리포트와 일치.
   - 판단 카드·감사 로그 최신 건 시각 확인 → RPO 산출.
   - 근거 API 표본 1건 경로 반환 정상.
5. 소요 시간 기록 → RTO.
6. 결과를 자산 대장에 `restore-drill-<날짜>`로 등록.

## 판정

- 통과: RTO ≤ 4시간, RPO ≤ 24시간(daily 주기), 검증 3종 전부 정상.
- 실패 시: 원인·조치 후 2주 내 재시험. 미통과 상태로 분기를 넘기지 않는다.

## 시험 기록

| 일자 | 수행자 | RTO | RPO | 판정 | 비고 |
|---|---|---|---|---|---|
| (1회차 — 현장 배치 후 첫 달 내 수행) | | | | | |
