# Turning what the session learned into something the next session cannot forget

A session forgets. The repo does not. The only learnings that count are
the ones that land in a file the next session reads, or a check it runs.
This reference says how to decide where each one goes, and who applies it.

It follows the fix ladder from the `retro` skill in this library, the
promotion rule in Anthropic's Claude Code memory guidance, and the same
rule stated independently by Cursor and Amp: **promote a learning into the
always-read instruction file only when the mistake or correction repeats;
keep that file short and prune it; procedures go in a skill, not the file
every session reads.**

## 1. Collect the raw material

Go through the session for these, in order. Write each as one line of
plain English, with the moment it happened.

1. **Corrections the owner made.** Anything they had to say that a rule, a
   skill, or the code should have made unnecessary. Count how many times
   this session, and search the instruction files and skills for whether
   it is already written down.
2. **Gates that went red**, and what the red was: a real defect, a gate
   that was wrong, or a gate the session did not know existed.
3. **Rules that were broken**, by this session, found by the owner, a
   reviewer, or a gate. A written rule broken anyway is the strongest
   signal here.
4. **Surprises.** A file that was not where the docs said, a skill whose
   step did not work, a tool call that needed three tries, a comment in
   code that was no longer true.
5. **Things that went well because of a rule or a skill.** One line each:
   a rule that earned its place is the argument for keeping it at the next
   prune.

## 2. Place each one on a rung

Ask in order. Stop at the first yes.

| Rung | Question | What it becomes |
|---|---|---|
| 1. A check | Can a machine tell whether this was done? And has it failed more than once? | A test, a lint rule, a CI step, a script that exits non-zero. Proven by breaking the thing and watching it go red. |
| 2. A skill | Does it matter only for one kind of task, and does it have steps? | A section in the skill that owns that task; a new skill only if none does. |
| 3. A short rule | Is it one or two sentences a session needs at one moment? | Those sentences, in the file that already owns the subject, at the place it is relevant. |
| 4. A long rule | Does the team need the why to follow the what, and no file owns it yet? | A section with reasoning, history and exceptions. Rare. |

Three further rules:

- **A correction made twice is at least rung 3. Three times, rung 1 or 2.**
- **A written rule that was broken anyway moves up a rung.** Not firmer
  words. If a rung-3 sentence was ignored, the question is what check or
  skill would have caught it.
- **A rung-1 candidate the session cannot prove by mutation stays a
  proposal.** Write the diff and the break you would run; do not land an
  unproven check. A check earns trust by failing.

## 3. Where a rule goes

Into the file that already owns the subject. Never a new "lessons" file
beside the real ones; that is how rules end up in three places that
disagree.

| Subject | Owning file (typical) |
|---|---|
| Words users read | the writing guide |
| How things look or move | the design system |
| Who the user is, what a feature is for | the product or user-model doc |
| Gates, failure classes, telemetry, migrations, changelog | the matching section of the instruction file (AGENTS.md / CLAUDE.md) |
| The end state of a session, previews, scheduled check-ins | the instruction file's definition-of-done section |
| How to do one kind of task | that task's skill |
| A durable product lesson | the changelog or decision log, and the owning doc if one exists |

## 4. Who applies what

This session may apply, in the close-out PR, without asking:

- **Rung 2**: a correction to a skill the session used (a wrong path, a
  missing step, a stale example). It rides the PR and the owner reviews it
  there.
- **Rung 3, when the correction was made at least twice this session or
  an existing rule was broken**, the sentence goes into a file that
  already owns the subject, and it does not touch areas the repo gates
  behind approval (auth, schema, build tooling, env behaviour, API
  contracts, or whatever the instruction file lists).

Everything else is handed to the owner as a decision, in the wrap-up,
with six parts: what is happening in plain words; why, one layer down;
what it costs to leave alone; the paths written as outcomes; which one
you recommend and why; what happens after they answer. Specifically:

- **Any rung-1 check.** It changes what every PR must pass. The decision
  carries the exact diff and the mutation that proves it fires.
- **Any change to the instruction file's failure rules, definition of
  done, or security section.**
- **Any new skill.**
- **Any pruning** of an existing rule. Deletion needs the owner.

Draft the exact text for all of them anyway. A decision that arrives with
the diff written is one the owner can take in a minute; "we should
probably add a rule about this" is a delay.

## 5. Write it so the next retro can read it

The fortnightly `retro` skill asks "did last time's changes hold?". Make
that answerable: in the wrap-up's learnings table, each row has the rung,
the file it went into or the decision it became, and the observable
behaviour that would show it held (for example "no PR this fortnight is
opened without the telemetry section").
