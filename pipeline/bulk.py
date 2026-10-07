"""Bulk corpus run (Plan Days 7-11; Corpus-Policy section 7, steps 2-6).

    python3 pipeline/bulk.py prep              # chunk every active source, in priority order
    python3 pipeline/bulk.py status            # progress: chunks, words, passages, tags
    python3 pipeline/bulk.py packs N SIZE      # claim the next N packs of SIZE pending chunks
    python3 pipeline/bulk.py check             # verbatim check of every extraction file
    python3 pipeline/bulk.py tagbatches N SIZE # claim N batches of SIZE checked, untagged passages
    python3 pipeline/bulk.py merge             # passages + tags -> corpus/passages/<source>.jsonl, cut list

Everything lives in corpus/passages/bulk/. Progress is saved per chunk and per tag
batch, so an interruption resumes where it stopped: a claim that has produced no
output after CLAIM_TTL minutes is released and handed out again.
"""

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "normalise"))
sys.path.insert(0, str(HERE / "extract"))
sys.path.insert(0, str(HERE / "tag"))
from common import ROOT, is_active, load_units, verbatim_match, squash  # noqa: E402
from chunk import make_chunks, render  # noqa: E402
from check import SENT_END  # noqa: E402
from compare import vocab, LIMITS  # noqa: E402

RUN = ROOT / "corpus" / "passages" / "bulk"
CHUNKS, EXTRACT, TAG_IN, TAGS = RUN / "chunks", RUN / "extract", RUN / "tag-in", RUN / "tags"
MANIFEST, CLAIMS = RUN / "manifest.json", RUN / "claims.json"
PILOT = ROOT / "corpus" / "passages" / "pilot"
CLAIM_TTL = 90 * 60
WORDS = 2500

BIBLE_FIRST = ["Psalms", "Proverbs", "Ecclesiastes"]
# Pre-filter (Corpus-Policy section 7, step 2): books that are almost entirely law codes,
# census lists or genealogy are not sent to the model.
BIBLE_SKIP = {"Leviticus", "Numbers", "1 Chronicles"}

# Priority order agreed with Shailesh, 7 Oct 2026. Each entry: (tier, source, filter, prefix).
# filter is None (whole source), ("work", name) or ("book", name).
TIER1 = [("gita-arnold-song-celestial", None, "gita-arnold"),
         ("gita-sivananda", None, "gita-siva"),
         ("suttacentral-sujato", ("work", "Dhammapada"), "dhp"),
         *[("bible-web", ("book", b), "bib-" + b.lower()[:3]) for b in BIBLE_FIRST],
         ("meditations-long", None, "meditations"),
         ("epictetus-enchiridion", None, "enchiridion"),
         ("tao-te-ching-legge", None, "tao"),
         ("prophet-gibran", None, "prophet"),
         ("pirkei-avot", None, "avot")]
TIER2 = [(s, None, s) for s in [
    "upanishads-paramananda", "as-a-man-thinketh-allen", "epictetus-discourses-long", "japji-macauliffe",
    "imitation-of-christ-benham", "light-of-asia-arnold", "soul-of-the-indian-eastman", "eckhart-sermons-field",
    "schopenhauer-counsels-maxims", "schopenhauer-wisdom-of-life", "emerson-essays", "walden-thoreau",
    "chuang-tzu-giles", "plato-apology-jowett", "plato-phaedo-jowett", "teresa-interior-castle",
    "augustine-confessions-pusey", "aristotle-ethics"]]
TIER4 = [(s, None, s) for s in ["teresa-way-of-perfection", "brother-lawrence",
                                "rumi-masnavi-whinfield", "american-indian-stories-zitkala"]]
NIKAYAS = [("Long Discourses (Digha Nikaya)", "dn"), ("Middle Discourses (Majjhima Nikaya)", "mn"),
           ("Linked Discourses (Samyutta Nikaya)", "sn"), ("Numbered Discourses (Anguttara Nikaya)", "an")]


def tier3():
    """Bulk sources: Seneca first (reviewer's safety check), then Vivekananda, the Bible, the Nikayas."""
    out = [("seneca-letters-gummere", None, "seneca")]
    works = []
    for u in load_units("vivekananda"):
        if u.get("work") and u["work"] not in works:
            works.append(u["work"])
    out += [("vivekananda", ("work", w), f"viv{i:02d}") for i, w in enumerate(works, 1)]
    books = []
    for u in load_units("bible-web"):
        b = u["loc"]["book"]
        if b not in books:
            books.append(b)
    out += [("bible-web", ("book", b), "bib-" + b.lower().replace(" ", "")) for b in books
            if b not in BIBLE_FIRST and b not in BIBLE_SKIP]
    out += [("suttacentral-sujato", ("work", w), p) for w, p in NIKAYAS]
    return out


def jload(p, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def jsave(p, obj):
    p.write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")


def prep():
    for d in (CHUNKS, EXTRACT, TAG_IN, TAGS):
        d.mkdir(parents=True, exist_ok=True)
    plan = [(1, *x) for x in TIER1] + [(2, *x) for x in TIER2] + \
           [(3, *x) for x in tier3()] + [(4, *x) for x in TIER4]
    cache, chunks = {}, []
    for tier, src, flt, prefix in plan:
        if not is_active(src):
            print(f"skip {src}: switched off")
            continue
        units = cache.setdefault(src, load_units(src))
        if flt:
            key, val = flt
            units = [u for u in units if (u.get("work") if key == "work" else u["loc"].get("book")) == val]
        # Zitkala-Ša: the quoted municipal report is not her writing (D04 flag).
        units = [u for u in units if not (u.get("meta") or {}).get("quoted_report")]
        for i, c in enumerate(make_chunks(units, WORDS), 1):
            cid = f"{prefix}-{i:03d}"
            (CHUNKS / f"{cid}.txt").write_text("\n\n".join(render(u) for u in c) + "\n", encoding="utf-8")
            wc = sum(len(u["text"].split()) for u in c if u["kind"] != "heading")
            chunks.append({"id": cid, "tier": tier, "source": src, "work": c[0].get("work") or (flt[1] if flt else None),
                           "first_uid": c[0]["uid"], "last_uid": c[-1]["uid"], "units": len(c), "words": wc})
    jsave(MANIFEST, {"chunks": chunks})
    # The Dhammapada was extracted on Opus 5.5 in the Day 4 pilot with the same prompt and
    # the same chunk boundaries; reuse it instead of paying for it twice.
    pilot = {c["id"]: c for c in jload(PILOT / "manifest.json", {"chunks": []})["chunks"]}
    for c in chunks:
        p, src = pilot.get(c["id"]), PILOT / "out" / "opus" / f"{c['id']}.json"
        if p and p["first_uid"] == c["first_uid"] and p["last_uid"] == c["last_uid"] and src.exists():
            (EXTRACT / src.name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"reused pilot output for {c['id']}")
    by_tier = Counter()
    for c in chunks:
        by_tier[c["tier"]] += c["words"]
    print(f"{len(chunks)} chunks, {sum(by_tier.values()):,} words; by tier: {dict(by_tier)}")


def done_chunks():
    return {p.stem for p in EXTRACT.glob("*.json")}


def live_claims():
    now, claims = time.time(), jload(CLAIMS, {})
    return {k: v for k, v in claims.items() if now - v < CLAIM_TTL}


def claim(ids):
    claims = live_claims()
    claims.update({i: time.time() for i in ids})
    jsave(CLAIMS, claims)


def packs(n, size, prefer=""):
    """prefer: comma-separated chunk-id prefixes to hand out first (e.g. high-yield Bible books)."""
    done, claimed = done_chunks(), live_claims()
    pending = [c for c in jload(MANIFEST, {})["chunks"] if c["id"] not in done and c["id"] not in claimed]
    if prefer:
        pre = [x for x in prefer.split(",") if x]
        rank = lambda c: next((i for i, x in enumerate(pre) if c["id"].startswith(x + "-")), len(pre))
        pending.sort(key=rank)  # stable: manifest order kept within each group
    out = []
    for _ in range(n):
        if not pending:
            break
        pack, pending = pending[:size], pending[size:]
        claim([c["id"] for c in pack])
        out.append(pack)
        print("PACK " + " ".join(c["id"] for c in pack) + f"   # {sum(c['words'] for c in pack):,} words")
    if not out:
        print("NO PENDING CHUNKS")


def check():
    """Verbatim check (Corpus-Policy section 4, rule 7). Rejects are logged, never repaired."""
    manifest = {c["id"]: c for c in jload(MANIFEST, {})["chunks"]}
    cache, ok, bad, bad_files = {}, defaultdict(list), defaultdict(list), []
    for f in sorted(EXTRACT.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            bad_files.append(f"{f.name}: {e}")
            continue
        chunk = manifest[f.stem]
        src = chunk["source"]
        units = cache.setdefault(src, load_units(src))
        by_uid = {u["uid"]: u for u in units}
        for i, p in enumerate(data.get("passages", []), 1):
            text = p.get("text", "")
            res = verbatim_match(text, units, p.get("start_uid"), p.get("end_uid"))
            rec = {"pid": f"{chunk['id']}-p{i:02d}", "chunk": chunk["id"], "tier": chunk["tier"], "source": src,
                   "work": chunk.get("work"), "start_uid": p.get("start_uid"), "end_uid": p.get("end_uid"),
                   "display": by_uid.get(p.get("start_uid"), {}).get("display"),
                   "text": text, "note": p.get("note"), "words": len(text.split()), "check": res}
            if res["ok"]:
                rec["warnings"] = [w for w, bad_ in (("may end mid-sentence", not SENT_END.search(squash(text))),
                                                     ("location claim wrong", res.get("where") != "claimed_range")) if bad_]
                ok[src].append(rec)
            else:
                bad[src].append(rec)
    (RUN / "checked").mkdir(exist_ok=True)
    for src in set(ok) | set(bad):
        with (RUN / "checked" / f"{src}.jsonl").open("w", encoding="utf-8") as fo:
            for r in ok[src]:
                fo.write(json.dumps(r, ensure_ascii=False) + "\n")
    with (RUN / "rejects.jsonl").open("w", encoding="utf-8") as fo:
        for src in bad:
            for r in bad[src]:
                fo.write(json.dumps(r, ensure_ascii=False) + "\n")
    n_ok, n_bad = sum(map(len, ok.values())), sum(map(len, bad.values()))
    print(f"verbatim: {n_ok + n_bad} extracted, {n_ok} exact, {n_bad} rejected; unreadable files: {len(bad_files)}")
    for b in bad_files:
        print("   BAD FILE", b)
    return ok


def checked_passages():
    out = []
    for f in sorted((RUN / "checked").glob("*.jsonl")):
        out += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    return out


def tagged_ids():
    ids = set()
    for f in TAGS.glob("*.json"):
        try:
            ids |= {t["id"] for t in json.loads(f.read_text(encoding="utf-8"))["tags"]}
        except (json.JSONDecodeError, KeyError):
            pass
    return ids


def tagbatches(n, size):
    check()
    tagged, claims = tagged_ids(), live_claims()
    in_batch = set()
    for f in TAG_IN.glob("*.jsonl"):
        if f.stem in claims or (TAGS / f"{f.stem}.json").exists():
            in_batch |= {json.loads(l)["id"] for l in f.read_text(encoding="utf-8").splitlines() if l.strip()}
    todo = [p for p in checked_passages() if p["pid"] not in tagged and p["pid"] not in in_batch]
    # Tag in priority order, keeping a source's passages together.
    order = {c["id"]: i for i, c in enumerate(jload(MANIFEST, {})["chunks"])}
    todo.sort(key=lambda p: (order.get(p["chunk"], 0), p["pid"]))
    k = len(list(TAG_IN.glob("*.jsonl")))
    made = 0
    while todo and made < n:
        batch, todo = todo[:size], todo[size:]
        k += 1
        bid = f"t{k:04d}"
        with (TAG_IN / f"{bid}.jsonl").open("w", encoding="utf-8") as fo:
            for p in batch:
                fo.write(json.dumps({"id": p["pid"], "source": p["source"], "work": p["work"],
                                     "display": p["display"], "text": p["text"]}, ensure_ascii=False) + "\n")
        claim([bid])
        made += 1
        print(f"BATCH {bid}   # {len(batch)} passages, {batch[0]['source']} .. {batch[-1]['source']}")
    if not made:
        print("NO UNTAGGED PASSAGES")


def merge():
    """One file per source in corpus/passages/, plus the cut list for Shailesh to scan."""
    V = vocab()
    tags = {}
    for f in sorted(TAGS.glob("*.json")):
        try:
            for t in json.loads(f.read_text(encoding="utf-8"))["tags"]:
                tags[t["id"]] = t
        except (json.JSONDecodeError, KeyError) as e:
            print(f"BAD TAG FILE {f.name}: {e}")
    problems = Counter()
    per_src = defaultdict(list)
    for p in checked_passages():
        t = tags.get(p["pid"])
        if t:
            for fld, (lo, hi) in LIMITS.items():
                vals = t.get(fld, [])
                if not lo <= len(vals) <= hi:
                    problems[f"{fld}: count {len(vals)}"] += 1
                problems.update(f"{fld}: unknown '{x}'" for x in vals if fld in V and x not in V[fld])
            problems.update(f"{fld}: unknown '{t.get(fld)}'" for fld in ("faith", "safety") if t.get(fld) not in V[fld])
            safety = t.get("safety")
            p["tags"] = {k: v for k, v in t.items() if k != "id"}
            p["status"] = ("cut" if safety in ("endorses-suicide", "sexual-violence", "group-hatred")
                           else "no-distress" if safety == "welcomes-death" else "keep")
        else:
            p["status"] = "untagged"
        per_src[p["source"]].append(p)
    for src, ps in per_src.items():
        with (ROOT / "corpus" / "passages" / f"{src}.jsonl").open("w", encoding="utf-8") as fo:
            for p in ps:
                fo.write(json.dumps(p, ensure_ascii=False) + "\n")
    # Cut list (Corpus-Policy section 6, rule 4): logged with the tagger's reason, never deleted.
    lines = ["# Safety-field cut list", "",
             "Written by `pipeline/bulk.py merge`. Passages tagged `endorses-suicide`, `sexual-violence` or "
             "`group-hatred` are cut; `welcomes-death` is kept but never shown to someone in distress "
             "(Corpus-Policy section 6). To restore a wrongly cut passage, tell Claude its id.", ""]
    order = [c["source"] for c in jload(MANIFEST, {})["chunks"]]
    n = 0
    for src in sorted(per_src, key=order.index):
        flagged = [p for p in per_src[src] if p["status"] in ("cut", "no-distress")]
        tagged = sum(1 for p in per_src[src] if p["status"] != "untagged")
        n += 1
        lines += [f"## {n}. {src}", "",
                  f"{tagged} tagged; {sum(p['status'] == 'cut' for p in flagged)} cut; "
                  f"{sum(p['status'] == 'no-distress' for p in flagged)} kept but hidden from distress.", ""]
        if flagged:
            lines += ["| Id | Location | Safety | Reason | Opening words |", "| --- | --- | --- | --- | --- |"]
            for p in flagged:
                opening = " ".join(p["text"].split()[:14]).replace("|", "/")
                reason = (p["tags"].get("safety_reason") or "").replace("|", "/")
                lines.append(f"| {p['pid']} | {p['display']} | {p['tags']['safety']} | {reason} | {opening}… |")
            lines.append("")
    (RUN / "cuts.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"merged {sum(map(len, per_src.values()))} passages over {len(per_src)} sources; "
          f"{len(tags)} tagged; tag validity problems: {sum(problems.values())}")
    for k, v in problems.most_common(8):
        print(f"   {v:>3} x {k}")


def status():
    chunks = jload(MANIFEST, {})["chunks"]
    done, claims = done_chunks(), live_claims()
    passages = checked_passages() if (RUN / "checked").exists() else []
    tagged = tagged_ids()
    rows = defaultdict(lambda: Counter())
    for c in chunks:
        r = rows[c["source"]]
        r["chunks"] += 1
        r["words"] += c["words"]
        r["done"] += c["id"] in done
        r["done_words"] += c["words"] if c["id"] in done else 0
        r["tier"] = c["tier"]
    for p in passages:
        rows[p["source"]]["passages"] += 1
        rows[p["source"]]["tagged"] += p["pid"] in tagged
    tot = Counter()
    print(f"{'source':34} tier  chunks  done  words_done/words   passages tagged")
    for src, r in rows.items():
        if r["done"] or r["tier"] <= 2:
            print(f"{src:34} {r['tier']:>4}  {r['chunks']:>6} {r['done']:>5}  {r['done_words']:>8,}/{r['words']:<9,} "
                  f"{r['passages']:>6} {r['tagged']:>6}")
        tot.update({k: v for k, v in r.items() if k != "tier"})
    print(f"TOTAL chunks {tot['done']}/{tot['chunks']}, words {tot['done_words']:,}/{tot['words']:,}, "
          f"passages {tot['passages']}, tagged {tot['tagged']}; live claims {len(claims)}")


if __name__ == "__main__":
    cmd, args = sys.argv[1], [int(a) if a.isdigit() else a for a in sys.argv[2:]]
    {"prep": prep, "status": status, "packs": packs, "check": check,
     "tagbatches": tagbatches, "merge": merge}[cmd](*args)
