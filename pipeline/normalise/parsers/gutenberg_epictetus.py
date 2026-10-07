"""Epictetus: Higginson's Enchiridion and Long's Selection from the Discourses.

epictetus-enchiridion (Higginson, Liberal Arts Press 1948 text)
  Kept: the 51 numbered sections (Roman numerals in the source) of the Enchiridion.
  Removed: Gutenberg header/footer, publisher title page, contents, Note on the
  Text, Salomon's Introduction, Selected Bibliography, the 11 footnote markers
  [1]..[11] and the footnote bodies (editor "Ed." notes and references), the
  Liberal Arts Press catalogue and Transcriber's Notes. Translator's own
  square-bracket insertions in the text (e.g. "[the habit of]") are kept.

epictetus-discourses-long (George Long, 1877)
  Kept: the selection from the Discourses (each starts with an upper-case title
  ending ".--") and Long's Encheiridion (sections I-LII).
  Removed: Gutenberg header/footer, title page, contents, Long's biographical
  note "Epictetus." (translator's introduction). One inline footnote ("[Footnote: Compare Encheiridion, 29.]") removed.
  Greek transliterations such as "[Greek: hormae]" are part of the translation
  and are kept.
"""

from __future__ import annotations

import re

from common import Unit, clean_prose, paragraphs

from . import gutenberg_util as U

SOURCES = ["epictetus-enchiridion", "epictetus-discourses-long"]


def parse(source: str) -> list[Unit]:
    return _enchiridion() if source == "epictetus-enchiridion" else _discourses()


def _enchiridion() -> list[Unit]:
    src = "epictetus-enchiridion"
    stats, warns, units = {}, [], []
    text = U.body(U.load(src))
    m = None
    for m in re.finditer(r"\n[ \t]+THE ENCHIRIDION[ \t]*\n", text):
        pass  # last occurrence is the real start of the work
    start = m.end()
    end = re.search(r"\n[ \t]+Footnotes[ \t]*\n", text).start()
    text = text[start:end]
    units.append(U.heading("The Enchiridion", {}, "The Enchiridion"))
    sec, para = 0, 0
    for b in paragraphs(text):
        one = b[0].strip()
        mm = re.fullmatch(r"([IVXL]+)(?:\[\d+\])?", one) if len(b) == 1 else None
        if mm:
            n = U.roman(mm.group(1))
            assert n == sec + 1, f"section order {mm.group(1)} after {sec}"
            sec, para = n, 0
            if re.search(r"\[\d+\]", one):
                stats["markers"] = stats.get("markers", 0) + 1
            continue
        assert sec, f"text before section I: {b[0][:40]}"
        if U.mixed_indent(b):
            warns.append(f"mixed indent in section {sec}")
        para += 1
        units.append(U.text_unit(b, {"section": sec, "para": para}, f"Enchiridion {sec}", stats=stats))
    stats["footnote_bodies"] = 11  # counted from the Footnotes list at the end of the file
    U.report(src, stats, warns)
    return units


def _discourses() -> list[Unit]:
    src = "epictetus-discourses-long"
    stats, warns, units = {}, [], []
    text = U.body(U.load(src))
    a = re.search(r"\nA SELECTION FROM THE DISCOURSES OF EPICTETUS\.\n", text).end()
    b_ = re.search(r"\nTHE ENCHEIRIDION,\s*\n\s*OR MANUAL\.\n", text)
    disc, ench = text[a:b_.start()], text[b_.end():]

    disc, nfn = re.subn(r"\[Footnote:[^\]]*\]", "", disc)  # one inline footnote (a cross-reference)
    stats['inline_footnotes'] = nfn

    # --- Discourses selection: pieces separated by a row of asterisks -------------
    pieces, cur = [], []
    for b in paragraphs(disc):
        if U.is_stars(b):
            pieces.append(cur)
            cur = []
        else:
            cur.append(b)
    pieces.append(cur)
    pieces = [p for p in pieces if p]
    for n, blocks in enumerate(pieces, 1):
        first = clean_prose(blocks[0])
        _m = re.search(r"\.--?(?=\S)", first)  # source has one ".-" typo
        title, sep, rest = (first[:_m.start() + 1], "--", first[_m.end():]) if _m else (first, "", "")
        t_chk = re.sub(r'\[Greek:[^\]]*\]', '', title)
        assert sep and t_chk.upper() == t_chk, f"selection {n}: no '.--' title: {first[:60]}"
        loc_d = f"Discourses selection {n}"
        units.append(U.heading(title, {"selection": n}, loc_d, work="discourses"))
        para = 0
        if rest.strip():
            para += 1
            units.append(Unit({"selection": n, "para": para}, loc_d, rest.strip(), "prose", "discourses"))
        for b in blocks[1:]:
            if U.mixed_indent(b):
                warns.append(f"mixed indent selection {n}")
            para += 1
            units.append(U.text_unit(b, {"selection": n, "para": para}, loc_d, stats=stats, work="discourses"))

    # --- Encheiridion ------------------------------------------------------------
    units.append(U.heading("The Encheiridion, or Manual", {}, "Encheiridion", work="encheiridion"))
    sec, para = 0, 0
    for b in paragraphs(ench):
        one = b[0].strip()
        mm = re.fullmatch(r"([IVXL]+)\.", one) if len(b) == 1 else None
        if mm:
            n = U.roman(mm.group(1))
            assert n == sec + 1, f"encheiridion order {mm.group(1)} after {sec}"
            sec, para = n, 0
            continue
        assert sec
        para += 1
        units.append(U.text_unit(b, {"section": sec, "para": para}, f"Encheiridion {sec}", stats=stats, work="encheiridion"))
    stats["selections"] = len(pieces)
    stats["encheiridion_sections"] = sec
    U.report(src, stats, warns)
    return units
