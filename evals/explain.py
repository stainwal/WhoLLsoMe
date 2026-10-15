"""Explain evals (Plan Day 20, sections 4.3 and 4.4 experiment 5; 15 Oct 2026).

    .venv/bin/python evals/explain.py pairs N SETUP        # N statement-passage pairs -> evals/explain/pairs.jsonl
    .venv/bin/python evals/explain.py genbatches NAME K     # pairs in K files for writer NAME -> evals/judge-in/gNAME-NN.jsonl
    .venv/bin/python evals/explain.py collect NAME          # writer output (evals/explain/out/NAME-NN.json) -> evals/explain/NAME.json
    .venv/bin/python evals/explain.py judgebatch A B [...]  # notes from writers A, B…, shuffled and anonymised -> evals/judge-in/ejNN.jsonl
    .venv/bin/python evals/explain.py report A B [...]      # rubric pass rate, mean score, biggest gaps -> evals/results/explain-*.json
    .venv/bin/python evals/explain.py spotcheck NAME N      # N notes for Shailesh -> evals/explain-spot-check.md

The pairs are each statement's first passage under the chosen retrieval setup, so the notes are tested on
what a user would actually see, good matches and weak ones alike. The prompt is read from
app/lib/explain-prompt.ts, the same file the app ships. Notes are judged blind: the judge sees neither the
writer nor the model, and items from all writers are shuffled together.
"""

import json
import random
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import retrieval as R  # noqa: E402

OUT = HERE / "explain"
PAIRS = OUT / "pairs.jsonl"
CHECKS = ("true_to_passage", "relevant", "no_advice", "no_claims", "short")
PRICE = {"haiku": (0.10, 0.50), "sonnet": (2.0, 10.0)}  # USD per 1M tokens, Claude API (15 Oct 2026)


def jl(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def wjl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def pairs(n, setup):
    run = R.jload(R.RUNS / f"{setup.replace('/', '__')}.json")
    st = [s for s in R.scored_statements()]
    human = [s for s in st if s["set"] == "human" and s["part"] == "held-out"]
    agent = [s for s in st if s["set"] == "agent" and s["part"] in ("golden", "held-out")]
    rng = random.Random(2020)
    pick = sorted(rng.sample(human, n // 2) + rng.sample(agent, n - n // 2), key=lambda s: s["id"])
    labels = R.jload(R.LABELS)
    with R.load.connect() as db:
        info = {p: (dt, pl, w, tr) for p, dt, pl, w, tr in db.execute(
            "select p.pid, p.display_text, p.plain, s.work, s.translator from passages p join sources s on s.id = p.source_id")}
    rows = []
    for s in pick:
        pid = run["ranked"][s["id"]][0][0]
        dt, pl, w, tr = info[pid]
        rows.append({"id": s["id"], "statement": s["text"], "pid": pid, "passage": dt, "plain": pl, "work": w,
                     "translator": tr, "relevance_grade": labels[s["id"]][pid]["grade"]})
    wjl(PAIRS, rows)
    g = [r["relevance_grade"] for r in rows]
    print(f"{len(rows)} pairs ({setup}): {', '.join(r['id'] for r in rows)}; first-passage grades 0/1/2/3 = "
          f"{g.count(0)}/{g.count(1)}/{g.count(2)}/{g.count(3)}")


def genbatches(name, k):
    rows = jl(PAIRS)
    size = -(-len(rows) // k)
    for i in range(k):
        part = [{key: r[key] for key in ("id", "statement", "passage", "plain", "work", "translator")}
                for r in rows[i * size:(i + 1) * size]]
        wjl(R.JUDGE_IN / f"g{name}-{i + 1:02d}.jsonl", part)
    print(f"{k} files for {name}")


def words(t):
    return len(re.findall(r"\S+", t))


def collect(name):
    want = {r["id"] for r in jl(PAIRS)}
    notes = {}
    for f in sorted((OUT / "out").glob(f"{name}-*.json")):
        for n in R.jload(f)["notes"]:
            notes[n["id"]] = n["note"].strip()
    missing = want - set(notes)
    if missing:
        sys.exit(f"{name}: missing notes for {sorted(missing)}")
    R.jsave(OUT / f"{name}.json", {"writer": name, "notes": {k: notes[k] for k in sorted(want)}})
    w = [words(t) for t in notes.values()]
    print(f"{name}: {len(notes)} notes, words median {statistics.median(w)}, max {max(w)}")


def judgebatch(names):
    rows = {r["id"]: r for r in jl(PAIRS)}
    items = []
    for name in names:
        for sid, note in R.jload(OUT / f"{name}.json")["notes"].items():
            items.append({"key": f"{name}|{sid}", "sid": sid, "note": note})
    rng = random.Random(2021)
    rng.shuffle(items)
    key = {}
    lines = []
    for i, it in enumerate(items, 1):
        anon = f"E{i:03d}"
        key[anon] = it["key"]
        r = rows[it["sid"]]
        lines.append({"id": anon, "statement": r["statement"], "passage": r["passage"], "plain": r["plain"], "note": it["note"]})
    tag = "-".join(names)
    n = len(list(R.JUDGE_IN.glob("ej*.jsonl"))) + 1
    path = R.JUDGE_IN / f"ej{n:02d}.jsonl"
    wjl(path, lines)
    R.jsave(OUT / f"key-ej{n:02d}.json", {"writers": names, "key": key})
    print(f"{path.name}: {len(lines)} notes from {tag} (key in evals/explain/key-ej{n:02d}.json)")


def judged(names):
    out = {}
    for kf in sorted(OUT.glob("key-ej*.json")):
        k = R.jload(kf)
        jf = R.JUDGE / f"{kf.stem[4:]}.json"
        if not jf.exists():
            continue
        for j in R.jload(jf)["judgements"]:
            writer, sid = k["key"][j["id"]].split("|")
            if writer in names:
                out[(writer, sid)] = j
    return out


def report(names):
    J = judged(names)
    rows = {r["id"]: r for r in jl(PAIRS)}
    res = {"writers": {}, "pairs": len(rows)}
    for name in names:
        js = [J[(name, sid)] for sid in rows if (name, sid) in J]
        notes = R.jload(OUT / f"{name}.json")["notes"]
        res["writers"][name] = {
            "judged": len(js),
            "rubric_pass": sum(all(j[c] for c in CHECKS) for j in js),
            "rubric_pass_rate": round(sum(all(j[c] for c in CHECKS) for j in js) / len(js), 3),
            "mean_score": round(statistics.mean(j["score"] for j in js), 2),
            "fails_by_check": {c: sum(not j[c] for j in js) for c in CHECKS},
            "words_median": statistics.median(words(t) for t in notes.values()),
        }
    if len(names) == 2:
        a, b = names
        gaps = sorted(((J[(a, s)]["score"] - J[(b, s)]["score"], s) for s in rows if (a, s) in J and (b, s) in J),
                      key=lambda x: -abs(x[0]))[:5]
        res["biggest_gaps"] = [{"id": s, f"{a}_score": J[(a, s)]["score"], f"{b}_score": J[(b, s)]["score"],
                                f"{a}_issue": J[(a, s)]["issue"], f"{b}_issue": J[(b, s)]["issue"],
                                f"{a}_note": R.jload(OUT / f"{a}.json")["notes"][s],
                                f"{b}_note": R.jload(OUT / f"{b}.json")["notes"][s]} for _, s in gaps]
    R.jsave(R.RESULTS / f"explain-{'-vs-'.join(names)}.json", res)
    print(json.dumps({k: v for k, v in res.items() if k != "biggest_gaps"}, indent=1))
    for g in res.get("biggest_gaps", []):
        print(g["id"], {k: v for k, v in g.items() if k.endswith("score") or k.endswith("issue")})


def spotcheck(name, n):
    J = judged([name])
    rows = jl(PAIRS)
    rng = random.Random(2022)
    human = [r for r in rows if r["id"].startswith("H")]
    # Mix: the lowest-scored human item (riskiest) plus random others.
    ordered = sorted(human, key=lambda r: J[(name, r["id"])]["score"])
    pick = [ordered[0]] + rng.sample(ordered[1:], n - 1)
    notes = R.jload(OUT / f"{name}.json")["notes"]
    L = ["# Explain spot check (Day 20)", "",
         f"*{n} Explain notes written by the chosen model ({name}), on human held-out statements and the passage shown "
         "first for each. Item 1 is the note the judge scored lowest; the rest are random. For each, mark **agree** or "
         "**disagree** with the judge's verdict on the Your call line, and add a word on why if you disagree.*", "",
         "Rubric: true to the passage, relevant to what was written, no advice or therapy language, no claims about the "
         "person beyond what they wrote, short (2–4 sentences, at most 90 words). Score 1–5 overall.", ""]
    for i, r in enumerate(sorted(pick, key=lambda r: r["id"]), 1):
        j = J[(name, r["id"])]
        failed = [c for c in CHECKS if not j[c]]
        verdict = "PASSES the rubric" if not failed else "FAILS: " + ", ".join(failed)
        L += [f"## {i}. {r['id']}", "", f"**Statement:** {r['statement']}", "",
              f"**Passage** ({r['work']}, tr. {r['translator']}):", "", f"> {r['passage']}", "",
              f"**In plain words:** {r['plain']}", "", f"**Explain:** {notes[r['id']]}", "",
              f"**Judge:** {verdict}; score {j['score']} of 5. {j['issue']}", "", "**Your call:** agree / disagree", ""]
    (HERE / "explain-spot-check.md").write_text("\n".join(L), encoding="utf-8")
    print("wrote evals/explain-spot-check.md:", ", ".join(r["id"] for r in sorted(pick, key=lambda r: r["id"])))


if __name__ == "__main__":
    cmd, a = (sys.argv[1] if len(sys.argv) > 1 else ""), sys.argv[2:]
    if cmd == "pairs":
        pairs(int(a[0]), a[1])
    elif cmd == "genbatches":
        genbatches(a[0], int(a[1]))
    elif cmd == "collect":
        collect(a[0])
    elif cmd == "judgebatch":
        judgebatch(a)
    elif cmd == "report":
        report(a)
    elif cmd == "spotcheck":
        spotcheck(a[0], int(a[1]))
    else:
        sys.exit(__doc__)
