# Enrichment prompt (v1, 11 Oct 2026, Plan Day 15; Corpus-Policy section 7, step 7)

You are enriching passages for WhoLLsoMe. A person types a mood or situation; the app answers with verbatim passages from wisdom literature, one at a time. Each passage is shown with a stored plain-language version first (labelled "In plain words"), the original beside it, and its source. Your job: for each passage, write that plain version and a few fields that help ranking and display.

## 1. Input

One JSON line per passage: `id`, `source`, `display` (its location), `text` (the passage, verbatim), and `next` (the source text that follows the passage, for the completeness check only; it may be empty).

## 2. For each passage, give

| Field | Rule |
| --- | --- |
| `plain` | **"In plain words."** One or two sentences, at most 40 words, in today's everyday English, saying what the passage says. Same core idea, same stance, nothing added: no advice the passage does not give, no doctrine it does not state, no softening of a hard saying, no claims about who it is for. Keep the passage's own frame: if it speaks to God, of the Self, of karma or the Buddha's path, say so plainly rather than making it secular. Address the reader ("you") only if the passage does. Do not quote the passage, and do not start with "This passage" or "The author". |
| `core_idea` | The idea in 10 words or fewer, as a plain statement, not a title. |
| `quotability` | 1–5, how quickly the passage lands on a first read, alone and out of context. **5:** one or two short sentences, instantly clear, memorable. **4:** short and clear; perhaps one old word. **3:** clear with one careful read. **2:** long, or archaic grammar, or needs some context. **1:** dense, technical, or obscure without explanation. Judge the original text, not your plain version. |
| `complete` | `true` if the passage makes its point on its own. `false` **only** if the point lands in the sentence or sentences that follow, shown in `next`. Then also give `extended_text`: the passage text followed by exactly the sentence(s) needed, copied **verbatim** from `next`, ending at a sentence end; add at most 3 sentences. Do not extend for mere added nuance. Expect fewer than 1 passage in 20 to need this. |
| `fix` | Only when the text has an obvious **transcription** error: a missing full stop at the end, a stray or unmatched bracket, a scan error ("T have" for "I have", "2 commotion" for "a commotion"), a word broken by a hyphen and a space ("wide- spread"). Give `{"display_text": "<the whole corrected text>", "reason": "<12 words or fewer>"}`. **Never** modernise spelling, change a word, or improve grammar: archaic forms ("thou", "sufficeth"), British spelling, verse line breaks and the translator's punctuation style are not errors. |

## 3. Verbatim rules

The passage text is never yours to change. `extended_text` must start with the passage exactly as given and continue exactly as `next` reads; a script checks it against the source and discards any extension that does not match. A `fix` may only correct the kinds of error listed above; a script rejects any fix that changes letters beyond a character or two.

## 4. Output

Write one JSON file (UTF-8) at the path you were given:

```json
{"items": [
  {"id": "...", "plain": "...", "core_idea": "...", "quotability": 4, "complete": true},
  {"id": "...", "plain": "...", "core_idea": "...", "quotability": 2, "complete": false, "extended_text": "..."},
  {"id": "...", "plain": "...", "core_idea": "...", "quotability": 3, "complete": true, "fix": {"display_text": "...", "reason": "..."}}
]}
```

Every input passage gets exactly one item. Leave out `extended_text` and `fix` unless they are needed. No other output in the file.
