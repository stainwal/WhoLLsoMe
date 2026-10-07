# Extraction prompt (v1, locked 7 Oct 2026 for the bulk run, Plan Day 6)

You are extracting passages for WhoLLSome. A person types a mood or situation, and the app answers with **one verbatim passage** from wisdom literature. Your job: read one chunk of a source and pick out the passages that could be that answer.

## 1. What earns a place

A passage qualifies only if all of these hold (Corpus-Policy section 4):

1. **Self-contained.** It makes sense to a stranger with no surrounding context: no dangling "he", "this", "therefore", "such a one" whose referent is outside the passage.
2. **Length.** Roughly 1–8 sentences (verse: 2–16 lines). It starts at the start of a sentence (or verse) and ends at the end of one. Never cut mid-sentence.
3. **Speaks to a human situation:** grief, failure, anger, fear, loss, love, work, purpose, change, loneliness, envy, guilt, ageing, decisions, and the like. **Spiritual seeking is a human situation too:** teaching on practice, meditation, prayer, the spiritual path, the true self and liberation qualifies when a thoughtful reader outside that tradition could follow it. Skip narrative, lists of names, law and ritual detail, technical argument, and lines that need specialist vocabulary or doctrine explained to make sense.
4. **Selective by design.** Most text does not qualify. Picking nothing from a chunk is a valid answer. Prefer the strongest, clearest passages; do not pick near-duplicates of each other.

## 2. Verbatim, exactly

- Copy the text **exactly** as it appears in the chunk: same words, spelling, punctuation, capitalisation and quote marks (curly ’ “ ” stay curly). Do not modernise, trim, fix typos, or join with "...".
- A passage may span several consecutive units; `start_uid` is the first unit it draws from and `end_uid` the last. You may start or end partway through a unit, but only at a sentence boundary.
- Do not include the `[uid]` markers or the `(location)` lines; they are not part of the text.
- For verse, keep the line breaks as `\n`.
- A script checks every passage against the source. Anything that does not match exactly is thrown away.

## 3. Output

Write a single JSON file (UTF-8) at the path you were given:

```json
{"chunk_id": "<id>", "passages": [
  {"start_uid": "<uid>", "end_uid": "<uid>", "text": "<verbatim text>", "note": "<≤12 words: the human situation it speaks to>"}
]}
```

No other output in the file. The `note` is for a human reviewer; keep it plain.
