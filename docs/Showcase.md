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

## 3. Tracker

Updated at each review.

| As of | Sessions | Plan days done | Your time (approx.) | Weekly allowance used on the project | Money spent |
| --- | --- | --- | --- | --- | --- |
| 7 Oct, after Session 2 | 2 | 1, 2, 4 (6 in part) | ~4 hours incl. planning | ~3 points (pilot) plus planning chats | $0 |

## 4. Screenshots and media to capture

- [ ] Usage screen before and after the first bulk run (cost story)
- [ ] A pilot passage with its tags (what the pipeline produces)
- [ ] Eval results table, first baseline and final (Days 17 and 32)
- [ ] The app: input, a passage with its bridging sentence, Next/Back, the crisis screen
- [ ] A session log and a review side by side (the process story)

## 5. Publication checklist

Clear every item before anything goes public.

1. **Copyrighted editions:** *Way of Perfection* (Peers, 1964) and *Brother Lawrence* (Lightheart, 2002) are kept on Shailesh's call. They cannot ship in a public repo or on a public site without permission or replacement. Same for the Sivananda Gita (Tier B GRAY).
2. **Clean public repo:** publish from a new repository with fresh history; the private repo's history contains the texts above.
3. **Personal details:** the first commit carries the Mac's local email; logs mention the GitHub account and usage readings. Review before release.
4. **Secrets scan** across everything published.
5. **Licences and credits:** choose a code licence (MIT or Apache 2.0); credit Kulp's Pirkei Avot (CC-BY) and the World English Bible per their terms; list every translator.
6. **Crisis test set:** keep private so the safety check can't be gamed.
7. **Claims check:** every number in the case study traces to a log, a review or an eval result.

## 6. Publication plan

- **At launch (Day 33):** a case-study page linked from the launch post.
- **After launch:** the clean public repo, a README for outside readers, and the process files (brief, skill, sample logs) as a template others can reuse.
