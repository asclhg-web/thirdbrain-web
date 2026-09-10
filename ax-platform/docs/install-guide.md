# 설치 가이드

## A. demo 모드 (개발·검증·교육 — 외부 서비스 불필요)

```bash
cd ax-platform
pip install pandas numpy scikit-learn pyyaml networkx matplotlib openpyxl fastapi uvicorn pytest
python -m demo.generate_data     # 합성 데이터 24개월
python -m demo.run_e2e           # M0→M7 수직 완주 (~1.5분)
python -m demo.acceptance        # G4 6영역 자동 점검
python -m pytest core/tests -q   # 단위 시험 19건
uvicorn axp.api:app --app-dir core --port 8000   # API·War Room
```

산출물: `demo/out/` — odoo.db(합성 원장), axp.db(스테이징·표준·운영),
raw/(원본 보존), artifacts/(EDA·브리핑·보드·모델·그래프 내보내기·수용 결과).

## B. prod 모드 (현장 배치)

`deploy/runbook.md`를 따른다 — 요약:
1. `deploy/.env` + secrets 4파일 + 사내 인증서 준비
2. `docker compose up -d` → 전 서비스 healthy
3. 초기화: 스키마 적용 · Keycloak 역할 6종(auth-roles.md) · MinIO 버킷 · Ollama 모델
4. Odoo 원장 서버에 `core/axp/ingest/odoo_cdc_prod.sql` — 논리 복제 발행/구독
5. 지식그래프 이관: `store.export_cypher()` 산출물을 cypher-shell로 적재
6. 검증 체크리스트 + 백업 1회 + (첫 달 내) 복구 리허설

### demo → prod 로 바뀌는 것

| 구성요소 | demo | prod |
|---|---|---|
| 저장소 | SQLite 단일 파일 | PostgreSQL + MinIO |
| CDC | 증분 폴링(합성 odoo.db) | 논리 복제(WAL) |
| 그래프 | SQLite 트리플+networkx | Neo4j (Cypher 이관) |
| LLM | 결정적 조립기 | Ollama(+GraphRAG), 폴백은 게이트 경유 |
| 실험추적 | 자체 카드 레지스트리 | MLflow 어댑터(카드 규격 동일) |
| 승인함 | API/CLI | Odoo 화면 내장 모듈 |
| 경보 | 테이블+stdout | 사내 메신저 webhook |

코어 로직·규율(카드 검증·인용 강제·게이트·확신도 루프)은 두 모드에서 같다.
