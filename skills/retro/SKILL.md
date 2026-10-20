---
name: retro
description: >-
  A fortnightly retrospective on HOW the work with AI agents got done, not
  what was built: what was redone, what waited, what was ignored, which
  rules failed, and what the owner had to say twice. Use when asked to "run
  the retro", "/retro", do a process retrospective or post-mortem on agent
  sessions, work out "why do I keep correcting the agent", "where does the
  time go", "are our CLAUDE.md rules working", or set up a team so the
  agents' work can be reviewed later. It gathers evidence from four places at
  once (the commit history, the pull-request record, the operators' own
  corrections, and the team's log and rule files), fills the same scorecard
  every run so the second run can say better or worse, checks whether the
  last run's changes held, makes the small process fixes itself, and hands
  the owner only the decisions that are theirs. On a repo with no record of
  agent sessions, its first job is to set one up: an append-only ledger of
  agent actions (metadata only, never customer content) that the retro, and
  any later audit, can read. Works for one person with one agent and for a
  team running several agents across many repos. Read-only on the codebase
  during evidence gathering; never fixes a live defect inside the retro;
  never edits the agent harness's own hooks or settings. Not a code review
  (/code-review), not a code-health audit (handoff-audit), not product QA
  (qa-sweep).
---

# Retro: a retrospective on how the agent work got done

Every two weeks a session gathers evidence about **how the work got done**:
not what was built, but what was redone, what waited, what was ignored, which
rules failed, and what the people steering the agents had to say more than
once. It counts the same things every time, checks whether the last round's
changes held, writes a short report, makes the small process changes itself,
and hands the owner the decisions only they can make.

The point is that the lessons land in **files and checks the next session
will read or run**. The sessions forget; the repo does not.

> Applies to any stack, any agent (Claude Code, Codex, Cursor, Copilot, a
> custom harness), and any team size from one person to a department.
> Commands below are examples. Read the repo's own manifests, CI and agent
> instruction files to learn the real ones, and use those.

## Who this is for, and what changes with size

| | One person, one agent | A small team, a few agents | An organisation |
|---|---|---|---|
| **Whose corrections** | The owner's own messages to the agent | Each operator's messages, plus review comments between people | Operators' messages are often unreachable; the ledger and PR review record stand in |
| **Where the record lives** | A ledger folder in the repo | The same, one entry per session, merge-safe | The same per repo, plus a roll-up across repos |
| **Who decides** | The owner | A named decision owner per finding | The team lead for process, security or platform owners for anything on their turf |
| **Where the report goes** | A file in the repo | The same, linked from wherever the team reads | The same, plus one paragraph for whoever funds the agents |
| **Privacy bar** | Keep customer data out of the ledger | The same, and keep one operator's transcript from being quoted at another | The same, with retention set by policy and a stated data classification |

Everything else is the same. Setup and the mode switches are in
`references/setup-guide.md`.

## The stop line (read before anything else)

- **Evidence gathering is read-only.** The passes read git, PRs, the
  ledger, transcripts and logs. They never post a comment, resolve a
  thread, close a PR, label anything, or write to a tracker. A subagent
  given write tools will post a "helpful" summary unless told not to, so
  every prompt in `references/agent-prompts.md` says so, and keeps that
  sentence word for word.
- **Never fix a live defect inside the retro.** A security gap, a broken
  build, a stuck migration: the retro names it, with evidence, at the top
  of the report. The fix is its own change, with the owner's go-ahead.
- **Never edit the agent harness's own hooks or settings from the
  session.** The harness is right to block that. A fix that needs a hook or
  a settings change is written into the report as an exact diff for the
  owner to apply.
- **Never put customer or user content in the ledger or the report.** Not
  a message, not a name, not a prompt someone typed into the product. The
  ledger holds metadata and the operator's own instructions, paraphrased.
  When reading a transcript, quote only the operator's instructions to the
  agent, never what they pasted from elsewhere.
- **Never quote one person's transcript at another** in a team report.
  Patterns are reported in aggregate ("three of five operators re-stated
  the test rule") and the detail goes to that operator alone if at all.
- **Never schedule the retro to wake itself up.** It starts when a person
  opens a session and asks for it. Scheduled self-wake-ups were the single
  largest cost found in the first repo this ran on.

## The four ideas that make it work

1. **Evidence first, from where the work leaves traces.** Four places, and
   they catch different things. The commit history shows what changed and,
   if bodies are written well, why. The PR record shows review, CI and
   timing. The operators' own messages show what they keep asking for. The
   team's log and rule files show what was learned and whether it stuck.
   Any one alone misses whole classes of problem: commits never show that a
   reviewer was ignored; PRs never show that the owner re-types the same
   quality bar into every session.
2. **A fixed scorecard.** The same measures every round, so the second
   retro can say "better" or "worse", not just "here is a list". This is
   the Spotify health-check idea. `references/scorecard.md` has the rows.
3. **"Did last time's changes hold?"** The step most retrospectives skip,
   and the one that stops a rule file from growing forever. A rule that did
   not hold gets replaced by a mechanism, not reinforced with more words.
4. **The fix ladder: check, then skill, then short rule, then long rule.**
   An agent does not remember. Something that runs by itself beats
   something a session must read, and a short file read at the right
   moment beats a long one read at the start. `references/fix-ladder.md`.

## The ledger: the prerequisite this skill creates if it is missing

A retro needs a record of the agent sessions themselves: who ran what, on
which branch, how it ended, what the operator had to repeat, what blocked on
a person, which checks failed. Git and PRs hold half of that. The other half
evaporates when the session closes unless something writes it down.

The **agent action ledger** is that record: one small JSON file per
session, under `.agents/ledger/`, holding metadata and the operator's own
instructions only. It is written three ways, and a repo should have at least
the first two:

1. **By the agent at wrap-up**, because its instruction file asks for it
   (one line in CLAUDE.md or AGENTS.md: "end every session by appending a
   ledger entry with `scripts/ledger-append.sh`").
2. **By a hook when the session ends**, which fills in the counts nobody
   remembers (turns, tool calls, duration, automated wake-ups) from the
   transcript and merges them into the agent's entry.
3. **By a person**, for sessions in agents that have neither.

`references/ledger.md` has the schema, the privacy rules, and the solo and
team variants. `scripts/retro-init.sh` creates the folder, the config, and
prints the two snippets (instruction-file line and hook) for the owner to
apply.

**If the ledger does not exist when the retro is asked for, setup comes
first, and the retro still runs** on what git and PRs can show. The report
marks every ledger-derived row "not yet measured, ledger started
<date>" and the next run has its baseline.

## The run

### 0. Intake (two minutes)

- **Window.** Default the last 14 days, or from the previous report's date.
  Find the previous report in `RETRO_REPORT_DIR` (default `.agents/retro/`).
  If the gap is longer than the cadence, widen the window to cover it and
  say so in the report. A missed fortnight is written down, not skipped.
- **Config.** Read `.agents/retro.env`. If it is missing, run
  `scripts/retro-init.sh` (see setup-guide) and continue.
- **Mode.** `RETRO_MODE=solo` or `team`. Team mode changes who is quoted,
  who decides, and how operators are named (see setup-guide).
- **Reach.** Decide now which of the four evidence sources you can read:
  git (always), PRs (`gh` or a GitHub tool), the ledger (if started),
  transcripts (`~/.claude/projects/<project>/*.jsonl` locally, a sessions
  API on the web, nothing for some agents), the team's log and rule files.
  Anything unreachable becomes an interview question for the owner in
  pass C, never a silent gap.

### 1. Evidence: four passes, in parallel, read-only

Run the scripts first; they are cheap and give the subagents numbers to
explain rather than invent. Then launch the four passes as background
subagents using the prompts in `references/agent-prompts.md`, filled in with
the repo's own names. Each pass returns findings tagged **verified** (it saw
the thing) or **inferred** (it is reasoning from a count), and nothing else.

| Pass | Reads | Catches |
|---|---|---|
| **A. Git** | `scripts/git-signals.sh` output, then commit bodies for the surfaces it flags | Rework (the same files reopened), catch-up merges, fix-on-fix chains, rule files growing, commits with no reason given |
| **B. PRs** | `scripts/pr-signals.sh` if `gh` is present, else a GitHub tool | Review findings never answered, CI red by step, PRs open past the cadence, the gap between the definition of done and what PRs contain |
| **C. Operators** | `scripts/ledger-summary.mjs`, then transcripts or the ledger's `corrections` fields, else a ten-minute interview | What people had to say twice, what blocked on a person, automated wake-ups, sessions that ended with nothing to show |
| **D. Log and rules** | The team's changelog or journal, the instruction files, skills, hooks, CI config, the previous report | Rules broken in the window, routines that did not run, lessons written down and not acted on, the same rule in three places |

Pass C is the one that differs most by size. Solo: read the owner's own
messages (first and last pages of each session, not the newest 100 events;
the opening prompt is where the ask lives). Team: read the ledger first,
transcripts only where the team has agreed to it, and treat PR review
comments between people as a second source of corrections. Organisation:
the ledger and PR record are usually all you have, so the ledger's
`corrections` field has to be written at wrap-up or the retro is blind here.

### 2. Fill the scorecard

Every row in `references/scorecard.md`, every run, with the previous value
beside it. A row you cannot compute says "not measured" and why, never a
guess. Twelve honest rows beat eighteen with six blanks: trim the scorecard
to what the repo can compute and keep the nine core rows in any repo.

### 3. Did last time's changes hold?

For each change the previous report made or asked for: **held**, **partly**,
**did not hold**, or **not yet testable**, with the evidence. A rule that
did not hold moves up the ladder (a check or a skill), it does not get a
firmer sentence. A check that never fired is suspect: break the thing it
guards on a scratch branch and confirm it goes red, or mark it "unproven".

### 4. Patterns, each with numbers and a reason

Group the evidence into at most eight patterns. Each one carries:

- **What happened**, in ordinary words, with counts and named PRs or
  sessions. Name each PR under one pattern only and cross-reference it from
  others, so the same PR is not counted as both rework and a collision.
- **Why it matters**, in the concrete: hours, a shipped defect, a reviewer
  ignored, a rule nobody could follow.
- **Which rung** of the fix ladder, and why not the rung above.
- **The fix**, as the exact change: the file, the check, the diff.

Separate **live issues** (a security finding nobody answered, a broken
guard in production) from process patterns, put them first, and do not fix
them here.

### 5. Act, within the stop line

- **Rungs 2 to 4 (a skill, a short rule, a long rule) you make yourself**,
  in the file that already owns the subject. A repeated correction about
  words goes in the writing guide; about looks, the design system; about
  tests, the testing section of the instruction file. A new "rules" file
  beside the real ones is how rules end up in three places that disagree.
- **Rung 1 (a check, a hook, a CI step)** you write as an exact diff in the
  report for the owner to apply, and you write the test that proves the
  check fires.
- **Decisions only the owner can make** are written as whole decisions:
  what is happening, why, what it costs to leave alone, the paths as
  outcomes, your recommendation, and what happens after they answer. Fewer
  than four per report. More than that and none get answered.

### 6. Write the report

`references/report-template.md`. Plain English first, the detail labelled
and below. Opens with live issues, then the scorecard, then "did it hold",
then patterns, then the changes made, then the decisions. One page for the
owner to read; the rest for whoever implements. Save it to
`RETRO_REPORT_DIR/YYYY-MM-DD.md` and commit it with the process changes on
one branch.

### 7. Ledger the retro, set the next date

Append a ledger entry for this session (`task: "retro YYYY-MM-DD"`). Write
the next run's date in the report footer. Do not schedule it; a person
starts the next one.

## How to tell it is working, by the third run

- Section 3 is mostly **held**. If it is mostly **did not hold**, the fixes
  are too low on the ladder.
- **Rule-file size is flat or shrinking** while the scorecard improves.
- **Operators' repeated corrections appear less often**, and the ones that
  remain are new.
- **Decisions get answered within a week.** If they do not, the report is
  too long or the decisions are not written as outcomes.
- **The ledger is written by the agents without being asked**, and the
  hook fills the counts. If entries are missing, that is the first finding
  of the next retro.

## Failure modes seen while building it

- **Subagents that act instead of read.** A PR-reading agent with write
  tools posted a summary comment. The read-only sentence stays in every
  prompt.
- **Session paging that never reached the opening prompt.** Read the first
  and last pages of each session.
- **Reporting a plan as unrun when its first phase sat in an open PR.**
  Check both before calling anything unrun.
- **Counting the same PR twice** across rework and collision.
- **Fixing a live issue inside the retro.** The database connector refused
  destructive SQL from an unattended session, correctly, and the fix went
  to the owner anyway. It should have started there.
- **Writing a hook from the session.** The harness blocked it, correctly.
- **A ledger nobody writes.** A ledger that depends on the agent
  remembering is a rule, not a mechanism. The hook is the mechanism; the
  instruction-file line is the fallback; a missing entry is a finding.
- **Quoting a transcript in a team report.** It read as blame. Aggregate,
  and take detail to the person.

## Files in this skill

| File | What it is for |
|---|---|
| `references/setup-guide.md` | First run on a new repo: tiers from solo to organisation, what to configure, how to rebuild from the original |
| `references/ledger.md` | The agent action ledger: why, the schema, privacy, the three ways it gets written, team variants |
| `references/scorecard.md` | The fixed rows, how each is computed, which nine are core |
| `references/agent-prompts.md` | The four read-only subagent prompts, parameterised |
| `references/fix-ladder.md` | Check, skill, short rule, long rule; choosing a rung; proving a check fires |
| `references/report-template.md` | The report, the decision format, the footer |
| `references/sources.md` | Where this comes from, and what transfers |
| `scripts/retro-init.sh` | Creates `.agents/retro.env`, the ledger folder, the report folder; prints the instruction-file line and the hook snippet |
| `scripts/git-signals.sh` | Pass A numbers for the window, from the paths in `retro.env` |
| `scripts/pr-signals.sh` | Pass B numbers via `gh`, when present |
| `scripts/ledger-append.sh` | Write one ledger entry from flags; used by agents at wrap-up and by people |
| `scripts/ledger-from-transcript.mjs` | The session-end hook: counts from a Claude Code transcript, merged into the session's entry; metadata only |
| `scripts/ledger-summary.mjs` | Pass C numbers: sessions, outcomes, repeated corrections, blocks, wake-ups, over the window |
