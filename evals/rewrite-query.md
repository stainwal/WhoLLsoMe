# Query rewrite prompt (v1, 13 Oct 2026, Plan section 4.4, experiment 3)

WhoLLsoMe answers a person's statement with one passage from wisdom literature (scripture, Stoic and other philosophy, poetry, aphorisms), found by meaning-based search over the passages and their plain-language versions. People write in everyday, often messy language; the passages speak in older, more general language. Your job is to bridge the two **for the search engine only**: the person never sees what you write.

For each statement, write a search query of 25–45 words that names:

1. the situation in general terms (e.g. "losing a job through no fault of one's own", not "got laid off from my tech job");
2. the feelings, using plain emotional words (grief, shame, fear, resentment, loneliness…);
3. the kind of wisdom that would speak to it (e.g. "worth not measured by fortune", "grief as the price of love", "patience with what can't be changed").

Write in calm, general language close to how wisdom literature talks about such things. No advice to the person, no "you", no names, places or other details from the statement, and no diagnosis. Literal slang is translated to its meaning ("I'm dead" said laughing means amusement, not death).

## Input and output

Input: one JSON line per statement, with `id` and `statement`. Write one JSON file (UTF-8) at the path you were given:

```json
{"rewrites": [{"id": "H02", "query": "..."}]}
```

Every statement gets exactly one rewrite. No other output in the file.
