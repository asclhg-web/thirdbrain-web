# 피지컬브레인 (Physical Brain) v0.1

온톨로지 지식그래프로 '나'를 아는 개인 건강 비서 — 1차(로컬 앱) 구현.

## 빠른 시작

```bash
cd physical-brain
pip install -r requirements.txt
make init      # 그래프 초기화 + 샘플 볼트 시드 + 30일 목업 데이터
make dev       # 서버 실행 → http://localhost:8800
make test      # 전체 테스트
make demo      # 가상 하루 가속 데모 (아침 브리핑→복약→저녁 리포트)
```

## 구조

```
server/     FastAPI 백엔드 (사서·안전망·브리핑·오케스트레이터·알림·리포트)
web/        대시보드 템플릿 (Jinja2+HTMX, 서버렌더)
graph/      온톨로지 v1 스키마·저장소·샘플 볼트·시더
pipelines/  볼트 동기화·건강 목업·CSV 인제스트
robot/      로봇 어댑터 (2차, 현재 시뮬레이션 스텁)
tests/      pytest (가상 하루 시뮬레이터 포함)
```

## 그래프 저장소에 대하여

기본 저장소는 **SQLite 기반 GraphStore**(파일 하나, 설치 불필요)이며, 온톨로지 v1의
노드/관계 모델을 그대로 구현한다. Neo4j로의 승격은 `GRAPH_BACKEND=neo4j` 환경변수와
`docker-compose.yml`(동봉)로 준비되어 있다 — 저장소 인터페이스가 동일하므로 앱 코드는
변경 없다. (개발 컨테이너에 도커 데몬이 없어 1차는 SQLite로 검증함)

## 원칙

- 로컬 퍼스트: 건강 데이터는 외부로 전송하지 않는다 (텔레그램 알림은 명시적 opt-in).
- 진실의 원본은 볼트: 지식 수정은 마크다운 노트에서만, 그래프는 거울.
- 미확인은 미확인으로 기록: 결측·무응답을 0이나 완료로 뭉개지 않는다.
- AI 4대 금지: 진단·처방·응급판단·불안조장 (`server/llm.py:LIBRARIAN_SYSTEM`).

## 환경변수 (.env.example 참고)

| 키 | 기본 | 설명 |
| --- | --- | --- |
| PB_DB | data/brain.db | SQLite 경로 |
| LLM_BASE_URL | http://localhost:11434 | Ollama 주소 (2차: GPU 서버 URL로 교체) |
| LLM_MODEL | (경량모델) | 없으면 규칙 기반 폴백으로 동작 |
| TELEGRAM_TOKEN / TELEGRAM_CHAT_* | 없음 | 없으면 dry-run(파일 로그) 모드 |
