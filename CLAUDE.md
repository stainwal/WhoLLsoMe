# WhoLLSome — Version 1 (Quick Launch)

Standing brief for Claude Code. Read this, then `STATUS.md`, then `docs/Plan.md` at the start of every session.

## 1. What we're building

A web app for people who turn to AI for reflection. The user types (or voice-types) a mood or situation. The app answers with **one verbatim passage** from a curated corpus of wisdom literature, its source and translator credit, and **one generated bridging sentence** linking the passage to what the user said. The constraint is the product: it counters the sycophancy and engagement-maximising habits of general chatbots.

- **Not therapy.** Never present it as mental-health support. Crisis language → helpline screen, every time.
- **Verbatim means verbatim.** Passage text is never paraphrased, trimmed mid-sentence or "modernised" by the model. Only the bridging sentence is generated.

## 2. Goal and constraints

1. **Goal:** a live, public, demonstrable product for Shailesh's resume, with published eval results. Business potential is secondary.
2. **Web first.** Next.js on Vercel. Mobile (Android, then iOS) comes after the web launch; the corpus, database and API carry over unchanged.
3. **Full corpus in v1:** all 33 sources in `corpus/source/`.
4. **Budget is small.** Prefer free tiers; every API key has a hard monthly spend cap.
5. **Shailesh** has strong product and conceptual skills and limited hands-on coding. Explain decisions in plain language; never expect him to write or debug code.
6. **Browser tasks use Brave**, not Chrome.

## 3. Roles

- **Claude leads.** Picks the next task from `docs/Plan.md`, plans it, builds it, tests it, reports results, and keeps `STATUS.md` current.
- **Shailesh executes and decides.** Runs sessions, creates accounts, pays, reviews flagged passages, writes the golden-set statements, and makes every call marked **[DECISION]**.
- Raise a [DECISION] whenever a choice changes scope, cost, the user experience, safety behaviour or published claims. Offer 2–3 options with a recommendation; don't decide these silently.

## 4. Session protocol (1 hour)

1. **Open (5 min):** read `STATUS.md` and `docs/Plan.md`. Say which plan day this is, what's done, and today's task. List any [DECISION] waiting on Shailesh.
2. **Plan (10 min):** for non-trivial work, use plan mode and get a yes before writing code.
3. **Build and check (35 min):** do the work; show results (eval scores, screenshots, sample passages) rather than describing them.
4. **Close (10 min):** run the `session-close` skill (section 4.1): it writes the session log, updates `STATUS.md`, ticks the plan, commits and starts any long unattended job. If Shailesh signals he's wrapping up and hasn't called it, run it anyway. A session is not closed until its log exists.

### 4.1 Session log

Written by the `session-close` skill (`.claude/skills/session-close/`), which holds the steps and the log format. One file per plan day: `logs/D01.md`, `logs/D02.md` … Logs carry evidence (numbers, samples, file paths), not narration, plus flags, decisions needed and the next task.

### 4.2 Phase reports

At each planned stop, write a phase report in `logs/` before Shailesh decides: `Phase-1-Report.md` (Day 14, corpus freeze), `Phase-2-Report.md` (Day 21, retrieval gate), `Launch-Report.md` (Day 32, go / no-go). Each covers what was built, the eval numbers, known weaknesses and a recommendation.

Sub-steps are recorded in git commit messages only; no separate docs for them.

### 4.3 Heavy runs (token budget)

A heavy run is any job that reads a lot of text or calls models many times: extraction, tagging, harm passes, full eval runs. Shailesh's plan allowance is shared with his other work, and he isn't familiar with `/usage`, so **Claude drives this every time**:

1. **Ask for a reading.** Before starting, ask him for two percentages: **Current session** (rolling 5-hour window) and **Weekly limits → All models**. He can read them in the Claude desktop app under Settings → Usage, or by typing `/usage` in Claude Code. A screenshot of the Usage screen works too. Claude cannot read them itself. His plan is Team, so the allowance is shared with his Cowork and chat use.
2. **Show an estimate.** A short table: what will be processed (sources or files), word count, estimated tokens, and estimated share of the weekly limit using the calibration in `STATUS.md` section 6. Before calibration exists, say so and give tokens only.
3. **Propose a budget.** Default: one run uses at most 15% of the weekly limit and leaves at least 30% of the week unused. He confirms or changes it.
4. **Run in batches.** Process source by source and chunk by chunk, keeping a running tally against the estimate. Stop at the end of the batch that would cross the budget; progress is saved, so the next run resumes there.
5. **Close the loop.** Afterwards, ask for a second `/usage` reading. Record estimated vs actual in the session log and update the calibration in `STATUS.md` section 6.

Bulk extraction and tagging run in subagents on **Opus 5.5** at medium effort, the same settings as the pilot (Shailesh's decision, 7 Oct 2026).

## 5. Rules

1. **Scope is frozen** to `docs/Plan.md` → section 2. New ideas go to the parking list in `STATUS.md`, not into the build.
2. **Folders:** the structure in section 6 is agreed. Inside `pipeline/`, `backend/`, `app/`, `evals/`, `corpus/passages/` and `logs/`, create files as tasks need. Any new top-level folder, any rename, move or delete outside those, and any change to `docs/` beyond editing existing files needs Shailesh's explicit yes first.
3. **`corpus/source/` is read-only.** Never edit source texts; derived output goes to `corpus/passages/`.
4. **Secrets** live in `.env` files that are git-ignored. Never commit keys.
5. **Don't store user input** on the server. Log counts and errors, not what people typed.
6. **Licensing:** follow `docs/Corpus-Policy.md`. Every passage shown carries its translator credit.
7. **No heavy run without a budget.** Follow section 4.3: reading, estimate, agreed budget, batches, second reading.
8. **Evals are the truth.** Any change to extraction, tagging, embeddings, retrieval or prompts is followed by an eval run, and the result goes in `evals/` and `STATUS.md`.
9. **Plain language.** Use the plan's terms consistently once agreed (golden set, held-out set, retrieval gate, bridging sentence, harm review).

## 6. Folder map

| Path | Holds |
| --- | --- |
| `CLAUDE.md` | This brief |
| `STATUS.md` | Current state, next step, open decisions, parking list |
| `docs/Plan.md` | The plan: scope, phases, days, gates |
| `docs/Decisions.md` | Decision log with dates and reasons |
| `docs/Corpus-Policy.md` | Sourcing rules, credits, extraction and harm-review rules, the corpus pipeline (section 7) |
| `corpus/source/` | 33 source texts, one folder per source (read-only) |
| `corpus/manifest.md` | Provenance of every source (copied 7 Oct 2026 from the original manifest) |
| `corpus/passages/` | Extracted, tagged, reviewed passages |
| `evals/` | Golden set, held-out set, eval scripts and results |
| `logs/` | Session logs (`D01.md` …) and phase reports (section 4.2) |
| `.claude/skills/session-close/` | Session-close skill: steps (`SKILL.md`) and log format (`log-template.md`) |
| `logs/Reviews.md` | Reviews of each session by the Cowork reviewer. Read; don't edit |
| `docs/Showcase.md` | Case-study material and the publication checklist, kept by the Cowork reviewer. Read; don't edit |
| `pipeline/` | Extraction and tagging code |
| `backend/` | Supabase database: schema, migrations, search functions |
| `app/` | Next.js web app, including its API routes (crisis check, retrieval, bridging sentence) |

## 7. Background

`../Version0/` holds the project's history (moved there 7 Oct 2026): `PICK_UP_FROM_HERE.md`, `corpus-sources.md`, `claude-context/` and the original `corpus/raw/`. Read them only when a decision's reasoning is unclear; this folder is the working home from 7 Oct 2026.
