# Decision Log

Newest first. **Decided** = Shailesh's call. **Proposed** = recommended, not yet confirmed; treat as the working assumption until he says otherwise.

## 1. Version 1 Quick Launch (7 Oct 2026)

| Status | Decision | Why | Supersedes |
| --- | --- | --- | --- |
| Decided | **Embeddings: Voyage `voyage-4-lite`, 1024 dimensions** (Shailesh, 12 Oct). Hosted API (decided earlier that day); payment method added for standard rate limits, budget cap $5/month. Baseline setup `voyage-4-lite/text+plain` (Plan section 4.4, experiment 2) | $0.02 per million tokens with 200M free tokens per account (Voyage pricing page, checked 12 Oct); the baseline used 603,619. 1024 is the default size and costs 47 MB of database in all | `voyage-3.5-lite` (now listed as older, no free tokens); OpenAI `text-embedding-3-small` (same price, no free allowance); a free self-hosted model |
| Decided | **Showcase framing removed from the public repo** (Shailesh, 12 Oct): README presented as a personal project; `docs/Showcase.md` cut to its checklist and renamed `docs/Publication-Checklist.md`; the case-study material moved to the private archive; log section 6 renamed "Lessons" | The repository is a personal project, not a portfolio piece | Showcase file and "Showcase note" log section |
| Decided | **Project name spelled WhoLLsoMe** (Shailesh, 12 Oct): LL for LLM. Text only; no file or folder renamed | Consistency with the repository name | "WhoLLSome" |
| Decided | **viv04-031-p02 (Vivekananda, Jnana-Yoga, "Can I kill myself?") hidden from distress** (Shailesh, 12 Oct). Status `no-distress` added to its existing override in `overrides.json`; the display correction stays; verbatim `text` unchanged. Shown passages stay 5,540; hidden from distress 62 → 63 | It names suicide, though rhetorically (in oneness, whom could I harm?); same safe-messaging rule as the other six suicide-naming passages (8 Oct precedent) | Keep it shown to everyone |
| Decided | **Two print-confirmed corrections applied as display overrides** (Shailesh, 12 Oct; logged by Cowork): viv04-031-p02 "an gods" → "all gods" (printed Complete Works Vol. II); schopenhauer-counsels-maxims-010-p06 "shortcoming's" → "shortcomings", "is own image" → "its own image" (1924 printing). In `overrides.json`; verbatim `text` unchanged | The Day 16 second-copy check refuted the AI's proposed fix but confirmed a different correct reading | Show uncorrected (D16 revert) |
| Decided | **Code licence MIT**, © stainwal (Shailesh, 12 Oct; logged by Cowork). Passages keep their source licences; README says so and names the Kulp (CC-BY) and WEB credits | Simplest permissive licence; the corpus is not the author's to license | Apache 2.0 |
| Decided | **Crisis test statements private** (Shailesh, 12 Oct; logged by Cowork; option A): the 13 crisis statements live in git-ignored `evals/private/crisis.jsonl`, read through `evals/sets.py`, purged from git history, blocked by the pre-commit hook. Look-alikes stay public | Keeps the crisis check from being tuned to its own test; publication checklist item 6 | Publish them (option B) |
| Decided | **Speed to release first; human review kept tiny** (11 Oct): automate everything possible; human checks capped at about 10 items, chosen as the riskiest by an AI judge | Shailesh's time is the constraint; deeper changes come after he has used the live app | Larger random samples (40) |
| Decided | **Plain-language version for every passage**, generated offline, stored, shown first as "In plain words" with the original beside it (11 Oct) | Day 5 review: dense passages need a quick way in; the plain version lets the user decide whether to read the original | Verbatim passage only |
| Decided | **Explain button replaces the bridging sentence** (11 Oct): generated on request, tailored to what the user wrote | Three generated layers is too much; costs nothing unless asked | Always-on bridging sentence |
| Decided | **Surprise me button**: random high-quotability passage, no input, no AI call (11 Oct) | A no-commitment way to try the app | — |
| Decided | **Quotability boost** in ranking among close matches (11 Oct) | Short aphorisms landed best in the Day 5 review | — |
| Decided | **Transcription errors fixed for display** even where the display then differs from the source file; translator's wording never changed (11 Oct) | Odd text (S15 Rumi, S29 Vivekananda) hurts reading; the verbatim `text` stays for audit | Display fixes only by explicit override |
| Decided | **Enrichment pass** over all shown passages: plain version, quotability, completeness (verbatim extension), text fixes, core idea (11 Oct) | One cheap offline run (~2–5% of a week) feeds the new UI and ranking | — |
| Decided | **Seven aphoristic public-domain works added**, pending licence check: Tagore (*Stray Birds*, *Sādhanā*, *Gitanjali*), Gibran (*Sand and Foam*, *The Madman*, *The Forerunner*), Gracián (Jacobs) (11 Oct) | Fill the appetite for short, graspable wisdom | Corpus freeze v1 (additions only) |
| Decided | **Alan Watts rejected** (11 Oct) | His estate licenses his work commercially; on the policy's "never" list | — |
| Decided | **AI judge labels acceptable passages for both test sets**; Shailesh spot-checks 8 human statements, labels stand at 6 of 8 agreement (11 Oct) | Labelling 32 statements by hand is the largest human task left | Shailesh labels the human set; judge on agent set only |
| Decided | **Corpus freeze v1 accepted** (Shailesh, 9 Oct; `logs/Phase-1-Report.md` section 6). `corpus/passages/` as of commit `207c285` is v1; only per-passage overrides may change after this. Reopen only if the Day 5 sample shows fewer than 34 keeps of 40 | Complete, verbatim, 0 tag errors, deduplicated; known gaps are retrieval problems; the 3 extension days are worth more in Phase 2 | Extend 1–3 days (option B) |
| Decided | **Gate thresholds, option A** (Shailesh, 9 Oct): human held-out hit@3 ≥ 70% (23 of 32); crisis 13 of 13 across both sets, borderline statements either way; false crisis ≤ 1 of 5 human and ≤ 1 of 8 agent; bridge rubric ≥ 90%; hit@10, MRR and agent held-out reported with no bar | One statement moves hit@3 by 3 points, so a stricter bar is noise; the absolute bar belongs on crisis recall | Plan's original 14 of 20; stricter 75% / 0 false crisis |
| Proposed | **Deduplication rule** (9 Oct, `pipeline/dedup.py`): exact repeats and stock formulae (8-gram Jaccard ≥ 0.8) keep the earliest in the source; a passage inside another keeps the longer; pairs sharing over half their wording are both kept in one `near_group` the search filter respects. Status `dup`, nothing deleted | 84 repeats, all but one in the Nikayas; the Gita and Epictetus translations are worded differently and stay for the search-time filter | Delete duplicates; dedup by embedding at load time |
| Decided | **Display apparatus rules widened** (Shailesh, 9 Oct): `display_text` also drops Gutenberg `_italics_` underscores and a quotation mark whose partner is outside the passage, capitalises a lower-case first letter, and carries per-passage scan-error corrections from `overrides.json` (Japji, Upanishads). `text` is untouched | File apparatus, not the translator's words; 316 passages read cleanly instead of showing markup | Show as extracted |
| Decided | **Japji OCR passage corrected for display** (9 Oct), not hidden | Four obvious scan errors in a 100-word passage; verbatim text kept for the check | Hide the passage |
| Decided | **Two passages that argue against suicide (MN 144, Walden Conclusion) are hidden from anyone in distress; SuttaCentral `<j>` layout markup is stripped for display** (8 Oct). Applied through `corpus/passages/bulk/overrides.json` and a `display_text` field; the verbatim `text` is unchanged | They name suicide, a safe-messaging risk; `<j>` is source formatting, not the translator's words | — |
| Decided | **Corpus stands as extracted; nothing cut is recovered** (8 Oct, after D7–11). The 16 safety-field cuts stay cut, including the three likely over-cuts. No re-run for the 7 verbatim rejects, the `<j>`-skipped SuttaCentral verses, or passages helpers left out at extraction | 5,029 passages is enough; recovering a handful is not worth the effort | Proposed restores and re-runs in `logs/D07.md` section 4 |
| Decided | **Crisis detection covers risk of harm to others as well as to self** (9 Oct); both go to the same crisis screen, no separate flow | One of Shailesh's crisis statements was about harming others; no extra work beyond the shared screen | Self-harm only |
| Decided | **Two independent test sets** (8 Oct): a human set written by Shailesh from intuition, and an agent set researched by several models from real public posts and compiled by the Cowork reviewer. Scored separately; the human held-out set is the headline. **Revised 9 Oct:** the human set is 32 situation statements, all held out (never tuned on), plus 5 crisis and 5 look-alikes; tuning uses the agent set (~60 golden, ~20 held-out) | Doubles coverage without letting AI-written statements flatter an AI-built system; real posts give realistic phrasing | Single 70-statement human set |
| Decided | **Opus 5.5 for bulk extraction and tagging**, medium effort (D6) | Pilot cost indistinguishable from Sonnet; Opus the stronger model. Picks more passages (86 vs 49), so tagging volume and corpus size are higher | Sonnet default (proposed 7 Oct) |
| Decided | **Tag schema: option C**, fixed lists plus up to 3 free keywords; fine tags rolled up to families (D2, 1) | Consistent across 33 sources; keywords catch nuance and help hybrid search | Free-form tags |
| Decided | **Feelings axis added** (36 tags), meaning the feeling a reader **arrives with** (D2, 1b; Decision 4) | Users type feelings; "arrives with" removed opposite-pole confusion in the pilot (positive tags 17% → 4%) | — |
| Decided | **Faith framing field** (secular / spiritual / devotional), used for ranking only (D2, 1c) | A secular reader shouldn't get a prayer first; Pew 2023: about 21% of US adults neither religious nor spiritual | — |
| Decided | **Taxonomy v2 approved**: 36 feelings, 37 themes (incl. growth and practice), 57 situations, 9 tones, grounded in ICD-10 Z codes, DSM-5, LTE, Holmes–Rahe, Crisis Text Line, Anthropic support study, VIA, Common Wisdom Model, Social Support Behavior Code | Credible external grounding; `pipeline/prompts/taxonomy.md` | Draft lists |
| Decided | **Extraction keeps spiritual teaching** a reader outside the tradition can follow (D2, 1d) | Old "skip doctrine" rule would have gutted the Upanishads, Vivekananda, Teresa | Corpus-Policy 4.3 wording |
| Decided | **Sivananda Gita treated like any other source**, no cap; Shailesh handles its licensing (D2, 2) | Shailesh's call | Proposed 75-passage cap |
| Decided | **Both Gita translations independent**; no one-voice-per-verse rule; duplicates only via the general search-time filter | Not worth extra logic or tokens | Corpus-Policy 4.6 |
| Decided | **Keep *Way of Perfection* (Peers) and *Brother Lawrence* (Lightheart 2002)** despite both being copyrighted editions | Shailesh has a plan for both | Manifest's wrong attributions |
| Decided | **Source on/off switch** in `pipeline/sources.toml`; switching off skips every pipeline step and the app, deletes nothing | Lets any source be withdrawn later in one edit | — |
| Decided | **Harm review narrowed (Decision 3, option B, amended)**: a safety field in tagging; cut endorses-suicide (incl. methods), sexual violence, group hatred; death-welcoming kept but never for distress; no separate harm pass, keyword pass or 5% sample | Broad harshness filtering would strip the corpus; serious cases still caught; WHO 2023 safe-messaging guidance | Corpus-Policy section 6 (three-layer review) |
| Decided | **Web first**; Android after the web launch, then iOS | Live with real users weeks sooner; no store review or 14-day closed test on the critical path; a link is an easier demo | iOS-first (Aug), Android-first (earlier on 7 Oct) |
| Decided | **Full corpus in v1:** all 33 sources | "Make sure it actually works" matters more than speed | 8-source v1 cut |
| Decided | Drop duplicates: WEB Bible over KJV; Arnold + Sivananda Gita, not Besant-Das | Near-identical passages would compete in search | — |
| Decided | **Evals are a workstream**; results published on the site | Proves it works; doubles as a learning record | — |
| Decided | **Claude leads**; Shailesh executes and makes high-level calls | His time is 1 hour/day | — |
| Decided | `Version1_QuickLaunch/` is the working home; plan lives in `docs/Plan.md` | One source of truth Claude Code reads every session | Plan doc in Claude Docs (now stale) |
| Proposed | Study list is no longer a gate; learning happens through the build and evals | Saves ~6 hours before anything ships | "Theory first" step |
| Proposed | Text box + keyboard voice typing instead of speech-to-text code | Free, no code, works on every phone | — |
| Superseded | Risk-based harm review (auto-flags + second Claude pass + 5% sample) — replaced 7 Oct by Decision 3 | Full manual review of thousands of passages won't fit 1 hour/day | "I curate, you edit" on every passage |
| Decided | **Heavy runs under a token budget**, driven by Claude (`CLAUDE.md` section 4.3) | Protects the plan allowance he shares with other daily work | — |
| Decided | Project history moved to `../../Version0/`; root holds only Version0 and Version1_QuickLaunch | Clean working home | — |
| Decided | Results shown **one passage at a time**, with Next / Back through the **10 best fits** in ranked order | Lets the user find the passage that lands without overwhelming them | Single answer + "show another" |
| Decided | **Next.js on Vercel** (existing account) for the web app and its API routes | Already learning Next.js; Vercel already in use; one codebase for UI + API | Expo web + Cloudflare Pages + Supabase Edge Function (proposed earlier on 7 Oct) |
| Proposed | Supabase Postgres + pgvector as the database; Cloudflare Turnstile for bot protection; Claude Haiku at runtime | Free tiers; Turnstile works on any host | — |
| Proposed | Gate bar: held-out hit@3 ≥ 70%, crisis 5/5, ≤ 1/5 false crisis, bridge rubric ≥ 90% | Set on Day 3 | — |

## 2. Earlier decisions still in force (Aug–Sep 2026)

| Date | Decision | Why |
| --- | --- | --- |
| 21 Aug | Answer = verbatim passage + one generated bridging sentence | Pure quotes feel like fortune cookies; generated prose loses the point |
| 21 Aug | Not positioned as therapy; crisis detection → helplines is mandatory | Store and regulatory risk; user safety |
| 21 Aug | Scope frozen: input → passage → optional save. No journaling, streaks, mood tracking, accounts | Scope creep is the named failure risk |
| 21 Aug | Retrieval (embeddings), not fine-tuning | Fine-tuning teaches behaviour, not knowledge; would bake GRAY translations into weights |
| 23 Aug | Tier 1 corpus finalised (31 sources, 11 traditions) | See `../../Version0/corpus-sources.md` |
| 24 Aug | Sourcing policy v2 (Tier A / Tier B GRAY / never) | See `Corpus-Policy.md` section 1 |
| 24 Aug | Sivananda Gita supersedes Besant-Das; Arnold stays primary | Besant-Das OCR unusable |
| 24 Aug | Curation model: Claude extracts and tags; Shailesh reviews | His time goes to judgement, not typing |
| 27 Aug | Architecture: offline extraction + tagging → embeddings search at runtime → generation only for the bridge | Most of the product is retrieval |
| 14 Sep | Project paused | Focus elsewhere; resumed 7 Oct |

## 3. Rejected and not to be reopened

Sources: see `Corpus-Policy.md` section 1. Product: no therapy positioning, no fine-tuning, no accounts in v1.
