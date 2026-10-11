"""Tagore's own English (Day 15 aphoristic additions, Corpus-Policy section 2.2).

tagore-stray-birds  (PG #6524, Macmillan 1916)
  326 numbered aphorisms, one unit each. Removed: boilerplate, title page lines,
  the two bracketed notes (translation, frontispiece) and the dedication.

tagore-gitanjali  (PG #7164, 1912)
  103 numbered prose poems, one unit per stanza (paragraph), display "Gitanjali, poem N".
  Removed: boilerplate, title page, dedication, W. B. Yeats's Introduction (not Tagore's
  words), and the underscores marking italic words (_maya_).

tagore-sadhana  (PG #6842, 1913; this etext 1916)
  Author's Preface plus chapters I-VIII, one unit per paragraph, chapter titles as headings.
  Removed: boilerplate, title page, dedication, contents, the bracketed
  "[Footnote: ...]" Sanskrit originals (one misspelt "[Footnoe:"), a transcriber's note,
  and italic underscores.
"""

import re

from common import Unit, clean_prose, paragraphs
from .gutenberg_util import body, heading, load, report, roman, tc

SOURCES = ["tagore-stray-birds", "tagore-gitanjali", "tagore-sadhana"]

FOOTNOTE = re.compile(r"\s*\[Footno[a-z]*:[^\]]*\]", re.S)   # one is misspelt "[Footnoe:" in the etext


def parse(source):
    text = body(load(source))
    stats = {}
    units = {"tagore-stray-birds": stray_birds, "tagore-gitanjali": gitanjali,
             "tagore-sadhana": sadhana}[source](text, stats)
    report(source, stats)
    return units


def stray_birds(text, stats):
    # body starts at the first numbered aphorism ("1" on its own line)
    m = re.search(r"^1\n", text, re.M)
    text = text[m.start():]
    units, num, lines = [], None, []
    for line in text.split("\n"):
        if re.fullmatch(r"\d+", line.strip()):
            if num is not None:
                units.append(aphorism(num, lines))
            num, lines = int(line.strip()), []
        elif num is not None:
            lines.append(line)
    units.append(aphorism(num, lines))
    assert [u.loc["aphorism"] for u in units] == list(range(1, 327)), "Stray Birds: numbering gap"
    stats["aphorisms"] = len(units)
    return units


def aphorism(num, lines):
    # a few aphorisms are short dialogues laid out as separate lines; joined as prose
    return Unit(loc={"aphorism": num}, display=f"Stray Birds, {num}", text=clean_prose(lines), kind="prose")


def gitanjali(text, stats):
    i = text.index("\nGITANJALI\n")                      # Yeats's Introduction precedes this
    stats["intro_removed"] = 1
    text = text[i + len("\nGITANJALI\n"):].replace("_", "")
    units, poem, k = [], None, 0
    for para in paragraphs(text):
        joined = " ".join(l.strip() for l in para)
        if re.fullmatch(r"\d+\.", joined):
            poem, k = int(joined[:-1]), 0
            continue
        k += 1
        units.append(Unit(loc={"poem": poem, "stanza": k}, display=f"Gitanjali, poem {poem}",
                          text=clean_prose(para), kind="prose"))
    assert units[-1].loc["poem"] == 103
    stats["poems"], stats["stanzas"] = 103, len(units)
    return units


def sadhana(text, stats):
    i = text.index("Author's Preface")
    j = text.index("\nCONTENTS\n")
    preface = text[i + len("Author's Preface"):j]
    rest = text[j:]
    # chapters: a roman numeral on its own line, then the title on its own line
    heads = list(re.finditer(r"\n\n\n+(I|II|III|IV|V|VI|VII|VIII)\n\n+([A-Z][A-Z ,']+)\n", rest))
    assert len(heads) == 8, f"Sadhana: {len(heads)} chapter headings"
    units = [heading("Author's Preface", {"chapter": 0}, "Sādhanā: Author's Preface")]
    units += paras(preface, {"chapter": 0}, "Sādhanā: Author's Preface", stats)
    for n, h in enumerate(heads):
        num, title = roman(h.group(1)), tc(h.group(2))
        end = heads[n + 1].start() if n + 1 < len(heads) else len(rest)
        display = f"Sādhanā: {title}"
        units.append(heading(f"{h.group(1)}. {title}", {"chapter": num}, display))
        units += paras(rest[h.end():end], {"chapter": num}, display, stats)
    return units


def paras(text, loc, display, stats):
    n = len(FOOTNOTE.findall(text))
    if n:
        stats["footnotes"] = stats.get("footnotes", 0) + n
        text = FOOTNOTE.sub("", text)
    text = text.replace("_", "")
    out = []
    blocks = [b for b in paragraphs(text) if not b[0].lstrip().startswith("[Transcriber")]
    stats["transcriber_notes"] = stats.get("transcriber_notes", 0) + len(paragraphs(text)) - len(blocks)
    for k, para in enumerate(blocks, 1):
        out.append(Unit(loc={**loc, "paragraph": k}, display=f"{display}, paragraph {k}",
                        text=clean_prose(para), kind="prose"))
    return out
