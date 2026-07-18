"""볼트(마크다운) → 그래프 동기화. 원칙: 진실의 원본은 볼트, 그래프는 거울.

- 프런트매터 `type:` 이 있는 노트만 노드가 된다 (person|medication|place)
- `for: "[[사람]]"` → TAKES 엣지, `rule_*` → Regimen 노드 + HAS_RULE 엣지
- 해시 기반 증분: 변경된 노트만 갱신. 삭제된 노트는 archived=1 (물리 삭제 금지)
"""
import argparse
import hashlib
import os
import re

from graph import store

TYPE_MAP = {"person": "Person", "medication": "Medication", "place": "Place"}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip().strip('"')
    return meta, m.group(2)


def slug(name: str) -> str:
    return re.sub(r"\s+", "_", name.strip())


def sync_note(path: str) -> str | None:
    """단일 노트를 그래프에 반영. 노드 id 반환(비대상 노트는 None)."""
    text = open(path, encoding="utf-8").read()
    meta, _body = parse_frontmatter(text)
    ntype = TYPE_MAP.get(meta.get("type", ""))
    if not ntype:
        return None
    name = meta.get("name") or os.path.splitext(os.path.basename(path))[0]
    node_id = f"{meta['type']}:{slug(name)}"

    props = {k: _num(v) for k, v in meta.items() if not k.startswith("rule_") and k not in ("type", "for")}
    props["name"] = name
    props["source"] = os.path.basename(path)
    store.upsert_node(node_id, ntype, props)

    if ntype == "Medication":
        # 복용자 연결
        for_ref = meta.get("for", "")
        m = re.search(r"\[\[(.+?)\]\]", for_ref)
        if m:
            pid = store.person_id(m.group(1))
            if not store.get_node(pid):
                store.upsert_node(pid, "Person", {"name": m.group(1)})
            store.upsert_edge(pid, "TAKES", node_id)
        # 복약규칙
        if meta.get("rule_time"):
            rid = f"regimen:{slug(name)}"
            store.upsert_node(rid, "Regimen", {
                "time": meta.get("rule_time", ""),
                "condition": meta.get("rule_condition", ""),
                "caution": meta.get("rule_caution", ""),
            })
            store.upsert_edge(node_id, "HAS_RULE", rid)
    return node_id


def _num(v):
    try:
        return float(v) if re.fullmatch(r"-?\d+(\.\d+)?", str(v)) else v
    except Exception:
        return v


def sync_vault(vault: str) -> dict:
    """증분 동기화: 신규/변경 반영, 사라진 노트는 archived 마킹."""
    conn = store.get_conn()
    seen_paths = set()
    changed = 0
    for root, _dirs, files in os.walk(vault):
        for fn in sorted(files):
            if not fn.endswith(".md"):
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, vault)
            seen_paths.add(rel)
            h = hashlib.sha256(open(path, "rb").read()).hexdigest()
            row = conn.execute("SELECT hash FROM sync_state WHERE path=?", (rel,)).fetchone()
            if row and row["hash"] == h:
                continue
            sync_note(path)
            conn.execute("INSERT OR REPLACE INTO sync_state(path,hash) VALUES(?,?)", (rel, h))
            changed += 1
    # 삭제 감지 → 해당 source 노드 archived
    archived = 0
    for row in conn.execute("SELECT path FROM sync_state").fetchall():
        if row["path"] not in seen_paths:
            fn = os.path.basename(row["path"])
            for n in conn.execute("SELECT id, props FROM nodes WHERE archived=0").fetchall():
                if f'"source": "{fn}"' in n["props"]:
                    store.archive_node(n["id"])
                    archived += 1
            conn.execute("DELETE FROM sync_state WHERE path=?", (row["path"],))
    conn.commit()
    return {"changed": changed, "archived": archived, **store.counts()}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=os.environ.get("VAULT_PATH")
                    or os.path.join(os.path.dirname(__file__), "..", "graph", "sample_vault"))
    ap.add_argument("--watch", action="store_true")
    args = ap.parse_args()
    print(sync_vault(args.vault))
    if args.watch:
        import time
        print("감시 모드 (5초 주기)... Ctrl+C로 종료")
        while True:
            time.sleep(5)
            r = sync_vault(args.vault)
            if r["changed"] or r["archived"]:
                print(r)
