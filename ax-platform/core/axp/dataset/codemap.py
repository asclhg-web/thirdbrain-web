"""M2-2 코드 매핑 엔진 — 별칭·중복 코드의 표준 사전 + 격리 큐.

원칙: 미매핑 행은 버리지 않는다 — 격리 큐로 보내 스튜어드가 확정하고,
확정 결과는 사전에 쌓여 재발하지 않는다.
"""
from __future__ import annotations

from .. import common, db

DDL = """
CREATE TABLE IF NOT EXISTS code_dictionary (
  domain TEXT NOT NULL,          -- store | product | worker | ...
  alias  TEXT NOT NULL,          -- 현장 표기
  standard_code TEXT NOT NULL,   -- 표준 코드
  confirmed_by TEXT, confirmed_at TEXT,
  PRIMARY KEY (domain, alias)
);
CREATE TABLE IF NOT EXISTS quarantine_queue (
  q_id INTEGER PRIMARY KEY AUTOINCREMENT,
  domain TEXT NOT NULL, alias TEXT NOT NULL,
  context TEXT DEFAULT '',        -- 어느 원천 몇 건인지
  n_rows INTEGER DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'pending'
         CHECK (status IN ('pending','confirmed','rejected')),
  proposed_code TEXT, decided_by TEXT, decided_at TEXT, created_at TEXT
);
"""

# 초기 사전 — 엑셀·장표의 현장 표기 (스튜어드 확정본은 위 테이블에 쌓인다)
SEED = [
    ("store", "본점", "S-MAIN"), ("store", "역전점", "S-STATION"),
    ("store", "마트납품", "B2B-MART"), ("store", "카페납품", "B2B-CAFE"),
    ("store", "S-MAIN", "S-MAIN"), ("store", "S-STATION", "S-STATION"),
    ("store", "B2B-MART", "B2B-MART"), ("store", "B2B-CAFE", "B2B-CAFE"),
    ("product", "크림빵", "P-CREAM"), ("product", "단팥빵", "P-RED"),
    ("product", "파이만쥬", "P-PIE"),
]


def init() -> None:
    db.executescript(DDL)
    db.executemany(
        "INSERT OR IGNORE INTO code_dictionary (domain, alias, standard_code) VALUES (?,?,?)",
        SEED)
    # 고객사 프로파일의 어휘 시드 — 온보딩 워크숍의 산출물이 여기로 들어온다
    from .. import profile_rt
    extra = profile_rt.alias_seed()
    if extra:
        db.executemany(
            "INSERT OR IGNORE INTO code_dictionary (domain, alias, standard_code) VALUES (?,?,?)",
            extra)


STANDARD_LOOKUP = {          # 별칭이 이미 표준 코드와 완전 일치하면 자기 매핑
    "product": ("dim_product", "product_id"),
    "store": ("dim_store", "store_id"),
    "worker": ("dim_worker", "worker_id"),
    "equipment": ("dim_equipment", "equipment_id"),
}


def resolve(domain: str, alias: str, context: str = "") -> str | None:
    """별칭 → 표준 코드. 표준 코드 자기 일치는 자동 매핑(사전에 기록).
    그 외 실패는 격리 큐 적재 후 None (행은 보존, 사실 반영은 보류)."""
    init()
    if alias is None or str(alias).strip() == "":
        return None
    alias = str(alias).strip()
    row = db.one("SELECT standard_code FROM code_dictionary WHERE domain=? AND alias=?",
                 (domain, alias))
    if row:
        return row["standard_code"]
    lookup = STANDARD_LOOKUP.get(domain)
    if lookup and db.table_exists(lookup[0]):
        hit = db.one(f"SELECT 1 FROM {lookup[0]} WHERE {lookup[1]}=?", (alias,))
        if hit:                                # 이미 표준 코드 — 자기 매핑 기록
            db.execute(
                "INSERT OR REPLACE INTO code_dictionary "
                "(domain, alias, standard_code, confirmed_by, confirmed_at) "
                "VALUES (?,?,?,?,?)",
                (domain, alias, alias, "auto(표준 코드 일치)", common.now_iso()))
            return alias
    existing = db.one("SELECT 1 FROM quarantine_queue WHERE domain=? AND alias=? AND status='pending'",
                      (domain, alias))
    if existing:
        db.execute("UPDATE quarantine_queue SET n_rows=n_rows+1 WHERE domain=? AND alias=? AND status='pending'",
                   (domain, alias))
    else:
        db.execute(
            "INSERT INTO quarantine_queue (domain, alias, context, created_at) VALUES (?,?,?,?)",
            (domain, alias, context, common.now_iso()))
    return None


def pending() -> list[dict]:
    init()
    return db.query("SELECT * FROM quarantine_queue WHERE status='pending' ORDER BY n_rows DESC")


def confirm(q_id: int, standard_code: str, by: str) -> None:
    """스튜어드 확정 — 사전 갱신 → 같은 별칭은 재발하지 않는다."""
    init()
    row = db.one("SELECT * FROM quarantine_queue WHERE q_id=? AND status='pending'", (q_id,))
    if row is None:
        raise ValueError(f"격리 건 {q_id} 없음")
    db.execute(
        "UPDATE quarantine_queue SET status='confirmed', proposed_code=?, decided_by=?, decided_at=? WHERE q_id=?",
        (standard_code, by, common.now_iso(), q_id))
    db.execute(
        "INSERT OR REPLACE INTO code_dictionary (domain, alias, standard_code, confirmed_by, confirmed_at) "
        "VALUES (?,?,?,?,?)",
        (row["domain"], row["alias"], standard_code, by, common.now_iso()))


def unconfirm(q_id: int, by: str) -> None:
    """확정 취소(undo) — I-09 교훈: 스튜어드 확정 실수는 반드시 일어난다.

    사전 항목을 제거하고 격리 건을 pending으로 되돌린다. 다음 야간 배치의
    전량 재구축(멱등)이 소급 반영하므로 하류 오염도 함께 청소된다."""
    init()
    row = db.one("SELECT * FROM quarantine_queue WHERE q_id=?", (q_id,))
    if row is None or row["status"] != "confirmed":
        raise ValueError(f"격리 건 {q_id}는 확정 상태가 아니다")
    db.execute("DELETE FROM code_dictionary WHERE domain=? AND alias=?",
               (row["domain"], row["alias"]))
    db.execute(
        "UPDATE quarantine_queue SET status='pending', proposed_code=NULL, "
        "decided_by=?, decided_at=? WHERE q_id=?",
        (f"undo({by})", common.now_iso(), q_id))
    common.alert("warn", "codemap",
                 f"확정 취소: {row['domain']}/{row['alias']} (by {by}) — 다음 배치에서 소급 반영")


def drain_self_matches(by: str = "auto(표준 코드 일치)") -> int:
    """대기 큐 정리 — 표준 코드와 완전 일치하는 별칭을 일괄 자기 매핑으로 확정."""
    init()
    n = 0
    for q in pending():
        lookup = STANDARD_LOOKUP.get(q["domain"])
        if lookup and db.table_exists(lookup[0]) and db.one(
                f"SELECT 1 FROM {lookup[0]} WHERE {lookup[1]}=?", (q["alias"],)):
            confirm(q["q_id"], q["alias"], by)
            n += 1
    return n


def unmapped_rate() -> float:
    """미매핑률 — 격리 대기 행수 / (사실 반영 행수 + 격리 행수). 수용 기준 5% 미만."""
    init()
    q = db.scalar("SELECT COALESCE(SUM(n_rows),0) FROM quarantine_queue WHERE status='pending'") or 0
    total = (db.scalar("SELECT COUNT(*) FROM fact_sales") or 0) + q
    return (q / total) if total else 0.0
