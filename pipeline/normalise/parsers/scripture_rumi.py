"""Masnavi (Whinfield's abridged verse translation, Wikisource scrape): six books.

Source layout (from the scrape): books are split by "===== BOOK BREAK =====". Every
line of verse is its own blank-line-separated paragraph (the scrape keeps no couplet
grouping), interleaved with:
  * STORY headings, each followed by Whinfield's prose "argument"      -> kept as headings
  * his marginal rubric lines ("Description of Love.") and prose links -> kept as headings
  * "NOTES:" blocks of numbered footnotes (some with quoted verse)     -> dropped
  * footnote markers (1-2 digits after a word or punctuation, OCR "l") -> removed
  * Wikisource navigation ("Next: The Masnavi Book II"), page header   -> dropped

Verse units are couplets: consecutive verse lines are paired within each run between
headings. Rubric lines cannot be told from verse lines by form alone, so inside a run
with an odd number of lines the most heading-like line (short, ends in a full stop, no
internal commas) is taken as the rubric. A heading mistaken for verse stays in the text,
and a verse line mistaken for a heading is still kept (as a heading unit), so no wording
is lost either way; see the heading units' meta {"heuristic": true}.
Translator wording and OCR slips are never edited.
"""

import re
from common import Unit, clean_prose, read_source

SOURCES = ["rumi-masnavi-whinfield"]

BOOK_BREAK = "===== BOOK BREAK ====="
ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
         "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15, "XVI": 16, "XVII": 17, "XVIII": 18}

# Footnote marker: a 1-2 digit number standing on its own (not inside a word, hyphenated
# item, or an enumeration like "(1)").
MARKER = re.compile(r"\s*(?<![\w(~'\-])\d{1,2}(?![\w)~\-])")
OCR_MARKER = re.compile(r"(?<=[,;.:!?])\s*l$")      # footnote "1" read as "l" at line end
STORY = re.compile(r"^=*\s*STORY ([IVX]+)\.?\s*(.*?)\s*=*$")


def strip_markers(s: str) -> str:
    s = MARKER.sub("", s)
    s = OCR_MARKER.sub("", s)
    return s.strip()


def heading_cost(line: str, prev: str | None = None, nxt: str | None = None) -> float:
    """Lower = more likely a rubric heading. inf = cannot be one."""
    core = line.rstrip("\"' ")
    if not core.endswith("."):
        return float("inf")
    if not (line[0].isupper() or line[0] in "(\"'"):
        return float("inf")
    c = 1.0
    # a rubric starts a new thought: the line before it ends a sentence,
    # the line after it starts one
    if prev is not None and prev.rstrip("\"' ")[-1:] in ",;:":
        c += 1.5
    if nxt is not None and nxt[:1].islower():
        c += 1.5
    if re.search(r"[,;:]", line):
        c += 1.5
    if len(line) > 70:
        c -= 0.5
    if line.startswith("("):
        c -= 0.5
    return c


def couplet_cost(a: str, b: str) -> float:
    c = 0.0
    if a.rstrip("\"' ")[-1:] in ".!?":
        c += 0.3
    if b.rstrip("\"' ")[-1:] == ",":
        c += 0.3
    return c


def segment(lines: list[str]):
    """Best split of a run of verse lines into ('couplet', i, j) / ('head', i) / ('single', i)."""
    n = len(lines)
    INF = float("inf")
    best = [INF] * (n + 1)
    back = [None] * (n + 1)
    best[0] = 0.0
    for i in range(n):
        if best[i] == INF:
            continue
        if i + 1 < n:
            c = best[i] + couplet_cost(lines[i], lines[i + 1])
            if c < best[i + 2]:
                best[i + 2], back[i + 2] = c, ("couplet", i)
        h = heading_cost(lines[i], lines[i - 1] if i else None, lines[i + 1] if i + 1 < n else None)
        if h < INF and best[i] + h < best[i + 1]:
            best[i + 1], back[i + 1] = best[i] + h, ("head", i)
        if best[i] + 4.0 < best[i + 1]:
            best[i + 1], back[i + 1] = best[i] + 4.0, ("single", i)
    out, k = [], n
    while k > 0:
        kind, i = back[k]
        out.append((kind, i))
        k = i
    return out[::-1]


def parse(source):
    raw = read_source(f"{source}/source.txt")
    books = raw.split(BOOK_BREAK)[1:]            # drop the Wikisource header before book 1
    assert len(books) == 6, len(books)
    units = []
    for bi, text in enumerate(books, 1):
        paras = []
        for blk in re.split(r"\n\s*\n", text):
            lines = [x.strip() for x in blk.split("\n") if x.strip()]
            joined = " ".join(lines)
            if not lines or re.fullmatch(r"\d{1,2}", joined):
                continue                       # lone footnote numbers
            if not re.search(r"\w", joined):   # stray punctuation: the tail of the previous line
                if paras:
                    paras[-1] += joined
                continue
            if len(lines) > 1 and len(joined) <= 150 and not STORY.match(joined) \
                    and not joined.startswith(("NOTES:", "Next:")):
                paras.extend(lines)       # adjacent verse lines with no blank between them
            else:
                paras.append(joined)
        section, in_notes, run = f"Book {bi}", False, []

        def flush():
            nonlocal run
            if not run:
                return
            for kind, i in segment(run):
                if kind == "couplet":
                    units.append(Unit(loc={"book": bi, "section": section, "couplet": None},
                                      display=f"Masnavi, Book {bi}, {section}",
                                      text="\n".join(run[i:i + 2]), kind="verse"))
                elif kind == "head":
                    units.append(Unit(loc={"book": bi, "section": section}, display=f"Masnavi, Book {bi}, {section}",
                                      text=run[i], kind="heading", meta={"rubric": True, "heuristic": True}))
                else:
                    units.append(Unit(loc={"book": bi, "section": section, "couplet": None},
                                      display=f"Masnavi, Book {bi}, {section}", text=run[i], kind="verse",
                                      meta={"single_line": True}))
            run = []

        for p in paras:
            m = STORY.match(p)
            if p.startswith("Note on Apocryphal"):           # end-matter of Book VI/VII
                break
            if p.startswith(("Next:", "Previous:")):
                flush()
                continue
            if m or p.startswith(("Epilogue to", "PROLOGUE")):
                flush()
                in_notes = False
                if m:
                    num, title = m.group(1), strip_markers(m.group(2))
                    section = f"Story {num}. {title}".strip()
                    heading = section
                elif p.startswith("PROLOGUE"):
                    section = heading = "Prologue"
                else:
                    section = heading = strip_markers(p)
                units.append(Unit(loc={"book": bi, "section": section}, display=f"Masnavi, Book {bi}, {section}",
                                  text=heading, kind="heading"))
                continue
            if p.startswith("NOTES:"):
                flush()
                in_notes = True
                continue
            if in_notes:
                continue
            if len(p) > 150:                                  # Whinfield's linking prose / argument
                flush()
                units.append(Unit(loc={"book": bi, "section": section}, display=f"Masnavi, Book {bi}, {section}",
                                  text=re.sub(r"\s+([,.;:])", r"\1", strip_markers(p)), kind="heading",
                                  meta={"argument": True}))
                continue
            run.append(strip_markers(p))
        flush()
    # number couplets within each section
    counters = {}
    for u in units:
        if u.kind == "verse":
            key = (u.loc["book"], u.loc["section"])
            counters[key] = counters.get(key, 0) + 1
            u.loc["couplet"] = counters[key]
    return units
