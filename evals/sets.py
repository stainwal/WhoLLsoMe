"""Test sets for the evals: public statements plus the private crisis statements (12 Oct 2026).

The 13 crisis statements (human C01-C05, agent AC01-AC08) are kept out of git so the crisis check
can't be tuned to them (docs/Publication-Checklist.md section 1, item 6). They live in the git-ignored
evals/private/crisis.jsonl, in the same record shape as the public sets; load_set() merges them back.

    python3 evals/sets.py status            # counts per set and part; says if the private file is missing
    python3 evals/sets.py scan [PATH ...]   # which files hold crisis text (default: all tracked files;
                                            # a folder is scanned recursively)
    python3 evals/sets.py check             # pre-commit: fail if any staged file holds crisis text

Every eval reads the sets through load_set(); never open the public .jsonl files directly, or the
crisis statements are silently left out.
"""

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PUBLIC = {"human": HERE / "human-set.jsonl", "agent": HERE / "agent-set.jsonl"}
PRIVATE = HERE / "private" / "crisis.jsonl"
RUN = 6           # a file sharing any 6-word run with a crisis statement is flagged (shortest is 16 words)


def _read(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def private_rows():
    if not PRIVATE.exists():
        sys.exit(f"missing {PRIVATE.relative_to(ROOT)}: the crisis statements are private and not in git; "
                 "restore it (the crisis rows of evals/*-set.jsonl in the private repo stainwal/WhoLLsoMe-archive)")
    return _read(PRIVATE)


def load_set(name):
    """All records of one set ('human' or 'agent'), crisis statements included, in the original file order."""
    rows = _read(PUBLIC[name]) + [r for r in private_rows() if r["set"] == name]
    return sorted(rows, key=lambda r: ({"crisis": 1, "look-alike": 2}.get(r["part"], 0), r["id"]))


def words(text):
    return re.findall(r"[a-z0-9']+", text.lower().replace("’", "'"))


def fingerprints():
    runs = {}
    for r in private_rows():
        w = words(r["text"])
        for i in range(len(w) - RUN + 1):
            runs.setdefault(" ".join(w[i:i + RUN]), r["id"])
    return runs


def hits(text, runs):
    w = words(text)
    return sorted({runs[k] for i in range(len(w) - RUN + 1) if (k := " ".join(w[i:i + RUN])) in runs})


def expand(paths):
    """Files to scan: a folder is read recursively (.git skipped), never silently passed over;
    a path that doesn't exist stops the scan rather than counting as clean."""
    out = []
    for p in paths:
        f = ROOT / p
        if f.is_dir():
            for x in sorted(f.rglob("*")):
                if x.is_file() and ".git" not in x.relative_to(f).parts:
                    out.append(str(x.relative_to(ROOT)) if x.is_relative_to(ROOT) else str(x))
        elif f.is_file():
            out.append(p)
        else:
            sys.exit(f"no such file or folder: {p}")
    return out


def scan(paths, staged=False):
    runs, found = fingerprints(), {}
    for p in (paths if staged else expand(paths)):
        if (ROOT / p).resolve() == PRIVATE.resolve():
            continue
        if staged:
            r = subprocess.run(["git", "show", f":{p}"], cwd=ROOT, capture_output=True)
            data = r.stdout if r.returncode == 0 else b""
        else:
            data = (ROOT / p).read_bytes()
        ids = hits(data.decode("utf-8", "ignore"), runs)
        if ids:
            found[p] = ids
    return found


def git_lines(*args):
    return [l for l in subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.splitlines() if l]


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        for name in PUBLIC:
            rows = load_set(name)
            print(name, len(rows), dict(Counter(r["part"] for r in rows)))
    elif cmd == "scan":
        found = scan(sys.argv[2:] or git_lines("ls-files"))
        for p, ids in found.items():
            print(f"{p}: {', '.join(ids)}")
        print(f"{len(found)} file(s) hold crisis text")
    elif cmd == "check":
        if not PRIVATE.exists():
            print("crisis check skipped: evals/private/crisis.jsonl not on this machine")
            sys.exit(0)
        found = scan(git_lines("diff", "--cached", "--name-only", "--diff-filter=ACMR"), staged=True)
        for p, ids in found.items():
            print(f"BLOCKED {p}: holds text of crisis statement(s) {', '.join(ids)} (evals/sets.py)")
        sys.exit(1 if found else 0)
    else:
        sys.exit(__doc__)
