# Corpus Policy

Rules for what goes into the corpus, how passages are extracted, how they're reviewed and how they're credited. Provenance for every source is in `../corpus/manifest.md`.

## 1. Sourcing policy (v2, decided 24 Aug 2026)

The ancient text is never the copyright problem; the translation is.

- **Tier A (default):** US public domain, or a verified open licence (CC0, CC-BY).
- **Tier B (stopgap):** a modern translation that is freely circulated, has a named translator and carries no stated restriction. Allowed only when no adequate Tier A option exists. Marked **GRAY**, credited in-app, excerpts kept modest, replaced before any real monetisation.
- **Never:** anonymous or unattributed translations; anything under an NC or ND licence; commercially active famous translations (Mitchell, Barks, Peers, Easwaran, Hays, Blakney). Exception: *Way of Perfection* in the Peers translation, kept on Shailesh's call (7 Oct 2026, `Decisions.md`).
- **Rejected sources, don't re-propose:** Carl Jung, Zen classics, *Black Elk Speaks*, the "Chief Seattle speech", the "Prayer of St Francis", *Man's Search for Meaning*, *Desiderata*, Bahá'í writings, the nitnemsahib.com Japji.

## 2. Sources in v1 (33)

All folders in `../corpus/source/`. Word counts from the manifest; SuttaCentral is a JSON tree, so its count includes markup. **Which sources are in use is set in `../pipeline/sources.toml`**: switching one off there removes it from every pipeline step and from the app, without deleting anything.

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
| brother-lawrence | Christianity | The Practice of the Presence of God | Lightheart edition, 2002 | **Copyrighted**; kept on Shailesh's call (7 Oct 2026) | 14,109 |
| augustine-confessions-pusey | Christianity | Confessions | Edward Pusey, 1838 | US PD | 114,873 |
| teresa-interior-castle | Christianity | Interior Castle | Benedictines of Stanbrook, 1921 | US PD | 90,288 |
| teresa-way-of-perfection | Christianity | Way of Perfection | E. Allison Peers (Image Books ed., 1964) | **Copyrighted**; kept on Shailesh's call (7 Oct 2026) | 83,771 |
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
3. **Speaks to a situation:** grief, failure, anger, fear, loss, love, work, purpose, change, loneliness and the like. Spiritual seeking counts too: teaching on practice, the path, the true self and liberation qualifies when a reader outside the tradition could follow it (decided 7 Oct 2026). Narrative, genealogy, law codes, ritual detail, technical argument and lines needing specialist vocabulary are skipped.
4. **Selective by design:** dense sources (Aristotle, Augustine, the Nikayas, most of the Bible) will yield a small fraction of their text. That's expected.
5. **Location kept:** every passage records its source folder and exact location so it can be traced back.
6. **Gita translations are independent sources.** Arnold and Sivananda are extracted separately, with no Gita-specific rule. Near-identical results are removed only by the general search-time filter (decided 7 Oct 2026).
7. **Verbatim check:** a script matches every extracted passage against the normalised source text. Anything that isn't an exact match is rejected and logged, never fixed by hand. This guarantees the model never paraphrases a source.

## 5. Tagging

Each passage gets fine-grained tags on six axes: feelings (the feeling a reader arrives with), themes, situations, tone, faith framing and safety, plus up to 3 free keywords and a one-line "when this helps". Tags and definitions are in `../pipeline/prompts/taxonomy.md`, grounded in clinical, psychological and support-service sources (decided 7 Oct 2026).

## 6. Harm review

Decided 7 Oct 2026: review is limited to the most serious cases. Harshness, blame, stern rebukes and talk of sin or death are **not** grounds for hiding a passage.

1. **Safety is one field filled in during tagging** (taxonomy section 7). There is no separate harm pass, keyword pass or random sample.
2. **Cut automatically:** passages that endorse suicide or self-harm (including "the door is open" images and descriptions of methods, following the WHO's 2023 safe-messaging guidance), sexual violence, and hatred of a group.
3. **Kept but never shown to someone in distress:** passages that present death as a release without recommending it.
4. **Cuts are logged with the tagger's reason, not deleted.** Shailesh can scan the cut list after each batch and restore anything wrongly cut.

## 7. Pipeline

How the corpus becomes searchable. Steps 1–6 run once, offline; step 7 runs every time someone uses the app.

| Step | What happens | Done by | Cost |
| --- | --- | --- | --- |
| 1. Normalise | Every source converted to clean text, each sentence keeping its location (book, chapter, verse, letter) | Script | Free |
| 2. Pre-filter | Sections that can't yield passages are skipped (genealogies, law codes, repetitive lists) | Script, with Claude judging unclear sections | Low |
| 3. Extract | Claude reads chunks of ~2,000–3,000 words and returns qualifying passages verbatim with locations (section 4) | Claude Code, parallel by source | Subscription tokens: the heavy step |
| 4. Verbatim check | Exact match against the normalised source (section 4, rule 7) | Script | Free |
| 5. Tag | Themes, situations, tone, "when this helps" line, harm flag (section 5) | Claude Code | Subscription tokens |
| 6. Safety check | Done inside tagging (step 5); cuts automatic and logged (section 6) | Claude Code | Subscription tokens (negligible) |
| 7. Embed | Each passage (or its "when this helps" line, whichever wins in evals) turned into a vector and stored in Supabase pgvector | Embeddings API | Cents for the whole corpus |

Between steps 6 and 7, **deduplication** (`../pipeline/dedup.py`, Plan Days 12–13) marks repeated text so it is loaded and searched once: an exact repeat, a passage lying wholly inside another, or a stock formula repeated with only a name changed gets status `dup` pointing at the passage kept; passages that share more than half their wording are kept but put in one `near_group`, and search never shows two from one group. Nothing is deleted. The app shows `display_text`, which is the verbatim `text` minus file apparatus (SuttaCentral `<j>` indents, Gutenberg `_italics_` underscores, a quotation mark whose partner lies outside the passage) and with per-passage display corrections for scan errors recorded in `../corpus/passages/bulk/overrides.json`. Corpus statistics are in `../corpus/passages/stats.md` (`../pipeline/stats.py`).

### 7.1 Running it

- One output file per source in `../corpus/passages/`, so sources can be rerun independently.
- Progress is saved after every chunk; an interruption or usage limit resumes where it stopped.
- Scale: 4.1M words after normalisation (7 Oct 2026). Spread over Plan Days 7–11.
- **Token budget:** every run follows `CLAUDE.md` section 4.3. The pre-filter (step 2) is the biggest saving: text no model reads costs nothing.
- **Calibration:** the Day 4 pilot measures how much of Shailesh's weekly limit a given number of words uses (a `/usage` reading before and after). The figure, as "% of weekly limit per 100,000 words", lives in `../STATUS.md` section 6 and is refined after every run.
- **Model:** bulk extraction and tagging run in subagents on Opus 5.5 at medium effort (decided 7 Oct 2026). The pilot showed Sonnet and Opus cost the same per chunk; Opus picks more passages (86 vs 49 on the pilot), so tagging volume is higher.

### 7.2 At runtime

The model never reads the corpus. The user's words are embedded the same way; the database returns the nearest candidates; near-duplicates are removed and the best 10 are ranked. The user sees them one at a time, and the model writes each passage's bridging sentence when it is first shown. Embeddings serve search; nothing is taught to the model.
