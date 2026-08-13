# Structure

Phase 4, plus the load-event hunt in phase 2. Structure is the highest-leverage
part of this skill and the part people skip, because sentence editing feels like
progress and rearranging feels like procrastination. It is the other way round.

In the study that first quantified this (51 users, five versions of the same
site), concise text scored 58% better on measured usability, a scannable layout
47% better, objective wording 27% better — and doing all three together scored
124% better. Structure and sentence craft compound. Neither substitutes for the
other.

## Load events: what to mark in the source

Read the source once, marking these. The script cannot see any of them.

- **Buried lede.** The point arrives in paragraph three, or in the last sentence
  of paragraph one.
- **Forward reference.** "As we will see below", "for reasons explained later".
  The reader now has to hold an unresolved thing.
- **Term before definition.** A word used, then defined two paragraphs on, or
  never.
- **Pronoun with a distant antecedent.** "This means" where *this* refers to the
  whole previous paragraph.
- **The paragraph doing three jobs.** Sets up, argues, and caveats in one block.
- **The stacked qualifier.** A sentence whose main claim is wrapped in three
  conditions before it arrives.
- **The reread.** Anywhere you had to go back a line. Mark it even if you cannot
  say why. Especially then.
- **Unmarked switches.** The piece changes topic, timeframe, or audience with no
  signal.
- **Numbers without an anchor.** "22%" with nothing to compare it to.
- **Silent hierarchy.** Four things listed in prose where only two matter.

## Pick a spine

Choose one and commit. Mixing them is the most common structural failure.

**Announcement** — what changed · why · what it means for you · what to do
**Argument** — the claim · the evidence · the strongest objection · so what
**Explainer** — the question · the short answer · how it works · the catch
**Update** — where we are · what moved · what is stuck · what is next
**Teardown** — what is broken · why it happens · what to do instead

Whichever spine, the same rule opens it: **the point goes first.** Conclusion,
then support, then detail. A reader who stops after two sentences should stop
correctly informed, not misinformed. This is the inverted pyramid, and it is the
opposite of how good dense writing is usually built — dense pieces earn their
conclusion, which is exactly why converting them means turning them upside down.

The lede is the hardest 30 words in the piece. Write it last, after the body has
told you what the piece actually says.

## Chunking

**Four top-level chunks, maximum.** Working memory holds about four items;
a reader who has to track seven sections is spending capacity on navigation
instead of content. If you need more, you have two pieces.

**One idea per block.** If a paragraph needs "and also", split it. If it needs
"but", that is usually the interesting half and it may deserve its own block.

**Blocks stay short.** 40–80 words in a scannable piece. Not because long
paragraphs are wrong, but because on a phone a 120-word block renders as a grey
wall and gets skipped whole.

**Order old before new.** Readers expect a sentence to open with something they
already have and close with what is new — the given-new contract. It holds
between paragraphs too: each block should open by touching what the previous one
left, and close on what you want carried forward. Misplacing old and new
information is, in Gopen and Swan's assessment, the single most common problem
in professional writing.

Practically: end each block on the phrase you want the next one to pick up.

## Headings

Headings do more work than any other element, because for most readers they
*are* the document.

- **Informative, not labelling.** "What changes for you" over "Changes".
  "Why per-seat pricing punishes your best users" over "Background".
- **Front-load the information-carrying word.** Scanners fixate on the first
  two words of a line, and only those.
- **Answer or assert; do not tease.** "The problem with usage pricing" tells the
  scanner nothing. "Usage bills move around, so caps ship first" does.
- **One per 150–200 words** in a scannable piece.
- **Read them alone.** In sequence, the headings should tell the story with a
  beginning and an end. If they read as a table of contents, rewrite them.

## Lists

Lists are not automatically lower load. A list strips the connective tissue
between items, so anything whose meaning lives in *how the parts relate* gets
harder, not easier, when bulleted. Reasoning does not belong in a list.

Use a list when the items are genuinely parallel, discrete, and unordered
relative to each other: steps, options, things that changed, what you need.

- Five items or fewer. Longer lists are a table or a set of subheadings.
- Front-load every item; the first two words carry it.
- Keep them grammatically parallel. Mixed shapes cost the reader a re-parse per
  item.
- Do not nest. A nested bullet is a heading pretending to be a bullet.
- Never bullet a two-item list. That is a sentence with an "and" in it.

## Emphasis

**One bolded phrase per section, at most**, on the phrase that carries the
section. Bold is a promise to the scanner that this is the part worth stopping
for, and a piece with eight bolded phrases has made that promise eight times and
kept it zero times.

No italics for emphasis in scannable copy; they are hard to see at a glance and
harder on small screens. No underline; it reads as a link. No ALL CAPS.

## The 20% test

The acceptance test for structure. Run it in phase 7, and run it again after any
structural edit.

1. Strip the piece to headings, the first sentence of every block, and the
   bolded phrases. `load_report.py` reports this as the scan payload and
   prints the heading-only read.
2. Read only that.
3. Ask three questions:
   - Does it deliver ONE THING?
   - Does it make ONE ACTION obvious?
   - Is anything in it *wrong* out of context? (This catches first sentences
     that only make sense after the sentence that follows them.)

Fail any of the three and the fix is structural. Do not fix it by bolding more.

## Signposting what stays hard

Some ideas are irreducibly difficult, and the answer is not to simplify them
into something false. Mark them instead:

> Here is the part that takes a minute.

Naming the difficulty lowers load on its own, because the reader stops wondering
whether they have missed something obvious. Then: define the term once in six
words, use one concrete example, and stop. Do not repeat it in three different
framings; that is three times the load, not one third.
