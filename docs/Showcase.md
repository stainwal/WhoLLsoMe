# Showcase

Material for the case study and for publishing the code and the build process. Kept by the Cowork reviewer from session logs (part 6, "Showcase note") and reviews (`../logs/Reviews.md`).

## 1. The story in one paragraph

A wisdom-literature app built mostly by AI at about one hour a day. The user describes a situation; the app answers only with verbatim passages from 33 public-domain and openly licensed sources, plus one generated sentence linking each to what the user said. The constraint is the product: no chatbot flattery, no invented wisdom. The process is the second story: Cowork plans and reviews, Claude Code builds, and session logs, a session-close skill, a token budget and published evals keep it honest.

## 2. Story points

Newest last. One line each; the source is the session log or review.

| Date | Point | Source |
| --- | --- | --- |
| 7 Oct | Plan pivoted three times in one day (iOS → Android → web) once the costs of each path were laid out; web removed Google Play's 14-day closed test from the critical path | Decisions |
| 7 Oct | Chose the full 33-source corpus over a quick 8-source cut: "make sure it actually works" beat speed | Decisions |
| 7 Oct | Built the operating system for an AI-led build before writing code: CLAUDE.md brief, session logs with evidence, a session-close skill, a token budget Claude drives | D01, Reviews |
| 7 Oct | Normalised 4.18M words from 33 sources in 11 formats, every parser checked word for word against its source | D04 |
| 7 Oct | Normalisation caught two sources misattributed as public domain (*Way of Perfection* is the 1964 Peers translation; *Brother Lawrence* is a 2002 edition) | D02 |
| 7 Oct | Tag taxonomy grounded in ICD-10 Z codes, DSM-5, Crisis Text Line data, the VIA classification and WHO safe-messaging guidance rather than invented | D02 |
| 7 Oct | Verbatim check: 135 of 135 pilot passages matched their source exactly; the model never paraphrased | D04 |
| 7 Oct | Sonnet vs Opus on the same text: Sonnet picked 49 passages, Opus 86, at indistinguishable cost | D04 |
| 7 Oct | First cost estimate ("2–3 weeks of allowance for the corpus") was wrong because it ignored prompt caching; measured calibration put a full extraction pass near half a week | D04 |
| 7 Oct | Narrowed harm review to a single safety field after seeing that broad filtering would strip the corpus of hard but valuable passages | D02 |
| 7–8 Oct | Full corpus (4.10M words, 33 sources) extracted and tagged unattended in about an hour of active time, overnight: 5,029 passages, 99.86% verbatim | D07 |
| 7–8 Oct | Actual cost was 20% of a week's allowance against a predicted 57%: the measured calibration replaced the estimate | D07 |
| 7–8 Oct | The safety field cut all 12 Seneca "open door" passages, including the test case the reviewer named in advance (Letter 70) | D07, Reviews |
| 8 Oct | Corpus phase finished about 6 days ahead of plan; the human-written test set became the critical path | Reviews |
| 9 Oct | Test sets split by author: 32 human statements kept untouched for the headline score; 80 more compiled from 304 statements four models researched from real public posts, after removing duplicates, prompt echoes and out-of-scope legal questions | Agent set |
| 9 Oct | All four research models reused the prompt's own example phrases, a small lesson in how examples leak into generated data | Agent set |
| 9 Oct | Phase 1 (corpus) closed 12 days ahead of plan: 4,929 showable passages, deduplicated (83 of 84 duplicates were stock repeats in the Buddhist Nikayas), every display fix reversible | D12, Phase 1 report |
| 11 Oct | Human review of 40 random passages: 95% kept. The two cuts and the notes all said the same thing: short, graspable wisdom lands; dense passages don't. That one finding reshaped the product: a plain-language version for every passage, an Explain button, Surprise me, and a ranking boost for aphorisms | Day 5 review |

## 3. Tracker

Updated at each review.

| As of | Sessions | Plan days done | Your time (approx.) | Weekly allowance used on the project | Money spent |
| --- | --- | --- | --- | --- | --- |
| 7 Oct, after Session 2 | 2 | 1, 2, 4 (6 in part) | ~4 hours incl. planning | ~3 points (pilot) plus planning chats | $0 |
| 8 Oct, after Session 3 | 3 | 1, 2, 4, 6, 7–11 | ~6 hours incl. planning | ~24 points (pilot + full run) plus planning chats | $0 |
| 9 Oct, after Session 4 | 4 | 1–4, 6–14 (5 drawn, not yet reviewed) | ~9 hours incl. test sets | ~24 points plus planning chats | $0 |

## 4. Screenshots and media to capture

- [ ] Usage screen before and after the first bulk run (cost story)
- [ ] A pilot passage with its tags (what the pipeline produces)
- [ ] Eval results table, first baseline and final (Days 17 and 32)
- [ ] The app: input, a passage with its bridging sentence, Next/Back, the crisis screen
- [ ] A session log and a review side by side (the process story)

## 5. Publication checklist

Clear every item before anything goes public. Status as of 12 Oct 2026, afternoon (Day 16, `logs/D16.md`).

| # | Item | Status |
| --- | --- | --- |
| 1 | **Copyrighted editions:** *Way of Perfection* (Peers, 1964) and *Brother Lawrence* (Lightheart, 2002) are kept on Shailesh's call. They cannot ship in a public repo or on a public site without permission or replacement. Same for the Sivananda Gita (Tier B GRAY). | **Repo: cleared.** All three are out of git and out of every commit (filter-repo, 12 Oct); a scan of all 6,414 file versions in history found no restricted text. They stay on disk for the pipeline (`restricted = true` in `pipeline/sources.toml`); a pre-commit hook and a session-close step block them from coming back. **Public site: open.** 147 of the 5,540 shown passages come from them. |
| 2 | **Clean public repo:** publish from a new repository with fresh history; the private repo's history contains the texts above. | **Open again.** History was rewritten in place (Shailesh, 12 Oct; pre-rewrite history in the private `stainwal/WhoLLsoMe-archive`), and the branch history is clean. But GitHub still serves the replaced commits by direct SHA (checked 12 Oct: `d4c50ae`, which holds the restricted texts, and `d2eb907`, which holds the crisis statements). If the repo is made public, they become public too. **Blocks the visibility switch.** Fix: push the clean history to a new repository and make that one public, or ask GitHub Support to purge the unreachable commits. |
| 3 | **Personal details:** the first commit carries the Mac's local email; logs mention the GitHub account and usage readings. Review before release. | **Cleared.** First commit's author and committer set to the GitHub no-reply address; all 17 commits now carry it. History search found no other email or local path. The GitHub account and usage readings stay in the logs as part of the story. |
| 4 | **Secrets scan** across everything published. | **Cleared** (re-run 12 Oct after the crisis scrub). gitleaks 8.30.1 over all 21 commits: no leaks; every commit's author and committer is the GitHub no-reply address. Run again before the visibility switch if more commits land. |
| 5 | **Licences and credits:** choose a code licence (MIT or Apache 2.0); credit Kulp's Pirkei Avot (CC-BY) and the World English Bible per their terms; list every translator. | **Cleared** (12 Oct). `LICENSE`: MIT, © stainwal. README section 7 says the code is MIT and the passages keep their source licences, names the Kulp (CC-BY, with Sefaria link) and WEB credits, and points to the per-source translator and licence table (`docs/Corpus-Policy.md` sections 2–3). |
| 6 | **Crisis test sets and source links:** keep the crisis statements private so the safety check can't be gamed. Never publish `evals/agent-set-provenance.md` (links to real people's posts). | **Cleared in the branch history** (12 Oct). `agent-set-provenance.md` is out of git and history. The 13 crisis statements are in git-ignored `evals/private/crisis.jsonl`, read through `evals/sets.py`; filter-repo replaced the 3 file versions that held them; scan of all 6,429 file versions: 0 with crisis text, 0 with restricted text. The pre-commit hook blocks both. The old commit on GitHub is item 2. |
| 7 | **Claims check:** every number in the case study traces to a log, a review or an eval result. | **README checked** 12 Oct: every figure traced; six corrected. Case study not yet written. |

## 6. Publication plan

- **At launch (Day 33):** a case-study page linked from the launch post.
- **After launch:** the clean public repo, a README for outside readers, and the process files (brief, skill, sample logs) as a template others can reuse.
