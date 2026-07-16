# 1차(T01~T20) 완료 체크리스트 — 2026-07-16 기준

| 태스크 | 완료 기준 | 상태 | 증빙 |
| --- | --- | --- | --- |
| T01 뼈대 | /health 응답 | ✅ | 스모크 테스트 `{"status":"ok"}` |
| T02 스키마 | 노드7·관계6 + 제약 | ✅ | graph/schema.py, 스키마 위반 테스트 |
| T03 샘플 볼트 | 사람2·약3·규칙3·장소4 | ✅ | 시드 결과 edges=6 |
| T04 볼트 동기화 | 수정→갱신, 삭제→archived | ✅ | test_incremental_sync_and_archive |
| T05 목업 | 30일 + 결측 10% 보존 | ✅ | made 491 / missing 21 |
| T06 인제스트 | CSV→그래프, 실패 격리 | ✅ | test_ingest_ok_and_failed |
| T07 오늘의 약 | 규칙→태스크 전개·상태 전이 | ✅ | 데모: 07:00 announce |
| T08 이벤트 | 미확인은 미확인으로 기록 | ✅ | test_scenario_a_unconfirmed_honest |
| T09 LLM 계층 | 폴백으로 오프라인 동작 | ✅ | LLM_MODEL 없이 전 테스트 통과 |
| T10 사서 | 혈압 추세 정답 + 금지영역 차단 | ✅ | test_librarian_* (수치=조회값) |
| T11 안전망 | 긴급 고정문구·주의·이중 기록 | ✅ | test_safety_layers |
| T12 브리핑 | 07:00 생성·기록 | ✅ | outbox 표본 |
| T13 알림 | 텔레그램/dry-run + 보호자 라우팅 | ✅ | outbox: guardian 미확인 알림 |
| T14 오케스트레이터 | YAML 규칙 구동 | ✅ | rules/*.yaml 4종 |
| T15 시나리오 | 가상 하루 가속 전이 검증 | ✅ | test_scenarios.py 4건 |
| T16 주간 리포트 | 리포트+전화할 거리 | ✅ | report.py guardian_version |
| T17 대시보드 | 30일 차트·결측 끊긴 선 | ✅ | /signals (결측일 표시) |
| T18 그래프 뷰어 | 읽기 전용·측정값 축약 | ✅ | /graphview |
| T19 시나리오 편집기 | 시각·on/off만 편집 | ✅ | /scenarios POST |
| T20 통합 데모 | 무인 하루 완주 | ✅ | make demo 로그 |

**테스트: 18 passed** · 실행: `make init && make dev` → http://localhost:8800

## 알려진 한계 (2차 및 실기기 단계로 이월)

1. 그래프 저장소: 개발 컨테이너에 도커 데몬이 없어 **SQLite 백엔드로 검증** — Neo4j는 동일 인터페이스로 준비됨(docker-compose 동봉, 사용자 PC에서 `make up`).
2. LLM: 컨테이너에 Ollama 없음 → **규칙 기반 폴백으로 전 기능 동작 확인**. 모델 연결 시 문장 품질만 향상(T22에서 GPU 승격).
3. 텔레그램: 토큰 미설정 시 dry-run(outbox.log) — 실폰 수신은 .env 설정만 하면 됨.
4. 로봇: RobotStub(시뮬레이션) — T25에서 MQTT 어댑터로 교체(동일 인터페이스).
5. 실기기 데이터: 헬스 커넥트 실시간 연동은 실기기 단계(WBS-2)로.
