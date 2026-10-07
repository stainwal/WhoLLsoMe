"""Philosophy sources from Project Gutenberg.

aristotle-ethics (Chase translation, ~1847, with J. A. Smith's introduction)
  Kept: Books I-X of the text (headed "ARISTOTLE'S ETHICS").
  Removed: boilerplate, title, Smith's long Introduction and the bibliography,
  the "NOTES" section after Book X (translator's notes, ~1,480 lines),
  "[Sidenote: ...]" markers (used for loc: Bekker pages; chapter numerals are
  too OCR-corrupted to cite, so only meta["chapter_est"] carries a best guess),
  stray "*" in front of sidenotes, standalone chapter numerals, one
  "[Illustration: ...]" line (a diagram). "[Greek: ...]" transliterations and
  Chase's own square-bracket insertions are part of the translation: kept.
  One sidenote in Book IX carries real translation text (a sentence on
  perceiving that one lives); the text is kept, only the marker is removed.

plato-apology-jowett, plato-phaedo-jowett
  Kept: the dialogue text only. Removed: boilerplate, title, Jowett's Introduction
  and (Phaedo) the Persons/Scene list, and Jowett's inline editorial
  parentheticals (cross-references and alternative renderings, listed in code).
  No Stephanus numbers exist in these texts, so loc is {"para": n}. In the
  Phaedo the frame speakers ECHECRATES/PHAEDO are recorded in meta["frame_speaker"]
  and the "NAME: " label is removed from the text.

schopenhauer-counsels-maxims, schopenhauer-wisdom-of-life (Bailey Saunders)
  Kept: Schopenhauer's own Introduction and all chapters/sections.
  Removed: boilerplate, title/contents, footnote markers [n] and the
  "[Footnote n: ...]" bodies (these include Saunders' "Translator's Note"s),
  the "SECTION n." prefixes (moved into loc). "[Greek: ...]" kept.
"""

from __future__ import annotations

import re

from common import Unit, clean_prose, clean_verse, paragraphs

from . import gutenberg_util as U

SOURCES = [
    "aristotle-ethics",
    "plato-apology-jowett",
    "plato-phaedo-jowett",
    "schopenhauer-counsels-maxims",
    "schopenhauer-wisdom-of-life",
]


def parse(source: str) -> list[Unit]:
    return {
        "aristotle-ethics": _aristotle,
        "plato-apology-jowett": _apology,
        "plato-phaedo-jowett": _phaedo,
        "schopenhauer-counsels-maxims": lambda s: _schopenhauer(s, "counsels"),
        "schopenhauer-wisdom-of-life": lambda s: _schopenhauer(s, "wisdom"),
    }[source](source)


# ---------------------------------------------------------------------------
# Plato
# ---------------------------------------------------------------------------
_APOLOGY_EDITORIAL = [
    r"\(Or, I am certain that I am right in taking this course\.\)",
    r"\(Aristoph\., Clouds\.\)",
    r"\(Probably in allusion to Aristophanes[^()]*\)",
]
_PHAEDO_EDITORIAL = [r"\((?:But c|C|c)ompare [^()]*\)"]


def _strip_editorial(txt: str, pats: list[str], stats: dict) -> str:
    for p in pats:
        txt, n = re.subn(r"\s?" + p, "", txt)
        stats["editorial_parentheticals"] = stats.get("editorial_parentheticals", 0) + n
    return txt


def _apology(src):
    stats, warns, units = {}, [], []
    text = U.body(U.load(src))
    i = text.index("\nAPOLOGY\n\n\nHow you")
    blocks = paragraphs(text[i:])
    units.append(U.heading("Apology", {}, "Apology"))
    para = 0
    for b in blocks[1:]:
        if U.mixed_indent(b):
            warns.append("mixed indent")
        txt = _strip_editorial(clean_prose(b), _APOLOGY_EDITORIAL, stats)
        para += 1
        units.append(Unit({"para": para}, f"Apology, paragraph {para}", clean_prose(txt)))
    assert stats["editorial_parentheticals"] == 3
    U.report(src, stats, warns)
    return units


def _phaedo(src):
    stats, warns, units = {}, [], []
    text = U.body(U.load(src))
    i = text.index("\nPHAEDO\n\n\nPERSONS")
    blocks = paragraphs(text[i:])
    units.append(U.heading("Phaedo", {}, "Phaedo"))
    speaker, para, started, skip_milton = None, 0, False, False
    label = re.compile(r"^([A-Z]{4,}): ")
    for b in blocks[1:]:
        first = b[0]
        m = label.match(first)
        if not started:
            if m and m.group(1) in ("ECHECRATES", "PHAEDO"):
                started = True
            else:
                stats["preamble_blocks"] = stats.get("preamble_blocks", 0) + 1
                continue
        if m and m.group(1) in ("ECHECRATES", "PHAEDO"):
            speaker = m.group(1).title()
            b = [first[m.end():]] + b[1:]
            stats["speaker_labels"] = stats.get("speaker_labels", 0) + 1
        if first.startswith("(Compare Milton, Comus:--") or skip_milton:
            # Jowett's two-block quotation from Milton's Comus, editorial
            skip_milton = not skip_milton
            stats["editorial_parentheticals"] = stats.get("editorial_parentheticals", 0) + (0 if skip_milton else 1)
            continue
        txt = _strip_editorial(clean_prose(b), _PHAEDO_EDITORIAL, stats)
        para += 1
        units.append(Unit({"para": para}, f"Phaedo, paragraph {para}", clean_prose(txt), "prose", None,
                          {"frame_speaker": speaker}))
    assert stats["editorial_parentheticals"] == 6, stats
    U.report(src, stats, warns)
    return units


# ---------------------------------------------------------------------------
# Schopenhauer (Saunders)
# ---------------------------------------------------------------------------
def _schopenhauer(src, which):
    stats, warns, units = {}, [], []
    blocks = paragraphs(U.body(U.load(src)))
    blocks = U.split_runs(U.split_footnote_blocks(blocks, stats))
    one = lambda b: " ".join(x.strip() for x in b)
    ii = next(i for i, b in enumerate(blocks) if one(b) == "INTRODUCTION.")
    work = "Counsels and Maxims" if which == "counsels" else "The Wisdom of Life"
    units.append(U.heading("Introduction", {"part": "Introduction"}, f"{work}, Introduction"))
    chapter, section, para = 0, 0, 0
    mode = "intro"
    sec_pref = re.compile(r"^SECTION (\d+)\.\s*")
    for b in blocks[ii + 1:]:
        t = one(b)
        mc = re.fullmatch(r"CHAPTER ([IVXL]+)[.,]", t)
        if mc:
            chapter, section, para, mode = U.roman(mc.group(1)), 0, 0, "chapter_title"
            continue
        if mode == "chapter_title":
            mode = "body"
            title = re.sub(r"--SECTION \d+\.$", "", t).rstrip(".")
            units.append(U.heading(U.tc(title) if title.isupper() else title, {"chapter": chapter},
                                   f"{work}, chapter {U.roman_str(chapter)}"))
            ms = re.search(r"--SECTION (\d+)\.$", t)
            if ms:
                section, para = int(ms.group(1)), 0
            continue
        if mode == "intro":
            if t == "THE WISDOM OF LIFE.":
                continue
            para += 1
            units.append(U.text_unit(b, {"part": "Introduction", "para": para}, f"{work}, Introduction", stats=stats))
            continue
        # wisdom of life: "_Section 1.--Reputation_." sub-headings in chapter IV
        mw = re.fullmatch(r"_Section (\d+)\.--(.+?)_\.?", t)
        if mw:
            section, para = int(mw.group(1)), 0
            units.append(U.heading(mw.group(2).strip(), {"chapter": chapter, "section": section},
                                   f"{work}, chapter {U.roman_str(chapter)}, section {section}"))
            continue
        # counsels: "SECTION 12." alone, or "SECTION 2. text..." opening a paragraph
        if len(b) == 1 and re.fullmatch(r"SECTION (\d+)\.", t):
            section, para = int(re.fullmatch(r"SECTION (\d+)\.", t).group(1)), 0
            continue
        ms = sec_pref.match(b[0])
        if ms:
            section, para = int(ms.group(1)), 0
            b = [b[0][ms.end():]] + b[1:]
            stats["section_prefixes"] = stats.get("section_prefixes", 0) + 1
        if U.mixed_indent(b):
            warns.append(f"mixed indent ch{chapter} s{section}: {b[0].strip()[:50]!r}")
        para += 1
        loc = {"chapter": chapter}
        if section:
            loc["section"] = section
        loc["para"] = para
        disp = f"{work}, chapter {U.roman_str(chapter)}" + (f", section {section}" if section else "")
        units.append(U.text_unit(b, loc, disp, stats=stats))
    U.report(src, stats, warns)
    return units


# ---------------------------------------------------------------------------
# Aristotle
# ---------------------------------------------------------------------------
_SIDE = re.compile(r"\*?\[Sidenote(?:\(\?\))?:?(.*?)\]", re.S)
_BARE_PAGE = re.compile(r"\[(\d{4})_?([ab])_?\]")
_CHAPTERS = {1: 13, 2: 9, 3: 12, 4: 9, 5: 11, 6: 13, 7: 14, 8: 14, 9: 12, 10: 9}  # standard chapter counts


def _side(content: str):
    """Interpret a sidenote -> (chapter|None, bekker|None, leftover text)."""
    c = content.strip().replace("\n", " ")
    keep = ""
    m = re.match(r"^((?:[IVXL]+\s+)?_?[\dIlo]{2,4}_?[abh]?_?)\s+(\S.*)$", c)
    if m and len(m.group(2)) > 15:
        c, keep = m.group(1), m.group(2)
    ch = pg = None
    if re.fullmatch(r"[IVXL]+", c):
        return U.roman(c), None, keep
    m = re.fullmatch(r"([IVXL]+)\s+(.+)", c)
    if m:
        ch, c = U.roman(m.group(1)), m.group(2)
    c2 = c.replace("_", "").replace(" ", "").replace("o", "0").replace("h", "b")
    m = re.fullmatch(r"(I{0,3})(\d{1,4})([ab]?)", c2)
    if m and m.group(3):
        digits = "1" * len(m.group(1)) + m.group(2)
        if len(digits) == 4 and 1094 <= int(digits) <= 1181:
            pg = digits + m.group(3)
    return ch, pg, keep


def _pkey(pg: str) -> int:
    return int(pg[:4]) * 2 + (1 if pg[4] == "b" else 0)


def _aristotle(src):
    stats, warns, units = {}, [], []
    text = U.body(U.load(src))
    a = text.index("\nARISTOTLE'S ETHICS\n")
    z = re.search(r"\nNOTES\n\n\nP 2, l\. 16", text).start()
    notes = text[z:]
    stats["translator_notes_blocks"] = sum(1 for b in paragraphs(notes) if re.match(r"P\.? ?\d+", b[0]))
    blocks = paragraphs(text[a:z])
    book, chapter, para, page = 0, 0, 0, None
    last_pg = 0
    ch_by_book: dict[int, int] = {}
    ill = 0
    for b in blocks:
        t = " ".join(x.strip() for x in b)
        if t == "ARISTOTLE'S ETHICS":
            continue
        mb = re.fullmatch(r"BOOK ([IVX]+)", t)
        if mb:
            if book:
                ch_by_book[book] = chapter
            book, chapter, para, page = U.roman(mb.group(1)), 1, 0, None
            units.append(U.heading(f"Book {mb.group(1)}", {"book": book}, f"Book {mb.group(1)}"))
            continue
        if re.fullmatch(r"\[Illustration:[^\]]*\]", t):
            ill += 1
            continue
        if re.fullmatch(r"[IVXL]+", t):  # standalone chapter numeral
            n = U.roman(t)
            if chapter < n <= _CHAPTERS.get(book, 0):
                chapter = n
            else:
                warns.append(f"book {book}: ignored standalone numeral {t} after chapter {chapter}")
            continue
        # --- process sidenotes inside the block text -----------------------------
        raw = "\n".join(b)
        events = []  # (position, chapter, page)
        def repl(m):
            ch, pg, keep = _side(m.group(1))
            events.append((m.start(), ch, pg))
            if not (ch or pg) and not keep:
                stats["sidenote_unparsed"] = stats.get("sidenote_unparsed", 0) + 1
            stats["sidenotes"] = stats.get("sidenotes", 0) + 1
            return keep
        cleaned = _SIDE.sub(repl, raw)
        for m in _BARE_PAGE.finditer(cleaned):
            events.append((m.start(), None, m.group(1) + m.group(2)))
            stats["bare_pages"] = stats.get("bare_pages", 0) + 1
        cleaned = _BARE_PAGE.sub("", cleaned)
        body_txt = cleaned
        if not body_txt.strip():
            # marker-only block still updates state
            for _, ch, pg in events:
                if ch and chapter < ch <= _CHAPTERS.get(book, 0):
                    chapter = ch
                if pg and _pkey(pg) >= last_pg:
                    page, last_pg = pg, _pkey(pg)
            continue
        # state at paragraph start: apply events located in the first ~12 characters
        start_events = [e for e in events if len(raw[:e[0]].strip()) < 4]
        for _, ch, pg in start_events:
            if ch:
                if chapter < ch <= _CHAPTERS.get(book, 0):
                    chapter = ch
                elif ch != chapter:
                    warns.append(f"book {book}: chapter marker {ch} after {chapter} ignored")
            if pg and _pkey(pg) >= last_pg:
                page, last_pg = pg, _pkey(pg)
        lines = body_txt.split("\n")
        if all(U.indent_of(l) >= 1 for l in lines if l.strip()):  # quoted lines are indented 1-2 spaces
            txt, kind = clean_verse(lines), "verse"
        else:
            txt, kind = clean_prose(lines), "prose"
        if U.mixed_indent([l for l in lines if l.strip()]):
            warns.append(f"mixed indent book {book}: {lines[0].strip()[:50]!r}")
        para += 1
        # The sidenote chapter numerals are too corrupted in this e-text to trust as a
        # citation (some missing, some OCR-garbled), so chapter is only a best-effort
        # estimate in meta; loc carries book + Bekker page (when a clean one was seen) + para.
        loc = {"book": book}
        if page:
            loc["bekker"] = page
        loc["para"] = para
        disp = f"Book {U.roman_str(book)}" + (f", Bekker {page}" if page else "")
        units.append(Unit(loc, disp, txt, kind, None, {"chapter_est": chapter}))
        # later events inside the paragraph update the running state
        for e in events:
            if e in start_events:
                continue
            _, ch, pg = e
            if ch and chapter < ch <= _CHAPTERS.get(book, 0):
                chapter = ch
            if pg and _pkey(pg) >= last_pg:
                page, last_pg = pg, _pkey(pg)
    ch_by_book[book] = chapter
    stats["illustration_lines"] = ill
    for bk, n in sorted(ch_by_book.items()):
        if n != _CHAPTERS[bk]:
            warns.append(f"book {bk}: detected {n} chapters, expected {_CHAPTERS[bk]}")
    U.report(src, stats, warns)
    return units
