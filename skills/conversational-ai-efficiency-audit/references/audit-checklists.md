# Audit checklists — census, inspection lists, ladder, prohibitions

Companion to `../SKILL.md`. Seed facts verified at commit `e80fde7`
(2026-07-15) — re-verify each audit with the rebuild greps in
`measurement-playbook.md` §7 before citing them.

## 1. Boundary census (Phase 1)

Enumerate, with file refs: user-facing entry points; request handlers and
streaming paths; auth / rate limit / quota / concurrency / budget gates;
context and prompt construction; conversation + user memory reads/writes;
retrieval and guidance injection; graph/state transitions; pre-model
classifiers and guards; primary + fallback model calls; tool definitions
and invocation paths; post-model validation; persistence; telemetry and
analytics; retries, dead letters, scheduled jobs, fallback behavior.

Per-activity tags (all six required): always | conditional | async;
sequential-despite-independent?; user-visible latency?; post-response
latency?; billed model work?; billed infra work?

## 2. Persistence hot path (Phase 1/4)

Per-turn tables: `conversation`, `conversation_state`,
`conversation_message` (+ `conversation_message_dropped` dead-letter),
`user_memory`, `conversation_memory`, `children`, `family_members`,
`profiles` (locale), `conversation_turn_metric`. Modules:
`src/lib/ai/state/{conversations,messages,memory,children,family}.ts`.
Look for: repeated reads of the same row within a turn; N+1 patterns;
unbounded result sets (`getRecentTurns` limits); fire-and-forget writes
that can silently drop state; missing indexes surfaced by
`mcp__Supabase__get_advisors`.

## 3. Static efficiency on the runtime path (Phase 4)

Inspect for: dead feature flags and config keys; duplicate implementations
of the same transform; overlapping prompt/policy layers; repeated
serialization of the same payload; repeated DB queries per turn; sequential
`await`s on independent work; per-invocation reloading of config that is
cacheable (note `loadRuntimeConfig`'s 60s in-memory cache — verify what
that means per serverless instance); unbounded or ineffective caches (LRU
sizes, invalidation); retry loops without limits or idempotency keys;
error paths that redo full work; code retained for obsolete product
behavior; oversized handlers with mixed responsibilities (`chat.ts` is
~2.5k lines — findings here are maintainability unless measured).

Discipline: any removal claim passes handoff-audit's two-signal rule and
false-positive trap table
(`.claude/skills/handoff-audit/references/scan-playbook.md` §4). Report
maintainability separately from measured runtime cost. Whole-repo
dead-code sweeps → defer to `handoff-audit`.

## 4. Model-call census seed (Phase 5)

Rows to re-verify, then document per the report-templates fields:

| Activity | Site | Model source | Blocks reply? |
|---|---|---|---|
| Primary chat (stream + JSON) | `api/llm/chat.ts` | `AI_CHAT_MODEL` (+ `AI_CHAT_FALLBACK_MODEL`) | yes — is the reply |
| Simple-routing downgrade (short toolless turns) | `api/llm/chat.ts` | `AI_LABEL_MODEL` | yes |
| Backchannel first-beat ack | `src/lib/ai/backchannel.ts` | backchannel runtime config | parallel first beat |
| Safety classifiers (crisis / injection / scope) | `src/lib/ai/safety/classifiers/shared.ts` | `AI_LABEL_MODEL` | yes — gates stream |
| Graph state classifier (~900ms timeout) | `src/lib/ai/state/classifier.ts` | chat model | yes, when enabled |
| Guidance-retrieval embeddings | `src/lib/ai/embeddings/gateway.ts` | `AI_EMBEDDING_MODEL` (non-ZDR) | yes (LRU-cached) |
| Conversation-summary refresh | `src/lib/ai/state/context.ts` | `AI_MEMORY_REFRESH_MODEL` | blocking variant only |
| Conversation titling (live + cron backstop) | `src/lib/ai/state/conversationLabel.ts`, `api/cron/title-unnamed-conversations.ts` | `AI_LABEL_MODEL` | no |
| Tone canary (sampled judge) | `src/lib/ai/toneCanary.ts` | `AI_MEMORY_REFRESH_MODEL` | no |
| Themes / summary endpoint | `api/llm/summarize.ts` | `AI_THEMES_MODEL` / `AI_SUMMARY_MODEL` | no |
| Web-search summarization | `api/llm/search-summarize.ts` | `AI_SUMMARY_MODEL` | tool path |
| Plan generation | `api/_lib/plans/generator.ts` | `AI_PLAN_MODEL` | tool/route |
| Sleep stories | `api/sleep.ts` | chat model | route |
| Memory promotion (daily cron) | `src/lib/ai/state/promoteUserMemory.ts` | `AI_MEMORY_PROMOTION_MODEL` | no |
| Weekly pattern check (cron) | `src/lib/ai/state/promoteWeeklyPatternCheck.ts` | `AI_WEEKLY_PATTERN_CHECK_MODEL` | no |
| Eval subject + judge | `src/lib/ai/evals/runner.ts` via `api/cron/drain-eval-runs.ts` | subject + `AI_EVAL_JUDGE_MODEL` (non-ZDR) | no |
| Admin prompt assistant / caretaker / transcript judge | `api/admin/prompt-assistant.ts`, `api/admin/caretaker.ts`, `api/admin/runtime-config.ts` | `AI_PROMPT_EDITOR_MODEL`, `AI_TRANSCRIPT_JUDGE_MODEL` | no (admin) |
| Model trials | `src/lib/ai/models/runModelTrial.ts` | trial-specified | no (admin) |

Defaults at verification time: chat `anthropic/claude-sonnet-4.6`;
background tasks `anthropic/claude-haiku-4-5`; embeddings
`openai/text-embedding-3-small`. All admin-tunable via `runtime_config` —
read the live values, do not assume.

## 5. The optimization ladder (Phase 8 priority order)

Unless evidence argues otherwise, generate and rank experiments in this
order:

1. Eliminate work producing no user or governance value.
2. Prevent unnecessary invocation of conditional activities.
3. Remove duplicate queries, model calls, transformations, prompt content.
4. Increase prompt-cache reuse (ordering, TTLs, digest churn).
5. Parallelize independent blocking work.
6. Move safe non-interactive work off the user-visible path.
7. Reduce unnecessary output length (`max_output_tokens`, verbosity).
8. Replace bounded model activities with deterministic logic.
9. Route narrowly-defined low-risk activities to smaller models.
10. Change the primary conversational model — only after 1–9 are
    exhausted, and via the model-trial harness, never a config flip.

## 6. Prohibited shortcuts

Do not:

- Globally replace the primary conversational model on price or generic
  benchmarks.
- Remove, combine, reorder, or weaken safety checks based on average-case
  traffic.
- Truncate conversation context without evaluating long-horizon coherence,
  memory accuracy, repair moments, and safety-sensitive cases.
- Recommend semantic response caching for emotionally sensitive
  user-facing replies without an explicit safety and personalization
  analysis (and never as a default).
- Add an agent framework merely to reorganize existing orchestration, or a
  new observability vendor when turn metrics + Langfuse can answer the
  question.
- Treat a lower average eval score as acceptable because cost declined —
  non-inferiority is judged per archetype and on safety-critical cases.
- Modify prompt or harness text outside /change-pass + /eval-changeset.
- Optimize the median while ignoring p95/p99 or the top-cost
  conversations.
- Move telemetry or persistence off the response path when that loses
  audit evidence or creates inconsistent state.
- Re-propose an item from `do-not-optimize.md` without new evidence that
  meets its recorded revisit condition.
