# 서드브레인 표준 개인 온톨로지 v1 (자동 생성)

## 노드
- **Person**
- **Medication**
- **Regimen**
- **Measurement**
- **Activity**
- **Event**
- **Place**

## 관계
- **TAKES**: Person → Medication
- **HAS_RULE**: Medication → Regimen
- **MEASURED**: Person → Measurement
- **PERFORMED**: Person → Activity
- **OCCURRED**: Person → Event
- **RELATES_TO**: 자유 연결
