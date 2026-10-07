# Reviews

Reviews of each Claude Code session by the Cowork reviewer: what was checked, what was flagged, what changed as a result. Newest last.

## 1. Session 1 (Day 1) — 7 Oct 2026

- **Checked:** `logs/D01.md`, `STATUS.md`, `.gitignore`, git history and remote, Plan ticks.
- **Verdict:** clean. Every Day 1 item done with evidence; repo private; secrets ignored.
- **Flagged:** first commit carries the Mac's local email (matters only if the repo goes public); pgvector on Supabase Free unconfirmed (low risk, checked Day 15).
- **Good judgement noted:** Supabase project creation deferred to Day 15 so the 7-day inactivity pause doesn't start early.
- **Changed:** `STATUS.md` section 6 gained the weekly reset time.

## 2. Session 2 (Days 2, 4, part of 6) — 7 Oct 2026

- **Checked:** `logs/D02.md`, `logs/D04.md`, `STATUS.md`, `docs/Decisions.md`, `docs/Corpus-Policy.md` section 6, `pipeline/sources.toml`, commit `da37e8c`.
- **Verdict:** strong session. Normalisation verified word for word; 135 of 135 pilot passages passed the verbatim check; taxonomy grounded in named external sources; token calibration honest about its ±50% error.
- **Flagged:**
  1. *Way of Perfection* (Peers) and *Brother Lawrence* (Lightheart) are copyrighted editions. Corpus policy lists Peers under "never". Kept on Shailesh's call; recommended they run last in the bulk order and they are now item 1 on the publication checklist.
  2. Harm review now rests on one tagger field with no sample check. Decision stands; the first bulk batches (Seneca, Epictetus) should be checked for missed "door is open" passages before the rest run.
  3. `docs/Plan.md` still described the old harm passes (D6, D7–11). Fixed.
  4. Calibration: about 1.4% of the weekly limit per 100,000 words per extraction pass (±50%). A full extraction pass over 4.18M words is roughly half a week of allowance, plus tagging. The 5-hour session bar (about 5.5× the weekly rate) is the tighter limit on any one night.
- **Changed:** Plan wording for D6, D7–11, D33 and after-launch publication prep; showcase setup added (`docs/Showcase.md`, this file, log part 6).
