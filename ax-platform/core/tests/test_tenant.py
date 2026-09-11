"""P4-1: 테넌트 도구 테스트 — 생성·리셋·파기·업로드 파기."""
import json
import os
import time
from pathlib import Path

import pytest

from axp import tenant


@pytest.fixture()
def tenant_env(tmp_path, monkeypatch):
    """작은 템플릿 + 격리된 테넌트 루트."""
    template = tmp_path / "template"
    (template / "raw").mkdir(parents=True)
    (template / "profile.json").write_text(json.dumps(
        {"profile": "demo", "company": "데모제과"}, ensure_ascii=False), encoding="utf-8")
    import sqlite3
    con = sqlite3.connect(template / "axp.db")
    con.execute("CREATE TABLE axp_users (username TEXT PRIMARY KEY, pw_hash TEXT)")
    con.execute("INSERT INTO axp_users VALUES ('admin', 'stale-hash')")
    con.commit(); con.close()
    monkeypatch.setattr(tenant, "TENANTS_ROOT", tmp_path / "tenants")
    monkeypatch.setattr(tenant, "DEFAULT_TEMPLATE", template)
    return template


def test_create_renames_profile_and_issues_credentials(tenant_env):
    r = tenant.create("bakery-t", company="제빵업체 T사 체험")
    d = Path(r["data_dir"])
    prof = json.loads((d / "profile.json").read_text(encoding="utf-8"))
    assert prof["company"] == "제빵업체 T사 체험"
    assert prof["profile"] == "bakery-t" and prof["trial"] is True
    cred = Path(r["credentials_file"])
    assert cred.exists() and "admin /" in cred.read_text(encoding="utf-8")
    assert oct(cred.stat().st_mode)[-3:] == "600"
    assert "bootstrap_pw" not in r          # 반환값에 비밀번호 노출 금지
    with pytest.raises(ValueError):
        tenant.create("bakery-t")            # 중복 거절
    with pytest.raises(ValueError):
        tenant.create("한글이름")             # 이름 규칙


def test_reset_restores_template_state(tenant_env):
    tenant.create("shop-a")
    d = tenant.data_dir("shop-a")
    (d / "dirty.txt").write_text("체험 중 오염", encoding="utf-8")
    r = tenant.reset("shop-a")
    assert not (d / "dirty.txt").exists()    # 오염 제거
    prof = json.loads((d / "profile.json").read_text(encoding="utf-8"))
    assert prof["profile"] == "shop-a"       # 개명은 유지
    assert "reset_at" in r


def test_destroy_removes_everything(tenant_env):
    tenant.create("gone")
    root = tenant.data_dir("gone").parent
    tenant.destroy("gone")
    assert not root.exists()
    with pytest.raises(ValueError):
        tenant.destroy("gone")


def test_purge_uploads_respects_age(tenant_env):
    tenant.create("purge-t")
    raw = tenant.data_dir("purge-t") / "raw"
    old = raw / "old.xlsx"; old.write_bytes(b"x")
    os.utime(old, (time.time() - 90000, time.time() - 90000))   # 25시간 전
    new = raw / "new.xlsx"; new.write_bytes(b"y")
    r = tenant.purge_uploads("purge-t", hours=24)
    assert r["purged"] == 1 and not old.exists() and new.exists()


def test_listing_hides_password(tenant_env):
    tenant.create("l-1")
    rows = tenant.listing()
    assert len(rows) == 1 and rows[0]["name"] == "l-1"
    assert "bootstrap_pw" not in rows[0]


def test_create_purges_template_accounts(tenant_env):
    """P4-I1 회귀: 템플릿의 웹 계정이 새 테넌트에 남으면 안 된다."""
    import sqlite3
    r = tenant.create("acct-t")
    con = sqlite3.connect(Path(r["data_dir"]) / "axp.db")
    n = con.execute("SELECT count(*) FROM sqlite_master WHERE name='axp_users'").fetchone()[0]
    con.close()
    assert n == 0
