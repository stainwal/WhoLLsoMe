"""Check the anon (public) role's read access (13 Oct 2026).

    .venv/bin/python backend/test_public_view.py

Switches to the anon role inside a transaction (the same role the public API key maps to) and checks:
the view holds every unrestricted shown passage and no restricted one; a known restricted passage can't
be read; the base tables refuse anon outright. Exits non-zero on any failure.
"""

import sys
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load  # noqa: E402

fails = 0


def check(name, ok, detail=""):
    global fails
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {name}{'  (' + detail + ')' if detail else ''}")


with load.connect() as db:
    expected = db.execute("select count(*) from passages p join sources s on s.id = p.source_id "
                          "where not s.restricted and s.active").fetchone()[0]
    restricted_ids = [r[0] for r in db.execute("select id from sources where restricted or not active")]
    restricted_pid = db.execute("select p.pid from passages p join sources s on s.id = p.source_id "
                                "where s.restricted order by p.pid limit 1").fetchone()[0]
    db.execute("set local role anon")
    n = db.execute("select count(*) from public_passages").fetchone()[0]
    check("anon reads the view: every unrestricted passage", n == expected, f"{n:,} of {expected:,}")
    r = db.execute("select count(*) from public_passages where pid = %s", (restricted_pid,)).fetchone()[0]
    check("restricted passage not in the view", r == 0, restricted_pid)
    leaked = db.execute("select count(*) from public_passages where source_id = any(%s)", (restricted_ids,)).fetchone()[0]
    check("no row from a restricted or switched-off source", leaked == 0, f"{len(restricted_ids)} such sources")
    for table in ("passages", "sources", "passage_embeddings"):
        try:
            with db.transaction():
                db.execute(f"select 1 from {table} limit 1")
            check(f"anon refused on base table {table}", False, "query succeeded")
        except psycopg.errors.InsufficientPrivilege:
            check(f"anon refused on base table {table}", True, "permission denied")
    db.rollback()

sys.exit(1 if fails else 0)
