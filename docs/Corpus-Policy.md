# Corpus Policy

Rules for what goes into the corpus, how passages are extracted, how they're reviewed and how they're credited. Provenance for every source is in `../corpus/manifest.md`.

## 1. Sourcing policy (v2, decided 24 Aug 2026)

The ancient text is never the copyright problem; the translation is.

- **Tier A (default):** US public domain, or a verified open licence (CC0, CC-BY).
- **Tier B (stopgap):** a modern translation that is freely circulated, has a named translator and carries no stated restriction. Allowed only when no adequate Tier A option exists. Marked **GRAY**, credited in-app, excerpts kept modest, replaced before any real monetisation.
- **Never:** anonymous or unattributed translations; anything under an NC or ND licence; commercially active famous translations (Mitchell, Barks, Peers, Easwaran, Hays, Blakney).
- **Rejected sources, don't re-propose:** Carl Jung, Zen classics, *Black Elk Speaks*, the "Chief Seattle speech", the "Prayer of St Francis", *Man's Search for Meaning*, *Desiderata*, Bahá'í writings, the nitnemsahib.com Japji.

## 2. Sources in v1 (33)

All folders in `../corpus/source/`. Word counts from the manifest; SuttaCentral is a JSON tree, so its count includes markup.

| Folder | Tradition | Work | Translator | Licence | Words |
| --- | --- | --- | --- | --- | --- |
| gita-arnold-song-celestial | Hinduism | Bhagavad Gita (primary) | Edwin Arnold, 1885 | US PD | 23,215 |
| gita-sivananda | Hinduism | Bhagavad Gita (readable prose) | Swami Sivananda | **GRAY (Tier B)** | 19,963 |
| upanishads-paramananda | Hinduism | Upanishads | Swami Paramananda, 1919 | US PD | 20,669 |
| vivekananda | Hinduism | 14 originally-English works | Vivekananda (original English) | US PD | ~540,000 |
| suttacentral-sujato | Buddhism | Dhammapada + four Nikayas | Bhikkhu Sujato, 2018 | CC0 | ~1.8M (JSON) |
| light-of-asia-arnold | Buddhism | The Light of Asia | Edwin Arnold (original English) | US PD | 37,629 |
| tao-te-ching-legge | Taoism | Tao Te Ching | James Legge, 1891 | US PD | 13,674 |
| chuang-tzu-giles | Taoism | Chuang Tzu | Herbert Giles, 1889 | US PD | 116,070 |
| meditations-long | Stoicism | Meditations | George Long, 1862 | US PD | 45,565 |
| epictetus-enchiridion | Stoicism | Enchiridion | T.W. Higginson, 1865 | US PD | 14,129 |
| epictetus-discourses-long | Stoicism | Discourses (selection) + Encheiridion | George Long, 1877 | US PD | 65,630 |
| seneca-letters-gummere | Stoicism | Letters to Lucilius (124) | Richard Gummere, 1917–25 | US PD | 247,444 |
| plato-apology-jowett | Greek philosophy | Apology | Benjamin Jowett | US PD | 19,097 |
| plato-phaedo-jowett | Greek philosophy | Phaedo | Benjamin Jowett | US PD | 45,789 |
| aristotle-ethics | Greek philosophy | Nicomachean Ethics | D.P. Chase, 1847 | US PD | 115,592 |
| pirkei-avot | Judaism | Pirkei Avot | Joshua Kulp (Mishnah Yomit) | **CC-BY** | 9,117 |
| bible-web | Christianity / Judaism | World English Bible (complete) | WEB | Public domain | 991,344 |
| imitation-of-christ-benham | Christianity | The Imitation of Christ | William Benham, 1874 | US PD | 63,729 |
| brother-lawrence | Christianity | The Practice of the Presence of God | PD translation | US PD | 14,109 |
| augustine-confessions-pusey | Christianity | Confessions | Edward Pusey, 1838 | US PD | 114,873 |
| teresa-interior-castle | Christianity | Interior Castle | Benedictines of Stanbrook, 1921 | US PD | 90,288 |
| teresa-way-of-perfection | Christianity | Way of Perfection | Benedictines of Stanbrook, 1911 | US PD | 83,771 |
| eckhart-sermons-field | Christianity | Sermons | Claud Field, 1909 | US PD | 12,871 |
| rumi-masnavi-whinfield | Sufism | Masnavi (abridged, 6 books) | E.H. Whinfield, 1887 | US PD | 104,350 |
| prophet-gibran | Sufism-adjacent | The Prophet | Kahlil Gibran (original English) | US PD | 15,725 |
| japji-macauliffe | Sikhism | Japji Sahib | M.A. Macauliffe, 1900 | US PD | 4,572 |
| soul-of-the-indian-eastman | Native American | The Soul of the Indian | Charles Eastman (original English) | US PD | 20,183 |
| american-indian-stories-zitkala | Native American | American Indian Stories | Zitkala-Ša (original English) | US PD | 35,543 |
| emerson-essays | Modern West | Essays, First and Second Series | Emerson (original English) | US PD | 132,642 |
| walden-thoreau | Modern West | Walden + Civil Disobedience | Thoreau (original English) | US PD | 118,840 |
| schopenhauer-wisdom-of-life | Modern West | The Wisdom of Life | T. Bailey Saunders, 1890 | US PD | 41,433 |
| schopenhauer-counsels-maxims | Modern West | Counsels and Maxims | T. Bailey Saunders, 1890 | US PD | 48,768 |
| as-a-man-thinketh-allen | Modern West | As a Man Thinketh | James Allen (original English) | US PD | 10,601 |

### 2.1 Excluded on purpose

- **bible-kjv:** duplicate of WEB; would compete in search with near-identical verses.
- **gita-besant-das:** OCR quality unusable; superseded by Sivananda.
- **Phase 2 (not yet acquired):** Dark Night of the Soul (David Lewis only), Macauliffe *Sikh Religion* selections, Epicurus (Hicks), Curtis *The Indians' Book*.

## 3. Credits shown in the app

- Every passage shows its work, location (chapter, verse, letter) and translator.
- **Pirkei Avot:** "Mishnah Yomit by Dr. Joshua Kulp", with a link to Sefaria (CC-BY requires it).
- **Gita (Sivananda):** "Translation by Swami Sivananda" (GRAY).
- **World English Bible:** credit as "World English Bible"; follow ebible.org's naming guidance (the name is a trademark; the text is free).
- An About page lists all 33 sources with translators.

## 4. Extraction rules

A passage earns a place only if it stands alone and speaks to a human situation.

1. **Self-contained:** makes sense with no surrounding context; no dangling "he", "this" or "therefore".
2. **Length:** roughly 1–8 sentences. Never cut mid-sentence; never alter wording.
3. **Speaks to a situation:** grief, failure, anger, fear, loss, love, work, purpose, change, loneliness and the like. Narrative, genealogy, law codes, ritual detail and technical argument are skipped.
4. **Selective by design:** dense sources (Aristotle, Augustine, the Nikayas, most of the Bible) will yield a small fraction of their text. That's expected.
5. **Location kept:** every passage records its source folder and exact location so it can be traced back.
6. **One Gita voice per verse:** when Arnold and Sivananda cover the same verse, keep the clearer one and record the other as an alternate.
7. **Verbatim check:** a script matches every extracted passage against the normalised source text. Anything that isn't an exact match is rejected and logged, never fixed by hand. This guarantees the model never paraphrases a source.

## 5. Tagging

Each passage gets: themes, situations it helps with, emotional tone, a one-line "when this helps" description, and a harm flag (section 6). The exact schema is set on Plan Day 2 ([DECISION]).

## 6. Harm review

Shailesh can't read thousands of passages, so review is risk-based.

1. **Auto-flag** any passage touching death, suicide, self-harm, violence, war, killing, sin, damnation, punishment, or contempt for a group of people. Expect flags in Schopenhauer, the Gita's battlefield setting, the Bible and Plato's *Phaedo*.
2. **Second pass:** a separate Claude review reads every passage as a vulnerable reader would and flags anything that could land as harmful out of context.
3. **Shailesh reviews** every flagged passage plus a 5% random sample of unflagged ones, deciding keep, cut or keep-but-never-for-distress.
4. **A passage that could read as endorsing self-harm is cut**, regardless of literary merit.
5. If the random sample turns up a problem the flags missed, the flag rules are tightened and the batch is re-flagged.

## 7. Pipeline

How the corpus becomes searchable. Steps 1–6 run once, offline; step 7 runs every time someone uses the app.

| Step | What happens | Done by | Cost |
| --- | --- | --- | --- |
| 1. Normalise | Every source converted to clean text, each sentence keeping its location (book, chapter, verse, letter) | Script | Free |
| 2. Pre-filter | Sections that can't yield passages are skipped (genealogies, law codes, repetitive lists) | Script, with Claude judging unclear sections | Low |
| 3. Extract | Claude reads chunks of ~2,000–3,000 words and returns qualifying passages verbatim with locations (section 4) | Claude Code, parallel by source | Subscription tokens: the heavy step |
| 4. Verbatim check | Exact match against the normalised source (section 4, rule 7) | Script | Free |
| 5. Tag | Themes, situations, tone, "when this helps" line, harm flag (section 5) | Claude Code | Subscription tokens |
| 6. Harm review | Second Claude pass, then Shailesh on flags + 5% sample (section 6) | Claude Code, then Shailesh | His review time |
| 7. Embed | Each passage (or its "when this helps" line, whichever wins in evals) turned into a vector and stored in Supabase pgvector | Embeddings API | Cents for the whole corpus |

### 7.1 Running it

- One output file per source in `../corpus/passages/`, so sources can be rerun independently.
- Progress is saved after every chunk; an interruption or usage limit resumes where it stopped.
- Scale: ~5M words, roughly 6–7M tokens to read once (estimate). Spread over Plan Days 7–11.
- **Token budget:** every run follows `CLAUDE.md` section 4.3. The pre-filter (step 2) is the biggest saving: text no model reads costs nothing.
- **Calibration:** the Day 4 pilot measures how much of Shailesh's weekly limit a given number of words uses (a `/usage` reading before and after). The figure, as "% of weekly limit per 100,000 words", lives in `../STATUS.md` section 6 and is refined after every run.
- **Model:** bulk extraction and tagging run in subagents on Sonnet. The Day 6 pilot runs the same chunks through Sonnet and Opus; Opus is used for bulk work only if its passages are clearly better.

### 7.2 At runtime

The model never reads the corpus. The user's words are embedded the same way; the database returns the nearest candidates; near-duplicates are removed and the best 10 are ranked. The user sees them one at a time, and the model writes each passage's bridging sentence when it is first shown. Embeddings serve search; nothing is taught to the model.
