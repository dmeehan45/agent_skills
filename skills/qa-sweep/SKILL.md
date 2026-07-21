---
name: qa-sweep
description: >-
  Run a scoped QA sweep of the product and file the findings as a dated
  report in qa/, in the house format (prioritized triage table, evidence,
  carry-forwards). Use when asked to "run the daily sweep", "do a QA pass on
  <surface>", after a burst of merges to main, before flipping a feature flag
  on for everyone, or when the qa/ directory has gone quiet for a while and
  David wants a fresh read on product health. Scopes: daily (full-product
  diff-driven sweep since the last baseline), surface (one area: admin,
  onboarding, landing, mobile), or visual (screenshot tiles + axe/WCAG via
  the sweep scripts). It runs the automated gates for real, reads the diff
  window since the last sweep, checks each bucket including the AGENTS.md
  analytics-and-instrumentation checks, and files findings as P0-P3 with
  file:line evidence — it does NOT fix them; fixes are separate approved
  changes. Not for reviewing a single diff (/code-review), not for
  security-only review (/security-review), not for strategy on one surface
  (adversarial-review), and not the deep handoff audit (handoff-audit).
  Repo: dmeehan45/satsang-dev.
---

# QA sweep (Satsang / Avani)

A sweep answers one question with evidence: *what broke or drifted since we
last looked?* Its output is a report in `qa/` that a future sweep can diff
against — same buckets, same priority scale, carry-forwards tracked until
resolved. The discipline that makes reports comparable across months matters
more than any single finding.

**When to invoke.** "Daily sweep" / "QA pass"; after a merge burst; before a
flag flips on for everyone; pre-release; any time the latest `qa/daily-*.md`
is stale enough that its baseline no longer describes the product.

## 1. Establish the diff window (this is what makes it a sweep, not a wander)

1. Find the previous report: latest `qa/daily-YYYY-MM-DD.md` (or the relevant
   surface report). Note its baseline commit — reports pin it in the Summary.
2. Window: `git log --oneline <baseline>..origin/main`, plus
   `git diff --stat <baseline>..origin/main`. Record PR range, files changed,
   and new migrations (`git diff --name-only ... -- supabase/migrations/`).
3. Summarize the major surfaces changed in the window, like the house reports
   do — this section is what tells the *next* sweep where to look.
4. Import the previous report's open findings as carry-forwards. Every one is
   either re-verified still-open, or moved to "Resolved this window" with the
   resolving commit/PR. Carry-forwards never silently vanish.

## 2. Run the automated gates (for real, report honestly)

- `npm run lint` · `npm run typecheck` · `npm test` (the full contract
  suite) · `npm audit --omit=dev` · `bash scripts/check-migrations.sh`.
- `npm run test:mobile` — known env caveat: Playwright browser binaries may
  be absent in a remote container; distinguish "binary missing, not a code
  regression" (a P3 env note, per precedent in the 2026-06-05 report) from a
  real failure.
- `npm run build` — watch the chunk-size output; bundle regressions are
  standing findings (the eager i18n catalog import was a P1 caught exactly
  this way).
- Supabase health: `mcp__Supabase__get_advisors` (security + performance)
  and, when crons changed, `mcp__Supabase__get_logs` for the affected
  functions.
- Paste real outputs (trimmed) into the Evidence section. A gate you did not
  run is listed as NOT RUN with a reason — never inferred green.

## 3. Sweep the buckets

Work the house buckets (the letters in recent reports run A–I; keep the
previous report's lettering so diffs line up):
Frontend/Visual · Conversational Runtime · Backend & Data · Auth &
Onboarding · Billing & Entitlement · AI Safety & Cost · Cron & Background ·
Admin · Memory & Cost Telemetry.

Per bucket: read what changed in the window, exercise the risky paths, and
write findings — not narrative. A finding = priority + status + bucket +
`file:line` + one-paragraph note with the failure scenario. Priorities:
**P0** ship-stopper/data-loss/safety, **P1** user-visible break or serious
regression, **P2** real defect with a workaround or bounded blast radius,
**P3** minor/DX/env.

**Analytics & Instrumentation checks (required by AGENTS.md in every daily
report — it names this "Bucket E"; recent reports already use E for Billing,
so append it under the next free letter and note the AGENTS.md name):**

1. Catalog vs. code: `node --test tests/phase4.contract.test.mjs` — both the
   registered-name and ServerEvent-union tests pass. PASS/FAIL.
2. New events since last sweep (diff `src/lib/analytics/events.ts`): each
   registered in a PostHog insight/funnel/cohort per its PR, or flagged P3
   "instrumented but not measured".
3. Removed/renamed events since last sweep: cross-check saved PostHog
   objects; a dashboard referencing a deleted name is a P2.
4. Suppressed surfaces: `git grep "trackEvent(" src/pages/admin
   src/routes/AdminRoutes.tsx src/components/admin` → zero matches.
5. Server-side capture wired from `api/billing.ts`, `api/cron/*.ts`,
   `api/user/request-deletion.ts`, `src/lib/ai/safety/turnMetrics.ts`; any
   new state-mutating endpoint without capture is a P3.

**Visual scope.** `npm run qa:visual-sweep` (`scripts/visual-sweep.mjs`;
`SWEEP_URL` for a preview or localhost, `SWEEP_ROUTES=/,/about,...`,
`SWEEP_MAX_TILES`) captures iPhone 14 / Pixel 7 / 1440px tiles plus axe-core
WCAG A/AA per route into gitignored `.visual-sweep/<stamp>/`; inspect the
tiles yourself (alignment, contrast, overflow, both themes) —
`scripts/admin-visual-sweep.mjs` for admin. Tiles are throwaway; findings
worth keeping go in the report.

## 4. File the report

`qa/daily-YYYY-MM-DD.md` (or `qa/<surface>-YYYY-MM-DD.md`), matching the
house structure — read the most recent daily report first and mirror it:

1. **Summary** — one bolded status line: PASS / FAIL with the open P0/P1/P2
   counts, then the diff window (baseline SHA → HEAD SHA, PR range,
   migration count) and major surfaces changed.
2. **Triage** — the table: `Pri | Status | Bucket | File:line | Note`, open
   findings first, then "Resolved this window" with resolving commits.
3. **Automated Gates** — each gate, its real result, trimmed output.
4. **Bucket sections** — findings + what was checked and found clean (a
   clean bucket says what was exercised; "no findings" without evidence is
   not a cleared bucket).
5. **Evidence** — commands run and key outputs.
6. **Footer** — baseline for the next sweep (HEAD SHA, date).

## 5. Guardrails

- **Report, don't repair.** A sweep that quietly fixes what it finds
  destroys the record and skips approval. File findings; fixes are separate
  PRs on David's direction. (Exception: none. Even a one-line fix is a
  finding first.)
- Never mark a carry-forward resolved without naming the resolving change.
- Never soften a status: one open P1 makes the sweep FAIL, per house
  precedent.
- Priorities are about user/production impact, not effort to fix.
- Findings carry `file:line`, or name the command/screenshot that shows the
  problem. Unverifiable findings are questions, listed separately.
- Do not let the report leak secrets: no env values, tokens, connection
  strings, or user PII in evidence — redact before pasting.
- The report itself goes in `qa/` in the PR; `.visual-sweep/` output stays
  out of git.

## 6. Preflight before you hand back

- [ ] Baseline found; diff window stated (SHAs, PR range, migrations).
- [ ] Every carry-forward re-verified or resolved-with-evidence.
- [ ] All gates run and honestly reported (or NOT RUN + reason).
- [ ] Every bucket either has findings or says what was exercised.
- [ ] Analytics & Instrumentation checks all five run.
- [ ] Report filed in qa/ in house format; status line states PASS/FAIL and
      counts; footer pins the next baseline.
- [ ] Nothing fixed in product code; zero secrets/PII in the report.
