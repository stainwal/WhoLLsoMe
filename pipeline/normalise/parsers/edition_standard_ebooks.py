"""Standard Ebooks dumps: Emerson's Essays and Marcus Aurelius' Meditations (Long).

The source file is a concatenation of xhtml-to-text dumps ("===== file.xhtml =====").
In these dumps a blank line separates paragraphs, while a single newline only marks
where an inline element (italic, note reference, line wrap) sat; the text on both
sides of such a newline already carries its own spacing, so lines of one paragraph
are joined with "" (never with a space).

Removed: file markers, endnote reference numbers (Meditations: digit-only lines).
The dumps lose blockquote markup, so verse quotations arrive as one short paragraph
per line; runs of >= 2 short paragraphs are merged into one kind="verse" unit.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import Unit, clean_prose, clean_verse, read_source  # noqa: E402

SOURCES = ["emerson-essays", "meditations-long"]

SHORT = 70  # max length (chars) of a paragraph that can be a verse line


def _files(text):
    parts = re.split(r"^===== (.*?) =====\n", text, flags=re.M)
    return list(zip(parts[1::2], parts[2::2]))


def _paragraphs(body, drop_note_numbers=False):
    out, cur = [], []
    for line in body.split("\n") + [""]:
        if drop_note_numbers and re.fullmatch(r"\d+", line):
            continue  # endnote reference on its own line
        if line.strip() == "":
            if cur:
                out.append(clean_prose("".join(cur)))
                cur = []
        else:
            cur.append(line)
    return [p for p in out if p]


def _runs(paras, split_before=()):
    """Group paragraphs into ('prose', text) / ('verse', [lines]) items.

    Runs of >= 2 consecutive short paragraphs become verse; a paragraph listed in
    split_before starts a new verse unit (speaker labels in a dialogue)."""
    items, run = [], []

    def flush():
        nonlocal run
        if len(run) >= 2:
            chunk = []
            for line in run:
                if line in split_before and chunk:
                    items.append(("verse", chunk))
                    chunk = []
                chunk.append(line)
            items.append(("verse", chunk))
        else:
            items.extend(("prose", p) for p in run)
        run = []

    for p in paras:
        if len(p) <= SHORT:
            run.append(p)
        else:
            flush()
            items.append(("prose", p))
    flush()
    return items


# ------------------------------------------------------------------ Emerson

# Epigraph pieces end after an attribution line; Self-Reliance opens with a Latin motto.
_ATTRIB = {"Muhammad", "Koran", "Ben Jonson", "Henry More",
           "Epilogue to Beaumont and Fletcher’s Honest Man’s Fortune", "Ne te quaesiveris extra."}
_SPEAKERS = {"Valerius", "Sophocles", "Dorigen", "Martius", "Juletta", "Master"}


def parse_emerson(source):
    units = []
    for _, body in _files(read_source(f"{source}/source.txt")):
        ps = _paragraphs(body)
        title, ps = ps[0], ps[1:]
        units.append(Unit({"essay": title}, title, title, kind="heading"))
        if len(ps[0]) > SHORT and len(ps[1]) <= SHORT:  # subtitle line (New England Reformers)
            units.append(Unit({"essay": title}, title, ps[0], kind="heading"))
            ps = ps[1:]
        n = 0
        while n < len(ps) and len(ps[n]) <= SHORT:
            n += 1
        epigraph, ps = ps[:n], ps[n:]
        piece, j = [], 0
        for line in epigraph + [None]:
            if line is not None:
                piece.append(line)
            if piece and (line is None or line in _ATTRIB):
                j += 1
                units.append(Unit({"essay": title, "epigraph": j}, title, clean_verse(piece), kind="verse"))
                piece = []
        k = 0
        for kind, content in _runs(ps, split_before=_SPEAKERS if title == "Heroism" else ()):
            k += 1
            text = clean_verse(content) if kind == "verse" else content
            units.append(Unit({"essay": title, "para": k}, title, text, kind=kind))
    return units


# ------------------------------------------------------------------ Meditations

_ROMAN = {"I": 1, "V": 5, "X": 10}


def _roman(s):
    t = 0
    for i, c in enumerate(s):
        v = _ROMAN[c]
        t += -v if i + 1 < len(s) and _ROMAN[s[i + 1]] > v else v
    return t


def parse_meditations(source):
    units = []
    books = []
    for name, body in _files(read_source(f"{source}/source.txt")):
        books.append((int(re.search(r"\d+", name).group()), body))
    for n, body in sorted(books):
        ps = _paragraphs(body, drop_note_numbers=True)
        assert ps[0] == "Book" and _roman(ps[1]) == n, (n, ps[:2])
        units.append(Unit({"book": n}, f"Meditations {n}", f"Book {ps[1]}", kind="heading"))
        k = 0
        for kind, content in _runs(ps[2:]):
            k += 1
            text = clean_verse(content) if kind == "verse" else content
            units.append(Unit({"book": n, "para": k}, f"Meditations {n}, paragraph {k}", text, kind=kind))
    return units


def parse(source):
    return parse_emerson(source) if source == "emerson-essays" else parse_meditations(source)
