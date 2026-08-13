# Triage and fidelity

Phase 3 and phase 7. The first decides what leaves the piece; the second proves
nothing left by accident. Together they are the difference between compression
and damage.

Plain-language rewriting has a well-documented failure mode: *communication by
subtraction*, where the simplifying pass deletes exactly the qualifications,
conditions, and precision that made the original worth reading, and the result
is easier to read and less true. The ledger below exists to make that
impossible to do quietly.

## The claim ledger

Walk the source and pull out every **claim**: anything a reader could act on,
argue with, or be misled by. Statements of fact, numbers, commitments,
recommendations, causal explanations, and the caveats attached to them.

Do not pull out sentences. Pull out claims. One sentence often holds three.

| ID | Claim (source wording) | Role | Disposition | Where it went |
| --- | --- | --- | --- | --- |
| C1 | "22% of provisioned seats registered no activity" | evidence for the core argument | keep | body, section 1 |
| C2 | "arrived at following an extended period of internal deliberation" | process narrative | cut | dropped |
| C3 | "spend caps and forecasting tools must be a precondition" | commitment | keep | body, section 3 |
| C4 | three-phase migration timing | detail | compress | one line in "When" |
| C5 | design-partner cohort selection criteria | detail | link | linked FAQ |

### The four dispositions

**keep** — survives at full precision, wording may change. Numbers, dates,
names, and hedges come across exactly.

**compress** — same claim, fewer words, *no loss of precision*. This is a
rewriting move, not a scope move. "Analysis of the last twelve months of billing
data indicates that approximately 22% of provisioned seats registered no
activity whatsoever in any given month" → "Last year, 22% of paid seats sat
unused in any given month." Same claim, same number, same hedge ("in any given
month" survives), 30 words to 12.

**cut** — leaves entirely. Goes on the cut list. The reader will not know it
existed, so the test is: would they feel misled if they later read the source?
If yes, it is not a cut, it is a link.

**link** — leaves the body, stays reachable. A link, a footnote, an appendix
line, a "more detail here". Use this for anything a minority of readers
genuinely need. It is how you keep faith with the careful reader while writing
for the fast one.

## What you may never cut

- **Numbers with consequences.** Prices, limits, dates, percentages that support
  the argument.
- **Commitments.** Anything the reader could hold the author to.
- **Caveats that change a decision.** "This only applies to accounts on the
  legacy plan" is not detail; it is the difference between correct and wrong.
- **Conditions and exceptions** attached to a benefit.
- **Attribution and credit.** Whose work, whose data, whose idea.
- **Safety, legal, privacy, and compliance wording.** Restructure around it;
  do not rewrite it without the owner.
- **The author's genuine uncertainty.** If they said "we think", they think.

## What to cut first

In order. Most pieces get to budget before you finish this list.

1. **Throat-clearing.** Everything before the point actually starts. The first
   paragraph of a dense piece is usually a runway, and the piece takes off in
   paragraph two.
2. **Process narrative.** How the decision got made, who met, how long it took,
   what was considered. Readers care what you decided and why it is right, not
   how hard it was.
3. **Background the audience already has.** The most common overspend.
4. **Pre-emptive defence.** Paragraphs answering objections nobody in this
   audience will raise. That is a conversation for the long version.
5. **Second and third examples** of the same point. Keep the most concrete one.
6. **Alternatives considered and rejected.** Interesting to the author, load for
   everyone else.
7. **Meta-commentary.** "In this post we will", "as mentioned above", "before we
   turn to". Signposting a five-minute read is like a table of contents on a
   postcard.
8. **The nuance paragraph for the pedants.** This is the hardest one, and the
   right home for it is usually a link, not the bin.
9. **Hedging that protects the author rather than informing the reader.** "It
   could be argued that" is not a hedge, it is a shrug. Real hedges — "roughly",
   "in our tests", "for accounts over 50 seats" — stay.

## Compression moves that never cost precision

These shorten without touching meaning, so apply them freely before you start
cutting scope.

| Move | Before | After |
| --- | --- | --- |
| Un-nominalize | "the mitigation of that variability" | "mitigating that" |
| Name the actor | "it was decided that" | "we decided" |
| Cut the frame | "it is important to note that X" | "X" |
| Preposition chain → verb | "in order to achieve a reduction in" | "to cut" |
| Relative clause → adjective | "customers who are on legacy plans" | "legacy-plan customers" |
| Kill the double | "each and every", "first and foremost" | pick one |
| Number instead of description | "a significant proportion" | "22%" |

That last one is worth noticing: the precise version is usually *shorter* than
the vague one. Vagueness is not a compression technique, and it never was.

## The cut list

Delivered with the rewrite, always. Grouped, one line each, no apology.

```
CUT LIST — pricing note, 3,100 words → 240

Dropped
  · The deliberation timeline and who was involved
  · The comparison to competitor per-seat models
  · Three of the four worked billing examples (kept the 40-seat one)

Linked, not dropped
  · Design-partner selection criteria → FAQ
  · Full phase-by-phase migration dates → status page

Held for a follow-up
  · The argument about annual-contract customers. It needs its own note;
    it does not fit here and it half-fits everywhere.

Open questions for you
  · Source says "must be regarded as a precondition". I wrote "ships
    before the migration, not after". Is that a promise you want to make
    in this wording?
```

The "held for a follow-up" and "open questions" sections are the valuable ones.
They are where the author finds out what their own piece was carrying.

## The fidelity check

Phase 7, by hand, before anything ships.

**1. Ledger sweep.** Every `keep` and `compress` row: find it in the rewrite.
Confirm it says the same thing at the same strength.

**2. Number sweep.** Every digit, unit, currency, date, percentage, and version
number in the rewrite matches the source exactly. Check the ones you retyped
most carefully; those are where errors live.

**3. Hedge sweep.** Search the source for hedge words and confirm each one
either survived or is on the cut list:

```
may · might · could · roughly · approximately · about · up to · at least
some · most · often · usually · typically · generally · tends to · likely
we think · we believe · in our experience · early data · so far · pilot
```

**4. Strength check.** These substitutions are all failures, and all of them
happen while trying to sound confident and spoken:

| Source | Rewrite | Verdict |
| --- | --- | --- |
| usually | always | strengthened, wrong |
| we believe | we know | strengthened, wrong |
| up to 40% | 40% | strengthened, wrong |
| 22% of seats | most seats | vaguer *and* wrong |
| in our tests | in practice | scope widened |
| should | will | commitment invented |
| we are considering | we are building | commitment invented |

**5. Reverse read.** Read the rewrite as someone who has not seen the source,
write down what you now believe, then read the source. Any gap between the two
is the finding.

If a fidelity failure and a load target conflict, fidelity wins and the budget
moves. That is not a compromise, it is the order of operations.
