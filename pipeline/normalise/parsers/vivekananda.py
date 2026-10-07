"""Vivekananda: 14 originally-English works, text extracted from the Complete Works PDF.

The PDF text has no blank lines between paragraphs (blank lines mark page
breaks, often mid-sentence) and no page numbers. So:
  - Paragraph breaks are inferred: the previous line ends a sentence AND is
    short (well under the ~80-character full line). This only affects where
    units split, never the words; the verbatim check ignores unit boundaries.
  - Titles are taken from the table of contents at the top of each file, plus
    any line directly followed by "(Delivered ...)".
  - Bracketed extractor notes "[...]" are dropped.
english-poems.txt is verse: one unit per poem, line breaks kept.
"""

import re

from common import SOURCE_DIR, Unit, clean_prose, clean_verse

SOURCES = ["vivekananda"]

WORKS = {
    "chicago-addresses": "Addresses at the Parliament of Religions",
    "karma-yoga": "Karma-Yoga",
    "raja-yoga": "Raja-Yoga",
    "jnana-yoga": "Jnana-Yoga",
    "bhakti-yoga": "Bhakti-Yoga",
    "para-bhakti": "Para-Bhakti or Supreme Devotion",
    "practical-vedanta": "Practical Vedanta and other lectures",
    "inspired-talks": "Inspired Talks",
    "vol2-lectures": "Lectures (Complete Works, Vol. II)",
    "vol3-lectures": "Lectures (Complete Works, Vol. III)",
    "colombo-to-almora": "Lectures from Colombo to Almora",
    "addresses-on-bhakti-yoga": "Addresses on Bhakti-Yoga",
    "vol4-lectures": "Lectures (Complete Works, Vol. IV)",
    "english-poems": "Poems",
}

END_PUNCT = re.compile(r"[.!?:;\"”’)\]]\s*$")
SHORT = 68  # a line shorter than this that ends a sentence closes a paragraph


def is_note(line: str) -> bool:
    s = line.strip()
    return s.startswith("[") and s.endswith("]")


def title_case(s: str) -> bool:
    """Most longer words capitalised, as in a title; wrapped prose lines fail this."""
    words = [w for w in re.findall(r"[A-Za-z][\w'’-]*", s) if len(w) > 3]
    return bool(words) and sum(w[0].isupper() for w in words) / len(words) >= 0.7


def toc_titles(lines: list[str]) -> tuple[set[str], int]:
    """Leading run of short, unpunctuated lines = work title + table of contents."""
    titles, i = set(), 0
    while i < len(lines):
        s = lines[i].strip()
        if not s or is_note(s):
            i += 1
            continue
        if s in titles and len(titles) > 1:
            break  # first repeat of a contents entry = start of the body
        if len(s) <= 75 and not s.startswith("(") and not re.search(r"[.,;!”’\"]\s*$", s) and title_case(s):
            titles.add(s)
            i += 1
            continue
        break
    return titles, i


def parse_prose(stem: str, raw: str) -> list[Unit]:
    work = WORKS[stem]
    lines = [l for l in raw.split("\n")[1:]]  # line 0 is the extractor's note
    titles, _ = toc_titles(lines)
    file_title = next((l.strip() for l in lines if l.strip() and not is_note(l)), None)
    for i, l in enumerate(lines[:-1]):
        if lines[i + 1].strip().startswith("(Delivered") and title_case(l):
            titles.add(l.strip())
    units, para, lecture, just_titled, open_paren = [], [], None, False, False

    def flush():
        nonlocal para
        if para:
            n = sum(1 for u in units if u.loc.get("lecture") == lecture and u.kind == "prose") + 1
            units.append(Unit(loc={"file": stem, "lecture": lecture, "para": n},
                              display=f"{work}: {lecture}" if lecture else work,
                              text=clean_prose(para), work=work))
            para = []

    for line in lines:
        s = line.strip()
        if not s or is_note(s):
            continue  # blank lines are page breaks, not paragraph breaks
        if s in titles and len(s) <= 75:
            flush()
            if not (s == file_title and s.lower()[:12] == work.lower()[:12]):
                lecture = s  # the file's own title line is the work, not a lecture
            units.append(Unit(loc={"file": stem, "title": s}, display=s, text=s, kind="heading", work=work))
            just_titled = True
            continue
        if open_paren:  # continuation of a "(Delivered ..." line
            units[-1].text += " " + s
            open_paren = ")" not in s
            continue
        if just_titled and (s.startswith("(") or re.match(r"^(At|Delivered|Given|A lecture|Lecture) ", s)) \
                and len(s) <= 90 and not END_PUNCT.search(s.rstrip(")")):
            units.append(Unit(loc={"file": stem, "subtitle": s}, display=s, text=s, kind="heading", work=work))
            open_paren = s.startswith("(") and ")" not in s
            continue
        just_titled = False
        para.append(s)
        if END_PUNCT.search(s) and len(s) < SHORT:
            flush()
    flush()
    return units


def parse_poems(raw: str) -> list[Unit]:
    work = WORKS["english-poems"]
    lines = raw.split("\n")[1:]
    titles, start = toc_titles(lines)
    units, poem, title = [], [], None

    def flush():
        nonlocal poem
        if poem and title:
            units.append(Unit(loc={"file": "english-poems", "poem": title}, display=f"Poem: {title}",
                              text=clean_verse(poem), kind="verse", work=work))
        poem = []

    for line in lines[start:]:
        s = line.strip()
        if not s or is_note(s):
            continue
        if s in titles:
            flush()
            title = s
            units.append(Unit(loc={"file": "english-poems", "title": s}, display=s, text=s, kind="heading", work=work))
            continue
        poem.append(s)
    flush()
    return units


def parse(source):
    units = []
    for stem in WORKS:
        raw = (SOURCE_DIR / source / f"{stem}.txt").read_text(encoding="utf-8").replace("\r\n", "\n")
        units += parse_poems(raw) if stem == "english-poems" else parse_prose(stem, raw)
    return units
