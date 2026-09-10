"""태성당 프로파일 적용 실행 — 구조는 실제, 거래는 합성(실데이터 대기).

실행: python -m demo.run_taesungdang
산출: customers/taesungdang/out/ (demo/out과 완전 분리)

실데이터 전환: docs/onboarding-taesungdang.md의 자료 요청서대로 원천이 준비되면
generate_data 호출을 M1 커넥터(odoo_cdc·excel_uploader·forms)로 바꾸는 것이
전환의 전부다 — 프로파일·계약·에이전트·게이트는 그대로 남는다.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ["AXP_PROFILE"] = "taesungdang"
os.environ.setdefault("AXP_DATA", str(ROOT / "customers" / "taesungdang" / "out"))

sys.path.insert(0, str(ROOT / "core"))
sys.path.insert(0, str(ROOT))

from demo import run_e2e  # noqa: E402

if __name__ == "__main__":
    run_e2e.main(fresh="--keep" not in sys.argv)
