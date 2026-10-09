"""Corpus statistics by source and theme (Plan Days 12-13).

    python3 pipeline/stats.py      # writes corpus/passages/stats.md

Counts are over the passages a user can be shown: status keep or no-distress (hidden
from distress only), excluding cut and dup. Source details come from docs/Corpus-Policy.md
section 2, words read from the bulk manifest, tag families from pipeline/prompts/taxonomy.md.
"""
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent.parent
PASSAGES = ROOT / "corpus" / "passages"
OUT = PASSAGES / "stats.md"
POLICY = ROOT / "docs" / "Corpus-Policy.md"
TAXONOMY = ROOT / "pipeline" / "prompts" / "taxonomy.md"
MANIFEST = PASSAGES / "bulk" / "manifest.json"


def section(md, n):
    return re.search(rf"^## {n}\..*?(?=^## {n + 1}\.|\Z)", md, re.S | re.M).group(0)


def families(md, n):
    """{tag: family} from the '### n.x Family' sub-sections of a taxonomy section."""
    fam, cur = {}, None
    for line in section(md, n).splitlines():
        m = re.match(rf"^### {n}\.\d+ (.+)$", line)
        if m:
            cur = m.group(1).strip()
        elif cur and line.startswith("| ") and not line.startswith("| Tag") and not line.startswith("| ---"):
            fam[line.split("|")[1].strip()] = cur
    return fam


def situation_families(md):
    fam = {}
    for line in section(md, 4).splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) > 3 and line.startswith("| ") and cells[2] not in ("Tags", "---"):
            for t in cells[2].split(";"):
                fam[t.strip()] = cells[1]
    return fam


def sources():
    """{folder: (tradition, work, translator)} from Corpus-Policy section 2."""
    out = {}
    for line in section(POLICY.read_text(encoding="utf-8"), 2).splitlines():
        c = [x.strip() for x in line.split("|")]
        if len(c) > 6 and c[1] not in ("Folder", "---"):
            out[c[1]] = (c[2], c[3], c[4])
    return out


def pct(n, d):
    return f"{100 * n / d:.0f}%" if d else "–"


def main():
    tax = TAXONOMY.read_text(encoding="utf-8")
    FEEL, THEME, SIT = families(tax, 2), families(tax, 3), situation_families(tax)
    SRC = sources()
    words_read = Counter()
    for c in json.loads(MANIFEST.read_text(encoding="utf-8"))["chunks"]:
        words_read[c["source"]] += c["words"]
    allp = []
    for f in sorted(PASSAGES.glob("*.jsonl")):
        allp += [json.loads(line) for line in f.open(encoding="utf-8")]
    shown = [p for p in allp if p["status"] in ("keep", "no-distress")]
    n = len(shown)
    st = Counter(p["status"] for p in allp)
    L = []
    L += [f"# Corpus statistics", "",
          f"*Written by `pipeline/stats.py` on {date.today():%d %b %Y}. Counts are over the {n:,} passages a user can be shown "
          f"(status keep or no-distress); cut and duplicate passages are excluded.*", ""]
    # 1. Totals
    w = [p["words"] for p in shown]
    L += ["## 1. Totals", "", "| Measure | Value |", "| --- | --- |",
          f"| Passages extracted and tagged | {len(allp):,} |",
          f"| Shown normally (keep) | {st['keep']:,} |",
          f"| Kept but hidden from distress (no-distress) | {st['no-distress']:,} |",
          f"| Cut by the safety field | {st['cut']:,} |",
          f"| Duplicates (status dup) | {st['dup']:,} |",
          f"| **Shown passages (keep + no-distress)** | **{n:,}** |",
          f"| Words in shown passages | {sum(w):,} |",
          f"| Passage length, words: median / mean / min / max | {median(w):.0f} / {sum(w) / n:.1f} / {min(w)} / {max(w)} |",
          f"| Under 10 words / over 250 words | {sum(x < 10 for x in w)} / {sum(x > 250 for x in w)} |",
          f"| Source words read | {sum(words_read.values()):,} |",
          f"| Yield, shown passages per 1,000 words read | {1000 * n / sum(words_read.values()):.2f} |",
          f"| In a near group (related passages, never two in one answer) | {sum('near_group' in p for p in shown)} in {len({p['near_group'] for p in shown if 'near_group' in p})} groups |",
          ""]
    faith = Counter(p["tags"]["faith"] for p in shown)
    L += ["Faith framing: " + ", ".join(f"{k} {v:,} ({pct(v, n)})" for k, v in faith.most_common()), ""]
    # 2. By source
    L += ["## 2. By source", "",
          "Yield is shown passages per 1,000 words read. Secular is the share of passages that make sense with no religious belief. "
          "Top themes are the three most frequent theme tags.", "",
          "| Source | Tradition | Translator | Words read | Extracted | Shown | Hidden | Cut | Dup | Yield | Median words | Secular | Top themes |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    by_src = defaultdict(list)
    for p in allp:
        by_src[p["source"]].append(p)
    src_theme_fam = {}
    for src in sorted(by_src, key=lambda s: -sum(p["status"] in ("keep", "no-distress") for p in by_src[s])):
        ps = by_src[src]
        sh = [p for p in ps if p["status"] in ("keep", "no-distress")]
        c = Counter(p["status"] for p in ps)
        themes = Counter(t for p in sh for t in p["tags"]["themes"])
        src_theme_fam[src] = Counter(THEME.get(t, "?") for p in sh for t in p["tags"]["themes"])
        tr, work, who = SRC.get(src, ("?", "?", "?"))
        L.append(f"| {src} | {tr} | {who} | {words_read[src]:,} | {len(ps)} | {len(sh)} | {c['no-distress']} | {c['cut']} | {c['dup']} | "
                 f"{1000 * len(sh) / words_read[src]:.2f} | {median(p['words'] for p in sh):.0f} | "
                 f"{pct(sum(p['tags']['faith'] == 'secular' for p in sh), len(sh))} | {', '.join(t for t, _ in themes.most_common(3))} |")
    L += [f"| **Total** | | | **{sum(words_read.values()):,}** | **{len(allp):,}** | **{n:,}** | **{st['no-distress']}** | **{st['cut']}** | **{st['dup']}** | "
          f"**{1000 * n / sum(words_read.values()):.2f}** | **{median(w):.0f}** | **{pct(faith['secular'], n)}** | |", ""]
    # 3. By theme
    L += ["## 3. By theme", "",
          "Each passage carries 1–3 theme tags, so shares add to more than 100%. Sources = number of sources with at least one passage on the theme.", ""]
    themes = Counter(t for p in shown for t in p["tags"]["themes"])
    breadth = {t: len({p["source"] for p in shown if t in p["tags"]["themes"]}) for t in themes}
    fam_tot = Counter(THEME.get(t, "?") for p in shown for t in p["tags"]["themes"])
    L += ["| Family | Passages with a theme in the family |", "| --- | --- |"]
    L += [f"| {f} | {c:,} ({pct(c, n)}) |" for f, c in fam_tot.most_common()]
    L += ["", "| Theme | Family | Passages | Share | Sources |", "| --- | --- | --- | --- | --- |"]
    for t, c in themes.most_common():
        L.append(f"| {t} | {THEME.get(t, '?')} | {c:,} | {pct(c, n)} | {breadth[t]} |")
    L.append("")
    missing = [t for t in THEME if t not in themes]
    L += [f"Themes with no passage: {', '.join(missing) if missing else 'none'}.", ""]
    # 4. Source x theme family
    fams = [f for f, _ in fam_tot.most_common()]
    L += ["## 4. Source by theme family", "", "Share of each source's theme tags that fall in each family (rows add to 100%).", "",
          "| Source | " + " | ".join(fams) + " |", "| --- |" + " --- |" * len(fams)]
    for src, fc in src_theme_fam.items():
        tot = sum(fc.values())
        L.append(f"| {src} | " + " | ".join(pct(fc[f], tot) for f in fams) + " |")
    L.append("")
    # 5. Feelings, situations, tone
    for title, key, FAM in (("5. By feeling (what the reader arrives with)", "feelings", FEEL),
                            ("6. By situation", "situations", SIT)):
        cnt = Counter(t for p in shown for t in p["tags"][key])
        ft = Counter(FAM.get(t, "?") for p in shown for t in p["tags"][key])
        L += [f"## {title}", "", "| Family | Tags (passages) |", "| --- | --- |"]
        for f, c in ft.most_common():
            tags = ", ".join(f"{t} {cnt[t]:,}" for t, _ in sorted(((t, cnt[t]) for t in cnt if FAM.get(t) == f), key=lambda x: -x[1]))
            L.append(f"| {f} ({c:,}) | {tags} |")
        none = [t for t in FAM if t not in cnt]
        L += ["", f"Tags with no passage: {', '.join(none) if none else 'none'}."]
        if key == "situations":
            L.append(f"Passages with no situation tag: {sum(not p['tags']['situations'] for p in shown):,} ({pct(sum(not p['tags']['situations'] for p in shown), n)}).")
        L.append("")
    tone = Counter(t for p in shown for t in p["tags"]["tone"])
    L += ["## 7. By tone", "", "| Tone | Passages | Share |", "| --- | --- | --- |"]
    L += [f"| {t} | {c:,} | {pct(c, n)} |" for t, c in tone.most_common()] + [""]
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {n:,} shown passages, {len(themes)} themes used, {len(missing)} unused")


if __name__ == "__main__":
    main()
