# Handoff doc template

Use when the session leaves work for a later session: a phase waiting on a
date, a verification that needs a connector this session lacked, findings
out of scope, a decision the owner has not made yet. Commit it as
`docs/plans/<scope>-closeout-prompt.md` (or wherever the repo keeps plans) on
the session's branch, so it
rides the PR and is reviewed like everything else.

Keep the two-part shape: section 1 is the state the next
session inherits; section 2 is the prompt to paste, written to be run by
someone who has read nothing else.

Rules that make the next session cheap instead of a re-derivation:

- **Settled decisions are listed and marked "do not re-ask".** With the
  date and, if it exists, the doc section that records them.
- **Every item has a priority, an owner, a verifiable end state, and the
  file:line it starts from.** "Fix the onboarding disclosure" is a wish;
  "`conversationalCopy.ts:225` names the fourteen days but not what stops
  on day 15; done when it names both and the comment above it no longer
  calls the boundary a later phase" is an item. (Google SRE workbook:
  an action item without an owner and an end state is a note.)
- **Dependencies are explicit**, including "needs the Stripe connector"
  and "needs PR #N merged first", and what to do if the dependency is
  not met (wait, ask, or skip).
- **What was NOT verified is stated as such.** A mock that agrees with
  our assumptions is not verification; say what was skipped and why.
- **No conversation content, message text, prompt content, or child
  names.** Same privacy bar as everything else the team files.

---

```markdown
# Handoff: close out <scope>

**Written <YYYY-MM-DD>**, at the end of the session that <what it did>.
Paste section 2 into a fresh session. Section 1 is the state it inherits.

---

## 1. Where things stand

**The scope** is <one paragraph in plain words>. Plan: `<path>`.
Strategy it implements: `<path>` (if any).

| Phase / PR | PR | State |
| --- | --- | --- |
| <name> | #<n> | merged / open, green, awaiting the owner's merge / open, red on <check> |

QA across the scope: `<qa/... path>`. <N> of <M> definition-of-done items
met; open: <ids>; held: <ids, why>.

**Decisions already made (do not re-ask).** <list with dates, pointing at
the doc section that records them>.

**Not verified in that session, and why.** <list>.

---

## 2. The prompt

---

You are closing out <scope> in `<owner/repo>`. <One sentence of
state.>

**Read before touching anything:**
- the repo's instruction file (`AGENTS.md` / `CLAUDE.md`) in full.
- `<plan doc>`, especially <section> (settled decisions) and the "what
  actually shipped" notes.
- `<qa report>`. This is your work list. Findings <ids> are yours.

**Check first whether PR #<n> has merged.** If it has, branch from `main`.
If it has not, <wait / ask / proceed on a branch off it>, because <why>.

### The work, in priority order

**1. <Title>. <Why it is first, in one line.>**

<file:line>. <What is wrong, in plain words, and what "done" looks like.>
Constraints: <copy rules, languages, which audience must not
be collapsed>.

**2. ...**

### When you are done

Run `/session-close`. End with a PR open into `main`, green, with a
preview link, and say plainly what you could not verify.
```
