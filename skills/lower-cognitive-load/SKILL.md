---
name: lower-cognitive-load
description: >-
  Rewrite dense or complex writing into a version that is fast to scan, cheap to
  read, and sounds like a real person saying it out loud, for readers who will
  give it five minutes or less: email blasts, notes to users, release notes,
  announcements, internal memos, newsletter editions, short write-ups, and posts
  derived from longer source material. Use when someone asks to make writing
  easier to read, faster to scan, less dense, less academic, more conversational,
  more human, or "less AI", or wants a long-form article, essay, spec, or report
  turned into something short that a busy reader will actually finish. Measures
  the source (read time, sentence rhythm, scan payload, machine tells), triages
  every claim into keep / compress / cut / link so nothing is dropped silently,
  rebuilds the piece point-first, runs a read-aloud speech pass and a de-AI pass,
  then verifies the result against the original for meaning, numbers, hedges, and
  voice. Preserves meaning, message, and tone. It is not a "make it casual" pass
  and it never lowers load by making a claim vaguer. Not a fact or sourcing check
  (content-rigor), not interface copy (frontend-polish, ux-quality-review).
---

# Lower cognitive load

Someone wrote something dense. It is probably good. It is also expensive to
read, and the reader it now has to reach will give it two minutes on a phone
between meetings. Your job is to make it cheap to read without making it less
true.

> This file is an internal working doc, so it does not obey its own spoken-style
> rules. The deliverable does.

## The one idea this rests on

There are exactly two ways to lower the cost of reading something.

```
carry less        remove whole ideas          → intrinsic load down
carry it better   present the same ideas well → extraneous load down
```

**Carry less** is a scope decision. It belongs to the author, it happens in the
open, and what got cut goes in a list they can see. **Carry it better** is
craft: structure, sentence shape, word choice, rhythm. You can do as much of it
as you like without asking anyone.

There is a third thing that looks like both and is neither: making a claim
vaguer so it takes less effort to process. "22% of seats went unused" becomes
"a lot of seats go unused". The sentence got shorter and the reader learned
less. That is not compression. That is damage, and it is the single most common
way this kind of rewrite fails. Cut the whole idea or keep it precise. Never
blur it.

## Three constraints, one job

```
usable = scannable × spoken × faithful
```

Multiplicative, so a zero anywhere is a zero.

- **Scannable.** A reader who takes in only the headings, the first sentence of
  each block, and the bolded phrases still gets the message. Readers take in
  roughly 20 to 28% of the words on a page. Design for that reader first, and
  let the full read be the bonus.
- **Spoken.** Every sentence survives being said out loud by a person who is
  not performing. No stumbles, no place where you run out of breath, no phrasing
  you would instinctively change halfway through.
- **Faithful.** Meaning, message, tone, numbers, hedges, and the author's voice
  all survive, or their removal is on a list the author signed off.

Scannable without spoken gives you a robot's bullet deck. Spoken without
scannable gives you a charming ramble nobody finishes. Either without faithful
gives you a nice-sounding lie.

## Hard rules

- **No silent cuts.** Every claim, number, caveat, name, and commitment that
  does not make it into the output appears in the cut list you hand back.
- **Never weaken a claim to shorten it.** "Usually" does not become "always".
  "We think" does not become "we know". "Up to 40%" does not become "40%".
  A hedge is content.
- **No new claims.** You may not invent an example, a statistic, a benefit, a
  date, or a specific detail that was not in the source. If the rewrite needs a
  concrete example to work and the source has none, ask for one.
- **Casual is not the goal.** Do not add slang, jokes, exclamation marks, emoji,
  hype, or second-person chumminess that the author does not use. Conversational
  means "a person said this", not "a brand said this".
- **Keep the necessary technical term.** Define it once, in line, in six words.
  Paraphrasing a precise term into a vague one is the vagueness failure wearing
  a helpful face.
- **Reading-level scores are thermometers, not targets.** Do not chop sentences
  to move a Flesch number. A text of short, simple, incoherent sentences scores
  beautifully and reads terribly.
- **Length is a budget, not a score.** Hitting the word count while burying the
  point is a failure, not a partial success.
- **Match the author, not a house style.** The output should sound like the
  person who wrote the source on a day they were talking instead of writing.
- **If the source is already at target, say so and stop.** Rewriting a piece
  that is already cheap to read only costs it voice.

## Phases

Run in order. Phase 3 needs the author. Everything before it is preparation and
everything after it is execution.

### 0. Contract — `references/intake-and-budget.md`

Do not start rewriting. Establish, in a short block you show back:

- **Who reads this**, and what they already know. Experts want it scannable too.
- **Where they read it** (inbox on a phone, Slack, a doc, a blog post). The
  channel sets the shape.
- **The one thing** they should walk away knowing.
- **The one action**, if any, they should take.
- **The budget**, in minutes, converted to words at 238 wpm.
- **What must survive** verbatim: legal wording, numbers, names, commitments,
  dates, the specific hedges the author cares about.

If the source has no single "one thing", you have a bundle, not a piece. Say so
and ask whether to split it or pick one.

### 1. Voice calibration — `references/ai-tells.md`

Before you write a word, get a sample of the author writing the way they talk:
a past newsletter, a Slack message, a customer email, anything unguarded. The
dense source is a sample of their *writing* voice, which is exactly the voice
you are moving away from, so it is the wrong reference.

Record their contraction habit, sentence-length range, how they open, whether
they use questions, what they never say. If no sample exists, say that the
output is a best guess at voice and flag it for the author's read-through.

### 2. Diagnose — `scripts/load_report.py`

```bash
python3 scripts/load_report.py source.md --profile brief
```

Profiles: `blast` (2 min), `brief` (5 min), `explainer` (10 min). The report
gives read time against budget, sentence rhythm, longest sentences, scan
payload, entry-point density, buried openers, nominalizations, filler, and
machine tells.

Then read the source and mark the **load events** the script cannot see: a term
used before it is defined, a forward reference, a buried lede, a paragraph doing
three jobs, an idea that only makes sense if you read the paragraph twice.
`references/structure.md` lists the ones worth hunting.

### 3. Triage — `references/triage.md`

Build the claim ledger. Every claim in the source gets one disposition:

| | |
| --- | --- |
| **keep** | earns its place at full precision |
| **compress** | same claim, fewer words, no loss of precision |
| **cut** | leaves the piece entirely; goes on the cut list |
| **link** | leaves the body, survives as a link or an appendix line |

This is where the real load reduction happens. A 3,000-word article does not
become a 5-minute read by tightening sentences. It becomes one by dropping
two-thirds of its ideas.

**Show the author the cut list before you write.** Ask about anything you are
unsure of. Get agreement on scope, then write once.

### 4. Rebuild the spine — `references/structure.md`

- **Point first.** The conclusion opens the piece. Then why. Then detail. A
  reader who leaves after two sentences should leave correctly informed.
- **Four chunks, maximum**, at the top level. Working memory holds about four
  things.
- **One idea per block.** If a paragraph needs "and also", it is two paragraphs.
- **Headings carry information.** "What changes for you" beats "Changes".
  "Overview" carries nothing. Read the headings alone; they should tell the
  story.
- **Old before new**, sentence to sentence and paragraph to paragraph. Open with
  the thing the reader already has; close on the thing you want them to keep.
- **Bold the load-bearing phrase**, once per section at most. Bold everywhere is
  bold nowhere.

### 5. The speech pass — `references/speech-pass.md`

The heart of the skill. Go sentence by sentence and read it as if saying it out
loud to one person. Mark every place you would stumble, pause somewhere odd, run
out of breath, or change the wording mid-sentence. Those marks are the work
list.

Then rewrite for rhythm rather than for length: **vary the sentence lengths on
purpose.** Machine prose is not too long, it is too even. A four-word sentence
after a twenty-two-word sentence is worth more than either sentence improved.

Sentence-level moves, examples, and before/after pairs live in the reference.

### 6. De-machine — `references/ai-tells.md`

Strip the tells: "not just X but Y", "it's not X, it's Y", triads of everything,
frictionless transitions, "delve", "leverage", "seamless", "crucial", em dashes
doing the work of full stops. Then check the piece still sounds like the person
from phase 1 and not like a well-behaved assistant.

The rhythm number from the report is the objective half of this. A sentence
length CV below 0.35 means the prose is mechanically even, whoever wrote it.

### 7. Verify — `references/triage.md`

```bash
python3 scripts/load_report.py rewrite.md --baseline source.md --profile brief
```

Then, by hand, in this order:

1. **Fidelity.** Walk the claim ledger. Every "keep" and "compress" claim is
   present and no more or less certain than it was. Every number, unit, date,
   and name matches the source exactly. Every hedge survived or is on the cut
   list.
2. **The 20% test.** Read only the headings, the first sentence of each block,
   and the bold. Does that alone deliver the one thing and the one action? If
   not, the structure failed, not the sentences.
3. **The out-loud test.** Read the whole thing aloud, at speed, once. Any place
   you re-read, re-phrase, or run out of air goes back to phase 5.
4. **The voice test.** Would the author recognise this as theirs? Would they be
   embarrassed by any line?

## The gate

Do not deliver while any of these are true:

- A claim changed strength, precision, or meaning.
- A number, date, name, or commitment differs from the source.
- Something was cut and is not on the cut list.
- The headings-only read does not carry the message.
- Read time is over budget and the author has not agreed to the overage.
- Sentence length CV is under 0.35, or more than a quarter of sentences run past
  25 words.
- A machine tell survives.

## What you hand back

1. **The rewrite**, ready to send.
2. **The cut list.** What left the piece, and where it went (dropped, linked,
   held for a follow-up). Grouped, one line each, no apology.
3. **The numbers.** Before and after, from the report: words, read time, rhythm,
   scan payload.
4. **Open questions**, if any: the places where you could not tell whether a
   nuance mattered, with the source wording quoted so the author can rule.

Keep the delivery note itself short. A long memo explaining a short document is
a bad joke to make in a skill about cognitive load.

## When not to use this

- **Contracts, policies, safety and medical instructions, anything legally
  operative.** Precision beats speed and the rewrite risk is not worth it. You
  can still restructure and add headings without touching the wording.
- **The dense original is the deliverable.** A piece written for someone to sit
  with and think about is not failing at being scannable. Ask before flattening
  it. The right output is often a short version *alongside* the long one, not
  instead of it.
- **The writing is fine and the problem is the idea.** No amount of rhythm fixes
  an argument that does not hold. Say that instead.

## References

- `references/intake-and-budget.md` — the contract, channel profiles, and the
  word-budget maths.
- `references/triage.md` — the claim ledger, cut discipline, and the fidelity
  check.
- `references/structure.md` — spine, chunking, headings, the 20% test.
- `references/speech-pass.md` — the read-aloud protocol and the sentence moves.
- `references/ai-tells.md` — voice calibration and the de-machine list.
- `references/worked-example.md` — one dense passage taken all the way through.
- `references/evidence.md` — why each rule is here, with sources.
