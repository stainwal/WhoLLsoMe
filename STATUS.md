# Status

*Updated at the end of every session. Last update: Wed 7 Oct 2026 (Day 1).*

## 1. Where we are

- **Plan day:** 1 of 33, done a day early (Wed 7 Oct). Plan dates unchanged: one day of slack.
- **Done:** Day 0 setup (folder, 33 sources in `corpus/source/`, brief, plan, decision log, corpus policy, session-close skill). Day 1: git repo, private GitHub repo [stainwal/WhoLLsoMe](https://github.com/stainwal/WhoLLsoMe) (sources included), Supabase account and organisation (no project until Day 15), Vercel linked to GitHub, free-tier limits recorded (section 7).
- **Not started:** schema, test sets, extraction, evals, code.

## 2. Next session (Day 2)

1. Claude proposes the passage and tag schema, with 2–3 options and a recommendation.
2. Claude proposes the per-source cap for the GRAY Sivananda Gita.
3. Shailesh chooses; the decision goes in `docs/Decisions.md`.

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
