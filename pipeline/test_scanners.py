"""Positive-control test for the two text scanners (Day 16, 12 Oct 2026).

    python3 pipeline/test_scanners.py

Both scanners once reported "0 found" for a folder they never opened (logs/D16.md, session 8). This test
plants restricted-source text and crisis text in a file three folders deep, passes only the top folder
to each scanner, and fails unless both find the file and pass over a clean neighbour. The planted text
is copied at run time from the git-ignored originals into a temp folder outside the repo, so no
restricted or crisis text is ever written into a tracked file.
"""

import importlib.util
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


restricted = load("pipeline/restricted.py", "restricted")
sets = load("evals/sets.py", "sets")


def restricted_sample(fp):
    """A 12-word stretch the restricted scan must flag: the first run of 5 consecutive fingerprints."""
    s = restricted.sources()[0]
    w = restricted.source_words(ROOT / "corpus" / "source" / s)
    for i in range(len(w) - 12):
        if all(" ".join(w[j:j + restricted.SHINGLE]) in fp for j in range(i, i + 5)):
            return " ".join(w[i:i + 12])
    sys.exit(f"no fingerprinted stretch found in {s}")


def main():
    failed = []
    with tempfile.TemporaryDirectory() as tmp:
        top = Path(tmp) / "top"
        deep = top / "a" / "b" / "c"
        deep.mkdir(parents=True)
        (top / "clean.txt").write_text("Nothing to see here: a note about the weather and a shopping list.\n")
        planted = deep / "planted.txt"

        # 1. Restricted-source text, found through the top folder only
        if not restricted.sources() or not (ROOT / "corpus" / "source" / restricted.sources()[0]).exists():
            print("SKIP restricted: restricted sources not on this machine")
        else:
            planted.write_text("Notes.\n" + restricted_sample(restricted.fingerprints()) + "\n")
            found = restricted.scan([str(top)])
            names = {Path(p).name for p in found}
            ok = names == {"planted.txt"}
            print(("PASS" if ok else "FAIL"), "restricted.py scan of a folder:", sorted(names) or "nothing found")
            ok or failed.append("restricted")

        # 2. Crisis text, found through the top folder only
        if not sets.PRIVATE.exists():
            print("SKIP crisis: evals/private/crisis.jsonl not on this machine")
        else:
            planted.write_text("Notes.\n" + sets.private_rows()[0]["text"] + "\n")
            found = sets.scan([str(top)])
            names = {Path(p).name for p in found}
            ok = names == {"planted.txt"}
            print(("PASS" if ok else "FAIL"), "sets.py scan of a folder:", sorted(names) or "nothing found")
            ok or failed.append("crisis")

        # 3. A missing path stops both scans instead of counting as clean
        for name, mod in (("restricted.py", restricted), ("sets.py", sets)):
            try:
                mod.expand([str(top / "no-such-folder")])
                print("FAIL", name, "accepted a missing path"); failed.append(name + " missing path")
            except SystemExit:
                print("PASS", name, "stops on a missing path")

    sys.exit(f"FAILED: {', '.join(failed)}" if failed else 0)


if __name__ == "__main__":
    main()
