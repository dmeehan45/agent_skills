---
name: analytics-instrument
description: >-
  Instrument a product change correctly against the analytics contract: the
  event catalog, the server union, the contract tests, the admin suppression
  rule, and the PII discipline. Use whenever a PR adds, removes, renames, or
  moves a user-facing surface or flow; whenever adding trackEvent /
  trackAdminAction / captureServer calls; when a new API endpoint mutates
  user state (does it need server-side capture?); when renaming or retiring
  an event; when writing the PR description's required events list; or when
  the phase4 analytics contract test is red. The single source of truth is
  ANALYTICS_EVENTS in src/lib/analytics/events.ts — every event name, client
  or server, is registered there, and tests/phase4.contract.test.mjs enforces
  the catalog in BOTH directions (unregistered call sites fail, and
  registered events with no call site fail as orphans). Not for choosing what
  to measure strategically (that is a product conversation), not for admin UX
  telemetry (deliberately unmeasured — the audit trail is admin_audit_log),
  and not for the AI harness's own eval metrics.
---

# Analytics instrumentation

The product's analytics are governed by one catalog and a pair of tripwires.
Instrumenting a change means making four seams agree: the call site, the
catalog, the server union (if server-fired), and the PR description. This
skill walks that, plus the two rules with no compiler behind them: admin
suppression and PII discipline.

> Written against a reference implementation — a TypeScript app with a single
> central analytics event catalog, PostHog client- and server-side capture, and
> contract tests that enforce the catalog in both directions. The file paths,
> event/table names, and command names below are examples from that
> implementation — map them to the equivalents in your own codebase.

**When to invoke.** Any PR touching a user-facing surface; any new
`trackEvent`/`captureServer` call; an event rename or removal; a new
state-mutating endpoint; a red `phase4.contract.test.mjs`; writing the PR
description's instrumentation section.

## 1. The mental model: one catalog, four firing paths

- **`src/lib/analytics/events.ts`** — `ANALYTICS_EVENTS`, an `as const` object
  mapping `event_name: 'surface-bucket'`. Ordered by lifecycle/surface with
  `// ---` group headers, deliberately not alphabetical, so diffs read like a
  feature changelog. Add new events inside the right group (or add a group).
  Client *and* server events register here — it answers "what does this
  product emit?" in one place. Reserved PostHog events (`$pageview` etc.) are
  never registered.
- **Client firing:** `trackEvent(name, payload)` in `src/lib/analytics.ts`,
  typed against `AnalyticsEventName` — an unregistered name is a typecheck
  failure before it is a test failure. Best-effort, never throws.
- **Admin exception:** `trackAdminAction(name, payload)` exists ONLY for
  admin actions that change public-facing state (a moderated post, a
  published voice post). It bypasses suppression and auto-tags
  `is_admin: true, surface: 'admin'`. It is never for admin UX telemetry.
- **Server firing:** `captureServer(distinctId, event, props)` in
  `src/lib/posthog-server.ts`, typed against the `ServerEvent` union there.
  (The header comment in `events.ts` points at `api/_lib/posthog-server.ts`;
  that path is stale — the module lives in `src/lib/`.) Wired today from
  `api/billing.ts` (Stripe webhook), `api/cron/*.ts`,
  `api/user/request-deletion.ts`, and
  `src/lib/ai/safety/turnMetrics.ts`.
- **Suppression:** `shouldCapture` in `src/lib/posthog.ts` returns false for
  any `/admin` path, so admin usage never contaminates product analytics.
  The audit trail for admin actions is the `admin_audit_log` table (written
  via `auditWrite` in the api layer), not PostHog.

## 2. The tripwires (know them before you edit)

`tests/phase4.contract.test.mjs` enforces, among page-level pins:

1. **Forward:** every `trackEvent('name'…)` in `src/` uses a registered
   catalog name (typecheck catches most; the grep catches interpolation).
2. **Reverse (the one that surprises):** every registered catalog name must
   appear as a quoted string literal in at least one `.ts/.tsx` under `src/`
   *other than* `events.ts` itself. Register an event with no call site and
   the suite fails with an orphan list. So you cannot "pre-register" events
   for a future PR, and removal must delete both catalog entry and call
   sites together.
3. **Server:** every `captureServer(…, 'name')` literal across `api/` and
   `turnMetrics.ts` must be in the `ServerEvent` union. A server event
   therefore lands in **two** files: the union *and* the catalog.

## 3. Adding an event

1. Name it `snake_case`, past-tense verb where natural
   (`paywall_dismissed`, `onboarding_tour_completed`), consistent with its
   surface's existing prefix family.
2. Register in `ANALYTICS_EVENTS` under the right lifecycle/surface group,
   with the group comment if new.
3. Fire it: `trackEvent` from the surface; or add to `ServerEvent` +
   `captureServer` for Stripe/cron/server-lifecycle events. A new endpoint
   that mutates user state but captures nothing is a P3 finding per the
   AGENTS.md sweep contract — say so rather than silently skipping.
4. Payload passes the PII gate (section 5).
5. `npm run typecheck && npm test` — the phase4 suite is the proof.
6. List it in the PR description: name, call site, payload fields, and
   whether a PostHog insight/funnel should be created (unmeasured
   instrumentation gets flagged "instrumented but not measured" in the daily
   sweep — name the intended chart so it doesn't).

## 4. Renaming or removing an event

**Renaming.** The AGENTS.md contract: register the new name AND keep the old
one for at least one release, marked `// deprecated: replaced by <new>` so
reviewers can prune it later — saved PostHog dashboards reference names, and a
silent rename breaks them. The orphan tripwire (section 2, test 2) honors this
directly: any catalog line carrying a `// deprecated` marker is exempt from
the "must have a live call site" check (`loadDeprecatedCatalogNames` in
`phase4.contract.test.mjs`), because a deprecated alias having no call site is
the whole point. So the mechanism is: register the new name, keep the old
entry in `events.ts` with `// deprecated: replaced by <new>` on its line, and
switch every call site to the new name. Say in the PR when the old name can be
pruned (after the release window). Do NOT instead keep a fake quoted literal
of the old name at a call site to trick the orphan check — the deprecated
marker is the sanctioned way.

**Removing.** Before deleting a name, check whether any saved PostHog
insight, funnel, or cohort references it (PostHog → Data Management →
Events; the quarterly `scripts/posthog-audit.mjs` report also lists broken
dashboard references). If referenced, flag it to the maintainer instead of deleting.
Then remove catalog entry and call sites together, or the orphan/forward
tripwires fire.

## 5. PII discipline (no compiler, so it's on you)

Payloads MAY carry: identifiers (`user_id` is the PostHog `distinct_id`),
feature variants, latency, token counts, error reasons, coarse enums.
Payloads must NEVER carry: conversation content, message text, prompt
content, child names, or anything a parent typed. When in doubt, send a
length, a hash, or an enum — never the string. This applies doubly to
server events (`turn_finished` carries metrics *about* a turn, never the
turn). If a payload needs redaction to be safe, redact at the call site,
not in PostHog.

## 6. Guardrails

- Never `trackEvent` inside `/admin/*` surfaces (`src/pages/admin`,
  `src/routes/AdminRoutes.tsx`, `src/components/admin`) — suppression makes
  it a silent no-op at best and a contract violation regardless. Admin
  actions that change public state use `trackAdminAction`; everything else
  admin uses `admin_audit_log`.
- Never bypass `trackEvent`/`captureServer` with a raw `posthog.capture` —
  the typed seam is the contract.
- Never build event names dynamically (interpolation defeats both the type
  and the grep); ternaries over registered literals are fine.
- Never rename an event without the deprecation window, and never delete one
  a saved dashboard references without flagging it.
- Never let a payload smuggle user text under a friendly key
  (`context`, `preview`, `firstLine` are how it happens).
- Register events in the surface group where they belong; a catalog dumped
  at the bottom stops reading as a changelog.

## 7. Preflight before you hand back

- [ ] Every new event: registered in the right group, fired from a real call
      site, typecheck + `npm test` (phase4) green.
- [ ] Server events on BOTH the `ServerEvent` union and the catalog.
- [ ] Renames keep the old name registered + literal-referenced with
      deprecation comments; removals checked against saved PostHog objects.
- [ ] No `/admin` trackEvent; `git grep "trackEvent(" src/pages/admin
      src/routes/AdminRoutes.tsx src/components/admin` returns nothing.
- [ ] Every payload field passes the PII gate.
- [ ] PR description lists added/renamed/removed events by name and call
      site, with the intended measurement for new ones.
