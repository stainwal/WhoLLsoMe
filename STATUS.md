# Status

*Updated at the end of every session. Last update: Thu 8 Oct 2026, 01:20 IST (overnight session 3: Day 6 rules locked, Days 7–11 full corpus run).*

## 1. Where we are

- **Plan days done:** 1, 2, 4, 6, 7–11. Still open: Day 3 (test sets) and Day 5 (blind keep/cut review). Days 7–11 finished about 5 days ahead of the plan dates.
- **Done:**
  - Days 0–1: setup, repo, accounts, free-tier limits.
  - Day 2: tag schema and taxonomy v2; source on/off switch; harm review narrowed to a safety field (Decision 3).
  - Day 4: 33 sources normalised (4.18M words); extraction harness; pilot on Sonnet and Opus.
  - Day 6: pilot tagged on both models; model Opus 5.5 at medium effort; prompts locked (v1).
  - Days 7–11 (`logs/D07.md`):
    - all 33 sources extracted: 4,096,568 words, 1,720 chunks;
    - 5,029 passages passed the verbatim check (7 rejected);
    - all 5,029 tagged;
    - 16 cut and 45 hidden from distress by the safety field;
    - one file per source in `corpus/passages/`.
- **Not started:** test sets, deduplication and corpus statistics, retrieval, app code.

## 2. Next session

1. Decided 8 Oct: cuts stay cut; MN 144 and Walden passages hidden from distress; `<j>` stripped for display.
2. **Day 3, mostly done 9 Oct** (Plan section 4.1):
   - Human set written: `../Test-Statements-Human.md` (32 held-out, 5 crisis, 5 look-alikes). Still to do: convert it to `evals/human-set.jsonl` in the same format as the agent set.
   - Agent set compiled by the Cowork reviewer: `evals/agent-set.md` and `.jsonl` (60 golden, 20 held-out, 8 crisis, 8 look-alikes); sources in `evals/agent-set-provenance.md` (private).
   - Still open: [DECISION] gate thresholds.
3. **Day 5:** blind keep/cut review, now on a 40-passage sample from the full corpus to measure Opus precision.
4. **Then Days 12–13:**
   - deduplicate;
   - corpus statistics by source and theme.

## 3. Open decisions

| Day | Decision |
| --- | --- |
| 3 | Gate thresholds (proposed bar in `docs/Plan.md` section 5.3) |
| 27 | Name, look, domain |

## 4. Eval results

- **Full corpus run (Days 7–11, `logs/D07.md`):**
  - Verbatim check: 5,029 of 5,036 exact (99.86%); 7 rejected and logged.
  - Tag validity: 0 problems across 5,029 passages.
  - Safety field: 16 cut (12 Seneca "open door" passages, 2 likely over-cuts, 2 `group-hatred`); 45 `welcomes-death`.
- **Pilot (`logs/D04.md`):**
  - Verbatim: Sonnet 49 of 49, Opus 86 of 86.
  - Same top tag, Sonnet vs Opus: themes 87%, tone 79%, feelings 57%, situations 55%, safety 100%.

## 5. Parking list

Ideas raised but out of v1 scope. Add here; don't build.

- Read-aloud of passages
- Share-as-image card
- Phase 2 sources (Dark Night/Lewis, Macauliffe selections, Epicurus, Curtis)
- Other SuttaCentral Minor Collection books already on disk (Sutta Nipata, Udana, Itivuttaka, Theragatha, Therigatha, Jataka…), all CC0
- Test whether a higher effort level changes extraction selectivity
- Pre-filtered Bible books (Leviticus, Numbers, 1 Chronicles; 73,189 words), not yet read

## 6. Token budget

Used by `CLAUDE.md` section 4.3 for every heavy run.

- **Calibration (measured on the full run, 7–8 Oct):**
  - **Cost:** about 0.5% of the weekly limit per 100,000 words for extraction and tagging together. The full run took 4.10M words and moved weekly from 46% to 66%.
  - **5-hour window:** about 3% per 100,000 words, so one window holds about 3M words. On a big run this is the binding limit.
  - **Ratio:** session % ≈ 6 × weekly %.
  - **Superseded:** the Day 4 estimate (1.4% per 100k words for extraction alone) was about 3 times too high.
  - **Readings:** Claude reads both bars through the app's usage API, so no screenshots are needed.
- **Overhead:** each helper carries about 70k tokens of mostly cached overhead, so pack many chunks per helper (batching tested: 101 passages tagged in one helper for about 94k tokens).
- **Default budget per run:** at most 15% of the weekly limit; leave at least 30% of the week unused.
- **Model for bulk work:** Opus 5.5, medium effort (decided 7 Oct; pilot showed the same cost as Sonnet).
- **Weekly limit resets:** Thursdays about 05:30 IST (Usage screen, 7 Oct). Allowance left unused before a reset is lost, so the evening before a reset the 30% reserve can be relaxed if Shailesh agrees.
- **Readings so far:**

  | When (7 Oct) | Session | Weekly (All models) |
  | --- | --- | --- |
  | 17:14 IST | 12% | 42% |
  | Before pilot | 23% | 44% |
  | After Sonnet extraction | 24% | 44% |
  | After Opus extraction | 25% | 44% |
  | After tagging | 29% | 45% |
  | Before full run, 22:07 | 3% | 46% |
  | Window 1 paused, 22:49 | 84% | 59% |
  | Window 2 start, 8 Oct 00:51 | 0% | 60% |
  | Full run complete, 8 Oct 01:12 | 39% | 66% |
- **One-time full reset:** available on the Usage screen ("Reset for free"), expires 22 Oct. Not needed for the corpus run, which fit in one week's allowance. Use only with Shailesh's say-so.

## 7. Free-tier limits

Checked 7 Oct 2026 on the official pricing and docs pages. Check again before launch (Day 32).

### 7.1 Supabase (Free)

| Limit | Value | What it means for us |
| --- | --- | --- |
| Projects | 2 per organisation (paused projects don't count) | One is enough |
| Database | 500 MB per project | Enough for the corpus plus embeddings at modest dimensions; size gets checked on Day 15 |
| Storage / egress | 1 GB / 5 GB per month | Fine at hobby scale |
| Edge functions | 500,000 invocations per month | Not used; the API runs on Vercel |
| pgvector | Can be enabled (Dashboard → Database → Extensions). The docs don't say it's paid-only | Confirm when we enable it on Day 15 |
| **Inactivity pause** | Paused after about 7 days of low activity. Data is kept; resume from the dashboard. Treat the restore window as 90 days (docs say 1 year, changelog says 90) | **Needs a keep-alive** once the app is live; until then, pause is harmless |
| **Backups** | None on Free | Keep our own `supabase db dump` exports in the repo |

### 7.2 Vercel (Hobby)

| Limit | Value | What it means for us |
| --- | --- | --- |
| Use | Non-commercial only. Ads, payments or a paid collaborator make it commercial | Fine for a resume project; Pro is $20/month if that changes |
| Function invocations | 1,000,000 per month | Ample |
| Active CPU / memory | 4 CPU-hours / 360 GB-hours per month | Ample: our functions mostly wait on API calls |
| Function duration | 300 s (Fluid compute, the default) | Ample |
| Data transfer | 100 GB per month Fast Data Transfer; 1,000,000 CDN requests | Ample |
| Builds | 100 deployments per day, 45 min per build | Ample |
| **Over a limit** | That feature pauses for about 30 days; no overage charges, no spend controls on Hobby | Rate limit + Turnstile protect this |

### 7.3 Cloudflare Turnstile (Free)

Unlimited verifications, 20 widgets, 10 hostnames per widget. No concerns.
