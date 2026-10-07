"""Shared types and helpers for normalising sources (Corpus-Policy section 7, step 1).

Every source is turned into a list of *units*: the smallest piece of text that
has its own location (a verse, a paragraph, a stanza, a mishnah). Units are
written as JSON Lines to corpus/passages/normalised/<source>.jsonl.

Normalisation may REMOVE editorial apparatus (licence boilerplate, page numbers,
footnote markers and bodies, facing-page Latin, transcriber notes) but must
never change the author's or translator's wording, spelling or punctuation.
The only change allowed inside a unit's text is whitespace:
  - prose:  line-wrapped lines are joined with single spaces
  - verse:  one line per verse line, joined with "\n", indentation stripped
"""

from __future__ import annotations

import json
import re
import tomllib
import unicodedata
from dataclasses import dataclass, field, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "corpus" / "source"
OUT_DIR = ROOT / "corpus" / "passages" / "normalised"

SOURCES_CONFIG = ROOT / "pipeline" / "sources.toml"

KINDS = {"prose", "verse", "heading"}


def source_config() -> dict:
    """{folder: {"active": bool, "note": str}} from pipeline/sources.toml."""
    return tomllib.loads(SOURCES_CONFIG.read_text(encoding="utf-8"))["sources"]


def is_active(source: str) -> bool:
    """Unknown sources count as inactive, so a typo never lets a source in by accident."""
    return source_config().get(source, {}).get("active", False)  # headings give context; never extracted


@dataclass
class Unit:
    loc: dict            # ordered location fields, e.g. {"chapter": 2, "verse": 47}
    display: str         # human-readable location, e.g. "Chapter 2, verse 47"
    text: str
    kind: str = "prose"
    work: str | None = None  # set when one folder holds several works (Vivekananda, Nikayas)
    meta: dict = field(default_factory=dict)


_WS = re.compile(r"[ \t ]+")


def clean_prose(lines_or_text) -> str:
    """Join wrapped prose lines into one line; collapse runs of spaces."""
    text = lines_or_text if isinstance(lines_or_text, str) else " ".join(lines_or_text)
    text = unicodedata.normalize("NFC", text)
    return _WS.sub(" ", text.replace("\n", " ")).strip()


def clean_verse(lines) -> str:
    """Keep verse line breaks; strip indentation and trailing spaces."""
    if isinstance(lines, str):
        lines = lines.split("\n")
    out = [_WS.sub(" ", unicodedata.normalize("NFC", l)).strip() for l in lines]
    return "\n".join(l for l in out if l)


def paragraphs(text: str) -> list[list[str]]:
    """Split on blank lines; return each paragraph as its list of lines."""
    paras, cur = [], []
    for line in text.split("\n"):
        if line.strip():
            cur.append(line.rstrip())
        elif cur:
            paras.append(cur)
            cur = []
    if cur:
        paras.append(cur)
    return paras


def gutenberg_body(text: str) -> str:
    """Return the text between Project Gutenberg START and END markers, if present."""
    start = re.search(r"^\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG.*$", text, re.M)
    end = re.search(r"^\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG.*$", text, re.M)
    if start:
        text = text[start.end():end.start() if end else None]
    elif end:
        text = text[:end.start()]
    return text


def read_source(rel: str) -> str:
    raw = (SOURCE_DIR / rel).read_text(encoding="utf-8-sig")
    return raw.replace("\r\n", "\n").replace("\r", "\n")


def write_units(source: str, units: list[Unit]) -> dict:
    """Write units to JSONL, assigning stable ids. Returns summary stats."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{source}.jsonl"
    words = 0
    with path.open("w", encoding="utf-8") as f:
        for i, u in enumerate(units, 1):
            assert u.kind in KINDS, f"{source}: bad kind {u.kind}"
            assert u.text.strip(), f"{source}: empty unit at {u.display}"
            rec = {"uid": f"{source}:{i:06d}", "source": source, **asdict(u)}
            if not rec["meta"]:
                rec.pop("meta")
            if rec["work"] is None:
                rec.pop("work")
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if u.kind != "heading":
                words += len(u.text.split())
    return {"source": source, "units": len(units), "words": words, "path": str(path.relative_to(ROOT))}


def load_units(source: str) -> list[dict]:
    path = OUT_DIR / f"{source}.jsonl"
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


# ---- Verbatim check (Corpus-Policy section 4, rule 7) ----------------------

def squash(s: str) -> str:
    """Whitespace-insensitive form: the only difference the check tolerates."""
    return _WS.sub(" ", unicodedata.normalize("NFC", s).replace("\n", " ")).strip()


def verbatim_match(passage: str, units: list[dict], start_uid: str | None = None,
                   end_uid: str | None = None) -> dict:
    """Is `passage` an exact (whitespace-insensitive) substring of the source?

    Checks the claimed unit range first (joined with spaces), then the whole
    source. Returns where it matched, so a wrong location is caught too.
    """
    p = squash(passage)
    if not p:
        return {"ok": False, "reason": "empty"}
    body = [u for u in units if u["kind"] != "heading"]
    if start_uid:
        ids = [u["uid"] for u in body]
        if start_uid in ids and (end_uid or start_uid) in ids:
            a, b = ids.index(start_uid), ids.index(end_uid or start_uid)
            span = " ".join(squash(u["text"]) for u in body[a:b + 1])
            if p in span:
                return {"ok": True, "where": "claimed_range"}
    full = " ".join(squash(u["text"]) for u in body)
    if p in full:
        return {"ok": True, "where": "elsewhere_in_source", "note": "location claim wrong"}
    return {"ok": False, "reason": "not_found"}
