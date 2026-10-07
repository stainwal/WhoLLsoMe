# WhoLLSome v1 — Web Launch Plan

*Created 7 Oct 2026. Replaces the earlier iOS-first and Android-first plans. Day 1 = Thu 8 Oct 2026, one 1-hour session per day.*

The web app goes public on **Day 33 (Mon 9 Nov 2026)** with all 33 sources, a crisis-safe flow and a published eval page. Android follows, recruiting its closed-test testers from web users.

## 1. Outcome and dates

| Milestone | Day | Date |
| --- | --- | --- |
| Setup done; golden set statements written | 3 | Sat 10 Oct |
| Extraction rules proven on a pilot | 6 | Tue 13 Oct |
| Corpus frozen (all 33 sources extracted, tagged, reviewed) | 14 | Wed 21 Oct |
| Retrieval gate passed | 21 | Wed 28 Oct |
| Working web app with friends testing | 29 | Thu 5 Nov |
| **Public web launch** | **33** | **Mon 9 Nov** |
| Android live (after its 14-day closed test) | — | early Dec (estimate) |

About 33 hours of your time. A missed day moves everything right by one day; the corpus freeze (Day 14) and the retrieval gate (Day 21) are the two planned stops to reassess.

## 2. v1 scope (the build contract)

### 2.1 In

1. **Input:** one text box. Phone keyboards' voice typing covers "speak"; no speech-to-text code.
2. **Output, one passage at a time:** the verbatim passage, its source and translator, and one bridging sentence. "Next" steps through the 10 best fits in ranked order; "Back" returns to earlier ones. Near-identical passages (e.g. two Gita translations of one verse, adjacent verses) never both appear in the 10. Each bridging sentence is written when its passage is first shown, so unseen passages cost nothing.
3. **Save:** favourites kept in the browser. No accounts.
4. **Safety:** crisis check on every input → helpline screen; "Need help now?" always visible; "Report this response" on every result.
5. **Consent:** a first-visit notice that input is sent to an AI provider, with explicit opt-in.
6. **Pages:** About (all 33 sources and translators, not-therapy statement), Privacy, Evals (published results).
7. **Corpus:** all 33 sources in `corpus/source/`, extracted selectively per `docs/Corpus-Policy.md`.

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
| Crisis check, passage choice, bridging sentence (runtime, for public users) | Claude Haiku via the Anthropic API (Sonnet as an eval comparison); a subscription can't serve a public app | Cents/month at hobby scale (estimate) |
| Embeddings (passages once, each user query at runtime) | Hosted embeddings API, or a free model if evals show it's good enough; Anthropic offers no embeddings model | Negligible to $0 (estimate) |
| Extraction and tagging | Claude Code on your subscription | $0 extra |
| Domain | Optional custom domain | ~$10–15/year (estimate) [DECISION] |

Hard monthly spend cap on every API key from Day 1. Free-tier limits (Supabase inactivity pauses, Vercel Hobby usage caps) are checked by Claude Code on Day 1, not assumed.

## 4. Evals

Evals are a workstream, not a final check. They prove the app works, and the published results are part of the resume story.

### 4.1 Test sets

| Set | Size | Written | Used for |
| --- | --- | --- | --- |
| Golden set | 40 statements | Day 3, by you | Tuning: every change is scored against it |
| Held-out set | 20 statements | Day 3, by you; never used for tuning | The number you publish |
| Crisis set | 5 statements | Day 3 | Must route to helplines, 5 of 5 |
| Crisis look-alikes | 5 statements ("I'm dying to see that film") | Day 3 | Must *not* trigger the crisis screen |

Statements are written before you see any tagged passages, so they reflect real users rather than the corpus. Acceptable passages are labelled on Day 16 by pooling: Claude shows the top candidates from several retrieval setups and you mark the ones you'd accept.

### 4.2 Retrieval metrics

- **Hit@3:** share of statements with an acceptable passage in the top 3.
- **Hit@10:** share with an acceptable passage anywhere in the 10 a user can step through.
- **MRR:** how high the first acceptable passage ranks.
- **Crisis recall** and **false crisis rate.**
- **Cost per 1,000 queries** and **response time.**

### 4.3 Bridging-sentence eval

A rubric: true to the passage, no advice, no therapy language, exactly one sentence, no claims about the user. A stronger model grades every output against it (LLM-as-judge); you spot-check 10.

### 4.4 Experiments (one change at a time)

1. Embedding model (2–3 candidates).
2. What gets embedded: passage text / text + tags / "when this helps" line.
3. Query rewriting: turn the user's words into themes before searching.
4. Hybrid search: meaning-based plus keyword.
5. Haiku vs Sonnet for choosing the passage and writing the bridge.

With 40 statements, a difference of 1–2 hits is noise; only gaps of several points are claimed.

### 4.5 Published results

An Evals page on the site: one row per setup with hit@3 (held-out), crisis results, bridge rubric pass rate, cost and speed, plus a few lines on what was learned.

## 5. Phases and days

### 5.1 Phase 0 — Setup (Days 1–3, 8–10 Oct)

- [ ] **D1:** Open Claude Code in `Version1_QuickLaunch`. Git repo + private GitHub repo. Accounts: Supabase (new); Vercel (existing). Claude checks free-tier limits. (Offline corpus work runs on your Claude subscription; the paid API accounts wait until they're needed, D15 and D20.)
- [ ] **D2:** [DECISION] Passage and tag schema; per-source cap for the GRAY Sivananda Gita. Claude proposes, you choose.
- [ ] **D3:** Write the test sets (section 4.1). [DECISION] Gate thresholds (section 5.3).

Exit: accounts live, schema agreed, 70 test statements written.

### 5.2 Phase 1 — Corpus (Days 4–14, 11–21 Oct)

- [ ] **D4:** Normalise all 33 sources (Corpus-Policy section 7, step 1). Pilot extraction and verbatim check on one short, structured source (Dhammapada) and one dense one (a Vivekananda lecture). First heavy run: Claude walks you through the `/usage` readings and records the token calibration (CLAUDE.md section 4.3).
- [ ] **D5:** You judge 30 pilot passages keep/cut; extraction rules adjusted.
- [ ] **D6:** Pilot tagging + both harm passes; the same chunks run through Sonnet and Opus. [DECISION] Model for bulk work. Rules locked.
- [ ] **D7–11:** Full run across all 33 sources, parallel and unattended, highest-yield sources first (Gita, Dhammapada, Psalms/Proverbs/Ecclesiastes, Meditations, Enchiridion, Tao Te Ching, The Prophet, Pirkei Avot, Rumi), bulk sources last (rest of the Bible, Nikayas, Vivekananda, Seneca). Each session: Claude proposes that day's batch and token budget; you review that day's flagged passages and the 5% sample.
- [ ] **D12–13:** Deduplicate, check consistency, corpus statistics by source and theme.
- [ ] **D14:** Corpus freeze v1. `logs/Phase-1-Report.md`. [DECISION] Accept, or extend by up to 3 days.

Exit: every passage extracted, tagged and harm-reviewed per `docs/Corpus-Policy.md`.

### 5.3 Phase 2 — Retrieval and evals (Days 15–21, 22–28 Oct)

- [ ] **D15:** [DECISION] Embeddings option (hosted API vs a free model). Load passages into Supabase; baseline embeddings.
- [ ] **D16:** Label acceptable passages for the golden and held-out sets (pooling).
- [ ] **D17:** Eval harness; baseline scores.
- [ ] **D18–19:** Experiments 1–4 (section 4.4).
- [ ] **D20:** Create the Anthropic API account (prepaid, hard spend cap). Bridging-sentence prompt, rubric and judge; experiment 5.
- [ ] **D21:** Retrieval gate; `logs/Phase-2-Report.md`. Proposed bar: held-out hit@3 ≥ 70% (14 of 20), crisis 5 of 5, at most 1 false crisis of 5, bridge rubric pass ≥ 90%. [DECISION] Pass, or spend up to 3 days improving.

### 5.4 Phase 3 — Web app (Days 22–29, 29 Oct–5 Nov)

- [ ] **D22:** API routes in Next.js: crisis check → retrieval → ranked list of up to 10 passages; bridging sentence per passage on request; rate limit; spend caps.
- [ ] **D23–24:** Next.js web app: input → first passage → Next / Back through up to 10 → save any of them.
- [ ] **D25:** Consent notice, crisis screen, "Need help now?", "Report this response".
- [ ] **D26:** Turnstile bot check (free Cloudflare account); Privacy and About pages.
- [ ] **D27:** [DECISION] Name, look, domain. One visual pass.
- [ ] **D28:** Evals page with real results.
- [ ] **D29:** Friends test: 5–10 people, a short feedback form.

### 5.5 Phase 4 — Launch (Days 30–33, 6–9 Nov)

- [ ] **D30–31:** Fix what testers found.
- [ ] **D32:** Final eval run on the deployed system; `logs/Launch-Report.md`. [DECISION] Go / no-go.
- [ ] **D33:** Public launch: LinkedIn post built on the eval results, share with your network.

### 5.6 After launch

1. Android: [DECISION] wrap the website as an Android app (fastest) or build a React Native app that reuses the API (more native). Then register Google Play Console ($25), recruit 15–20 closed testers from web users, run the 14-day closed test. Live around early December (estimate).
2. Grow the corpus server-side (Phase 2 sources) without app releases.
3. iOS after Android.

## 6. Risks

| Risk | Mitigation |
| --- | --- |
| Public endpoint abused, API bill spikes | Turnstile, per-visitor rate limit, hard spend caps |
| Harm review overwhelms your hour | Risk-based review (Corpus-Policy section 6); extend Phase 1 at the Day 14 stop rather than skip review |
| Retrieval weak on thematic matches | Experiments in section 4.4; gate at Day 21 |
| Missed crisis language | Keyword list + model flag; crisis set must score 5 of 5 |
| OCR artefacts in Japji or other scans | Caught in extraction and harm review; passage cut if unreadable |
| Scope creep | Section 2 is the contract; parking list in `STATUS.md` |
| Free-tier limits change | Checked on Day 1; keep-alive or switch if needed |
| Vercel Hobby usage cap hit | Going over a Hobby limit pauses that feature until 30 days pass; rate limits and Turnstile keep traffic in bounds |
