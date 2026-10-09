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

## 3. Session 3 (Days 6, 7–11) and the 8 Oct decisions — 8 Oct 2026

- **Checked:** `logs/D07.md`, `STATUS.md`, `docs/Decisions.md` (8 Oct rows), `.claude/settings.json`, `corpus/passages/bulk/cuts.md`, commits `4fbbdf3`, `35fc075`, `a6bdf9d`, `d4c50ae`.
- **Verdict:** outstanding run. All 33 sources (4.10M words) extracted and tagged unattended in about 64 minutes of active time; 5,029 passages, 99.86% verbatim, 0 tag-validity problems; cost 20% of the week against a predicted 57%. The safety field cut all 12 Seneca "open door" passages, including the Letter 70 test case. The permission allowlist for the unattended run is narrow (pipeline script, caffeinate, sleep, writes only to bulk output folders).
- **Flagged:**
  1. **Japji passage `japji-macauliffe-002-p02` shows source OCR errors** ("T have", "2 commotion"). Verbatim to a faulty scan, so it would display garbled. Not covered by the 8 Oct decisions. Needs a display fix through `overrides.json` or hiding.
  2. **No re-runs** (Shailesh, 8 Oct): passages that early helpers left out of Meditations, As a Man Thinketh and Pirkei Avot stay out. Low loss: the omissions were safety-motivated and largely overlap what the safety field would have hidden.
  3. **The 8 Oct decision work has no session log**; it was committed under D07. Minor; future follow-ups should append to the day's log.
  4. **Day 3 (test sets) is now the critical path.** The corpus is about 6 days ahead of the plan; retrieval work on Day 16 can't start without the test statements.
- **Changed:** `CLAUDE.md` section 4.3 (Claude reads usage itself when it can); `STATUS.md` section 6 (full reset no longer earmarked); `docs/Showcase.md` story points and tracker.

