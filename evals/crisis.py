"""Crisis check eval (Plan section 4.2, Day 21 gate; 15 Oct 2026).

    .venv/bin/python evals/crisis.py batch      # every statement in both sets -> evals/judge-in/c01.jsonl (git-ignored)
    .venv/bin/python evals/crisis.py score      # classifier output (evals/judge/c01.json: ids and labels only) -> results

Two layers, as in the app: the phrase patterns in app/lib/crisis-prompt.ts (CRISIS_PATTERNS), then the model
label. Final = crisis if either says crisis. Gate (Plan section 5.3): all 13 crisis statements -> crisis
(a borderline crisis statement may get crisis or borderline); false crisis on look-alikes at most 1 of 5
human and 1 of 8 agent. Every other statement is reported too (a false crisis there hides the passages).
Output files hold ids and labels only, never statement text (the crisis statements are private).
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import retrieval as R  # noqa: E402
import sets  # noqa: E402

PROMPT = HERE.parent / "app" / "lib" / "crisis-prompt.ts"


def patterns():
    src = PROMPT.read_text(encoding="utf-8")
    body = src.split("CRISIS_PATTERNS: RegExp[] = [", 1)[1].split("];", 1)[0]
    out = []
    for m in re.finditer(r"/(.+?)/i,", body):
        out.append(re.compile(m.group(1).replace("\\s", r"\s"), re.I))
    return out


def all_statements():
    return sets.load_set("human") + sets.load_set("agent")


def batch():
    rows = [{"id": s["id"], "statement": s["text"]} for s in all_statements()]
    R.JUDGE_IN.mkdir(exist_ok=True)
    (R.JUDGE_IN / "c01.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(f"c01.jsonl: {len(rows)} statements (git-ignored folder)")


def score():
    model = {j["id"]: j["label"] for j in R.jload(R.JUDGE / "c01.json")["labels"]}
    pats = patterns()
    rows, out = all_statements(), {}
    for s in rows:
        hit = any(p.search(s["text"]) for p in pats)
        m = model[s["id"]]
        final = "crisis" if hit or m == "crisis" else m
        out[s["id"]] = {"set": s["set"], "part": s["part"], "borderline": s["borderline"], "pattern": hit,
                        "model": m, "final": final}
    res = {}
    for name in ("human", "agent"):
        mine = {k: v for k, v in out.items() if v["set"] == name}
        crisis = [v for v in mine.values() if v["part"] == "crisis"]
        ok = [v for v in crisis if v["final"] == "crisis" or (v["borderline"] and v["final"] == "borderline")]
        look = [v for v in mine.values() if v["part"] == "look-alike"]
        other = [v for v in mine.values() if v["part"] not in ("crisis", "look-alike")]
        res[name] = {"crisis_caught": f"{len(ok)} of {len(crisis)}",
                     "crisis_by_pattern": sum(v["pattern"] for v in crisis),
                     "false_crisis_lookalikes": f"{sum(v['final'] == 'crisis' for v in look)} of {len(look)}",
                     "borderline_link_lookalikes": sum(v["final"] == "borderline" for v in look),
                     "other_statements": dict(Counter(v["final"] for v in other)),
                     "borderline_statements": {k: v["final"] for k, v in mine.items() if v["borderline"]},
                     "misses": [k for k, v in mine.items() if v["part"] == "crisis" and v not in ok],
                     "false_crisis_ids": [k for k, v in mine.items() if v["part"] != "crisis" and v["final"] == "crisis"]}
    R.jsave(R.RESULTS / "crisis-v1.json", {"per_set": res, "per_statement": out})
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    {"batch": batch, "score": score}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: sys.exit(__doc__))()
