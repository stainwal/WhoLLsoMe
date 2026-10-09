"""Day 5 blind keep/cut sample: 40 passages drawn at random from the shown corpus.

    python3 evals/build_keep_cut_sample.py     # writes evals/keep-cut-sample.md and keep-cut-sample-key.jsonl

Shailesh marks each passage Keep or Cut against Corpus-Policy section 4 (stands alone; speaks to
a human situation; 1-8 sentences; no mid-sentence cut) without seeing tags, notes or model
reasoning. The key file maps S01-S40 back to passage ids; precision = keeps / 40.
"""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PASSAGES = ROOT / "corpus" / "passages"
MD = ROOT / "evals" / "keep-cut-sample.md"
KEY = ROOT / "evals" / "keep-cut-sample-key.jsonl"
SEED, N = 20261009, 40

ps = []
for f in sorted(PASSAGES.glob("*.jsonl")):
    ps += [json.loads(line) for line in f.open(encoding="utf-8")]
shown = [p for p in ps if p["status"] in ("keep", "no-distress")]
rng = random.Random(SEED)
sample = rng.sample(shown, N)

L = ["# Keep/cut sample (Day 5)", "",
     f"*40 passages drawn at random (seed {SEED}) from the {len(shown):,} passages a user can be shown, on 9 Oct 2026. "
     "Blind: no tags, notes or model reasoning. Judge each against Corpus-Policy section 4: it stands alone, speaks to a human "
     "situation, runs 1–8 sentences, and is not cut mid-sentence. Write K or C in the last column, and a few words if you cut. "
     "The key is in `keep-cut-sample-key.jsonl`.*", "",
     "| # | Source and location | Passage | K / C | Why (if cut) |", "| --- | --- | --- | --- | --- |"]
with KEY.open("w", encoding="utf-8") as k:
    for i, p in enumerate(sample, 1):
        sid = f"S{i:02d}"
        text = p["display_text"].replace("\n", " ").replace("|", "/")
        L.append(f"| {sid} | {p['source']}: {p['display']} | {text} | | |")
        k.write(json.dumps({"sample_id": sid, "pid": p["pid"], "source": p["source"], "words": p["words"]}) + "\n")
MD.write_text("\n".join(L) + "\n", encoding="utf-8")
from collections import Counter
print(f"wrote {MD.relative_to(ROOT)} and key; sources in sample:", dict(Counter(p['source'] for p in sample)))
