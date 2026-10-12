# Corpus statistics

*Written by `pipeline/stats.py` on 12 Oct 2026. Counts are over the 5,540 passages a user can be shown (status keep or no-distress); cut and duplicate passages are excluded.*

## 1. Totals

| Measure | Value |
| --- | --- |
| Passages extracted and tagged | 5,642 |
| Shown normally (keep) | 5,477 |
| Kept but hidden from distress (no-distress) | 63 |
| Cut by the safety field | 18 |
| Duplicates (status dup) | 84 |
| **Shown passages (keep + no-distress)** | **5,540** |
| Words in shown passages | 327,982 |
| Passage length, words: median / mean / min / max | 51 / 59.2 / 4 / 322 |
| Under 10 words / over 250 words | 56 / 5 |
| Source words read | 4,172,016 |
| Yield, shown passages per 1,000 words read | 1.33 |
| In a near group (related passages, never two in one answer) | 43 in 18 groups |

Faith framing: secular 2,906 (52%), spiritual 1,399 (25%), devotional 1,235 (22%)

## 2. By source

Yield is shown passages per 1,000 words read. Secular is the share of passages that make sense with no religious belief. Top themes are the three most frequent theme tags.

| Source | Tradition | Translator | Words read | Extracted | Shown | Hidden | Cut | Dup | Yield | Median words | Secular | Top themes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bible-web | Christianity / Judaism | WEB | 842,907 | 988 | 987 | 6 | 1 | 0 | 1.17 | 37 | 29% | faith and the sacred, compassion and kindness, truth and integrity |
| vivekananda | Hinduism | Vivekananda (original English) | 540,270 | 764 | 763 | 6 | 0 | 1 | 1.41 | 59 | 44% | the true self, faith and the sacred, wisdom and understanding |
| suttacentral-sujato | Buddhism | Bhikkhu Sujato, 2018 | 1,293,581 | 750 | 666 | 3 | 1 | 83 | 0.51 | 46 | 46% | character and growth, self-mastery, desire and attachment |
| seneca-letters-gummere | Stoicism | Richard Gummere, 1917–25 | 208,335 | 479 | 467 | 13 | 12 | 0 | 2.24 | 70 | 94% | character and growth, death and mortality, wisdom and understanding |
| emerson-essays | Modern West | Emerson (original English) | 132,470 | 257 | 256 | 3 | 1 | 0 | 1.93 | 65 | 77% | truth and integrity, friendship, character and growth |
| gibran-sand-and-foam | Sufism-adjacent | Kahlil Gibran (original English), 1926 | 7,372 | 252 | 252 | 4 | 0 | 0 | 34.18 | 19 | 76% | compassion and kindness, wisdom and understanding, humility and pride |
| imitation-of-christ-benham | Christianity | William Benham, 1874 | 58,849 | 187 | 187 | 0 | 0 | 0 | 3.18 | 77 | 4% | faith and the sacred, humility and pride, patience and perseverance |
| chuang-tzu-giles | Taoism | Herbert Giles, 1889 | 85,090 | 165 | 165 | 3 | 0 | 0 | 1.94 | 48 | 75% | wisdom and understanding, acceptance and surrender, humility and pride |
| meditations-long | Stoicism | George Long, 1862 | 45,363 | 162 | 162 | 3 | 0 | 0 | 3.57 | 56 | 85% | the mind and thoughts, character and growth, compassion and kindness |
| tagore-stray-birds | Modern India | Rabindranath Tagore (his own English), 1916 | 5,550 | 149 | 149 | 1 | 0 | 0 | 26.85 | 15 | 74% | love, humility and pride, death and mortality |
| walden-thoreau | Modern West | Thoreau (original English) | 115,574 | 147 | 147 | 1 | 0 | 0 | 1.27 | 54 | 90% | nature, simplicity and enough, freedom and self-reliance |
| augustine-confessions-pusey | Christianity | Edward Pusey, 1838 | 111,772 | 144 | 144 | 0 | 0 | 0 | 1.29 | 56 | 20% | faith and the sacred, desire and attachment, love |
| rumi-masnavi-whinfield | Sufism | E.H. Whinfield, 1887 | 61,563 | 125 | 124 | 1 | 1 | 0 | 2.01 | 47 | 29% | faith and the sacred, wisdom and understanding, the true self |
| epictetus-discourses-long | Stoicism | George Long, 1877 | 60,257 | 113 | 112 | 0 | 1 | 0 | 1.86 | 69 | 91% | acceptance and surrender, the mind and thoughts, character and growth |
| schopenhauer-counsels-maxims | Modern West | T. Bailey Saunders, 1890 | 42,511 | 107 | 107 | 1 | 0 | 0 | 2.52 | 75 | 99% | wisdom and understanding, the mind and thoughts, time and the present |
| tagore-sadhana | Modern India | Rabindranath Tagore (original English), 1913 | 36,723 | 93 | 93 | 2 | 0 | 0 | 2.53 | 79 | 31% | the true self, desire and attachment, purpose and meaning |
| aristotle-ethics | Greek philosophy | D.P. Chase, 1847 | 91,741 | 77 | 77 | 1 | 0 | 0 | 0.84 | 83 | 99% | friendship, character and growth, wisdom and understanding |
| teresa-way-of-perfection | Christianity | E. Allison Peers (Image Books ed., 1964) | 72,935 | 77 | 77 | 1 | 0 | 0 | 1.06 | 78 | 14% | faith and the sacred, humility and pride, spiritual practice |
| tagore-gitanjali | Modern India | Rabindranath Tagore (his own English), 1912 | 12,034 | 72 | 72 | 5 | 0 | 0 | 5.98 | 90 | 6% | faith and the sacred, acceptance and surrender, death and mortality |
| teresa-interior-castle | Christianity | Benedictines of Stanbrook, 1921 | 62,237 | 70 | 70 | 1 | 0 | 0 | 1.12 | 52 | 7% | faith and the sacred, humility and pride, the spiritual path |
| gita-sivananda | Hinduism | Swami Sivananda | 18,295 | 49 | 49 | 1 | 0 | 0 | 2.68 | 27 | 27% | work and duty, desire and attachment, inner peace and stillness |
| schopenhauer-wisdom-of-life | Modern West | T. Bailey Saunders, 1890 | 36,080 | 42 | 42 | 0 | 0 | 0 | 1.16 | 64 | 100% | reputation and others' opinions, simplicity and enough, self-worth |
| gita-arnold-song-celestial | Hinduism | Edwin Arnold, 1885 | 18,611 | 35 | 35 | 1 | 0 | 0 | 1.88 | 45 | 9% | faith and the sacred, inner peace and stillness, desire and attachment |
| light-of-asia-arnold | Buddhism | Edwin Arnold (original English) | 34,545 | 34 | 34 | 0 | 0 | 0 | 0.98 | 52 | 38% | compassion and kindness, character and growth, suffering and its causes |
| prophet-gibran | Sufism-adjacent | Kahlil Gibran (original English) | 12,282 | 33 | 33 | 1 | 0 | 0 | 2.69 | 66 | 52% | love, purpose and meaning, the true self |
| epictetus-enchiridion | Stoicism | T.W. Higginson, 1865 | 7,087 | 27 | 27 | 0 | 0 | 0 | 3.81 | 71 | 81% | reputation and others' opinions, acceptance and surrender, the mind and thoughts |
| gibran-madman | Sufism-adjacent | Kahlil Gibran (original English), 1918 | 6,960 | 27 | 27 | 0 | 0 | 0 | 3.88 | 78 | 89% | solitude, wisdom and understanding, humility and pride |
| pirkei-avot | Judaism | Joshua Kulp (Mishnah Yomit) | 8,902 | 23 | 23 | 0 | 0 | 0 | 2.58 | 44 | 61% | wisdom and understanding, compassion and kindness, friendship |
| tao-te-ching-legge | Taoism | James Legge, 1891 | 10,324 | 23 | 23 | 0 | 0 | 0 | 2.23 | 40 | 74% | humility and pride, simplicity and enough, wisdom and understanding |
| as-a-man-thinketh-allen | Modern West | James Allen (original English) | 7,428 | 21 | 21 | 0 | 0 | 0 | 2.83 | 56 | 76% | character and growth, the mind and thoughts, patience and perseverance |
| brother-lawrence | Christianity | Lightheart edition, 2002 | 10,226 | 21 | 21 | 0 | 0 | 0 | 2.05 | 66 | 0% | faith and the sacred, spiritual practice, patience and perseverance |
| gibran-forerunner | Sufism-adjacent | Kahlil Gibran (original English), 1920 | 6,809 | 20 | 20 | 0 | 0 | 0 | 2.94 | 60 | 60% | love, character and growth, the true self |
| american-indian-stories-zitkala | Native American | Zitkala-Ša (original English) | 30,637 | 20 | 19 | 0 | 1 | 0 | 0.62 | 79 | 74% | family, compassion and kindness, wrongdoing and injustice |
| eckhart-sermons-field | Christianity | Claud Field, 1909 | 11,594 | 19 | 19 | 0 | 0 | 0 | 1.64 | 57 | 0% | faith and the sacred, suffering and its causes, the spiritual path |
| soul-of-the-indian-eastman | Native American | Charles Eastman (original English) | 16,768 | 18 | 18 | 1 | 0 | 0 | 1.07 | 64 | 44% | faith and the sacred, compassion and kindness, nature |
| plato-phaedo-jowett | Greek philosophy | Benjamin Jowett | 27,153 | 16 | 16 | 1 | 0 | 0 | 0.59 | 80 | 62% | wisdom and understanding, character and growth, death and mortality |
| upanishads-paramananda | Hinduism | Swami Paramananda, 1919 | 5,664 | 15 | 15 | 0 | 0 | 0 | 2.65 | 40 | 7% | desire and attachment, the true self, wisdom and understanding |
| japji-macauliffe | Sikhism | M.A. Macauliffe, 1900 | 4,169 | 11 | 11 | 0 | 0 | 0 | 2.64 | 57 | 0% | faith and the sacred, spiritual practice, humility and pride |
| plato-apology-jowett | Greek philosophy | Benjamin Jowett | 11,348 | 10 | 10 | 3 | 0 | 0 | 0.88 | 66 | 70% | death and mortality, truth and integrity, wisdom and understanding |
| **Total** | | | **4,172,016** | **5,642** | **5,540** | **63** | **18** | **84** | **1.33** | **51** | **52%** | |

## 3. By theme

Each passage carries 1–3 theme tags, so shares add to more than 100%. Sources = number of sources with at least one passage on the theme.

| Family | Passages with a theme in the family |
| --- | --- |
| Living | 3,306 (60%) |
| The self | 2,444 (44%) |
| Others | 2,112 (38%) |
| Spirit | 1,833 (33%) |
| Growth and practice | 1,602 (29%) |
| Mortality and change | 1,139 (21%) |

| Theme | Family | Passages | Share | Sources |
| --- | --- | --- | --- | --- |
| faith and the sacred | Spirit | 1,025 | 19% | 33 |
| wisdom and understanding | Living | 644 | 12% | 34 |
| character and growth | Growth and practice | 604 | 11% | 36 |
| compassion and kindness | Others | 563 | 10% | 32 |
| humility and pride | The self | 492 | 9% | 35 |
| truth and integrity | Living | 486 | 9% | 32 |
| the mind and thoughts | The self | 478 | 9% | 30 |
| desire and attachment | The self | 467 | 8% | 32 |
| self-mastery | The self | 424 | 8% | 34 |
| patience and perseverance | Living | 400 | 7% | 33 |
| acceptance and surrender | Spirit | 361 | 7% | 31 |
| the true self | Growth and practice | 354 | 6% | 33 |
| impermanence | Mortality and change | 351 | 6% | 28 |
| simplicity and enough | Living | 349 | 6% | 31 |
| death and mortality | Mortality and change | 339 | 6% | 29 |
| love | Others | 329 | 6% | 29 |
| inner peace and stillness | Spirit | 324 | 6% | 31 |
| freedom and self-reliance | The self | 301 | 5% | 31 |
| courage | Living | 289 | 5% | 35 |
| self-worth | The self | 282 | 5% | 27 |
| suffering and its causes | Living | 278 | 5% | 28 |
| wrongdoing and injustice | Others | 268 | 5% | 29 |
| reputation and others' opinions | Others | 268 | 5% | 27 |
| time and the present | Mortality and change | 266 | 5% | 27 |
| friendship | Others | 264 | 5% | 26 |
| purpose and meaning | Living | 259 | 5% | 31 |
| work and duty | Living | 254 | 5% | 30 |
| failure and adversity | Living | 250 | 5% | 27 |
| the spiritual path | Growth and practice | 250 | 5% | 28 |
| spiritual practice | Growth and practice | 241 | 4% | 23 |
| forgiveness | Others | 186 | 3% | 27 |
| loss and letting go | Mortality and change | 183 | 3% | 26 |
| liberation and realisation | Growth and practice | 153 | 3% | 17 |
| family | Others | 135 | 2% | 21 |
| nature | Spirit | 123 | 2% | 24 |
| solitude | Others | 99 | 2% | 23 |
| beauty | Living | 97 | 2% | 18 |

Themes with no passage: none.

## 4. Source by theme family

Share of each source's theme tags that fall in each family (rows add to 100%).

| Source | Living | The self | Others | Spirit | Growth and practice | Mortality and change |
| --- | --- | --- | --- | --- | --- | --- |
| bible-web | 28% | 12% | 23% | 24% | 5% | 8% |
| vivekananda | 25% | 23% | 13% | 11% | 22% | 6% |
| suttacentral-sujato | 25% | 24% | 16% | 6% | 19% | 10% |
| seneca-letters-gummere | 29% | 21% | 13% | 9% | 11% | 17% |
| emerson-essays | 33% | 20% | 20% | 10% | 8% | 8% |
| gibran-sand-and-foam | 31% | 17% | 29% | 7% | 10% | 7% |
| imitation-of-christ-benham | 21% | 23% | 13% | 28% | 10% | 5% |
| chuang-tzu-giles | 25% | 25% | 12% | 18% | 9% | 12% |
| meditations-long | 23% | 22% | 19% | 13% | 8% | 15% |
| tagore-stray-birds | 27% | 15% | 23% | 12% | 6% | 17% |
| walden-thoreau | 37% | 16% | 13% | 13% | 9% | 11% |
| augustine-confessions-pusey | 21% | 18% | 16% | 26% | 10% | 8% |
| rumi-masnavi-whinfield | 25% | 20% | 10% | 21% | 14% | 9% |
| epictetus-discourses-long | 18% | 33% | 15% | 14% | 9% | 11% |
| schopenhauer-counsels-maxims | 33% | 24% | 11% | 9% | 6% | 17% |
| tagore-sadhana | 31% | 20% | 15% | 11% | 19% | 4% |
| aristotle-ethics | 35% | 17% | 30% | 2% | 14% | 3% |
| teresa-way-of-perfection | 14% | 24% | 14% | 25% | 19% | 4% |
| tagore-gitanjali | 22% | 12% | 10% | 26% | 10% | 18% |
| teresa-interior-castle | 16% | 13% | 13% | 30% | 26% | 0% |
| gita-sivananda | 29% | 26% | 2% | 21% | 15% | 7% |
| schopenhauer-wisdom-of-life | 30% | 31% | 26% | 2% | 7% | 3% |
| gita-arnold-song-celestial | 20% | 22% | 6% | 26% | 19% | 7% |
| light-of-asia-arnold | 16% | 18% | 22% | 5% | 23% | 17% |
| prophet-gibran | 24% | 23% | 23% | 8% | 11% | 11% |
| epictetus-enchiridion | 17% | 37% | 25% | 12% | 4% | 6% |
| gibran-madman | 28% | 20% | 26% | 11% | 6% | 9% |
| pirkei-avot | 33% | 22% | 33% | 4% | 5% | 4% |
| tao-te-ching-legge | 44% | 23% | 19% | 5% | 2% | 7% |
| as-a-man-thinketh-allen | 33% | 35% | 2% | 6% | 22% | 2% |
| brother-lawrence | 26% | 5% | 9% | 32% | 28% | 0% |
| gibran-forerunner | 22% | 14% | 27% | 8% | 18% | 10% |
| american-indian-stories-zitkala | 14% | 9% | 42% | 19% | 9% | 7% |
| eckhart-sermons-field | 10% | 18% | 12% | 34% | 24% | 2% |
| soul-of-the-indian-eastman | 25% | 11% | 23% | 25% | 9% | 7% |
| plato-phaedo-jowett | 34% | 20% | 9% | 7% | 16% | 14% |
| upanishads-paramananda | 19% | 32% | 0% | 8% | 27% | 14% |
| japji-macauliffe | 5% | 14% | 5% | 45% | 32% | 0% |
| plato-apology-jowett | 47% | 5% | 5% | 5% | 11% | 26% |

## 5. By feeling (what the reader arrives with)

| Family | Tags (passages) |
| --- | --- |
| Fear (2,474) | insecurity 833, anxiety 670, fear 455, overwhelm 309, dread 207 |
| Disconnection (2,261) | restlessness 759, lostness 564, loneliness 418, exhaustion 320, emptiness 200 |
| Anger (1,755) | frustration 750, anger 489, resentment 383, bitterness 133 |
| Sadness (1,715) | discouragement 551, sorrow 467, grief 298, disappointment 247, despair 152 |
| Enjoyment and ease (1,166) | love 230, pride 227, hope 145, awe 132, gratitude 128, joy 119, contentment 90, peace 72, relief 23 |
| Desire (1,031) | craving 513, longing 329, envy 166, jealousy 23 |
| Shame (986) | guilt 406, shame 261, regret 212, embarrassment 107 |

Tags with no passage: none.

## 6. By situation

| Family | Tags (passages) |
| --- | --- |
| Self and direction (1,430) | self-doubt 261, facing a decision 240, searching for meaning 226, worry about the future 208, a big life change 158, questions of identity 122, feeling directionless 112, existential dread 103 |
| Work and study (1,238) | facing a hard task 242, career setback or feeling stuck 217, success and its temptations 185, overwork or burnout 172, workplace conflict 152, unrecognised effort 124, exams or study pressure 47, a career change or new job 44, retirement 29, job loss 26 |
| Health and body (935) | living with anxiety or depression 240, a habit or addiction I can't break 187, ageing 179, facing one's own death 135, illness or injury 119, chronic pain or illness 75 |
| Friends and community (826) | conflict with a friend or colleague 431, feeling excluded or rejected 145, living alone or isolated 105, bullying or harassment 87, discrimination or prejudice 58 |
| Seeking (680) | struggling with faith or practice 410, starting or deepening a practice 270 |
| Family (342) | family conflict 154, parenting struggles 64, caring for a sick or ageing relative 38, estrangement 35, a loved one's illness 33, pregnancy or a new baby 11, children leaving home 7 |
| Money, home and law (334) | money worries or debt 200, moving country or culture 62, legal trouble 33, moving home 32, insecure housing 7 |
| Loss (298) | bereavement (partner, parent or child) 107, bereavement (friend or other relative) 82, loss of a dream or plan 60, loss of a home or something valued 49 |
| Harm done (254) | something I did wrong 245, having been abused or assaulted 9 |
| Love and partnership (197) | relationship trouble 106, a new relationship or marriage 42, breakup or divorce 29, unrequited love 19, a partner's infidelity 1 |
| Everyday (147) | an ordinary day 108, good news or a celebration 39 |

Tags with no passage: losing a pet.
Passages with no situation tag: 919 (17%).

## 7. By tone

| Tone | Passages | Share |
| --- | --- | --- |
| contemplative | 1,647 | 30% |
| challenging | 1,408 | 25% |
| practical | 1,298 | 23% |
| uplifting | 1,043 | 19% |
| steadying | 917 | 17% |
| consoling | 745 | 13% |
| affirming | 643 | 12% |
| companioning | 502 | 9% |
| stern | 338 | 6% |

