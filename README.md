# WhoLLsoMe

**A reflection app that answers only in wisdom literature: no chatbot flattery, no invented advice.** You describe what you're going through; it answers with real passages from the Gita, the Dhammapada, the Stoics, the Psalms, Rumi, Tagore and 30-odd other sources, each with a plain-language version and an explanation on request.

> **Status:** in active development, Phase 2 of 4 (retrieval and evals). Web launch target: 9 November 2026. Live state of the project: [`STATUS.md`](STATUS.md).

## 1. The product

General-purpose chatbots tend to agree with you and keep you talking. WhoLLsoMe makes a different promise: everything it shows you was written by someone else, centuries ago, and is quoted word for word. The constraint is the product.

1. **You type (or voice-type) a situation:** "I just got laid off and I don't know how to tell anyone."
2. **You get the 10 best-matching passages, one at a time**, each with its plain-language version first ("In plain words") and the original beside it, credited to its source and translator.
3. **Explain** (on request) generates a short note on how that passage applies to what you wrote.
4. **Surprise me** shows a random, highly quotable passage, for anyone who just wants to try it.
5. **Not therapy.** Any sign of risk of harm, to yourself or others, goes straight to a crisis screen with helplines.

## 2. About this repository

A personal project, built mostly by AI agents at about one hour of my time a day. Alongside the code, the repository keeps the plan, every decision, the eval sets and the session logs, in the order they happened.

## 3. Progress so far

| Milestone | Result |
| --- | --- |
| Corpus | 39 sources across 13 traditions, 4.2M words read. 36 are public domain or openly licensed and are in this repository; 3 are under licence review and kept out of it (section 7) |
| Passages | 5,540 shown passages, each extracted verbatim, tagged (feelings, themes, situations, tone, faith framing, safety) and enriched with a plain-language version |
| Verbatim check | 99.88% of extracted passages (5,642 of 5,649) matched their source exactly; the rest were rejected, never repaired |
| Human quality review | 38 of 40 randomly sampled passages judged worth showing (95%) |
| Plain versions | All 5,540 rated 4 or 5 of 5 for faithfulness by an AI judge, after the 103 weakest were rewritten to keep each passage's conclusion (98.1% before). The judge is the writer's model family; a human checked the 10 weakest |
| Cost of the full corpus run | 20% of one week's subscription allowance, against 57% predicted |
| Schedule | Corpus phase closed 12 days ahead of plan |

Numbers trace to the session logs in [`logs/`](logs/).

## 4. How it's being built

### 4.1 Roles

| Who | Does what |
| --- | --- |
| **Me (product owner)** | Product calls, every decision marked [DECISION], small targeted reviews (about 10 items at a time), accounts and payments |
| **Claude in Cowork (lead and reviewer)** | Plans, writes the plan and policies, reviews every session's output against its evidence, flags risks |
| **Claude Code (builder)** | Builds the pipeline and app, runs the heavy jobs unattended, writes a session log with evidence, commits |

### 4.2 Working files

- [`CLAUDE.md`](CLAUDE.md): the standing brief every session starts from: goal, roles, rules, the one-hour session protocol.
- [`STATUS.md`](STATUS.md): one page on where things stand, updated at every session close.
- [`docs/Plan.md`](docs/Plan.md): scope, phases, day-by-day tasks and the go/no-go gates.
- [`docs/Decisions.md`](docs/Decisions.md): every decision with its date, reason and what it replaced.
- [`logs/`](logs/): a session log per working day (done, evidence, flags, decisions needed, next), phase reports, and [`Reviews.md`](logs/Reviews.md), the reviewer's verdict on each session.
- [`.claude/skills/session-close/`](.claude/skills/session-close/): a Claude Code skill that closes every session the same way: log, status, plan ticks, commit.
- **Token budget:** before any heavy run, Claude reads the usage meter, estimates the cost and runs in batches under an agreed budget.

### 4.3 The pipeline

```
sources ─► normalise ─► extract (Opus) ─► verbatim check ─► tag + safety field ─► deduplicate
        ─► enrich (plain version, quotability, completeness) ─► AI judge ─► embed ─► search ─► rank
```

Details: [`docs/Corpus-Policy.md`](docs/Corpus-Policy.md) section 7.

## 5. Evals

Evals are a workstream from day one, not a final check.

- **Two independent test sets.** 32 situations I wrote from intuition before seeing any output, kept untouched for the headline score; and 80 more researched by four different models from real public posts, compiled for coverage, used for tuning.
- **Safety cases.** Crisis statements (13 across both sets) that must all reach the crisis screen, and look-alikes ("my boss is going to kill me", "cut myself slicing onions") that must not.
- **Go/no-go gate:** at least 70% of my held-out statements get an acceptable passage in the top 3, every crisis statement caught, at most one false alarm per set, and Explain passing its rubric 90% of the time.
- **Published results:** the launched site will carry an Evals page comparing every setup tried (embedding models, what gets embedded, ranking boosts), with the method and its limits stated.

## 6. Key decisions

| Date | Decision | Why |
| --- | --- | --- |
| 7 Oct | Web first, not iOS or Android | App-store review and Google Play's 14-day closed test were on the critical path; a link is also an easier demo |
| 7 Oct | Full 33-source corpus (later 39) rather than a quick 8-source cut | "Make sure it actually works" mattered more than speed |
| 7 Oct | Opus over Sonnet for extraction | A pilot showed equal cost and more passages found |
| 8 Oct | Two test sets, human and AI-researched, scored separately | More coverage without letting AI-written tests flatter an AI-built system |
| 11 Oct | Plain-language versions, Explain and Surprise me | A 40-passage human review showed that short, graspable wisdom lands and dense passages don't |
| 11 Oct | Human review capped at about 10 targeted items | Speed to release first; the AI judge picks what a human should look at |

Full log: [`docs/Decisions.md`](docs/Decisions.md).

## 7. Safety, ethics and licensing

- **Verbatim sources.** Passage text is never paraphrased or modernised; only the plain version and Explain are generated, and both are labelled.
- **Safe messaging.** Passages that endorse suicide or self-harm are cut, following the WHO's 2023 media guidance; passages that present death as a release are never shown to someone in distress.
- **No user data kept.** What people type is not stored.
- **Licensing.** Every source in this repository is US public domain or openly licensed, credited to its translator. Three sources whose rights are unclear (two copyrighted editions and one translation of unstated licence) are excluded from this repository and its history; they will be cleared or replaced before the public launch. Policy and per-source licences: [`docs/Corpus-Policy.md`](docs/Corpus-Policy.md).
- **Licence of this repository.** The code is MIT ([`LICENSE`](LICENSE)). The passages are not covered by it: each keeps its source's licence, as listed per source, with its translator, in [`docs/Corpus-Policy.md`](docs/Corpus-Policy.md) section 2 (credits as shown in the app: section 3). Two sources carry attribution terms: Pirkei Avot is "Mishnah Yomit by Dr. Joshua Kulp" ([Sefaria](https://www.sefaria.org/Pirkei_Avot), CC-BY), and Bible passages are from the World English Bible (public domain; the name is used per [ebible.org](https://ebible.org/web/)).
- **Crisis test statements are private.** The 13 crisis statements in the test sets are kept out of this repository so the safety check can't be tuned to them; the look-alikes are public.

## 8. Roadmap

1. **Phase 2:** retrieval and evals (embeddings, Supabase, experiments, the gate).
2. **Phase 3:** the Next.js web app on Vercel.
3. **Phase 4:** launch, with the Evals page.
4. **Then:** Android, iOS, and a growing corpus.

## 9. Repository map

| Path | Holds |
| --- | --- |
| `docs/` | Plan, decisions, corpus policy, showcase notes |
| `logs/` | Session logs, phase reports, reviews |
| `pipeline/` | Normalisation, extraction, tagging, deduplication, enrichment |
| `corpus/` | Source texts and extracted passages (the three restricted sources are kept out; see section 7) |
| `evals/` | Test sets and evaluation scripts |
| `app/`, `backend/` | The web app and database (Phase 3) |

## 10. About

Built by Shailesh ([@stainwal](https://github.com/stainwal)).
