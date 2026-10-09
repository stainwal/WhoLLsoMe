"""Convert Shailesh's human test statements into evals/human-set.jsonl.

    python3 evals/build_human_set.py            # reads ../Test-Statements-Human.md, writes evals/human-set.jsonl

Same record shape as evals/agent-set.jsonl: id, set, part, life_area, borderline, text.
H01-H32 are all held out (decided 9 Oct 2026); C01-C05 are crisis; L01-L05 are look-alikes.
Life areas are Claude's reading of each statement, using the agent set's 11 areas, so the
two sets can be compared area by area. Re-run after any edit to the source file.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent.parent / "Test-Statements-Human.md"
OUT = HERE / "human-set.jsonl"

PART = {"H": "held-out", "C": "crisis", "L": "look-alike"}
LIFE_AREA = {
    "H01": "Self-doubt, direction and decisions", "H02": "Work and study", "H03": "Love and partnership",
    "H04": "Health and body", "H05": "Everyday life and good news", "H06": "Work and study",
    "H07": "Loss and grief", "H08": "Family", "H09": "Self-doubt, direction and decisions",
    "H10": "Family", "H11": "Health and body", "H12": "Friends and community", "H13": "Family",
    "H14": "Friends and community", "H15": "Work and study", "H16": "Self-doubt, direction and decisions",
    "H17": "Self-doubt, direction and decisions", "H18": "Faith, practice and meaning",
    "H19": "Faith, practice and meaning", "H20": "Love and partnership", "H21": "Friends and community",
    "H22": "Faith, practice and meaning", "H23": "Family", "H24": "Health and body", "H25": "Health and body",
    "H26": "Self-doubt, direction and decisions", "H27": "Family", "H28": "Harm done to me or by me",
    "H29": "Love and partnership", "H30": "Money, home and law", "H31": "Loss and grief",
    "H32": "Everyday life and good news",
}

# A statement starts "- H01: " and runs until the next "- X00:" line or the next heading.
# Continuation paragraphs are indented; blank lines inside a statement become paragraph breaks.
ITEM = re.compile(r"^- (?P<id>[HCL]\d{2}): (?P<first>.*)$")


def parse(md: str):
    items, cur = [], None
    for line in md.splitlines():
        m = ITEM.match(line)
        if m:
            cur = {"id": m["id"], "paras": [m["first"].strip()]}
            items.append(cur)
        elif cur is None or line.startswith("#"):
            cur = None
        elif line.strip() == "":
            if cur["paras"] and cur["paras"][-1] != "":
                cur["paras"].append("")
        else:
            cur["paras"][-1] = (cur["paras"][-1] + " " + line.strip()).strip()
    out = []
    for it in items:
        text = "\n\n".join(p for p in it["paras"] if p)
        borderline = "[borderline]" in text
        text = text.replace("[borderline]", "").strip()
        text = re.sub(r"[ \t]+", " ", text)
        kind = it["id"][0]
        out.append({"id": it["id"], "set": "human", "part": PART[kind],
                    "life_area": LIFE_AREA.get(it["id"]) if kind == "H" else None,
                    "borderline": borderline, "text": text})
    return out


if __name__ == "__main__":
    recs = parse(SRC.read_text(encoding="utf-8"))
    with OUT.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter
    print(f"wrote {len(recs)} records to {OUT.relative_to(HERE.parent)}:", dict(Counter(r['part'] for r in recs)),
          "| borderline:", [r['id'] for r in recs if r['borderline']])
