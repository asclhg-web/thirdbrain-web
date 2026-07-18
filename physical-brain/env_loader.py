"""'.env' 로더 (의존성 0) — graph/server/robot 패키지 import 시 자동 실행.

원칙: 이미 설정된 환경변수는 절대 덮어쓰지 않는다(셸/테스트 설정이 우선).
빈 값(KEY=)은 건너뛴다 — 코드의 기본값을 살리기 위해.
"""
import os

_loaded = False


def load(path: str | None = None) -> None:
    global _loaded
    if _loaded:
        return
    _loaded = True
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            # 인라인 주석 제거(값 안에 '#'가 공백과 함께 올 때만) + 따옴표 벗기기
            if " #" in val:
                val = val.split(" #", 1)[0]
            val = val.strip().strip('"').strip("'")
            if key and val:
                os.environ.setdefault(key, val)
