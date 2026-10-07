"""Helpers shared by the gutenberg_*.py parsers (no SOURCES: not a parser itself).

Everything here only REMOVES apparatus or restructures; it never rewrites the
author's/translator's words. Whitespace is the only thing that may change.
"""

from __future__ import annotations

import re
import sys

from common import SOURCE_DIR, Unit, clean_prose, clean_verse, paragraphs, gutenberg_body

# footnote markers like [1] or [Footnote 3] (NOT [Greek: ...], [Sidenote: ...])
FN_MARK = re.compile(r"\[(?:Footnote\s*:?\s*)?\d+\]")

ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman(s: str) -> int:
    s = s.upper().strip(". ")
    total = 0
    for i, ch in enumerate(s):
        v = ROMAN[ch]
        total += -v if i + 1 < len(s) and ROMAN[s[i + 1]] > v else v
    return total


def roman_str(n: int) -> str:
    out = ""
    for v, r in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
                 (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += r
            n -= v
    return out


def is_roman(s: str) -> bool:
    return bool(re.fullmatch(r"[IVXLCDM]+", s.strip(". ")))


def load(source: str) -> str:
    """Read source.txt tolerating utf-8 (BOM) and 8-bit encodings; LF newlines."""
    raw = (SOURCE_DIR / source / "source.txt").read_bytes()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            t = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    return t.replace("\r\n", "\n").replace("\r", "\n")


def body(text: str) -> str:
    """Text between the Gutenberg START/END markers, minus the closing 'End of ...' line."""
    t = gutenberg_body(text)
    m = re.search(r"^\s*End of (the )?Project Gutenberg", t, re.M | re.I)
    if m:
        t = t[:m.start()]
    return t


def indent_of(line: str) -> int:
    return len(line.expandtabs(8)) - len(line.expandtabs(8).lstrip(" "))


def all_indented(block: list[str], n: int = 2) -> bool:
    return all(indent_of(l) >= n for l in block)


def mixed_indent(block: list[str], n: int = 2) -> bool:
    flags = [indent_of(l) >= n for l in block]
    # a first-line paragraph indent alone is normal prose, not mixed
    return any(flags) and not all(flags) and flags != [True] + [False] * (len(flags) - 1)


def split_runs(blocks: list[list[str]], n: int = 2) -> list[list[str]]:
    """Split blocks that mix indented (verse) and flush (prose) lines into separate blocks."""
    out = []
    for b in blocks:
        if not mixed_indent(b, n):
            out.append(b)
            continue
        run, flag = [], None
        for l in b:
            f = indent_of(l) >= n
            if flag is not None and f != flag:
                out.append(run)
                run = []
            run.append(l)
            flag = f
        out.append(run)
    return out


def is_stars(block: list[str]) -> bool:
    return len(block) == 1 and re.fullmatch(r"\s*(\*\s+){2,}\*\s*", block[0] + " ") is not None


def prose(block_or_text) -> str:
    return clean_prose(block_or_text)


def strip_markers(s: str, stats: dict, key: str = "markers") -> str:
    """Remove [n] / [Footnote n] markers; count them."""
    n = len(FN_MARK.findall(s))
    if n:
        stats[key] = stats.get(key, 0) + n
        s = FN_MARK.sub("", s)
    return s


def split_footnote_blocks(blocks: list[list[str]], stats: dict, start=r"\[Footnote\b"):
    """Drop '[Footnote N: ...]' blocks (bracket-balanced, may span blocks)."""
    out, i = [], 0
    pat = re.compile(start)
    while i < len(blocks):
        b = blocks[i]
        if pat.match(b[0].lstrip()):
            depth, j = 0, i
            while j < len(blocks):
                txt = " ".join(blocks[j])
                depth += txt.count("[") - txt.count("]")
                j += 1
                if depth <= 0:
                    break
            stats["footnote_bodies"] = stats.get("footnote_bodies", 0) + 1
            i = j
            continue
        out.append(b)
        i += 1
    return out


def text_unit(b, loc, display, verse=True, stats=None, strip_fn=True, work=None, meta=None) -> Unit:
    """Build a prose or verse unit from a block of lines."""
    lines = list(b)
    if strip_fn and stats is not None:
        lines = [strip_markers(l, stats) for l in lines]
    if verse and all_indented(lines, 2):
        return Unit(loc=loc, display=display, text=clean_verse(lines), kind="verse", work=work, meta=meta or {})
    return Unit(loc=loc, display=display, text=clean_prose(lines), kind="prose", work=work, meta=meta or {})


def heading(text, loc, display, work=None, meta=None) -> Unit:
    return Unit(loc=loc, display=display, text=clean_prose(text), kind="heading", work=work, meta=meta or {})


def report(source: str, stats: dict, warns: list[str] | None = None):
    bits = ", ".join(f"{k}={v}" for k, v in sorted(stats.items())) or "none"
    print(f"[{source}] removed: {bits}", file=sys.stderr)
    for w in (warns or [])[:15]:
        print(f"[{source}] WARN {w}", file=sys.stderr)
    if warns and len(warns) > 15:
        print(f"[{source}] WARN ... {len(warns) - 15} more", file=sys.stderr)


def titlecase_display(s: str) -> str:
    return s.strip()


_SMALL = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "of", "on", "or", "the", "to", "with", "versus"}


def tc(s: str) -> str:
    """Title-case an ALL-CAPS heading for display only (headings are not passages)."""
    words = s.lower().split()
    return " ".join(w if (i and w in _SMALL) else w[:1].upper() + w[1:] for i, w in enumerate(words))
