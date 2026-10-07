"""Seneca, Moral Letters to Lucilius (Gummere, Loeb) -- Wikisource EPUB export.

The export holds the English text only (no facing Latin). Around the 124 letters
sit Loeb front matter, volume breaks, footnote bodies ("↑" blocks), appendices
and indexes. We keep only Gummere's English of each letter:
  * letter titles (taken from the Loeb contents list) become headings,
  * the English salutation ("Greetings from Seneca ...") becomes a heading,
  * every paragraph of the letter body becomes a prose unit; the section number
    (1., 2., ...) is stripped from the text and kept in meta["section"].
Removed: footnote markers "[ n ]", footnote bodies, section numerals, volume
front matter, indexes.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import Unit, clean_prose, clean_verse, read_source  # noqa: E402

SOURCES = ["seneca-letters-gummere"]

_ROMAN = [(100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def roman(n: int) -> str:
    out = ""
    for v, s in _ROMAN:
        while n >= v:
            out += s
            n -= v
    return out


def _toc_titles(lines):
    """Letter titles from the Loeb contents list: 'XIII.' / blank / 'ON GROUNDLESS FEARS'."""
    titles = {}
    for i, l in enumerate(lines[:1000]):
        m = re.fullmatch(r"([IVXLC]+)\.", l.strip())
        if m:
            j = i + 1
            while not lines[j].strip():
                j += 1
            titles[m.group(1)] = clean_prose(lines[j])
    return titles


def _find_headings(lines, titles):
    start = next(i for i, l in enumerate(lines) if l.strip() == "THE EPISTLES OF SENECA" and i > 1000)
    pos, heads = start, []
    for n in range(1, 125):
        r = roman(n)
        pat = re.compile(r"^" + r + r"\.\s+[A-Z][A-Z’' ,.\-]+$")
        found = None
        for i in range(pos, len(lines)):
            s = lines[i].strip()
            if pat.match(s) or (s == titles[r] and i > pos):  # Letter 91 has no numeral in the body
                found = i
                break
        assert found is not None, f"heading for letter {n} not found"
        heads.append(found)
        pos = found + 1
    return heads


_MARK = re.compile(r"^\d+\.$")


def _strip_note_markers(block):
    """Drop the three-line footnote marker '[' / '12' / ']' wherever it occurs."""
    out, i = [], 0
    while i < len(block):
        if (block[i].strip() == "[" and i + 2 < len(block)
                and block[i + 1].strip().isdigit() and block[i + 2].strip() == "]"):
            i += 3
            continue
        out.append(block[i])
        i += 1
    return out


def _letter_paragraphs(block):
    """Return [(section|None, text)] for one letter's body lines."""
    block = _strip_note_markers(block)
    paras, cur, sec, cur_sec = [], [], None, None

    def flush():
        nonlocal cur
        if cur:
            text = clean_prose("".join(cur))
            if text:
                paras.append((cur_sec, text))
        cur = []

    for line in block:
        s = line.strip()
        if _MARK.match(s):
            flush()
            sec = int(s[:-1])
            cur_sec = sec
        elif line == "":
            flush()
        elif not s:
            cur.append(" ")  # nbsp-only lines sit inside ". . . ." ellipsis rows: spacing, not a break
        else:
            cur.append(line)
    flush()
    return paras


VERSE_MAX = 76  # the export drops line structure of Gummere's verse quotations: each
                # verse line arrives as its own short paragraph.


def _group_verse(paras):
    """Merge runs of >=2 consecutive short paragraphs of one section into one verse unit
    (a list of lines). Single short paragraphs stay prose."""
    out, run = [], []

    def flush():
        nonlocal run
        if len(run) >= 2:
            out.append((run[0][0], [t for _, t in run]))
        else:
            out.extend(run)
        run = []

    for sec, text in paras:
        if len(text) <= VERSE_MAX and sec is not None and (not run or run[-1][0] == sec):
            run.append((sec, text))
        else:
            flush()
            if len(text) <= VERSE_MAX and sec is not None:
                run = [(sec, text)]
            else:
                out.append((sec, text))
    flush()
    return out


def parse(source: str):
    lines = read_source(f"{source}/source.txt").split("\n")
    titles = _toc_titles(lines)
    heads = _find_headings(lines, titles)
    units = []
    for n in range(1, 125):
        end = heads[n] if n < 124 else len(lines)
        body = lines[heads[n - 1] + 1:end]
        # footnote bodies start at the first "↑" line; everything after is apparatus
        cut = next((i for i, l in enumerate(body) if l.strip() == "↑"), len(body))
        body = body[:cut]
        paras = _group_verse(_letter_paragraphs(body))
        units.append(Unit({"letter": n}, f"Letter {n}", titles[roman(n)], kind="heading"))
        k = 0
        for sec, text in paras:
            if sec is None:
                # text before the first section numeral is the salutation
                units.append(Unit({"letter": n}, f"Letter {n}", text, kind="heading"))
                continue
            k += 1
            if isinstance(text, list):  # verse quotation: one line per source paragraph
                units.append(Unit({"letter": n, "para": k}, f"Letter {n}", clean_verse(text),
                                  kind="verse", meta={"section": sec}))
            else:
                units.append(Unit({"letter": n, "para": k}, f"Letter {n}", text, meta={"section": sec}))
    return units
