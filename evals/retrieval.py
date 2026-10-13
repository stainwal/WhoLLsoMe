"""Retrieval eval harness (Plan Day 17, sections 4.1-4.2; 13 Oct 2026).

    .venv/bin/python evals/retrieval.py pool                 # run the pooling setups -> evals/runs/<setup>.json
    .venv/bin/python evals/retrieval.py batches SIZE         # unlabelled (statement, passage) pairs -> evals/judge-in/bNN.jsonl
    .venv/bin/python evals/retrieval.py verify               # check judge output (evals/judge/bNN.json) -> evals/labels.json
    .venv/bin/python evals/retrieval.py score [SETUP ...]    # hit@3, hit@10, MRR per set and part -> evals/results/
    .venv/bin/python evals/retrieval.py spotcheck N          # N human statements for Shailesh -> evals/judge-spot-check.md
    .venv/bin/python evals/retrieval.py recheck PCT SIZE     # random PCT% of labelled pairs, for a fresh judge -> evals/judge-in/rNN.jsonl
    .venv/bin/python evals/retrieval.py xbatches SETUP K NAME  # every statement's top K for a second model -> evals/judge-in/xNAME-NN.jsonl
    .venv/bin/python evals/retrieval.py xcompare NAME SETUP    # second model (evals/judge/xNAME-NN.json) vs labels -> evals/results/cross-NAME.json
    .venv/bin/python evals/retrieval.py consistency          # second judge (evals/judge/rNN.json) vs labels -> evals/results/judge-consistency.json

Which statements are scored: every statement except the crisis part (those must route to helplines, and
no passage is shown). Borderline statements and look-alikes are scored. Sets are read through
evals/sets.py, never from the .jsonl files directly.

What the public site can show is what gets searched: restricted and switched-off sources are left out,
passages hidden from distress are left out (no distress check exists yet, so every statement is treated as
possibly in distress), and no two passages from one near-duplicate group appear in a list.

Labels are pooled (Plan section 4.1): the judge grades every passage that any pooling setup put in its top
POOL depth for a statement. **An unjudged passage is never counted as a miss.** A later setup is saved as a run
file in evals/runs/; `batches` then picks up every passage in its top 10 that the pool hasn't judged, and
`score` refuses to score a setup while any passage in its top 10 is still unjudged.
Grades: 3 strong, 2 acceptable, 1 loosely related, 0 off-topic or unsuitable. Acceptable means 2 or 3.
"""

import json
import os
import random
import re
import statistics
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "backend"))
import load  # noqa: E402
import sets  # noqa: E402

RUNS, JUDGE_IN, JUDGE, RESULTS = HERE / "runs", HERE / "judge-in", HERE / "judge", HERE / "results"
LABELS, CACHE = HERE / "labels.json", HERE / "cache" / "query-embeddings.json"
TOP, ACCEPT = 10, 2                                   # a user can step through 10; grade >= 2 is acceptable
POOL = {"voyage-4-lite/text+plain": 15, "keyword/fts": 10}   # pooling setups and how deep each is judged
VOYAGE_PRICE = 0.02                                   # USD per 1M tokens, voyage-4-lite (list price, 13 Oct 2026)

def scored_statements():
    out = []
    for name in ("human", "agent"):
        out += [r for r in sets.load_set(name) if r["part"] != "crisis"]
    return out


def jload(path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def jsave(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def dedupe(rows, n):
    """Keep rank order; drop a passage whose near-duplicate group already appeared."""
    seen, out = set(), []
    for pid, group, score in rows:
        if group and group in seen:
            continue
        seen.add(group)
        out.append((pid, round(float(score), 4)))
        if len(out) == n:
            break
    return out


# ---- setups -------------------------------------------------------------------------------------------

def embed_queries(texts):
    """Voyage query embeddings, cached by statement text so re-runs cost nothing."""
    cache = jload(CACHE, {})
    todo = [t for t in texts if t not in cache]
    tokens = 0
    if todo:
        load.load_dotenv(ROOT / ".env")
        body = json.dumps({"input": todo, "model": "voyage-4-lite", "input_type": "query",
                           "output_dimension": 1024}).encode()
        req = urllib.request.Request("https://api.voyageai.com/v1/embeddings", body,
                                     {"Authorization": f"Bearer {os.environ['VOYAGE_API_KEY']}",
                                      "Content-Type": "application/json"})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=120) as r:
            out = json.load(r)
        print(f"  embedded {len(todo)} statements in {time.time() - t0:.1f}s, {out['usage']['total_tokens']:,} tokens")
        tokens = out["usage"]["total_tokens"]
        for t, d in zip(todo, sorted(out["data"], key=lambda d: d["index"])):
            cache[t] = d["embedding"]
        jsave(CACHE, cache)
    return cache, tokens


def run_dense(db, statements, setup, depth):
    cache, tokens = embed_queries([s["text"] for s in statements])
    out, times = {}, []
    for s in statements:
        t0 = time.time()
        rows = db.execute("""select p.pid, p.near_group, 1 - (e.embedding <=> %s::vector)
                             from passages p join sources s on s.id = p.source_id
                             join passage_embeddings e on e.pid = p.pid and e.setup = %s
                             where not s.restricted and s.active and not p.hide_in_distress
                             order by e.embedding <=> %s::vector limit 60""",
                          (str(cache[s["text"]]), setup, str(cache[s["text"]]))).fetchall()
        times.append(time.time() - t0)
        out[s["id"]] = dedupe(rows, depth)
    return out, {"db_ms_median": round(statistics.median(times) * 1000), "query_tokens": tokens}


def run_keyword(db, statements, depth):
    """Postgres full-text search: any of the statement's words, ranked by ts_rank (length-normalised)."""
    out = {}
    for s in statements:
        q = " | ".join(sorted(set(re.findall(r"[a-z]{3,}", s["text"].lower()))))
        rows = db.execute("""with q as (select to_tsquery('english', %s) as q)
                             select p.pid, p.near_group,
                                    ts_rank(to_tsvector('english', p.display_text || ' ' || p.plain || ' ' || p.core_idea), q.q, 1) r
                             from passages p join sources s on s.id = p.source_id cross join q
                             where not s.restricted and s.active and not p.hide_in_distress
                              and to_tsvector('english', p.display_text || ' ' || p.plain || ' ' || p.core_idea) @@ q.q
                              order by r desc limit 60""", (q,)).fetchall()
        out[s["id"]] = dedupe(rows, depth)
    return out, {}


def pool():
    statements = scored_statements()
    with load.connect() as db:
        for setup, depth in POOL.items():
            t0 = time.time()
            ranked, info = (run_keyword(db, statements, depth) if setup.startswith("keyword")
                            else run_dense(db, statements, setup, depth))
            jsave(RUNS / f"{setup.replace('/', '__')}.json",
                  {"setup": setup, "depth": depth, "run_at": time.strftime("%Y-%m-%d %H:%M"), **info,
                   "ranked": ranked})
            print(f"{setup}: {len(ranked)} statements, top {depth} each, {time.time() - t0:.1f}s {info}")
    pairs = pooled_pairs()
    print(f"pool: {sum(len(v) for v in pairs.values()):,} unique (statement, passage) pairs "
          f"over {len(pairs)} statements")


def pooled_pairs():
    pairs = {}
    for f in sorted(RUNS.glob("*.json")):
        r = jload(f)
        for sid, ranked in r["ranked"].items():
            pairs.setdefault(sid, set()).update(pid for pid, _ in ranked[:POOL.get(r["setup"], TOP)])
    return pairs


# ---- judging ------------------------------------------------------------------------------------------

def batches(size):
    labels = jload(LABELS, {})
    claimed = set()
    for f in JUDGE_IN.glob("b*.jsonl"):
        if not (JUDGE / f"{f.stem}.json").exists():
            claimed |= {json.loads(l)["id"] for l in f.read_text().splitlines() if l.strip()}
    pairs = pooled_pairs()
    todo = {sid: sorted(pids - set(labels.get(sid, {}))) for sid, pids in pairs.items() if sid not in claimed}
    todo = {k: v for k, v in todo.items() if v}
    by_id = {s["id"]: s for s in scored_statements()}
    with load.connect() as db:
        text = {pid: (dt, pl) for pid, dt, pl in db.execute("select pid, display_text, plain from passages")}
    n = max([int(f.stem[1:]) for f in JUDGE_IN.glob("b*.jsonl")] or [0])
    ids = sorted(todo)
    rng = random.Random(17)
    made = []
    for i in range(0, len(ids), size):
        n += 1
        lines = []
        for sid in ids[i:i + size]:
            cands = todo[sid][:]
            rng.shuffle(cands)              # the judge never sees rank or setup
            lines.append({"id": sid, "statement": by_id[sid]["text"],
                          "passages": [{"pid": p, "text": text[p][0], "plain": text[p][1]} for p in cands]})
        path = JUDGE_IN / f"b{n:02d}.jsonl"
        path.parent.mkdir(exist_ok=True)
        path.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lines), encoding="utf-8")
        made.append((path.name, len(lines), sum(len(l["passages"]) for l in lines),
                     sum(len(l["statement"].split()) + sum(len((p["text"] + " " + p["plain"]).split())
                                                           for p in l["passages"]) for l in lines)))
    for name, st, ps, w in made:
        print(f"{name}: {st} statements, {ps} passages, {w:,} words")
    print(f"{len(made)} batches, {sum(m[2] for m in made):,} pairs, {sum(m[3] for m in made):,} words")


def verify():
    labels = jload(LABELS, {})
    added, problems = 0, []
    for f in sorted(JUDGE_IN.glob("b*.jsonl")):
        out = JUDGE / f"{f.stem}.json"
        if not out.exists():
            continue
        want = {(l["id"], p["pid"]) for l in map(json.loads, f.read_text().splitlines()) for p in l["passages"]}
        got = {}
        for j in jload(out)["judgements"]:
            ok = isinstance(j.get("grade"), int) and 0 <= j["grade"] <= 3 and isinstance(j.get("reason"), str)
            if (j.get("id"), j.get("pid")) not in want or not ok:
                problems.append(f"{out.name}: bad or unexpected item {j.get('id')}/{j.get('pid')}")
                continue
            got[(j["id"], j["pid"])] = {"grade": j["grade"], "reason": j["reason"].strip(), "batch": f.stem}
        missing = want - set(got)
        if missing:
            problems.append(f"{out.name}: {len(missing)} pairs not judged, e.g. {sorted(missing)[:3]}")
        for (sid, pid), v in got.items():
            if pid not in labels.setdefault(sid, {}):
                added += 1
            labels[sid][pid] = v
    jsave(LABELS, labels)
    n = sum(len(v) for v in labels.values())
    acc = sum(v["grade"] >= ACCEPT for d in labels.values() for v in d.values())
    print(f"labels: {n:,} pairs over {len(labels)} statements ({added:,} new); acceptable {acc:,} ({acc / max(n, 1):.0%})")
    for p in problems:
        print("PROBLEM", p)
    sys.exit(1 if problems else 0)


def recheck(pct, size):
    """A random pct% of labelled pairs, grouped by statement, for a second judge in a fresh context.
    Written as rNN.jsonl so `verify` never merges them into the labels."""
    labels = jload(LABELS, {})
    pairs = sorted((sid, pid) for sid, d in labels.items() for pid in d)
    rng = random.Random(1713)
    pick = rng.sample(pairs, round(len(pairs) * pct / 100))
    by_sid = {}
    for sid, pid in pick:
        by_sid.setdefault(sid, []).append(pid)
    by_id = {s["id"]: s for s in scored_statements()}
    with load.connect() as db:
        text = {pid: (dt, pl) for pid, dt, pl in db.execute("select pid, display_text, plain from passages")}
    ids, n = sorted(by_sid), 0
    for i in range(0, len(ids), size):
        n += 1
        lines = []
        for sid in ids[i:i + size]:
            cands = by_sid[sid][:]
            rng.shuffle(cands)
            lines.append({"id": sid, "statement": by_id[sid]["text"],
                          "passages": [{"pid": p, "text": text[p][0], "plain": text[p][1]} for p in cands]})
        (JUDGE_IN / f"r{n:02d}.jsonl").write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lines),
                                                  encoding="utf-8")
    print(f"recheck: {len(pick)} of {len(pairs):,} pairs ({pct}%), {len(ids)} statements, {n} files r01-r{n:02d}")


def xbatches(setup, k, name, size=45):
    """A second judge model re-grades every statement's top K of one setup (Opus stays judge of record)."""
    run = jload(RUNS / f"{setup.replace('/', '__')}.json")
    by_id = {s["id"]: s for s in scored_statements()}
    with load.connect() as db:
        text = {pid: (dt, pl) for pid, dt, pl in db.execute("select pid, display_text, plain from passages")}
    rng, ids = random.Random(1813), sorted(by_id)
    for n, i in enumerate(range(0, len(ids), size), 1):
        lines = []
        for sid in ids[i:i + size]:
            cands = [pid for pid, _ in run["ranked"][sid][:k]]
            rng.shuffle(cands)
            lines.append({"id": sid, "statement": by_id[sid]["text"],
                          "passages": [{"pid": p, "text": text[p][0], "plain": text[p][1]} for p in cands]})
        (JUDGE_IN / f"x{name}-{n:02d}.jsonl").write_text(
            "".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lines), encoding="utf-8")
        print(f"x{name}-{n:02d}.jsonl: {len(lines)} statements, {sum(len(l['passages']) for l in lines)} pairs")


def xcompare(name, setup):
    labels, run = jload(LABELS, {}), jload(RUNS / f"{setup.replace('/', '__')}.json")
    second = {}
    for f in sorted(JUDGE.glob(f"x{name}-*.json")):
        want = {(l["id"], p["pid"]) for l in map(json.loads, (JUDGE_IN / f"{f.stem}.jsonl").read_text().splitlines())
                for p in l["passages"]}
        got = {(j["id"], j["pid"]): j for j in jload(f)["judgements"]}
        if set(got) != want:
            sys.exit(f"{f.name}: judged pairs don't match its input ({len(want ^ set(got))} differ)")
        second.update(got)
    sets_of = {s["id"]: s for s in scored_statements()}
    out = {"model": name, "setup": setup, "checked_at": time.strftime("%Y-%m-%d %H:%M"), "by_set": {}}
    for name_set in ("human", "agent", "all"):
        pairs = [(labels[sid][pid]["grade"], j["grade"]) for (sid, pid), j in second.items()
                 if name_set == "all" or sets_of[sid]["set"] == name_set]
        sids = [sid for sid in sets_of if name_set == "all" or sets_of[sid]["set"] == name_set]
        def top(lab_of):
            hit3 = sum(any(lab_of(sid, p) >= ACCEPT for p, _ in run["ranked"][sid][:3]) for sid in sids)
            t1ok = sum(lab_of(sid, run["ranked"][sid][0][0]) >= ACCEPT for sid in sids)
            t1zero = sum(lab_of(sid, run["ranked"][sid][0][0]) == 0 for sid in sids)
            return {"hit@3": hit3, "top1_acceptable": t1ok, "top1_graded_0": t1zero}
        n = len(pairs)
        out["by_set"][name_set] = {
            "statements": len(sids), "pairs": n,
            "exact_grade_agreement": round(sum(a == b for a, b in pairs) / n, 3),
            "within_one_grade": round(sum(abs(a - b) <= 1 for a, b in pairs) / n, 3),
            "acceptable_agreement": round(sum((a >= ACCEPT) == (b >= ACCEPT) for a, b in pairs) / n, 3),
            "acceptable_rate_opus": round(sum(a >= ACCEPT for a, _ in pairs) / n, 3),
            "acceptable_rate_second": round(sum(b >= ACCEPT for _, b in pairs) / n, 3),
            "opus_labels": top(lambda sid, p: labels[sid][p]["grade"]),
            "second_labels": top(lambda sid, p: second[(sid, p)]["grade"])}
    # biggest disagreements: grade gap, then whether they split on acceptable, then rank shown
    rank = {(sid, pid): i + 1 for sid in sets_of for i, (pid, _) in enumerate(run["ranked"][sid][:3])}
    dis = sorted(((abs(labels[sid][pid]["grade"] - j["grade"]),
                   (labels[sid][pid]["grade"] >= ACCEPT) != (j["grade"] >= ACCEPT), -rank[(sid, pid)], sid, pid)
                  for (sid, pid), j in second.items()), reverse=True)
    out["biggest_disagreements"] = [
        {"id": sid, "pid": pid, "rank": -r, "opus": labels[sid][pid], "second": second[(sid, pid)]}
        for gap, split, r, sid, pid in dis[:10] if gap > 0]
    jsave(RESULTS / f"cross-{name}.json", out)
    print(json.dumps(out["by_set"], indent=1))
    return out


def consistency():
    labels = jload(LABELS, {})
    pairs = []
    for f in sorted(JUDGE.glob("r*.json")):
        want = {(l["id"], p["pid"]) for l in map(json.loads, (JUDGE_IN / f"{f.stem}.jsonl").read_text().splitlines())
                for p in l["passages"]}
        got = {(j["id"], j["pid"]): j["grade"] for j in jload(f)["judgements"]}
        if set(got) != want:
            sys.exit(f"{f.name}: judged pairs don't match its input ({len(want ^ set(got))} differ)")
        pairs += [(labels[sid][pid]["grade"], g) for (sid, pid), g in got.items()]
    n = len(pairs)
    exact = sum(a == b for a, b in pairs)
    within1 = sum(abs(a - b) <= 1 for a, b in pairs)
    binary = sum((a >= ACCEPT) == (b >= ACCEPT) for a, b in pairs)
    # Cohen's kappa on acceptable / not: agreement beyond what chance would give
    p1, p2 = sum(a >= ACCEPT for a, _ in pairs) / n, sum(b >= ACCEPT for _, b in pairs) / n
    pe = p1 * p2 + (1 - p1) * (1 - p2)
    kappa = (binary / n - pe) / (1 - pe)
    matrix = {f"{a}->{b}": sum(1 for x, y in pairs if (x, y) == (a, b)) for a in range(4) for b in range(4)}
    out = {"checked_at": time.strftime("%Y-%m-%d %H:%M"), "pairs": n,
           "exact_grade_agreement": round(exact / n, 3), "within_one_grade": round(within1 / n, 3),
           "acceptable_agreement": round(binary / n, 3), "acceptable_kappa": round(kappa, 3),
           "acceptable_rate_first": round(p1, 3), "acceptable_rate_second": round(p2, 3),
           "first_to_second_grade_counts": {k: v for k, v in matrix.items() if v}}
    jsave(RESULTS / "judge-consistency.json", out)
    print(json.dumps(out, indent=1))


# ---- scoring ------------------------------------------------------------------------------------------

def table(summary, groups=None):
    """Plain-text results table: the two top-1 metrics first, then hit@3, hit@10, MRR."""
    pct = lambda v, k: f"{v[k]:>3} ({v[k] / v['n']:>4.0%})"
    out = [f"{'group':18} {'n':>3}  {'top-1 ok':>10}  {'top-1 = 0':>10}  {'hit@3':>10}  {'hit@10':>10}  {'MRR':>5}"]
    for k, v in summary.items():
        if groups is None or k in groups:
            out.append(f"{k:18} {v['n']:>3}  {pct(v, 'top1_ok')}  {pct(v, 'top1_zero')}  {pct(v, 'hit@3')}  "
                       f"{pct(v, 'hit@10')}  {v['mrr']:>5.3f}")
    return "\n".join(out)


def score(setups):
    labels = jload(LABELS, {})
    statements = scored_statements()
    RESULTS.mkdir(exist_ok=True)
    for setup in setups or ["voyage-4-lite/text+plain"]:
        run = jload(RUNS / f"{setup.replace('/', '__')}.json")
        rows = {}
        unjudged = [(s["id"], pid) for s in statements for pid, _ in run["ranked"][s["id"]][:TOP]
                    if pid not in labels.get(s["id"], {})]
        if unjudged:
            sys.exit(f"{setup}: {len(unjudged)} passages in its top {TOP} are unjudged (e.g. {unjudged[:3]}); "
                     "an unjudged passage is never scored as a miss. Run `batches`, the judge, then `verify` first.")
        for s in statements:
            ranked = [pid for pid, _ in run["ranked"][s["id"]][:TOP]]
            lab = labels.get(s["id"], {})
            first = next((i + 1 for i, pid in enumerate(ranked) if lab.get(pid, {}).get("grade", 0) >= ACCEPT), None)
            rows[s["id"]] = {"set": s["set"], "part": s["part"], "first_acceptable": first,
                             "top1_grade": lab[ranked[0]]["grade"], "top3": ranked[:3]}
        groups = {}
        for sid, r in rows.items():
            for key in (f"{r['set']}/{r['part']}", f"{r['set']}/all"):
                groups.setdefault(key, []).append((r["first_acceptable"], r["top1_grade"]))
        # Main targets (Shailesh, 13 Oct): top-1 acceptable and top-1 graded 0 (what a user sees first), with hit@3.
        summary = {k: {"n": len(v),
                       "top1_ok": sum(1 for x, _ in v if x == 1),
                       "top1_zero": sum(1 for _, g in v if g == 0),
                       "hit@3": sum(1 for x, _ in v if x and x <= 3),
                       "hit@10": sum(1 for x, _ in v if x),
                       "mrr": round(sum(1 / x for x, _ in v if x) / len(v), 3)}
                   for k, v in sorted(groups.items())}
        cost = run.get("query_tokens", 0) / max(len(statements), 1) * 1000 / 1e6 * VOYAGE_PRICE
        out = {"setup": setup, "scored_at": time.strftime("%Y-%m-%d %H:%M"), "statements": len(statements),
               "embed_cost_per_1000_queries_usd": round(cost, 4),
               "db_ms_median": run.get("db_ms_median"), "summary": summary, "per_statement": rows}
        jsave(RESULTS / f"{setup.replace('/', '__')}.json", out)
        print(f"\n{setup}  (embed cost ${cost:.4f} per 1,000 queries; "
              f"search {run.get('db_ms_median')} ms median)")
        print(table(summary))


# ---- spot check ---------------------------------------------------------------------------------------

def spotcheck(n):
    """N human held-out statements, one judged passage each, for Shailesh to agree or disagree with.
    The item is the baseline's top-ranked passage (what a user would see first), so the check covers
    both acceptable and unacceptable verdicts on the passages that matter most."""
    labels = jload(LABELS, {})
    run = jload(RUNS / "voyage-4-lite__text+plain.json")
    by_id = {s["id"]: s for s in scored_statements()}
    with load.connect() as db:
        info = {pid: (disp, dt, pl, w, tr) for pid, disp, dt, pl, w, tr in db.execute(
            "select p.pid, p.display, p.display_text, p.plain, s.work, s.translator "
            "from passages p join sources s on s.id = p.source_id")}
    cands = [s for s in by_id.values() if s["set"] == "human" and s["part"] == "held-out"]
    rng = random.Random(1013)
    rng.shuffle(cands)
    # Half judged acceptable, half not, where the set allows: the check must test both kinds of verdict.
    ok = [s for s in cands if labels[s["id"]][run["ranked"][s["id"]][0][0]]["grade"] >= ACCEPT]
    no = [s for s in cands if s not in ok]
    k = min(max(n // 2, n - len(no)), len(ok))
    picked = sorted(ok[:k] + no[:n - k], key=lambda s: s["id"])
    lines = ["# Judge spot check (Day 17)", "",
             f"*{n} human held-out statements, drawn at random (seed 1013), half where the judge accepted the passage and half where it didn't. For each, the passage the baseline search "
             "shows first, and the AI judge's verdict on it. Mark each one **agree** or **disagree** in the "
             "Your call line. The judge's labels stand if you agree with at least 6 of 8 (Plan section 4.1).*", "",
             "Grades: 3 strong match, 2 acceptable, 1 loosely related, 0 off-topic or unsuitable. "
             "**Acceptable means 2 or 3.**", ""]
    for i, s in enumerate(picked, 1):
        pid = run["ranked"][s["id"]][0][0]
        disp, dt, pl, work, tr = info[pid]
        lab = labels[s["id"]][pid]
        verdict = "ACCEPTABLE" if lab["grade"] >= ACCEPT else "NOT acceptable"
        lines += [f"## {i}. {s['id']}", "",
                  f"**Statement:** {s['text']}", "",
                  f"**Passage** ({disp}, {work}, tr. {tr}):", "", f"> {dt}", "",
                  f"**In plain words:** {pl}", "",
                  f"**Judge:** grade {lab['grade']}, {verdict}. {lab['reason']}", "",
                  "**Your call:** agree / disagree", ""]
    (HERE / "judge-spot-check.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote evals/judge-spot-check.md: {', '.join(s['id'] for s in picked)}")


if __name__ == "__main__":
    cmd, args = (sys.argv[1] if len(sys.argv) > 1 else ""), sys.argv[2:]
    if cmd == "pool":
        pool()
    elif cmd == "batches":
        batches(int(args[0]) if args else 8)
    elif cmd == "verify":
        verify()
    elif cmd == "score":
        score(args)
    elif cmd == "recheck":
        recheck(float(args[0]) if args else 10, int(args[1]) if len(args) > 1 else 60)
    elif cmd == "xbatches":
        xbatches(args[0], int(args[1]), args[2])
    elif cmd == "xcompare":
        xcompare(args[0], args[1])
    elif cmd == "consistency":
        consistency()
    elif cmd == "spotcheck":
        spotcheck(int(args[0]) if args else 8)
    else:
        sys.exit(__doc__)
