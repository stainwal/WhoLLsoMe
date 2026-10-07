# Status

*Updated at the end of every session. Last update: Wed 7 Oct 2026 (Day 2 evening session, which also completed Day 4 and part of Day 6).*

## 1. Where we are

- **Plan days done:** 1, 2, 4; Day 6 partly done. Day 3 (test sets) is still to come; it was skipped on purpose so the statements are written before any pilot review. Plan dates unchanged.
- **Done:**
  - Days 0–1: setup, repo, accounts, free-tier limits.
  - Day 2: tag schema and taxonomy v2 (`pipeline/prompts/taxonomy.md`); source on/off switch (`pipeline/sources.toml`); harm review narrowed to a safety field (Decision 3).
  - Day 4:
    - all 33 sources normalised (4.18M words, `corpus/passages/normalised/`);
    - extraction harness built;
    - pilot extracted on Sonnet 5.5 and Opus 5.5, with 100% verbatim matches.
  - Day 6, pulled forward: pilot tagged on both models.
- **Not started:** test sets, full corpus run, retrieval, app code.

## 2. Next session (Day 3)

1. Shailesh writes the test sets (Plan section 4.1):
   - 40 golden statements
   - 20 held-out statements
   - 5 crisis statements
   - 5 crisis look-alikes

   Suggestion: cover every situation family in taxonomy section 4 at least once.
2. [DECISION] Gate thresholds (Plan section 5.3).
3. Then Day 5: blind keep/cut review of the 101 pooled pilot passages (`corpus/passages/pilot/pool.jsonl`).

## 3. Open decisions

| Day | Decision |
| --- | --- |
| 3 | Gate thresholds (proposed bar in `docs/Plan.md` section 5.3) |
| 6 | Model for bulk work: Sonnet (49 picks) vs Opus (86 picks); decide after the Day 5 blind review |
| 27 | Name, look, domain |

## 4. Eval results

Pilot results (Day 4 and Day 6 pulled forward; details in `logs/D04.md`):

- **Verbatim check:**
  - Sonnet 49 of 49 exact matches
  - Opus 86 of 86 exact matches
- **Tag agreement, Sonnet vs Opus, same top tag:**
  - themes 87%
  - tone 79%
  - feelings 57% (after Decision 4)
  - situations 55%
  - safety 100%

## 5. Parking list

Ideas raised but out of v1 scope. Add here; don't build.

- Read-aloud of passages
- Share-as-image card
- Phase 2 sources (Dark Night/Lewis, Macauliffe selections, Epicurus, Curtis)
- Other SuttaCentral Minor Collection books already on disk (Sutta Nipata, Udana, Itivuttaka, Theragatha, Therigatha, Jataka…), all CC0
- Test whether a higher effort level changes extraction selectivity

## 6. Token budget

Used by `CLAUDE.md` section 4.3 for every heavy run.

- **Calibration (rough, 7 Oct):**
  - **Cost:** about 1.4% of the weekly limit per 100,000 words, per extraction pass (±50%).
  - **Method:** the pilot moved weekly by under 1% per 13,000-word run, so the figure is derived from the session bar (session % ≈ 5.5 × weekly %).
  - **Model:** Sonnet 5.5 and Opus 5.5 look the same at this resolution.
  - **Next:** refine on the first Day 7 batch.
- **Overhead:** each helper carries about 70k tokens of mostly cached overhead, so pack many chunks per helper (batching tested: 101 passages tagged in one helper for about 94k tokens).
- **Default budget per run:** at most 15% of the weekly limit; leave at least 30% of the week unused.
- **Model for bulk work:** Sonnet, pending the Day 6 decision.
- **Weekly limit resets:** Thursdays about 05:30 IST (Usage screen, 7 Oct). Allowance left unused before a reset is lost, so the evening before a reset the 30% reserve can be relaxed if Shailesh agrees.
- **Readings so far:**

  | When (7 Oct) | Session | Weekly (All models) |
  | --- | --- | --- |
  | 17:14 IST | 12% | 42% |
  | Before pilot | 23% | 44% |
  | After Sonnet extraction | 24% | 44% |
  | After Opus extraction | 25% | 44% |
  | After tagging | 29% | 45% |
- **One-time full reset:** available on the Usage screen ("Reset for free"), expires 22 Oct. Save it for the full corpus run (Plan Days 7–11); use only with Shailesh's say-so.

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
