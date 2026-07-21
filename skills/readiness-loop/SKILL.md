---
name: readiness-loop
description: >-
  Recurring (~every 2 weeks) engineering-readiness loop for Satsang
  (dmeehan45/satsang-dev): re-baseline the gates, sweep what changed,
  correlate with runtime evidence, work the tech-debt register, execute
  at most ONE bounded low-risk improvement, and keep the living handoff
  docs in docs/engineering/ current — run as the senior engineer
  preparing this codebase for a real dev team to understand, run, change
  safely, and diagnose. Use when asked to "run the readiness loop", do
  the biweekly cleanup / handoff-prep / maintenance cycle, "get the
  codebase ready for a new developer", update or work down the tech-debt
  register, refresh SYSTEM_MAP / ENGINEERING_HEALTH / onboarding docs,
  or after an incident, before a big dependency or architecture change,
  or right before a developer onboards. Modes: AUDIT_ONLY /
  FIX_LOW_RISK / IMPLEMENT_APPROVED_ITEM. Not the deep one-shot census
  (handoff-audit — this loop consumes its report and keeps it alive),
  not product QA (qa-sweep), not single-diff review (/code-review,
  /security-review), not cost/latency work
  (conversational-ai-efficiency-audit), and never a license for a
  repo-wide "professionalization" refactor.
---

# Engineering-readiness loop (Satsang)

A future engineer does not need a pristine codebase. They need one they
can **understand, run, change safely, and diagnose when it breaks**.
Every cycle of this loop answers five questions with evidence — what
does this system do, where is it fragile, which problems affect real
users, what would make the next change safer, what does a new developer
need to know before touching it — and then does exactly three things:
refreshes the truth (gates + register + handoff docs), executes at most
one bounded improvement, and names the next one.

The failure mode this loop exists to prevent: an agent told to "improve
code quality" indiscriminately produces churn, speculative abstractions,
a giant professionalization branch nobody can review, and new bugs in
code that worked. Awkward-looking code that runs reliably is less urgent
than elegant-looking code that fails in production. When in doubt, the
bias is: smaller change, more evidence, better documentation.

## 0. Modes and standing rules

| Mode | When | May change product code? |
| --- | --- | --- |
| `AUDIT_ONLY` | First run ever, or any run David asks to keep read-only | No — findings + one *proposed* action only |
| `FIX_LOW_RISK` | Default for recurring runs, once David has reviewed the first report | One change inside the low-risk envelope (§5) |
| `IMPLEMENT_APPROVED_ITEM` | David names a specific register item | That item only, at whatever scope he approved |

If `docs/engineering/ENGINEERING_HEALTH.md` does not exist, this is the
first run: run `AUDIT_ONLY` and bootstrap the handoff shelf (§7). David
reviewing that first report is what turns on `FIX_LOW_RISK` for later
cycles — do not assume it.

Standing rules, every cycle, every mode:

- **Understand before changing.** If you cannot explain an area's
  architecture, you may not refactor it — record it in `SYSTEM_MAP.md`
  as not-yet-understood instead. That record is a finding, not a
  failure.
- **Every claim cites evidence**: file:line, the command and its real
  output, the runtime signal, or the reproduction. Distinguish
  Confirmed / Probable / Speculative (handoff-audit's rubric).
  Speculative items are questions, never actions.
- **Runtime evidence and user consequence outrank aesthetics.** Never
  recommend a code change when the evidence doesn't implicate the code.
- **Behavior-preserving by default.** User-facing behavior changes need
  explicit approval, full stop.
- **One bounded change per cycle.** The cycle's branch carries the
  shelf updates plus that one change, so the PR is reviewable as a
  unit; an `IMPLEMENT_APPROVED_ITEM` of medium or large scope gets its
  own branch instead. Never mix architectural moves, feature changes,
  dependency upgrades, and formatting in one patch.
- **AGENTS.md fully applies**: feature branch off `main`, never merge,
  stop-and-ask before >3 files / auth / schema / build tooling /
  env-config behavior / API contracts, surface the branch preview URL
  after pushing, close with teaching notes (1–3 concepts). Route gated
  work to its owning skill: schema → migration-lifecycle, events →
  analytics-instrument, user-facing copy → i18n-propagate, harness
  behavior → change-pass.
- **Secrets and PII discipline**: never print env values, tokens, or
  anything a parent typed — in findings, logs added, or docs.

## 1. Orient — the loop's memory (Stage 0)

This is what makes it a loop rather than a wander. Before inspecting
anything:

1. Read the latest cycle entry in
   `docs/engineering/ENGINEERING_HEALTH.md` — its baseline SHA, its
   "next cycle starting point", its open uncertainties.
2. Read `docs/engineering/TECH_DEBT_REGISTER.md`. Every open item is a
   carry-forward: this cycle re-verifies it still stands, resolves it
   with the resolving commit, or explicitly re-dates it. Carry-forwards
   never silently vanish (qa-sweep discipline).
3. Establish the diff window: `git log --oneline <last-baseline>..origin/main`
   and `git diff --stat`, noting merged PRs, new migrations, new
   `api/` files, dependency changes, and new analytics events.
4. Pull in what landed since last cycle: new `qa/*.md` reports, new
   `docs/production-readiness/*` audits or addenda, answered questions
   from the previous cycle's report.
5. Note which deep-dive area is next in the rotation (§2b).

If there is no handoff-audit report at all, or the newest one is badly
stale (~a quarter old with heavy churn since), say so and recommend
running handoff-audit first — this loop maintains a baseline; it does
not rebuild one from nothing.

## 2. Inspect (Stage 1)

### 2a. Verification baseline — run the gates for real

`npm run lint` · `npm run typecheck` · `npm test` ·
`npm audit --omit=dev --audit-level=high` ·
`bash scripts/check-migrations.sh` · `npm run build` (watch chunk-size
regressions) · `npm run test:mobile` (known caveat: Playwright binaries
may be absent in a remote container — that is an env note, not a
regression). Record each as PASS / FAIL with trimmed real output, or
NOT RUN with the reason. A gate you did not run is never inferred
green. A newly-red gate outranks everything else this cycle.

Also answer, each cycle: could a new developer go from clean clone to
running app and green tests using only committed docs? The distance
between "what the docs say" and "what you actually had to do" is a
finding.

### 2b. Scoped review — diff window + register + one deep dive

Do not re-census the repo every two weeks; that is handoff-audit's job.
Scope this cycle's reading to (1) the diff window, (2) areas implicated
by register items and runtime evidence, and (3) **one deep-dive area**
from this rotation, recorded in the cycle entry so coverage compounds
across cycles:

1. `api/` routes, crons, and webhook handlers
2. AI harness and safety pipeline (`src/lib/ai/`)
3. Auth, billing, and entitlement seams
4. Data layer: migrations, RLS, query patterns
5. Client app shell: routing, state, error boundaries
6. Build, CI, dependencies, and config/env surface
7. The test suite itself (what's pinned, what's flaky, what's missing)
8. Docs truthfulness (README, onboarding paths, runbooks vs reality)

Read through the five lenses in `references/review-lenses.md`
(correctness & data integrity, security & privacy, maintainability,
operational readiness, developer experience) — load that file when you
start this stage. Anything resembling a dead-code or "unused" claim
must pass handoff-audit's two-signal rule and false-positive trap table
(`.claude/skills/handoff-audit/SKILL.md` §4) before it is written down;
this repo punishes naive scanning (filesystem-routed `api/`, contract
tests that grep source, string-keyed registries).

## 3. Correlate with runtime evidence (Stage 2)

Code review says what *could* fail; runtime evidence says what *is*
failing. Consult, as available: Supabase advisors and logs
(`mcp__Supabase__get_advisors`, `get_logs`), Vercel runtime errors and
logs (Vercel MCP), PostHog product analytics (plus
`scripts/posthog-audit.mjs` quarterly), Langfuse traces for LLM
behavior/latency/tool failures (langfuse skill), the
`conversation_turn_metric` and `cron_run` tables, feedback queues
(`assistant_turn_feedback`, `conversation_feedback`,
`caretaker_feedback_item` — interpretation belongs to
process-feedback; read them here only as prioritization signal), CI
history, and `qa/` reports. A source you could not reach is recorded
NOT CHECKED — never fabricated.

For each meaningful signal ask: how frequent, how many users/sessions,
does it block a critical flow, new/worsening/stable, reproducible,
which code path, and — crucially — is current instrumentation even
sufficient to tell code from infrastructure from external service from
model behavior from UX confusion? When the answer is no, **the smallest
instrumentation that would decide it is itself a first-class candidate
action** for §5. The full question list is in
`references/review-lenses.md` §6.

## 4. Prioritize (Stage 3)

Classify every finding by consequence, not effort:

- **P0** — security exposure, privacy breach, data loss, broken access
  control, destructive behavior.
- **P1** — user-facing correctness or reliability failure in a critical
  flow (see `CRITICAL_USER_FLOWS.md`).
- **P2** — material developer risk: changes are unsafe to make,
  diagnosis is blind, onboarding is misleading, operational visibility
  is missing.
- **P3** — local maintainability, duplication, naming, cleanup.
- **Observation** — worth recording, not currently actionable.

A P0, or a P1 that is live in production, does not wait for the cycle
report — surface it to David immediately (it belongs in qa/ triage
too). Each finding carries: title, priority, evidence, affected
files/systems, consequence, confidence, recommended action, scope
(S/M/L), verification method, risk of changing, risk of leaving.
Keep **at most ten active recommendations**; everything else goes to
the register. The register is allowed to hold cheap P3s indefinitely —
that is its job, not a failure of the loop.

## 5. Change — one bounded action (Stage 4)

Choose the smallest action that most reduces risk. Prefer, roughly in
order: a focused test around critical untested behavior · missing
validation at a boundary · making a swallowed failure visible
(structured error context, an error boundary) · the smallest
instrumentation that decides an open question · making a dangerous
operation idempotent · removing a Confirmed-dead path (traps checked) ·
consolidating two *demonstrably conflicting* implementations ·
documenting a critical hidden assumption. A docs-only or test-only
cycle is a fully legitimate cycle — often the highest-value one.

The **low-risk envelope** for `FIX_LOW_RISK` — all five, or it's a
proposal, not a change: small and reversible · behavior-preserving ·
≤3 files and outside the AGENTS.md gated areas (auth, schema, build
tooling, env behavior, API contracts, dependency migrations) · covered
by an existing test or accompanied by a focused new one · verifiable by
the gates plus the affected flow. Never: repo-wide rewrites, new
frameworks or abstraction layers for hypothetical needs, mass renames,
mixed cosmetic-plus-functional patches, multi-dependency upgrades.

In `AUDIT_ONLY`, write the proposal (with two options and tradeoffs
when there's a real design choice, per AGENTS.md) and stop. In
`IMPLEMENT_APPROVED_ITEM`, do the named item and nothing adjacent —
"while I'm here" is how professionalization branches start.

## 6. Verify (Stage 5)

A change is not complete because it seems sensible. Re-run the gates
relevant to the change plus `npm run build`; exercise the affected
critical flow on the branch preview (preview-qa owns the handoff link);
then — reviewer must not be implementer — run `/code-review` on the
diff as an independent pass, and `/security-review` when the change
touches auth, PII, payments, storage, or AI tool surfaces. Treat their
findings as a colleague's review, not a formality. Report what was
verified and what was not, honestly: "tests pass but I could not
exercise the Stripe path" is a good sentence; silence about it is not.

## 7. Document — the handoff shelf (Stage 6)

The shelf lives in `docs/engineering/` (templates and per-file guidance
in `references/artifact-templates.md` — load it when bootstrapping or
when unsure what belongs where):

- `SYSTEM_MAP.md` — components, request/data flows, where auth is
  enforced, external dependencies, business-critical files, and what is
  intentionally unusual vs accidentally inconsistent.
- `DEVELOPER_ONBOARDING.md` — clean clone → running app → green tests →
  first safe change, as actually verified in §2a.
- `CRITICAL_USER_FLOWS.md` — the flows that must keep working, each
  with entry point, code path, and how to verify it.
- `TECH_DEBT_REGISTER.md` — the open findings, in the §4 record format.
- `ENGINEERING_HEALTH.md` — one compact entry per cycle, newest first:
  date, mode, SHA, gate results, register movement, signals reviewed,
  uncertainties, next starting point. This file is the loop's memory.
- `OBSERVABILITY_GUIDE.md` — where to look when something breaks, per
  symptom class.
- `decisions/` — one short ADR per decision with lasting consequences
  ("must not be casually reversed"), including decisions *not* to act.

Update only what this cycle touched, plus the health entry (always).
The most useful handoff docs are not exhaustive — they say where to
start, how the system is shaped, what is fragile, and which decisions
are deliberate. On first run, bootstrap the shelf by mining the latest
`docs/production-readiness/handoff-audit-*.md` (its findings seed the
register; its addenda record what already got fixed) rather than
re-deriving from scratch. Docs the shelf supersedes get a pointer, not
deletion — dated reports in `qa/` and `docs/` are records (trap 6).

## 8. Cycle wrap-up (required output, in this order)

1. **State of the system** — two or three sentences a hiring CTO could
   read, then the gate table (real results).
2. **Since last cycle** — diff window, register movement
   (new / resolved-with-commit / carried), regressions.
3. **Runtime evidence** — the consequential signals, each with
   frequency and blast radius; sources NOT CHECKED listed.
4. **Findings** — ≤10, ordered by consequence, in the §4 record format.
5. **The change** — what was made (diff summary + verification results,
   including what was *not* verified) or, in `AUDIT_ONLY`, the proposal
   with options and a recommendation.
6. **Docs updated** — which shelf files changed.
7. **Open questions for David** — specific, answerable inline.
8. **Next cycle's starting point** — one item, named precisely.

Plus, per the house contract: the branch preview URL (READY-confirmed)
near the top, and 1–3 teaching notes at the close.

## 9. Definition of done and cadence

A cycle is done when the system model is no less accurate than before,
every finding is evidenced, any change is bounded and independently
reviewed, verification results are recorded honestly, the shelf
reflects reality, and the next action is named. If a cycle finds
nothing worth changing, say so plainly — a short, honest cycle beats a
manufactured finding.

Cadence: every ~2 weeks during active development; also after an
incident or repeated production error, before changing a major
dependency or architecture boundary, and immediately before a
developer's first day — that last run should bias entirely toward
`DEVELOPER_ONBOARDING.md` and `SYSTEM_MAP.md` accuracy.
