# Voice and machine tells

Phases 1 and 6. Phase 1 works out what the author sounds like. Phase 6 makes
sure the rewrite sounds like that and not like an assistant.

This matters more than it looks. A reader who clocks a piece as machine-written
stops reading, and they stop reading *for reasons they will not articulate* —
they will say it was boring or corporate. The point of a low-load rewrite is
that the reader finishes it. A machine-sounding rewrite fails that on the first
line, no matter how good its Flesch score is.

## Phase 1: the voice card

Get a sample of the author writing the way they talk. In descending order of
usefulness: a Slack or text thread, an email to a customer, a past newsletter,
a conference talk transcript, a comment they left somewhere.

**The dense source is the wrong sample.** It is a specimen of the voice you are
moving away from. Use it only to learn vocabulary and what they care about.

Fill this in:

```
VOICE CARD
  sentence range      shortest and longest they naturally write
  contractions        always / sometimes / never
  person              I / we / you — and which they avoid
  openings            how they start things (question? claim? story? news?)
  connectives         the joining words they actually use ("so", "but",
                      "which means") vs ones they never use ("moreover",
                      "thus", "hence")
  humour              dry / none / self-deprecating / absent under pressure
  hedging             do they qualify, and how ("I think", "roughly",
                      "we'll see")
  swearing / slang    yes and which, or no
  signature moves     the thing only they do
  never says          words that would be obviously not-them
```

With no sample available, say so in the delivery note and mark the voice as a
best guess for the author's read-through. Do not invent a personality.

## Phase 6: the machine tells

### Phrases

Strike on sight unless the author genuinely uses them:

```
delve · tapestry · landscape of · realm of · navigate the complexities
in today's fast-paced · ever-evolving · game-changer · unlock the power
harness · leverage · seamless · robust · holistic · multifaceted
underscore · testament to · at the end of the day · the key takeaway
dive in · deep dive · buckle up · paradigm shift · elevate · supercharge
transformative · empower · resonate · curated · bespoke · myriad
plethora · utilize · commence · endeavor · facilitate · encompass
crucial · pivotal · vital · meticulous · cornerstone
furthermore · moreover · additionally · consequently
```

Some of these are ordinary words. "Crucial" is a real word with a real job. The
test is whether *this author* would say it out loud to a colleague. Mostly they
would say "important", or better, they would say why it matters instead.

### Constructions

- **"Not just X, but Y."** The single loudest tell. One study of message data
  found variants of it in about 6% of messages. Also: "not merely", "not simply".
- **"It's not X — it's Y."** And its cousin "isn't about X, it's about Y".
- **Rule of three.** Three adjectives, three clauses, three examples, over and
  over. Real speech uses two, or four, or one.
- **Symmetric paragraphs.** Every section the same length with the same internal
  shape. People write lopsided.
- **Frictionless transitions.** Every paragraph connecting smoothly to the next
  with no jump, no aside, no change of pace.
- **The closing restatement.** A final paragraph that summarises what was just
  said and adds nothing. In a five-minute read, end on the last real point.
- **Openings that announce.** "In this post, we'll explore", "Let's take a look
  at", "Before we dive in".
- **Hedged enthusiasm.** "We're excited to announce", "we're thrilled to share".
- **Em dashes everywhere.** Two or three per paragraph, doing the work of full
  stops.
- **Bolded lead-ins on every bullet.** `**Thing:** explanation`, repeated eight
  times, is a slide deck wearing prose.

### The rhythm number

The objective half. `load_report.py` computes the sentence-length coefficient of
variation. Model prose clusters in a narrow band; human prose does not. Below
0.35, the piece is mechanically even regardless of who wrote it. Fix it by
varying the lengths, not by adding words.

## What is not a tell

Over-correction has its own smell. These are all normal human writing and should
not be "fixed":

- Starting a sentence with "But", "And", or "So".
- One-sentence paragraphs.
- Contractions.
- The occasional em dash where the author uses them.
- Short sentences. Fragments, used deliberately and rarely.
- A clean, well-organised structure. Being organised is not a tell; being
  *uniformly* organised is.

And never manufacture humanity: no deliberate typos, no fake hesitation, no
"honestly", no inserted personal anecdote that did not happen. That is worse
than sounding like a machine, because it is dishonest as well.

## Positive markers

What actually makes writing read as human, in rough order of power:

1. **A specific detail nobody would bother to invent.** "22% of seats" beats
   "many seats". "The Tuesday the invoice went out" beats "recently".
2. **An admitted limit.** "We do not know yet whether this holds for annual
   contracts."
3. **A real opinion, attributable to a person.** Not "it could be argued".
4. **Asymmetry.** One section much shorter than the others because there was
   less to say.
5. **A sentence that turns.** Sets up one thing and lands somewhere else.
6. **Restraint at the end.** Stopping when the point is made, rather than
   landing the plane with a summary.

Every one of those comes from the source material or the author, which is why
phase 0 asks for a voice sample and phase 3 asks what may not be cut. You cannot
add humanity in the final pass. You can only avoid removing it in the earlier
ones.

## Final check

Read the first three sentences of the rewrite. If they could have opened a piece
by anyone about anything, they are wrong — no matter how readable they are.
