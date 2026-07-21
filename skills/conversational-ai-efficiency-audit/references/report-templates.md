# Report templates — deliverables, schemas, ranking

Companion to `../SKILL.md`. This file defines what the audit produces and the
exact shape of every finding, experiment, and the machine-readable ledger.

## Audit directory

`docs/production-readiness/efficiency-audit-YYYY-MM-DD/` on the working
branch. A **full audit** produces all eleven files below. A **scoped audit**
produces `executive-findings.md`, `audit-data.json`, and only the ledger
files its scope touches — and says in the executive summary which files were
skipped and why. If a prior `efficiency-audit-*` directory exists, run
incrementally: diff `audit-data.json` against the latest prior one and mark
each prior finding resolved / open / regressed.

1. `executive-findings.md` — TL;DR; cost per turn / conversation / active
   user at current AND projected volume; the top three experiments; blocking
   instrumentation gaps; coverage statement (what was measured vs read vs
   sampled — no silent sampling); deltas vs the prior audit.
2. `system-request-path.md` — the request-path map. Every activity tagged:
   always / conditional / async; sequential-despite-independent;
   user-visible vs post-response; billed model or infra work.
3. `model-call-inventory.md` — one row per model call site (chat AND
   background: crons, evals/CI, admin, search-summarize): purpose, trigger,
   observed rate, model, prompt source, token distribution, cache behavior,
   latency, retry/fallback behavior, blocks-response?, async-able?,
   duplicates-another-call?, deterministic-replaceable?, smaller-model-able?,
   shared-structured-output candidate?, eval cases that gate it.
4. `context-token-ledger.md` — block-by-block prompt attribution: tokens,
   source file, stability class (static / per-user / per-turn), position
   relative to cache breakpoints, evidence of behavioral contribution,
   ablation candidate?
5. `latency-waterfall.md` — stage timings at p50/p95/p99 (auth/quota, config
   load, context assembly, retrieval, classifiers/safety, queueing, TTFT,
   generation, tools, post-model checks, persistence, telemetry flush),
   client-measured perceived latency, tail diagnosis, and the top
   sequential-but-independent segments.
6. `cost-model.md` — unit economics with dated pricing assumptions and a
   sensitivity note (which assumption moves the total most); non-production
   model spend (eval runner, CI, crons, admin tools); infra beyond tokens
   (Vercel function-seconds, Supabase, PostHog events, Langfuse ingestion);
   waste share (failed / retried / abandoned / fallback turns).
7. `static-code-findings.md` — code findings **on the AI runtime path
   only**, with measured-runtime findings separated from maintainability
   findings. Every removal claim passes the handoff-audit trap table
   (`.claude/skills/handoff-audit/references/scan-playbook.md` §4).
   Whole-repo dead-code sweeps are deferred to `handoff-audit`.
8. `optimization-opportunities.md` — all ranked findings, full schema below.
9. `experiment-backlog.md` — sequenced experiments, full schema below, one
   major variable each.
10. `do-not-optimize.md` — the negative registry: everything evaluated and
    rejected, with rationale and an explicit **revisit condition** (e.g.
    "revisit if daily conversations exceed N" ) so future audits do not
    re-propose it.
11. `audit-data.json` — machine-readable ledger, schema below. This is what
    makes the next audit diffable.

## Finding schema (required for every finding, every file)

```
ID:            EFF-YYYYMMDD-NN
Category:      model-calls | context-tokens | latency | db-io |
               orchestration | static-code | output-length |
               instrumentation-gap | cost-model
Statement:     one sentence.
Evidence:      [{source, detail, window}] — source ∈ turn-metrics | langfuse |
               posthog | vercel-logs | supabase-query | code-read |
               synthetic-probe | dated-pricing-sheet | estimate
Grade:         Measured | Inferred | Hypothesis
File refs:     path:line, …
Frequency:     per-turn | per-conversation | per-user-day | cron(<schedule>) |
               rare — with the observed rate and window
Current impact: $/month at current and projected volume; ms at p50/p95;
               tokens/turn; or complexity note
Proposed action:
Expected benefit: quantified where evidence allows; labeled estimate otherwise
Quality/safety risk: which conversation archetypes are exposed; which eval
               suites gate the change
Validation:    the exact experiment or measurement that would confirm it
Confidence:    High | Medium | Low — and why
Priority:      one of the six ranking buckets
```

**Evidence grades** (map to the house rubric in handoff-audit):

- **Measured** (≈Confirmed) — real telemetry from the audit window or a
  measurement you executed, with the query/trace/log citation. Only Measured
  findings can claim quantified savings as fact.
- **Inferred** (≈Probable) — code reading plus at least one corroborating
  signal (config, schema, historical metric). State the inference chain.
  Savings stated as labeled estimates.
- **Hypothesis** (≈Speculative) — code reading alone. Never enters the
  experiment backlog directly; it becomes a "Measure first" item.

## Ranking

Buckets: **Safe cleanup** / **Measure first** / **Low-risk experiment** /
**High-leverage controlled experiment** / **Do not pursue** / **Blocked by
missing evidence**.

Score each opportunity coarsely (high / medium / low — no false numerical
precision; one line of basis each) on: monthly savings at projected volume;
user-visible latency win; maintainability win; evidence strength; effort;
reversibility; quality risk; safety risk; privacy/compliance risk; and
**added operational complexity** as a penalty.

Hard rules:

- Safety risk ≥ medium → cannot be ranked "Low-risk experiment", whatever
  the savings.
- A change that introduces a new caching, routing, or orchestration layer
  must project savings clearly exceeding the cost of operating that layer,
  or it ranks no higher than "Measure first".
- Ties break toward the option that removes work and complexity rather than
  making existing work faster.
- Findings graded Hypothesis rank no higher than "Measure first".

## Experiment schema

```
ID:              EXP-YYYYMMDD-NN   (links finding IDs)
Hypothesis:      falsifiable, with a number.
Surface:         exact files / config / harness atoms touched.
Baseline:        cohort, window, and the measured baseline metrics.
Change:          one major variable (bundles only when explicitly testing a bundle).
Expected effect: cost and latency, with the arithmetic shown.
Quality invariants (pre-registered BEFORE running):
                 stated in the harness's own vocabulary — the 5-point
                 ordinal verdicts and green/amber/red/black outcome bands.
                 Safety-critical dimensions (src/lib/ai/harness/states.ts):
                 zero regression, no new red/black. Golden/holdout/
                 multi-turn: within a stated margin. Checked per archetype
                 and per graph state, never only in aggregate; repair-
                 moment, tone, and memory-coherence cases called out
                 explicitly for context/prompt changes.
Eval plan:       which eval_case suites, how invoked (drain-eval-runs /
                 /eval-changeset), judge calibration noted.
Rollout plan:    offline eval → shadow/preview → canary %, with gates.
Success threshold / Rollback threshold: numeric, pre-registered.
New telemetry:   what must be instrumented first, if anything.
Confidence:      High | Medium | Low.
Implementation route: /change-pass + /eval-changeset for any harness or
                 prompt text; migration-lifecycle for schema;
                 analytics-instrument for event changes; ordinary
                 branch + PR + preview-qa for code.
```

## audit-data.json schema

```json
{
  "audit": {"date": "", "commit_sha": "", "mode": "full|scoped:<scope>",
             "data_window": "", "prior_audit": "path-or-null"},
  "traffic": {"turns_per_day": 0, "conversations_per_day": 0,
               "active_users": 0, "source": "", "note": "current volumes;
               projections live in cost assumptions"},
  "pricing_assumptions": [{"model": "", "usd_per_mtok_in": 0,
    "usd_per_mtok_out": 0, "usd_per_mtok_cached_in": 0,
    "source": "", "as_of": "date"}],
  "activities": [{"id": "", "name": "", "kind": "model|db|api|compute",
    "trigger": "", "model": null, "blocking": true, "freq_per_day": 0,
    "tokens": {"in_p50": 0, "out_p50": 0, "cached_share": 0},
    "latency_ms": {"p50": 0, "p95": 0, "p99": 0},
    "cost_usd": {"per_call": 0, "per_month_current": 0,
                  "per_month_projected": 0},
    "grade": "Measured|Inferred|Hypothesis"}],
  "findings": [{"id": "", "category": "", "grade": "", "priority": "",
                 "statement": ""}],
  "experiments": [{"id": "", "finding_ids": [], "hypothesis": "",
                    "status": "proposed"}]
}
```

Numbers you did not measure stay out of the JSON or carry
`"grade": "Inferred"` / `"Hypothesis"` — the next audit will diff this file
and treat Measured entries as trend data.
