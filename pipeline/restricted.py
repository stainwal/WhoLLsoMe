"""Restricted sources: kept on disk and used by the pipeline, never committed to git (Day 16, 12 Oct 2026).

Sources marked `restricted = true` in pipeline/sources.toml are copyrighted or of unclear licence
(Corpus-Policy section 2). Their text lives in two kinds of place, both git-ignored:
  - per-source files, ignored in place by name (.gitignore, "Restricted sources" block);
  - corpus/restricted/<path>: the restricted share of a file that mixes sources (enrichment.json,
    helper batches, reports). The public file holds everything else; readers merge the two.

    python3 pipeline/restricted.py split            # move restricted items out of mixed files
    python3 pipeline/restricted.py scan [PATH ...]  # which files hold restricted text (default: all tracked;
                                                    # a folder is scanned recursively)
    python3 pipeline/restricted.py check            # pre-commit: fail if any staged file holds restricted text

The scan fingerprints every restricted source as overlapping 8-word runs and reports any file sharing
one; it works on the text itself, so it catches a quotation in a log or a report as well as a data file.
"""

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RDIR = ROOT / "corpus" / "restricted"
SHINGLE = 8
MIN_RUNS = 3      # an unbroken stretch of 3 overlapping 8-word runs = 10+ shared words
# Mixed files and folders whose items carry a passage id or a source name: split by item.
# (tags/ is not split: tag files hold labels and ids, no passage text.)
MIXED_DIRS = ["corpus/passages/bulk/enrich", "corpus/passages/bulk/judge",
              "corpus/passages/bulk/rewrite", "corpus/passages/bulk/rejudge"]
MIXED_DICTS = ["corpus/passages/bulk/enrichment.json", "corpus/passages/bulk/overrides.json",
               "corpus/passages/bulk/duplicates.json", "corpus/passages/bulk/fix-reverts.json"]
LIST_KEYS = ("items", "judgements", "tags")


def sources():
    cfg = tomllib.loads((ROOT / "pipeline" / "sources.toml").read_text(encoding="utf-8"))["sources"]
    return sorted(s for s, c in cfg.items() if c.get("restricted"))


def prefixes():
    """Passage-id prefixes of the restricted sources (an id is <chunk prefix>-NNN-pNN)."""
    out = set()
    for s in sources():
        out.add(s)
        f = ROOT / "corpus" / "passages" / "bulk" / "checked" / f"{s}.jsonl"
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines()[:1]:
                out.add(json.loads(line)["chunk"].rsplit("-", 1)[0])
    return tuple(sorted(out))


def is_restricted_id(pid):
    pid = str(pid).split("#")[0]
    return any(pid.startswith(p + "-") for p in prefixes())


def twin(path):
    """corpus/restricted/<path relative to ROOT>: where the restricted share of a mixed file lives."""
    return RDIR / Path(path).resolve().relative_to(ROOT)


# ---- reading and writing mixed files -------------------------------------------------------------

def load_json(path, default=None):
    """A mixed JSON file merged with its restricted twin (dicts by key, item lists appended)."""
    path = Path(path)
    if not path.exists() and not twin(path).exists():
        return default
    pub = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    t = twin(path)
    if not t.exists():
        return pub
    res = json.loads(t.read_text(encoding="utf-8"))
    if pub is None:
        return res
    if isinstance(pub, dict) and not any(k in pub for k in LIST_KEYS):
        return {**pub, **res}
    for k in LIST_KEYS:
        if k in res:
            pub.setdefault(k, []).extend(res[k])
    return pub


def save_json(path, obj, indent=1):
    """Write a pid-keyed dict, putting restricted keys in the twin."""
    path = Path(path)
    pub = {k: v for k, v in obj.items() if not is_restricted_id(k)}
    res = {k: v for k, v in obj.items() if is_restricted_id(k)}
    path.write_text(json.dumps(pub, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8")
    if res:
        twin(path).parent.mkdir(parents=True, exist_ok=True)
        twin(path).write_text(json.dumps(res, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8")
    elif twin(path).exists():
        twin(path).unlink()


def glob_mixed(folder, pattern="*.json"):
    """File names in a mixed folder, public or restricted-only, sorted; read each with load_json."""
    folder = Path(folder)
    names = {f.name for f in folder.glob(pattern)} | {f.name for f in twin(folder).glob(pattern)}
    return [folder / n for n in sorted(names)]


def split_file(path):
    """Move restricted items of one helper output file into its twin. Returns items moved."""
    path = Path(path)
    obj = json.loads(path.read_text(encoding="utf-8"))
    moved = 0
    for k in LIST_KEYS:
        if k not in obj:
            continue
        keep = [x for x in obj[k] if not is_restricted_id(x.get("id"))]
        out = [x for x in obj[k] if is_restricted_id(x.get("id"))]
        if not out:
            continue
        t = twin(path)
        prev = json.loads(t.read_text(encoding="utf-8")) if t.exists() else {}
        known = {x.get("id") for x in prev.get(k, [])}
        prev.setdefault(k, []).extend(x for x in out if x.get("id") not in known)
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(json.dumps(prev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        obj[k], moved = keep, moved + len(out)
    if moved:
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return moved


def split():
    """Run after helpers write output, before verify, merge or commit. Idempotent."""
    n = 0
    for d in MIXED_DIRS:
        for f in sorted((ROOT / d).glob("*.json")):
            n += split_file(f)
    for f in MIXED_DICTS:
        p = ROOT / f
        if p.exists():
            obj = load_json(p, {})
            save_json(p, obj)
    print(f"split: {n} restricted items moved out of helper files; pid-keyed files re-split")
    return n


def write_report(path, lines):
    """A Markdown report: the full version goes to the restricted twin; in the public file, a table
    row that names a restricted passage keeps its first cell and loses its text."""
    path, full = Path(path), "\n".join(lines) + "\n"
    ids = re.compile(r"\b(?:" + "|".join(re.escape(x) for x in prefixes()) + r")-[\w-]+")
    pub, n = [], 0
    for line in lines:
        if line.startswith("| ") and ids.search(line):
            cells = line.strip().strip("|").split(" | ")
            m = ids.search(line).group(0)
            note = f"restricted source ({m}); text kept off git in `corpus/restricted/`"
            line = "| " + " | ".join([cells[0] if ids.search(cells[0]) else m, note] + [""] * (len(cells) - 2)) + " |"
            n += 1
        pub.append(line)
    path.write_text("\n".join(pub) + "\n", encoding="utf-8")
    t = twin(path)
    if n:
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(full, encoding="utf-8")
    elif t.exists():
        t.unlink()
    return n


# ---- the text scan -------------------------------------------------------------------------------

def words(text):
    return re.findall(r"[a-z]+", text.lower().replace("’", "'").replace("'", ""))


def source_words(folder):
    txt = ""
    for f in sorted(folder.glob("*.*")):
        if f.suffix in (".txt", ".json", ".md", ".html", ".xml"):
            raw = f.read_text(encoding="utf-8", errors="replace")
            txt += " " + raw.replace("\\n", " ").replace('\\"', '"')
    return words(txt)


def fingerprints():
    """8-word runs of the restricted sources, minus any run also found in a public source: licence
    boilerplate, scripture quoted in both, and stock phrases are not the restricted translator's text."""
    fp, restricted = {}, set(sources())
    for s in restricted:
        w = source_words(ROOT / "corpus" / "source" / s)
        for i in range(len(w) - SHINGLE + 1):
            fp.setdefault(" ".join(w[i:i + SHINGLE]), s)
    for d in sorted((ROOT / "corpus" / "source").iterdir()):
        if d.is_dir() and d.name not in restricted:
            w = source_words(d)
            for i in range(len(w) - SHINGLE + 1):
                fp.pop(" ".join(w[i:i + SHINGLE]), None)
    return fp


def hits(text, fp):
    """Per restricted source: the longest unbroken stretch of matching 8-word runs in text.
    3 = a shared stretch of 10+ words; scattered stock phrases never add up."""
    w = words(text.replace("\\n", " ").replace('\\"', '"'))
    found, run, prev = {}, 0, None
    for i in range(len(w) - SHINGLE + 1):
        s = fp.get(" ".join(w[i:i + SHINGLE]))
        run = run + 1 if s and s == prev else (1 if s else 0)
        prev = s
        if s:
            found[s] = max(found.get(s, 0), run)
    return found


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


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


def scan(paths=None, staged=False):
    fp = fingerprints()
    if staged:
        paths = [p for p in git("diff", "--cached", "--name-only", "--diff-filter=ACMR").splitlines()]
    else:
        paths = expand(paths or git("ls-files").splitlines())
    bad = {}
    for p in paths:
        try:
            text = git("show", f":{p}") if staged else (ROOT / p).read_text(encoding="utf-8", errors="replace")
        except subprocess.CalledProcessError:
            continue
        h = {k: v for k, v in hits(text, fp).items() if v >= MIN_RUNS}
        if h:
            bad[p] = h
    return bad


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if cmd == "split":
        split()
    elif cmd in ("scan", "check"):
        bad = scan(sys.argv[2:] or None, staged=(cmd == "check"))
        for p, h in sorted(bad.items()):
            print(f"{p}: " + ", ".join(f"{s} (stretch of {n + SHINGLE - 1} words)" for s, n in sorted(h.items())))
        what = "staged files" if cmd == "check" else "files"
        print(f"{len(bad)} {what} hold restricted text ({', '.join(sources())})")
        if cmd == "check" and bad:
            print("BLOCKED: restricted-source text must not be committed. Run `python3 pipeline/restricted.py split`, "
                  "or unstage the files above.")
            sys.exit(1)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
