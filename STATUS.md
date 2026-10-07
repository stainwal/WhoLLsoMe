# Status

*Updated at the end of every session. Last update: Wed 7 Oct 2026 (Day 0).*

## 1. Where we are

- **Plan day:** 0 of 33. Day 1 is Thu 8 Oct 2026.
- **Done:** `Version1_QuickLaunch/` created; 33 sources copied to `corpus/source/` (4,215 files, 40 MB; originals untouched in `../Version0/corpus/raw/`); `CLAUDE.md`, `docs/Plan.md`, `docs/Decisions.md`, `docs/Corpus-Policy.md` written; `logs/` folder and the `session-close` skill (`.claude/skills/session-close/`) set up; token-budget process defined (`CLAUDE.md` section 4.3).
- **Not started:** git repo, accounts, extraction, evals, code.

## 2. Next session (Day 1)

1. Open Claude Code in `Version1_QuickLaunch` and say "start session".
2. Create a git repo and a private GitHub repo.
3. Accounts: Supabase (new); Vercel (existing account). The Anthropic API and embeddings accounts come later (Days 20 and 15).
4. Claude checks current free-tier limits and records them here.

## 3. Open decisions

| Day | Decision |
| --- | --- |
| 2 | Passage and tag schema; cap on GRAY Sivananda passages |
| 3 | Gate thresholds (proposed bar in `docs/Plan.md` section 5.3) |
| 27 | Name, look, domain |

## 4. Eval results

None yet.

## 5. Parking list

Ideas raised but out of v1 scope. Add here; don't build.

- Read-aloud of passages
- Share-as-image card
- Phase 2 sources (Dark Night/Lewis, Macauliffe selections, Epicurus, Curtis)

## 6. Token budget

Used by `CLAUDE.md` section 4.3 for every heavy run.

- **Calibration:** not measured yet. Set during the Day 4 pilot as "% of weekly limit per 100,000 words processed", refined after every run.
- **Default budget per run:** at most 15% of the weekly limit; leave at least 30% of the week unused.
- **Model for bulk work:** Sonnet, pending the Day 6 comparison.
- **Weekly limit resets:** not recorded yet (Claude asks on the first reading).
