"""Verbatim check for extracted passages (Corpus-Policy section 4, rule 7).

    python3 pipeline/extract/check.py <run_dir> <label>

Reads <run_dir>/out/<label>/<chunk>.json (written by the extracting model):
    {"chunk_id": "...", "passages": [{"start_uid": "...", "end_uid": "...", "text": "...", "note": "..."}]}
Writes <run_dir>/<label>-passages.jsonl (accepted) and <label>-rejects.jsonl.
Anything that is not an exact match (whitespace aside) is rejected and logged,
never repaired.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "normalise"))
from common import ROOT, load_units, verbatim_match, squash  # noqa: E402

SENT_END = re.compile(r"[.!?;:…”’\"')\]]$")


def main(run_dir, label):
    run = ROOT / run_dir
    manifest = {c["id"]: c for c in json.loads((run / "manifest.json").read_text())["chunks"]}
    cache, ok, bad = {}, [], []
    for f in sorted((run / "out" / label).glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        chunk = manifest[data.get("chunk_id", f.stem)]
        src = chunk["source"]
        units = cache.setdefault(src, load_units(src))
        by_uid = {u["uid"]: u for u in units}
        for i, p in enumerate(data.get("passages", []), 1):
            text = p.get("text", "")
            res = verbatim_match(text, units, p.get("start_uid"), p.get("end_uid"))
            rec = {"pid": f"{chunk['id']}-p{i:02d}", "chunk": chunk["id"], "source": src,
                   "start_uid": p.get("start_uid"), "end_uid": p.get("end_uid"),
                   "display": by_uid.get(p.get("start_uid"), {}).get("display"),
                   "work": chunk.get("work"), "text": text, "note": p.get("note"),
                   "words": len(text.split()), "check": res}
            if res["ok"]:
                # Soft warnings for review; not rejections.
                warns = []
                if not SENT_END.search(squash(text)):
                    warns.append("may end mid-sentence")
                if res.get("where") != "claimed_range":
                    warns.append("location claim wrong")
                rec["warnings"] = warns
                ok.append(rec)
            else:
                bad.append(rec)
    with (run / f"{label}-passages.jsonl").open("w", encoding="utf-8") as fo:
        for r in ok:
            fo.write(json.dumps(r, ensure_ascii=False) + "\n")
    with (run / f"{label}-rejects.jsonl").open("w", encoding="utf-8") as fo:
        for r in bad:
            fo.write(json.dumps(r, ensure_ascii=False) + "\n")
    total = len(ok) + len(bad)
    warned = sum(1 for r in ok if r["warnings"])
    print(f"{label}: {total} extracted, {len(ok)} exact match, {len(bad)} rejected, {warned} accepted-with-warning")
    return ok, bad


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
