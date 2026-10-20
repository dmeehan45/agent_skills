# Setting up the retro in a repo

The first run on a new repo is a setup run. It creates the config and the
ledger, prints the two snippets the owner has to apply, and still runs the
retro on what git and PRs can show, so the second run has a baseline.

## The one-paragraph version

Copy `skills/retro/` into the place your agent loads skills from. Run
`scripts/retro-init.sh` from the repo root. Edit the paths it guessed in
`.agents/retro.env`. Apply the two snippets it printed: the instruction-file
line (so agents write ledger entries) and the hook (so the counts are
filled in). Run `/retro`. Treat the first report as the baseline. Run it
again in two weeks.

## Tiers

Pick the one that describes you now. Moving up later is adding, not
redoing.

### Tier 0: one person, one agent, running locally

- **Ledger:** `.agents/ledger/`, written by the agent at wrap-up and by the
  session-end hook.
- **Operators' corrections (pass C):** read your own transcripts. Claude
  Code keeps them at `~/.claude/projects/<project-slug>/*.jsonl`; the
  `"type":"user"` lines are what you typed. Read the first and last pages
  of each session.
- **PRs (pass B):** if you work on `main` without PRs, say so in
  `retro.env` (`RETRO_PR_FLOW=none`) and the PR rows read "not used". The
  retro will still ask, once, whether a PR flow would catch what you keep
  catching by hand.
- **Decisions:** yours. The report writes them as whole decisions anyway,
  because a decision you can act on in one read is the one that gets made.
- **Report:** `.agents/retro/YYYY-MM-DD.md`, committed.

### Tier 1: one person, agents in the cloud and in the terminal, PRs on

- Everything in Tier 0.
- **Transcripts** for cloud sessions come through the agent's sessions API
  when one exists (Claude Code on the web exposes one), else from the
  ledger alone. Set `RETRO_TRANSCRIPTS=local,api`.
- **Automated wake-ups** become a scorecard row. Any scheduled self
  check-in or event-driven wake counts. If the number is not zero, the
  first question is whether each one found anything.
- **Reviewer bot:** name its login in `RETRO_REVIEWER_LOGINS` so pass B
  can ask "were its findings answered?".

### Tier 2: a small team, several agents, one or a few repos

- Everything in Tier 1, plus `RETRO_MODE=team`.
- **Operators are named by handle** in the ledger and the retro aggregates
  by handle but reports patterns, not people. Write that in
  `.agents/ledger/README.md`, which `retro-init.sh` drafts for you.
- **Corrections** come from the ledger's `corrections` field, written by
  the agent at wrap-up, and from PR review comments between people. Reading
  another person's transcript needs the team's agreement; default to not.
- **Decision owner per finding.** `RETRO_DECISION_OWNER` is the default;
  a finding on someone else's turf names them instead.
- **Cadence** is still two weeks, started by a person. Rotate who starts
  it so the retro is not one person's hobby.
- **Where the report is read:** link it from wherever the team already
  reads (the PR that commits it is usually enough).

### Tier 3: an organisation, many teams, many repos

- Everything in Tier 2, per repo. The retro runs per repo; the roll-up is
  a separate, read-only step.
- **Cross-repo roll-up:** a nightly job copies every repo's
  `.agents/ledger/` into one read-only location, and
  `scripts/ledger-summary.mjs --dir <that location>` gives the
  organisation view: sessions by agent, by team, outcomes, corrections
  that repeat across teams, wake-up counts. The per-repo files stay the
  source of truth; the roll-up never writes back.
- **Policy fields:** set retention and data classification in each ledger
  README. The schema has no field for content, by design; do not add one.
- **Who reads what:** operators' corrections aggregated across teams tell
  the platform team which rule belongs in a shared check rather than in
  forty CLAUDE.md files. That is the organisational payoff of the fix
  ladder.
- **One paragraph for whoever pays for the agents:** sessions, outcomes,
  the share of turns that were automated, and the two or three patterns
  that cost the most. It goes at the top of the roll-up, not in each repo's
  report.

## What `retro-init.sh` does

1. Creates `.agents/retro.env` with guessed values:
   `RETRO_TEST_PATHS`, `RETRO_MIGRATION_PATHS`, `RETRO_I18N_PATHS`,
   `RETRO_SRC_PATHS`, `RETRO_RULE_FILES` (every instruction file it can
   find: CLAUDE.md, AGENTS.md, `.cursorrules`,
   `.github/copilot-instructions.md`, `.claude/skills/*/SKILL.md`),
   `RETRO_REVIEWER_LOGINS`, `RETRO_LOG_SOURCE`, `RETRO_ROUTINES`,
   `RETRO_MODE`, `RETRO_DECISION_OWNER`, `RETRO_REPORT_DIR`,
   `RETRO_PR_FLOW`, `RETRO_TRANSCRIPTS`. Every guess is commented so the
   owner knows what to check.
2. Creates `.agents/ledger/README.md` (what it is, who reads it, the
   privacy rules, retention) and `.agents/retro/`.
3. Prints the instruction-file line and the hook snippet. It does not
   apply either. The hook is the owner's to install; the instruction-file
   line the session may add if the owner says so.
4. Writes nothing else and touches no existing file.

Run it again at any time; it never overwrites a file that exists.

## Adapting `git-signals.sh`

Change the path filters in `retro.env`, then run the script once over the
last 14 days and check that every number looks believable before trusting
it in a report:

- `RETRO_TEST_PATHS`: your test directories.
- `RETRO_I18N_PATHS`: your translations, or empty to drop the row.
- `RETRO_MIGRATION_PATHS`: your migrations, or empty.
- `RETRO_SRC_PATHS`: your user-facing code, for the "most reopened
  surfaces" row.
- `RETRO_RULE_FILES`: the files whose size the scorecard tracks.

## Adapting the four prompts

In `agent-prompts.md`, fill in the repo name, the reviewer bot's login,
your log (a CHANGELOG, release notes, a journal table, an incident log, or
"none"), and your recurring routines. Keep the **read-only** sentence and
the **verified or inferred** sentence word for word. They are what keep the
subagents honest and harmless.

## Trimming the scorecard

Twelve good rows beat eighteen with six written "not measured" every time.
Keep the nine core rows in `scorecard.md` in any repo and add the rest as
you can compute them.

## Rebuilding from the original, in order

For someone porting this from the repo it was first built in:

1. Copy the folder.
2. Run `retro-init.sh`; fix the guessed paths.
3. Fill in the prompts.
4. Trim the scorecard.
5. Rewrite `sources.md` only if your team uses a different retro
   tradition. The sources cited apply to any software team.
6. Run it once by hand and treat the first report as the baseline. The
   first run finds more than later ones; handle its decisions one at a
   time.
7. Decide the cadence (two weeks) and how it starts (a person types
   `/retro`). Do not give it a scheduled self-wake-up.

## What the first run found in the repo this came from, as calibration

From about 87 commits, 57 PRs, 31 sessions and 74 log entries, in about
25 minutes of wall-clock time with each background pass making 20 to 120
tool calls:

- one live security gap: a reviewer finding nobody answered, still open in
  production;
- one structural blocker: nothing behind sign-in could be tested, because
  there were no test accounts;
- six process patterns, each with numbers;
- one written rule that failed on the day it merged.

That is what "working" looks like on a first run. Later runs should find
less, and what they find should be new.
