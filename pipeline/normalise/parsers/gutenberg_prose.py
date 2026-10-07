"""Prose sources from Project Gutenberg with simple chapter structure.

as-a-man-thinketh-allen
  Kept: Allen's Foreword (author's own) + 7 chapters. Removed: Gutenberg
  boilerplate, title page, epigraph poem, contents, signature/address lines
  after the Foreword.

brother-lawrence
  Kept: the four Conversations (recorded by de Beaufort) and fifteen Letters.
  Removed: boilerplate, copyright line, "Editor's Preface" and the editor's
  "Introduction:" paragraphs for Conversations and Letters (Lightheart, 2002),
  the labels "First Conversation:" / "First Letter:" (kept in loc), the editor's
  closing line about Brother Lawrence's death, and the "Visit:" web line.

soul-of-the-indian-eastman
  Kept: Eastman's Foreword (author's own) and chapters I-VI. Removed:
  boilerplate, dedication, three epigraph poems, contents, the italic-style
  chapter synopsis lines under each chapter title, the foreword signature.

american-indian-stories-zitkala
  Kept: the nine stories/sketches and the essay "America's Indian Problem".
  Removed: boilerplate, title page, contents, the one footnote marker [1] and
  its body "[Footnote 1: ...]", the publisher's advertisement and Helen Keller's
  letter about "Old Indian Legends" after the last asterisk row. NOTE: in
  "America's Indian Problem" everything from "PREFATORY NOTE." on is quoted
  from a Bureau of Municipal Research report, not Zitkala-Sa's own prose; those
  units carry meta {"quoted_report": true}.

walden-thoreau  (two works in the folder)
  Kept: Walden (18 chapters) and "On the Duty of Civil Disobedience".
  Removed: boilerplate, title/contents, '* * * * *' section breaks. Verse
  quotations are kept as verse. The farm-account lists (indented, dotted
  leaders) are kept as kind="verse" with meta {"layout": "table"} so later
  stages can skip them.

chuang-tzu-giles
  Kept: Giles' translation, chapters I-XXXIII, with chapter titles as headings.
  Removed: boilerplate, title page and contents, Giles' Introduction (with its
  ~50 footnotes) and Canon Moore's "Note on the Philosophy", the per-chapter
  "_Argument_" summaries, every one-space-indented commentary block (Giles'
  translations of the Chinese commentators, interleaved in the text), bracketed
  editorial lines such as "[This chapter is supplementary to ch. v.]" and
  "[Spurious.]", one inline bracketed gloss in ch. xvii, two editor-supplied
  English verse quotations (Mrs. Alexander's "Burial of Moses"; a Hudibras
  couplet), a list of the five relationships that belongs to a commentary, the
  Index, Errata and publisher's list. Where a commentary block interrupted a
  sentence, the two text fragments are re-joined with a single space.
"""

from __future__ import annotations

import re

from common import Unit, clean_prose, clean_verse, paragraphs

from . import gutenberg_util as U

SOURCES = [
    "as-a-man-thinketh-allen",
    "brother-lawrence",
    "soul-of-the-indian-eastman",
    "american-indian-stories-zitkala",
    "walden-thoreau",
    "chuang-tzu-giles",
]

tc = U.tc


def parse(source: str) -> list[Unit]:
    return {
        "as-a-man-thinketh-allen": _allen,
        "brother-lawrence": _lawrence,
        "soul-of-the-indian-eastman": _eastman,
        "american-indian-stories-zitkala": _zitkala,
        "walden-thoreau": _walden,
        "chuang-tzu-giles": _chuang,
    }[source](source)


# ---------------------------------------------------------------------------
def _allen(src):
    stats, warns, units = {}, [], []
    blocks = paragraphs(U.body(U.load(src)))
    one = lambda b: " ".join(x.strip() for x in b)
    ci = next(i for i, b in enumerate(blocks) if one(b) == "CONTENTS")
    fi = next(i for i, b in enumerate(blocks) if one(b) == "FOREWORD")
    titles = [one(b) for b in blocks[ci + 1:fi]]
    assert len(titles) == 7, titles
    units.append(U.heading("Foreword", {"part": "Foreword"}, "Foreword"))
    mode, n, para = "foreword", 0, 0
    for b in blocks[fi + 1:]:
        t = one(b)
        if mode == "foreword":
            if t == "JAMES ALLEN.":
                mode = "sig"
                continue
            para += 1
            units.append(U.text_unit(b, {"part": "Foreword", "para": para}, "Foreword", stats=stats))
        elif mode == "sig":
            if t == "AS A MAN THINKETH":
                mode = "chapters"
            continue
        else:
            if len(b) == 1 and t in titles:
                n += 1
                assert t == titles[n - 1], (t, titles[n - 1])
                para = 0
                units.append(U.heading(tc(t), {"chapter": n}, f"Chapter {n}"))
                continue
            assert n, t[:40]
            if U.mixed_indent(b):
                warns.append(f"mixed indent ch{n}")
            para += 1
            units.append(U.text_unit(b, {"chapter": n, "para": para}, f"Chapter {n}", stats=stats))
    assert n == 7
    U.report(src, stats, warns)
    return units


# ---------------------------------------------------------------------------
_ORD = "First Second Third Fourth Fifth Sixth Seventh Eighth Ninth Tenth Eleventh Twelfth Thirteenth Fourteenth Fifteenth".split()


def _lawrence(src):
    stats, warns, units = {}, [], []
    blocks = paragraphs(U.body(U.load(src)))
    ci = next(i for i, b in enumerate(blocks) if " ".join(b).strip() == "CONVERSATIONS")
    label = re.compile(r"^(%s) (Conversation|Letter): " % "|".join(_ORD))
    kind, num, para, skipping = None, 0, 0, True
    dropped = 0
    for b in blocks[ci + 1:]:
        first = b[0].strip()
        if first == "Letters":
            skipping = True  # editor's introduction follows
            dropped += 1
            continue
        m = label.match(first)
        if m:
            skipping = False
            kind = m.group(2).lower()
            num = _ORD.index(m.group(1)) + 1
            para = 0
            b = [first[m.end():]] + b[1:]
            units.append(U.heading(f"{m.group(1)} {m.group(2)}", {kind: num}, f"{kind.title()} {num}"))
        elif skipping:
            dropped += 1
            continue
        txt = " ".join(b)
        if txt.startswith("Brother Lawrence died peacefully within days") or txt.startswith("------- Visit"):
            dropped += 1
            continue
        para += 1
        units.append(U.text_unit(b, {kind: num, "para": para}, f"{kind.title()} {num}", stats=stats))
    stats["editor_blocks_dropped"] = dropped
    U.report(src, stats, warns)
    assert sum(1 for u in units if u.kind == "heading" and "Conversation" in u.text) == 4
    assert sum(1 for u in units if u.kind == "heading" and "Letter" in u.text) == 15
    return units


# ---------------------------------------------------------------------------
def _eastman(src):
    stats, warns, units = {}, [], []
    blocks = paragraphs(U.body(U.load(src)))
    fi = next(i for i, b in enumerate(blocks) if b == ["FOREWORD"])
    units.append(U.heading("Foreword", {"part": "Foreword"}, "Foreword"))
    n, para, mode = 0, 0, "foreword"
    title_re = re.compile(r"^([IVX]+)\. ([A-Z][A-Z ,'’\-]+)$")
    for b in blocks[fi + 1:]:
        t = " ".join(x.strip() for x in b)
        if mode == "foreword":
            if t.startswith("CHARLES A. EASTMAN"):
                mode = "front"
                continue
            para += 1
            units.append(U.text_unit(b, {"part": "Foreword", "para": para}, "Foreword", stats=stats))
            continue
        m = title_re.match(b[0]) if len(b) == 1 and not b[0].startswith(" ") else None
        if m:
            n += 1
            assert U.roman(m.group(1)) == n
            mode, para = "chapter", 0
            units.append(U.heading(f"{m.group(1)}. {tc(m.group(2))}", {"chapter": n}, f"Chapter {m.group(1)}"))
            synopsis_next = True
            continue
        if mode == "front":
            continue  # contents lines
        if synopsis_next:
            synopsis_next = False
            if all(l.startswith("   ") for l in b):
                stats["synopsis_blocks"] = stats.get("synopsis_blocks", 0) + 1
                continue
        if U.mixed_indent(b):
            warns.append(f"mixed indent ch{n}")
        para += 1
        units.append(U.text_unit(b, {"chapter": n, "para": para}, f"Chapter {U.roman_str(n)}", stats=stats))
    assert n == 6
    U.report(src, stats, warns)
    return units


# ---------------------------------------------------------------------------
_ZPARTS = [
    "IMPRESSIONS OF AN INDIAN CHILDHOOD",
    "THE SCHOOL DAYS OF AN INDIAN GIRL",
    "AN INDIAN TEACHER AMONG INDIANS",
    "THE GREAT SPIRIT",
    "THE SOFT-HEARTED SIOUX",
    "THE TRIAL PATH",
    "A WARRIOR'S DAUGHTER",
    "A DREAM OF HER GRANDFATHER",
    "THE WIDESPREAD ENIGMA CONCERNING BLUE-STAR WOMAN",
    "AMERICA'S INDIAN PROBLEM",
]


def _zitkala(src):
    stats, warns, units = {}, [], []
    text = U.body(U.load(src))
    cut = text.index("_This Book should be in every home_")
    text = text[:cut]
    blocks = paragraphs(text)
    # drop any trailing asterisk row
    while blocks and U.is_stars(blocks[-1]):
        blocks.pop()
    blocks = U.split_footnote_blocks(blocks, stats)
    start = next(i for i, b in enumerate(blocks) if len(b) == 1 and b[0].strip() == _ZPARTS[0])
    part, ch, para, quoted = 0, 0, 0, False
    expect_title = False
    pname = lambda k: tc(_ZPARTS[k - 1]).replace("'S", "'s")
    for b in blocks[start:]:
        t = " ".join(x.strip() for x in b)
        if U.is_stars(b):
            continue
        if t in _ZPARTS and (part == 0 or t == _ZPARTS[part]):
            part = _ZPARTS.index(t) + 1
            ch, para, quoted = 0, 0, False
            units.append(U.heading(pname(part), {"part": part}, pname(part)))
            continue
        if part == 10 and t.isupper() and len(t) < 120:
            units.append(U.heading(t, {"part": part, "section": "quoted"}, pname(part)))
            if t.startswith("PREFATORY NOTE"):
                quoted = True
            continue
        if len(b) == 1 and re.fullmatch(r"[IVX]+\.", t):
            ch = U.roman(t)
            para = 0
            expect_title = True
            continue
        if expect_title:
            expect_title = False
            if t.isupper():
                units.append(U.heading(tc(t.rstrip(".")), {"part": part, "chapter": ch},
                                       f"{pname(part)}, chapter {U.roman_str(ch)}"))
                continue
        loc = {"part": part}
        if ch:
            loc["chapter"] = ch
        para += 1
        loc["para"] = para
        disp = pname(part) + (f", chapter {U.roman_str(ch)}" if ch else "")
        if U.mixed_indent(b):
            warns.append(f"mixed indent part{part}")
        units.append(U.text_unit(b, loc, disp, stats=stats, meta={"quoted_report": True} if quoted else None))
    assert part == 10
    U.report(src, stats, warns)
    return units


# ---------------------------------------------------------------------------
def _walden(src):
    stats, warns, units = {}, [], []
    blocks = paragraphs(U.body(U.load(src)))
    one = lambda b: " ".join(x.strip() for x in b)
    ci = next(i for i, b in enumerate(blocks) if one(b) == "Contents")
    wi = next(i for i, b in enumerate(blocks) if one(b) == "=WALDEN=")
    cd = next(i for i, b in enumerate(blocks) if one(b) == "=ON THE DUTY OF CIVIL DISOBEDIENCE=")
    titles = [one(b) for b in blocks[wi + 1:cd]]
    assert len(titles) == 18, titles
    start = next(i for i, b in enumerate(blocks) if i > cd and one(b) == "WALDEN")
    ch_i, para, work, cur = 0, 0, "walden", None
    meta_titles = {"COMPLEMENTAL VERSES", "The Pretensions of Poverty"}
    for b in blocks[start + 1:]:
        t = one(b)
        if U.is_stars(b):
            continue
        if work == "walden" and ch_i < 18 and t == titles[ch_i]:
            ch_i += 1
            cur, para = titles[ch_i - 1], 0
            units.append(U.heading(cur, {"chapter": cur, "chapter_no": ch_i}, f"Walden, {cur}", work="walden"))
            continue
        if work == "walden" and t == "ON THE DUTY OF CIVIL DISOBEDIENCE":
            work, para, cur = "civil-disobedience", 0, None
            units.append(U.heading("On the Duty of Civil Disobedience", {}, "Civil Disobedience", work=work))
            continue
        assert cur or work != "walden", f"text before first chapter: {t[:50]}"
        if t in meta_titles:
            units.append(U.heading(t, ({"chapter": cur} if cur else {}), f"Walden, {cur}", work=work))
            continue
        if U.mixed_indent(b):
            warns.append(f"mixed indent {cur}: {b[0].strip()[:40]}")
        para += 1
        loc = {"chapter": cur, "para": para} if work == "walden" else {"para": para}
        disp = f"Walden, {cur}" if work == "walden" else "Civil Disobedience"
        meta = None
        if U.all_indented(b, 2) and re.search(r"\.{5,}|\$ ?\d|^\s+-{5,}", "\n".join(b), re.M):
            meta = {"layout": "table"}
        u = U.text_unit(b, loc, disp, stats=stats, work=work, meta=meta)
        units.append(u)
    assert ch_i == 18, ch_i
    U.report(src, stats, warns)
    return units


# ---------------------------------------------------------------------------
_CHUANG_DROP_VERSE = (
    "And had he not high honour?--",
    "And the dark rock pines like nodding plumes",
    "_The Burial of Moses_",
    "Compounds for sins he feels inclined to",
)


def _chuang(src):
    stats, warns, units = {}, [], []
    text = U.body(U.load(src))
    blocks = paragraphs(text)
    start = next(i for i, b in enumerate(blocks)
                 if b == ["CHAPTER I."] and blocks[i + 1] == ["TRANSCENDENTAL BLISS."])
    end = next(i for i, b in enumerate(blocks) if b == ["_INDEX_"])
    ch, para = 0, 0
    pending: list[str] | None = None
    gap = False          # a commentary block was dropped since `pending` was started
    prev_dropped_gloss = False
    merges = []

    def flush():
        nonlocal pending, gap, para
        if pending is not None:
            para += 1
            txt = clean_prose(pending)
            txt, nb = re.subn(r"\s?\[[^\]]*\]", "", txt)
            stats["inline_brackets"] = stats.get("inline_brackets", 0) + nb
            units.append(Unit({"chapter": ch, "para": para}, f"Chapter {U.roman_str(ch)}", txt, "prose", None, {}))
        pending, gap = None, False

    i = start
    while i < end:
        b = blocks[i]
        t = " ".join(x.strip() for x in b)
        m = re.fullmatch(r"CHAPTER ([IVXL]+)\.", t)
        if m:
            flush()
            ch, para = U.roman(m.group(1)), 0
            title = " ".join(x.strip() for x in blocks[i + 1]).rstrip(".")
            units.append(U.heading(f"Chapter {m.group(1)}. {tc(title)}", {"chapter": ch}, f"Chapter {m.group(1)}"))
            i += 2
            prev_dropped_gloss = False
            continue
        if U.is_stars(b):
            flush()
            i += 1
            continue
        ind = U.indent_of(b[0])
        # commentary / argument block: every line indented exactly one space
        if all(U.indent_of(l) == 1 for l in b):
            stats["commentary_blocks"] = stats.get("commentary_blocks", 0) + 1
            if t.startswith("_Argument_"):
                stats["arguments"] = stats.get("arguments", 0) + 1
            gap = pending is not None
            prev_dropped_gloss = True
            i += 1
            continue
        if re.match(r"\[(This chapter|Spurious|Summary by|Illustration)", t) and t.endswith("]"):
            stats["bracket_notes"] = stats.get("bracket_notes", 0) + 1
            i += 1
            continue
        if U.all_indented(b, 2):
            if prev_dropped_gloss and re.match(r"\d\. ", t):
                stats["commentary_lists"] = stats.get("commentary_lists", 0) + 1
                i += 1
                continue
            if t.startswith(_CHUANG_DROP_VERSE):
                stats["editor_verse"] = stats.get("editor_verse", 0) + 1
                i += 1
                continue
            flush()
            para += 1
            meta = {"layout": "list"} if re.match(r"(Right|Relationship|Division|Emulation)\s", t) else {}
            units.append(Unit({"chapter": ch, "para": para}, f"Chapter {U.roman_str(ch)}", clean_verse(b), "verse", None, meta))
            prev_dropped_gloss = False
            i += 1
            continue
        if U.mixed_indent(b):
            warns.append(f"mixed indent ch{ch}: {t[:40]}")
        prev_dropped_gloss = False
        if pending is not None and gap and (b[0][:1].islower() or pending[-1].rstrip()[-1:] == "," or pending[-1].rstrip()[-1:].isalnum()):
            merges.append((pending[-1].strip()[-30:], b[0].strip()[:30]))
            pending = pending + b
            gap = False
        else:
            flush()
            pending = list(b)
        i += 1
    flush()
    stats["joined_across_commentary"] = len(merges)
    U.report(src, stats, warns)
    globals()["_LAST_MERGES"] = merges
    assert ch == 33
    return units
