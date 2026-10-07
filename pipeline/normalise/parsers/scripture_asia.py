"""The Light of Asia (Arnold, Gutenberg #8920): eight books of blank verse.

Unit = one blank-line-separated verse paragraph; each unit's loc is its book and
paragraph number. Indentation (Arnold's paragraph indents) is stripped.
"""

import re
from common import Unit, clean_verse, gutenberg_body, paragraphs, read_source

SOURCES = ["light-of-asia-arnold"]

ORD = ["First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth"]


def parse(source):
    text = gutenberg_body(read_source(f"{source}/source.txt"))
    lines = text.split("\n")
    heads = [(i, ORD.index(m.group(1).title())) for i, l in enumerate(lines)
             if (m := re.match(r"^Book [Tt]he (\w+)\s*$", l))]
    assert [h[1] for h in heads] == list(range(8)), heads
    units = []
    for k, (start, idx) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        body = lines[start + 1:end]
        # drop the closing "The End" colophon of Book Eight
        body = [l for l in body if l.strip() != "The End"
                and not re.match(r"^End of (the )?Project Gutenberg", l.strip())]
        title = f"Book the {ORD[idx]}"
        units.append(Unit(loc={"book": idx + 1}, display=f"The Light of Asia, {title}", text=title, kind="heading"))
        for n, para in enumerate(paragraphs("\n".join(body)), 1):
            units.append(Unit(loc={"book": idx + 1, "stanza": n},
                              display=f"The Light of Asia, {title}",
                              text=clean_verse(para), kind="verse"))
    return units
