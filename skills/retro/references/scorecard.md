# The scorecard

The same rows every run, with the previous value beside each, so the second
retro can say "better" or "worse". A row you cannot compute says "not
measured" and why. Never a guess, never a blank.

Nine rows are **core** and belong in any repo. The rest are added when the
repo can compute them. Twelve honest rows beat eighteen with six blanks.

## Core rows

| # | Row | What it counts | How | Direction |
|---|---|---|---|---|
| 1 | **Surfaces reopened 3+ times** (rework) | Files under `RETRO_SRC_PATHS` changed by three or more distinct non-merge commits in the window | `git-signals.sh`, "reopened" section; then read the commits to tell iteration from rework | Lower |
| 2 | **Catch-up merges** (collisions) | Commits whose subject is a merge of the base branch into a feature branch | `git-signals.sh`, "catch-up merges" | Lower |
| 3 | **Commits with a failing check, by step** | Pushes whose CI went red, grouped by the step that failed | `pr-signals.sh` or the CI tool; the ledger's `checks_failed` as a second source | Lower, and the step mix matters more than the total |
| 4 | **Reviewer findings answered** | Of the review comments the bot or a person left, how many were answered (a reply, a fix commit, or a resolve with a reason) | Pass B reads each PR's review threads | Higher; 100% is the target |
| 5 | **Open PRs older than the cadence** | PRs open at the end of the window that were opened more than 14 days before it | `pr-signals.sh` | Lower |
| 6 | **Routines with no run** | Of the recurring routines in `RETRO_ROUTINES`, how many produced nothing in the window | Pass D checks each routine's output location | Zero |
| 7 | **Sessions blocked on a person** | Ledger entries with a non-empty `blocked_on_person`, and how many were answered before close | `ledger-summary.mjs` | Lower, and "unanswered at close" lower still |
| 8 | **Rule-file size** | Total lines across `RETRO_RULE_FILES`, now and at the start of the window | `git-signals.sh`, "rule files" | Flat or shrinking while other rows improve |
| 9 | **Rules broken in the window** | Written rules that a commit, PR or session visibly broke | Pass D cross-checks instruction files against git, PRs and the ledger's `rules_broken` | Lower; each one is a candidate to move up the ladder |

## Added rows, when the repo can compute them

| # | Row | What it counts | How |
|---|---|---|---|
| 10 | **Repeated corrections** | Distinct corrections in the ledger that appear in two or more sessions, and the top three | `ledger-summary.mjs` |
| 11 | **Automated turns** | Turns from scheduled wake-ups or events, as a share of all turns; and how many found work to do | `ledger-summary.mjs` (`turns.automated`); pass C reads a sample |
| 12 | **Sessions by outcome** | merged / pr-open / pushed-no-pr / local-only / abandoned / question-only | `ledger-summary.mjs` |
| 13 | **Ledger coverage** | Sessions the ledger holds versus sessions git and PRs imply (distinct `claude/*`-style branches pushed, PR authors that are agents) | Compare `ledger-summary.mjs` to `git-signals.sh` branches |
| 14 | **Fix-on-fix chains** | Commits whose subject starts with fix, hotfix or revert and that touch a file changed by another fix in the window | `git-signals.sh` |
| 15 | **Commits with no reason** | Non-merge commits whose body is empty or one line | `git-signals.sh`, "body quality" |
| 16 | **Definition-of-done gap** | PRs missing a section the template requires (telemetry, verification steps, a preview link, a changelog entry) | Pass B reads PR bodies against the template |
| 17 | **Learned entries acted on** | Of the log's "learned" entries in the previous window, how many produced a check, skill or rule | Pass D |
| 18 | **Time to merge, median** | Open to merge, for PRs merged in the window | `pr-signals.sh` |

## Reading the scorecard

- **A number alone is not a finding.** Row 1 at 12 might be a surface under
  deliberate iteration. Read the commits before calling it rework.
- **Direction over level.** The first run sets a baseline; the second says
  better or worse. Do not compare a row to another repo.
- **Three rows moving the wrong way together are one pattern.** Rework up,
  collisions up, catch-up merges up is parallel sessions on the same
  surface. Report it once.
- **Row 8 against the rest** is the test of the fix ladder. If the rule
  files grow and nothing else improves, the fixes are at the wrong rung.

## The baseline column

The first run fills "previous" with "baseline" and nothing else. Trend
language ("improving", "worse") starts on the second run. Do not back-fill
a baseline from a window nobody measured at the time; the first honest
number is better than a reconstructed one.
