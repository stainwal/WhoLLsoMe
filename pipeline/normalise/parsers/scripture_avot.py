"""Pirkei Avot (Sefaria JSON): one unit per mishnah. Bracketed words are part of the translation."""

import json
import re
from common import Unit, clean_prose, read_source

SOURCES = ["pirkei-avot"]


def parse(source):
    data = json.loads(read_source(f"{source}/source.json"))
    units = []
    for ch, mishnayot in enumerate(data["text"], 1):
        for mi, text in enumerate(mishnayot, 1):
            # Sefaria stores a paragraph break inside one mishnah (6:11) as <br><br>;
            # that is markup, not translator text: treat it as a space.
            text = re.sub(r"(?:<br\s*/?>\s*)+", " ", text)
            units.append(Unit(
                loc={"chapter": ch, "mishnah": mi},
                display=f"Pirkei Avot {ch}:{mi}",
                text=clean_prose(text),
                kind="prose",
            ))
    return units
