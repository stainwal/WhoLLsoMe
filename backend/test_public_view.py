"""Check the anon (public) role's read access (13 Oct 2026).

    .venv/bin/python backend/test_public_view.py

Two passes, the same checks in each: the view holds every unrestricted shown passage and no restricted
one; a known restricted passage can't be read; the base tables refuse anon outright; the view can't be
written to.
  1. Database: switches to the anon role inside a transaction (the role the public key maps to).
  2. REST API: calls Supabase's public API with the publishable key (SUPABASE_URL, SUPABASE_ANON_KEY
     in .env), exactly as a stranger with the key from the web page would.
Exits non-zero on any failure.
"""

import json
import os
import sys
import urllib.error
import urllib.request
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


def rest(path, method="GET", body=None, count=False):
    """(status, parsed body, total count or None) for one call to the REST API with the publishable key."""
    key = os.environ["SUPABASE_ANON_KEY"]
    headers = {"apikey": key, "Content-Type": "application/json"}
    if count:
        headers.update({"Prefer": "count=exact", "Range": "0-0"})
    req = urllib.request.Request(os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1/" + path,
                                 json.dumps(body).encode() if body else None, headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            total = r.headers.get("Content-Range", "").rpartition("/")[2]
            return r.status, json.loads(r.read() or b"null"), int(total) if total.isdigit() else None
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null"), None


if not (os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_ANON_KEY")):
    check("REST API pass", False, "SUPABASE_URL or SUPABASE_ANON_KEY missing from .env")
else:
    code, _, n = rest("public_passages?select=pid", count=True)
    check("REST: view readable, every unrestricted passage", code in (200, 206) and n == expected, f"HTTP {code}, {n} of {expected:,}")
    code, rows, _ = rest(f"public_passages?select=pid&pid=eq.{restricted_pid}")
    check("REST: restricted passage not returned", code == 200 and rows == [], f"HTTP {code}, {len(rows or [])} rows")
    code, rows, _ = rest("public_passages?select=pid&source_id=in.(" + ",".join(restricted_ids) + ")&limit=1")
    check("REST: no row from a restricted or switched-off source", code == 200 and rows == [], f"HTTP {code}")
    for table in ("passages", "sources", "passage_embeddings"):
        code, body, _ = rest(f"{table}?select=*&limit=1")
        refused = code == 401 and isinstance(body, dict) and body.get("code") == "42501"   # permission denied
        check(f"REST: base table {table} refused", refused, f"HTTP {code} {body.get('code') if isinstance(body, dict) else ''}")
    # Writes are refused twice over: anon holds only select, and a two-table view can't be written through
    # (Postgres reports the second, 55000, before checking privileges).
    for method, path, body in (("POST", "public_passages", {"pid": "x"}),
                               ("PATCH", f"public_passages?pid=eq.{restricted_pid}", {"plain": "x"}),
                               ("DELETE", "public_passages?pid=neq.x", None)):
        code, out, _ = rest(path, method, body)
        refused = code >= 400 and isinstance(out, dict) and out.get("code") in ("42501", "55000")
        check(f"REST: {method} on the view refused", refused, f"HTTP {code} {out.get('code') if isinstance(out, dict) else ''}")
    code, _, n = rest("public_passages?select=pid", count=True)
    check("REST: view unchanged after the write attempts", n == expected, f"{n} of {expected:,}")

sys.exit(1 if fails else 0)
