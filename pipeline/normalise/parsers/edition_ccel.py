"""CCEL plain-text sources: Eckhart (Field), Teresa's Interior Castle (Stanbrook /
Zimmerman) and Way of Perfection (Peers).

CCEL text is cut into blocks by long rows of underscores. Every block is classified
by its first line; only blocks that are the author's text are kept. Removed:
CCEL header and footer, title pages, introductions, prefaces and translator's notes,
footnote blocks ("[12] ..."), indexes, the "References" list, the editor's chapter
summary lists, inline note markers "[12]", paragraph numbers are moved to meta.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import Unit, clean_prose, read_source  # noqa: E402

SOURCES = ["eckhart-sermons-field", "teresa-interior-castle", "teresa-way-of-perfection"]

_SEP = re.compile(r"^\s*_{20,}\s*$")
_NOTE = re.compile(r"\s*\[\d+\]")          # inline footnote marker
_ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50}


def roman_to_int(s: str) -> int:
    total = 0
    for i, ch in enumerate(s):
        v = _ROMAN[ch]
        total += -v if i + 1 < len(s) and _ROMAN[s[i + 1]] > v else v
    return total


def blocks(text: str) -> list[list[str]]:
    out, cur = [], []
    for line in text.split("\n"):
        if _SEP.match(line):
            out.append(cur)
            cur = []
        else:
            cur.append(line)
    out.append(cur)
    return out


def paras(lines: list[str]) -> list[str]:
    """Blank-line separated paragraphs, each joined into one line, markers removed."""
    res, cur = [], []
    for line in lines + [""]:
        if line.strip():
            cur.append(line.strip())
        elif cur:
            res.append(clean_prose(_NOTE.sub("", " ".join(cur))))
            cur = []
    return res


def _first(block):
    return next((l.strip() for l in block if l.strip()), "")


def _is_footnotes(block):
    return bool(re.match(r"^\[\d+\]", _first(block)))


# ---------------------------------------------------------------- Eckhart

def parse_eckhart(source):
    units = []
    for b in blocks(read_source(f"{source}/source.txt")):
        ls = [l for l in b if l.strip()]
        if ls and ls[0].strip() == "ECKHART'S SERMONS":
            ls = ls[1:]
            b = b[b.index(next(l for l in b if l.strip() == "ECKHART'S SERMONS")) + 1:]
        if not ls or not re.fullmatch(r"[IVX]+", ls[0].strip()):
            continue
        n = roman_to_int(ls[0].strip())
        title = clean_prose(_NOTE.sub("", ls[1]))
        units.append(Unit({"sermon": n}, f"Sermon {n}", title, kind="heading"))
        body = b[b.index(next(l for l in b if l.strip() == ls[1].strip())) + 1:]
        for k, p in enumerate(paras(body), 1):
            units.append(Unit({"sermon": n, "para": k}, f"Sermon {n}", p, meta={"title": title}))
    return units


# ---------------------------------------------------------------- Interior Castle

_MANSION = {w: i for i, w in enumerate("FIRST SECOND THIRD FOURTH FIFTH SIXTH SEVENTH".split(), 1)}
_SUMMARY = re.compile(r"^1\. [A-Z].* 2\. ")


def parse_castle(source):
    units = []
    mansion = None
    for b in blocks(read_source(f"{source}/source.txt")):
        first = _first(b)
        m = re.fullmatch(r"THE (\w+) MANSIONS", first)
        if m and m.group(1) in _MANSION and len([l for l in b if l.strip()]) == 1:
            mansion = _MANSION[m.group(1)]
            continue
        if first == "THE INTERIOR CASTLE" and any(l.strip() == "BY ST. TERESA" for l in b):
            ps = paras(b)
            start = next(i for i, p in enumerate(ps) if p.startswith("THIS TREATISE, STYLED")) + 1
            units.append(Unit({"mansion": 0}, "Prologue", "PROLOGUE", kind="heading"))
            for k, p in enumerate(ps[start:], 1):
                units.append(Unit({"mansion": 0, "chapter": 0, "para": k}, "Prologue", p))
            continue
        if first == "IHS" and mansion == 7:  # Teresa's closing address after the seventh mansions
            ps = [p for p in paras(b) if p != "IHS" and not p.startswith("HERE ENDS THE INTERIOR CASTLE")]
            units.append(Unit({"epilogue": 1}, "Epilogue", "EPILOGUE", kind="heading"))
            for k, p in enumerate(ps, 1):
                units.append(Unit({"epilogue": 1, "para": k}, "Epilogue", p))
            continue
        m = re.fullmatch(r"CHAPTER ([IVXL]+)\.|(ONLY CHAPTER)", first)
        if not m or mansion is None:
            continue
        chap = roman_to_int(m.group(1)) if m.group(1) else 1
        idx = next(i for i, l in enumerate(b) if l.strip())
        ps = paras(b[idx + 1:])
        argument, summary, rest = ps[0], ps[1], ps[2:]
        assert argument.isupper(), (mansion, chap, argument[:40])
        assert _SUMMARY.match(summary), (mansion, chap, summary[:40])
        # drop the colophon after the last chapter
        rest = [p for p in rest if not p.startswith("HERE ENDS THE INTERIOR CASTLE")]
        disp = f"Mansion {mansion}, chapter {chap}"
        units.append(Unit({"mansion": mansion, "chapter": chap}, disp, argument, kind="heading"))
        for k, p in enumerate(rest, 1):
            sec = None
            mm = re.match(r"^(\d+)\.\s+(.*)$", p)
            if mm:
                sec, p = int(mm.group(1)), mm.group(2)
            units.append(Unit({"mansion": mansion, "chapter": chap, "para": k}, disp, p,
                              meta={"section": sec} if sec else {}))
    return units


# ---------------------------------------------------------------- Way of Perfection

def parse_way(source):
    units = []
    for b in blocks(read_source(f"{source}/source.txt")):
        first = _first(b)
        if _is_footnotes(b):
            continue
        idx = next((i for i, l in enumerate(b) if l.strip()), None)
        if idx is None:
            continue
        m = re.fullmatch(r"CHAPTER (\d+)", first)
        if m:
            n = int(m.group(1))
            rest = b[idx + 1:]
            j = 0
            while not rest[j].strip():
                j += 1
            arg = []
            while rest[j].strip():
                arg.append(rest[j].strip())
                j += 1
            disp = f"Chapter {n}"
            units.append(Unit({"chapter": n}, disp, clean_prose(arg), kind="heading"))
            for k, p in enumerate(paras(rest[j:]), 1):
                units.append(Unit({"chapter": n, "para": k}, disp, p))
        elif re.fullmatch(r"PROTESTATIONS( \[\d+\])?", first):
            units.append(Unit({"chapter": 0}, "Protestation", "PROTESTATIONS", kind="heading"))
            for k, p in enumerate(paras(b[idx + 1:]), 1):
                units.append(Unit({"chapter": 0, "section": "protestation", "para": k}, "Protestation", p))
        elif first == "PROLOGUE":
            units.append(Unit({"chapter": 0}, "Prologue", "PROLOGUE", kind="heading"))
            ps = [p for p in paras(b[idx + 1:]) if p != "J. H. S."]
            for k, p in enumerate(ps, 1):
                units.append(Unit({"chapter": 0, "section": "prologue", "para": k}, "Prologue", p))
    return units


def parse(source):
    return {"eckhart-sermons-field": parse_eckhart,
            "teresa-interior-castle": parse_castle,
            "teresa-way-of-perfection": parse_way}[source](source)
