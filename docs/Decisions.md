# Decision Log

Newest first. **Decided** = Shailesh's call. **Proposed** = recommended, not yet confirmed; treat as the working assumption until he says otherwise.

## 1. Version 1 Quick Launch (7 Oct 2026)

| Status | Decision | Why | Supersedes |
| --- | --- | --- | --- |
| Decided | **Two passages that argue against suicide (MN 144, Walden Conclusion) are hidden from anyone in distress; SuttaCentral `<j>` layout markup is stripped for display** (8 Oct). Applied through `corpus/passages/bulk/overrides.json` and a `display_text` field; the verbatim `text` is unchanged | They name suicide, a safe-messaging risk; `<j>` is source formatting, not the translator's words | — |
| Decided | **Corpus stands as extracted; nothing cut is recovered** (8 Oct, after D7–11). The 16 safety-field cuts stay cut, including the three likely over-cuts. No re-run for the 7 verbatim rejects, the `<j>`-skipped SuttaCentral verses, or passages helpers left out at extraction | 5,029 passages is enough; recovering a handful is not worth the effort | Proposed restores and re-runs in `logs/D07.md` section 4 |
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
| Decided | **Web first**; Android after the web launch, then iOS | Live with real users weeks sooner; no store review or 14-day closed test on the critical path; a link is an easier resume demo | iOS-first (Aug), Android-first (earlier on 7 Oct) |
| Decided | **Full corpus in v1:** all 33 sources | "Make sure it actually works" matters more than speed | 8-source v1 cut |
| Decided | Drop duplicates: WEB Bible over KJV; Arnold + Sivananda Gita, not Besant-Das | Near-identical passages would compete in search | — |
| Decided | **Evals are a workstream**; results published on the site | Proves it works; doubles as learning and resume story | — |
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
