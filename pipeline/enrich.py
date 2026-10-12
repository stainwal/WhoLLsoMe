"""Enrichment pass (Plan Day 15; Corpus-Policy section 7, step 7) and the plain-version judge (Plan 4.3).

    python3 pipeline/enrich.py batches N SIZE       # claim N batches of SIZE shown, unenriched passages -> enrich-in/eNNNN.jsonl
    python3 pipeline/enrich.py verify               # check helper output; write enrichment.json + enrich-rejects.jsonl
    python3 pipeline/enrich.py judgebatches N SIZE  # claim N batches of SIZE enriched, unjudged passages -> judge-in/jNNNN.jsonl
    python3 pipeline/enrich.py status               # progress counts
    python3 pipeline/enrich.py weakest N            # the N plain versions the judge rated least faithful -> evals/plain-version-check.md
    python3 pipeline/enrich.py rewritebatch MAX     # plain versions judged <= MAX -> rewrite-in/r0001.jsonl (Day 16)
    python3 pipeline/enrich.py rejudgebatch         # old and new plain versions of the rewrites, shuffled -> judge-in/k0001.jsonl
    python3 pipeline/bulk.py merge                  # then applies enrichment.json to corpus/passages/<source>.jsonl

Helpers (Opus 5.5, medium effort) read pipeline/prompts/enrich.md or judge-plain.md, one input
file, and write one output file:
    enrich-in/eNNNN.jsonl  -> enrich/eNNNN.json   {"items": [{id, plain, core_idea, quotability, complete,
                                                              extended_text?, fix?: {display_text, reason}}]}
    judge-in/jNNNN.jsonl   -> judge/jNNNN.json    {"judgements": [{id, faithful, advice, issue}]}
Everything is verified here before it reaches the corpus: an extension must be verbatim in the
source; a display fix may change punctuation, spacing, brackets and case freely but letters by at
most two characters; everything else is rejected and logged, never repaired.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from bulk import ROOT, RUN, checked_passages, claim, display_text, jload, jsave, live_claims  # noqa: E402
from common import load_units, squash, verbatim_match  # noqa: E402
from check import SENT_END  # noqa: E402
import restricted  # noqa: E402

ENRICH_IN, ENRICH, JUDGE_IN, JUDGE = RUN / "enrich-in", RUN / "enrich", RUN / "judge-in", RUN / "judge"
ENRICHMENT, REJECTS = RUN / "enrichment.json", RUN / "enrich-rejects.jsonl"
# Day 16 rewrite of weak plain versions: rewrite/rNNNN.json {"items": [{id, plain}]} replaces the plain
# version; rejudge/kNNNN.json judges old and new side by side (ids "<pid>#old" / "<pid>#new"), and the
# "#new" judgement replaces the Day 15 one, which is kept as judge_v1.
REWRITE_IN, REWRITE, REJUDGE = RUN / "rewrite-in", RUN / "rewrite", RUN / "rejudge"
# Shailesh's 12 Oct rule for AI display fixes: punctuation and spacing fixes stand; a fix that changes
# letters stands only if a second copy of the text confirms it. {pid: reason} for each fix withdrawn.
FIX_REVERTS = RUN / "fix-reverts.json"
PASSAGES = ROOT / "corpus" / "passages"
NEXT_WORDS, MAX_EXTENSION_WORDS = 90, 130
PLAIN_MAX, CORE_MAX = 60, 14            # hard limits; the prompt asks for 40 and 10


def shown():
    """Passages a user can be shown: keep or no-distress, not dup, not cut."""
    out = []
    for f in sorted(PASSAGES.glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                p = json.loads(line)
                if p["status"] in ("keep", "no-distress"):
                    out.append(p)
    return out


_units = {}


def units_of(source):
    if source not in _units:
        _units[source] = load_units(source)
    return _units[source]


def body_index(source):
    us = [u for u in units_of(source) if u["kind"] != "heading"]
    return us, {u["uid"]: i for i, u in enumerate(us)}


def next_text(p):
    """Source text after the passage: the rest of its last unit, then following units, up to
    NEXT_WORDS words, never past a heading. Used only for the completeness check."""
    us, idx = body_index(p["source"])
    full = units_of(p["source"])
    end = p.get("end_uid") or p["start_uid"]
    if end not in idx:
        return ""
    i = idx[end]
    u, ptxt = squash(us[i]["text"]), squash(p["text"])
    tail = ptxt[-80:]
    k = u.find(tail)
    parts = [u[k + len(tail):].strip()] if k >= 0 else []
    # stop at the next heading in the full unit list
    pos = next(j for j, x in enumerate(full) if x["uid"] == end)
    for x in full[pos + 1:]:
        if x["kind"] == "heading" or sum(len(t.split()) for t in parts) >= NEXT_WORDS:
            break
        parts.append(x["text"])
    return "\n".join(t for t in parts if t)


def enriched_ids():
    ids = set()
    for f in restricted.glob_mixed(ENRICH):
        try:
            ids |= {it["id"] for it in restricted.load_json(f)["items"]}
        except (json.JSONDecodeError, KeyError):
            pass
    return ids


def judged_ids():
    ids = set()
    for f in restricted.glob_mixed(JUDGE):
        try:
            ids |= {j["id"] for j in restricted.load_json(f)["judgements"]}
        except (json.JSONDecodeError, KeyError):
            pass
    return ids


def in_flight(in_dir, out_dir):
    """Ids already handed out in a claimed or finished batch."""
    ids, claims = set(), live_claims()
    for f in in_dir.glob("*.jsonl"):
        if f.stem in claims or (out_dir / f"{f.stem}.json").exists():
            ids |= {json.loads(l)["id"] for l in f.read_text(encoding="utf-8").splitlines() if l.strip()}
    return ids


def batches(n, size):
    ENRICH_IN.mkdir(exist_ok=True)
    ENRICH.mkdir(exist_ok=True)
    done, flight = enriched_ids(), in_flight(ENRICH_IN, ENRICH)
    todo = [p for p in shown() if p["pid"] not in done and p["pid"] not in flight]
    k, made = len(list(ENRICH_IN.glob("*.jsonl"))), 0
    while todo and made < n:
        batch, todo = todo[:size], todo[size:]
        k += 1
        bid = f"e{k:04d}"
        with (ENRICH_IN / f"{bid}.jsonl").open("w", encoding="utf-8") as fo:
            for p in batch:
                # helpers see the shown text (file apparatus removed), never the raw file text
                fo.write(json.dumps({"id": p["pid"], "source": p["source"], "display": p["display"],
                                     "text": display_text(p["text"]), "next": next_text(p)}, ensure_ascii=False) + "\n")
        claim([bid])
        made += 1
        print(f"BATCH {bid}   # {len(batch)} passages, {batch[0]['source']} .. {batch[-1]['source']}")
    if not made:
        print("NO UNENRICHED PASSAGES")


def letters(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def edit_distance(a, b, cap=3):
    """Levenshtein with early exit above cap (strings here differ little or are rejected)."""
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        if min(cur) > cap:
            return cap + 1
        prev = cur
    return prev[-1]


def check_extension(p, ext):
    """An accepted extension is verbatim in the source, starts with the passage, ends a sentence,
    and adds at most MAX_EXTENSION_WORDS words. Returns (record or None, reason)."""
    s_ext, s_txt, s_disp = squash(ext), squash(p["text"]), squash(display_text(p["text"]))
    if s_ext.startswith(s_txt):
        added = s_ext[len(s_txt):].strip()
    elif s_ext.startswith(s_disp):          # the helper saw the display text
        added = s_ext[len(s_disp):].strip()
    else:
        return None, "extension does not start with the passage"
    ext = p["text"] + ("\n" if p["text"].count("\n") > 1 else " ") + added   # raw text + continuation
    if not added:
        return None, "extension adds nothing"
    if len(added.split()) > MAX_EXTENSION_WORDS:
        return None, f"extension adds {len(added.split())} words"
    s_ext = squash(ext)
    if not SENT_END.search(s_ext):
        return None, "extension does not end at a sentence end"
    us, idx = body_index(p["source"])
    a = idx.get(p["start_uid"])
    if a is None:
        return None, "start unit not found"
    for k in range(0, 8):
        b = min(a + k, len(us) - 1)
        span = " ".join(squash(u["text"]) for u in us[a:b + 1])
        if s_ext in span:
            res = verbatim_match(ext, us, p["start_uid"], us[b]["uid"])
            if res["ok"]:
                return {"text": ext, "end_uid": us[b]["uid"], "words": len(ext.split()),
                        "added_words": len(added.split())}, ""
        if b == len(us) - 1:
            break
    return None, "extension not verbatim in the source"


def doubled_word_removed(cur, new):
    """True when `new` is `cur` with exactly one repeated word ("and and") dropped: a transcription slip."""
    w = lambda t: re.findall(r"[a-z0-9]+", t.lower())
    a, b = w(cur), w(new)
    if len(a) != len(b) + 1:
        return False
    for i in range(1, len(a)):
        if a[i] == a[i - 1] and a[:i] + a[i + 1:] == b:
            return True
    return False


def check_fix(p, fix):
    """A display fix may change punctuation, spacing, brackets and case; letters by at most 2 edits."""
    if not isinstance(fix, dict) or not fix.get("display_text") or not fix.get("reason"):
        return None, "fix malformed"
    cur, new = display_text(p["text"]), fix["display_text"]
    if squash(new) == squash(cur):
        return None, "fix changes nothing"
    d = edit_distance(letters(cur), letters(new), cap=2)
    if d > 2 and not doubled_word_removed(cur, new):
        return None, f"fix changes letters (distance > 2)"
    if abs(len(new) - len(cur)) > 12:
        return None, "fix changes length by more than 12 characters"
    # display_text() already drops a quotation mark whose partner lies outside the passage; a fix
    # that puts an unmatched one back undoes that on purpose and is refused
    if new.count("\u201c") != new.count("\u201d") or new.count('"') % 2:
        return None, "fix leaves an unmatched quotation mark"
    q = lambda t: sum(t.count(c) for c in "\u201c\u201d\"")
    if q(new) > q(cur):      # the display rule drops an unpaired mark; it never invents its partner
        return None, "fix adds a quotation mark the source does not have"
    return {"display_text": new, "reason": str(fix["reason"])[:160]}, ""


def verify():
    """Read every enrich/*.json and judge/*.json; write enrichment.json and the reject log."""
    restricted.split()     # helper output may mix sources; restricted items move to corpus/restricted/
    # check against the passage as extracted: after a merge, corpus/passages/ already holds extended text
    ids = {p["pid"] for p in shown()}
    by = {p["pid"]: p for p in checked_passages() if p["pid"] in ids}
    reverts = jload(FIX_REVERTS, {})
    out, rejects, counts = {}, [], Counter()
    for f in restricted.glob_mixed(ENRICH):
        try:
            items = restricted.load_json(f)["items"]
        except (json.JSONDecodeError, KeyError) as e:
            rejects.append({"file": f.name, "reason": f"unreadable: {e}"})
            continue
        for it in items:
            pid = it.get("id")
            p = by.get(pid)
            if not p:
                rejects.append({"file": f.name, "id": pid, "reason": "unknown or unshown id"})
                continue
            plain, core, q = str(it.get("plain", "")).strip(), str(it.get("core_idea", "")).strip(), it.get("quotability")
            problems = []
            if not plain or len(plain.split()) > PLAIN_MAX:
                problems.append(f"plain: {len(plain.split())} words")
            if not core or len(core.split()) > CORE_MAX:
                problems.append(f"core_idea: {len(core.split())} words")
            if not isinstance(q, int) or not 1 <= q <= 5:
                problems.append(f"quotability: {q!r}")
            if not isinstance(it.get("complete"), bool):
                problems.append("complete: not a boolean")
            if problems:
                rejects.append({"file": f.name, "id": pid, "reason": "; ".join(problems)})
                counts["rejected items"] += 1
                continue
            rec = {"plain": plain, "core_idea": core, "quotability": q, "complete": it["complete"], "batch": f.stem}
            if it.get("extended_text"):
                ext, why = check_extension(p, str(it["extended_text"]))
                if ext:
                    rec["extension"] = ext
                    counts["extensions accepted"] += 1
                else:
                    rejects.append({"file": f.name, "id": pid, "field": "extended_text", "reason": why})
                    counts["extensions rejected"] += 1
            elif it["complete"] is False:
                counts["incomplete without extension"] += 1
            if it.get("fix") and pid in reverts:
                counts["fixes reverted"] += 1
            elif it.get("fix"):
                fx, why = check_fix(p, it["fix"])
                if fx:
                    rec["fix"] = fx
                    counts["fixes accepted"] += 1
                else:
                    rejects.append({"file": f.name, "id": pid, "field": "fix", "reason": why})
                    counts["fixes rejected"] += 1
            out[pid] = rec
            counts["enriched"] += 1
    for f in restricted.glob_mixed(JUDGE):
        try:
            js = restricted.load_json(f)["judgements"]
        except (json.JSONDecodeError, KeyError) as e:
            rejects.append({"file": f.name, "reason": f"unreadable: {e}"})
            continue
        for j in js:
            pid, score = j.get("id"), j.get("faithful")
            if pid not in out:
                rejects.append({"file": f.name, "id": pid, "reason": "judgement for an unenriched id"})
                continue
            if not isinstance(score, int) or not 1 <= score <= 5:
                rejects.append({"file": f.name, "id": pid, "reason": f"faithful: {score!r}"})
                continue
            out[pid]["judge"] = {"faithful": score, "advice": bool(j.get("advice", False)),
                                 "issue": str(j.get("issue", ""))[:200], "batch": f.stem}
            counts["judged"] += 1
    apply_rewrites(out, rejects, counts)
    jsave(ENRICHMENT, out)
    with REJECTS.open("w", encoding="utf-8") as fo:
        for r in rejects:
            fo.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"enrichment.json: {len(out)} passages; " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    print(f"rejects logged: {len(rejects)}")
    return out


def apply_rewrites(out, rejects, counts):
    """Day 16: a rewritten plain version replaces the Day 15 one only once it has its own judgement."""
    judged, key = {}, {}
    for f in REJUDGE.glob("*-key.jsonl"):          # opaque id -> "<pid>#old" / "<pid>#new"
        for line in f.read_text(encoding="utf-8").splitlines():
            k = json.loads(line)
            key[k["opaque"]] = k["id"]
    for f in restricted.glob_mixed(REJUDGE):
        for j in restricted.load_json(f)["judgements"]:
            judged[key.get(j["id"], j["id"])] = {"faithful": j["faithful"], "advice": bool(j.get("advice", False)),
                               "issue": str(j.get("issue", ""))[:200], "batch": f.stem}
    for f in restricted.glob_mixed(REWRITE):
        for it in restricted.load_json(f)["items"]:
            pid, plain = it.get("id"), str(it.get("plain", "")).strip()
            if pid not in out:
                rejects.append({"file": f.name, "id": pid, "reason": "rewrite for an unenriched id"})
                continue
            if not plain or len(plain.split()) > PLAIN_MAX:
                rejects.append({"file": f.name, "id": pid, "reason": f"rewrite plain: {len(plain.split())} words"})
                continue
            new = judged.get(f"{pid}#new")
            if not new or not isinstance(new["faithful"], int):
                counts["rewrites awaiting judge"] += 1
                continue
            rec = out[pid]
            rec["plain_v1"], rec["judge_v1"] = rec["plain"], rec.get("judge")
            if f"{pid}#old" in judged:
                rec["judge_v1_rejudged"] = judged[f"{pid}#old"]
            rec["plain"], rec["judge"], rec["rewrite"] = plain, new, f.stem
            counts["rewrites applied"] += 1


def rewritebatch(max_score):
    """All plain versions the judge scored max_score or lower, in one batch for a rewrite helper."""
    REWRITE_IN.mkdir(exist_ok=True)
    REWRITE.mkdir(exist_ok=True)
    e = jload(ENRICHMENT, {})
    by = {p["pid"]: p for p in shown()}
    rows = [pid for pid, v in e.items() if "judge" in v and v["judge"]["faithful"] <= max_score and pid in by]
    bid = f"r{len(list(REWRITE_IN.glob('*.jsonl'))) + 1:04d}"
    with (REWRITE_IN / f"{bid}.jsonl").open("w", encoding="utf-8") as fo:
        for pid in rows:
            v, p = e[pid], by[pid]
            text = v["extension"]["text"] if "extension" in v else p["text"]
            shown_text = v["fix"]["display_text"] if "fix" in v else display_text(text)
            fo.write(json.dumps({"id": pid, "source": p["source"], "display": p["display"], "text": shown_text,
                                 "old_plain": v["plain"], "issue": v["judge"]["issue"]}, ensure_ascii=False) + "\n")
    print(f"BATCH {bid}   # {len(rows)} plain versions judged <= {max_score}")


def rejudgebatch():
    """Old and new plain versions of every rewrite, shuffled together, judged cold with the same prompt."""
    import random
    JUDGE_IN.mkdir(exist_ok=True)
    REJUDGE.mkdir(exist_ok=True)
    e = jload(ENRICHMENT, {})
    by = {p["pid"]: p for p in shown()}
    items = []
    for f in restricted.glob_mixed(REWRITE):
        for it in restricted.load_json(f)["items"]:
            pid = it["id"]
            v, p = e[pid], by[pid]
            text = v["extension"]["text"] if "extension" in v else p["text"]
            shown_text = v["fix"]["display_text"] if "fix" in v else display_text(text)
            old = v.get("plain_v1", v["plain"])
            items += [{"id": f"{pid}#old", "text": shown_text, "plain": old},
                      {"id": f"{pid}#new", "text": shown_text, "plain": it["plain"]}]
    random.Random(16).shuffle(items)
    bid = f"k{len(list(JUDGE_IN.glob('k*.jsonl'))) + 1:04d}"
    # the judge sees opaque ids, so it cannot tell the old version from the new; the key stays here
    with (JUDGE_IN / f"{bid}.jsonl").open("w", encoding="utf-8") as fo, \
         (REJUDGE / f"{bid}-key.jsonl").open("w", encoding="utf-8") as fk:
        for i, it in enumerate(items, 1):
            opaque = f"{bid}-{i:03d}"
            fk.write(json.dumps({"opaque": opaque, "id": it["id"]}) + "\n")
            fo.write(json.dumps({**it, "id": opaque}, ensure_ascii=False) + "\n")
    print(f"BATCH {bid}   # {len(items)} items (old and new, shuffled)")


def judgebatches(n, size):
    JUDGE_IN.mkdir(exist_ok=True)
    JUDGE.mkdir(exist_ok=True)
    enr = verify()
    done, flight = judged_ids(), in_flight(JUDGE_IN, JUDGE)
    by = {p["pid"]: p for p in shown()}
    todo = [pid for pid in enr if pid not in done and pid not in flight]
    k, made = len(list(JUDGE_IN.glob("*.jsonl"))), 0
    while todo and made < n:
        batch, todo = todo[:size], todo[size:]
        k += 1
        bid = f"j{k:04d}"
        with (JUDGE_IN / f"{bid}.jsonl").open("w", encoding="utf-8") as fo:
            for pid in batch:
                e, p = enr[pid], by[pid]
                text = e["extension"]["text"] if "extension" in e else p["text"]
                fo.write(json.dumps({"id": pid, "text": display_text(text), "plain": e["plain"]},
                                    ensure_ascii=False) + "\n")
        claim([bid])
        made += 1
        print(f"BATCH {bid}   # {len(batch)} items")
    if not made:
        print("NO UNJUDGED PASSAGES")


def status():
    total = len(shown())
    enr, jd = enriched_ids(), judged_ids()
    print(f"shown {total}; enriched {len(enr)}; judged {len(jd)}; live claims {len(live_claims())}")
    if ENRICHMENT.exists():
        e = jload(ENRICHMENT, {})
        q = Counter(v["quotability"] for v in e.values())
        f = Counter(v["judge"]["faithful"] for v in e.values() if "judge" in v)
        print("quotability:", dict(sorted(q.items())), "| faithful:", dict(sorted(f.items())),
              "| extensions:", sum("extension" in v for v in e.values()), "| fixes:", sum("fix" in v for v in e.values()))


def weakest(n):
    """The n plain versions the judge rated least faithful, as a check sheet for Shailesh (Plan Day 16)."""
    e = jload(ENRICHMENT, {})
    by = {p["pid"]: p for p in shown()}
    rows = [(v["judge"]["faithful"], v["judge"]["advice"], pid, v) for pid, v in e.items() if "judge" in v and pid in by]
    rows.sort(key=lambda r: (r[0], not r[1], r[2]))
    pick = rows[:n]
    lines = ["# Plain-version check (Day 16)", "",
             f"*The {n} plain versions the AI judge rated least faithful, out of {len(rows)} judged "
             f"(Plan section 4.3). Read each plain version against its passage. In the last column write "
             f"**OK** (keep as is), **Fix** (and write the fix in the row or below), or **Hide** (show the "
             f"passage without a plain version). Everything the judge scored higher stands.*", "",
             "| # | Passage (source, location) | In plain words | Judge | OK / Fix / Hide |",
             "| --- | --- | --- | --- | --- |"]
    for i, (score, advice, pid, v) in enumerate(pick, 1):
        p = by[pid]
        text = (v["extension"]["text"] if "extension" in v else p["text"])
        shown_text = v["fix"]["display_text"] if "fix" in v else display_text(text)
        cell = lambda s: s.replace("|", "/").replace("\n", " / ")
        judge = f"{score}/5" + (", gives advice" if advice else "") + (f": {v['judge']['issue']}" if v["judge"]["issue"] else "")
        lines.append(f"| P{i:02d} | **{p['source']}: {cell(p['display'])}** ({pid})<br>{cell(shown_text)} | {cell(v['plain'])} | {cell(judge)} | |")
    out = ROOT / "evals" / "plain-version-check.md"
    restricted.write_report(out, lines)
    print(f"wrote {out.relative_to(ROOT)}: {len(pick)} rows; score distribution of all judged: "
          f"{dict(sorted(Counter(r[0] for r in rows).items()))}")


def report():
    """corpus/passages/bulk/enrich-report.md: every accepted extension and display fix, for a human scan."""
    e = jload(ENRICHMENT, {})
    by = {p["pid"]: p for p in shown()}
    cell = lambda s: s.replace("|", "/").replace("\n", " / ")
    ext = [(pid, v) for pid, v in e.items() if "extension" in v]
    fixes = [(pid, v) for pid, v in e.items() if "fix" in v]
    word_fixes = [(pid, v) for pid, v in fixes if letters(display_text(by[pid]["text"])) != letters(v["fix"]["display_text"])]
    punct_fixes = [(pid, v) for pid, v in fixes if (pid, v) not in word_fixes]
    lines = ["# Enrichment report (Day 15)", "",
             f"*Written by `pipeline/enrich.py report`. {len(e)} passages enriched; {len(ext)} extended verbatim for "
             f"completeness; {len(fixes)} display fixes accepted ({len(word_fixes)} change letters, {len(punct_fixes)} "
             f"punctuation or spacing only). Everything here was verified by script (Corpus-Policy section 4, rule 8) and "
             f"is reversible: remove the entry from `enrichment.json` or add an override. Rejected proposals are in "
             f"`enrich-rejects.jsonl`.*", "",
             "## 1. Display fixes that change letters (scan these first)", "",
             "| Passage | Was (shown text) | Now | Reason |", "| --- | --- | --- | --- |"]
    import difflib
    def snippet(a, b):
        sm = difflib.SequenceMatcher(None, a, b)
        out_a, out_b = [], []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                out_a.append(a[max(0, i1 - 25):i2 + 25]); out_b.append(b[max(0, j1 - 25):j2 + 25])
        return " … ".join(out_a), " … ".join(out_b)
    for pid, v in word_fixes:
        a, b = snippet(display_text(by[pid]["text"]), v["fix"]["display_text"])
        lines.append(f"| {pid} ({cell(by[pid]['display'])}) | {cell(a)} | {cell(b)} | {cell(v['fix']['reason'])} |")
    lines += ["", "## 2. Punctuation and spacing fixes", "", "| Passage | Was | Now | Reason |", "| --- | --- | --- | --- |"]
    for pid, v in punct_fixes:
        a, b = snippet(display_text(by[pid]["text"]), v["fix"]["display_text"])
        lines.append(f"| {pid} | {cell(a)} | {cell(b)} | {cell(v['fix']['reason'])} |")
    lines += ["", "## 3. Verbatim extensions (passage was incomplete without the next sentence)", "",
              "| Passage | Added words | Text now ends with |", "| --- | --- | --- |"]
    for pid, v in ext:
        t = v["extension"]["text"]
        lines.append(f"| {pid} ({cell(by[pid]['display'])}) | {v['extension']['added_words']} | …{cell(t[-160:])} |")
    out = RUN / "enrich-report.md"
    restricted.write_report(out, lines)
    print(f"wrote {out.relative_to(ROOT)}: {len(word_fixes)} letter fixes, {len(punct_fixes)} punctuation fixes, {len(ext)} extensions")


if __name__ == "__main__":
    cmd, args = sys.argv[1], [int(a) if a.isdigit() else a for a in sys.argv[2:]]
    {"batches": batches, "verify": verify, "judgebatches": judgebatches,
     "status": status, "weakest": weakest, "report": report,
     "rewritebatch": rewritebatch, "rejudgebatch": rejudgebatch}[cmd](*args)
