# Report template

Save as `RETRO_REPORT_DIR/YYYY-MM-DD.md`. Plain English first, detail
labelled and below. The owner reads the first page; whoever implements
reads the rest.

```markdown
# Retro: <YYYY-MM-DD>

Window: <start> to <end> (<n> days; <"on cadence" | "widened to cover a
missed run on <date>">). Mode: <solo | team>. Previous report: <path or
"none, this is the baseline">.

Evidence reached: git <yes>, PRs <yes | not used | unreachable: why>,
ledger <n entries | not yet started, started today>, transcripts <local |
api | interview | none>, log <source | none>.

## The one-page version

<Three to six sentences. What the fortnight looked like in ordinary words.
The one or two things that matter most. Whether last time's changes held.
What you changed. What you need decided.>

## Live issues (not fixed here)

<None, or each as: what, where, evidence, who should fix it, how urgent.
These are not process findings. They go first because they do not wait for
a cadence.>

## Scorecard

| Row | This run | Previous | Direction | Note |
|---|---|---|---|---|
| Surfaces reopened 3+ times | | | | |
| Catch-up merges | | | | |
| Commits with a failing check, by step | | | | |
| Reviewer findings answered | | | | |
| Open PRs older than 14 days | | | | |
| Routines with no run | | | | |
| Sessions blocked on a person | | | | |
| Rule-file size (lines) | | | | |
| Rules broken in the window | | | | |
| <added rows> | | | | |

"Not measured" rows say why, in the note.

## Did last time's changes hold?

| Change from <previous date> | Rung | Verdict | Evidence | If not held: moved to |
|---|---|---|---|---|

## Patterns

### 1. <Plain-English name>

**What happened.** <Counts, named PRs or sessions. Each PR named under one
pattern only; cross-reference from others.>

**Why it matters.** <The concrete cost: hours, a defect shipped, a reviewer
ignored, a rule nobody could follow.>

**Rung, and why not the one above.** <...>

**Fix.** <The exact change: file, check, diff. "Made in this branch" or
"for the owner to apply" or "decision 2 below".>

<Up to eight patterns. Verified findings before inferred ones, and each
tagged.>

## Changes made in this branch

- <file>: <what and why, one line each>

## Changes for the owner to apply (rung 1)

<Each as an exact diff or command, with the test that proves it fires and
what you saw when you ran that test on a scratch branch.>

## Decisions

<Fewer than four. Each in six parts, in plain English, in this order:>

### Decision 1: <the question in one line>

1. **What is happening.** <In words the owner would use. The symptom, not
   the component.>
2. **Why.** <One layer down, still in ordinary words.>
3. **What it costs to leave alone.** <Who, how often, how bad. "I don't
   know how often" is an acceptable answer; implying is not.>
4. **The paths, as outcomes.** <Two, at most three. For each: what changes
   for the people doing the work, what it costs, what it risks.>
5. **Recommendation, and why.**
6. **What happens after you answer.** <What I do next, whether it is
   reversible, what ships.>

## Ledger note

This retro's session: <ledger entry id>. Ledger coverage this window: <n
of ~m sessions>; <"the hook is installed" | "the hook is not installed;
counts are self-reported">.

## Next run

<Date, two weeks out.> A person starts it. Nothing is scheduled.
```

## Writing rules for the report

- Name the thing in ordinary words first; the internal term once, in
  brackets, if the implementer will need it.
- Numbers over adjectives. "4 of 11 review findings unanswered" beats
  "review is often ignored".
- No pattern without a count, and no count without a reason.
- Verified before inferred, and say which is which.
- A decision the owner cannot act on in one read is not ready. Rewrite it.
- In team mode, patterns are about the work, never about a person. Detail
  that would identify someone goes to them, not in the file.
