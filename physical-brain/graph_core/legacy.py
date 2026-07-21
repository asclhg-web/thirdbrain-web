"""유산 패키지 (G-Legacy) — 헌장 제1원칙의 코드화: 언제 멈춰도 선물이 되도록.

build_package(): 모든 프로필 DB(안전 백업) + 볼트(마크다운) + 설정 + '받는 이에게'
안내문 + 목록(manifest)을 zip 하나로 묶는다 — 이동·상속 가능한 단위.
verify_package(): 상속 리허설 — 패키지를 열어 복원 가능성을 검증한다.
"""
import json
import os
import sqlite3
import zipfile
from datetime import datetime

from graph_core import profiles, store

README_TEMPLATE = """# 받는 이에게 — 이 꾸러미에 대하여

이것은 한 사람이 살아 있는 동안 매일 길러 온 지식그래프입니다.
숫자와 기록처럼 보이지만, 실은 그 사람이 세상을 어떻게 돌보고,
무엇을 배우고, 무엇을 만들고, 어떤 마음으로 하루를 건넜는지의 지도입니다.

## 원칙 (만든 사람의 약속)

1. 여기 담긴 것은 전부 실제 기록입니다 — 지어낸 것이 없습니다.
2. 받을지, 열지, 지울지는 전적으로 당신의 선택입니다.
3. 이것은 끝난 기록이 아니라 살아 있는 시스템입니다 — 당신이 이어서
   기록하면 그래프는 2대째 성장을 계속합니다.

## 여는 방법

1. https://github.com/asclhg-web/thirdbrain-web 의 physical-brain 폴더 설치
   (scripts/windows/setup.ps1 — 30분)
2. 이 꾸러미의 dbs/ 안 DB 파일을 data/ 폴더에, vault/ 폴더를 옵시디언 보관함으로
3. 앱을 켜면 사서에게 물어볼 수 있습니다 — 사서는 기록에 있는 것만,
   출처와 함께 답합니다.

## 이 꾸러미의 내용

{inventory}

만든 날: {created}
"""


def _legacy_dir() -> str:
    base = os.path.dirname(os.path.abspath(store.db_path()))
    d = os.path.join(base, "legacy")
    os.makedirs(d, exist_ok=True)
    return d


def _backup_db(src_path: str, dst_path: str) -> None:
    """쓰는 중에도 안전한 SQLite 백업."""
    src = sqlite3.connect(src_path)
    dst = sqlite3.connect(dst_path)
    with dst:
        src.backup(dst)
    src.close()
    dst.close()


def build_package(vault: str | None = None, now: datetime | None = None) -> str:
    now = now or datetime.now()
    out = os.path.join(_legacy_dir(), f"legacy_{now.strftime('%Y%m%d_%H%M')}.zip")
    inv_lines, manifest = [], {"created_at": now.isoformat(), "profiles": [], "vault_files": 0}

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        # ① 프로필별 그래프 DB (안전 백업)
        for pr in profiles.list_profiles():
            db = pr["db"] or store.db_path()
            if not os.path.exists(db):
                continue
            tmp = db + ".legacy_tmp"
            _backup_db(db, tmp)
            z.write(tmp, f"dbs/{pr['id']}.db")
            os.remove(tmp)
            conn = sqlite3.connect(db)
            n = conn.execute("SELECT COUNT(*) FROM nodes WHERE archived=0").fetchone()[0]
            conn.close()
            manifest["profiles"].append({"id": pr["id"], "name": pr["name"],
                                         "kind": pr["kind"], "nodes": n})
            inv_lines.append(f"- 프로필 '{pr['name']}'({pr['kind']}): 노드 {n}개")
        # ② 프로필 레지스트리
        reg = profiles._registry_path()
        if os.path.exists(reg):
            z.write(reg, "profiles.json")
        # ③ 볼트 (마크다운 원본 — 30년 뒤에도 열리는 형식)
        vault = vault or os.environ.get("VAULT_PATH", "")
        if vault and os.path.isdir(vault):
            cnt = 0
            for root, _d, files in os.walk(vault):
                for fn in files:
                    if fn.endswith((".md", ".csv")):
                        full = os.path.join(root, fn)
                        z.write(full, os.path.join("vault", os.path.relpath(full, vault)))
                        cnt += 1
            manifest["vault_files"] = cnt
            inv_lines.append(f"- 볼트 노트·기록: {cnt}개 파일")
        # ④ 안내문 + 목록
        z.writestr("README_받는이에게.md", README_TEMPLATE.format(
            inventory="\n".join(inv_lines) or "- (아직 비어 있음)",
            created=now.strftime("%Y년 %m월 %d일")))
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return out


def verify_package(zip_path: str) -> dict:
    """상속 리허설 — 백업이 아니라 유산의 건강검진."""
    issues = []
    result = {"path": zip_path, "profiles": [], "vault_files": 0, "issues": issues, "healthy": False}
    try:
        with zipfile.ZipFile(zip_path) as z:
            names = z.namelist()
            if "manifest.json" not in names:
                issues.append("manifest.json 없음")
            if "README_받는이에게.md" not in names:
                issues.append("안내문 없음")
            manifest = json.loads(z.read("manifest.json")) if "manifest.json" in names else {}
            import tempfile
            with tempfile.TemporaryDirectory() as td:
                for pr in manifest.get("profiles", []):
                    member = f"dbs/{pr['id']}.db"
                    if member not in names:
                        issues.append(f"DB 누락: {pr['id']}")
                        continue
                    z.extract(member, td)
                    conn = sqlite3.connect(os.path.join(td, member))
                    n = conn.execute("SELECT COUNT(*) FROM nodes WHERE archived=0").fetchone()[0]
                    conn.close()
                    if n != pr["nodes"]:
                        issues.append(f"{pr['id']}: 노드 수 불일치 ({n} != {pr['nodes']})")
                    result["profiles"].append({"id": pr["id"], "nodes": n})
            result["vault_files"] = sum(1 for m in names if m.startswith("vault/"))
    except Exception as e:
        issues.append(f"패키지 열기 실패: {e}")
    result["healthy"] = not issues
    return result


def latest_package() -> str | None:
    d = _legacy_dir()
    zips = sorted(f for f in os.listdir(d) if f.startswith("legacy_") and f.endswith(".zip"))
    return os.path.join(d, zips[-1]) if zips else None


def auto_build_if_due(days: int = 7, vault: str | None = None) -> str | None:
    """심장박동용: 최근 패키지가 없거나 오래됐으면 자동 생성 (매주가 기본)."""
    last = latest_package()
    if last:
        age_days = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(last))).days
        if age_days < days:
            return None
    return build_package(vault)
