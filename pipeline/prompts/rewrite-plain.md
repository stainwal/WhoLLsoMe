# Plain-version rewrite prompt (v1, 12 Oct 2026, Plan Day 16)

You are rewriting weak plain-language versions for WhoLLsoMe. A person types a mood or situation; the app answers with verbatim passages from wisdom literature, each shown with a stored plain version first (labelled "In plain words"). An AI judge scored the current plain version of each passage below 4 of 5 for faithfulness. Write a new one.

## 1. Input

One JSON line per passage: `id`, `source`, `display` (its location), `text` (the passage as shown, verbatim), `old_plain` (the current plain version) and `issue` (the judge's complaint about it).

## 2. The rule that matters most

**Keep the passage's conclusion or point, not just its set-up.** Many passages open with a picture, a question, a parable or a complaint and only make their point at the end ("In the same way…", "So…", "But…", the answer to the question, the condition attached to a promise). The plain version must carry that point. If space is short, compress the set-up, never the point. A reader who sees only the plain version must come away with what the passage concludes.

## 3. The other rules (unchanged from the enrichment prompt)

- One or two sentences, **at most 50 words**, in today's everyday English, saying what the passage says.
- Same core idea, same stance, nothing added: no advice the passage does not give, no doctrine it does not state, no softening of a hard saying, no claims about who it is for.
- Keep conditions and qualifiers that change the meaning ("only if…", "unless…", "if you don't go higher…").
- Keep the passage's own frame: if it speaks to God, of the Self, of karma or the Buddha's path, say so plainly rather than making it secular. If it addresses God directly, keep the address ("You", "Lord"), don't turn it into third person.
- Address the reader ("you") only if the passage does.
- Do not quote the passage, and do not start with "This passage" or "The author".
- Use the judge's `issue` as a pointer to what went wrong, but check it against the text yourself; the passage, not the judge, is the authority.

## 4. Output

Write one JSON file (UTF-8) at the path you were given:

```json
{"items": [
  {"id": "...", "plain": "..."}
]}
```

Every input passage gets exactly one item. No other output in the file.
