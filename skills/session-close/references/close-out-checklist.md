# The close-out checklist

Every row is a yes, a no with a reason, or "not applicable" with a reason.
Copy the table into the wrap-up with the answers filled in. A row answered
"will do in a follow-up" is a follow-up and goes in the handoff (see
`handoff-template.md`), not here.

> Written against a reference implementation: a web app on a hosted
> platform with per-branch preview builds, a CI gate set, database
> migrations, an analytics event catalog, translated copy, and a changelog
> the product owner reads. Rows that name one of those apply when the repo
> has it. Read the repo's instruction file (AGENTS.md, CLAUDE.md, the
> contributing guide) for its real names and commands.

## A. Nothing left on the floor

| # | Check | How |
|---|---|---|
| A1 | Working tree clean on every branch this session touched | `scripts/session-inventory.sh`; `git status` on each branch |
| A2 | No local branch holds commits that reached no PR | inventory section "Other local branches ahead" |
| A3 | Scratch files (recording specs, screenshots, scratch scripts) are out of the commit | inventory "Scratch files" |
| A4 | No secrets in any commit this session made | eyeball the diff for `.env*`, keys, tokens, private URLs |

## B. Every PR is in the done state

Per PR this session opened or pushed to:

| # | Check | How |
|---|---|---|
| B1 | Open, targets the default branch, not draft unless the owner asked for draft | the PR list for the head branch |
| B2 | CI green on the **current** head, every workflow that reports | the PR's checks |
| B3 | No merge conflict with the default branch | same call |
| B4 | Every open review thread answered | PR review threads |
| B5 | Preview link in the body, read from the deployment record, ready at the pushed commit | the platform's deployment list, matched by commit SHA; never a constructed URL |
| B6 | A before-and-after render in the body for any visual change the preview cannot show (motion, theme, a state that is hard to reach) | the repo's visual-QA guidance |
| B7 | The PR template's required sections answered truthfully (telemetry, migrations, verification, changelog) | read the body |
| B8 | Migrations applied, verified against the schema, and recorded wherever the repo records them | the repo's migration guidance |
| B9 | Changelog or journal entries filed for user-facing change | the repo's changelog guidance |
| B10 | The description still describes the PR as it is now (later pushes often change the shape) | re-read against the diff |

## C. The gates, run here, not just on CI

| # | Check | Command |
|---|---|---|
| C1 | The repo's full local gate command (the one CI runs) | from the instruction file or `package.json` / `Makefile` |
| C2 | Any gate the local command leaves out because it needs a base ref (new-test guards, copy-freshness checks) | run it with the base ref supplied by hand |
| C3 | Migration ledger or schema-diff state | the repo's own check |

## D. The whole body of work, QA'd as one thing

Each PR was checked alone. The user uses them together.

| # | Check | How |
|---|---|---|
| D1 | A code review of the **union** diff of the session's PRs against the default branch, by a fresh pair of eyes | a review command, or a subagent given only the diff and the acceptance criteria, with no write tools |
| D2 | The one flow the session changed most, walked end to end on the preview | a real browser, as a sample user |
| D3 | The surfaces the session touched, judged on a phone, in every theme, with reduced motion if motion changed | device emulation, both themes |
| D4 | Copy changed? Every language, and the repo's copy rules | the repo's translation workflow |
| D5 | Events fire for arrive, act, succeed, fail on anything new; failures reach the on-call signal | the repo's analytics contract |
| D6 | A model call added or changed is named, traced, and costed | the repo's AI telemetry rules |
| D7 | Production's own error signal read since the first merge this session | the error tracker |
| D8 | Anything the PRs claimed as verified was actually run, not described | re-read each PR's verification section against what you ran |

## E. The docs say what shipped

| # | Check | Where |
|---|---|---|
| E1 | The plan doc the session worked from has a "what actually shipped" note per phase, including every departure from the plan | the plan |
| E2 | Comments in code that say "not yet", "later phase", "when X ships" are true today | inventory "Deferral markers"; also grep the files touched for older ones now stale |
| E3 | The user-model or product-definition doc updated if what a feature is for, or who it is for, moved | the repo's user doc |
| E4 | Runbooks, journey maps, architecture references, README sections that describe a surface or flow this session changed | docs |
| E5 | A skill or rule this session followed gave wrong or missing instructions? Fix it in this PR | the skill or rule file |
| E6 | A durable lesson recorded where the team keeps lessons | changelog, journal, or decision log |

## F. Loose ends have a home

| # | Check | Where |
|---|---|---|
| F1 | Every deferral, every dependency on a person or a date, every out-of-scope discovery is in exactly one of: done now, the handoff doc, or dropped with a reason | `handoff-template.md` |
| F2 | Anything that depends on a service or credential this session lacked is named as not verified, never reported as verified | wrap-up "Not verified" |
| F3 | A follow-up session is needed? The handoff doc exists, is committed, and the wrap-up points at it | `docs/plans/<scope>-closeout-prompt.md` or the repo's equivalent |
| F4 | A critical or production-live finding was surfaced to the owner at once, not left for the handoff | wrap-up, top |

## G. Learnings are placed, not just listed

| # | Check | Where |
|---|---|---|
| G1 | Every correction the owner made this session is on a rung of the fix ladder | `learning-capture.md` |
| G2 | Every gate that went red is traced to a real defect fixed, or a gap in the gate fixed in the open (never with an allowlist) | |
| G3 | Every rule that was broken this session is moved up a rung or has a proposed mechanism | `learning-capture.md` |
| G4 | Rules this session is allowed to apply are applied, in the file that owns the subject; new checks and contract changes are handed to the owner as a decision | `learning-capture.md` "Who applies what" |

## H. Nothing is left running

| # | Check |
|---|---|
| H1 | No scheduled wake-up, loop, or PR subscription is armed unless the owner asked for one |
| H2 | No background agent or workflow is still running with work the wrap-up does not mention |
