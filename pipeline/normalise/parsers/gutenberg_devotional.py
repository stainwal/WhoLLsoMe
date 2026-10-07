"""Devotional prose from Project Gutenberg.

augustine-confessions-pusey (E. B. Pusey translation)
  Kept: Books I-XIII (13 books), paragraph by paragraph; verse quotations (indented
  blocks) kept as verse. The closing "GRATIAS TIBI DOMINE" is kept as a heading.
  The source has no chapter numbers, so loc is {"book": n, "para": k}.
  Removed: Gutenberg boilerplate, title lines.

imitation-of-christ-benham (Rev. William Benham translation)
  Kept: Books I-IV, chapter titles as headings, the speaker labels ("The Voice of
  the Disciple" etc.) as headings, prayer headings as headings. The translation's
  paragraph numbers ("2. ", "3. " ...) are removed from the text and become loc
  "para" (an unnumbered block after a numbered one, e.g. an inset verse, is the
  same paragraph, "part" 2, 3...). Book IV opens with an untitled-number prologue ("A devout exhortation
  to the Holy Communion"), recorded as chapter 0.
  Removed: the old (1999) Project Gutenberg header and "Small Print" licence,
  the translator's Introductory Note, the scripture-reference footnote markers
  "(1)", "(2)" in the text and the footnote bodies at the end of chapters (lists
  of Bible references), the trailing "Project Gutenberg Etext" line.
"""

from __future__ import annotations

import re

from common import Unit, clean_prose, clean_verse, paragraphs

from . import gutenberg_util as U

SOURCES = ["augustine-confessions-pusey", "imitation-of-christ-benham"]


def parse(source: str) -> list[Unit]:
    return _augustine(source) if source.startswith("augustine") else _imitation(source)


def _augustine(src):
    stats, warns, units = {}, [], []
    text = U.body(U.load(src))
    blocks = paragraphs(text)
    start = next(i for i, b in enumerate(blocks) if b == ["BOOK I"])
    book, para = 0, 0
    for b in blocks[start:]:
        t = " ".join(x.strip() for x in b)
        m = re.fullmatch(r"BOOK ([IVX]+)", t)
        if m:
            book, para = U.roman(m.group(1)), 0
            assert book > 0
            units.append(U.heading(f"Book {m.group(1)}", {"book": book}, f"Book {m.group(1)}"))
            continue
        if t == "GRATIAS TIBI DOMINE":
            units.append(U.heading(t, {"book": book}, f"Book {U.roman_str(book)}, close"))
            continue
        if U.mixed_indent(b):
            warns.append(f"mixed indent book {book}")
        para += 1
        units.append(U.text_unit(b, {"book": book, "para": para}, f"Book {U.roman_str(book)}, paragraph {para}", stats=stats))
    assert book == 13, book
    U.report(src, stats, warns)
    return units


_BOOKS = {"FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4}
_SPEAKER = re.compile(r"^The Voice of (the Disciple|the Beloved|Christ)$")
_FN_ENTRY = re.compile(r"\((\d+)\)")


def _disp(book, chapter):
    return f"Book {U.roman_str(book)}, chapter {chapter}" if chapter else "Book IV, prologue"


def _imitation(src):
    stats, warns, units = {}, [], []
    text = U.load(src).replace("\t", "\t")
    text = text[text.index("THE FIRST BOOK"):]
    cut = text.rindex("Project Gutenberg Etext Imitation of Christ")
    blocks = paragraphs(text[:cut])
    book, chapter, para = 0, 0, 0
    cur_num, sub = 0, 0
    speaker = None
    pending: list[Unit] = []  # units of the current chapter (footnote markers get stripped at chapter end)

    def finish(fn_nums=None):
        nonlocal pending
        for u in pending:
            if fn_nums and u.kind != "heading":
                u.text, n = re.subn(r"\((?:%s)\)" % "|".join(map(str, sorted(fn_nums))), "", u.text)
                u.text = clean_prose(u.text) if u.kind == "prose" else u.text
                stats["markers"] = stats.get("markers", 0) + n
            units.append(u)
        pending = []

    expect_chapter_title = False
    expect_book_sub = False
    for b in blocks:
        t = " ".join(x.strip() for x in b)
        mb = re.fullmatch(r"THE (FIRST|SECOND|THIRD|FOURTH) BOOK", t)
        if mb:
            finish()
            book, chapter, para, speaker = _BOOKS[mb.group(1)], 0, 0, None
            cur_num, sub = 0, 0
            pending.append(U.heading(f"The {mb.group(1).title()} Book", {"book": book}, f"Book {U.roman_str(book)}"))
            expect_book_sub = True
            continue
        mc = re.fullmatch(r"CHAPTER ([IVXL]+)", t)
        if mc:
            finish()
            chapter, para, speaker = U.roman(mc.group(1)), 0, None
            cur_num, sub = 0, 0
            expect_chapter_title = True
            continue
        if expect_chapter_title:
            expect_chapter_title = False
            pending.append(U.heading(t, {"book": book, "chapter": chapter}, f"Book {U.roman_str(book)}, chapter {chapter}"))
            continue
        if re.match(r"\(\d+\) ", b[0]) and all(re.match(r"\(\d+\) ", x) or True for x in b):
            nums = {int(n) for n in _FN_ENTRY.findall(t)}
            stats["footnote_bodies"] = stats.get("footnote_bodies", 0) + len(nums)
            finish(nums)
            continue
        if expect_book_sub and t.isupper():
            expect_book_sub = False
            pending.append(U.heading(U.tc(t), {"book": book}, f"Book {U.roman_str(book)}"))
            continue
        expect_book_sub = False
        if book == 4 and chapter == 0 and not t.isupper() and para == 0 and speaker is None and not _SPEAKER.match(t) \
                and t == "A devout exhortation to the Holy Communion":
            pending.append(U.heading(t, {"book": book, "chapter": 0}, "Book IV, prologue"))
            continue
        if _SPEAKER.match(t):
            speaker = t
            pending.append(U.heading(t, {"book": book, "chapter": chapter}, _disp(book, chapter), meta={"speaker": t}))
            continue
        if t.isupper() and len(b) == 1:  # e.g. "A PRAYER FOR THE SPIRIT OF DEVOTION" (tab-indented in places)
            pending.append(U.heading(t, {"book": book, "chapter": chapter}, _disp(book, chapter)))
            continue
        # --- ordinary paragraph ---------------------------------------------------
        # loc "para" is the translation's own paragraph number; an unnumbered block after
        # a numbered one (verse quotation, speaker change) is a continuation: "part" 2, 3...
        mnum = re.match(r"(\d+)\. ", b[0])
        if mnum:
            num = int(mnum.group(1))
            if num < cur_num:
                warns.append(f"book {book} ch {chapter}: number {num} after {cur_num}")
            cur_num, sub = num, 1
            b = [b[0][mnum.end():]] + b[1:]
        elif cur_num == 0:
            cur_num, sub = 1, 1
        else:
            sub += 1
        meta = {"speaker": speaker} if speaker else {}
        if U.mixed_indent(b):
            warns.append(f"mixed indent book {book} ch {chapter}")
        loc = {"book": book, "chapter": chapter, "para": cur_num}
        if sub > 1:
            loc["part"] = sub
        u = U.text_unit(b, loc,
                        f"Book {U.roman_str(book)}, chapter {chapter}" if chapter else "Book IV, prologue",
                        strip_fn=False, meta=meta)
        pending.append(u)
    finish()
    left = sum(len(_FN_ENTRY.findall(u.text)) for u in units if u.kind != "heading")
    if left:
        warns.append(f"{left} '(n)' patterns remain in text")
    U.report(src, stats, warns)
    return units
