"""M2-2 품질 게이트 + 일일 품질 리포트 (W12).

검사는 데이터 계약(registry/contracts)의 규칙에서 자동 생성된다 —
계약 없는 테이블은 게이트를 통과할 수 없다.
"""
from __future__ import annotations

import json
from datetime import date

from .. import common, db
from ..custody import contracts
from . import codemap

FACT_TABLES = ["fact_sales", "fact_production", "fact_procurement",
               "fact_inventory_move", "fact_defect", "fact_equipment_event"]

DDL = """
CREATE TABLE IF NOT EXISTS quality_reports (
  report_date TEXT PRIMARY KEY, ok INTEGER, unmapped_rate REAL, detail TEXT, created_at TEXT
);
"""


def run_checks(table: str) -> list[dict]:
    """계약의 규칙 실행 — not_null / range / ref / unique."""
    results = []
    for rule in contracts.quality_rules(table):
        col, check = rule["column"], rule["check"]
        if check == "not_null":
            n = db.scalar(f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL OR CAST({col} AS TEXT)=''")
        elif check == "range":
            conds = []
            if rule.get("min") is not None:
                conds.append(f"{col} < {rule['min']}")
            if rule.get("max") is not None:
                conds.append(f"{col} > {rule['max']}")
            n = db.scalar(f"SELECT COUNT(*) FROM {table} WHERE {' OR '.join(conds)}") if conds else 0
        elif check == "ref":
            n = db.scalar(
                f"SELECT COUNT(*) FROM {table} t LEFT JOIN {rule['ref_table']} r "
                f"ON t.{col}=r.{rule['ref_column']} "
                f"WHERE t.{col} IS NOT NULL AND CAST(t.{col} AS TEXT)!='' AND r.{rule['ref_column']} IS NULL")
        elif check == "unique":
            n = db.scalar(
                f"SELECT COALESCE(SUM(c-1),0) FROM (SELECT COUNT(*) c FROM {table} "
                f"GROUP BY {col} HAVING COUNT(*)>1) d")
        else:
            continue
        results.append({"table": table, "column": col, "check": check,
                        "violations": int(n or 0)})
    return results


def daily_report(report_date: str | None = None) -> dict:
    """일일 품질 리포트 — 계열별 건수·게이트 위반·미매핑률·전일 대비."""
    db.executescript(DDL)
    rdate = report_date or date.today().isoformat()
    detail: dict = {"tables": {}, "violations": []}
    ok = True
    for t in FACT_TABLES:
        cnt = db.scalar(f"SELECT COUNT(*) FROM {t}") or 0
        latest = db.scalar(f"SELECT MAX(date_key) FROM {t}")
        detail["tables"][t] = {"rows": cnt, "latest": latest}
        try:
            checks = run_checks(t)
        except contracts.ContractError as e:
            ok = False
            detail["violations"].append({"table": t, "error": str(e)})
            common.alert("crit", "M2-2", f"계약 없음: {t} — {e}")
            continue
        for c in checks:
            if c["violations"] > 0:
                ok = False
                detail["violations"].append(c)
                common.alert("warn", "M2-2",
                             f"품질 위반 {c['table']}.{c['column']} [{c['check']}] {c['violations']}건")
    rate = codemap.unmapped_rate()
    detail["unmapped_rate"] = round(rate, 4)
    detail["quarantine_pending"] = len(codemap.pending())
    if rate >= 0.05:
        ok = False
        common.alert("warn", "M2-2", f"미매핑률 {rate:.1%} — 기준(5%) 초과")
    prev = db.one("SELECT * FROM quality_reports ORDER BY report_date DESC LIMIT 1")
    if prev:
        prev_tables = json.loads(prev["detail"])["tables"]
        detail["day_over_day"] = {
            t: detail["tables"][t]["rows"] - prev_tables.get(t, {}).get("rows", 0)
            for t in FACT_TABLES}
    db.execute(
        "INSERT OR REPLACE INTO quality_reports VALUES (?,?,?,?,?)",
        (rdate, int(ok), rate, json.dumps(detail, ensure_ascii=False), common.now_iso()))
    return {"report_date": rdate, "ok": ok, "unmapped_rate": rate, "detail": detail}


def render_md(report: dict) -> str:
    d = report["detail"]
    lines = [f"# 일일 품질 리포트 — {report['report_date']}",
             "", f"판정: {'✅ 통과' if report['ok'] else '⚠️ 위반 있음'} · "
             f"미매핑률 {report['unmapped_rate']:.2%} · 격리 대기 {d.get('quarantine_pending', 0)}건", "",
             "| 계열 | 행수 | 최신 일자 |", "|---|---|---|"]
    for t, v in d["tables"].items():
        lines.append(f"| {t} | {v['rows']:,} | {v['latest']} |")
    if d["violations"]:
        lines += ["", "## 위반", ""]
        for v in d["violations"]:
            lines.append(f"- {v}")
    return "\n".join(lines)
