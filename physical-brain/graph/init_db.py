"""그래프 초기화 + 온톨로지 문서 자동 생성."""
import os

from graph import schema, store


def write_docs():
    lines = ["# 서드브레인 표준 개인 온톨로지 v1 (자동 생성)", "", "## 노드"]
    for n in schema.NODE_TYPES:
        lines.append(f"- **{n}**")
    lines += ["", "## 관계"]
    for r in schema.REL_TYPES:
        rule = schema.REL_RULES.get(r)
        lines.append(f"- **{r}**: {rule[0]} → {rule[1]}" if rule else f"- **{r}**: 자유 연결")
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "ontology-v1.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


if __name__ == "__main__":
    store.get_conn()
    p = write_docs()
    print("초기화 완료:", store.db_path())
    print("온톨로지 문서:", p)
