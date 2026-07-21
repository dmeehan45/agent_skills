# Handoff shelf templates (`docs/engineering/`)

Load this when bootstrapping the shelf (first `AUDIT_ONLY` run) or when
unsure what belongs in which file. Principles that outrank any
template: **truthful beats complete** (a wrong map is worse than no
map — every claim in these docs gets the same evidence bar as a
finding); **useful beats exhaustive** (where to start, how it's shaped,
what's fragile, what must not be casually reversed); **maintained beats
written** (every doc header carries `Last verified: <date> at <sha>` —
a cycle that touches a doc re-stamps it; a stale stamp is itself a
register item). Do not duplicate what the repo already answers well —
link to `AGENTS.md`, `api/README.md`, `docs/governance/`, prior audits
— the shelf is the index and the judgment layer, not a mirror.

On bootstrap: mine the newest `docs/production-readiness/
handoff-audit-*.md` (+ addenda). Its confirmed findings and checklist
items seed `TECH_DEBT_REGISTER.md`; its coverage/census sections seed
`SYSTEM_MAP.md`; its "not examined" list seeds the open uncertainties
of the first `ENGINEERING_HEALTH.md` entry. Do not re-derive what it
already proved; do re-verify anything you promote into the map.

## SYSTEM_MAP.md

```markdown
# System map
Last verified: YYYY-MM-DD at <sha>

## What this product is (3–5 sentences, current name, live domains)
## Components and responsibilities
<!-- SPA (src/), serverless api/ (filesystem-routed), Supabase
     (Postgres+RLS, migrations ledger), crons, edge functions, external
     services (Stripe, LLM gateway, ElevenLabs, Resend, PostHog,
     Langfuse). One paragraph each: responsibility, entry points,
     owner-of-truth. -->
## How a request travels
<!-- One worked example per class: a chat turn (client → api → safety →
     model → persistence), a checkout, a cron firing. Name the actual
     files. -->
## Where auth and authorization are enforced
<!-- The seams, not every check: token verification, admin gate, cron
     secret, RLS, service-role usage rules. -->
## Data: written, read, transformed, deleted
<!-- The tables that matter, retention/deletion paths, what is
     content-excluded from telemetry and why. -->
## Business-critical files
<!-- The short list a new dev must not edit casually, with one line on
     why each is load-bearing. -->
## Intentionally unusual (do not "fix")
<!-- Deliberate divergences with their rationale/ADR links — e.g.
     patterns a naive cleanup would wrongly consolidate. -->
## Not yet understood
<!-- Honest list. Items here block refactors of those areas. -->
```

## DEVELOPER_ONBOARDING.md

```markdown
# Developer onboarding
Last verified: YYYY-MM-DD at <sha> (walked end-to-end: yes/no)

## Day one: clone to running app
<!-- Exact commands, Node version (as CI pins it), env var NAMES with
     purpose and where a dev-safe value comes from. Never values. -->
## Verify your setup
<!-- The gate commands and what green looks like; known env caveats
     (e.g. Playwright binaries in containers). -->
## Your first safe change
<!-- A worked, low-risk example: branch discipline, which gates run in
     CI vs locally, preview URL QA flow, who merges (the maintainer, only). -->
## The rules that bite
<!-- Pointers with one-line summaries: AGENTS.md contract, migration
     ledger, analytics catalog, i18n propagation, PII discipline. -->
## Where to ask / how decisions get made
```

## CRITICAL_USER_FLOWS.md

```markdown
# Critical user flows
Last verified: YYYY-MM-DD at <sha>

<!-- 3–7 flows that must keep working. Candidates to confirm with
     the maintainer on bootstrap: signup/onboarding → first conversation;
     a chat turn (incl. safety + quota); paywall → checkout →
     entitlement; plans + reminders; sleep story generation (spend
     path); account deletion / privacy request. -->

## <Flow name>
- Why it is critical:
- Entry point → code path: <files, in order>
- External dependencies:
- How to verify it works: <manual steps on preview, and/or test file>
- Known fragilities: <register links>
```

## TECH_DEBT_REGISTER.md

```markdown
# Tech debt register
<!-- Open items only; resolved items move to the resolving cycle's
     entry in ENGINEERING_HEALTH.md. Sorted P0→P3, then by age.
     Cheap P3s may live here indefinitely — that is the register
     working, not failing. -->

## RL-<nnn>: <title>
- Priority / Confidence: P2 / Confirmed
- First recorded: YYYY-MM-DD · Last re-verified: YYYY-MM-DD
- Evidence: <file:line, command output, signal>
- Consequence: <user or developer cost, concretely>
- Recommended action / scope: <S/M/L>
- Verification once fixed:
- Risk of changing / of leaving:
- Blocked on: <approval / owner-side setting / evidence / nothing>
```

## ENGINEERING_HEALTH.md

```markdown
# Engineering health log
<!-- One entry per cycle, newest first. This file is the loop's
     memory: next cycle's Orient stage reads the top entry. -->

## Cycle YYYY-MM-DD — <mode>
- Reviewed: <sha> · window: <prev-sha>..<sha> (<n> PRs, <n> migrations)
- Deep-dive area this cycle: <rotation item + one-line outcome>
- Gates: lint PASS · typecheck PASS · test <passed>/<total> ·
  audit PASS · migrations PASS · build PASS · mobile NOT RUN (<reason>)
- Signals reviewed: <sources checked / NOT CHECKED>
- Register: +<new> −<resolved: RL-ids w/ commits> ↺<carried>
- Change made: <one line + PR/branch> · Verified: <what, honestly>
- Uncertainties: <what we still can't explain>
- Next cycle starts at: <one named item>
```

## OBSERVABILITY_GUIDE.md

```markdown
# Observability guide
Last verified: YYYY-MM-DD at <sha>

## When something breaks, look here first
<!-- Symptom → source table: user reports chat failure → Vercel
     runtime logs + Langfuse trace; billing wrong → Stripe dashboard +
     webhook logs + server events; cron suspicion → cron_run +
     Supabase logs; data question → conversation_turn_metric,
     admin_audit_log. Include retention limits — what disappears in a
     day, what keeps. -->
## What we deliberately do NOT record
<!-- Content exclusion, PII discipline, admin PostHog suppression —
     so nobody "fixes" the absence. -->
## Known gaps
<!-- Mirror the register's ops items: e.g. no error tracker, no
     alerting — with RL-ids. -->
```

## decisions/NNN-short-title.md

```markdown
# NNN. <Decision title>
Date: YYYY-MM-DD · Status: accepted | superseded by NNN
## Context      <!-- the forces, in this repo's terms -->
## Decision     <!-- one paragraph, active voice -->
## Consequences <!-- incl. what becomes harder; revisit-when trigger -->
```

Write an ADR when a cycle makes or surfaces a decision with lasting
consequences — including decisions **not** to act (e.g. "divergent
fetch wrappers are deliberate; do not consolidate") — so future cycles
and future developers stop re-litigating them. Number sequentially;
never rewrite an accepted ADR, supersede it.
