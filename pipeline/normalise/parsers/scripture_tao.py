"""Tao Te Ching (Legge, Gutenberg #216): one unit per paragraph, chapters numbered 1-81.

Legge prints "N. 1. text" at the start of each chapter and "2. text" for later
sections. Those leading numerals are editorial numbering and are stripped; the
translator's wording is untouched. Indented rhyming paraphrases stay as verse units.
"""

import re
from common import Unit, clean_prose, clean_verse, gutenberg_body, paragraphs, read_source

SOURCES = ["tao-te-ching-legge"]

NUMERAL = re.compile(r"^(?:Ch\. )?\d+\.(?:\s+\d+\.)?(?:\s+|$)")


def parse(source):
    text = gutenberg_body(read_source(f"{source}/source.txt"))
    # Drop the trailing Gutenberg colophon line, if any, and the title block.
    start = text.index("PART 1.")
    lines = [l for l in text[start:].split("\n")
             if not re.match(r"^End of (the )?Project Gutenberg", l.strip())]
    # Chapter n+1 starts after >= 2 blank lines with "n+1." at the line start.
    chapters, cur, blank, c = [], None, 0, 0
    heads = []   # (part heading lines) kept as headings, keyed by chapter they precede
    pending_heading = None
    for l in lines:
        if not l.strip():
            blank += 1
            if cur is not None:
                cur.append(l)
            continue
        if re.match(r"^PART [IVX0-9]+\.\s*$", l):
            pending_heading = l.strip()
            blank = 0
            continue
        if re.match(rf"^(Ch\. )?{c + 1}\.(\s|$)", l) and (blank >= 2 or c == 0):
            c += 1
            cur = [l]
            chapters.append([c, pending_heading, cur])
            pending_heading = None
        elif cur is not None:
            cur.append(l)
        blank = 0
    assert c == 81, c
    units = []
    for n, part, lns in chapters:
        if part:
            units.append(Unit(loc={"part": part}, display=part.rstrip("."), text=part.rstrip("."), kind="heading"))
        units.append(Unit(loc={"chapter": n}, display=f"Tao Te Ching {n}", text=f"Chapter {n}", kind="heading"))
        k = 0
        for para in paragraphs("\n".join(lns)):
            # strip "Ch. n. m." / "m." numerals from the first line only
            first = NUMERAL.sub("", para[0])
            para = [x for x in [first] + para[1:] if x.strip()]
            if not para:                      # a bare "3." or "12." numeral paragraph
                continue
            indented = all(x.startswith(" ") for x in para)
            k += 1
            units.append(Unit(loc={"chapter": n, "para": k}, display=f"Tao Te Ching {n}",
                              text=clean_verse(para) if indented else clean_prose(para),
                              kind="verse" if indented else "prose"))
    return units

