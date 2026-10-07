"""Upanishads (Paramananda): Isa, Katha, Kena. Translation only.

Layout of the source: for every numbered verse (I, II, ...) the first paragraph is
Paramananda's translation; the paragraphs that follow it, up to the next numeral,
are his commentary and are dropped. Peace Chants are the paragraph(s) up to and
including the "OM! PEACE!" line. Introductions, blurbs and the closing notes after
"Here ends this Upanishad" are dropped.

The file is Latin-1, not UTF-8 (its only accented character is in a dropped introduction).
"""

import re
from common import SOURCE_DIR, Unit, clean_prose

SOURCES = ["upanishads-paramananda"]

ROMAN = re.compile(r"^[IVXL]+$")
PART = re.compile(r"^Part (first|second|third|fourth|fifth|sixth)$", re.I)
PARTS = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6}
UPAN = re.compile(r"^(Isa|Katha|Kena)-Upanishad$", re.I)


def _roman(s):
    vals = {"I": 1, "V": 5, "X": 10, "L": 50}
    total = 0
    for i, ch in enumerate(s):
        v = vals[ch]
        total += -v if i + 1 < len(s) and vals[s[i + 1]] > v else v
    return total


def _read():
    raw = (SOURCE_DIR / "upanishads-paramananda" / "source.txt").read_bytes()
    return raw.decode("latin-1").replace("\r\n", "\n").replace("\r", "\n").split("\n")


def parse(source):
    lines = _read()
    # translation proper runs from the Isa Peace Chant to the end of Kena (before PG licence)
    start = next(i for i, l in enumerate(lines) if l.strip() == "Peace Chant")
    end = next((i for i, l in enumerate(lines) if l.startswith("*** END OF")), len(lines))
    # sections: (kind, label, [lines])
    sections, cur = [], None
    upan, part = "Isa", None
    for i in range(start, end):
        s = lines[i].strip()
        if UPAN.match(s):
            upan, part, cur = s.split("-")[0].title(), None, None
            continue
        if s.upper() == "KENA-UPANISHAD":
            upan, part, cur = "Kena", None, None
            continue
        m = PART.match(s)
        if m:
            part, cur = PARTS[m.group(1).lower()], None
            sections.append(("part", (upan, part), None))
            continue
        if s.lower() == "peace chant":
            cur = ["chant", (upan, part), []]
            sections.append(cur)
            continue
        if ROMAN.match(s):
            cur = ["verse", (upan, part, _roman(s)), []]
            sections.append(cur)
            continue
        if s.lower().startswith("here ends this upanishad"):
            cur = None                          # closing notes follow: drop
            continue
        if cur is not None:
            cur[2].append(lines[i])
    units = []
    for kind, key, body in sections:
        if kind == "part":
            upan, part = key
            units.append(Unit(loc={"upanishad": upan, "part": part}, display=f"{upan} Upanishad, Part {part}",
                              text=f"{upan} Upanishad, Part {part}", kind="heading"))
            continue
        paras, c = [], []
        for l in body:
            if l.strip():
                c.append(l.strip())
            elif c:
                paras.append(c)
                c = []
        if c:
            paras.append(c)
        if not paras:
            continue
        if kind == "chant":
            upan, part = key
            # translation = first paragraph, plus the "OM! PEACE!" paragraph that follows
            take = [paras[0]]
            if len(paras) > 1 and paras[1][0].upper().startswith("OM!"):
                take.append(paras[1])
            # part is None for the opening chant, 6 (Katha) for the closing one
            position = "opening" if part is None else "closing"
            units.append(Unit(loc={"upanishad": upan, "section": "Peace Chant", "position": position},
                              display=f"{upan} Upanishad, Peace Chant ({position})",
                              text=clean_prose([" ".join(p) for p in take]), kind="prose"))
            continue
        upan, part, v = key
        loc = {"upanishad": upan, **({"part": part} if part else {}), "verse": v}
        disp = f"{upan} Upanishad " + (f"{part}.{v}" if part else str(v))
        units.append(Unit(loc=loc, display=disp, text=clean_prose(paras[0]), kind="prose"))
        # paras[1:] are Paramananda's commentary: dropped
    return units
