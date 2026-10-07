"""SuttaCentral (Bhikkhu Sujato, CC0): bilara JSON, one file per sutta.

Segment ids look like "mn1:2.3" (sutta mn1, section 2, segment 3) or, in the
Dhammapada, "dhp5:2" (verse 5, line 2). Segments ending ":0.x" are titles.

Units:
  - Dhammapada: one verse per unit, lines kept (kind="verse").
  - Nikayas (DN, MN, SN, AN): one section per unit (segments joined as prose).
    The translation JSON carries no verse/prose markup, so verse sections are
    joined as prose; this changes whitespace only.

Only the Dhammapada and the four Nikayas are in scope (Corpus-Policy section 2).
The folder also holds other Minor Collection books (Sutta Nipata, Udana,
Theragatha ...); they are skipped here and flagged for a decision.
"""

import json
import re

from common import SOURCE_DIR, Unit, clean_prose, clean_verse

SOURCES = ["suttacentral-sujato"]

WORKS = [("dn", "Long Discourses (Digha Nikaya)", "DN"),
         ("mn", "Middle Discourses (Majjhima Nikaya)", "MN"),
         ("sn", "Linked Discourses (Samyutta Nikaya)", "SN"),
         ("an", "Numbered Discourses (Anguttara Nikaya)", "AN")]

SEG = re.compile(r"^([a-z]+)([\d.\-]+):(\d+)(?:\.(\d+))?(?:\.(\d+))?$")
COLOPHON = re.compile(r"(are|is) complete\.?\s*$|^The chapter on .* is finished", re.I)


def natural_key(name: str):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name)]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dhammapada() -> list[Unit]:
    units, chapter = [], None
    files = sorted((SOURCE_DIR / SOURCES[0] / "kn" / "dhp").glob("*.json"), key=lambda p: natural_key(p.name))
    for path in files:
        verses: dict[int, list[str]] = {}
        for sid, text in load(path).items():
            m = SEG.match(sid)
            if not m or not text.strip():
                continue
            verse, major = int(m.group(2)), int(m.group(3))
            if major == 0:  # title segments: "Minor Collection", "Sayings ... 1–20", "1. Pairs"
                if re.match(r"^\d+\.\s", text.strip()):
                    chapter = text.strip()
                    units.append(Unit(loc={"chapter": chapter}, display=f"Dhammapada, {chapter}",
                                      text=chapter, kind="heading", work="Dhammapada"))
                continue
            if COLOPHON.search(text):
                continue
            verses.setdefault(verse, []).append(text)
        for v in sorted(verses):
            units.append(Unit(loc={"verse": v}, display=f"Dhammapada {v}",
                              text=clean_verse(verses[v]), kind="verse", work="Dhammapada",
                              meta={"chapter": chapter}))
    return units


def nikayas() -> list[Unit]:
    units = []
    for folder, work, abbr in WORKS:
        files = sorted((SOURCE_DIR / SOURCES[0] / folder).rglob("*.json"), key=lambda p: natural_key(str(p)))
        for path in files:
            sections: dict[int, list[str]] = {}
            titles = []
            sutta = None
            for sid, text in load(path).items():
                m = SEG.match(sid)
                if not m or not text.strip():
                    continue
                sutta = m.group(1).upper() + " " + m.group(2)
                major = int(m.group(3))
                if major == 0:
                    titles.append(text.strip())
                    continue
                sections.setdefault(major, []).append(text)
            if not sections:
                continue
            title = titles[-1] if titles else ""
            units.append(Unit(loc={"sutta": sutta}, display=f"{sutta} {title}".strip(),
                              text=title or sutta, kind="heading", work=work))
            for sec in sorted(sections):
                units.append(Unit(loc={"sutta": sutta, "section": sec},
                                  display=f"{sutta}, {title}" if title else sutta,
                                  text=clean_prose("".join(sections[sec])), work=work))
    return units


def parse(source):
    return dhammapada() + nikayas()
