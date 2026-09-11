# 태성당 데모 상태 스냅샷 복원 (9/14 데모 보험)

`demo-snapshot-20260911.tar.gz` 는 9/14 1차 데모용 실행 상태의 압축 보존본이다
(합성 데이터 · 대기 판단 카드 #42·43·44·46·47 포함, 원본 out/은 .gitignore).

복원:
```bash
cd ax-platform/customers/taesungdang
tar -xzf demo-snapshot-20260911.tar.gz     # → out/ 생성
cd ../../core
AXP_DATA=$(pwd)/../customers/taesungdang/out AXP_DB=sqlite \
  python3 -m uvicorn axp.webapp:app --port 8900
```
계정: out/ 상태에 포함(테넌트로 새로 발급하려면 tenant create 사용).
