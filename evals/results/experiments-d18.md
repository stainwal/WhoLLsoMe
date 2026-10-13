# Retrieval experiments (Days 18–19)

*13 Oct 2026. Every setup's top 10 fully judged by the Opus 5.5 judge of record before scoring (6,610 judged pairs in all). Columns per group: **top-1 ok** (first passage acceptable), **top-1 = 0** (first passage graded 0: off-topic or lands badly), **hit@3**. Tuning is read on the agent golden set (60); held-out sets are reported, not tuned on. On 20–32 statements one statement is 3–5 points, so gaps under about 3 statements are noise. Baseline row 1 is the Day 17 run; row 2 is the same search after the 5 harsh passages were hidden.*

## 1. Results

### 1.1 Baseline

| Setup | Golden (60): top-1 ok / top-1 = 0 / hit@3 | Agent held-out (20) | Human held-out (32) |
| --- | --- | --- | --- |
| `voyage-4-lite/text+plain@d17` | 31 / 11 / 50 | 9 / 6 / 12 | 19 / 6 / 29 |
| `voyage-4-lite/text+plain` | 31 / 11 / 50 | 9 / 4 / 12 | 21 / 4 / 29 |

### 1.2 Experiment 4: hybrid (meaning + keyword, reciprocal rank fusion)

| Setup | Golden (60): top-1 ok / top-1 = 0 / hit@3 | Agent held-out (20) | Human held-out (32) |
| --- | --- | --- | --- |
| `hybrid/rrf` | 21 / 18 / 39 | 3 / 9 / 7 | 17 / 2 / 26 |
| `hybrid/rrf-kw0.5` | 21 / 19 / 42 | 4 / 5 / 9 | 17 / 3 / 26 |

### 1.3 Experiment 7: quotability boost

| Setup | Golden (60): top-1 ok / top-1 = 0 / hit@3 | Agent held-out (20) | Human held-out (32) |
| --- | --- | --- | --- |
| `quot/0.01` | 32 / 10 / 49 | 8 / 3 / 15 | 19 / 4 / 28 |
| `quot/0.02` | 30 / 9 / 49 | 7 / 4 / 12 | 18 / 5 / 26 |
| `quot/0.04` | 26 / 14 / 45 | 7 / 5 / 12 | 14 / 5 / 27 |

### 1.4 Experiment 3: query rewriting (rewrites written offline by Opus 5.5)

| Setup | Golden (60): top-1 ok / top-1 = 0 / hit@3 | Agent held-out (20) | Human held-out (32) |
| --- | --- | --- | --- |
| `rewrite/only` | 30 / 11 / 47 | 13 / 1 / 18 | 21 / 3 / 27 |
| `rewrite/concat` | 34 / 8 / 49 | 9 / 3 / 15 | 15 / 2 / 31 |
| `rewrite/fuse` | 31 / 10 / 48 | 10 / 3 / 15 | 20 / 1 / 30 |

### 1.5 Experiment 6: faith framing

| Setup | Golden (60): top-1 ok / top-1 = 0 / hit@3 | Agent held-out (20) | Human held-out (32) |
| --- | --- | --- | --- |
| `faith/0.03` | 31 / 11 / 49 | 8 / 4 / 14 | 20 / 5 / 31 |
| `faith/0.06` | 31 / 12 / 48 | 8 / 4 / 13 | 21 / 5 / 31 |

### 1.6 Experiment 1: embedding model

| Setup | Golden (60): top-1 ok / top-1 = 0 / hit@3 | Agent held-out (20) | Human held-out (32) |
| --- | --- | --- | --- |
| `voyage-4/text+plain` | 29 / 14 / 51 | 10 / 3 / 16 | 19 / 2 / 30 |

### 1.7 Experiment 2: what gets embedded

| Setup | Golden (60): top-1 ok / top-1 = 0 / hit@3 | Agent held-out (20) | Human held-out (32) |
| --- | --- | --- | --- |
| `voyage-4-lite/text` | 23 / 12 / 44 | 7 / 5 / 13 | 15 / 4 / 26 |
| `voyage-4-lite/plain` | 31 / 12 / 43 | 12 / 4 / 15 | 20 / 1 / 31 |
| `voyage-4-lite/text+plain+when` | 35 / 7 / 49 | 9 / 5 / 17 | 20 / 2 / 30 |

### 1.8 Added: tone prior (from golden-set labels)

| Setup | Golden (60): top-1 ok / top-1 = 0 / hit@3 | Agent held-out (20) | Human held-out (32) |
| --- | --- | --- | --- |
| `tone/0.1` | 34 / 11 / 50 | 10 / 4 / 14 | 21 / 5 / 30 |
| `tone/0.2` | 35 / 11 / 50 | 11 / 4 / 14 | 18 / 4 / 29 |
| `tone/0.4` | 31 / 9 / 49 | 10 / 5 / 16 | 16 / 4 / 27 |
| `rewrite-only+tone/0.2` | 34 / 8 / 50 | 13 / 2 / 18 | 23 / 2 / 28 |
| `rewrite-concat+tone/0.2` | 38 / 7 / 52 | 11 / 3 / 16 | 21 / 0 / 32 |

### 1.9 Combinations

| Setup | Golden (60): top-1 ok / top-1 = 0 / hit@3 | Agent held-out (20) | Human held-out (32) |
| --- | --- | --- | --- |
| `when+tone/0.1` | 37 / 6 / 53 | 11 / 5 / 16 | 23 / 2 / 30 |
| `when+tone/0.2` | 37 / 8 / 53 | 11 / 5 / 18 | 21 / 1 / 30 |
| `when+rewrite-concat` | 28 / 7 / 49 | 12 / 1 / 18 | 18 / 1 / 28 |
| `when+rewrite-concat+tone/0.2` | 39 / 5 / 52 | 11 / 1 / 18 | 19 / 1 / 29 |
## 2. What was learned

1. **Hybrid search hurts** (golden top-1 ok 31 → 21). The keyword side matches words literally ("dead", "murder", "cheated") and drags in off-topic passages; the low overlap with meaning-based search (3.5 of 10) was noise, not missed matches.
2. **Quotability and faith framing change nothing** that clears noise. A strong quotability boost (0.04) hurts.
3. **Embedding the "when this helps" line** (passage + plain version + when-helps) is the best single change: golden top-1 ok 31 → 35, top-1 graded 0 11 → 7. Text alone is clearly worse (23); the larger `voyage-4` model is no better than `voyage-4-lite`.
4. **Tone matters.** On golden-set labels, passages tagged *stern* were acceptable 6% of the time and graded 0 61%; *consoling* 46% and 19%. A small tone prior lifts top-1 acceptable (31 → 34–35).
5. **Query rewriting** helps the short, messy agent statements (agent held-out top-1 = 0: 4 → 1) but is mixed on the long human statements. The rewrites were written offline by Opus 5.5; at runtime this needs an LLM call per query (Haiku or Sonnet, experiment 5, Day 20), so its result here is a ceiling, not a measured runtime cost.
6. **Best two candidates** (picked on golden, then read on held-out):
   - `when+tone/0.1`, no LLM at query time: golden 37 / 6 / 53; agent held-out 11 / 5 / 16; human held-out **23 / 2 / 30** (baseline 21 / 4 / 29, Day 17 19 / 6 / 29).
   - `when+rewrite-concat+tone/0.2`, needs a runtime rewrite: golden **39 / 5 / 52**; agent held-out 11 / **1** / 18; human held-out 19 / 1 / 29.

## 3. Cost

- Judging: 3,536 new Opus pairs this session, about 3% of the weekly limit (41% → 44%).
- Embeddings: 4 extra setups of 5,540 passages on Voyage's free allowance; database 53 → 174 MB of the 500 MB free tier. Unused setups can be dropped once one is chosen.
