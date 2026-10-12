# WhoLLsoMe v1 — Web Launch Plan

*Created 7 Oct 2026. Replaces the earlier iOS-first and Android-first plans. Day 1 = Thu 8 Oct 2026, one 1-hour session per day. **Revised 11 Oct:** plain-language versions, Explain and Surprise me added; an enrichment pass and seven aphoristic sources added to Phase 2; human review cut to small targeted checks; speed to release first.*

The web app goes public on **Day 33 (Mon 9 Nov 2026)** with all 33 sources, a crisis-safe flow and a published eval page. Android follows, recruiting its closed-test testers from web users.

## 1. Outcome and dates

| Milestone | Day | Date |
| --- | --- | --- |
| Setup done; golden set statements written | 3 | Sat 10 Oct |
| Extraction rules proven on a pilot | 6 | Tue 13 Oct |
| Corpus frozen (all 33 sources extracted, tagged, reviewed) — done 9 Oct | 14 | Wed 21 Oct |
| Enrichment pass and new sources | 15 | Thu 22 Oct |
| Retrieval gate passed | 21 | Wed 28 Oct |
| Working web app with friends testing | 29 | Thu 5 Nov |
| **Public web launch** | **33** | **Mon 9 Nov** |
| Android live (after its 14-day closed test) | — | early Dec (estimate) |

Your time goes mostly on decisions and a few 10-minute checks; Claude runs the rest. A missed day moves everything right by one day; the corpus freeze (Day 14) and the retrieval gate (Day 21) are the two planned stops to reassess.

## 2. v1 scope (the build contract)

### 2.1 In

1. **Input:** one text box. Phone keyboards' voice typing covers "speak"; no speech-to-text code.
2. **Output, one passage at a time:** the passage's plain-language version first (labelled "In plain words"), the verbatim passage beside it, and its source and translator. "Next" steps through the 10 best fits in ranked order; "Back" returns to earlier ones. Near-identical passages (e.g. two Gita translations of one verse, adjacent verses) never both appear in the 10.
3. **Explain:** a button under each passage generates, on request, a short explanation of how the passage applies to what the user wrote. It replaces the always-on bridging sentence (decided 11 Oct), so nothing is generated unless asked.
4. **Surprise me:** a button on the home screen shows a random passage with no input. Drawn only from high-quotability passages (enrichment score 4–5), never from those hidden from distress. No AI call.
5. **Save:** favourites kept in the browser. No accounts.
6. **Safety:** crisis check on every input (risk of harm to self or to others) → one crisis screen with helplines; "Need help now?" always visible; "Report this response" on every result.
7. **Consent:** a first-visit notice that input is sent to an AI provider, with explicit opt-in.
8. **Pages:** About (all sources and translators, not-therapy statement), Privacy, Evals (published results).
9. **Corpus:** all 33 sources in `corpus/source/` plus the aphoristic additions that clear their licence check (Corpus-Policy section 2.2), extracted selectively and enriched (plain version, quotability, completeness, text fixes) per `docs/Corpus-Policy.md`.
10. **Ranking:** relevance first; among close matches, short and immediately graspable passages (higher quotability) rank higher.

### 2.2 Later (parking list, not v1)

Read-aloud, share-as-image, daily passage, accounts, journaling, streaks, mood tracking, analytics beyond basic counts, Phase 2 sources, Android (after launch), iOS (after Android).

## 3. Stack and cost

| Layer | Pick | Cost |
| --- | --- | --- |
| Web app | Next.js (React, TypeScript) | Free |
| Hosting | Vercel, on your existing account (Hobby plan: personal, non-commercial use only; Pro is $20/month if it's ever monetised) | Free |
| Bot protection | Cloudflare Turnstile on the input (works on any host; needs only a free Cloudflare account, D26) | Free |
| API | Next.js API routes on Vercel; they hold the API keys and call the database and models | Free |
| Database | Supabase: Postgres + pgvector | Free tier |
| Crisis check, passage choice, Explain (runtime, for public users) | Claude Haiku via the Anthropic API (Sonnet as an eval comparison); a subscription can't serve a public app | Cents/month at hobby scale (estimate) |
| Embeddings (passages once, each user query at runtime) | Hosted embeddings API, or a free model if evals show it's good enough; Anthropic offers no embeddings model | Negligible to $0 (estimate) |
| Extraction, tagging and enrichment | Claude Code on your subscription | $0 extra |
| Domain | Optional custom domain | ~$10–15/year (estimate) [DECISION] |

Hard monthly spend cap on every API key from Day 1. Free-tier limits (Supabase inactivity pauses, Vercel Hobby usage caps) are checked by Claude Code on Day 1, not assumed.

## 4. Evals

Evals are a workstream, not a final check. They prove the app works, and the published results are part of the resume story.

### 4.1 Test sets

Two independent sets of the same shape, scored separately and never pooled (decided 8 Oct).

| Set | Written by | How |
| --- | --- | --- |
| Human set | Shailesh, from personal intuition | `../Test-Statements-Human.md`, written before reading any agent list |
| Agent set | Several models in fresh sessions, each researching real public posts where people ask for guidance or support | Each model returns paraphrased statements (no names, places or identifying detail); the Cowork reviewer compiles them: removes duplicates, flags problems, checks sources, picks for coverage |

| Part | Human set | Agent set | Used for |
| --- | --- | --- | --- |
| Golden | — | ~60 statements | Tuning: every change is scored against it |
| Held-out | 32 statements (all of Shailesh's) | ~20 statements | Reporting only; never used for tuning |
| Crisis | 5 statements | 5–8 statements | Must route to helplines, every one |
| Crisis look-alikes | 5 statements | 5–8 statements | Must *not* trigger the crisis screen |

- **Headline number:** the human held-out set (32). The gate (section 5.3) is judged on it; agent-set scores are reported beside it. At 32 statements each one moves the score by about 3 points, so gaps under about 7 points are noise.
- **Borderline statements** (marked `[borderline]`, e.g. relapse with hopelessness): either the crisis screen or a gentle "Need help now?" link counts as correct; the passage is still scored.
- **Agent split:** the compiled agent statements are divided into golden and held-out at random.
- **Final files:** compiled sets go to `evals/`. Source links from the agent research stay private and never ship.
- **Labelling (Day 17, revised 11 Oct for speed):** acceptable passages are labelled by pooling: the top candidates from several retrieval setups. An AI judge labels both sets. Shailesh spot-checks the judge on 8 human statements; if he agrees with at least 6 of 8, the judge's labels stand. The Evals page says labels are AI-judged with a human spot-check.

### 4.2 Retrieval metrics

- **Hit@3:** share of statements with an acceptable passage in the top 3.
- **Hit@10:** share with an acceptable passage anywhere in the 10 a user can step through.
- **MRR:** how high the first acceptable passage ranks.
- **Crisis recall** and **false crisis rate.**
- **Cost per 1,000 queries** and **response time.**

### 4.3 Generated-text evals

- **Plain versions (offline):** an AI judge checks every plain version against its passage for faithfulness (same core idea, nothing added, no doctrine invented). Shailesh reads only the 10 it rates least faithful and fixes or hides them.
- **Explain (runtime):** a rubric: true to the passage, relevant to what the user wrote, no advice or therapy language, no claims about the user beyond what they said, short. A stronger model grades every output; Shailesh spot-checks 5.

### 4.4 Experiments (one change at a time)

1. Embedding model (2–3 candidates).
2. What gets embedded: passage text / text + tags / "when this helps" line / the plain version (likely closest to how users write).
3. Query rewriting: turn the user's words into themes before searching.
4. Hybrid search: meaning-based plus keyword.
5. Haiku vs Sonnet for choosing the passage and writing Explain.
6. Faith-framing in ranking: does down-ranking devotional passages for statements that show no faith lift results for secular users? (Added 9 Oct: about half the corpus is spiritual or devotional.)
7. Quotability boost: does favouring short, graspable passages among close matches lift results? (Added 11 Oct.)

Tuning runs on the agent golden set (60); results are reported on both held-out sets. On 20–32 statements, a gap of 1–2 hits is noise; only gaps of several points are claimed.

### 4.5 Published results

An Evals page on the site: one row per setup with hit@3 (held-out), crisis results, plain-version faithfulness, Explain rubric pass rate, cost and speed, plus a few lines on what was learned.

## 5. Phases and days

### 5.1 Phase 0 — Setup (Days 1–3, 8–10 Oct)

- [x] **D1:** Open Claude Code in `Version1_QuickLaunch`. Git repo + private GitHub repo. Accounts: Supabase (new); Vercel (existing). Claude checks free-tier limits. (Offline corpus work runs on your Claude subscription; the paid API accounts wait until they're needed, D15 and D20.)
- [x] **D2:** [DECISION] Passage and tag schema; per-source cap for the GRAY Sivananda Gita. Claude proposes, you choose.
- [x] **D3:** Test sets (section 4.1): Shailesh writes the human set; several models research the agent set; the Cowork reviewer compiles it into `evals/`. [DECISION] Gate thresholds (section 5.3).

Exit: accounts live, schema agreed, 70 test statements written.

### 5.2 Phase 1 — Corpus (Days 4–14, 11–21 Oct)

- [x] **D4:** Normalise all 33 sources (Corpus-Policy section 7, step 1). Pilot extraction and verbatim check on one short, structured source (Dhammapada) and one dense one (a Vivekananda lecture). First heavy run: Claude walks you through the `/usage` readings and records the token calibration (CLAUDE.md section 4.3).
- [x] **D5:** You judge pilot passages keep/cut; extraction rules adjusted. No longer gates the model choice: it now checks the quality of Opus picks and can run alongside the bulk run.
- [x] **D6:** Pilot tagging with the safety field (Decision 3); the same chunks run through Sonnet and Opus. Model for bulk work: **Opus 5.5** (decided 7 Oct). Rules locked.
- [x] **D7–11:** Full run across all 33 sources, parallel and unattended, highest-yield sources first (Gita, Dhammapada, Psalms/Proverbs/Ecclesiastes, Meditations, Enchiridion, Tao Te Ching, The Prophet, Pirkei Avot, Rumi), bulk sources last (rest of the Bible, Nikayas, Vivekananda, Seneca). Each session: Claude proposes that day's batch and token budget; you scan that day's cut list (Corpus-Policy section 6). Sources with open questions (Rumi headings, the Zitkala-Ša quoted report, *Way of Perfection*, *Brother Lawrence*) run last.
- [x] **D12–13:** Deduplicate, check consistency, corpus statistics by source and theme.
- [x] **D14:** Corpus freeze v1. `logs/Phase-1-Report.md`. [DECISION] Accept, or extend by up to 3 days.

Exit: every passage extracted, tagged and harm-reviewed per `docs/Corpus-Policy.md`.

### 5.3 Phase 2 — Enrichment, retrieval and evals (Days 15–21, 22–28 Oct)

- [x] **D15:** Enrichment pass, unattended under a token budget (Corpus-Policy section 7, step 7): plain version, quotability 1–5, completeness flag with verbatim extension, text-error fixes for display, core idea in 10 words or fewer. New sources: licence check, then extract, tag and enrich the aphoristic additions (Corpus-Policy section 2.2). The AI judge checks every plain version.
- [ ] **D16:** You (~10 min): read the 10 plain versions the judge rated least faithful; fix or hide. [DECISION] Embeddings option (hosted API vs a free model). Create the Supabase project; load passages; baseline embeddings.
- [ ] **D17:** Eval harness. AI judge labels acceptable passages for both test sets; you spot-check it on 8 human statements (~10 min). Baseline scores.
- [ ] **D18–19:** Experiments 1–4, 6 and 7 (section 4.4).
- [ ] **D20:** Create the Anthropic API account (prepaid, hard spend cap). Explain prompt, rubric and judge; experiment 5. You spot-check 5 explanations (~5 min).
- [ ] **D21:** Retrieval gate; `logs/Phase-2-Report.md`. Bar (decided 9 Oct; the bridge rubric now applies to Explain): human held-out hit@3 ≥ 70% (23 of 32); crisis 13 of 13 across both sets, borderline statements correct either way; false crisis at most 1 of 5 human and 1 of 8 agent; Explain rubric pass ≥ 90%; hit@10, MRR and agent held-out reported with no bar. [DECISION] Pass, or spend up to 3 days improving.

### 5.4 Phase 3 — Web app (Days 22–29, 29 Oct–5 Nov)

- [ ] **D22:** API routes in Next.js: crisis check → retrieval → ranked list of up to 10 (plain version + passage); Explain on request; Surprise me; rate limit; spend caps.
- [ ] **D23–24:** Next.js web app: input → first passage (plain version first, original beside it) → Next / Back through up to 10 → Explain → Save. Surprise me on the home screen.
- [ ] **D25:** Consent notice, crisis screen, "Need help now?", "Report this response".
- [ ] **D26:** Turnstile bot check (free Cloudflare account); Privacy and About pages.
- [ ] **D27:** [DECISION] Name, look, domain. One visual pass.
- [ ] **D28:** Evals page with real results.
- [ ] **D29:** Friends test, optional: 5–10 people if they're quick to find; otherwise you use it yourself for a few days.

### 5.5 Phase 4 — Launch (Days 30–33, 6–9 Nov)

- [ ] **D30–31:** Fix what testers found.
- [ ] **D32:** Final eval run on the deployed system; `logs/Launch-Report.md`. [DECISION] Go / no-go.
- [ ] **D33:** Public launch: LinkedIn post built on the eval results, linking a case-study page (`docs/Showcase.md`); share with your network.

### 5.6 After launch

1. Android: [DECISION] wrap the website as an Android app (fastest) or build a React Native app that reuses the API (more native). Then register Google Play Console ($25), recruit 15–20 closed testers from web users, run the 14-day closed test. Live around early December (estimate).
2. Grow the corpus server-side (Phase 2 sources) without app releases.
3. iOS after Android.
4. Publication prep: a clean public repo with fresh history, a public README and code licence, and every item on the `docs/Showcase.md` checklist cleared before anything is made public.

## 6. Risks

| Risk | Mitigation |
| --- | --- |
| Public endpoint abused, API bill spikes | Turnstile, per-visitor rate limit, hard spend caps |
| Review work overwhelms your time | Human checks capped at about 10 items, chosen as the riskiest by an AI judge (CLAUDE.md section 2, item 7) |
| A plain version misstates its passage | AI judge checks every one; you fix the 10 weakest; labelled "In plain words" with the original always beside it |
| Retrieval weak on thematic matches | Experiments in section 4.4; gate at Day 21 |
| Missed crisis language | Keyword list + model flag; crisis set must score 5 of 5 |
| OCR artefacts in Japji or other scans | Caught in extraction and harm review; passage cut if unreadable |
| Scope creep | Section 2 is the contract; parking list in `STATUS.md` |
| Free-tier limits change | Checked on Day 1; keep-alive or switch if needed |
| Vercel Hobby usage cap hit | Going over a Hobby limit pauses that feature until 30 days pass; rate limits and Turnstile keep traffic in bounds |
