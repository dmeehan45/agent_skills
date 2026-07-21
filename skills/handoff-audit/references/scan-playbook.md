# Scan playbook — commands, briefs, traps, rubric

Companion to `../SKILL.md`. Everything here is evidence-gathering; judgment
happens in the verification pass and the report.

## 1. Census commands (Phase A)

Run from the repo root; save outputs to the scratchpad for the coverage
statement.

```bash
# File census by area
git ls-files | awk -F/ '{print $1}' | sort | uniq -c | sort -rn

# Server route table: every api/ file IS an endpoint (Vercel filesystem routing)
git ls-files 'api/**/*.ts' | grep -v '_lib'
# ...plus aliases and schedules that reference them
cat vercel.json          # rewrites, crons, functions (maxDuration), headers

# SPA route table
grep -rn 'path[:=]' src/routes/ src/App.tsx | head -80
grep -rn 'React.lazy\|lazy(' src/ --include='*.tsx' -l

# scripts/ reference census — all four reference sources
ls scripts/
grep -n 'scripts/' package.json .github/workflows/*.yml
grep -rln 'scripts/' docs/ qa/ AGENTS.md CLAUDE.md

# Dependency census
node -e "const p=require('./package.json');console.log(Object.keys(p.dependencies).join('\n'),'\n--dev--\n',Object.keys(p.devDependencies).join('\n'))"

# Env-var reference census (report names only — never values)
grep -rhoE 'process\.env\.[A-Z0-9_]+' api/ src/ scripts/ | sort -u
grep -rhoE 'import\.meta\.env\.[A-Z0-9_]+' src/ | sort -u

# Analytics catalog and its tripwire
sed -n '1,50p' src/lib/analytics/events.ts
node --test tests/phase4.contract.test.mjs

# Migration ledger integrity (gaps, not deletions)
bash scripts/check-migrations.sh
diff <(ls supabase/migrations/*.sql | xargs -n1 basename | sort) <(grep -vE '^\s*(#|$)' supabase/migrations/.applied | sort)

# Test census
ls tests/*.test.mjs | wc -l && ls tests/mobile/ 2>/dev/null

# Prior audit? If yes, run in incremental mode.
ls docs/production-readiness/handoff-audit-*.md 2>/dev/null

# Churn signal: recently-touched vs fossilized files
git log --since='3 months ago' --name-only --pretty=format: | sort | uniq -c | sort -rn | head -40
```

## 2. Mechanical evidence sweep (Phase B)

**Gates first** — a failing gate is itself a finding for section 5 of the
report:

```bash
npm run typecheck
npm run lint
npm test
npm audit --omit=dev
bash scripts/check-migrations.sh
```

**Static analyzers** — advisory inputs only; each output line is a
*candidate* that still needs a second signal and the trap-table pass:

```bash
npx knip            # unused files, exports, deps (reads vite/ts config)
npx depcheck        # unused deps, cross-check knip
npx ts-prune -p tsconfig.app.json   # unused exports
npx madge --circular --extensions ts,tsx src/   # dependency cycles
```

If `npx` cannot fetch (offline env), fall back to manual reachability:
walk imports from the entrypoints (`src/main.tsx`, every `api/**/*.ts`
non-`_lib` file, `scripts/*` referenced in §1) and diff against the file
census.

**Grep sweeps** — prototype-scaffolding markers:

```bash
grep -rn 'TODO\|FIXME\|HACK\|XXX' src/ api/ scripts/ --include='*.ts' --include='*.tsx' --include='*.mjs'
grep -rn 'console\.log' src/ api/ --include='*.ts' --include='*.tsx' | grep -v test
grep -rniE 'mock|placeholder|lorem|dummy|fake[A-Z_]|demo[A-Z_]' src/ api/ --include='*.ts' --include='*.tsx'
grep -rnE 'https?://(localhost|127\.0\.0\.1)' src/ api/
# Secret-shaped strings: report the file:line and the shape ("sk_-prefixed
# string in X"), NEVER the value. Suspected committed secrets → warn and
# recommend rotation + history remediation per AGENTS.md; do not print them.
grep -rnE '(sk_live|sk_test|phx_|eyJ[A-Za-z0-9])' --include='*.ts' --include='*.tsx' --include='*.mjs' -l src/ api/ scripts/
```

## 3. Domain reader briefs (fan-out)

One reader per report bucket. Give each: (a) its brief below, (b) the
relevant census lists, (c) the trap table (§4), and (d) the required
finding shape:

```
{ area, finding, evidence: [{signal_type, detail}], confidence,
  removal_risk, recommended_action, validation_step }
```

Signal types: `import-graph`, `grep-string`, `runtime-registration`
(vercel.json / crons / package scripts / CI), `git-history`,
`test-reference`, `docs-reference`, `analytics-usage`, `gate-output`.

- **Dead code**: unused files, components, exports, routes, handlers,
  flags, styles, assets, deps, env vars, config. Start from analyzer
  output; demand a second signal type per item; run every item through §4.
- **Duplication & complexity**: repeated logic, copy-pasted components,
  inconsistent abstractions for the same job, deep nesting, needless
  indirection, unclear naming. Cite both/all sites; propose the *smallest*
  consolidation; flag behavior-change risk explicitly.
- **Prototype scaffolding**: grep-sweep hits in context — mock data,
  placeholder flows, TODOs, console logs, hardcoded values, fake states,
  demo-only logic, commented-out blocks, half-implemented features.
  Separate "delete" from "finish" from "productionize".
- **Documentation**: every file in `docs/` and root docs vs the actual
  code. Classify: accurate / outdated / misleading / duplicated /
  missing. Check README setup steps actually work against `package.json`.
  Remember trap 6: dated qa/ and history docs are records. Identify what a
  new team needs on day one that does not exist.
- **Architecture & maintainability**: module boundaries (`src/lib`,
  `src/features`, `src/components`, `api/_lib`), state management,
  API-boundary consistency across `api/` handlers, error handling and
  logging patterns, config sprawl, test structure. Highest-leverage
  simplifications that do not change behavior.
- **Build / deploy / ops**: package scripts, `.github/workflows/*` (what
  is blocking vs advisory; is `migration-check` a required check?),
  Vercel config (function durations, crons, headers/CSP), env-var
  handling and secrets hygiene, migrations process, seed data, release
  process, rollback story.
- **Production gaps**: reliability, observability (what exists:
  PostHog + `captureServer`, turn metrics; what is missing: alerting,
  error tracking, uptime), testing coverage vs contract-test greps,
  security posture (auth boundaries, RLS, admin gating, rate limits,
  CSP), data privacy (PII discipline per AGENTS.md), backups/DR,
  incident response, ownership and onboarding.
- **Scalability to 1M users**: for each candidate bottleneck give the
  mechanism and the tier — **needed now** / **before serious launch** /
  **only when scale signals appear** — plus the signal that would trigger
  the investment. Look at: Supabase query patterns and indexes
  (`mcp__Supabase__get_advisors` for index/RLS advice), cron fan-out
  (some run every 1–2 min — what do they scan?), LLM/API cost per user,
  serverless duration ceilings in `vercel.json`, analytics event volume,
  rate limiting, file storage, auth load, bundle size. Do not
  over-engineer: an unindexed table with 10k rows is a note, not a P1.

## 4. False-positive trap table (verification pass)

For each cleanup candidate, run every applicable check. One hit = not a
"safe" candidate.

| # | Trap | Refutation check |
|---|------|------------------|
| 1 | `api/` filesystem routing | Is the file under `api/` (non-`_lib`)? Check `vercel.json` rewrites + crons, and `grep -rn "<url-path>" src/ api/` for fetch-by-string. |
| 2 | Contract tests grep source | `grep -rn "<name-or-string>" tests/` |
| 3 | scripts/ referenced elsewhere | `grep -n "<script>" package.json .github/workflows/*.yml; grep -rln "<script>" docs/ qa/ AGENTS.md CLAUDE.md` |
| 4 | Analytics names are external contracts | Is it in `ANALYTICS_EVENTS` or `ServerEvent`? → confirmation item, never safe-delete. `scripts/posthog-audit.mjs` is the deep check. |
| 5 | Migrations are a ledger | Under `supabase/migrations/`? → integrity finding only, never removal. |
| 6 | Records ≠ stale docs | Dated `qa/*.md`, `docs/history/`, `qa/ab-runs/`? → archive-marker at most. |
| 7 | `.claude/` harness tooling | Skills/hooks/settings are invoked by the agent harness, not imported. |
| 8 | Env vars set in Vercel | Cross-check against deployment env (or flag as "verify in Vercel dashboard") before calling a var unused. |
| 9 | Dynamic/lazy references | `grep -rn "<basename-without-ext>" src/ api/ scripts/ index.html vite.config.ts` catches lazy imports, registries, template URLs, prerender scripts. |

## 5. Confidence rubric

- **Confirmed** — ≥2 independent signal types agree AND the trap-table
  refutation pass found nothing. Eligible for "Safe cleanup candidates".
- **Probable** — solid evidence but one plausible unresolved doubt (e.g.
  an env var that may be set in Vercel). Goes to "Cleanup candidates
  requiring confirmation" with the specific doubt as the question.
- **Speculative** — single signal, or depends on product intent, roadmap,
  or ownership. Never a cleanup candidate: either a "Needs Human
  Confirmation" question worth asking, or dropped.

Risk-of-removal is graded separately (low / medium / high) by blast
radius: what breaks if the claim is wrong — a dev script, a build, a
production endpoint, a paying user's flow.

## 6. Coverage statement

The report must say what was and was not examined: census totals, files
actually read vs pattern-matched, buckets that were sampled rather than
swept, analyzers that failed to run. Silent sampling that reads as full
coverage is the audit equivalent of a flaky green test.
