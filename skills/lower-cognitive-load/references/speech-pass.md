# The speech pass

Phase 5. The structure is set and the scope is agreed. Now every sentence has to
survive being said out loud.

This is not a stylistic preference. In eleven of eleven controlled tests,
learners given the same material in conversational rather than formal wording
did better on transfer tests, at a median effect size of d = 1.11 — one of the
largest effects in instructional design. The mechanism is that a reader who
feels spoken to treats the writer as a conversational partner and works harder
to make sense of what is being said. Formal register does not signal rigour to a
reader. It signals that no one is home.

## The protocol

Go through the draft sentence by sentence and read each one as if you were
saying it out loud to one person who is standing in front of you. Mark five
signals:

| Mark | Signal | Usual cause |
| --- | --- | --- |
| `S` | you stumble | consonant pile-up, or a word you would not use |
| `P` | you pause somewhere odd | clause boundary in the wrong place |
| `B` | you run out of breath | too many words before the verb resolves |
| `R` | you re-word it mid-sentence | the written version was never the natural one |
| `F` | it comes out flat | no actor, no verb doing work, nothing at stake |

`R` is the most valuable mark. Whatever you said instead is usually the correct
sentence. Write that down before you lose it.

Then rewrite the marked sentences. Do not rewrite the unmarked ones. A sentence
that reads aloud cleanly is finished, even if it is long, even if the report
flagged it.

## Rhythm

The failure that makes prose feel machine-written is not length. It is
evenness. Language models produce a narrower variance in sentence length and
syntactic shape than people do; human writing, even careful writing, has
asymmetric pacing, interruptions, and digressions. Uniform sentence length is
the tell that survives every other edit.

So vary the lengths on purpose.

- After a long sentence, write a short one. Four words is fine. Three is fine.
- Never write three sentences in a row within four words of the same length.
- Put the shortest sentence in each section at the point you most want the
  reader to stop.
- Vary the openings too. Three consecutive sentences opening with the subject
  reads as a list; three consecutive sentences opening with a subordinate clause
  reads as a lecture.

`load_report.py` reports this as the length CV (standard deviation over mean).
Below 0.35 the prose is mechanically even. Around 0.5 is a person talking. The
number is a symptom check, not the goal — the goal is that it sounds right out
loud, and the CV is how you catch yourself when it does not.

## The breath rule

A sentence you cannot finish in one comfortable breath is too long, no matter
how well punctuated. That lands around 25 words for most people and hard-stops
around 30. Sentences past that are not wrong, they are expensive, and they
should be rare and deliberate.

The fix is almost never "add commas". It is:

- Split at the conjunction and keep the second half.
- Move the qualifier into its own sentence: "That only applies to legacy plans."
- Cut the clause that was protecting the author rather than informing the
  reader.

## Sentence moves

Each of these lowers load without touching meaning.

**Put a real actor in the subject.**
> The decision to restructure the pricing architecture was arrived at following
> an extended period of internal deliberation.

> We spent four months arguing about pricing. Here is where we landed.

**Turn nouns back into verbs.** Nominalizations bury the action.
> the mitigation of that variability through the implementation of spend caps

> spend caps keep the bill from swinging

**Front-load the point; move the condition after it.**
> While the per-seat model offered predictability that procurement teams
> appreciated, it systematically misallocated cost.

> Per-seat pricing misallocates cost. Procurement teams liked it because it was
> predictable, and that is the only reason it lasted this long.

**Cut the frame.** "It is important to note that", "it should be acknowledged
that", "one thing worth mentioning is". If it is important, say it. The frame
tells the reader you are about to say something, which is not information.

**Prefer the concrete noun.** "Provisioned seats registered no activity" →
"nobody logged in". "Engagement with the product is most intensive" → "they use
it every day".

**Use contractions.** Not for informality — for rhythm. "We will not" and "we
won't" scan differently out loud, and only one of them sounds like a person.
Match the author's habit from the voice card; do not force them on someone who
never uses them.

**Kill most em dashes.** You cannot hear an em dash. In speech it is either a
full stop or a comma, so pick one. Keep the occasional one for a genuine aside
in the author's own voice. `load_report.py` flags anything above four per
thousand words.

**Replace "there is / there are".** "There are three phases to the migration" →
"The migration runs in three phases." The dummy subject costs two words and
delays the actor.

**One idea per sentence.** If you need a semicolon, you have two sentences. If
you need two semicolons, you have three.

**Say numbers the way you would say them, but keep the digits.** "22% of seats"
stays 22%. You may *add* an intuitive gloss — "22% of seats, about one in five"
— but never swap the precise figure for the loose one. Precision is content;
this is the vagueness failure in its most tempting form.

**Verbs over adjective piles.** "A robust, comprehensive, enterprise-grade
solution" says nothing. What does it do?

**Ask the question the reader is asking.** A question as a heading or a lead-in
is the most natural transition in speech, and it does the work three sentences
of setup would do.

## Where the reader's attention goes

Two positions in a sentence carry more weight than the rest: the opening, which
sets what the sentence is *about*, and the ending, which is where readers place
emphasis. Put familiar material at the front and the new, load-bearing material
at the end. A sentence that ends on a throwaway qualifier wastes its strongest
position:

> Spend caps will ship before the migration, in most cases.

> In most cases, spend caps ship before the migration.

Same words, same hedge, but the second one ends on the promise instead of on the
doubt.

## What not to do in the name of natural speech

- **Do not add filler to sound casual.** "So, basically", "look", "honestly",
  "here's the thing". Written speech is not transcribed speech. Real transcripts
  are unreadable.
- **Do not add jokes, hype, or exclamation marks** that the author does not use.
- **Do not chop sentences into fragments to hit a readability score.** A run of
  five-word sentences is its own kind of exhausting, and it reads as
  condescension.
- **Do not swap a precise technical term for a friendly vague one.** Define it
  once and move on.
- **Do not simplify a quotation.** Quotes are verbatim or they are paraphrase,
  and paraphrase is not in quotation marks.
