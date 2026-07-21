# -*- coding: utf-8 -*-
"""T28 — 실볼트 초기 생성기: 노트 생성 + .env의 VAULT_PATH 등록까지 한 번에.

사용: python scripts\\make_vault.py            (기본: 문서\\피지컬브레인)
     python scripts\\make_vault.py --dir "다른 경로"

생성되는 약 노트는 예시값이다 — 이름·시간·주의는 옵시디언(또는 메모장)에서
본인 것으로 고치면 5분 내 자동 반영된다(진실의 원본은 볼트).
"""
import argparse
import io
import os

NOTES = {
    "나.md": """---
type: person
name: 나
---
피지컬브레인의 주 사용자.
""",
    "약_혈압약.md": """---
type: medication
name: 혈압약(암로디핀)
for: "[[나]]"
rule_time: "08:00"
rule_condition: 아침 식후
rule_caution: 자몽주스 금지
---
""",
    "약_오메가3.md": """---
type: medication
name: 오메가3
for: "[[나]]"
rule_time: "08:30"
rule_condition: 아침 식후
---
""",
    "약_고지혈증약.md": """---
type: medication
name: 고지혈증약
for: "[[나]]"
rule_time: "21:00"
rule_condition: 저녁 식후
---
""",
    "측정_예시_혈당.md": """---
type: measure
name: 혈당
key: glucose
unit: mg/dL
warn: 180
emergency: 300
---
몸 마스터 확장 예시 — 이 노트 하나로 새 측정 유형(그래프·안전망)이 생깁니다.
key는 데이터의 type 값과 일치해야 합니다 (CSV·인박스의 type 컬럼).
""",
    # ── v2 삼각(몸×학습×프로젝트) 예시 — 이름·내용을 본인 것으로 수정 ──
    "학습_AI활용.md": """---
type: skill
name: AI 활용
for: "[[나]]"
status: learning
---
유튜브로 제미나이·챗GPT 배우는 중.
""",
    "프로젝트_내프로젝트.md": """---
type: project
name: 내 프로젝트
for: "[[나]]"
status: active
---
예: 라인댄스 발표회, 책 출간 — 본인 프로젝트로 수정하세요.
""",
    "활동_예시_라인댄스연습.md": """---
type: activity
name: 라인댄스 연습 (예시)
for: "[[나]]"
date: 2026-07-19
kind: 운동
body: 운동 90분
skills: "[[AI 활용]]"
projects: "[[내 프로젝트]]"
---
일석삼조 활동 예시: 한 활동이 몸(kind/body)·학습(skills)·프로젝트(projects)에 동시 기여.
활동한 날마다 이런 노트를 남기면 홈의 '삼각 밸런스'에 집계됩니다.
""",
}


def main():
    ap = argparse.ArgumentParser()
    default_dir = os.path.join(os.path.expanduser("~"), "Documents", "피지컬브레인")
    ap.add_argument("--dir", default=default_dir)
    args = ap.parse_args()

    os.makedirs(args.dir, exist_ok=True)
    made = 0
    for fn, text in NOTES.items():
        path = os.path.join(args.dir, fn)
        if os.path.exists(path):
            print("건너뜀(이미 있음):", fn)
            continue
        with io.open(path, "w", encoding="utf-8") as f:
            f.write(text)
        made += 1
        print("생성:", fn)

    # .env의 VAULT_PATH 등록 (앱 루트 기준)
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    if os.path.exists(env_path):
        s = io.open(env_path, encoding="utf-8-sig").read()
        lines = []
        replaced = False
        for line in s.splitlines():
            if line.startswith("VAULT_PATH="):
                lines.append(f"VAULT_PATH={args.dir}")
                replaced = True
            else:
                lines.append(line)
        if not replaced:
            lines.append(f"VAULT_PATH={args.dir}")
        io.open(env_path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print("VAULT_PATH 등록:", args.dir)
    print(f"완료 — 노트 {made}개 생성. 서버를 재시작하면 반영됩니다.")


if __name__ == "__main__":
    main()
