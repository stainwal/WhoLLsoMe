"""Gibran's shorter books in his own English (Day 15 aphoristic additions, Corpus-Policy 2.2).
The Prophet has its own parser (scripture_prophet.py).

gibran-madman  (PG #5616, Knopf 1918)
  An untitled opening piece, then 34 titled parables and poems; one unit per paragraph.
  A title is a short line set off by four or more blank lines. Removed: boilerplate and
  the title-page lines.

gibran-forerunner  (PG #54580, Knopf 1920)
  An untitled opening piece, then 24 titled pieces named in the CONTENTS list; one unit
  per paragraph. Removed: boilerplate, the "Books by" advertisement, title page, copyright,
  contents, [Illustration] lines, "* * *" scene breaks, and the underscores marking
  italic paragraphs (the cat's lines in "The King-Hermit").

gibran-sand-and-foam  (Wikisource, validated March 2022, from the Knopf printing; first
  published 1926)
  Unnumbered aphorisms; one unit per paragraph, located by paragraph number. The book
  separates aphorisms by spacing that the rendering does not keep, so a verse aphorism of
  several lines becomes several consecutive units (extraction may span them). Removed:
  Wikisource navigation and licence lines, front matter up to the half-title, the
  zero-width spaces marking page breaks, and the type note at the end.
"""

import re

from common import Unit, clean_prose, paragraphs
from .gutenberg_util import body, heading, load, report

SOURCES = ["gibran-madman", "gibran-forerunner", "gibran-sand-and-foam"]


def parse(source):
    stats = {}
    if source == "gibran-sand-and-foam":
        units = sand_and_foam(load(source), stats)
    else:
        units = {"gibran-madman": madman, "gibran-forerunner": forerunner}[source](body(load(source)), stats)
    report(source, stats)
    return units


_SMALL = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "of", "on", "or", "the", "to", "with"}


def tc(s):
    """Title-case an ALL-CAPS contents title for display: each hyphen part capitalised, a leading quote kept."""
    def word(w, i):
        core = w.lower()
        if i and core in _SMALL:
            return core
        return "-".join(part[:1].upper() + part[1:] for part in core.split("-"))
    out = " ".join(word(w, i) for i, w in enumerate(s.split()))
    return re.sub(r'^(["\u201c])(\w)', lambda m: m.group(1) + m.group(2).upper(), out)


def pieces_to_units(work_display, pieces, stats):
    """pieces: [(title or None, text)] -> heading + paragraph units."""
    units = []
    for n, (title, text) in enumerate(pieces):
        if title is None:
            display = f"{work_display}: opening piece"
            loc = {"piece": 0}
        else:
            display = f"{work_display}: {title}"
            loc = {"piece": n, "title": title}
            units.append(heading(title, loc, display))
        for k, para in enumerate(paragraphs(text), 1):
            units.append(Unit(loc={**loc, "paragraph": k}, display=f"{display}, paragraph {k}",
                              text=clean_prose(para), kind="prose"))
    stats["pieces"] = len(pieces)
    return units


def madman(text, stats):
    i = text.index("By Kahlil Gibran")
    text = text[i + len("By Kahlil Gibran"):]
    # titles: a short line set off by 4+ blank lines on each side
    parts = re.split(r"\n{5,}([^\n]{1,45})\n{5,}", "\n" * 5 + text.strip("\n") + "\n" * 5)
    # parts[0] is the untitled opening piece
    pieces = [(None, parts[0])]
    for t, body_ in zip(parts[1::2], parts[2::2]):
        pieces.append((t.strip(), body_))
    assert len(pieces) == 35, f"Madman: {len(pieces)} pieces"
    return pieces_to_units("The Madman", pieces, stats)


def forerunner(text, stats):
    i = text.index("\nCONTENTS\n")
    contents = re.search(r"\nCONTENTS\n(.*?)\n\n\n\s*THE FIVE ILLUSTRATIONS", text[i:], re.S).group(1)
    titles = [re.sub(r"\s+\d+$", "", l.strip()) for l in contents.split("\n") if l.strip()]
    assert len(titles) == 24, f"Forerunner: {len(titles)} titles"
    j = text.index("DRAWINGS BY THE AUTHOR", i)
    rest = text[j + len("DRAWINGS BY THE AUTHOR"):]
    rest = re.sub(r"^\s*\[Illustration:[^\]]*\]\s*$", "", rest, flags=re.M)
    stats["illustrations"] = 1
    rest = re.sub(r"^\s*(\*\s+)+\*\s*$", "", rest, flags=re.M)          # scene breaks
    rest = rest.replace("_", "")
    pieces, cur_title, cur = [], None, []
    pending = list(titles)
    for line in rest.split("\n"):
        if pending and line.strip() == pending[0]:
            pieces.append((cur_title, "\n".join(cur)))
            cur_title, cur = pending.pop(0), []
        else:
            cur.append(line)
    pieces.append((cur_title, "\n".join(cur)))
    assert not pending, f"Forerunner: titles not found: {pending}"
    return pieces_to_units("The Forerunner", [(tc(t) if t else None, b) for t, b in pieces], stats)


def sand_and_foam(text, stats):
    start = text.index("I am forever walking upon these shores")
    end = text.index("A NOTE ON THE TYPE")
    text = text[start:end].replace("​", "")
    stats["front_and_back_matter"] = 1
    units = []
    for k, para in enumerate(paragraphs(text), 1):
        units.append(Unit(loc={"paragraph": k}, display=f"Sand and Foam, paragraph {k}",
                          text=clean_prose(para), kind="prose"))
    return units
