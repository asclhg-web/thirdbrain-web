# 서드브레인 표준 개인 온톨로지 v2 — 삼각 모델 (KG-DMAIC v2)

v1(건강 7노드·6관계)에 **몸×학습×프로젝트 삼각**을 추가한 확장. 하위 호환 —
기존 노트·데이터는 그대로 동작한다.

## 추가된 것

| 구분 | v2 추가 | 의미 |
|---|---|---|
| 노드 | **Skill** (배움 주제) | 삼각의 '학습' 꼭짓점 — 요리, AI 활용, 라인댄스 스텝 |
| 노드 | **Project** (개인 프로젝트) | 삼각의 '프로젝트' 꼭짓점 — 발표회, 책 출간 |
| 관계 | **LEARNS** (Person→Skill) | 배우는 중 |
| 관계 | **WORKS_ON** (Person→Project) | 진행 중 |
| 관계 | **CONTRIBUTES_TO** (Activity→Skill/Project) | **일석삼조의 심장** — 한 활동이 여러 영역에 동시 기여 |

'몸' 영역은 노드가 아니라 Activity 자체의 속성으로 판정한다
(kind가 걷기·수면·운동 계열이거나 `body:` 속성이 있으면 몸 기여).

## 노트 작성법 (옵시디언)

```markdown
---                              ---                            ---
type: skill                      type: project                  type: activity
name: 라인댄스 스텝              name: 라인댄스 발표회           name: 라인댄스 연습
for: "[[아내]]"                  for: "[[아내]]"                 for: "[[아내]]"
status: learning                 status: active                  date: 2026-07-19
---                              due: 2026-10-01                 kind: 운동
                                 ---                             body: 운동 90분
                                                                 skills: "[[라인댄스 스텝]]"
                                                                 projects: "[[라인댄스 발표회]]"
                                                                 ---
```

활동 노트 하나가 몸(kind/body) + 학습(skills) + 프로젝트(projects)에 동시 기여
= **일석삼조 활동(Triple-Win Activity)**. skills/projects에 여러 개를 쉼표로 나열 가능.

## 대시보드

홈의 **🔺 삼각 밸런스** 카드: 최근 7일 활동의 영역별 기여 수 + 교차기여율
(2개 이상 영역에 기여한 활동 비율 — KG-DMAIC v2의 CTQ, 목표 30%↑).

## 측정 API

`store.triangle_week(person)` → `{total, 몸, 학습, 프로젝트, cross_rate}`
