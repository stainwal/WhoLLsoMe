"""Load the corpus into Supabase (Day 16, 12 Oct 2026).

    .venv/bin/python backend/load.py schema   # create the extension and tables (backend/schema.sql)
    .venv/bin/python backend/load.py load     # upsert sources and every shown passage
    .venv/bin/python backend/load.py status   # row counts, and a check against the files on disk

Reads DATABASE_URL from .env (git-ignored). Shown passages are status keep or no-distress in
corpus/passages/<source>.jsonl. Sources switched off in pipeline/sources.toml are left out. Restricted
sources are loaded with restricted = true, so the app can keep them off the public site.
"""

import json
import os
import re
import sys
import tomllib
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

ROOT = Path(__file__).resolve().parents[1]
SHOWN = ("keep", "no-distress")


def connect():
    load_dotenv(ROOT / ".env")
    url = os.environ.get("DATABASE_URL")
    if not url:
        sys.exit("DATABASE_URL is not set in .env")
    return psycopg.connect(url)


def config():
    return tomllib.loads((ROOT / "pipeline" / "sources.toml").read_text(encoding="utf-8"))["sources"]


def credits():
    """Tradition, work, translator and licence per source, from the table in Corpus-Policy section 2."""
    out, md = {}, (ROOT / "docs" / "Corpus-Policy.md").read_text(encoding="utf-8")
    section = md.split("## 2. Sources in v1", 1)[1].split("\n### ", 1)[0]
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 6 and re.fullmatch(r"[a-z][a-z0-9-]+", cells[0]):
            out[cells[0]] = dict(tradition=cells[1], work=cells[2], translator=cells[3],
                                 licence=re.sub(r"\*\*|;.*", "", cells[4]).strip())
    return out


def shown_passages():
    cfg = config()
    for s, c in sorted(cfg.items()):
        if not c.get("active", True):
            continue
        f = ROOT / "corpus" / "passages" / f"{s}.jsonl"
        for line in f.read_text(encoding="utf-8").splitlines():
            p = json.loads(line)
            if p["status"] in SHOWN:
                yield p


def schema():
    with connect() as db:
        db.execute((ROOT / "backend" / "schema.sql").read_text(encoding="utf-8"))
    print("schema applied")


def load():
    cfg, cr = config(), credits()
    missing = [s for s in cfg if cfg[s].get("active", True) and s not in cr]
    if missing:
        sys.exit(f"no credit row in Corpus-Policy section 2 for: {', '.join(missing)}")
    with connect() as db, db.cursor() as cur:
        for s, c in sorted(cfg.items()):
            if s in cr:
                cur.execute("""insert into sources (id, tradition, work, translator, licence, restricted, active)
                               values (%s, %s, %s, %s, %s, %s, %s)
                               on conflict (id) do update set tradition = excluded.tradition, work = excluded.work,
                                 translator = excluded.translator, licence = excluded.licence,
                                 restricted = excluded.restricted, active = excluded.active""",
                            (s, *cr[s].values(), bool(c.get("restricted")), c.get("active", True)))
        rows = []
        for p in shown_passages():
            tags = {k: v for k, v in p["tags"].items() if k != "faith"}
            rows.append((p["pid"], p["source"], p["display"], p["display_text"], p["plain"], p["core_idea"],
                         p["quotability"], p["complete"], p["status"] == "no-distress", p.get("near_group"),
                         p["words"], p["tags"]["faith"], Jsonb(tags)))
        cur.executemany("""insert into passages (pid, source_id, display, display_text, plain, core_idea, quotability,
                             complete, hide_in_distress, near_group, words, faith, tags)
                           values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                           on conflict (pid) do update set source_id = excluded.source_id, display = excluded.display,
                             display_text = excluded.display_text, plain = excluded.plain, core_idea = excluded.core_idea,
                             quotability = excluded.quotability, complete = excluded.complete,
                             hide_in_distress = excluded.hide_in_distress, near_group = excluded.near_group,
                             words = excluded.words, faith = excluded.faith, tags = excluded.tags""", rows)
        # Passages no longer shown (cut, deduplicated, or source switched off) leave the database
        cur.execute("delete from passages where not (pid = any(%s))", ([r[0] for r in rows],))
        print(f"loaded {len(rows):,} passages; removed {cur.rowcount} no longer shown")


def status():
    files = list(shown_passages())
    with connect() as db:
        q = lambda sql: db.execute(sql).fetchone()[0]
        n = q("select count(*) from passages")
        print(f"sources: {q('select count(*) from sources')}  passages: {n:,} (files on disk: {len(files):,})")
        print(f"restricted passages: {q('select count(*) from passages join sources s on s.id = source_id where s.restricted')}"
              f"  hidden from distress: {q('select count(*) from passages where hide_in_distress')}")
        for setup, k in db.execute("select setup, count(*) from passage_embeddings group by setup order by setup"):
            print(f"embeddings {setup}: {k:,}")
        print(f"database size: {q('select pg_size_pretty(pg_database_size(current_database()))')}")
    sys.exit(0 if n == len(files) else "MISMATCH between database and files")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"schema": schema, "load": load, "status": status}.get(cmd, lambda: sys.exit(__doc__))()
