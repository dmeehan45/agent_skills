---
name: handoff-audit
description: >-
  Comprehensive codebase handoff audit, run as a senior staff engineer
  preparing a prototype for handoff to a maintained dev team. Use when
  asked for a handoff audit, full codebase
  audit, dead-code or unused-code sweep, cleanup-opportunity review,
  tech-debt assessment, production-readiness review, maintainability
  review, or "what breaks at a million users". It censuses the repo,
  gathers tool-backed evidence in parallel, adversarially verifies every
  cleanup claim against this repo's known false-positive traps, and
  produces a structured, evidence-graded report checked into
  docs/production-readiness/. It never deletes or modifies product code —
  report first, cleanup only after the maintainer approves specific items.
  Not for reviewing a single diff (/code-review), a single surface
  (adversarial-review), or security-only review (/security-review). For
  the recurring biweekly maintenance cycle that consumes this report,
  works the tech-debt register, and executes one bounded improvement per
  run, use readiness-loop.
---

# Codebase handoff audit

This skill prepares the prototype for handoff to a professional dev team. It
answers four questions with evidence: what can be safely removed or
simplified, what is misleading or undocumented, what must be hardened before
production, and what breaks on the road to one million users. The deliverable
is a report, not a diff. Cleanup happens later, item by item, after the
maintainer approves.

> Written against a reference implementation — a TypeScript React/Vite SPA with filesystem-routed Vercel serverless functions, a Supabase Postgres database with an append-only migration ledger, contract tests that grep source, scheduled cron jobs, and a PostHog analytics catalog. The file paths, table names, environment variables, command names, and sibling-doc references below are examples from that implementation — map them to the equivalents in your own codebase.

The failure mode this method prevents: an auditor eyeballs the repo, calls
things "unused" from a single missing import, and the cleanup PR breaks a
Vercel cron, a contract test that greps the source, or a PostHog dashboard.
Every claim here is built from a census, at least two independent signals,
and a refutation attempt before it reaches the report.

## 0. The rules (non-negotiable)

- **Read-only on product code.** The only files this skill writes are the
  report (and its scratchpad). No deletions, no refactors, no "cleanup while
  I'm here" — even for items graded Confirmed.
- **Every claim cites evidence**: file paths, the command or agent that
  produced the signal, and the signals by type (see rubric in
  `references/scan-playbook.md`). No evidence, no claim.
- **Two-signal rule.** Nothing is called unused, dead, or safe to remove on
  one signal. It takes two *independent* signal types (e.g. static import
  graph + grep for string/dynamic references), and it must survive the
  false-positive trap table (section 4) before it lands in
  "Safe cleanup candidates".
- **Distinguish findings from guesses.** Confirmed / Probable / Speculative,
  per the rubric. Speculative items never appear as cleanup candidates —
  they go to "Needs Human Confirmation" or are dropped.
- **Product decisions are not engineering decisions.** Anything that depends
  on product intent, roadmap, user-facing behavior, security posture, or
  ownership goes to "Needs Human Confirmation" with a specific question,
  the options, and a recommended default.
- **No rewrites where targeted cleanup is safer.** Recommend the smallest
  intervention that reduces maintenance burden. A rewrite recommendation
  requires demonstrated production, security, or maintainability risk.
- **AGENTS.md still applies**: work on a feature branch, never touch `main`,
  never merge, surface the branch preview URL after pushing the report, and
  close with the teaching notes (1–3 concepts).

## 1. Phase A — Census (mechanical, no judgment)

Build the inventory before forming any opinion. Save each list to the
scratchpad; the report's coverage statement comes from this census. Exact
commands live in `references/scan-playbook.md` §1.

Inventory at minimum: all tracked files by area; the SPA route table
(`src/routes/`, `src/App.tsx`) and the server route table (every file under
`api/` — Vercel filesystem-routes them — plus `vercel.json` rewrites and
crons); `package.json` scripts, dependencies, and everything that references
`scripts/*` (package scripts, `.github/workflows/*`, docs and qa
procedures); env-var references (`process.env.`, `import.meta.env.`);
the analytics catalog (`src/lib/analytics/events.ts`); the migration ledger
(`supabase/migrations/.applied` vs the directory); the test census
(`tests/*.test.mjs`, `tests/mobile/`, Playwright configs); and the docs
census (`docs/`, `qa/`, `README.md`, `AGENTS.md`/`CLAUDE.md`).

If a previous `docs/production-readiness/handoff-audit-*.md` exists, this is
an **incremental audit**: diff against it, mark each prior finding
resolved / open / regressed, and spend the effort on what changed.

## 2. Phase B — Evidence sweep (tool-backed, fan out)

Two kinds of evidence, gathered in parallel:

**Mechanical signals** (run these yourself; details in playbook §2):
gates (`npm run typecheck`, `npm run lint`, `npm test`, `npm audit`,
`bash scripts/check-migrations.sh`); static analyzers (`npx knip`,
`npx depcheck`, `npx ts-prune`, `npx madge --circular` — all advisory
inputs, never verdicts); grep sweeps (TODO/FIXME/HACK, `console.log`,
commented-out blocks, mock/placeholder/demo markers, hardcoded URLs and
magic values). Never print secret values while sweeping; report the file
path and shape only.

**Domain readers** (fan out): one reader per report bucket — dead code,
duplication, prototype scaffolding, documentation, architecture,
build/deploy/ops, production gaps, scalability. Launch them as parallel
Explore agents with the bucket briefs in playbook §3; every reader returns
findings in the structured shape `{area, finding, evidence[], confidence,
removal_risk, recommended_action, validation_step}`. For a full audit of
the whole repo, orchestrate the fan-out and the verification pass below as
a Workflow (finder → adversarial-verifier pipeline; invoking this skill is
the opt-in); for a scoped audit, a handful of parallel Explore agents is
enough.

## 3. Phase C — Adversarial verification

Every finding bound for "Safe cleanup candidates" gets a refutation attempt
before it is written down: a separate check (or verifier agent, prompted to
*refute*, not confirm) that walks the trap table below and hunts for the
reference the finder missed — string-based imports, filesystem routing,
CI/docs references, test greps, runtime config. A finding that survives is
Confirmed; a finding refuted is dropped or rewritten; a finding with
surviving doubt is downgraded to Probable and moved to
"Cleanup candidates requiring confirmation". Do the same skeptical pass on
scalability claims: a bottleneck assertion needs a mechanism (which query,
which limit, which cost line), not vibes.

## 4. Repo ground truths — the false-positive traps

These are the reasons naive scanning lies in this repo. Check every cleanup
claim against each one (full table with commands in playbook §4):

1. **`api/` is filesystem-routed.** Vercel serves every file under `api/`
   as an endpoint. Zero imports ≠ unused: check `vercel.json` rewrites
   (short aliases like `/api/gd` → `/api/admin/guidance`), crons
   (`api/cron/*` run on schedules), and client `fetch` calls by URL string.
2. **Contract tests grep the source.** Many `tests/*.contract.test.mjs`
   assert on source text. "Unused" strings, names, or files may be
   load-bearing for the gates.
3. **`scripts/` is referenced from four places**: `package.json` scripts
   (including `postbuild` prerender), `.github/workflows/*`, docs runbooks
   (e.g. quarterly `scripts/posthog-audit.mjs` in AGENTS.md), and qa/
   procedures. Check all four before calling a script orphaned.
4. **Analytics event names are external contracts.** Entries in
   `ANALYTICS_EVENTS` may back saved PostHog dashboards/funnels/cohorts.
   Removal is never "safe" — it is always a confirmation item (AGENTS.md
   instrumentation rules).
5. **Migrations are append-only history.** `supabase/migrations/*.sql` and
   `.applied` are a ledger, never dead code. Audit them for *gaps*
   (unledgered, reused prefixes), never for deletion.
6. **Records are not stale docs.** `qa/*.md` dated reports, `docs/history/`,
   and `qa/ab-runs/` are point-in-time records. Flag genuinely misleading
   ones for an "archived" marker; do not recommend deletion.
7. **`.claude/` is operational tooling** (skills, hooks, settings), invoked
   by the agent harness, not imported by the app.
8. **Env vars live in Vercel, not the repo.** An env var with no repo
   default may still be set in the deployment. Absence of documentation is
   the finding; the fix is documenting, not removing.
9. **Dynamic and lazy references.** `React.lazy`, route config objects,
   string-keyed registries, and template-built URLs defeat import-graph
   tools. Grep for the basename/string before trusting knip or ts-prune.

## 5. Phase D — Report and hand off

Write the report using `references/report-template.md` — executive summary
then sections 1–9, with the per-item fields exactly as specified, the
confidence rubric applied, and scalability items tiered
(needed now / before serious launch / only when scale signals appear).

Deliver it as `docs/production-readiness/handoff-audit-YYYY-MM-DD.md` on
the working branch (never `main`), commit, push, and surface the branch
preview URL per the repo contract. In the chat wrap-up: lead with the
executive summary, state coverage honestly (what the census contained and
what was actually examined — no silent sampling), list the top "Needs Human
Confirmation" questions so the maintainer can answer inline, and close with the
teaching notes. Then stop. Cleanup execution is a separate, per-item,
explicitly approved follow-up — each approved item becomes its own small
branch/PR with the validation step from its report row.
