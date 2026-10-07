"""Validate tagger output against the taxonomy and compare two taggers.

    python3 pipeline/tag/compare.py <a.json> <b.json>

1. Validity: every tag must exist in pipeline/prompts/taxonomy.md; counts per field obeyed.
2. Agreement per axis: mean Jaccard overlap, and how often the top (first) tag matches.
3. Confusions: fine-tag pairs one model chose where the other chose the other.
   Pairs that recur are candidates for merging (taxonomy section 1.3).
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TAXONOMY = ROOT / "pipeline" / "prompts" / "taxonomy.md"
LIMITS = {"feelings": (1, 3), "themes": (1, 3), "situations": (0, 3), "tone": (1, 2), "keywords": (0, 3)}


def section(md, n):
    m = re.search(rf"^## {n}\..*?(?=^## {n + 1}\.|\Z)", md, re.S | re.M)
    return m.group(0)


def first_col(text):
    rows = [l for l in text.splitlines() if l.startswith("| ") and not l.startswith("| ---")]
    return {r.split("|")[1].strip() for r in rows} - {"Tag", "Family", "Field"}


def vocab():
    md = TAXONOMY.read_text(encoding="utf-8")
    sit = set()
    for row in section(md, 4).splitlines():
        cells = [c.strip() for c in row.split("|")]
        if len(cells) > 3 and row.startswith("| ") and cells[2] not in ("Tags", "---"):
            sit |= {t.strip() for t in cells[2].split(";") if t.strip()}
    return {"feelings": first_col(section(md, 2)), "themes": first_col(section(md, 3)),
            "situations": sit, "tone": first_col(section(md, 5)),
            "faith": first_col(section(md, 6)), "safety": first_col(section(md, 7))}


def load(path):
    return {t["id"]: t for t in json.loads(Path(path).read_text(encoding="utf-8"))["tags"]}


def validate(name, tags, V):
    problems = Counter()
    for t in tags.values():
        for f, (lo, hi) in LIMITS.items():
            v = t.get(f, [])
            if not lo <= len(v) <= hi:
                problems[f"{f}: count {len(v)}"] += 1
            if f in V:
                for x in v:
                    if x not in V[f]:
                        problems[f"{f}: unknown '{x}'"] += 1
        for f in ("faith", "safety"):
            if t.get(f) not in V[f]:
                problems[f"{f}: unknown '{t.get(f)}'"] += 1
    print(f"{name}: {len(tags)} passages tagged, {sum(problems.values())} validity problems")
    for p, c in problems.most_common(10):
        print(f"   {c:>3} x {p}")


def jac(a, b):
    a, b = set(a), set(b)
    return 1.0 if not a and not b else len(a & b) / len(a | b)


def main(pa, pb):
    V = vocab()
    A, B = load(pa), load(pb)
    validate("A " + Path(pa).stem, A, V)
    validate("B " + Path(pb).stem, B, V)
    ids = sorted(set(A) & set(B))
    print(f"\nAgreement on {len(ids)} passages (Jaccard = shared tags / all tags used):")
    for f in ("feelings", "themes", "situations", "tone"):
        j = sum(jac(A[i].get(f, []), B[i].get(f, [])) for i in ids) / len(ids)
        top = sum(1 for i in ids if A[i].get(f) and B[i].get(f) and A[i][f][0] == B[i][f][0]) / len(ids)
        print(f"   {f:11} overlap {j:.0%}   same top tag {top:.0%}")
    for f in ("faith", "safety"):
        same = sum(1 for i in ids if A[i].get(f) == B[i].get(f)) / len(ids)
        print(f"   {f:11} same {same:.0%}")
    print("\nSafety tags:", "A", Counter(A[i]["safety"] for i in ids), "| B", Counter(B[i]["safety"] for i in ids))
    print("\nMost frequent confusions (A chose x, B chose y instead, on the same passage):")
    for f in ("feelings", "themes", "situations", "tone"):
        conf = Counter()
        for i in ids:
            a, b = set(A[i].get(f, [])), set(B[i].get(f, []))
            for x in a - b:
                for y in b - a:
                    conf[tuple(sorted((x, y)))] += 1
        print(f"   {f}: " + "; ".join(f"{x} / {y} ({c})" for (x, y), c in conf.most_common(5)))
    print("\nTag use across both (tags never used by either):")
    for f in ("feelings", "themes", "situations", "tone"):
        used = {x for T in (A, B) for t in T.values() for x in t.get(f, [])}
        print(f"   {f}: {len(used)} of {len(V[f])} used")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
