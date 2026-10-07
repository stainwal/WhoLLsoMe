# Tag taxonomy (draft v2, 7 Oct 2026)

Draft for Shailesh's review (Plan Day 2). Once agreed, this file is what the tagging model reads. Every tag has a one-line definition and, where it has a close neighbour, a boundary line saying how to choose between them.

## 1. Design

### 1.1 Four questions, one axis each

Each axis answers a different question about a passage, so they don't overlap:

| Axis | Question | Per passage |
| --- | --- | --- |
| Feelings | What feeling is a reader **in** when this passage would help them? | 1–3 |
| Themes | What is the passage about: its subject or teaching? | 1–3 |
| Situations | What might be happening in the reader's life when it helps? | 0–3 |
| Tone | How does it speak? | 1–2 |
| Faith framing | Does it assume religious belief? | exactly 1 |

Plus 0–3 free keywords, the one-line "when this helps", and the harm fields (Corpus-Policy section 6).

Emotions live only under Feelings. Themes hold subjects and teachings, not emotions. That is why "grief" is a feeling and "loss and letting go" is a theme.

### 1.2 Fine tags, rolled up into families

The tagger always picks the **fine tag** (anger, resentment). The **family** (Anger) is derived automatically and used for corpus statistics and coverage checks. We keep the precision of fine tags and the readable counts of families.

### 1.3 Proving the boundaries

On the pilot, Sonnet and Opus tag the same passages independently. Where two fine tags are confused with each other again and again, that boundary is not real, and we merge them. Tags that are never used are dropped. The taxonomy is frozen after that test (Plan Day 6).

## 2. Feelings (36 tags, 7 families)

Tag the feeling the reader **arrives with**, not the feeling the passage leaves them with (Decision 4). A passage that brings hope to an anxious reader is tagged `anxiety`, not `hope`; what it does to them is captured by tone. Positive feelings apply when a reader arrives already in them (grateful, joyful, at peace) and the passage meets them there.

### 2.1 Sadness

| Tag | Definition | Boundary |
| --- | --- | --- |
| grief | Pain at losing someone or something that mattered, especially through death | vs sorrow: grief has a specific loss |
| sorrow | General heaviness or heartache, not tied to one loss | |
| disappointment | Something hoped for did not happen | vs discouragement: about one outcome, not the will to go on |
| discouragement | Losing heart; the will to keep trying is fading | vs despair: hope is dimmed, not gone |
| despair | Hope is gone; nothing seems worth it | Always also tagged for crisis-adjacent review |

### 2.2 Fear

| Tag | Definition | Boundary |
| --- | --- | --- |
| fear | Afraid of a specific, present threat | vs anxiety: has a clear object |
| anxiety | Diffuse, ongoing unease about what might happen | vs dread: no single known event |
| dread | Fear of a known event that is coming (a diagnosis, a hearing) | |
| insecurity | Doubting one's own adequacy or worth | vs shame: "am I enough?", not "I am bad" |
| overwhelm | Too much at once; unable to cope with the load | vs exhaustion: about load, not depleted energy |

### 2.3 Anger

| Tag | Definition | Boundary |
| --- | --- | --- |
| anger | Heat in the moment at a person or event | vs resentment: now, not held over time |
| frustration | Blocked from a goal; things won't go one's way | vs anger: aimed at circumstances, not a person |
| resentment | A grievance held and replayed over time | vs bitterness: about a particular wrong |
| bitterness | A soured, cynical outlook spread across life | |

### 2.4 Desire

| Tag | Definition | Boundary |
| --- | --- | --- |
| craving | Wanting that won't be satisfied: possessions, pleasure, status | |
| envy | Wanting what someone else has | vs jealousy: about having, not losing |
| jealousy | Fear of losing someone or something to a rival | |
| longing | Yearning for someone or something absent, including the past | vs grief: what is absent may still be possible |

### 2.5 Shame

| Tag | Definition | Boundary |
| --- | --- | --- |
| guilt | "I did something wrong" | vs shame: about an act |
| shame | "I am bad, unworthy" | vs guilt: about the self |
| regret | Wishing a past choice had gone differently, not necessarily a wrong | vs guilt: no wrongdoing needed |
| embarrassment | Exposed or foolish in front of others | |

### 2.6 Disconnection

| Tag | Definition | Boundary |
| --- | --- | --- |
| loneliness | Feeling alone or unseen, even among people | |
| emptiness | Numb, flat, nothing matters | vs despair: absence of feeling, not active hopelessness |
| exhaustion | Depleted, burnt out | |
| restlessness | Unable to settle; bored, agitated, distracted | |
| lostness | No direction; confused about what to do or who to be | |

### 2.7 Enjoyment and ease

| Tag | Definition | Boundary |
| --- | --- | --- |
| joy | Delight, gladness | |
| gratitude | Thankfulness for what one has | vs contentment: directed thanks |
| contentment | Enough-ness; at ease with what is | vs peace: about having, not inner stillness |
| peace | Inner calm, stillness | |
| hope | Expecting or trusting that things can be better | |
| awe | Wonder before something vast: nature, the sacred, existence | |
| love | Warmth and tenderness toward someone | |
| relief | Release after strain or fear | |
| pride | Healthy satisfaction in effort or achievement | Theme "humility and pride" covers its downside |

## 3. Themes (37 tags, 6 families)

Checked against the VIA classification of character strengths and virtues (Peterson and Seligman, 2004), which surveyed 2,500 years of religious and philosophical traditions, and the Common Wisdom Model (Grossmann et al., 2020). Courage, wisdom and understanding, and beauty were added from them.

### 3.1 Mortality and change

| Tag | Definition |
| --- | --- |
| death and mortality | Facing one's own or others' death; the shortness of life |
| loss and letting go | Losing what one loves, and releasing it |
| impermanence | All things change and pass |
| time and the present | Using time well; living now rather than in past or future |

### 3.2 The self

| Tag | Definition | Boundary |
| --- | --- | --- |
| the mind and thoughts | How thought shapes experience; watching one's mind | |
| self-mastery | Discipline, restraint, governing impulses | vs the mind: about acting, not perceiving |
| desire and attachment | Teaching on craving, clinging, and freedom from them | |
| humility and pride | Ego, vanity, arrogance, and their remedy | |
| self-worth | One's value, independent of others' verdict | vs reputation: inner worth, not public standing |
| freedom and self-reliance | Inner freedom; standing on one's own judgement | |

### 3.3 Others

| Tag | Definition | Boundary |
| --- | --- | --- |
| love | Love between people: romantic, familial, universal | |
| friendship | Choosing, keeping and being a friend | |
| family | Parents, children, home | |
| forgiveness | Forgiving others or oneself; releasing grievance | |
| compassion and kindness | Care for others' suffering; generosity | |
| wrongdoing and injustice | Being wronged; how to respond to harm or unfairness | vs forgiveness: about the wrong, not the release |
| reputation and others' opinions | Praise, blame, status, what people think | |
| solitude | Being alone as a choice or a value | vs feeling "loneliness": a theme, not the pain |

### 3.4 Living

| Tag | Definition |
| --- | --- |
| work and duty | Doing one's work or role; action without attachment to results |
| purpose and meaning | Why live; what matters |
| failure and adversity | Setbacks, hardship, and how to meet them |
| suffering and its causes | Why suffering arises and how it ends |
| patience and perseverance | Endurance, keeping on |
| simplicity and enough | Wanting less; frugality; wealth and possessions |
| truth and integrity | Honesty, living by one's values |
| courage | Facing fear, danger or hardship; doing the right thing when it costs |
| wisdom and understanding | Seeing clearly; knowing the limits of one's knowledge; weighing other perspectives |
| beauty | Noticing and being moved by beauty in art, people or the world |

### 3.5 Spirit

| Tag | Definition | Boundary |
| --- | --- | --- |
| acceptance and surrender | Accepting what can't be controlled; trust | |
| inner peace and stillness | Staying calm amid ordinary life | vs feeling "peace": the teaching, not the state; vs spiritual practice: not a method |
| faith and the sacred | God, the divine, prayer, devotion | |
| nature | The natural world as teacher or consolation | |

### 3.6 Growth and practice

| Tag | Definition | Boundary |
| --- | --- | --- |
| spiritual practice | Methods: meditation, prayer, contemplation, mantra, sadhana, yoga, mindfulness | vs inner peace: the how, not the calm itself |
| the spiritual path | Progress on the way: stages, obstacles, dryness, effort and grace, beginning again | vs practice: the journey, not a method |
| liberation and realisation | The goal: enlightenment, nirvana, moksha, union with God, freedom from rebirth | vs suffering and its causes: the goal, not the diagnosis |
| the true self | What one really is: soul, Atman, Buddha-nature, the divine within | vs self-worth: what the self is, not how one values it |
| character and growth | Building virtue and habits over time; becoming a better person | vs self-mastery: cultivating good, not restraining impulse |

## 4. Situations (57 tags, 11 families)

What a reader might be living through. A passage can have none: some speak to a feeling without fitting any circumstance.

The families follow the life domains used in clinical classifications of psychosocial problems: ICD-10 Z55–Z65, DSM-5 "Other conditions that may be a focus of clinical attention", the List of Threatening Experiences (Brugha) and the Holmes–Rahe life-events scale. Tags are checked against what people actually bring to support services: Crisis Text Line's yearly data and Anthropic's study of emotional-support conversations with Claude. The Grounding column says where each family comes from.

| Family | Tags | Grounding |
| --- | --- | --- |
| Loss | bereavement (partner, parent or child); bereavement (friend or other relative); losing a pet; loss of a home or something valued; loss of a dream or plan | LTE; Holmes–Rahe; DSM bereavement |
| Love and partnership | relationship trouble; breakup or divorce; a partner's infidelity; unrequited love; a new relationship or marriage | Holmes–Rahe; LTE; CTL "relationships" (33% of texters) |
| Family | family conflict; estrangement; parenting struggles; children leaving home; pregnancy or a new baby; a loved one's illness; caring for a sick or ageing relative | ICD Z63; LTE; DSM phase of life |
| Friends and community | conflict with a friend or colleague; feeling excluded or rejected; bullying or harassment; discrimination or prejudice; living alone or isolated | ICD Z60; DSM social exclusion, adverse discrimination, living alone; CTL bullying and isolation |
| Work and study | job loss; career setback or feeling stuck; workplace conflict; overwork or burnout; unrecognised effort; facing a hard task; a career change or new job; retirement; exams or study pressure; success and its temptations | ICD Z55–Z56; LTE; Holmes–Rahe; Anthropic coaching topics |
| Money, home and law | money worries or debt; insecure housing; moving home; moving country or culture; legal trouble | ICD Z59; LTE; DSM acculturation; Holmes–Rahe |
| Health and body | illness or injury; chronic pain or illness; living with anxiety or depression; a habit or addiction I can't break; ageing; facing one's own death | LTE; Holmes–Rahe; CTL anxiety, depression; Anthropic counselling topics |
| Harm done | having been abused or assaulted; something I did wrong | LTE (assault); DSM abuse codes; ICD Z65 |
| Self and direction | facing a decision; a big life change; feeling directionless; self-doubt; questions of identity; worry about the future; existential dread; searching for meaning | DSM identity and phase-of-life problems; Anthropic existential topics; Yalom's existential givens |
| Seeking | starting or deepening a practice; struggling with faith or practice | DSM religious or spiritual problem |
| Everyday | an ordinary day; good news or a celebration | Holmes–Rahe counts positive events too |

## 5. Tone (9 tags)

| Tag | Definition | Boundary |
| --- | --- | --- |
| consoling | Soothes; holds the reader's pain | vs steadying: comforts rather than grounds |
| affirming | Reminds the reader of their own worth, strength or capacity | vs uplifting: about the reader, not the world |
| companioning | Says "you are not alone": others have suffered this, it is part of being human | vs consoling: shared experience, not comfort |
| steadying | Grounds and calms; puts things in proportion | |
| uplifting | Inspires, lifts the eyes | vs consoling: energises rather than soothes |
| contemplative | Invites reflection without telling the reader what to do | |
| practical | Concrete counsel: do this, notice that | vs challenging: advice, not confrontation |
| challenging | Pushes back on the reader's view of things | vs stern: provokes, does not rebuke |
| stern | Warns, rebukes, uses hard words | Ranked low for distress statements |

Checked against the Social Support Behavior Code (Cutrona and Suhr, 1992), the standard coding of supportive messages: emotional support (consoling), esteem support (affirming), informational support (practical) and network support (companioning). Affirming and companioning were added from it.

## 6. Faith framing (exactly one)

| Tag | Definition |
| --- | --- |
| secular | Makes sense with no religious belief |
| spiritual | Speaks of the soul, the sacred or the divine in open terms |
| devotional | Assumes faith: addressed to God, or relies on doctrine |

Pew Research (2023) finds about 21% of US adults neither religious nor spiritual and another 21% spiritual but not religious, so a faith-neutral first answer matters for many readers. Purpose: a reader who writes in secular terms should not be handed a prayer first. Retrieval can use this as a ranking signal; it never filters anything out.

## 7. Safety (exactly one)

Decision 3 (7 Oct 2026): harm review is limited to the most serious cases and done inside tagging. Harshness, blame, stern rebukes and talk of sin or death are **not** safety issues.

| Tag | Definition | What happens |
| --- | --- | --- |
| none | Nothing below applies | Shown normally |
| endorses-suicide | Recommends or approves suicide or self-harm, openly or by image ("the door is open", leaving life like a smoky room), or describes a method | Cut |
| welcomes-death | Presents death as a release or something to long for, without recommending it ("the philosopher desires death") | Kept, but never shown to someone in distress |
| sexual-violence | Depicts or condones rape or sexual abuse | Cut |
| group-hatred | Calls for harm to, or shows contempt for, a people, faith, sex or class | Cut |

Grounded in the WHO's guidance on safe messaging about suicide (*Preventing suicide: a resource for media professionals*, 2023): never present suicide as a solution, never describe methods. Facing death honestly (grief, mortality, impermanence) is `none`. When torn between `welcomes-death` and `endorses-suicide`, choose `endorses-suicide`.
