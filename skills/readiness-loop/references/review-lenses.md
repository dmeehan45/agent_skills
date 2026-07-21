# Review lenses for the readiness loop

Load this at Inspect (SKILL.md §2b) and Correlate (§3). These are
prompts for attention, not a form to fill in — a cycle reports what it
actually found in the areas it actually read, and says which lenses it
applied where. Items marked ⚑ are known past findings in this repo
(from `docs/production-readiness/handoff-audit-2026-07-07.md` and its
addenda): verify their *current* state instead of rediscovering them,
and treat their pattern as a class to hunt for elsewhere.

## 1. Correctness and data integrity

- Swallowed failures: `catch` blocks that log nothing or return success
  anyway. ⚑ Class exemplar: the Stripe webhook returning 200 on
  processing errors, silently stranding a paying user — hunt this
  pattern in any handler that acks before durably completing work.
- Fallbacks that conceal rather than recover. ⚑ Class exemplar: LLM
  routes serving deterministic mock replies with HTTP 200 when the
  gateway key is missing, bypassing quota and safety. Any "default
  value on failure" deserves the question: who notices when this fires?
- Async operations not awaited, or awaited without a failure path;
  retries that aren't idempotent. Payments, webhooks, crons, email
  dispatch, and TTS/LLM spend paths must tolerate duplicate delivery
  and partial failure — check for idempotency keys, upserts vs inserts,
  and dead-letter/retry design.
- State that can diverge across client, server, and database; partial
  writes with no transaction or reconciliation job.
- Validation at boundaries: API handlers parsing request bodies without
  zod (the house pattern), DB writes trusting client-shaped data, model
  outputs trusted without shape checks.
- Business rules duplicated in more than one place, quietly diverging.
- Critical behavior with no test. The contract-test suite is large;
  the question is coverage of *consequences* (quota enforcement,
  entitlement checks, safety gates), not file count.

## 2. Security and privacy

Weight this lens above aesthetics, always.

- Authentication vs authorization: which routes check *who* you are but
  not *what* you own. Row-level security and data-ownership checks on
  every user-data table touched by new code.
- The admin seam: ⚑ the cached fail-closed admin gate and constant-time
  cron-secret comparison are deliberate designs — new `api/admin/*` or
  `api/cron/*` files must adopt them (a contract test enforces the cron
  gate; confirm it still does).
- Service-role usage: where the service key is used, is the query
  scoped by user id from a *verified* token, not from the request body?
- Secrets: never in the repo, never printed, never in findings. ⚑ Env
  vars live in Vercel, not the repo — absence of documentation is the
  finding; the fix is documenting the *name and purpose*, never the
  value.
- Sensitive data in logs, traces, analytics, prompts. House PII
  discipline: payloads never include conversation content, message
  text, or child names. ⚑ LLM tracing is content-excluded by
  design (`recordInputs`/`recordOutputs` hard false) — any change near
  telemetry must keep it that way.
- Spend-bearing and abuse-prone endpoints: rate limits present and
  fail-closed. ⚑ TTS was the unprotected spend path once; new
  endpoints that call paid vendors get the same token-bucket treatment.
- Prompt injection and AI tool authorization: tools reachable from a
  conversation must enforce the same ownership checks as the API —
  the model is a confused deputy waiting to happen.
- Dependency risk: `npm audit --omit=dev --audit-level=high` is the
  gate; low/moderate transitive advisories are register material, not
  cycle-stoppers.

## 3. Maintainability

The cost that matters is bugs, change risk, unclear ownership, or slow
diagnosis — name it, or the finding is a style preference.

- Files with unrelated responsibilities that force wide diffs for
  narrow changes; UI components doing database or infrastructure work
  directly.
- Competing patterns for the same operation — but verify intent first:
  ⚑ the divergent fetch wrappers and config read-planes were audited
  and are *deliberate*; consolidation was explicitly rejected. Check
  `decisions/` and prior audits before calling divergence accidental.
- Helpers hiding important side effects; business rules embedded in
  interface code; hard-coded prompts, IDs, URLs, model names, flags.
  ⚑ Wrong-domain fallback URLs were a real production hazard of this
  class.
- Types that vanish at boundaries (`as any` at the API seam, untyped
  JSON columns). ⚑ Files excluded from typecheck are a standing
  register item — do not let the list grow silently.
- Dead code: apply handoff-audit's two-signal rule and trap table
  (`.claude/skills/handoff-audit/SKILL.md` §4) before writing the
  word "unused". ⚑ knip without `knip.json` is unusable here; contract
  tests pin source text; `api/` is filesystem-routed.
- Comments and docs describing old behavior. ⚑ The README/product-name
  drift class: docs that misname or misdescribe the deployed product
  are P2 onboarding hazards, not cosmetics.

## 4. Operational readiness

- Can failures be seen? ⚑ Standing gaps at last audit: no error
  tracker (Sentry planned, not installed), no alerting (a dead cron
  pages no one), Vercel log retention ~1 day. Verify current state
  each cycle; these decay invisibly.
- Are background jobs observable and retryable? `cron_run` rows exist —
  who reads them, and would a silent stop be noticed?
- Deployment visibility: are build failures and runtime errors on the
  path someone actually looks at? ⚑ Lighthouse-nightly failures were
  double-suppressed — CI that cannot fail anyone is decoration.
- Rollback: is there a documented path, and does it warn that
  migrations do not roll back with code? Are migrations repeatable and
  ledgered (`scripts/check-migrations.sh`)?
- Environment separation: can staging/preview be told from production
  safely (keys, data, feature flags)? ⚑ Node-version drift between CI
  and Vercel is the exemplar config-plane divergence.
- Third-party outage behavior: Supabase, Stripe, the LLM gateway,
  ElevenLabs, Resend — for each, what does the user see and what does
  the operator see when it's down? "Fails closed and quietly" is only
  half-right.
- Backups and retention: ⚑ Supabase backups were OFF at last audit —
  an owner-side setting; verify and keep on the register until
  confirmed on with a documented restore procedure.

## 5. Developer experience and onboarding

- Clean clone → install → run → green tests, using only committed docs,
  on the CI-pinned Node version. Time-to-first-successful-change is the
  metric; every undocumented step you had to intuit is a finding.
- Are required env var *names* documented with purpose and where to get
  a dev-safe value (`.env.example` completeness vs actual
  `process.env.`/`import.meta.env.` references)?
- Does CI run what developers are told to run locally, and nothing
  secretly different? (Gates workflow skips docs-only changes; mobile
  CI has its own config — say so in onboarding docs.)
- Could a new developer find where a given user-visible behavior lives
  in under ten minutes using `SYSTEM_MAP.md`? Spot-check it against
  reality each cycle — a wrong map is worse than no map. ⚑ The
  primary walkthrough doc once failed 8 of 13 spot-checks; truthfulness
  beats completeness.
- Bus factor: which knowledge exists only in David's head or in chat
  history? Each cycle should move at least one such fact into the
  shelf — that is often the cheapest high-value "change".

## 6. Runtime-signal questions (Correlate stage)

For each candidate signal from Supabase / Vercel / PostHog / Langfuse /
feedback queues / CI / qa reports:

1. How frequent, and how many users or sessions?
2. Does it touch a flow in `CRITICAL_USER_FLOWS.md`?
3. First seen / last seen — new, worsening, or stable?
4. Reproducible? With what steps or trace id (never paste content)?
5. Which code path is implicated, with what confidence?
6. Root-cause class: application logic · data/database ·
   infrastructure · external integration · auth/permissions · UX
   confusion · model behavior · prompt/tool behavior ·
   instrumentation gap · unknown.
7. Is instrumentation sufficient to distinguish those classes? If not,
   the smallest decisive instrumentation is a candidate action.
8. What evidence would confirm a fix actually worked?

Signals with no implicated code path produce register items or
instrumentation actions — not code changes.
