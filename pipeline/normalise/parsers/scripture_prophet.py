"""The Prophet (Gibran, Gutenberg #58585): 27 sections, one unit per paragraph.

The Gutenberg text has no section titles inline; sections are separated by a doubled
"***** *****" rule (or two "*****" lines) and are named from the contents list, in
order ("The Farewell" is split off "On Death" at its page-92 marker). A single "*****" is a scene break inside a section and is dropped.
Removed: page-number markers like {7}, the stray leading "|", [Illustration: ...]
lines, and the underscores that mark italics in the plain-text edition.
"""

import re
from common import Unit, clean_prose, gutenberg_body, paragraphs, read_source

SOURCES = ["prophet-gibran"]

PAGE = re.compile(r"\{\d+\}")
RULE = re.compile(r"^\*+(?:\s+\*+)*$")


def parse(source):
    text = gutenberg_body(read_source(f"{source}/source.txt"))
    text = re.sub(r"^End of the Project Gutenberg.*$", "", text, flags=re.M)
    # contents list -> ordered section titles
    contents = re.search(r"^CONTENTS\s*$(.*?)^THE PROPHET\s*$", text, re.M | re.S | re.I)
    titles = [re.sub(r"\.{2,}\s*\d+\s*$", "", l).strip() for l in contents.group(1).split("\n") if l.strip()]
    body = text[contents.end():]
    # "The Farewell" (print p. 92) is divided from "On Death" only by a page marker in
    # the middle of a paragraph; start a new section there.
    marker = "\n{92}And now it was evening."
    assert body.count(marker) == 1
    body = body.replace(marker, "\n\n***** *****\n\nAnd now it was evening.")
    body = PAGE.sub("", body)
    body = re.sub(r"^\[Illustration:[^\]]*\]\s*$", "", body, flags=re.M)
    body = re.sub(r"^\|", "", body, flags=re.M)
    body = body.replace("_", "")                   # italic markers of the plain-text edition
    # walk paragraphs, splitting sections on two consecutive rules
    sections, cur, prev_rule = [[]], None, False
    for para in paragraphs(body):
        joined = " ".join(p.strip() for p in para)
        if RULE.match(joined):
            double = len(re.findall(r"\*+", joined)) > 1
            if double or prev_rule:
                if sections[-1]:
                    sections.append([])
                prev_rule = False
            else:
                prev_rule = True
            continue
        prev_rule = False
        sections[-1].append(para)
    sections = [s for s in sections if s]
    assert len(sections) == len(titles), (len(sections), len(titles))
    units = []
    for title, paras in zip(titles, sections):
        units.append(Unit(loc={"section": title}, display=title, text=title, kind="heading"))
        for n, para in enumerate(paras, 1):
            units.append(Unit(loc={"section": title, "para": n}, display=f"The Prophet, {title}",
                              text=clean_prose(para), kind="prose"))
    return units
