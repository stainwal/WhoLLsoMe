"""World English Bible (with deuterocanon): one unit per verse.

Source lines look like "GEN 1:1 In the beginning, ..." (USFM book code,
chapter:verse, text). The text after the reference is kept exactly.
"""

import re
from common import Unit, clean_prose, read_source

SOURCES = ["bible-web"]

# USFM code -> English book name, in source order (kept as the source orders them).
BOOKS = {
    "GEN": "Genesis", "EXO": "Exodus", "LEV": "Leviticus", "NUM": "Numbers",
    "DEU": "Deuteronomy", "JOS": "Joshua", "JDG": "Judges", "RUT": "Ruth",
    "1SA": "1 Samuel", "2SA": "2 Samuel", "1KI": "1 Kings", "2KI": "2 Kings",
    "1CH": "1 Chronicles", "2CH": "2 Chronicles", "EZR": "Ezra", "NEH": "Nehemiah",
    "EST": "Esther", "JOB": "Job", "PSA": "Psalms", "PRO": "Proverbs",
    "ECC": "Ecclesiastes", "SNG": "Song of Solomon", "ISA": "Isaiah",
    "JER": "Jeremiah", "LAM": "Lamentations", "EZK": "Ezekiel", "DAN": "Daniel",
    "HOS": "Hosea", "JOL": "Joel", "AMO": "Amos", "OBA": "Obadiah", "JON": "Jonah",
    "MIC": "Micah", "NAM": "Nahum", "HAB": "Habakkuk", "ZEP": "Zephaniah",
    "HAG": "Haggai", "ZEC": "Zechariah", "MAL": "Malachi",
    # Deuterocanon / apocrypha
    "TOB": "Tobit", "JDT": "Judith", "ESG": "Esther (Greek)", "WIS": "Wisdom of Solomon",
    "SIR": "Sirach", "BAR": "Baruch", "LJE": "Letter of Jeremiah",
    "S3Y": "Song of the Three Young Men", "SUS": "Susanna", "BEL": "Bel and the Dragon",
    "1MA": "1 Maccabees", "2MA": "2 Maccabees", "1ES": "1 Esdras",
    "MAN": "Prayer of Manasseh", "PS2": "Psalm 151", "3MA": "3 Maccabees",
    "2ES": "2 Esdras", "4MA": "4 Maccabees",
    # New Testament
    "MAT": "Matthew", "MRK": "Mark", "LUK": "Luke", "JHN": "John", "ACT": "Acts",
    "ROM": "Romans", "1CO": "1 Corinthians", "2CO": "2 Corinthians", "GAL": "Galatians",
    "EPH": "Ephesians", "PHP": "Philippians", "COL": "Colossians",
    "1TH": "1 Thessalonians", "2TH": "2 Thessalonians", "1TI": "1 Timothy",
    "2TI": "2 Timothy", "TIT": "Titus", "PHM": "Philemon", "HEB": "Hebrews",
    "JAS": "James", "1PE": "1 Peter", "2PE": "2 Peter", "1JN": "1 John",
    "2JN": "2 John", "3JN": "3 John", "JUD": "Jude", "REV": "Revelation",
}

LINE = re.compile(r"^([1-4A-Z][A-Z0-9]{2}) (\d+):(\d+) (.+)$")


def _display(code: str, name: str, ch: int, v: int) -> str:
    if code == "PSA":
        return f"Psalm {ch}:{v}"
    if code == "PS2":                       # Psalm 151 is a one-chapter book
        return f"Psalm 151:{v}" if ch == 1 else f"Psalm {ch}:{v}"
    return f"{name} {ch}:{v}"


def parse(source: str) -> list[Unit]:
    units = []
    for n, line in enumerate(read_source(f"{source}/source.txt").split("\n"), 1):
        if not line.strip():
            continue
        m = LINE.match(line)
        if not m or m.group(1) not in BOOKS:
            raise ValueError(f"{source}: unexpected line {n}: {line[:60]!r}")
        code, ch, v, text = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4)
        name = BOOKS[code]
        units.append(Unit(
            loc={"book": name, "chapter": ch, "verse": v},
            display=_display(code, name, ch, v),
            text=clean_prose(text),
            kind="prose",
            meta={"usfm": code},
        ))
    return units
