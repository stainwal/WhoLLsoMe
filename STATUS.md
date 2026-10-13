# Status

*Updated at the end of every session. Last update: Tue 13 Oct 2026, ~21:30 IST (session 11: Day 17 closed; Days 18–19 experiments done; retrieval setup decision waiting).*

## 1. Where we are

- **Plan days done:** 1–19 (`logs/D18.md`, session 11). Days 18–19 finished on 13 Oct, 9 days ahead of plan. Phase 1 closed 9 Oct (`logs/Phase-1-Report.md`); Day 15 (new sources, enrichment pass, plain-version judge) done 11–12 Oct, 10 days ahead of plan (`logs/D15.md`).
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
  - Session 9 (12 Oct, `logs/D16.md` fourth entry): name spelled WhoLLsoMe everywhere; GitHub description and topics; README as a personal project; `docs/Showcase.md` cut to `docs/Publication-Checklist.md` (case-study material in the private archive); both scanners recurse into folders (`pipeline/test_scanners.py`). **Supabase loaded:** pgvector 0.8.2, 39 sources, 5,540 passages (0 differ from files), RLS on, 47 MB. **Baseline embeddings:** Voyage `voyage-4-lite`, 1024 dims, passage text + plain version, 5,540 vectors, 603,619 tokens, $0 (free allowance). **`stainwal/WhoLLsoMe` is public** (Shailesh).
  - Session 10 (13 Oct, `logs/D17.md`): `public_passages` view, the only thing the public key can read (16 of 16 checks, database and REST API); deny rules for hook-bypassing git commands; pause plan in section 7.1. Eval harness `evals/retrieval.py`; 3,074 pooled pairs AI-judged; baseline scored (section 4); 10% consistency re-judge.
  - Session 11 (13 Oct, `logs/D18.md`): spot check 7 of 8, labels stand; 5 harsh passages hidden from distress (68 in all); top-1 metrics; commits pushed through `6b8df0b`; Opus vs Fable cross-check; 24 retrieval setups scored, every top 10 judged (6,610 labels).
- **Not started:** Explain and experiment 5 (Day 20), app code.

## 2. Next session

1. **Shailesh:** the three decisions in section 3 (retrieval setup; judge prompt v2; dropping unused embeddings). And create the Anthropic API account (prepaid, hard spend cap) for Day 20.
2. **Day 20, Claude:** Explain prompt, rubric and judge; experiment 5 (Haiku vs Sonnet), including runtime query rewrites compared with `evals/rewrites/opus-v1.json`; Shailesh spot-checks 5 explanations.
3. **Every push publishes** (the repo is public): the pre-commit hook guards restricted and crisis text; re-run gitleaks before the site launch. Session 11's close commit is **not pushed**.
4. **App, when built:** read passages through `public_passages` only; `SUPABASE_URL` and the publishable key are in `.env`.

## 3. Open decisions

| Day | Decision | Where |
| --- | --- | --- |
| 19 | Retrieval setup: A `when+tone/0.1` (no runtime model call), B A + query rewriting if Haiku matches on Day 20, C baseline. Recommend A now, test B | `logs/D18.md` section 4 |
| 19 | Judge prompt v2: no credit for a passage that only restates the problem (Shailesh's H03 disagreement); re-judge the chosen setup before the gate. Recommend yes | `logs/D18.md` section 4 |
| 19 | Drop the 3 unused embedding setups (174 → about 100 MB) once the setup is chosen | `logs/D18.md` section 4 |
| 27 | Name, look, domain | — |

## 4. Eval results

- **Experiments (Days 18–19, `evals/results/experiments-d18.md`):** each value is top-1 acceptable / top-1 graded 0 / hit@3. Baseline after the hides: golden 31 / 11 / 50, agent held-out 9 / 4 / 12, human held-out 21 / 4 / 29. **`when+tone/0.1`** (embed passage + plain + when-helps; tone prior): 37 / 6 / 53; 11 / 5 / 16; **23 / 2 / 30**. **`when+rewrite-concat+tone/0.2`** (needs a runtime rewrite): 39 / 5 / 52; 11 / 1 / 18; 19 / 1 / 29. Hybrid search hurts (golden 21 / 18 / 39); quotability, faith framing and `voyage-4` don't help.
- **Opus vs Fable (Day 18, `evals/judge-cross-model.md`):** 375 baseline top-3 pairs. Acceptable/not agreement: human 83.8%, agent 85.6%; exact grade 59.5% and 61.7%. Fable is more lenient, especially on tone: top-1 graded 0 is 12 of 125 under Fable and 26 under Opus. hit@3 is about the same (105 vs 103 of 125). Opus stays the judge of record.
- **Spot check (Day 17):** Shailesh agreed with 7 of 8; the labels stand.
- **Top-1 metrics, Day 17 baseline:** human held-out top-1 acceptable 19 of 32 (59%), graded 0 6 (19%).
- **Baseline retrieval (Day 17, `logs/D17.md`):** `voyage-4-lite/text+plain`, AI-judged pooled labels (3,074 pairs, 24% acceptable). **Human held-out hit@3 29 of 32 (91%)**, hit@10 100%, MRR 0.755. Agent held-out hit@3 12 of 20 (60%), hit@10 85%, MRR 0.557. Agent golden hit@3 83%. Look-alikes: human 5 of 5, agent 7 of 8. Keyword search alone: human held-out 44%. 26 of 125 statements would open on a passage graded 0. Labels stand only if Shailesh agrees with 6 of 8 spot-check items.
- **Judge consistency (Day 17):** 307 pairs (10%) re-judged blind: exact grade 70.4%, within one grade 100%, acceptable/not 88.6% (kappa 0.70); the second pass slightly more lenient (28% vs 23% acceptable).
- **Baseline embeddings (Day 16, `logs/D16.md` session 9):** `voyage-4-lite/text+plain`, 5,540 of 5,540 embedded. No eval scores yet (Day 17). Two sample searches: a comparison-with-friends statement gets three well-matched Seneca and Schopenhauer passages; a layoff statement gets Job and Jeremiah on shame and abandonment, not work.
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
- A second judge model for retrieval labels (Day 17 used one model, checked against itself and by Shailesh's spot check)

## 6. Token budget

Used by `CLAUDE.md` section 4.3 for every heavy run.

- **Calibration (measured on the full run, 7–8 Oct):**
  - **Cost:** about 0.5% of the weekly limit per 100,000 words for extraction and tagging together. The full run took 4.10M words and moved weekly from 46% to 66%.
  - **5-hour window:** about 3% per 100,000 words, so one window holds about 3M words. On a big run this is the binding limit.
  - **Ratio:** session % ≈ 6 × weekly %.
  - **Superseded:** the Day 4 estimate (1.4% per 100k words for extraction alone) was about 3 times too high.
  - **Readings:** Claude reads both bars through the app's usage API, so no screenshots are needed.
- **Enrichment and judge (Day 15, measured):** about **9% of the weekly limit** for one pass over 5,540 passages (plain version plus judge) together with 75k words of extraction and tagging: roughly 1.5% per 1,000 passages enriched and judged. The 5-hour window moved about 35 points over the run, so one window holds a pass of this size with room to spare.
- **Relevance judging (Day 17, measured):** 3,074 + 307 judgements took about **2% of the weekly limit** (cap agreed 10%, estimate 2–4%): about 0.6% per 1,000 judgements, 8 + 2 helpers of about 170k tokens each, mostly cached.
- **Experiments (Days 18–19, measured):** 3,536 judgements, 125 rewrites and Fable's 375 took about **3% of the weekly limit** (cap agreed 15%): about 0.8% per 1,000 judgements. Fable has its own weekly bar (moved 2 points).
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
  | Day 17 start, 13 Oct ~16:00 | 2% | 39% |
  | Day 17 judge run done | 9% (new window) | 41% |
  | Day 17 re-judge done, ~19:25 | 10% | 41% |
  | Session 11 start | 11% | 41% (Fable 45%) |
  | After Fable check, experiment round 1 | 19% | 42% (Fable 47%) |
  | Session 11 close | 27% | 44% (Fable 47%) |
- **One-time full reset:** available on the Usage screen ("Reset for free"), expires 22 Oct. Not needed for the corpus run, which fit in one week's allowance. Use only with Shailesh's say-so.

## 7. Free-tier limits

Checked 7 Oct 2026 on the official pricing and docs pages. Check again before launch (Day 32).

### 7.1 Supabase (Free)

| Limit | Value | What it means for us |
| --- | --- | --- |
| Projects | 2 per organisation (paused projects don't count) | One is enough |
| Database | 500 MB per project | **13 Oct:** 174 MB with 6 embedding setups (about 25 MB each); drop the unused ones once the setup is chosen |
| Storage / egress | 1 GB / 5 GB per month | Fine at hobby scale |
| Edge functions | 500,000 invocations per month | Not used; the API runs on Vercel |
| pgvector | Can be enabled (Dashboard → Database → Extensions). The docs don't say it's paid-only | **Confirmed 12 Oct:** pgvector 0.8.2 enabled on the free plan |
| **Inactivity pause** | Paused after about 7 days of low activity. Data is kept; resume from the dashboard. Treat the restore window as 90 days (docs say 1 year, changelog says 90) | **Plan (13 Oct):** until launch, every eval run queries the database, so it stays awake while we work; after a gap of 7+ days, Shailesh resumes it from the dashboard (a minute; nothing lost). **At launch (Day 31–32):** a daily Vercel cron job calls a small `/api/health` route that runs one read query, which keeps the project active; launch checklist item. If a pause still happens, the app shows a friendly "resting, back soon" screen, not an error |
| **Backups** | None on Free | Keep our own `supabase db dump` exports, but **not in this repo**: it is public and the database holds the 147 restricted passages. Dumps go to a git-ignored folder or the private archive. The files in `corpus/passages/` can rebuild the database anyway (`backend/load.py`, `backend/embed.py`) |

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
