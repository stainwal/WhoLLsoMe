"""Japji (Macauliffe 1900, OCR text): Mul Mantra, pauris I-XXXVIII, closing Slok.

Dropped: the SOURCE header block and Macauliffe's introduction. The source's line breaks
are print-column wraps (not reliably verse lines), so each pauri is joined into one prose
unit. Two stray footnote-marker digits left by the OCR at line ends are removed.
OCR slips in the text itself (e.g. "Te is not established") are left exactly as they are.
"""

import re
from common import Unit, clean_prose, read_source

SOURCES = ["japji-macauliffe"]

PAURI = re.compile(r"^([IVXL]+)\.$")
STRAY_NOTE_NO = re.compile(r"(?<=[?.!,;:])\s+\d{1,2}$")


def _roman(s):
    vals = {"I": 1, "V": 5, "X": 10, "L": 50}
    t = 0
    for i, c in enumerate(s):
        t += -vals[c] if i + 1 < len(s) and vals[s[i + 1]] > vals[c] else vals[c]
    return t


def parse(source):
    lines = read_source(f"{source}/source.txt").split("\n")
    first = next(i for i, l in enumerate(lines) if l.startswith("There is but one God"))
    blocks, cur, label = [], [], "Mul Mantra"   # (label, lines)
    for l in lines[first:]:
        s = l.strip()
        m = PAURI.match(s)
        if m or s == "SLOK.":
            blocks.append((label, cur))
            label, cur = (m.group(1) if m else "Slok"), []
        elif s:
            cur.append(STRAY_NOTE_NO.sub("", s))
    blocks.append((label, cur))
    units = []
    for label, body in blocks:
        if label == "Mul Mantra":
            loc, disp = {"section": "Mul Mantra"}, "Japji, Mul Mantra"
        elif label == "Slok":
            loc, disp = {"section": "Slok"}, "Japji, Slok"
        else:
            n = _roman(label)
            loc, disp = {"pauri": n}, f"Japji, Pauri {label}"
        units.append(Unit(loc=loc, display=disp, text=disp.split(", ")[1], kind="heading"))
        units.append(Unit(loc=loc, display=disp, text=clean_prose(body), kind="prose"))
    return units
