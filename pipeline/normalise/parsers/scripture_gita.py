"""Bhagavad Gita: Sivananda (verse-numbered JSON) and Arnold's Song Celestial (verse paragraphs)."""

import json
import re
from common import Unit, clean_prose, clean_verse, gutenberg_body, paragraphs, read_source

SOURCES = ["gita-sivananda", "gita-arnold-song-celestial"]

ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9,
         "X": 10, "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15, "XVI": 16,
         "XVII": 17, "XVIII": 18}


def _sivananda(source):
    data = json.loads(read_source(f"{source}/source.json"))
    units = []
    for v in data["verses"]:
        units.append(Unit(
            loc={"chapter": v["chapter"], "verse": v["verse"]},
            display=f"Bhagavad Gita {v['chapter']}.{v['verse']}",
            text=clean_prose(v["translation"]),
            kind="prose",
        ))
    return units


FN = re.compile(r"\[FN#\w+\]")


def _arnold(source):
    body = gutenberg_body(read_source(f"{source}/source.txt"))
    lines = body.split("\n")
    # Contents list (chapter titles) sits before the first "CHAPTER I" heading.
    titles = {}
    for l in lines:
        m = re.match(r"^\s+([IVX]+)\. ([A-Z][A-Z -]+)$", l)
        if m and m.group(1) in ROMAN and m.group(1) not in titles:
            titles[m.group(1)] = m.group(2).strip()
    # Chapter bodies run from "  CHAPTER X" to its "HERE END..." colophon.
    heads = [(i, re.match(r"^\s*CHAPTER ([IVX]+)\s*$", l).group(1))
             for i, l in enumerate(lines) if re.match(r"^\s*CHAPTER ([IVX]+)\s*$", l)]
    assert [h[1] for h in heads] == list(ROMAN), "chapter headings"
    units = []
    for k, (start, rom) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        chunk = []
        for l in lines[start + 1:end]:
            if re.match(r"^\s*HERE END", l):      # colophon: drop it and the rest of chapter
                break
            chunk.append(FN.sub("", l))           # strip footnote markers (bodies are after the text)
        ch = ROMAN[rom]
        title = titles.get(rom, "")
        units.append(Unit(loc={"chapter": ch}, display=f"Bhagavad Gita (Arnold), Chapter {rom}",
                          text=f"CHAPTER {rom}. {title}".strip(". "), kind="heading"))
        for n, para in enumerate(paragraphs("\n".join(chunk)), 1):
            units.append(Unit(loc={"chapter": ch, "stanza": n},
                              display=f"Bhagavad Gita (Arnold), Chapter {rom}",
                              text=clean_verse(para), kind="verse"))
    return units


def parse(source):
    return _sivananda(source) if source == "gita-sivananda" else _arnold(source)
