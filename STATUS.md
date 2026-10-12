# Status

*Updated at the end of every session. Last update: Sun 12 Oct 2026, ~18:00 IST (session 8: clean history on a new repo, old commits 404, viv04-031-p02 hidden from distress).*

## 1. Where we are

- **Plan days done:** 1–15, and Day 16 in part (`logs/D16.md`, sessions 6–8). Phase 1 closed 9 Oct (`logs/Phase-1-Report.md`); Day 15 (new sources, enrichment pass, plain-version judge) done 11–12 Oct, 10 days ahead of plan (`logs/D15.md`).
- **Done:**
  - Days 0–1: setup, repo, accounts, free-tier limits.
  - Day 2: tag schema and taxonomy v2; source on/off switch; harm review narrowed to a safety field (Decision 3).
  - Day 3: both test sets in `evals/`: human (32 held-out, 5 crisis, 5 look-alikes) and agent (60 golden, 20 held-out, 8 crisis, 8 look-alikes).
  - Day 4: 33 sources normalised (4.18M words); extraction harness; pilot on Sonnet and Opus.
  - Day 5: Shailesh's blind review of 40 passages: 38 kept (95%); 2 cut by override, 2 display fixes.
  - Day 6: pilot tagged on both models; model Opus 5.5 at medium effort; prompts locked (v1).
  - Days 7–11 (`logs/D07.md`): all 33 sources extracted and tagged; 5,029 passages, 99.86% verbatim.
  - Days 12–14 (`logs/D12.md`): deduplication, display clean-ups, statistics; corpus v1 frozen (Decision, 9 Oct).
  - Day 15 (`logs/D15.md`): six Tagore and Gibran works licence-checked, fetched, extracted and tagged (613 passages; the Gracián dropped, no clean text). **5,540 passages can be shown across 39 sources.** Every shown passage enriched (plain version, core idea, quotability, completeness, display fixes) and every plain version AI-judged: 98.1% scored 4 or 5 of 5.
  - Day 16, part (`logs/D16.md`): the 103 plain versions judged 3 or lower rewritten to keep the conclusion; blind side-by-side re-judge: new 95 fives, 8 fours, 0 at 3 or lower. Six suicide-naming passages confirmed hidden from distress. 28 of 34 AI letter fixes confirmed against a second copy and kept, 6 reverted; all 54 punctuation fixes kept.
  - Repo prepared to go public (12 Oct): private archive `stainwal/WhoLLsoMe-archive`; the three restricted sources (Way of Perfection, Brother Lawrence, Sivananda Gita) and `evals/agent-set-provenance.md` out of git and out of history, still on disk (`pipeline/restricted.py`, pre-commit hook); history rewritten and force-pushed; gitleaks clean; README committed. **`stainwal/WhoLLsoMe` is still private.**
  - Public prep, session 7 (12 Oct, `logs/D16.md` second entry): `LICENSE` MIT and README licence note; the 13 crisis statements moved to git-ignored `evals/private/crisis.jsonl` (read via `evals/sets.py`), purged from history, blocked by the pre-commit hook, force-pushed; two print-confirmed corrections applied as overrides. History scan: 21 commits, 6,429 file versions, 0 crisis text, 0 restricted text, gitleaks clean. **Still private; one blocker: GitHub still serves the replaced commits by SHA** (section 3).
  - Session 8 (12 Oct, `logs/D16.md` third entry): old repo renamed `stainwal/WhoLLsoMe-old` (private, keep private for good); clean `main` (23 commits, head `cf19ba5`) pushed alone to a new `stainwal/WhoLLsoMe`; **`d4c50ae` and `d2eb907` return 404 there**. Pre-push scan of 6,432 file versions: 0 restricted, 0 crisis; gitleaks clean. Showcase item 2 cleared: **no checklist item blocks the repo; it stays private** pending the timing decision. viv04-031-p02 hidden from distress (63 hidden in all).
- **Not started:** retrieval (rest of Day 16 on), app code.

## 2. Next session

1. **Shailesh:** push the pre-purge backup to `WhoLLsoMe-archive` (blocked for Claude; command in the session 8 report); the decisions in section 3.
2. **Day 16, rest, Claude:** create the Supabase project; load the 5,540 passages with plain versions, quotability and tags; baseline embeddings.
3. **Before the visibility switch:** re-run the history scan and gitleaks if more commits land.
4. **Day 17:** eval harness, reading the sets through `evals/sets.py`; AI judge labels acceptable passages for both test sets; Shailesh spot-checks 8 human statements; baseline scores.

## 3. Open decisions

| Day | Decision | Where |
| --- | --- | --- |
| 16 | Embeddings option: hosted API vs a free model | Plan section 5.3 |
| 16 | When to make `stainwal/WhoLLsoMe` public: A at launch, as Showcase section 6 plans (recommended), B now | `logs/D16.md` session 8, section 4 |
| 27 | Name, look, domain | — |

## 4. Eval results

- **Plain-version rewrite (Day 16, `logs/D16.md`):** the 103 judged ≤ 3 rewritten. Blind side-by-side judge on the same 103: old mean 3.86 (21 at ≤ 3), new mean 4.92 (95 fives, 8 fours, 0 at ≤ 3). Corpus now 4,763 fives, 777 fours: **100% at 4 or 5**, mean 4.86. The judge drifts between days (Day 15 gave the same old versions a mean of 2.92).
- **Display fixes (Day 16):** 82 applied (28 letter fixes confirmed against a printed edition or independent transcription, 54 punctuation); 6 reverted (`evals/letter-fix-check.json`).
- **Plain-version faithfulness (Day 15, `logs/D15.md`):** 5,540 of 5,540 plain versions judged by Opus 5.5 in a separate pass. Score 5: 4,668 (84.3%); 4: 769; 3: 96; 2: 6; 1: 1. **98.1% at 4 or 5**, mean 4.82, 0 flagged for adding advice. The judge is the writer's model family and is sensitive to its wording (0 vs 17 threes on the same 200 items with and without "be exacting"); the 10 weakest go to Shailesh on Day 16.
- **Enrichment (Day 15):** quotability 1/2/3/4/5 = 48 / 1,137 / 2,415 / 1,405 / 535; Surprise-me pool (4–5, keep) 1,929. 28 passages extended verbatim for completeness; 88 display fixes accepted, 26 rejected by the checks (`corpus/passages/bulk/enrich-report.md`).
- **New sources (Day 15):** 613 passages, 613 verbatim, 0 tag problems. Sand and Foam 252 and Stray Birds 149 passages, median 15–19 words, about 75% secular.
- **Corpus now (`corpus/passages/stats.md`, 12 Oct):** 5,477 keep, 63 no-distress, 5,540 shown.
- **Corpus after Day 15:** 5,642 extracted; 5,484 keep, 56 no-distress, 18 cut, 84 dup; **5,540 shown**. Median 51 words. Secular 52%. All 37 themes used.
- **Corpus after dedup (Days 12–13):** 5,029 extracted; 4,882 keep, 47 no-distress, 16 cut, 84 dup; 4,929 shown. Median 53 words. Secular 51%. "Losing a pet" was the one situation with no passage.
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
- A source for pet loss, breakup and partnership (corpus gap found on Day 13; Phase 2 sources)
- Re-run of the `<j>`-skipped SuttaCentral chunks and the three early-filtered helper packs (declined 8 Oct; listed in case the freeze is extended)
- Gracián, *The Art of Worldly Wisdom* (Jacobs 1892): public domain but only OCR scans exist; needs a clean transcription before it can be added (dropped 11 Oct)
- A second, independent judge model for the plain versions (the Day 15 judge is the writer's own model family)

## 6. Token budget

Used by `CLAUDE.md` section 4.3 for every heavy run.

- **Calibration (measured on the full run, 7–8 Oct):**
  - **Cost:** about 0.5% of the weekly limit per 100,000 words for extraction and tagging together. The full run took 4.10M words and moved weekly from 46% to 66%.
  - **5-hour window:** about 3% per 100,000 words, so one window holds about 3M words. On a big run this is the binding limit.
  - **Ratio:** session % ≈ 6 × weekly %.
  - **Superseded:** the Day 4 estimate (1.4% per 100k words for extraction alone) was about 3 times too high.
  - **Readings:** Claude reads both bars through the app's usage API, so no screenshots are needed.
- **Enrichment and judge (Day 15, measured):** about **9% of the weekly limit** for one pass over 5,540 passages (plain version plus judge) together with 75k words of extraction and tagging: roughly 1.5% per 1,000 passages enriched and judged. The 5-hour window moved about 35 points over the run, so one window holds a pass of this size with room to spare.
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
  | Day 15 start, 11 Oct 22:21 | 15% | 22% |
  | Day 15 midpoint, 23:17 | 13% (new window) | 26% |
  | Day 15 run complete, 12 Oct 00:52 | 48% | 32% |
  | Day 16 start, 12 Oct ~14:20 | 4% | 33% |
  | Day 16 close, 15:25 | 8% | 34% |
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
| Use | Non-commercial only. Ads, payments or a paid collaborator make it commercial | Fine for a personal, non-commercial project; Pro is $20/month if that changes |
| Function invocations | 1,000,000 per month | Ample |
| Active CPU / memory | 4 CPU-hours / 360 GB-hours per month | Ample: our functions mostly wait on API calls |
| Function duration | 300 s (Fluid compute, the default) | Ample |
| Data transfer | 100 GB per month Fast Data Transfer; 1,000,000 CDN requests | Ample |
| Builds | 100 deployments per day, 45 min per build | Ample |
| **Over a limit** | That feature pauses for about 30 days; no overage charges, no spend controls on Hobby | Rate limit + Turnstile protect this |

### 7.3 Cloudflare Turnstile (Free)

Unlimited verifications, 20 widgets, 10 hostnames per widget. No concerns.
