# The fix ladder

An agent does not remember. Something that runs by itself beats something a
session must read, and a short file read at the right moment beats a long
one read at the start. Every finding gets placed on a rung, and the report
says why not the rung above.

| Rung | What it is | When it fits | Who applies it |
|---|---|---|---|
| **1. A check** | A test, a lint rule, a CI step, a hook, a script that exits non-zero | The thing can be stated precisely enough to test, and it has failed more than once | The owner, from an exact diff in the report (hooks and settings especially) |
| **2. A skill** | A short file loaded only when a matching task comes up | The lesson is a workflow, has several steps, and applies to a kind of task rather than every session | The retro, in the skills folder |
| **3. A short rule** | One or two lines in the file every session reads, at the moment it is relevant (next to the PR rule, in the testing section) | A single instruction that is cheap to read and hard to test | The retro, in the file that already owns the subject |
| **4. A long rule** | A section with the reasoning, the history, the exceptions | The team needs the why to follow the what, and the subject has no owning file yet | The retro, sparingly, and only after rungs 1 to 3 have been considered |

## Choosing a rung

Ask, in order:

1. **Can a machine tell whether this was done?** Then rung 1, and the retro
   writes the diff and the test that proves the check fires.
2. **Does this only matter for one kind of task?** Then rung 2. A skill is
   read when it is needed, which is the cheapest form of memory an agent
   has.
3. **Is it one sentence a session needs at one moment?** Rung 3, placed at
   that moment in the file.
4. **Otherwise rung 4**, and the report says what it would take to move it
   up next time.

A correction the operator made twice is at least rung 3. Three times, and
it is a candidate for rung 1 or 2. A written rule that was broken anyway
moves up a rung; it does not get firmer words.

## Where a rule goes

Into the file that already owns the subject. Words go in the writing
guide. Looks go in the design system. Tests go in the testing section of
the instruction file. Finishing work goes next to the definition of done.

A new "rules" or "house bar" file beside the real ones is how rules end up
in three places that disagree, and every disagreement gets applied by
somebody. The first run of this retro made that mistake and the file was
folded back in the same day.

## Proving a check fires

A check earns trust by failing, not by passing. Before a rung-1 change is
written into the report:

1. On a scratch branch, break the thing the check guards.
2. Run the check. Confirm it goes red.
3. Confirm it went red **for the reason named**, not because the break
   also broke something else. Two tells of a bad assertion: it matches the
   whole file when the behaviour lives in one function, and the input you
   gave it never exercised the branch you disabled.
4. Restore. Write down what you ran and what happened, not what you
   intended.

A check that cannot be made to fail is not measuring what it claims to.
That is the finding.

## "Did it hold?"

For each change the previous report made or asked for, the verdict is one
of four, with the evidence:

- **Held**: the behaviour it targets did not recur, or the check fired when
  it should have.
- **Partly**: it recurred less, or in a new form.
- **Did not hold**: it recurred as before. Move it up a rung.
- **Not yet testable**: nothing in the window could have triggered it. Say
  so; do not count it as held.

A rung-1 change that never fired in the window is "not yet testable" until
it has been proven on a scratch branch, after which it is "held, proven by
mutation".
