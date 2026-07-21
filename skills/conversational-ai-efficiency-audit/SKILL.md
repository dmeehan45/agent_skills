---
name: conversational-ai-efficiency-audit
description: >-
  Audit the complete Avani conversational AI system for measurable
  opportunities to reduce cost, latency, token usage, model calls, and
  runtime complexity without degrading experience quality, behavioral
  safety, privacy/ZDR, or reliability. Use when asked for an efficiency,
  cost, token, or latency audit; a cost-per-conversation or unit-economics
  model; "why is Avani slow / expensive"; a prompt-cache or context-window
  analysis; a model-call inventory; or a pre-scale-up review. It maps the
  request path, builds the cost and latency ledger from real telemetry
  (conversation_turn_metric, Langfuse, Vercel, Supabase), inventories every
  model-backed activity including crons, evals, and admin surfaces,
  attributes prompt tokens block by block, and files an evidence-graded
  report with ranked, pre-registered experiments in
  docs/production-readiness/. Audit-only: it never implements optimizations
  in the same pass. Not for whole-repo maintainability (handoff-audit),
  product QA (qa-sweep), single-diff review (/code-review), security
  (/security-review), or authoring harness changes (/change-pass and
  /eval-changeset implement those).
argument-hint: "[full | scoped:<subsystem> | refresh]"
---

# Conversational AI efficiency audit (Avani)

The objective is not the cheapest individual turn. It is the lowest
sustainable cost per successful, safe, high-quality conversation. The
deliverable is an evidence-graded report and experiment backlog, not a diff.

The failure mode this method prevents: plausible-sounding optimizations
built on unmeasured assumptions — trimming a prompt block an eval depends
on, caching an emotionally sensitive reply, "cleaning up" code that never
runs on the hot path, or swapping the chat model globally to save money the
telemetry says we do not spend. Every number in the report is measured,
labeled as an estimate, or absent.

Companion files: `references/measurement-playbook.md` (data sources,
queries, methods), `references/audit-checklists.md` (per-phase inspection
lists, model-call census seed, optimization ladder, prohibited shortcuts),
`references/report-templates.md` (deliverables, schemas, ranking rubric).

## 0. Rules (non-negotiable)

- **Audit-only.** The only files this skill writes are the report directory
  and scratchpad notes. No optimization is implemented in the audit pass,
  not even "obviously safe" ones. Each approved item later becomes its own
  branch/PR through the owning process.
- **The recommendation contract.** No optimization is recommended without
  all seven: evidence the activity exists; its observed (or honestly
  estimated) frequency; its current cost / latency / complexity
  contribution; the expected improvement with arithmetic shown; the
  behavioral and operational risks; a validation experiment; rollback
  criteria. Missing one → it is a "Measure first" item, not a
  recommendation.
- **Evidence grades** (rubric in report-templates): **Measured** (telemetry
  or executed measurement, citation attached) / **Inferred** (code reading
  plus a corroborating signal, chain stated) / **Hypothesis** (code reading
  alone — never enters the experiment backlog). Never present Inferred as
  Measured. Never claim cleaner code will reduce runtime cost or latency
  without execution-path evidence.
- **Prefer, in order:** removing work; preventing invocation of conditional
  work; deduplicating work; caching; parallelizing; deferring off the
  user-visible path; shortening output; deterministic code over a model
  call for bounded tasks; narrowly routing small models; and only then —
  with everything else exhausted — changing the primary model.
- **Invariants, not variables:** behavioral safety, privacy, ZDR routing,
  data retention, and the governance process. An optimization that needs
  one of these loosened is "Do not pursue", with the reason recorded.
- **No aggregate-only validation.** Averages hide concentrated harm. Every
  quality claim is checked per conversation archetype, per graph state, and
  on safety-critical cases; every latency claim at p50 / p95 / p99, never
  only the median.
- **AGENTS.md applies.** Feature branch, never `main`, never merge, no
  secrets in the report, preview link after pushing, teaching notes (1–3
  concepts) in the wrap-up.

## Phase 0 — Scope intake and prior art

1. **Mode**: `full` (all phases, all deliverables), `scoped:<subsystem>`
   (e.g. `scoped:context-cache`, `scoped:crons` — run phases 1–3 for the
   boundary plus the deep phase for that subsystem), or `refresh`
   (re-measure the ledger and diff `audit-data.json` against the prior
   audit, no new deep reading). If David named a scope, honor it; a bare
   invocation means `full`.
2. **Snapshot** the commit SHA and define the data window (default: last 30
   days, or since the prior audit).
3. **Prior art first** — do not rediscover: the latest
   `docs/production-readiness/efficiency-audit-*/` (if any → incremental
   mode), `handoff-audit-*.md`, `avani-observability-eval-strategy.md`,
   `docs/plans/cache-hit-rate-improvement.md`,
   `docs/plans/cache-zero-day-investigation.md`, recent `qa/daily-*.md`,
   and `do-not-optimize.md` from the prior audit (re-proposing a rejected
   item without new evidence is a defect).
4. **Instrumentation check**: can `conversation_turn_metric` + Langfuse
   answer frequency, tokens, cost, and latency for the window? Gaps become
   finding #1 (category `instrumentation-gap`); proceed with labeled
   estimates rather than stalling.
5. **Traffic honesty**: state current volumes plainly. At pre-launch
   traffic, monthly savings are small by definition — rank by projected
   volume (state the projection and its source) and by complexity removed,
   and say so in the executive summary.

## Phase 1 — System boundary and request-path map

Map every entry point and everything a turn executes: auth → rate limit →
quota → concurrency slot → input guard → safety classifiers → context
assembly → retrieval → primary call (+ fallback) → tools → post-model
checks → persistence → telemetry flush — plus the non-chat surfaces
(`api/llm/summarize.ts`, `api/llm/search-summarize.ts`, `api/sleep.ts`,
plans generator) and all model-backed crons. Tag each activity: always /
conditional / async; sequential-despite-independent; user-visible vs
post-response; billed model or infra work. Verify against executable code
and `vercel.json`, not docs. Seed paths and census commands:
checklists §1–2, playbook §1. Output: `system-request-path.md`.

## Phase 2 — Behavioral baseline

Locate and run the strongest quality controls available: the `eval_case`
DB suites via the harness runner (`src/lib/ai/evals/runner.ts`,
`src/lib/ai/harness/`, drained by `api/cron/drain-eval-runs.ts`) — golden,
safety-critical, holdout, multi-turn; judge calibration data and
`SAFETY_CRITICAL_DIMENSIONS` (`src/lib/ai/harness/states.ts`); human
review artifacts in `qa/` and the feedback tables; VERA-MH per the
observability-eval strategy doc (planned benchmark — not in-repo; say so
rather than claiming a score). Record the verdict distribution (the house
5-point ordinal and green/amber/red/black bands), safety pass rate,
failure-mode distribution, and judge disagreement — per archetype, graph
state, prompt variant, and model. If no defensible baseline can be
established, that is the first **blocking** finding: efficiency work that
cannot prove non-inferiority does not ship.

## Phase 3 — Cost and latency ledger

Build the ledger from real telemetry per playbook §2–4: per-activity
frequency, tokens (in / out / cache-read / cache-creation), model, cost,
latency percentiles, failure and retry rates, user-visible vs background.
Compute cost per turn, per conversation, per active user, per
quality-passing conversation, by archetype, and projected monthly cost at
current and projected volume. Include the **waste ledger** (fallbacks,
errors, non-`stop` finishes, dropped-message retries, abandoned streams)
and **non-production spend** (eval runner, CI, admin tools, model trials,
crons). Beware the two recorded-cost gotchas in playbook §2 (cache tokens
not folded into `cost_usd`; PostHog undercounts turns). Pricing: dated,
sourced, and cross-checked against `runtime_config` price keys. Outputs:
`cost-model.md`, `latency-waterfall.md` (with Phase 7).

## Phase 4 — Static code efficiency (runtime path only)

Inspect the AI runtime path for dead flags, duplicate work, repeated
queries and serialization, sequential awaits that could run concurrently,
unbounded caches, retry loops without limits or idempotency, and code
retained for obsolete behavior — checklist in checklists §3. Scope
discipline: whole-repo dead-code and dependency sweeps belong to
`handoff-audit`; anything resembling a removal claim must pass that
skill's two-signal rule and false-positive trap table
(`.claude/skills/handoff-audit/references/scan-playbook.md` §4). Report
maintainability findings separately from measured-runtime findings.
Output: `static-code-findings.md`.

## Phase 5 — Model-call inventory

Document every model-backed activity — chat, backchannel, classifiers,
summarizers, memory promotion, titling, tone canary, plans, sleep stories,
embeddings, eval judges, admin assistants — one row each, fields per
report-templates. Start from the seed census in checklists §4 and
re-verify it (files move). For each call ask: does it block the reply;
could it run async; does it duplicate another call's reasoning; could
deterministic logic replace it; could a smaller model do it; could several
activities share one structured output; which eval cases gate it. Do not
merge calls merely because they look semantically similar — merged calls
couple failure modes and can raise total tokens. Output:
`model-call-inventory.md`.

## Phase 6 — Context and prompt efficiency

Attribute prompt tokens to the actual system-block architecture (four
segments with distinct cache TTLs — playbook §5): tokens per block, source
file, stability class, position relative to cache breakpoints, and
evidence of behavioral contribution. Inspect for: repeated or
contradictory instructions across blocks; large exemplars with low
demonstrated contribution; tool schemas exposed on turns that cannot use
them; retrieved guidance injected but unused
(`guidance_retrieval_skipped` exists for a reason); dynamic values placed
ahead of cacheable prefixes; config-digest churn busting the cache;
summaries repeating recent raw turns; output verbosity beyond product
need. Contribution is established by **ablation through the eval harness**
(a draft change-set through /change-pass + /eval-changeset), never by "a
human read it and it looked redundant". Output: `context-token-ledger.md`.

## Phase 7 — Runtime latency waterfall

Build the end-to-end waterfall per playbook §6: server stages from turn
metrics and Langfuse spans; client-perceived timing correlated via
`x-request-id`; TTFT vs total generation; tail analysis on the p99 and the
top-1% most expensive conversations. Evaluate the latency machinery the
system already has — backchannel first beat, simple-routing downgrade,
classifier timeout budgets, retrieval skip, blocking vs background memory
refresh — and measure whether each earns its cost. Never move work off the
user-visible path when doing so creates unsafe responses, inconsistent
state, or loss of audit evidence. Output: `latency-waterfall.md`.

## Phase 8 — Experiments

Convert findings into isolated experiments per the optimization ladder
(checklists §5) and the experiment schema (report-templates): falsifiable
hypothesis, exact surface, baseline cohort, **pre-registered quality
invariants** (safety-critical: zero regression; golden/holdout: stated
margin; checked per archetype and graph state), eval plan, rollout plan
(offline eval → preview shadow → canary), numeric success and rollback
thresholds, and the implementation route (/change-pass + /eval-changeset
for harness text; migration-lifecycle for schema; analytics-instrument for
events; ordinary PR for code). One major variable per experiment. Output:
`experiment-backlog.md`.

## Phase 9 — Rank, report, hand off

Rank into the six buckets with the rubric in report-templates (savings,
latency, maintainability, evidence, effort, reversibility, quality /
safety / privacy risk, added-operational-complexity penalty — coarse
grades, no false precision). Favor changes that reduce both work and
complexity; penalize savings that buy new routing/caching/orchestration
layers. Write the full directory (report-templates), including
`do-not-optimize.md` with revisit conditions and `audit-data.json` for the
next audit to diff. Close `executive-findings.md` with the three
experiments offering the strongest combination of savings, evidence,
reversibility, and low behavioral risk — and with proposed **regression
guards** (turn-metric budget alerts, cache-hit-rate watch, eval-cost line)
so the wins persist.

Commit to the working branch, push, and surface the branch preview URL per
the repo contract (preview-qa). In the wrap-up: executive summary, honest
coverage statement, the top three experiments, open questions for David,
teaching notes. Then stop — implementation is a separate, per-item,
explicitly approved follow-up.

## Avani invariants (constraints on every recommendation)

- **Gateway + ZDR routing stays.** The Vercel AI Gateway credential and
  env-var routing pattern (`AI_GATEWAY_*`, per-task model env vars) is the
  seam; user-content calls run ZDR fail-closed, admin/eval surfaces run on
  the separate non-ZDR tier. No recommendation may move user content to a
  non-ZDR path or bypass the gateway.
- **Prompt text is governed.** Any change to prompt or harness text — even
  deletions "just for tokens" — routes through /change-pass +
  /eval-changeset. This audit may draft the change-set; it may not apply
  it.
- **Existing machinery first.** Turn metrics, harness snapshots, the eval
  runner, `runtime_config`, Langfuse-over-OTLP, and the Supabase data
  model are used before any new vendor, framework, or observability layer
  is proposed. An agent-framework migration is recommendable only if the
  thin runtime demonstrably prevents a required optimization.
- **High-risk surfaces**: emotionally sensitive, relationship, parenting,
  and crisis-adjacent conversations; repair moments; the safety-classifier
  path. No semantic caching of user-facing coaching replies by default; no
  weakening, combining, or reordering of safety checks justified by
  average-case traffic; crisis-adjacent flows are excluded from
  latency-motivated reordering that would weaken pre-response checks.
- **PII discipline** (AGENTS.md): the report and `audit-data.json` carry
  identifiers, counts, tokens, and latencies — never conversation content,
  message text, prompt content, or child names. Quote code, not users.

## Orchestration

Fan out read-only Explore agents per phase (boundary, ledger, call
inventory, context, latency), each returning findings in the report
schema; then run an adversarial verification pass that tries to **refute**
each Measured/Inferred claim before it enters the report — the query
re-run, the trap-table check, the counter-example hunt. For a full audit,
orchestrate finder → verifier as a Workflow (invoking this skill is the
opt-in); for a scoped audit, a handful of parallel agents suffices. One
synthesis owner writes the report; agents never write product files.
