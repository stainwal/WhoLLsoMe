# Corpus statistics

*Written by `pipeline/stats.py` on 09 Oct 2026. Counts are over the 4,929 passages a user can be shown (status keep or no-distress); cut and duplicate passages are excluded.*

## 1. Totals

| Measure | Value |
| --- | --- |
| Passages extracted and tagged | 5,029 |
| Shown normally (keep) | 4,882 |
| Kept but hidden from distress (no-distress) | 47 |
| Cut by the safety field | 16 |
| Duplicates (status dup) | 84 |
| **Shown passages (keep + no-distress)** | **4,929** |
| Words in shown passages | 300,216 |
| Passage length, words: median / mean / min / max | 53 / 60.9 / 5 / 322 |
| Under 10 words / over 250 words | 20 / 4 |
| Source words read | 4,096,568 |
| Yield, shown passages per 1,000 words read | 1.20 |
| In a near group (related passages, never two in one answer) | 43 in 18 groups |

Faith framing: secular 2,536 (51%), spiritual 1,230 (25%), devotional 1,163 (24%)

## 2. By source

Yield is shown passages per 1,000 words read. Secular is the share of passages that make sense with no religious belief. Top themes are the three most frequent theme tags.

| Source | Tradition | Translator | Words read | Extracted | Shown | Hidden | Cut | Dup | Yield | Median words | Secular | Top themes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bible-web | Christianity / Judaism | WEB | 842,907 | 988 | 987 | 6 | 1 | 0 | 1.17 | 37 | 29% | faith and the sacred, compassion and kindness, truth and integrity |
| vivekananda | Hinduism | Vivekananda (original English) | 540,270 | 764 | 763 | 5 | 0 | 1 | 1.41 | 58 | 44% | the true self, faith and the sacred, wisdom and understanding |
| suttacentral-sujato | Buddhism | Bhikkhu Sujato, 2018 | 1,293,581 | 750 | 666 | 3 | 1 | 83 | 0.51 | 46 | 46% | character and growth, self-mastery, desire and attachment |
| seneca-letters-gummere | Stoicism | Richard Gummere, 1917–25 | 208,335 | 479 | 467 | 13 | 12 | 0 | 2.24 | 70 | 94% | character and growth, death and mortality, wisdom and understanding |
| emerson-essays | Modern West | Emerson (original English) | 132,470 | 257 | 257 | 1 | 0 | 0 | 1.94 | 65 | 77% | truth and integrity, friendship, character and growth |
| imitation-of-christ-benham | Christianity | William Benham, 1874 | 58,849 | 187 | 187 | 0 | 0 | 0 | 3.18 | 77 | 4% | faith and the sacred, humility and pride, patience and perseverance |
| chuang-tzu-giles | Taoism | Herbert Giles, 1889 | 85,090 | 165 | 165 | 3 | 0 | 0 | 1.94 | 48 | 75% | wisdom and understanding, acceptance and surrender, humility and pride |
| meditations-long | Stoicism | George Long, 1862 | 45,363 | 162 | 162 | 3 | 0 | 0 | 3.57 | 56 | 85% | the mind and thoughts, character and growth, compassion and kindness |
| walden-thoreau | Modern West | Thoreau (original English) | 115,574 | 147 | 147 | 1 | 0 | 0 | 1.27 | 54 | 90% | nature, simplicity and enough, freedom and self-reliance |
| augustine-confessions-pusey | Christianity | Edward Pusey, 1838 | 111,772 | 144 | 144 | 0 | 0 | 0 | 1.29 | 56 | 20% | faith and the sacred, desire and attachment, love |
| rumi-masnavi-whinfield | Sufism | E.H. Whinfield, 1887 | 61,563 | 125 | 124 | 1 | 1 | 0 | 2.01 | 47 | 29% | faith and the sacred, wisdom and understanding, the true self |
| epictetus-discourses-long | Stoicism | George Long, 1877 | 60,257 | 113 | 113 | 0 | 0 | 0 | 1.88 | 68 | 91% | acceptance and surrender, the mind and thoughts, character and growth |
| schopenhauer-counsels-maxims | Modern West | T. Bailey Saunders, 1890 | 42,511 | 107 | 107 | 1 | 0 | 0 | 2.52 | 75 | 99% | wisdom and understanding, the mind and thoughts, time and the present |
| aristotle-ethics | Greek philosophy | D.P. Chase, 1847 | 91,741 | 77 | 77 | 0 | 0 | 0 | 0.84 | 83 | 99% | friendship, character and growth, wisdom and understanding |
| teresa-way-of-perfection | Christianity | E. Allison Peers (Image Books ed., 1964) | 72,935 | 77 | 77 | 1 | 0 | 0 | 1.06 | 78 | 14% | faith and the sacred, humility and pride, spiritual practice |
| teresa-interior-castle | Christianity | Benedictines of Stanbrook, 1921 | 62,237 | 70 | 70 | 1 | 0 | 0 | 1.12 | 52 | 7% | faith and the sacred, humility and pride, the spiritual path |
| gita-sivananda | Hinduism | Swami Sivananda | 18,295 | 49 | 49 | 1 | 0 | 0 | 2.68 | 27 | 27% | work and duty, desire and attachment, inner peace and stillness |
| schopenhauer-wisdom-of-life | Modern West | T. Bailey Saunders, 1890 | 36,080 | 42 | 42 | 0 | 0 | 0 | 1.16 | 64 | 100% | reputation and others' opinions, simplicity and enough, self-worth |
| gita-arnold-song-celestial | Hinduism | Edwin Arnold, 1885 | 18,611 | 35 | 35 | 1 | 0 | 0 | 1.88 | 45 | 9% | faith and the sacred, inner peace and stillness, desire and attachment |
| light-of-asia-arnold | Buddhism | Edwin Arnold (original English) | 34,545 | 34 | 34 | 0 | 0 | 0 | 0.98 | 52 | 38% | compassion and kindness, character and growth, suffering and its causes |
| prophet-gibran | Sufism-adjacent | Kahlil Gibran (original English) | 12,282 | 33 | 33 | 1 | 0 | 0 | 2.69 | 66 | 52% | love, purpose and meaning, the true self |
| epictetus-enchiridion | Stoicism | T.W. Higginson, 1865 | 7,087 | 27 | 27 | 0 | 0 | 0 | 3.81 | 71 | 81% | reputation and others' opinions, acceptance and surrender, the mind and thoughts |
| pirkei-avot | Judaism | Joshua Kulp (Mishnah Yomit) | 8,902 | 23 | 23 | 0 | 0 | 0 | 2.58 | 44 | 61% | wisdom and understanding, compassion and kindness, friendship |
| tao-te-ching-legge | Taoism | James Legge, 1891 | 10,324 | 23 | 23 | 0 | 0 | 0 | 2.23 | 40 | 74% | humility and pride, simplicity and enough, wisdom and understanding |
| as-a-man-thinketh-allen | Modern West | James Allen (original English) | 7,428 | 21 | 21 | 0 | 0 | 0 | 2.83 | 56 | 76% | character and growth, the mind and thoughts, patience and perseverance |
| brother-lawrence | Christianity | Lightheart edition, 2002 | 10,226 | 21 | 21 | 0 | 0 | 0 | 2.05 | 66 | 0% | faith and the sacred, spiritual practice, patience and perseverance |
| american-indian-stories-zitkala | Native American | Zitkala-Ša (original English) | 30,637 | 20 | 19 | 0 | 1 | 0 | 0.62 | 79 | 74% | family, compassion and kindness, wrongdoing and injustice |
| eckhart-sermons-field | Christianity | Claud Field, 1909 | 11,594 | 19 | 19 | 0 | 0 | 0 | 1.64 | 57 | 0% | faith and the sacred, suffering and its causes, the spiritual path |
| soul-of-the-indian-eastman | Native American | Charles Eastman (original English) | 16,768 | 18 | 18 | 1 | 0 | 0 | 1.07 | 64 | 44% | faith and the sacred, compassion and kindness, nature |
| plato-phaedo-jowett | Greek philosophy | Benjamin Jowett | 27,153 | 16 | 16 | 1 | 0 | 0 | 0.59 | 80 | 62% | wisdom and understanding, character and growth, death and mortality |
| upanishads-paramananda | Hinduism | Swami Paramananda, 1919 | 5,664 | 15 | 15 | 0 | 0 | 0 | 2.65 | 40 | 7% | desire and attachment, the true self, wisdom and understanding |
| japji-macauliffe | Sikhism | M.A. Macauliffe, 1900 | 4,169 | 11 | 11 | 0 | 0 | 0 | 2.64 | 57 | 0% | faith and the sacred, spiritual practice, humility and pride |
| plato-apology-jowett | Greek philosophy | Benjamin Jowett | 11,348 | 10 | 10 | 3 | 0 | 0 | 0.88 | 66 | 70% | death and mortality, truth and integrity, wisdom and understanding |
| **Total** | | | **4,096,568** | **5,029** | **4,929** | **47** | **16** | **84** | **1.20** | **53** | **51%** | |

## 3. By theme

Each passage carries 1–3 theme tags, so shares add to more than 100%. Sources = number of sources with at least one passage on the theme.

| Family | Passages with a theme in the family |
| --- | --- |
| Living | 2,944 (60%) |
| The self | 2,232 (45%) |
| Others | 1,822 (37%) |
| Spirit | 1,693 (34%) |
| Growth and practice | 1,466 (30%) |
| Mortality and change | 1,012 (21%) |

| Theme | Family | Passages | Share | Sources |
| --- | --- | --- | --- | --- |
| faith and the sacred | Spirit | 947 | 19% | 27 |
| wisdom and understanding | Living | 573 | 12% | 28 |
| character and growth | Growth and practice | 569 | 12% | 30 |
| compassion and kindness | Others | 482 | 10% | 26 |
| the mind and thoughts | The self | 456 | 9% | 27 |
| truth and integrity | Living | 443 | 9% | 26 |
| desire and attachment | The self | 422 | 9% | 26 |
| humility and pride | The self | 419 | 9% | 29 |
| self-mastery | The self | 406 | 8% | 30 |
| patience and perseverance | Living | 375 | 8% | 28 |
| acceptance and surrender | Spirit | 331 | 7% | 26 |
| impermanence | Mortality and change | 323 | 7% | 22 |
| simplicity and enough | Living | 317 | 6% | 26 |
| inner peace and stillness | Spirit | 313 | 6% | 27 |
| death and mortality | Mortality and change | 298 | 6% | 24 |
| the true self | Growth and practice | 290 | 6% | 27 |
| freedom and self-reliance | The self | 268 | 5% | 25 |
| courage | Living | 266 | 5% | 29 |
| self-worth | The self | 261 | 5% | 23 |
| love | Others | 252 | 5% | 23 |
| suffering and its causes | Living | 250 | 5% | 24 |
| friendship | Others | 244 | 5% | 22 |
| reputation and others' opinions | Others | 241 | 5% | 21 |
| the spiritual path | Growth and practice | 233 | 5% | 22 |
| spiritual practice | Growth and practice | 233 | 5% | 20 |
| time and the present | Mortality and change | 232 | 5% | 22 |
| wrongdoing and injustice | Others | 231 | 5% | 24 |
| failure and adversity | Living | 230 | 5% | 22 |
| work and duty | Living | 227 | 5% | 26 |
| purpose and meaning | Living | 210 | 4% | 25 |
| forgiveness | Others | 177 | 4% | 25 |
| loss and letting go | Mortality and change | 159 | 3% | 20 |
| liberation and realisation | Growth and practice | 141 | 3% | 14 |
| family | Others | 119 | 2% | 16 |
| nature | Spirit | 102 | 2% | 19 |
| solitude | Others | 76 | 2% | 18 |
| beauty | Living | 53 | 1% | 12 |

Themes with no passage: none.

## 4. Source by theme family

Share of each source's theme tags that fall in each family (rows add to 100%).

| Source | Living | The self | Others | Spirit | Growth and practice | Mortality and change |
| --- | --- | --- | --- | --- | --- | --- |
| bible-web | 28% | 12% | 23% | 24% | 5% | 8% |
| vivekananda | 25% | 23% | 13% | 11% | 22% | 6% |
| suttacentral-sujato | 25% | 24% | 16% | 6% | 19% | 10% |
| seneca-letters-gummere | 29% | 21% | 13% | 9% | 11% | 17% |
| emerson-essays | 33% | 21% | 20% | 10% | 8% | 9% |
| imitation-of-christ-benham | 21% | 23% | 13% | 28% | 10% | 5% |
| chuang-tzu-giles | 25% | 25% | 12% | 18% | 9% | 12% |
| meditations-long | 23% | 22% | 19% | 13% | 8% | 15% |
| walden-thoreau | 37% | 16% | 13% | 13% | 9% | 11% |
| augustine-confessions-pusey | 21% | 18% | 16% | 26% | 10% | 8% |
| rumi-masnavi-whinfield | 25% | 20% | 10% | 21% | 14% | 9% |
| epictetus-discourses-long | 18% | 33% | 15% | 14% | 9% | 11% |
| schopenhauer-counsels-maxims | 33% | 24% | 11% | 9% | 6% | 17% |
| aristotle-ethics | 35% | 17% | 30% | 2% | 14% | 3% |
| teresa-way-of-perfection | 14% | 24% | 14% | 25% | 19% | 4% |
| teresa-interior-castle | 16% | 13% | 13% | 30% | 26% | 0% |
| gita-sivananda | 29% | 26% | 2% | 21% | 15% | 7% |
| schopenhauer-wisdom-of-life | 30% | 31% | 26% | 2% | 7% | 3% |
| gita-arnold-song-celestial | 20% | 22% | 6% | 26% | 19% | 7% |
| light-of-asia-arnold | 16% | 18% | 22% | 5% | 23% | 17% |
| prophet-gibran | 24% | 23% | 23% | 8% | 11% | 11% |
| epictetus-enchiridion | 17% | 37% | 25% | 12% | 4% | 6% |
| pirkei-avot | 33% | 22% | 33% | 4% | 5% | 4% |
| tao-te-ching-legge | 44% | 23% | 19% | 5% | 2% | 7% |
| as-a-man-thinketh-allen | 33% | 35% | 2% | 6% | 22% | 2% |
| brother-lawrence | 26% | 5% | 9% | 32% | 28% | 0% |
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
| Fear (2,312) | insecurity 758, anxiety 647, fear 427, overwhelm 298, dread 182 |
| Disconnection (1,995) | restlessness 676, lostness 519, loneliness 349, exhaustion 287, emptiness 164 |
| Sadness (1,570) | discouragement 519, sorrow 412, grief 265, disappointment 234, despair 140 |
| Anger (1,561) | frustration 669, anger 440, resentment 343, bitterness 109 |
| Enjoyment and ease (988) | pride 198, love 187, hope 133, gratitude 112, awe 105, joy 88, contentment 83, peace 61, relief 21 |
| Desire (908) | craving 468, longing 269, envy 152, jealousy 19 |
| Shame (903) | guilt 378, shame 236, regret 192, embarrassment 97 |

Tags with no passage: none.

## 6. By situation

| Family | Tags (passages) |
| --- | --- |
| Self and direction (1,341) | self-doubt 244, facing a decision 233, searching for meaning 210, worry about the future 204, a big life change 143, questions of identity 108, feeling directionless 104, existential dread 95 |
| Work and study (1,139) | facing a hard task 229, career setback or feeling stuck 194, success and its temptations 169, overwork or burnout 153, workplace conflict 144, unrecognised effort 112, exams or study pressure 46, a career change or new job 43, job loss 26, retirement 23 |
| Health and body (868) | living with anxiety or depression 224, a habit or addiction I can't break 179, ageing 166, illness or injury 115, facing one's own death 111, chronic pain or illness 73 |
| Friends and community (754) | conflict with a friend or colleague 404, feeling excluded or rejected 131, living alone or isolated 89, bullying or harassment 81, discrimination or prejudice 49 |
| Seeking (650) | struggling with faith or practice 385, starting or deepening a practice 265 |
| Family (314) | family conflict 147, parenting struggles 52, caring for a sick or ageing relative 37, estrangement 34, a loved one's illness 31, pregnancy or a new baby 7, children leaving home 6 |
| Money, home and law (312) | money worries or debt 188, moving country or culture 58, legal trouble 30, moving home 29, insecure housing 7 |
| Loss (262) | bereavement (partner, parent or child) 90, bereavement (friend or other relative) 75, loss of a dream or plan 49, loss of a home or something valued 48 |
| Harm done (244) | something I did wrong 236, having been abused or assaulted 8 |
| Love and partnership (156) | relationship trouble 84, a new relationship or marriage 34, breakup or divorce 20, unrequited love 17, a partner's infidelity 1 |
| Everyday (137) | an ordinary day 100, good news or a celebration 37 |

Tags with no passage: losing a pet.
Passages with no situation tag: 713 (14%).

## 7. By tone

| Tone | Passages | Share |
| --- | --- | --- |
| contemplative | 1,360 | 28% |
| challenging | 1,261 | 26% |
| practical | 1,260 | 26% |
| uplifting | 912 | 19% |
| steadying | 855 | 17% |
| consoling | 661 | 13% |
| affirming | 580 | 12% |
| companioning | 450 | 9% |
| stern | 328 | 7% |

