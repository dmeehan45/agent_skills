# The four evidence passes

Launch all four as background subagents after the scripts have run, so each
has numbers to explain rather than invent. Fill in the angle-bracket
values from `.agents/retro.env` and the intake. Keep the two sentences
marked **(keep word for word)** exactly as written; they are what keep the
passes honest and harmless.

Each pass returns a short report in this shape:

```
## Findings
- [VERIFIED] <what, where (PR/commit/session/file), count>
- [INFERRED] <what the numbers suggest, and what would confirm it>
## Numbers I could not get, and why
## Anything that looks like a live issue (do not act on it)
```

---

## Pass A: the commit history

```
You are gathering evidence for a process retrospective on <REPO>, window
<START> to <END>. You are READ-ONLY: you must not create, edit, commit,
push, comment, label, or resolve anything; you only read and report.
(keep word for word)

Tag every finding VERIFIED if you read the thing itself, or INFERRED if
you are reasoning from a count or a pattern; report nothing untagged.
(keep word for word)

Start from this output of scripts/git-signals.sh:
<PASTE OUTPUT>

Then read commits, not just counts:
1. For each surface in "reopened 3+ times", read the commits that touched
   it. Tell deliberate iteration (a feature built in steps, bodies that
   say so) from rework (a fix of the previous commit, a revert, "again",
   "actually", a bug the earlier commit introduced). Report which, with
   the commit shas.
2. For each catch-up merge, name the branch, how long it had been open,
   and whether the same files were changed on both sides (a true
   collision) or the merge was clean (a long-lived branch).
3. For fix-on-fix chains, read the chain and say what the first fix
   missed.
4. Read the diff of each rule file (<RULE_FILES>) in the window. What was
   added, what was removed, and whether an addition restates something
   already in the file or in another rule file.
5. Sample ten non-merge commits with one-line bodies. Could a reader tell
   why the change was made? If not, that is a finding.

Do not count the same commit under two headings; name it once and
cross-reference. Keep the report under 600 words.
```

## Pass B: the pull-request record

```
You are gathering evidence for a process retrospective on <REPO>, window
<START> to <END>. You are READ-ONLY: you must not create, edit, commit,
push, comment, label, or resolve anything; you only read and report.
(keep word for word)

Tag every finding VERIFIED if you read the thing itself, or INFERRED if
you are reasoning from a count or a pattern; report nothing untagged.
(keep word for word)

Start from this output of scripts/pr-signals.sh (or, if absent, list the
PRs in the window yourself with the GitHub tool, newest first, including
merged and closed):
<PASTE OUTPUT>

Then, for each PR in the window:
1. Review threads. For every comment left by <REVIEWER_LOGINS> or by a
   person, was it answered? "Answered" means a reply, a commit that
   addresses it, or a resolve with a stated reason. Count answered and
   unanswered; list the unanswered ones with PR number and a one-line
   paraphrase. A security or data finding left unanswered goes under
   "live issue".
2. CI. Which checks went red on which pushes, and which step failed. Was
   the fix a real fix or an allowlist, a skipped test, a loosened rule?
3. Age. PRs still open at <END> that were opened before <END minus 14
   days>: number, title, what they are waiting on.
4. Definition of done. The template is <PR_TEMPLATE_PATH or "none">; the
   team's definition of done is <DEFINITION_OF_DONE>. For each merged PR,
   which required parts were missing (a telemetry section, verification
   steps, a preview link, a changelog entry, a migration note)?
5. Branches pushed with no PR in the window (compare the pushed branches
   in git-signals.sh to the PR list). Count them; they are sessions whose
   work ran no checks.

Name each PR under one heading only and cross-reference it from others.
Keep the report under 600 words.
```

## Pass C: the operators' own corrections

```
You are gathering evidence for a process retrospective on <REPO>, window
<START> to <END>. You are READ-ONLY: you must not create, edit, commit,
push, comment, label, or resolve anything; you only read and report.
(keep word for word)

Tag every finding VERIFIED if you read the thing itself, or INFERRED if
you are reasoning from a count or a pattern; report nothing untagged.
(keep word for word)

Privacy, which overrides everything below: quote only the operator's own
instructions to the agent, paraphrased as the rule they imply ("no em
dashes in copy"), never as a quote longer than a few words. Never report
anything an operator pasted from elsewhere, never product or customer
content, never a name other than the operator's handle. In team mode
(<MODE>), do not quote one operator's session in a way another could
recognise; report counts and the rule, not the person.

Start from this output of scripts/ledger-summary.mjs:
<PASTE OUTPUT>

Then:
1. Repeated corrections. Which instructions appear in two or more
   sessions? For each: the rule it implies, how many sessions, and
   whether a rule file (<RULE_FILES>) already says it. A correction that
   is already written down is a rule that did not hold.
2. Blocked on a person. For each session with a non-empty
   blocked_on_person: what was asked, was it answered before close, and
   could the session have done everything else first?
3. Automated turns. For sessions with turns.automated > 0: sample up to
   five wake-ups and say whether each found work to do. Report the share
   that found nothing.
4. Outcomes. Sessions that ended pushed-no-pr, abandoned or unknown: how
   many, and what the ledger or transcript says happened.
5. Where transcripts are reachable (<TRANSCRIPT_SOURCE>): read the FIRST
   and LAST pages of each session in the window, not the newest 100
   events. The opening prompt is where the ask lives; the close is where
   the outcome is. Count operator messages that re-state an earlier
   instruction.
6. Where transcripts are not reachable, stop and return these three
   questions for the retro to ask the owner: "What did you have to say
   twice this fortnight?", "Where did a session stop and wait for you?",
   "What did a session do that a rule already told it not to?"

Keep the report under 600 words.
```

## Pass D: the team's log and rule files

```
You are gathering evidence for a process retrospective on <REPO>, window
<START> to <END>. You are READ-ONLY: you must not create, edit, commit,
push, comment, label, or resolve anything; you only read and report.
(keep word for word)

Tag every finding VERIFIED if you read the thing itself, or INFERRED if
you are reasoning from a count or a pattern; report nothing untagged.
(keep word for word)

Read:
- the team's log: <LOG_SOURCE: a CHANGELOG, release notes, a journal
  table, an incident log, or "none">;
- the rule files: <RULE_FILES>;
- the skills folder, hooks config and CI workflows;
- the previous retro report: <PREVIOUS_REPORT or "none">.

Then:
1. Learned entries. In the log, which entries from the window or the
   previous window say "we learned" or name a lesson? For each, did a
   check, a skill or a rule follow? Which are still only words?
2. Rules broken. For each rule in the rule files that a commit, PR or
   ledger entry in the window visibly broke, name the rule, the evidence,
   and whether the rule has a check behind it. A rule broken with a check
   behind it means the check did not fire; say so.
3. Routines. For each of <ROUTINES>, where does its output land, and did
   it land in the window? A routine whose first phase sits in an open PR
   is "in progress", not "unrun"; check both before calling anything
   unrun.
4. Duplication. Which rules appear in more than one file? Do the copies
   agree?
5. Previous report. For each change it made or asked for, what is the
   evidence it held, partly held, did not hold, or could not be tested in
   this window?
6. Rule-file growth. From git-signals.sh, which files grew, and does the
   growth restate existing rules?

Keep the report under 600 words.
```

---

## Running them

- Launch all four at once, in the background, and do the scorecard
  arithmetic while they run.
- If a pass comes back with a finding that looks like a live issue, it
  goes to the top of the report untouched. The pass must not act on it,
  and neither does the retro.
- If a pass returns untagged findings, send it back for tags. Untagged
  findings read as verified and are usually not.
- The four passes name the same PR from different angles. The retro, not
  the passes, decides which pattern each PR belongs to.
