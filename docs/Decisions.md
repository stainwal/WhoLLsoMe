# Decision Log

Newest first. **Decided** = Shailesh's call. **Proposed** = recommended, not yet confirmed; treat as the working assumption until he says otherwise.

## 1. Version 1 Quick Launch (7 Oct 2026)

| Status | Decision | Why | Supersedes |
| --- | --- | --- | --- |
| Decided | **Web first**; Android after the web launch, then iOS | Live with real users weeks sooner; no store review or 14-day closed test on the critical path; a link is an easier resume demo | iOS-first (Aug), Android-first (earlier on 7 Oct) |
| Decided | **Full corpus in v1:** all 33 sources | "Make sure it actually works" matters more than speed | 8-source v1 cut |
| Decided | Drop duplicates: WEB Bible over KJV; Arnold + Sivananda Gita, not Besant-Das | Near-identical passages would compete in search | — |
| Decided | **Evals are a workstream**; results published on the site | Proves it works; doubles as learning and resume story | — |
| Decided | **Claude leads**; Shailesh executes and makes high-level calls | His time is 1 hour/day | — |
| Decided | `Version1_QuickLaunch/` is the working home; plan lives in `docs/Plan.md` | One source of truth Claude Code reads every session | Plan doc in Claude Docs (now stale) |
| Proposed | Study list is no longer a gate; learning happens through the build and evals | Saves ~6 hours before anything ships | "Theory first" step |
| Proposed | Text box + keyboard voice typing instead of speech-to-text code | Free, no code, works on every phone | — |
| Proposed | Risk-based harm review (auto-flags + second Claude pass + 5% sample) | Full manual review of thousands of passages won't fit 1 hour/day | "I curate, you edit" on every passage |
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
