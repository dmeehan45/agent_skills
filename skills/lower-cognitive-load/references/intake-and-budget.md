# Intake and budget

Phase 0. Nothing gets rewritten until this block exists and the author has seen
it. Every later decision — what to cut, how long it runs, how it opens — comes
from here, and guessing at it is how a rewrite ends up technically shorter and
practically useless.

## The contract block

Fill this in and show it back before touching the text.

```
SOURCE        what it is, how long, who wrote it, when
AUDIENCE      who reads it, what they already know, how they feel about
              the sender right now
CHANNEL       where it lands (phone inbox, Slack, blog, doc, in-app)
ONE THING     the single sentence they should be able to repeat afterwards
ONE ACTION    what they should do, or "nothing, just know this"
BUDGET        minutes → words (see below)
MUST SURVIVE  exact numbers, dates, names, commitments, legal wording,
              specific hedges the author cares about
TONE          the register that would be wrong to lose (dry, warm, blunt,
              apologetic, technical)
VOICE SAMPLE  where to find the author writing the way they talk
```

### Getting ONE THING right

Ask: if the reader remembers a single sentence in a week, what is it? Write it
in the reader's words, not the author's. Then check it against the source. If
the source cannot support it, you have found the real problem and it is not a
style problem.

If more than one sentence fits, the piece is a bundle. Say so and offer three
options: split it into separate sends, pick the one that matters this week, or
raise the budget. Do not silently write a piece with two centres of gravity —
that is the load you were hired to remove.

### When the audience is expert

Do not raise the density. Expertise changes *which words are free* (you can say
"idempotent" to engineers without defining it), not how much effort a reader has
to spend. Experts are just as busy, read on the same phones, and scan just as
hard. The only thing expertise buys you is vocabulary.

## The budget

Adult silent reading of English non-fiction averages **238 words per minute**
(Brysbaert 2019, meta-analysis of 190 studies). Reading aloud averages 183.

| Target | Ceiling | Plan for |
| --- | --- | --- |
| 1 min | 240 words | 190 |
| 2 min | 475 words | 380 |
| 3 min | 715 words | 570 |
| 5 min | 1,190 words | 950 |
| 10 min | 2,380 words | 1,900 |

**Ceiling** is the arithmetic. **Plan for** is the ceiling minus 20%, which is
what you should actually aim at, because the headings, lists, and white space
that make a piece scannable all consume budget without carrying much meaning,
and because a reader who finishes early trusts you more than one who finishes
exactly on time.

Three adjustments, applied to the plan number:

- **Phone-first, cold audience: take another 20% off.** An email blast to users
  who did not ask for it is a 60-second document no matter what the budget says.
- **Unavoidably technical content: take 10% off**, because the necessary terms
  cost the reader more per word.
- **Warm, opted-in audience** (a newsletter they subscribed to, a doc they asked
  for): use the ceiling.

Two things the budget does not do. It does not license padding to reach the
number — under budget is a good outcome. And it does not override structure: a
900-word piece that buries the point failed, whatever the counter says.

## The scanning reader

Readers take in roughly **20 to 28% of the words** on a page during an average
visit, and fall back to F-shaped scanning — first line across, then progressively
less of each line, then a vertical run down the left — precisely when a page
lacks headings and visual entry points.

So write for two readers at once:

1. **The scanner** reads the headings, the first sentence of each block, and the
   bold. Roughly a fifth of your words. This has to work on its own.
2. **The reader** reads all of it. This is the bonus tier.

If the scanner's version does not carry ONE THING and ONE ACTION, no amount of
sentence polish saves the piece. `structure.md` has the test.

## Channel profiles

### Email blast to users
250–400 words. Cold-ish, on a phone, one thumb. The subject line is the point,
not a tease. The first sentence repeats the point in case the subject was
truncated. One action, one link, one place to click. Three chunks maximum. Cut
background first: they did not ask for the history.

### In-app note or announcement
150–300 words. They are mid-task and you interrupted them. Lead with what
changed and what it means for them. Everything else goes behind a link.

### Release note / changelog entry
100–250 words. Grouped by what the reader can now do, not by which team shipped
it. Each entry front-loads the verb. No narrative.

### Short write-up shared for reaction
600–1,000 words. Warm audience, they will read it if it earns the time. Point
first, then the reasoning, then the open questions. Keep the open questions —
they are the reason it was shared.

### Newsletter edition
600–1,200 words. Opted in, but competing with everything else in the inbox.
Strong first line, sections that can be skipped independently, and a clear end.

### Slack / LinkedIn / social post
80–250 words. No headings; line breaks are the structure. First line has to work
as the whole post, because for most readers it is. No preamble at all.

### Long article → short version
800–1,200 words, plus a link to the full piece. This is the most dangerous
profile, because the temptation is to summarise everything shallowly. Do not.
Pick one argument from the article, make it completely, and let the link carry
the rest. A thin summary of eight ideas is worse than a full treatment of one.

## Output of this phase

The contract block, the budget number, the channel profile, and one line saying
what you will not be able to do inside that budget. That last line is what makes
the next conversation honest.
