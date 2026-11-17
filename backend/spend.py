"""API spend report (Day 23): live site (Supabase api_spend) plus scripts (evals/results/api-spend.jsonl).

Neither source holds any text: only time, route or purpose, model, tokens and cost.

    .venv/bin/python backend/spend.py                 everything
    .venv/bin/python backend/spend.py 2026-11-17      since a date (or ISO time, UTC)
"""

import json
import sys
from collections import defaultdict

import load

since = sys.argv[1] if len(sys.argv) > 1 else "1970-01-01"
rows = defaultdict(lambda: [0, 0, 0, 0.0])  # calls, input, output, usd


def add(key, i, o, usd):
    r = rows[key]
    r[0] += 1
    r[1] += i
    r[2] += o
    r[3] += float(usd)


with load.connect() as db:
    for route, model, i, o, usd in db.execute(
        "select route, model, input_tokens, output_tokens, usd from api_spend where at >= %s::timestamptz", (since,)
    ):
        add(("live", route, model), i, o, usd)

for line in open(load.ROOT / "evals/results/api-spend.jsonl", encoding="utf-8"):
    r = json.loads(line)
    if r["at"] >= since:
        add(("script", r["purpose"], r["model"]), r["input"], r["output"], r["usd"])

print(f"Spend since {since}")
print(f"{'where':7} {'route / purpose':28} {'model':20} {'calls':>6} {'in':>9} {'out':>8} {'usd':>9}")
total = 0.0
for (where, what, model), (n, i, o, usd) in sorted(rows.items()):
    total += usd
    print(f"{where:7} {what[:28]:28} {model:20} {n:6} {i:9} {o:8} {usd:9.4f}")
print(f"{'total':>79} {total:9.4f}")
