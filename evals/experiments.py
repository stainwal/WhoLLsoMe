"""Retrieval experiments (Plan Days 18-19, section 4.4; 13 Oct 2026).

    .venv/bin/python evals/experiments.py list             # the setups defined below
    .venv/bin/python evals/experiments.py run NAME [...]   # rank every scored statement -> evals/runs/<setup>.json

Each setup writes a run file in the same shape as evals/retrieval.py's, so the same steps follow:
`retrieval.py batches` (judge only passages the pool hasn't seen), the judge, `verify`, then `score`.
Tuning is judged on the agent golden set; held-out sets are reported, never tuned on (Plan section 4.4).

Search covers only what the public site can show (restricted and switched-off sources, and passages hidden
from distress, are left out) and keeps one passage per near-duplicate group, exactly as the baseline does.
Dense search is done here in memory (numpy) on the vectors stored in Supabase; the ranking is identical to
the database's cosine ordering and much faster for 125 statements.
"""

import json
import re
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import retrieval as R  # noqa: E402

DEPTH = 15                 # ranked passages kept per statement (top 10 is scored)
KW_CACHE = HERE / "cache" / "keyword.json"
REWRITES = HERE / "rewrites"
FAITH_WORDS = re.compile(r"\b(god|gods|pray|prayer|prayed|church|faith|lord|jesus|christ|allah|bible|scripture|"
                         r"spiritual|soul|heaven|temple|mosque|synagogue|religious|religion|blessed|sin|karma|dharma)\b", re.I)


class Corpus:
    """Showable passages, their metadata and stored embeddings, loaded once."""

    def __init__(self, db):
        rows = db.execute("""select p.pid, p.near_group, p.quotability, p.faith, p.words
                             from passages p join sources s on s.id = p.source_id
                             where not s.restricted and s.active and not p.hide_in_distress
                             order by p.pid""").fetchall()
        self.pids = [r[0] for r in rows]
        self.meta = {r[0]: {"group": r[1], "quot": r[2], "faith": r[3], "words": r[4]} for r in rows}
        self.index = {p: i for i, p in enumerate(self.pids)}
        self.db, self.vectors = db, {}

    def matrix(self, setup):
        if setup not in self.vectors:
            rows = db_rows = self.db.execute("select pid, embedding::text from passage_embeddings where setup = %s",
                                             (setup,)).fetchall()
            m = np.zeros((len(self.pids), 1024), dtype=np.float32)
            found = 0
            for pid, vec in db_rows:
                if pid in self.index:
                    m[self.index[pid]] = np.array(json.loads(vec), dtype=np.float32); found += 1
            if found != len(self.pids):
                sys.exit(f"{setup}: {found} of {len(self.pids)} showable passages embedded")
            self.vectors[setup] = m / np.linalg.norm(m, axis=1, keepdims=True)
        return self.vectors[setup]


def dense(corpus, setup, queries):
    """{sid: [(pid, cosine)] best first, all showable passages} for query texts {sid: text}."""
    cache, _ = R.embed_queries(list(queries.values()), setup.split("/")[0])
    m = corpus.matrix(setup)
    out = {}
    for sid, text in queries.items():
        q = np.array(cache[text], dtype=np.float32)
        sims = m @ (q / np.linalg.norm(q))
        order = np.argsort(-sims)
        out[sid] = [(corpus.pids[i], float(sims[i])) for i in order]
    return out


def keyword(corpus, statements):
    """Full-text ranks (any word, ts_rank length-normalised), cached; same query as the pooling setup."""
    cache = R.jload(KW_CACHE, {})
    key = lambda s: f"{len(corpus.pids)}|{s['text']}"      # showable set size guards against stale caches
    todo = [s for s in statements if key(s) not in cache]
    for s in todo:
        q = " | ".join(sorted(set(re.findall(r"[a-z]{3,}", s["text"].lower()))))
        rows = corpus.db.execute("""with q as (select to_tsquery('english', %s) as q)
              select p.pid, ts_rank(to_tsvector('english', p.display_text || ' ' || p.plain || ' ' || p.core_idea), q.q, 1) r
              from passages p join sources s on s.id = p.source_id cross join q
              where not s.restricted and s.active and not p.hide_in_distress
                and to_tsvector('english', p.display_text || ' ' || p.plain || ' ' || p.core_idea) @@ q.q
              order by r desc limit 200""", (q,)).fetchall()
        cache[key(s)] = [(p, float(r)) for p, r in rows]
    if todo:
        R.jsave(KW_CACHE, cache)
    return {s["id"]: cache[key(s)] for s in statements}


def finish(corpus, scored):
    """Best-first (pid, score) -> near-duplicate groups collapsed, cut to DEPTH."""
    return R.dedupe([(p, corpus.meta[p]["group"], sc) for p, sc in scored], DEPTH)


def rrf(lists, weights, k=60):
    score = {}
    for lst, w in zip(lists, weights):
        for r, (p, _) in enumerate(lst, 1):
            score[p] = score.get(p, 0) + w / (k + r)
    return sorted(score.items(), key=lambda x: -x[1])


def rewrites(name):
    return {r["id"]: r["query"] for r in R.jload(REWRITES / f"{name}.json")["rewrites"]}


# ---- setups: name -> function(corpus, statements) -> {sid: [(pid, score)] best first} -------------------

BASE = "voyage-4-lite/text+plain"
WHEN = "voyage-4-lite/text+plain+when"


def s_dense(c, st, setup=BASE):
    return dense(c, setup, {s["id"]: s["text"] for s in st})


def s_hybrid(c, st, w_kw=1.0, k=60):
    d, kw = s_dense(c, st), keyword(c, st)
    return {s["id"]: rrf([d[s["id"]][:200], kw[s["id"]]], [1.0, w_kw], k) for s in st}


def s_quot(c, st, w=0.02, base=None):
    """Among close matches, favour short, graspable passages: score + w * (quotability - 3)."""
    d = base(c, st) if base else s_dense(c, st)
    return {sid: sorted(((p, sc + w * (c.meta[p]["quot"] - 3)) for p, sc in lst[:200]), key=lambda x: -x[1])
            for sid, lst in d.items()}


def s_rewrite(c, st, mode="rewrite", name="opus-v1", setup=BASE):
    rw = rewrites(name)
    if mode == "rewrite":
        return dense(c, setup, {s["id"]: rw[s["id"]] for s in st})
    if mode == "concat":
        return dense(c, setup, {s["id"]: s["text"] + "\n\n" + rw[s["id"]] for s in st})
    a, b = s_dense(c, st, setup), dense(c, setup, {s["id"]: rw[s["id"]] for s in st})   # mode "fuse": RRF of both
    return {s["id"]: rrf([a[s["id"]][:200], b[s["id"]][:200]], [1.0, 1.0]) for s in st}


def s_faith(c, st, w=0.03):
    """Statements with no faith words: devotional passages pushed down by w (spiritual by w/2)."""
    d = s_dense(c, st)
    out = {}
    for s in st:
        if FAITH_WORDS.search(s["text"]):
            out[s["id"]] = d[s["id"]]
            continue
        pen = {"devotional": w, "spiritual": w / 2, "secular": 0}
        out[s["id"]] = sorted(((p, sc - pen[c.meta[p]["faith"]]) for p, sc in d[s["id"]][:200]), key=lambda x: -x[1])
    return out


# Tone prior (added 13 Oct): how much more (or less) often a passage with each tone tag was judged acceptable
# than average, measured on the agent GOLDEN set only (25% overall), so held-out sets stay untouched.
TONE = {"stern": -0.19, "challenging": -0.10, "contemplative": -0.05, "practical": -0.01, "steadying": 0.01,
        "companioning": 0.06, "affirming": 0.07, "uplifting": 0.13, "consoling": 0.21}


def tone_meta(c):
    if not hasattr(c, "tone"):
        c.tone = {p: t for p, t in c.db.execute("select pid, tags->'tone' from passages")}
    return c.tone


def s_tone(c, st, u=0.1, base=None):
    """score + u * mean tone prior of the passage's tones (cosine-scale setups only)."""
    d, tone = (base(c, st) if base else s_dense(c, st)), tone_meta(c)
    prior = lambda p: sum(TONE[t] for t in tone[p]) / len(tone[p]) if tone[p] else 0
    return {sid: sorted(((p, sc + u * prior(p)) for p, sc in lst[:200]), key=lambda x: -x[1]) for sid, lst in d.items()}


SETUPS = {
    BASE: s_dense,
    "hybrid/rrf": s_hybrid,
    "hybrid/rrf-kw0.5": lambda c, st: s_hybrid(c, st, w_kw=0.5),
    "quot/0.01": lambda c, st: s_quot(c, st, 0.01),
    "quot/0.02": lambda c, st: s_quot(c, st, 0.02),
    "quot/0.04": lambda c, st: s_quot(c, st, 0.04),
    "rewrite/only": lambda c, st: s_rewrite(c, st, "rewrite"),
    "rewrite/concat": lambda c, st: s_rewrite(c, st, "concat"),
    "rewrite/fuse": lambda c, st: s_rewrite(c, st, "fuse"),
    "voyage-4-lite/text": lambda c, st: s_dense(c, st, "voyage-4-lite/text"),
    "voyage-4-lite/plain": lambda c, st: s_dense(c, st, "voyage-4-lite/plain"),
    "voyage-4-lite/text+plain+when": lambda c, st: s_dense(c, st, "voyage-4-lite/text+plain+when"),
    "voyage-4/text+plain": lambda c, st: s_dense(c, st, "voyage-4/text+plain"),
    "tone/0.1": lambda c, st: s_tone(c, st, 0.1),
    "tone/0.2": lambda c, st: s_tone(c, st, 0.2),
    "tone/0.4": lambda c, st: s_tone(c, st, 0.4),
    "rewrite-concat+tone/0.2": lambda c, st: s_tone(c, st, 0.2, lambda c, st: s_rewrite(c, st, "concat")),
    "rewrite-only+tone/0.2": lambda c, st: s_tone(c, st, 0.2, lambda c, st: s_rewrite(c, st, "rewrite")),
    "when+tone/0.1": lambda c, st: s_tone(c, st, 0.1, lambda c, st: s_dense(c, st, WHEN)),
    "when+tone/0.2": lambda c, st: s_tone(c, st, 0.2, lambda c, st: s_dense(c, st, WHEN)),
    "when+rewrite-concat": lambda c, st: s_rewrite(c, st, "concat", setup=WHEN),
    "when+rewrite-concat+tone/0.2": lambda c, st: s_tone(c, st, 0.2, lambda c, st: s_rewrite(c, st, "concat", setup=WHEN)),
    # Setup B with runtime-model rewrites (experiment 5, Day 20)
    "B/haiku": lambda c, st: s_tone(c, st, 0.2, lambda c, st: s_rewrite(c, st, "concat", "haiku-v1", WHEN)),
    "B/sonnet": lambda c, st: s_tone(c, st, 0.2, lambda c, st: s_rewrite(c, st, "concat", "sonnet-v1", WHEN)),
    "faith/0.03": lambda c, st: s_faith(c, st, 0.03),
    "faith/0.06": lambda c, st: s_faith(c, st, 0.06),
}


def run(names):
    statements = R.scored_statements()
    with R.load.connect() as db:
        corpus = Corpus(db)
        for name in names:
            if name not in SETUPS:
                sys.exit(f"unknown setup {name}; see `list`")
            t0 = time.time()
            ranked = {sid: finish(corpus, lst) for sid, lst in SETUPS[name](corpus, statements).items()}
            R.jsave(R.RUNS / f"{name.replace('/', '__')}.json",
                    {"setup": name, "depth": DEPTH, "run_at": time.strftime("%Y-%m-%d %H:%M"),
                     "showable": len(corpus.pids), "ranked": ranked})
            print(f"{name}: {len(ranked)} statements ranked in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "list":
        print("\n".join(SETUPS))
    elif cmd == "run":
        run(sys.argv[2:])
    else:
        sys.exit(__doc__)
