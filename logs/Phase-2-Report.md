# Phase 2 Report: retrieval gate (Day 21)

*Written 15 Oct 2026 (session 12), six days ahead of the planned 22 Oct. Covers Days 15–21: enrichment, retrieval, evals, Explain. The gate decision is Shailesh's (Plan section 5.3, D21).*

## 1. Recommendation

**Pass on retrieval and Explain; do not pass on the crisis check yet.** Retrieval clears its bar by a wide margin and Explain clears it on the subscription test. The crisis check caught 12 of 13 crisis statements, one short of the bar of 13. Recommend spending **one** of the three allowed improvement days on the crisis check only (see section 4), then re-running the crisis eval once, on fresh statements as well as the 13. Everything else can move on to Phase 3.

## 2. What was built

- **Corpus:** 5,540 passages a user can be shown, from 39 sources; 147 restricted (never on the public site); 68 hidden from distress. Every passage has a stored plain version (98.1% judged faithful at 4–5 of 5, the 103 weakest rewritten).
- **Database:** Supabase with pgvector; the public key reads one view only (`public_passages`, restricted sources excluded; 16 of 16 checks over SQL and the REST API).
- **Eval harness:** `evals/retrieval.py`, `evals/experiments.py`, `evals/explain.py`, `evals/crisis.py`. Every passage in a scored top 10 is judged before scoring; none counts as a miss by default.
- **Retrieval, Setup B** (chosen 15 Oct by Shailesh's rules): Haiku rewrites the statement into a search query; the statement plus the query is embedded with `voyage-4-lite` and searched against passage text + plain version + "when this helps" line; a small tone prior favours consoling over stern passages.
- **Explain:** Sonnet 5.5, prompt `app/lib/explain-prompt.ts`, endpoint `app/app/api/explain/route.ts` with Turnstile hook, 20-per-hour visitor limit and server-side passage lookup.
- **Crisis check:** `app/lib/crisis-prompt.ts`: narrow phrase patterns, then a Haiku classifier (crisis / borderline / none). Written without looking at the private crisis statements.

## 3. Gate results

| Bar (Plan section 5.3) | Result | Pass? |
| --- | --- | --- |
| Human held-out hit@3 ≥ 70% (23 of 32) | **29 of 32 (91%)**, judge prompt v2 | Yes |
| Crisis 13 of 13 across both sets | **12 of 13**: human 4 of 5, agent 8 of 8. C04 was labelled borderline (passages + "Need help now?" link) instead of crisis | **No** |
| Borderline statements correct either way | H04 and AS57 both borderline | Yes |
| False crisis ≤ 1 of 5 human | 0 of 5 (one look-alike gets the "Need help now?" link) | Yes |
| False crisis ≤ 1 of 8 agent | 1 of 8 (AL01, a kitchen cut: the phrase "cut myself" in the pattern layer; the model said none) | Yes, at the limit |
| Explain rubric pass ≥ 90% | **39 of 40 (97.5%)** on the subscription test; 3 of 5 on the API fidelity sample (see section 5) | Yes, with a caveat |

Reported with no bar (Setup B, judge v2): human held-out hit@10 32 of 32, MRR 0.676, first passage acceptable 15 of 32 (47%), first passage graded 0: **0 of 32**. Agent held-out hit@3 15 of 20 (75%), hit@10 20 of 20, MRR 0.590, first acceptable 7 of 20, first graded 0 2 of 20.

## 4. Known weaknesses

1. **Crisis recall is one short.** One indirect crisis statement read as despair, not risk. The private statements were not used to design the check and must not be used to tune it. Options for the improvement day: map "borderline" to the crisis screen with a "continue to passages" choice (catches anything the model hedges on; costs a few extra helpline screens); or run the crisis check on Sonnet; or both. Re-test on newly written statements, so the 13 stay a fair test.
2. **The phrase layer over-fires.** "Cut myself" caught a kitchen accident. Narrow it to self-harm wording, or let the model overrule a pattern hit when it says "none" with high confidence.
3. **Explain runs longer through the API** than through the subscription (median 81 vs 54 words); 1 of 5 API notes went over 90 words and 1 guessed the person's feelings. The 97.5% may overstate real use. A tighter length rule and an API-measured re-run of the 40 (about $0.13) would settle it.
4. **Judge v2 is stricter.** On the same 1,250 pairs, v2 accepts 45.8% where v1 accepted 52.2% (82.9% agreement). First-passage-acceptable drops (human held-out 24 → 15) mostly because passages that only mirror the problem lose credit; hit@3 barely moves (30 → 29).
5. **Rewrites vary run to run.** The same 5 statements through the API gave a different first passage for 2 of 5 than the subscription rewrites, so results will differ slightly between visits.
6. **Coverage gaps** in the corpus (pet loss, partnership, money worries) still show as weak first passages.

## 5. Cost (measured on 6 API calls each where available)

| Item | Per call | Per 1,000 |
| --- | --- | --- |
| Explain, Sonnet 5.5 (913 in, 134 out tokens, measured) | $0.0032 | **$3.16** |
| Explain, Haiku 5.5 (same tokens, estimated) | $0.00016 | $0.16 |
| Query rewrite, Haiku 5.5 (466 in, 104 out, measured) | $0.0001 | **$0.10** |
| Crisis check, Haiku 5.5 (about 650 in, 5 out, estimated) | $0.00007 | $0.07 |
| Query embedding, Voyage | — | under $0.01 |

A search costs about $0.17 per 1,000; Explain only runs when pressed. API spend for all of Day 20: **$0.0195** (12 calls; `evals/results/api-spend.jsonl`).
