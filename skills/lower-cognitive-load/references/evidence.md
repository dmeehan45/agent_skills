# Evidence

Why the rules in this skill are the rules. Each entry says what it supports and
where it comes from, so a rule can be argued with on its merits rather than on
whether it sounds sensible.

## Cognitive load has parts, and only some of them are yours to cut

Cognitive load theory splits the demand a text places on working memory into
**intrinsic** load (the difficulty of the ideas themselves), **extraneous** load
(difficulty added by how the material is presented), and **germane** load (the
useful work of building understanding). Extraneous load comes from presentation,
not content: irrelevant information, unnecessary detail, formats that make
processing harder. Linguistic complexity counts as extraneous, because it
consumes working memory without contributing to the reader's mental model.

**Supports:** the skill's central split — carry less (scope, intrinsic) versus
carry it better (presentation, extraneous) — and the rule that you never lower
load by degrading the content itself.

- Sweller et al., cognitive load theory (overview: <https://www.sciencedirect.com/topics/psychology/cognitive-load-theory>)
- <https://readabilitymatters.org/articles/increase-readability-reduce-cognitive-load>

## Conversational wording beats formal wording, measurably

Mayer's **personalization principle**: people learn better when words are in a
conversational rather than formal style. Eleven of eleven experimental tests
favoured conversational, median effect size **d = 1.11**. The proposed mechanism
is social: a reader who feels addressed treats the writer as a conversational
partner and invests more effort in making sense of the material.

**Supports:** the speech pass as a load-reduction technique, not a stylistic
preference; the rule that formal register is not a signal of rigour.

- Mayer, *Multimedia Learning*, personalization/voice/image principles
  (<https://www.cambridge.org/core/books/abs/multimedia-learning/personalization-voice-and-image-principles/97F9B31362E6491806A4718FECCADE3D>)
- <https://files.eric.ed.gov/fulltext/EJ944963.pdf>

## Cutting extraneous material improves comprehension

Mayer's **coherence principle**: people learn more deeply when extraneous
material is excluded. Supported in **23 of 23** tests, median effect size 0.86.
Removing interesting-but-irrelevant material improves outcomes even though it
removes content people enjoy.

**Supports:** the triage phase; the cut-first list; the instruction to make a
full argument for one idea rather than a thin summary of eight.

- Mayer, coherence principle (<https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/4C1367F7716D91DE196CA8D319DF5FAD/9781139164603c7_p113-133_CBO.pdf/coherence_principle.pdf>)

## Concise, scannable, objective — and all three together

NN/g's study of five versions of the same site (51 experienced users, identical
information, different treatments) measured usability against a promotional
control: **concise +58%, scannable +47%, objective +27%, all three combined
+124%.**

**Supports:** doing structure *and* sentence craft rather than either alone; the
rule against marketing register; the whole premise that this is measurable.

- <https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/>

## Readers take in about a fifth of the words

Users read at most **28%** of the words on an average page visit, more
realistically around **20%**. The **F-shaped scanning pattern** — full first
line, progressively shorter scans, then a vertical run down the left — was
documented across 232 users and thousands of pages, and appears specifically on
text-heavy pages with weak visual hierarchy and low reader motivation. It is a
fallback behaviour that structure prevents.

**Supports:** the 20% test; the scan-payload metric; heading density; front-
loading the first two words of headings and list items.

- <https://www.nngroup.com/articles/how-little-do-users-read/>
- <https://www.nngroup.com/videos/f-pattern-reading-digital-content/>

## Point first: the inverted pyramid

Need-to-know information goes first, then detail. Every unit gets front-loaded:
the first sentence of a paragraph is its most important, and the first words of
a sentence carry what follows.

**Supports:** the point-first rule; the buried-opener metric; "a reader who
stops after two sentences should stop correctly informed".

- <https://www.nngroup.com/articles/inverted-pyramid/>

## Experts want it plain too

NN/g's usability study with domain experts found highly educated specialist
readers want succinct, scannable information just as much as anyone else.
Plain language is not a concession to a less capable audience.

**Supports:** the intake rule that expertise changes vocabulary, not density.

- <https://www.nngroup.com/articles/plain-language-experts/>

## Old information first, new information last

Clark and Haviland's **given-new contract** (1977): readers expect a sentence to
open with familiar, contextualising material and close with the new material
being emphasised. Gopen and Swan built the reader-expectation approach on it —
put old information that links backward in the topic position, and the new
information you want emphasised in the stress position — and judged the
misplacement of old and new information to be the number one problem in
American professional writing.

**Supports:** given-new ordering within and between blocks; the rule about not
ending a sentence on a throwaway qualifier.

- Gopen & Swan, "The Science of Scientific Writing", *American Scientist* (1990)
  (<https://www.stat.cmu.edu/~brian/rm/764-2016/week02/gopenswanrev.ppt>)
- <https://writingcenter.gmu.edu/writing-resources/grammar-style/improving-cohesion-the-known-new-contract>

## Four chunks, not seven

Cowan's reconsideration of short-term memory capacity puts the working limit at
about **four chunks**, not Miller's seven, once rehearsal and long-term memory
support are controlled. Agreement is not universal, but no serious estimate is
above four to five.

**Supports:** the four-top-level-chunks ceiling; one idea per block.

- Cowan, "The magical number 4 in short-term memory" (2001)
  (<https://www.cambridge.org/core/services/aop-cambridge-core/content/view/44023F1147D4A1D44BDC0AD226838496/S0140525X01003922a.pdf/the-magical-number-4-in-short-term-memory-a-reconsideration-of-mental-storage-capacity.pdf>)

## The word budget

Brysbaert's meta-analysis (190 studies, 18,573 participants) gives adult English
silent reading of **non-fiction at 238 wpm**, fiction at 260, and **reading aloud
at 183 wpm**.

**Supports:** the minutes-to-words table; the read-time metric in the script.

- Brysbaert, M. (2019), *Journal of Memory and Language* 109, 104047
  (<https://gwern.net/doc/psychology/linguistics/2019-brysbaert.pdf>)

## Readability formulas are thermometers, not targets

Flesch-Kincaid and its relatives measure surface features only — average
sentence length and syllables per word — and overlook semantics, discourse
coherence, jargon, and conceptual difficulty. A text of short sentences and
short words can be deeply confusing. The formulas are trivially gameable:
deliberately chopped sentences score well and mean nothing. Worse, the pressure
to hit a formula target produces artificially split sentences and fragments,
and the connective words that would genuinely aid comprehension push the score
in the wrong direction.

**Supports:** reporting Flesch as INFO only; the rule against chopping sentences
to move a number; the mean-sentence floor that flags prose as *too* short.

- <https://pubmed.ncbi.nlm.nih.gov/28707643/>
- <https://academic.oup.com/heapro/article/26/3/338/663305>

## Simplification can delete the meaning

The health-communication literature's warning about "communication by
subtraction": popular simplification methods delete exactly the things that give
language its power, making complex and nuanced concepts harder to represent
rather than easier. Shorter and simpler is an inadequate account of what a
reader needs to negotiate a text. In risk communication specifically, replacing
precise numeric probabilities with verbal descriptions trades measurable
precision for words different readers interpret very differently.

**Supports:** the whole fidelity apparatus — the claim ledger, the hedge sweep,
the strength check, and the rule that you never blur a claim to shorten it.

- <https://academic.oup.com/heapro/article/26/3/338/663305>
- <https://www.medrxiv.org/content/10.1101/2024.04.04.24305365.full.pdf>

## Machine prose is too even

Analyses of model-generated text find far narrower variance in sentence length
and syntactic shape than human writing, along with persistent structural habits:
symmetry, neat parallelism, frictionless transitions, and negative parallelism
("not just X but Y", which appeared in roughly 6% of messages in one large
dataset). Human writing, even careful human writing, has digressions,
interruptions, tonal shifts, and asymmetric pacing.

**Supports:** the sentence-length CV metric and its 0.35 floor; the tell lists;
the "vary length on purpose" instruction; the warning against over-correcting
into fake humanity.

- <https://decrypt.co/348923/5-biggest-tells-something-written-ai>
- <https://arxiv.org/pdf/2501.15654>

## Plain language is not dumbing down

The first rule of plain language is to write for your audience: use words they
know, take their existing knowledge into account, prefer common everyday words
except for necessary technical terms, use personal pronouns and the active
voice, organise logically, and use lists and tables where they help. The most
common myth about plain language is that it requires dumbing content down; the
guidance explicitly rejects that.

**Supports:** keeping necessary technical terms and defining them once; the
active-voice and actor-first moves; the audience-first intake.

- <https://digital.gov/guides/plain-language/principles>
- Federal Plain Language Guidelines (<https://www.opm.gov/information-management/plain-language/>)
