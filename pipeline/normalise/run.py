"""Normalise sources: python3 pipeline/normalise/run.py [source ...]

Each parser lives in parsers/<module>.py and exposes:
    SOURCES = ["folder-name", ...]
    def parse(source: str) -> list[Unit]
With no arguments, every parser runs. Prints a summary table.
"""

import importlib
import pkgutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import SOURCE_DIR, is_active, write_units  # noqa: E402
import parsers  # noqa: E402

def registry() -> dict:
    reg = {}
    for m in pkgutil.iter_modules(parsers.__path__):
        mod = importlib.import_module(f"parsers.{m.name}")
        for s in getattr(mod, "SOURCES", []):
            reg[s] = mod
    return reg


def main(argv):
    reg = registry()
    wanted = argv or sorted(reg)
    missing = sorted(p.name for p in SOURCE_DIR.iterdir() if p.is_dir() and p.name not in reg)
    rows = []
    for s in wanted:
        if not is_active(s):
            print(f"{s:36} skipped: switched off in pipeline/sources.toml")
            continue
        units = reg[s].parse(s)
        rows.append(write_units(s, units))
    total = 0
    for r in rows:
        total += r["words"]
        print(f"{r['source']:36} {r['units']:>7} units {r['words']:>9,} words")
    print(f"{'TOTAL':36} {sum(r['units'] for r in rows):>7} units {total:>9,} words")
    if missing and not argv:
        print("NO PARSER YET:", ", ".join(missing))


if __name__ == "__main__":
    main(sys.argv[1:])
