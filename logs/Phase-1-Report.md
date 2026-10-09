# Phase 1 Report — Corpus

*Written Fri 9 Oct 2026 at the Day 14 stop (planned for 21 Oct; reached 12 days early). For the corpus-freeze decision in Section 6.*

## 1. What was built

- **33 sources, 4,096,568 words read** (after normalisation and the Bible pre-filter), extracted and tagged by Opus 5.5 helpers in one overnight run (7–8 Oct), then deduplicated and cleaned for display (9 Oct).
- **5,029 passages** passed the verbatim check. After the safety field and deduplication, **4,929 can be shown**: 4,882 shown normally and 47 kept but hidden from anyone in distress. 16 are cut, 84 are duplicates.
- **Every passage carries:** verbatim `text`, a `display_text` with file apparatus removed, its source, exact location (`display`, `start_uid`–`end_uid`), translator credit (via `docs/Corpus-Policy.md` section 2), 1–3 feelings, 1–3 themes, 0–3 situations, 1–2 tones, a faith framing, a safety value with reason, up to 3 keywords and a one-line "when this helps".
- **Pipeline** (`pipeline/`): `normalise/` → `bulk.py prep` (chunking and pre-filter) → extraction helpers → `bulk.py check` (verbatim) → tagging helpers → `dedup.py` → `bulk.py merge` (per-source files, overrides, cut list) → `stats.py`. Every step is a script that re-runs from saved state; nothing in the corpus was edited by hand.
- **Human controls:** `corpus/passages/bulk/overrides.json` (4 entries: two "hide from distress", two display corrections), `cuts.md` (every cut and hidden passage with its reason), `duplicates.json`.

## 2. Numbers

### 2.1 Extraction and tagging

| Check | Result |
| --- | --- |
| Verbatim match against the source | 5,029 of 5,036 exact (99.86%); 7 rejected and logged, none repaired |
| Tag validity (every tag in the taxonomy, counts within limits) | 0 problems in 5,029 passages |
| Safety field | 16 cut (12 Seneca "open door", 2 likely over-cuts, 2 group-hatred); 45 `welcomes-death` hidden from distress; 2 more hidden by decision (MN 144, Walden) |
| Pilot, Sonnet vs Opus on the same text (D04/D06) | both 100% verbatim; Opus picked 86 passages to Sonnet's 49; same top tag on themes 87%, tone 79%, feelings 57%, situations 55%, safety 100% |
| Cost | 20% of one week's subscription allowance for the full run, against 57% predicted |

### 2.2 Corpus shape (shown passages; full tables in `corpus/passages/stats.md`)

| Measure | Value |
| --- | --- |
| Shown passages | 4,929 (300,216 words) |
| Length, words: median / mean / range | 53 / 61 / 5–322; 20 under 10 words, 4 over 250 |
| Yield | 1.20 passages per 1,000 words read; from 0.51 (Nikayas) to 3.81 (Enchiridion) |
| Faith framing | secular 51%, spiritual 25%, devotional 24% |
| Largest sources | Bible 987 (20%), Vivekananda 763 (15%), SuttaCentral 666 (14%), Seneca 467 (9%), Emerson 257 (5%) |
| Smallest sources | Plato Apology 10, Japji 11, Upanishads 15, Phaedo 16, Eastman 18 |
| Themes | all 37 in use; top: faith and the sacred 19%, wisdom and understanding 12%, character and growth 12%; bottom: beauty 1%, solitude 2%, nature 2%, family 2% |
| Situations | 56 of 57 in use; **"losing a pet" has 0 passages**; 14% of passages have no situation tag |
| Tone | contemplative 28%, challenging 26%, practical 26%; consoling 13%, companioning 9%; stern 7% |

### 2.3 Deduplication (Days 12–13)

| Band | Rule | Passages |
| --- | --- | --- |
| Exact repeat | keep the earliest in its source | 44 marked `dup` |
| Contained (one passage wholly inside another) | keep the longer | 34 marked `dup` |
| Near-identical (word 8-gram Jaccard ≥ 0.8; stock formulae with a name swapped) | keep the earliest | 6 marked `dup` |
| Related (Jaccard 0.5–0.8) | both kept, same `near_group`; search never shows two from one group | 43 passages in 18 groups |

83 of the 84 duplicates are in SuttaCentral (the Nikayas repeat stock passages across suttas); 1 is in Vivekananda. No duplicate crosses a source: the two Gita translations and the two Epictetus translators are worded differently, so they fall to the search-time filter as the policy intends (Corpus-Policy section 4, rule 6).

### 2.4 Display clean-ups (verbatim `text` untouched)

| Apparatus removed from `display_text` | Passages |
| --- | --- |
| SuttaCentral `<j>` verse indents (decided 8 Oct) | 1 |
| Gutenberg `_italics_` underscores | 58 |
| Quotation mark whose partner lies outside the passage | 257 (40 remain where speech opens mid-passage; they read fine) |
| Lower-case first letter after a cut at a colon (Pirkei Avot) | 2 |
| Scan errors corrected by override (Japji "T have", "2 commotion"; Upanishads "wide- spread") | 2 |

## 3. Known weaknesses

1. **Extraction precision is unmeasured.** The Day 5 blind review has not happened. A 40-passage random sample is ready in `evals/keep-cut-sample.md`; Shailesh's keep count gives the precision figure (each cut is 2.5 points).
2. **Coverage gaps against the test sets.** "Losing a pet" has no passage, and two test statements are about a dog dying (H07, AS02); retrieval will have to reach them through grief and loss passages. Love and partnership is thin: 156 passages, with 1 on a partner's infidelity and 20 on breakup, against 3 human and 8 agent statements in that area. Good news has 37 passages against 2 human and 8 agent statements.
3. **Religious weight.** "Faith and the sacred" is the most common theme and nearly half the corpus is spiritual or devotional. A secular user must not be handed a prayer first; the faith-framing signal exists for ranking but is untested until Phase 2.
4. **Two sources are not public domain.** Brother Lawrence (Lightheart 2002 edition, 21 passages) and *Way of Perfection* (Peers, 77 passages) are kept on Shailesh's call; Sivananda's Gita (49) is Tier B GRAY. Together 147 passages (3%). Switching any off in `pipeline/sources.toml` removes it without a re-run.
5. **Text left unread or unrecovered, by decision (8 Oct):** Leviticus, Numbers and 1 Chronicles (73,189 words, pre-filtered); SuttaCentral verses skipped by one helper because of `<j>` markup; passages that three early helpers filtered out on their own judgement (Meditations, As a Man Thinketh, Pirkei Avot); 7 verbatim rejects; 3 likely over-cuts.
6. **The Nikayas yield little and repeat.** 1.29M words gave 666 shown passages (0.51 per 1,000) and 83 duplicates. Fine for v1; not worth extending.
7. **Length outliers.** 20 passages under 10 words (mostly one-line proverbs and Bible verses; they read as complete) and 4 over 250 words (policy says about 1–8 sentences). The sample review will show whether either end should be trimmed by rule.
8. **Safety relies on one tagging pass.** No human has sampled passages tagged `none` for safe-messaging problems; the Day 5 sample doubles as a spot check. The crisis test sets (13 statements) test the app's crisis check, not the corpus.
9. **Tag agreement is modest on feelings and situations** (57% and 55% same top tag between two models on the pilot). Themes (87%) and safety (100%) are solid. Evals in Phase 2 decide whether feelings and situations are worth embedding.

## 4. What the freeze means

A frozen corpus is the 33 per-source files in `corpus/passages/` as of commit `D12–13` plus any overrides Shailesh adds from the Day 5 review. Phase 2 loads these files into Supabase and tunes retrieval against them. Changes after the freeze are limited to per-passage overrides (hide, restore, display fix); no re-extraction and no new sources until after launch (Plan section 5.6, item 2).

## 5. Recommendation

**Freeze now (option A below).** The corpus is complete, verbatim, tagged without validity errors, deduplicated and large enough that the known gaps are retrieval problems, not extraction problems. The one open measurement, extraction precision, does not need the pipeline re-run to act on: a low score would be fixed by rules applied at load time (length limits, a per-source cap) or by overrides. The three days the plan allows for extension are better spent on Phase 2, which is the critical path to the Day 21 gate.

Condition: if the Day 5 review finds fewer than 34 keeps in 40 (precision under 85%), reopen the freeze and take option B.

## 6. [DECISION] Corpus freeze v1

| Option | What happens | Cost |
| --- | --- | --- |
| **A. Accept the freeze now** (recommended) | `corpus/passages/` as committed is v1. Day 5 review still happens; its result goes in the Phase 2 report as the precision figure, and any passages Shailesh cuts become overrides | 0 days |
| B. Extend up to 3 days | Re-run the `<j>`-affected SuttaCentral chunks and the three early-filtered helper packs; read Leviticus, Numbers and 1 Chronicles; restore the 3 likely over-cuts. Then freeze | 1–3 sessions; about 2% of a week's allowance; recovers perhaps 50–100 passages, none in the gap areas |
| C. Extend to close the coverage gaps | Add a Phase 2 source aimed at love, breakup and pet loss (none is acquired or cleared for licence yet) | More than 3 days; off-plan |
