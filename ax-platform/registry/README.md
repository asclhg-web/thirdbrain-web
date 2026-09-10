# 스키마 레지스트리 (M0-3)

데이터 계약(규격서)의 단일 출처. Git으로 버전 관리한다.

## 규칙

1. `contracts/<이름>.yaml` — 테이블·특징셋마다 계약 하나 (양식: CONTRACT_TEMPLATE.yaml).
2. 변경은 PR로만 — 승인자: 현장 스튜어드 + 플랫폼 리드. 직접 push 금지.
3. 병합 시 버전을 올리고 change_log에 한 줄 남긴다.
4. 계약 없는 테이블은 품질 게이트(M2)가 거부한다 — "계약 우선" 원칙의 강제 지점.
5. 특징량(M2-3)도 계약이다 — kind: features 로 등록한다.

## 구성

```
contracts/           계약 본문 (YAML)
CONTRACT_TEMPLATE.yaml  양식
```

prod에서는 이 디렉터리를 사내 Git 원격에 미러링하고, PR 승인 규칙을
저장소 보호 설정으로 강제한다.
