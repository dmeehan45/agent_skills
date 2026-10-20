---
name: session-close
description: >-
  Close out a body of work at the end of a coding-agent session, cleanly and
  completely, so nothing is left half-finished, unverified, undocumented, or
  only remembered. Invoke as `/session-close` at the end of any session that
  pushed commits, and especially after a multi-PR session. It inventories
  everything the session touched (branches, PRs, migrations, scratch files,
  deferral comments), runs the repo's gates locally, QAs the WHOLE body of
  work as one thing rather than PR by PR (a fresh-eyes review of the union
  diff, the changed flow walked end to end on the preview, phone and theme
  checks, copy in every language, telemetry on every new path), brings every
  PR to the done state (open into the default branch, green, preview link,
  template sections truthful, migrations applied and recorded), updates the
  docs that now describe something that is no longer true, puts every loose
  end in exactly one home (done now, a committed handoff doc for the next
  session, or dropped with a reason), and places every learning on the fix
  ladder (a check, a skill, a short rule, a long rule) with the rule text
  drafted and the contract changes handed to the owner as whole decisions.
  Ends with a wrap-up that stands alone. Not a merge (the owner merges), not
  the fortnightly process retro (that is `retro`), not a full product sweep
  (`qa-sweep`), and never a scheduled check-in. Works for any stack and any
  agent that reads an instruction file.
---

# Session close

A session is not finished when the branch is pushed, and it is not finished
when a PR is open either. It is finished when the body of work has been
looked at as one thing, every PR is in the done state, the docs say what
shipped, every loose end has a home, and what the session learned is
somewhere the next session will read or run. This skill is that last hour,
done the same way every time.

**When to invoke.** `/session-close` at the end of any session that pushed
commits. At the end of a multi-PR session it is not optional: each PR was
checked alone, and the user uses them together.

> Written against a reference implementation: a TypeScript web app on a
> hosting platform with per-branch previews, a CI gate set, database
> migrations, an analytics event catalog, translated copy, and a product
> changelog the owner reads. Steps that name one of those apply when the
> repo has it. Read the repo's instruction file (AGENTS.md, CLAUDE.md, the
> contributing guide) for its real names and commands, and use those.

## 0. The stop line

- **You never merge.** Green plus a preview link is where the work ends.
- **Never schedule anything** unless the owner asked for it: no delayed
  wake-up, no loop, no PR subscription. Every scheduled wake-up replays the
  whole conversation; one repo lost a week of usage to hourly check-ins on
  a PR that had been green since the first hour. Wait for CI in this
  session, then stop.
- **Never answer a red gate with an allowlist, a baseline, a tolerated
  count, or a skipped test.** Fix the defect, or fix the gate in the open
  and say so.
- **Never report something as verified that was described rather than
  run.** The honest wrap-up names what was not verified and why. A mock
  you wrote agrees with whatever you assumed.
- **Never change the instruction file's failure rules, definition of done,
  or security section, or add a new gate, without the owner's decision.**
  Draft the text; hand over the decision. `references/learning-capture.md`
  says exactly what this session may apply on its own.
- **Privacy bar.** The handoff doc, the changelog, the wrap-up and the
  learnings table carry no customer content, message text, prompt content,
  or personal names from the product.

## 1. Why it is shaped like this

The practice it follows is published, not invented here. The parts that
several teams state independently:

- **A session ends by persisting state outside the context window, and the
  next session starts by reading it, not re-deriving it.** Anthropic's
  long-running-agent harness ends every session with "a git commit and
  progress update" and starts the next by reading the git log and the
  progress file; its context-engineering guidance calls the same thing
  structured note-taking; Cline's memory bank updates "current focus,
  recent changes, next steps" after each session; Amp's handoff starts a
  fresh thread carrying only what matters. Section 6 is this skill's
  version.
- **A close-out ends in owned, tracked action items with a verifiable end
  state, not a prose summary.** Google's SRE workbook: "a postmortem
  without subsequent action is indistinguishable from no postmortem", and
  every action item has an owner, a priority and a measurable end state.
  Atlassian's retrospective play puts actions in the tracker, not the
  document. The Scrum Guide: work that does not meet the definition of
  done returns to the backlog rather than being presented. Section 6.
- **Promote a learning into the always-read instruction file only when it
  repeats; keep that file short; procedures go in a skill.** Anthropic's
  Claude Code memory guidance (add to CLAUDE.md when Claude "makes the
  same mistake a second time" or "you type the same correction that you
  typed last session"; under 200 lines; prune), Cursor's rules guidance
  ("add rules only when you notice Agent making the same mistake
  repeatedly"), Amp's "update AGENTS.md based on what I told you in this
  thread", and agents.md's "living documentation". Section 7.
- **Show evidence rather than asserting success, from a fresh pair of
  eyes.** Anthropic's best-practice guidance: before counting work done,
  have a subagent that sees only the diff and the criteria review it, and
  report test output and commands, not claims. Section 4.

One vendor's mechanism each, borrowed because it fits: the `retro` skill's
fix ladder (a check, then a skill, then a short rule, then a long rule),
and the SRE workbook's "what went well, what went poorly, where we got
lucky".

Sources, read 2026-10-20: code.claude.com/docs/en/best-practices and
/memory; anthropic.com/engineering/effective-harnesses-for-long-running-agents
and /effective-context-engineering-for-ai-agents; sre.google/workbook/postmortem-culture;
scrumguides.org; atlassian.com/team-playbook/plays/retrospective;
cursor.com/docs/context/rules; ampcode.com/docs/customize/agents-md;
agents.md; docs.cline.bot/prompting/cline-memory-bank.

## 2. Inventory: what did this session touch?

Run the script first. It is read-only and prints everything in one pass.

```
git fetch origin <default-branch>
bash skills/session-close/scripts/session-inventory.sh [origin/<default-branch>]
```

It lists the branch's commits, every other local branch ahead of the base,
the working tree, files changed, deferral markers the branch added in code
("TODO", "not yet shipped", "later phase", "temporary"), test files,
schema files, translation files, telemetry files, docs and rules touched,
and untracked scratch files. Its area globs are a starting point; edit
them to match the repo.

Then the parts a script cannot see:

- **The PRs.** List every PR whose head is a branch this session pushed.
  Note number, state, base branch, draft or not.
- **The plan.** Which plan, ticket, or report the session worked from, and
  its definition-of-done list if it has one.
- **The corrections.** Every message where the owner corrected course this
  session. Write each as one line now, while the conversation is in
  context; section 7 needs them.
- **Anything still running.** Background agents, workflows, loops.

## 3. The gates, here

Run the command CI runs, locally, plus any gate it leaves out because it
needs a base ref (a guard on new test files, a copy-freshness check): run
those with the base ref supplied by hand. A red here is work now, in this
session. A red check on a new test means go and break the thing the test
guards and watch it fail; never write the proof from intent.

## 4. QA the whole body of work

This is the step a per-PR session never does. Scope it to what the session
changed; the periodic sweep covers the rest.

1. **Fresh-eyes review of the union diff.** The repo's review command on
   each branch, or one subagent given only the diff against the default
   branch and the plan's acceptance criteria, told it has no write tools
   and may not post anything. Findings are fixed now or go in the handoff
   with an id.
2. **Walk the one flow the session changed most**, end to end, on the
   preview, in a real browser, as a sample user. Across PRs the joins are
   where it breaks: a wall that a later PR moved, a state an earlier PR
   stopped writing.
3. **Phone and every theme** for any surface touched; reduced motion if
   motion changed. A before-and-after render if the preview cannot show
   it (an animation, a glow, a state that is awkward to reach).
4. **Copy.** Changed words exist in every language the product ships, and
   pass the repo's copy rules.
5. **Telemetry.** For anything new: an event when the user arrives, acts,
   succeeds, fails; failures reach whoever is on call; model calls are
   named, traced and costed. Then re-read each PR's telemetry section
   against what the code now does; a false "none" passes the form and
   fails the user.
6. **Production's own signal.** If anything merged during the session,
   read the error tracker since the first merge. No access: say so under
   "Not verified".
7. **Re-read every PR's verification section** and ask of each line: did
   this session run it, or write it? Anything written is run now or moved
   to "Not verified".

## 5. Bring every PR to the done state

For each PR, every row of section B in `references/close-out-checklist.md`:
open into the default branch, green on the current head, no conflict,
threads answered, preview link read from the deployment record and ready at
the pushed commit, render link if visual, template sections truthful,
migrations applied and recorded, changelog entries filed, and the
description still matching the diff after the session's later pushes.

A PR this session did not open but pushed to is held to the same bar.

## 6. Loose ends, each in exactly one home

Collect every deferral marker the script found, every "later" in the
conversation, every dependency on a person, a date, a merge, or a
credential, every out-of-scope discovery, and every QA finding not fixed.
For each, one of three:

- **Do it now.** Small, in scope, and it would otherwise become the next
  session's first hour.
- **File it in the handoff.** `references/handoff-template.md`, committed
  on the branch so it rides the PR. Each item has a priority, a verifiable
  end state, and the file:line it starts from. Settled decisions are
  listed as "do not re-ask".
- **Drop it, with the reason written** in the wrap-up. "Decided not to"
  is a reason. Silence is not.

A critical finding, or one live in production, goes to the top of the
wrap-up at once; it does not wait in a handoff.

Then make the docs true (section E of the checklist): the plan's "what
actually shipped" note per phase, stale "not yet" comments in code, the
user-model doc if what a feature is for moved, runbooks and journey maps,
and any skill whose instructions were wrong when this session followed
them. A doc that describes the product as it was before this session is a
loose end too.

## 7. Place the learnings

`references/learning-capture.md` is the method. In short: list the
corrections, the red gates, the broken rules, the surprises and the rules
that earned their keep; put each on a rung (check, skill, short rule, long
rule; a correction made twice is at least a short rule; a rule broken
anyway moves up a rung); write the exact text; apply what this session is
allowed to apply (a skill fix, a short rule in the owning file after a
repeated correction) and hand the rest to the owner as whole decisions
with the diff already drafted.

Every learning gets a row in the wrap-up table with the rung, where it
went, and the observable behaviour that would show it held, so the
fortnightly `retro` can answer "did it hold?".

## 8. The wrap-up

`references/wrap-up-template.md`, filled in, as the last message. It leads
with anything red or unverified, lists the PRs with CI state and links,
says what was QA'd as a whole and what was not verified, names the docs
and changelog entries, points at the handoff, tables the learnings, and
hands over the decisions.

Before sending it, section H of the checklist: nothing scheduled, nothing
still running that the wrap-up does not mention. Then stop. If CI is
still running, wait for it in this session and send the wrap-up when it
has reported; a wrap-up that says "CI pending" is not a close.

## Where the detail lives

| Need | Where |
| --- | --- |
| The full row-by-row checklist | `references/close-out-checklist.md` |
| The next-session handoff doc | `references/handoff-template.md` |
| Which learning goes where, and who may apply it | `references/learning-capture.md` |
| The last message | `references/wrap-up-template.md` |
| The one-pass inventory | `scripts/session-inventory.sh` |
| The fortnightly look at how the work got done | `retro` |
| A scoped product sweep | `qa-sweep` |
