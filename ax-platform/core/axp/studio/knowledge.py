"""지식센터 미니 (4대 지능화 ④의 1단계 씨앗) — 현장의 말이 데이터가 된다.

원천: fact_defect.memo + staging_forms.memo (원문 보존분).
기능: ① 키워드 주간 추이(변화 탐지와 같은 규율 — 급증만 보고)
      ② 메모 검색(근거 인용 — defect_id/form_id까지)
원칙: 메모 원문은 수정하지 않는다. 요약·추출만 하고 참조를 남긴다.
"""
from __future__ import annotations

import re
from collections import Counter

import pandas as pd

from .. import db

# 조사·어미 등 한국어 스톱워드(경량) — 현장 어휘 사전은 커스터디 대상
STOP = {"있는", "있음", "같음", "같은", "듯", "보임", "문제", "으로", "에서", "이번",
        "오늘", "어제", "관련", "확인", "필요", "발생", "조금", "약간"}


def _tokens(text: str) -> list[str]:
    words = re.findall(r"[가-힣A-Za-z0-9]{2,}", text or "")
    return [w for w in words if w not in STOP]


def corpus(start: str, end: str) -> pd.DataFrame:
    """메모 말뭉치 — 출처·원장 참조 포함."""
    d1 = db.df("""
        SELECT date_key AS d, memo, 'fact_defect' AS src,
               'defect_id=' || defect_id AS ref
        FROM fact_defect WHERE memo != '' AND date_key BETWEEN ? AND ?""",
        (start, end))
    d2 = db.df("""
        SELECT form_date AS d, memo, 'staging_forms(' || form_type || ')' AS src,
               'form_id=' || form_id AS ref
        FROM staging_forms WHERE memo != '' AND form_date BETWEEN ? AND ?""",
        (start, end)) if db.table_exists("staging_forms") else pd.DataFrame()
    return pd.concat([d1, d2], ignore_index=True)


def keyword_trend(end: str, weeks: int = 8) -> pd.DataFrame:
    """주간 키워드 빈도 + 직전 주 대비 급증 표시."""
    start = (pd.Timestamp(end) - pd.Timedelta(weeks=weeks)).date().isoformat()
    c = corpus(start, end)
    if c.empty:
        return pd.DataFrame(columns=["week", "keyword", "n", "surge"])
    c["week"] = pd.to_datetime(c["d"]).dt.to_period("W").astype(str)
    rows = []
    for wk, g in c.groupby("week"):
        cnt = Counter(t for m in g["memo"] for t in _tokens(m))
        for k, n in cnt.most_common(15):
            rows.append({"week": wk, "keyword": k, "n": n})
    t = pd.DataFrame(rows)
    t["prev"] = t.groupby("keyword")["n"].shift(1).fillna(0)
    t["surge"] = (t["n"] >= 3) & (t["n"] >= t["prev"] * 2)
    return t


def surges(end: str, weeks: int = 8) -> list[dict]:
    """급증 키워드 — 아침 브리핑·지식검증 에이전트의 입력."""
    t = keyword_trend(end, weeks)
    if t.empty:
        return []
    last_week = t["week"].max()
    out = t[(t["week"] == last_week) & (t["surge"])]
    return out[["keyword", "n", "prev"]].to_dict("records")


def surge_candidates(end: str, weeks: int = 8) -> list[dict]:
    """급증 키워드 → 원인 후보 (지식센터 → 그래프 M5).

    급증 키워드가 특정 설비/근무조의 불량 메모에 집중되어 있으면(점유율 60%+,
    5건+) 원인 후보로 만든다 — 현장의 말이 그래프의 후보가 되는 길."""
    out = []
    start = (pd.Timestamp(end) - pd.Timedelta(weeks=2)).date().isoformat()
    for s in surges(end, weeks):
        kw = s["keyword"]
        hits = db.df("""
            SELECT equipment_id, shift, COUNT(*) n FROM fact_defect
            WHERE memo LIKE ? AND date_key BETWEEN ? AND ?
            GROUP BY equipment_id, shift""", (f"%{kw}%", start, end))
        if hits.empty:
            continue
        total = hits["n"].sum()
        for dim in ("equipment_id", "shift"):
            g = hits.groupby(dim)["n"].sum().sort_values(ascending=False)
            if len(g) and g.iloc[0] >= 5 and g.iloc[0] / total >= 0.6:
                out.append({"dims": {dim: g.index[0]},
                            "importance": round(float(g.iloc[0] / total), 3),
                            "source": f"memo_surge:{kw}"})
    return out


def search_memos(query: str, limit: int = 5) -> dict:
    """메모 검색 — assembler의 'memo' 질의 유형이 쓴다. 원장 참조 필수."""
    c = corpus("0000-01-01", "9999-12-31")
    toks = _tokens(query)
    if c.empty or not toks:
        return {"query_type": "memo", "query": query, "hits": []}
    mask = c["memo"].apply(lambda m: any(t in (m or "") for t in toks))
    hits = c[mask].sort_values("d", ascending=False).head(limit)
    return {"query_type": "memo", "query": query,
            "hits": [{"date": r.d, "memo": r.memo, "src": r.src, "ref": r.ref}
                     for r in hits.itertuples()]}
