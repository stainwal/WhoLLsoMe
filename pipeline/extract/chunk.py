"""Cut normalised units into extraction chunks (Corpus-Policy section 7, step 3).

    python3 pipeline/extract/chunk.py <run_dir> <source> [--work W] [--lecture L] [--words 2500]

Chunks never split a unit. Each chunk is a text file the extracting model reads:
every unit is prefixed with its uid so passages can be traced back exactly.
Headings are shown (marked) for context. A manifest.json lists the chunks.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "normalise"))
from common import ROOT, is_active, load_units  # noqa: E402


def select(units, work=None, lecture=None):
    out = [u for u in units if (work is None or u.get("work") == work)]
    if lecture:
        keep, on = [], False
        for u in out:
            if u["kind"] == "heading" and "title" in u["loc"]:
                on = u["text"] == lecture
            if on:
                keep.append(u)
        out = keep
    return out


def render(u) -> str:
    if u["kind"] == "heading":
        return f"[{u['uid']}] ## {u['text']}"
    return f"[{u['uid']}] ({u['display']})\n{u['text']}"


def make_chunks(units, words=2500):
    chunks, cur, n = [], [], 0
    for u in units:
        w = len(u["text"].split())
        if cur and n + w > words and u["kind"] != "heading":
            chunks.append(cur)
            cur, n = [], 0
        cur.append(u)
        n += w if u["kind"] != "heading" else 0
    if cur:
        if chunks and sum(len(x["text"].split()) for x in cur) < words * 0.3:
            chunks[-1].extend(cur)  # fold a small tail into the previous chunk
        else:
            chunks.append(cur)
    return chunks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("source")
    ap.add_argument("--work")
    ap.add_argument("--lecture")
    ap.add_argument("--words", type=int, default=2500)
    ap.add_argument("--prefix", default=None)
    a = ap.parse_args()

    if not is_active(a.source):
        sys.exit(f"{a.source} is switched off in pipeline/sources.toml")
    run = ROOT / a.run_dir
    (run / "chunks").mkdir(parents=True, exist_ok=True)
    units = select(load_units(a.source), a.work, a.lecture)
    prefix = a.prefix or a.source
    man_path = run / "manifest.json"
    manifest = json.loads(man_path.read_text()) if man_path.exists() else {"chunks": []}
    manifest["chunks"] = [c for c in manifest["chunks"] if not c["id"].startswith(prefix + "-")]
    for i, c in enumerate(make_chunks(units, a.words), 1):
        cid = f"{prefix}-{i:03d}"
        body = "\n\n".join(render(u) for u in c)
        (run / "chunks" / f"{cid}.txt").write_text(body + "\n", encoding="utf-8")
        wc = sum(len(u["text"].split()) for u in c if u["kind"] != "heading")
        manifest["chunks"].append({"id": cid, "source": a.source, "work": c[0].get("work"),
                                   "first_uid": c[0]["uid"], "last_uid": c[-1]["uid"],
                                   "units": len(c), "words": wc})
        print(f"{cid}: {len(c)} units, {wc} words")
    man_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
