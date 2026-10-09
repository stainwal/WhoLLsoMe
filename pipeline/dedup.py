"""Deduplicate the corpus (Plan Days 12-13).

    python3 pipeline/dedup.py          # writes corpus/passages/bulk/duplicates.json, prints a summary
    python3 pipeline/bulk.py merge     # then applies it: status "dup" + dup_of, or near_group

Reads the merged per-source files. Nothing is deleted: a duplicate keeps its record and
gets status "dup" with the id it duplicates, so the database loader and search skip it.

Three bands, measured on word 8-grams after lower-casing and stripping punctuation:
  exact      identical text                         -> keep the earliest in its source, others "dup"
  contained  one passage lies wholly inside another -> the shorter is "dup" of the longer
  near       Jaccard >= 0.8 (stock formulae with a name swapped, e.g. "Please, Kalamas, don't go
             by oral transmission" / "Please, Bhaddiya, ...")  -> keep the earliest, others "dup"
  related    0.5 <= Jaccard < 0.8  -> both kept, same near_group; the search-time filter never
             shows two passages from one group in the 10 (Plan section 2.1, item 2)
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PASSAGES = ROOT / "corpus" / "passages"
OUT = PASSAGES / "bulk" / "duplicates.json"
K = 8                      # shingle length in words
NEAR, RELATED = 0.8, 0.5   # Jaccard thresholds


def norm(t):
    return re.sub(r"[^a-z0-9 ]", "", re.sub(r"\s+", " ", t.lower().replace("<j>", ""))).strip()


def shingles(t):
    w = norm(t).split()
    return {" ".join(w[i:i + K]) for i in range(max(1, len(w) - K + 1))}


def uid_n(u):
    return int(u.split(":")[1])


def load():
    ps = []
    for f in sorted(PASSAGES.glob("*.jsonl")):
        ps += [json.loads(line) for line in f.open(encoding="utf-8")]
    return [p for p in ps if p["status"] != "cut"]   # cut passages never show, so they can't duplicate anything


def earliest(a, b):
    """The passage to keep: earlier in its source; on a tie the longer one."""
    ka = (a["source"], uid_n(a["start_uid"]), -a["words"], a["pid"])
    kb = (b["source"], uid_n(b["start_uid"]), -b["words"], b["pid"])
    return (a, b) if ka <= kb else (b, a)


def main():
    ps = load()
    by = {p["pid"]: p for p in ps}
    S = {p["pid"]: shingles(p["text"]) for p in ps}
    N = {p["pid"]: norm(p["text"]) for p in ps}
    index = defaultdict(set)
    for pid, s in S.items():
        for g in s:
            index[g].add(pid)
    shared = defaultdict(int)
    for g, pids in index.items():
        if 1 < len(pids) <= 40:
            pids = sorted(pids)
            for i in range(len(pids)):
                for j in range(i + 1, len(pids)):
                    shared[(pids[i], pids[j])] += 1
    pairs = []   # (band, keep, drop) or ("related", a, b)
    for (a, b), c in shared.items():
        jac = c / len(S[a] | S[b])
        if N[a] == N[b]:
            keep, drop = earliest(by[a], by[b])
            pairs.append(("exact", keep["pid"], drop["pid"]))
        elif N[a] in N[b] or N[b] in N[a]:
            keep, drop = (by[b], by[a]) if len(N[a]) < len(N[b]) else (by[a], by[b])
            pairs.append(("contained", keep["pid"], drop["pid"]))
        elif jac >= NEAR:
            keep, drop = earliest(by[a], by[b])
            pairs.append(("near", keep["pid"], drop["pid"]))
        elif jac >= RELATED:
            pairs.append(("related", a, b))
    # Resolve drops transitively: if X is dropped for Y and Y is dropped for Z, X points at Z.
    dup_of, why = {}, {}
    for band, keep, drop in sorted(pairs, key=lambda x: ("exact", "contained", "near").index(x[0]) if x[0] != "related" else 9):
        if band == "related":
            continue
        if drop in dup_of:
            continue
        while keep in dup_of:
            keep = dup_of[keep]
        if keep == drop:
            continue
        dup_of[drop], why[drop] = keep, band
    def resolve(pid):
        """The kept passage at the end of a dup_of chain (a keep can itself be dropped by a later pair)."""
        while pid in dup_of:
            pid = dup_of[pid]
        return pid

    dup_of = {k: resolve(v) for k, v in dup_of.items()}
    # Related groups (union-find over kept passages only)
    parent = {}

    def find(x):
        while parent.get(x, x) != x:
            x = parent[x]
        return x

    for band, a, b in pairs:
        if band != "related":
            continue
        a, b = resolve(a), resolve(b)
        if a != b:
            parent[find(a)] = find(b)
    groups = defaultdict(list)
    for pid in set(list(parent) + [v for v in parent.values()]):
        groups[find(pid)].append(pid)
    out = {}
    for drop, keep in sorted(dup_of.items()):
        out[drop] = {"status": "dup", "dup_of": keep, "why": why[drop]}
    for n, (root, members) in enumerate(sorted(groups.items(), key=lambda kv: min(kv[1])), 1):
        for pid in members:
            out.setdefault(pid, {})["near_group"] = f"ng-{n:03d}"
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    bands = defaultdict(int)
    for v in why.values():
        bands[v] += 1
    print(f"{len(ps)} shown passages scanned; {len(dup_of)} marked dup "
          f"({', '.join(f'{k} {v}' for k, v in bands.items())}); "
          f"{sum(len(m) for m in groups.values())} kept passages in {len(groups)} near groups")
    by_src = defaultdict(int)
    for d in dup_of:
        by_src[by[d]["source"]] += 1
    print("dups by source:", dict(by_src))


if __name__ == "__main__":
    main()
