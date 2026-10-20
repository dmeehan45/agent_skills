# The wrap-up

The last message of the session. It stands alone: a reader who sees only
this knows what shipped, where to look at it, what is not done, and what
to decide. Written for the owner, in plain words, so that a non-engineer
can decide. Lead with anything red or unverified.

```markdown
## Where it stands

<One paragraph. What this session set out to do and what state it is in.
If anything is red, not verified, or waiting on a person, that is the first
sentence.>

## The PRs

| PR | What it does, in one line | CI | Preview | Render |
| --- | --- | --- | --- | --- |
| [#N](url) | ... | green / red on `<check>` | [link](url) → route → what to look at | link or n/a |

## QA of the whole

<What was walked end to end, on which preview, as which sample parent, and
what it found. Findings fixed in this session say which commit. Findings
not fixed are in the handoff below, by id.>

## Not verified, and why

<Bullet list. Each: the thing, why it could not be verified here (no
connector, needs a merge first, needs a date), and what would verify it.
"Nothing" is an acceptable answer only if every PR's Verification section
was actually run.>

## Docs updated

<Bullet list of the plan, runbook, user-model, skill and journey-map files
changed so they describe what shipped. changelog entries filed, as
title + kind + surface.>

## Follow-ups

<Either "none" or: the handoff doc path, and the items in it by priority,
one line each, with what each waits on.>

## What this session learned

| Learning | Rung | Where it went | How we will know it held |
| --- | --- | --- | --- |
| ... | 1 / 2 / 3 / 4 | file + section, or "decision below" | ... |

## Decisions for you

<Zero or more, each in the six-part shape in `learning-capture.md` (what is happening, why, the cost of leaving it,
the paths as outcomes, the recommendation, what happens after). If zero, say "None.">

## What you could learn from this one

<One to three concepts, tied to the files touched.
Only if the owner has asked to learn as they go.>
```
