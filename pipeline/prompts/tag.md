# Tagging prompt (v1, locked 7 Oct 2026 for the bulk run, Plan Day 6)

You are tagging passages for WhoLLSome. A person types a mood or situation; the app answers with one verbatim passage from wisdom literature. Your tags help search find the right passage and let us measure what the corpus covers.

## 1. Read first

`pipeline/prompts/taxonomy.md` holds every allowed tag with its definition and boundary. Use **only** tags from it, spelled exactly as written. When two tags seem to fit, use the boundary lines to choose; pick both only if the passage truly does both.

## 2. For each passage, give

| Field | Rule |
| --- | --- |
| `feelings` | 1–3 fine tags (taxonomy section 2): the feeling a reader is **in** when this passage would help them, not the feeling it leaves them with |
| `themes` | 1–3 fine tags (section 3): what the passage is about |
| `situations` | 0–3 tags (section 4): what might be happening in the reader's life |
| `tone` | 1–2 tags (section 5) |
| `faith` | exactly one of `secular`, `spiritual`, `devotional` (section 6) |
| `keywords` | 0–3 free words or short phrases the lists miss (e.g. a vivid image, a named concept) |
| `safety` | exactly one tag from section 7, plus `safety_reason` (one sentence) unless it is `none` |
| `when_helps` | One plain sentence, max 25 words: who this passage would help, and when. Describe the reader, never quote the passage |

Judge the passage **as a reader would meet it**, alone and out of context. Order tags by strength, strongest first.

## 3. Output

Write one JSON file at the path you were given:

```json
{"tags": [
  {"id": "pp001", "feelings": ["..."], "themes": ["..."], "situations": [], "tone": ["..."],
   "faith": "secular", "keywords": [], "safety": "none", "safety_reason": "", "when_helps": "..."}
]}
```

Every input passage gets exactly one entry. No other output in the file.
