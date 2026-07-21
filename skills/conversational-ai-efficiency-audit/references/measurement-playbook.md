# Measurement playbook — data sources, queries, methods

Companion to `../SKILL.md`. Everything here is evidence-gathering. Paths and
schema facts verified at commit `e80fde7` (2026-07-15); re-verify anything
load-bearing before citing it — files move, columns get added.

## 1. Request-path ground truth (Phase 1)

Read the executable path, not the docs:

- `api/llm/chat.ts` — the whole turn lifecycle (~2.5k lines; `maxDuration`
  60s in `vercel.json`). Pre-model gate order inside `POST`: `requireUser`
  (`api/_lib/auth.ts`) → `checkRateLimit` (`api/_lib/rateLimit.ts`) → mock
  fallback when `!isAiGatewayConfigured()` → `enforceFreeConversationQuota`
  (`src/lib/ai/safety/conversationQuota.ts`) → `acquireLlmSlot`
  (`api/_lib/concurrencyLimit.ts`) → `runInputGuard`
  (`src/lib/ai/safety/guards.ts`) → safety classifiers in parallel with
  context build → `checkPreCallBudgets` (`src/lib/ai/safety/budgets.ts`,
  kill-switch / token / spend caps) → stream.
- Context assembly: `buildTurnContext()` in `src/lib/ai/state/context.ts` —
  a `Promise.all` of six reads (user memory, conversation memory, recent
  turns, children, family, locale) + conversation state + guidance
  retrieval (embedding call + pgvector RPC, LRU-cached) + moments
  retrieval.
- Other model endpoints: `api/llm/summarize.ts` (themes + summary),
  `api/llm/search-summarize.ts` (30s cap), `api/sleep.ts` (sleep stories),
  `api/_lib/plans/generator.ts` (plans), `api/llm/chat-persist-retry.ts`
  (dead-letter recovery, no model).
- Crons: the `crons` block in `vercel.json` is the schedule of record.
  Model-backed today: `drain-eval-runs` (every minute),
  `title-unnamed-conversations`, `promote-user-memory` (daily),
  `promote-weekly-pattern-check` (weekly); verify the rest each audit.
- Client: `src/hooks/useConversationController.ts` (sends `x-request-id`,
  reads the stream), `src/lib/ai/streamChunks.ts` (SSE parser),
  `src/contexts/ConversationContext.tsx`.

## 2. The turn ledger: `conversation_turn_metric` (primary source)

One row per turn via `recordTurnMetric()`
(`src/lib/ai/safety/turnMetrics.ts`). Key columns: `created_at`, `user_id`,
`conversation_id`, `request_id`, `source`, `intent`, `model`,
`prompt_tokens`, `completion_tokens`, `total_tokens`,
`cache_read_input_tokens`, `cache_creation_input_tokens`, `cost_usd`,
`latency_ms`, `tool_call_count`, `guard_trip_count`, `finish_reason`,
`error_message`, `graph_id`, `current_node_key`, `prompt_variant_label`,
`fallback_used`, `provider_used`, `zdr_requested`, `backchannel_*`,
`guidance_retrieval_skipped`, `deterministic_signal_count`.

Query read-only via `mcp__Supabase__execute_sql` (project `Satsang`, ref
`facgwtempyxekghnpxth`). Starters — adjust the window to the audit window:

```sql
-- Daily volume, tokens, recorded cost, cache-read share
select date_trunc('day', created_at) d, count(*) turns,
       sum(total_tokens) tokens,
       round(sum(cost_usd)::numeric, 4) recorded_cost_usd,
       round(avg(prompt_tokens)) avg_in, round(avg(completion_tokens)) avg_out,
       round(100.0 * sum(cache_read_input_tokens)
             / nullif(sum(prompt_tokens), 0), 1) cache_read_pct
from conversation_turn_metric
where created_at > now() - interval '30 days'
group by 1 order by 1;

-- Latency percentiles per model
select model, count(*) n,
       percentile_cont(0.5)  within group (order by latency_ms) p50,
       percentile_cont(0.95) within group (order by latency_ms) p95,
       percentile_cont(0.99) within group (order by latency_ms) p99
from conversation_turn_metric
where created_at > now() - interval '30 days' group by 1;

-- Waste ledger: fallbacks, errors, non-stop finishes
select finish_reason, fallback_used, count(*) n,
       round(sum(cost_usd)::numeric, 4) cost
from conversation_turn_metric
where created_at > now() - interval '30 days'
group by 1, 2 order by n desc;

-- Cost per conversation + the expensive tail (diagnose the top rows)
select conversation_id, count(*) turns, sum(total_tokens) tokens,
       round(sum(cost_usd)::numeric, 4) cost
from conversation_turn_metric
where created_at > now() - interval '30 days'
group by 1 order by cost desc limit 20;

-- Backchannel: what the first-beat ack costs and buys
select count(*) filter (where backchannel_latency_ms is not null) with_bc,
       avg(backchannel_latency_ms) avg_bc_ms, avg(latency_ms) avg_total_ms
from conversation_turn_metric
where created_at > now() - interval '30 days';
```

**Recorded-cost gotchas (do not skip):**

1. `cost_usd` = `computeTurnCostUsd()` using the flat
   `model_input_cost_per_mtok` / `model_output_cost_per_mtok` keys from
   `runtime_config`. Cache reads (~10% of input rate) and cache writes
   (~125%) are recorded as separate token columns but **not folded into
   `cost_usd`**. When caching is active, recompute true cost from the
   three token columns and the provider's current cache pricing — and
   first confirm in `src/lib/ai/gateway.ts` whether `prompt_tokens`
   includes or excludes the cache columns before trusting any formula.
2. PostHog's `turn_finished` fires **only** on non-`stop`/fallback
   finishes (`recordTurnMetric` seam). Never use PostHog for turn volume;
   use this table.
3. Price keys are admin-editable data, not ground truth. Cross-check
   against the provider's current price sheet, date-stamp every price in
   `cost-model.md`, and note which findings are sensitive to a price
   assumption.

## 3. Langfuse traces (span-level breakdown)

`src/lib/ai/telemetry/otel.ts` exports AI-SDK spans over OTLP to Langfuse
and/or Agnost (gated on env keys; conversation content is never exported —
`recordInputs`/`recordOutputs` forced false, consistent with ZDR). Use the
**langfuse skill** (CLI via `npx langfuse-cli`) for span queries: per-stage
latency, TTFT where recorded, token usage per call site, trace counts per
activity. Also check whether `flushTelemetry` (called after the reply in
`chat.ts`) ever blocks the response path.

## 4. Infra and non-token cost

- **Vercel MCP**: `get_runtime_logs` / deployment data for function
  durations vs `maxDuration` (chat 60s, search-summarize 30s), cold
  starts, and error rates. Function-seconds are a real cost line at
  volume.
- **Supabase MCP**: `get_advisors` (index/RLS advice on the per-turn
  tables: `conversation`, `conversation_message`, `conversation_state`,
  `user_memory`, `conversation_memory`, `conversation_turn_metric`),
  `get_logs` for slow queries.
- Cron overhead: `cron_run_history` (via `api/_lib/cronRun.ts`) for run
  counts, durations, failures — `reminders` runs every 2 minutes,
  `drain-eval-runs` every minute; scan cost scales with table size, not
  usage.
- Dead-letter volume: `conversation_message_dropped` rows and
  `chat-persist-retry` hits.
- PostHog event volume and Langfuse ingestion are per-event cost lines;
  estimate and label.

Non-production model spend: `eval_run` row counts × per-run judge+subject
tokens; admin `prompt-assistant` / `caretaker` / transcript-judging usage;
`runModelTrial` runs. At current traffic this can rival production spend —
report it as its own cost-model section.

## 5. Context-token attribution (Phase 6)

The system prompt is assembled by `assembleSystemBlocks()`
(`src/lib/ai/state/context.ts`) into four segments with distinct cache
behavior (breakpoints applied in `src/lib/ai/gateway.ts`, Anthropic models
only):

| Segment | Cache | Contents (builders) |
|---|---|---|
| 0 stable | 1h TTL | config digest, instruction hierarchy + constitution (`safety/spotlight.ts`, `harness/constitution.ts`), base persona, exemplars (`harness/examples.ts`), model voice overlay (`prompts/modelVoiceOverlay.ts`) |
| 1 session | 1h TTL | graph stance + node overlay (`state/graph.ts`), handoff copy |
| 2 userScope | 5m TTL | user-memory summary, children + family roster |
| 3 perTurn | uncached | canary, language, entry context (`prompts/entryContext.ts`), retrieved guidance (`knowledge/retrieveGuidance.ts`), conversation memory, moments (`moments/retrieve.ts`), do-not-say (`doNotSay/promptBlock.ts`), governance overlay, voice rules |

Method: capture the composed blocks via `captureHarnessSnapshot`
(`src/lib/ai/harness/snapshot.ts`) for representative users/states; count
tokens per block; compute each block's share of `prompt_tokens` and its
cache position. Cache-hit economics: `cache_read_input_tokens /
prompt_tokens` from the ledger, segment TTLs, and **digest churn** —
`computeConfigDigest()` busts segment 0 on any admin config edit, so count
config-edit frequency (`admin_audit_log` / `runtime_config` versions) in
the window. Prior art to read first:
`docs/plans/cache-hit-rate-improvement.md`,
`docs/plans/cache-zero-day-investigation.md`.

Ablations run through the eval harness as draft change-sets
(/change-pass + /eval-changeset) — never raw prompt edits, never "a human
read it and it looked redundant".

## 6. Latency waterfall method (Phase 7)

- **Server stages**: Langfuse spans + `latency_ms`,
  `backchannel_latency_ms`, and stage evidence from code (classifier
  timeout budget ~900ms; blocking vs background memory refresh; guidance
  retrieval when not skipped; `flushTelemetry` after reply).
- **Client-perceived**: the controller stamps `x-request-id` → correlate a
  client-side timing capture with the server row by `request_id`. If no
  client timing exists, that is an `instrumentation-gap` finding — do not
  hack a patch in during the audit.
- **Synthetic probes**: scripted turns against a **preview deployment**
  with a test account, timed at the client; label every such number
  `synthetic`. Never probe production users' conversations; probe content
  must contain no real user data; probes cost real tokens — budget and
  count them.
- **Tail**: pull the p99 latency rows and the top-1% cost conversations
  from the ledger and diagnose drivers individually (long context, tool
  loops, retries, fallback restarts, cold starts).

## 7. Model-call census rebuild (Phase 5)

The seed census lives in `audit-checklists.md` §4. Rebuild/verify it with:

```bash
grep -rn "streamText\|generateText\|generateObject\|embedMany\|embed(" \
  src/lib/ai api src --include='*.ts' -l
grep -rn "gateway(" src/lib/ai --include='*.ts'
grep -rhoE "AI_[A-Z_]*MODEL" src api | sort -u   # per-task model env vars
```

Model/provider config: `src/lib/ai/config.ts` (`getAiConfig()`), ZDR tiers
and provider ordering (`AI_GATEWAY_ZDR_ENABLED`,
`AI_GATEWAY_ALLOWED_PROVIDERS`, `AI_GATEWAY_PROVIDER_ORDER`, admin
variants), runtime overrides in `runtime_config` (60s in-memory cache in
`config/runtimeConfig.ts`).
