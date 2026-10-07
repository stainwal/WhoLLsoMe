# Bulk run log

Usage readings (read by Claude via the app's usage API) and dispatch events. Session = 5-hour window; Weekly = all models.

| Time (IST) | Event | Session | Weekly |
| --- | --- | --- | --- |
| 7 Oct 22:07 | Before run | 3% | 46% |
| 7 Oct 22:09 | Wave 1: 6 extraction helpers, 24 chunks, 56,849 words (Gita x2, Psalms 1-8); tag batch t0001 (Dhammapada, 77 passages) | — | — |
| 7 Oct ~22:08 | First helper done (gita-siva 005-008: 11 passages, 92.8k helper tokens, 38 s) | 6% | 46% |
| 7 Oct ~22:12 | ~10 helpers done or running; first 2 tag batches | 9% | 47% |
| 7 Oct ~22:14 | Priority sources (tier 1) fully extracted | 12% | 48% |

## Helper notes (for the session log)

- meditations 007-014 helper left out parts of 000333 and all of 000351-000352 as "welcoming death" at extraction. Policy says keep and tag `welcomes-death`. From ~22:13 every extraction helper is told not to filter for safety.
- avot helper: a few passages start after a speaker lead-in ("He used to say:"), e.g. avot 1:14, 3:17, 4:3.
- as-a-man-thinketh helper skipped units 000021, 000029, 000033-000035 as possibly blaming people for poverty or illness (also a safety-style filter at extraction).
- japji-macauliffe-002 passage from uid 000068 carries source OCR errors ("T have", "2 commotion"). Copied verbatim; review before it can be shown.
| 7 Oct ~22:20 | Tier 2 under way (Emerson done, Walden/Chuang Tzu running) | 27% | 50% |
| 7 Oct 22:23 | Chuang Tzu, Walden, Emerson, Schopenhauer done | 31% | 51% |
| 7 Oct 22:29 | Tiers 1-2 extracted (except Rumi etc. in tier 4); Seneca started | 42% | 52% |
- seneca-033 helper kept Letter 70 unit 001010 (argues for suicide, "Live, if you so desire; if not...") and flagged it for tagging. Safety spot-check: confirm the tagger marks it endorses-suicide.
- t0012 tagger: walden-thoreau-044-p03 ("Shall a man go and hang himself...") tagged none because it argues against suicide; worth a human look.
- Safety spot-check passed: seneca-033-p01 (Letter 70, 001010) tagged endorses-suicide and cut. t0016-t0017 cut 8 Seneca passages as endorses-suicide.
- Bible narrative books yield ~0-2 passages per 2,500-word chunk (Genesis-Judges). From 22:39 the remaining Bible is reordered: wisdom, prophets and New Testament first (list in prefer.txt), histories after. Order only; nothing skipped.
| 7 Oct 22:49 | Window 1 paused: 4,058 verified passages, 3,998 tagged; Bible narrative, prophets, apocrypha mostly done | 84% | 59% |
- Likely over-cut for Shailesh to check: bib-2maccabees-003-p01 (Eleazar's martyrdom) tagged endorses-suicide by the tie-break rule.
| 8 Oct 00:51 | Window 2 started: 8 helpers (rest of Bible, Digha Nikaya) | 0% | 60% |
- mn-123 helper kept MN 144 unit 004994 (friends plead with Channa not to take his life); check its safety tag.
- SuttaCentral normalised text still carries '<j>' markup in places (e.g. 005788); strip for display or fix the parser before freeze.
- SN rejects (6, sn-001..005): helper dropped opening curly quotes on verse dialogues; verbatim check rejected them as designed. Not repaired.
- mn-123-p02 (MN 144, "Please don't commit suicide... keep going") tagged safety none; contains the word suicide; Shailesh to decide whether it may be shown.
- '<j>' markup: 191 SuttaCentral units contain it; an-010..027 helper skipped verses containing it (e.g. 013473, 014031). Follow-up: fix the SuttaCentral parser, re-normalise, re-extract affected chunks.
- Likely over-cut: rumi-masnavi-whinfield-019-p06 (Sufi 'seek annihilation' = ego-death, not suicide) tagged endorses-suicide by tie-break rule.
| 8 Oct 01:12 | Run complete: 1,720/1,720 chunks, 5,029 passages, all tagged | see log | see log |
