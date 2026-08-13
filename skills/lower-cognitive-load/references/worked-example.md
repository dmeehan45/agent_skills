# Worked example

One passage taken through all eight phases. The source is a section of an
internal pricing memo; the deliverable is the note that goes to customers. In a
real run the source would be the whole memo — this example scopes to one section
so the transformation can be shown line for line.

---

## Phase 0 — contract

```
SOURCE        section of an internal pricing memo, 397 words, written by
              the founder for the leadership team, last week
AUDIENCE      existing customers on per-seat plans. They know the product,
              they did not ask for this, and any email about pricing is
              read as "my bill is going up"
CHANNEL       email, opened on a phone
ONE THING     we're moving to usage-based pricing, and your bill won't
              move without a conversation first
ONE ACTION    none this month; just don't panic
BUDGET        2 min ceiling 475 → plan 380 → cold phone audience, so ~300
MUST SURVIVE  the 22% figure, the Q3 date, the three-phase shape, the
              commitment that spend caps ship before the migration, the
              promise to contact anyone whose bill would rise
TONE          direct, slightly blunt, not apologetic. The founder does not
              do corporate.
VOICE SAMPLE  their last three customer emails and #general posts
```

## Phase 1 — voice card (abridged)

```
contractions   always
person         "we" for the company, "you" for the customer, never "one"
openings       leads with the news, no preamble, often a sentence fragment
connectives    "so", "but", "which means". Never "moreover" or "thus"
hedging        real hedges only: "roughly", "we'll see"
signature      names the objection before the reader can raise it
never says     "excited to announce", "valued customer", "solution"
```

That last habit — naming the objection first — is the thing to protect. It is
also what makes the rewrite work.

## Phase 2 — diagnose

```
$ python3 scripts/load_report.py source.md --profile blast
```

| | |
| --- | --- |
| read time | 1.7 min against a 2 min budget |
| mean sentence | **38.9 words** |
| longest sentence | **66 words** |
| over 25 words | **70% of sentences** |
| rhythm CV | 0.50 |
| passive | **70% of sentences** |
| 3+ syllable words | **26%** |
| nominalizations | **62 per 1,000 words** |
| entry points | **1.3 per 500 words** |
| longest unbroken run | **389 words** |

Note the trap in the first row. The piece is *inside* its time budget and still
unreadable. Length was never the problem here; density was. A skill that only
counts words would have declared this fine.

Load events marked by hand:

- The point ("we are changing pricing") does not appear until the third
  paragraph, and even there it is phrased as an abstraction.
- Paragraph 1 is entirely process narrative: who deliberated, for how long.
- The reader's actual question — *does my bill go up* — is answered in the last
  sentence of the last paragraph.
- One heading for 397 words. Nothing to scan.

## Phase 3 — triage

| ID | Claim | Disposition | Where |
| --- | --- | --- | --- |
| C1 | per-seat misallocates cost toward heavy users | keep | opens "Why" |
| C2 | 22% of provisioned seats inactive in a given month | keep, exact | "Why" |
| C3 | high-dormancy accounts were flagged at risk | keep | "Why" |
| C4 | four quarters of deliberation, finance + product | **cut** | dropped |
| C5 | usage billing introduces variability | keep | "The obvious problem" |
| C6 | caps and forecasting are a precondition, not a follow-up | keep, exact | "The obvious problem" |
| C7 | three phases, Q2–Q3, volunteers first, per-seat retires end Q3 | compress | "When" |
| C8 | design-partner cohort selection criteria | link | FAQ |
| C9 | customers whose bill would rise get contacted first | keep, promote | lede + close |

C9 is the interesting one. In the source it is the last sentence of the last
paragraph. It is the only thing the reader actually wants to know, so it moves
to the opening line and gets repeated at the end.

## Phase 4–6 — the rewrite

### Before (397 words)

> **Reconsidering the Economics of Our Usage-Based Pricing Model**
>
> The decision to restructure the pricing architecture that has governed
> customer billing since the platform's initial commercial release was arrived
> at following an extended period of internal deliberation, during which a
> considerable quantity of usage telemetry was analysed by the finance and
> product organisations in parallel. It has become increasingly apparent over
> the preceding four quarters that the per-seat model, while offering a degree
> of predictability that was appreciated by procurement teams at larger
> accounts, systematically misallocates cost in a manner that penalises exactly
> the population of customers whose engagement with the product is most
> intensive, which is to say the customers whose retention is of greatest
> strategic importance to the business.
>
> The underlying dynamic is not complicated, although its consequences are.
> Under a per-seat arrangement, an organisation that purchases forty seats and
> utilises the platform heavily across all forty pays precisely the same amount
> as an organisation that purchases forty seats and permits thirty of them to
> lie dormant. The former organisation is, in effect, subsidising the latter.
> Analysis of the last twelve months of billing data indicates that
> approximately 22% of provisioned seats registered no activity whatsoever in
> any given month, and that the accounts exhibiting the highest ratio of dormant
> seats were also, unsurprisingly, the accounts that were most likely to be
> characterised as at-risk during quarterly business reviews.
>
> A transition to consumption-based billing, in which charges are assessed
> against the volume of work actually processed rather than the number of
> individuals nominally authorised to process it, resolves this misallocation.
> It should be noted, however, that such a transition introduces a degree of
> variability into the customer's monthly expenditure which was not previously
> present, and the mitigation of that variability through mechanisms such as
> spend caps and forecasting tools must be regarded as a precondition of the
> change rather than an enhancement to be delivered subsequently.
>
> The migration will therefore proceed in three phases across the second and
> third quarters, commencing with a cohort of volunteer accounts drawn from the
> existing design-partner programme, followed by a general availability window
> during which both models will operate concurrently, and concluding with the
> retirement of per-seat billing for all remaining accounts at the end of the
> third quarter. Customers whose modelled consumption-based expenditure exceeds
> their current per-seat expenditure will be contacted individually in advance
> of any change taking effect.

### After (242 words)

> **We're changing how billing works**
>
> **We're moving from per-seat pricing to usage-based pricing. Nothing changes
> for you until Q3, and no one's bill goes up without a conversation first.**
>
> **Why we're doing it**
>
> Per-seat pricing charges you for people, not for work.
>
> Buy 40 seats and use all 40, and you pay exactly what a company pays that
> bought 40 and uses 10. Last year, 22% of the seats companies paid for sat
> completely unused in any given month. Heavy users were quietly covering the
> cost of the dormant ones.
>
> Here's the part that bothered us most. The accounts with the most dead seats
> were also the accounts most likely to get flagged at risk in a quarterly
> review. They were paying for something they weren't getting, and then leaving.
>
> **What actually changes**
>
> You'll be billed for the work you process, not for how many people are allowed
> to log in.
>
> **The obvious problem with that**
>
> Usage-based bills move around. Finance teams hate that, and they're right to.
>
> So spend caps and a forecasting view ship **before** the migration, not after.
> That's a precondition, not a nice-to-have.
>
> **When**
>
> Three phases, Q2 into Q3:
>
> - Volunteer accounts from the design-partner programme go first.
> - Then a window where both models run side by side.
> - Per-seat billing retires at the end of Q3.
>
> If your usage-based bill would come out higher than your current one, we'll
> call you before anything changes. No surprises on an invoice.

## What actually happened, sentence by sentence

**The 66-word opener was deleted, not rewritten.** It is entirely C4: process
narrative. Nothing in it survives, because nothing in it is about the reader.
The rewrite opens with C9 instead — the answer to the question they are already
asking.

**"Systematically misallocates cost in a manner that penalises exactly the
population of customers whose engagement with the product is most intensive"**
became **"Per-seat pricing charges you for people, not for work."** Nine words.
Same claim, actor in the subject, abstract nouns replaced with concrete ones,
and it survives being said out loud.

**The 40-seat example moved from a 40-word sentence to a 24-word one** by
dropping "an organisation that purchases" twice and letting the reader supply
the parallel. Spoken language does this constantly; written language forgets it
can.

**"It should be noted, however, that such a transition introduces a degree of
variability"** became **"Usage-based bills move around."** The frame is deleted
outright and the nominalization ("variability") becomes a verb ("move").

**A short sentence was added where none existed:** "Finance teams hate that, and
they're right to." That is the author's signature move from the voice card —
name the objection before the reader can — and it is the line that makes the
piece sound like a person. It adds no claim; it concedes one the source already
implied.

**Rhythm.** The "Why" section runs 9 / 21 / 16 / 11 / 7 / 22 / 11 words. The
two source paragraphs it replaces ran 46 / 66 / 10 / 38 / 9 / 53. The source
was not just long; it was long *repeatedly*, and the two short sentences it did
have were stranded between 66-word and 38-word neighbours where nobody would
reach them. That is what makes dense writing tiring rather than merely slow.

## The rewrite that would have been wrong

An early pass produced this, and it fails the fidelity check:

> Most of the seats companies pay for go unused, so heavy users end up
> subsidising everyone else.

It reads well. It is 17 words. It is also false: the source says **22%**, and
"most" means over half. This is the vagueness failure in its natural habitat —
the writer reached for a plainer word and changed the fact. The strength check
in `triage.md` exists to catch exactly this.

## Phase 7 — verify

```
$ python3 scripts/load_report.py rewrite.md --baseline source.md --profile blast
```

| | before | after |
| --- | --- | --- |
| words | 397 | 242 |
| read time | 1.7 min | 1.0 min |
| mean sentence | 38.9 | 11.2 |
| longest sentence | 66 | 22 |
| over 25 words | 70% | 0% |
| rhythm CV | 0.50 | 0.48 |
| passive sentences | 70% | 5% |
| 3+ syllable words | 26% | 8% |
| nominalizations | 62/1k | 13/1k |
| scan payload | 39% | 60% |
| entry points | 1.3/500 | 20.7/500 |
| contractions | 5/1k | 36/1k |
| Flesch (info only) | 6 | 78 |

**The 20% test.** Headings only:

> We're changing how billing works · Why we're doing it · What actually changes ·
> The obvious problem with that · When

Plus the bolded lede and the bolded "before". A reader who takes in nothing else
learns that billing is changing, that there is a known problem with it, and that
their bill will not move without a conversation. ONE THING and ONE ACTION both
survive. Pass.

**Fidelity.** C1, C2, C3, C5, C6, C7, C9 all present. 22% intact with its "in
any given month" qualifier. Q3 intact. The precondition commitment is stated
more plainly and no more strongly. C4 and C8 on the cut list. Pass.

**Out loud.** Reads clean at speed. One catch on "the accounts with the most
dead seats were also the accounts most likely" — the repetition of "the accounts"
is deliberate and survives being spoken, so it stays.

## Cut list delivered with the rewrite

```
Dropped
  · The four quarters of deliberation and who was involved. It explains why
    you're confident; it doesn't help them.

Linked, not dropped
  · Design-partner cohort criteria → FAQ

Open question for you
  · The source says caps "must be regarded as a precondition". I wrote
    "ship before the migration, not after". That reads as a commitment
    with a date attached. Confirm you want to make it in an email.
```

That last line is the most useful output of the whole pass. The rewrite did not
add a promise, but it made an existing one legible — and a promise nobody could
parse is a promise nobody was going to hold you to.
