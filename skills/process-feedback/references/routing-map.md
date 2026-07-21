# Routing map — where feedback lives, where evidence lives, where action goes

Repo-grounded reference for the `process-feedback` skill. Everything here is a
pointer, not policy; the owning docs stay canonical. If a path here disagrees
with the repo, trust the repo and fix this map in the same PR.

## 1. The channels feedback arrives from

| Channel | Where it lives | What it holds |
|---|---|---|
| Inline turn reactions | `assistant_turn_feedback` (written by `src/components/satsang/MessageFeedback.tsx`, `source: 'inline'`) | lands / unsure / missed (plus `made_worse` from the outcome loop), optional note, and a `guidance_refs` blob joining the reaction back to the scripts / moments / KB chunks / prompt version that produced the turn (see `supabase/migrations/20260901120013_outcome_feedback.sql`) |
| Async outcome follow-ups | `pending_followup` rows scheduled by cron; card on `/home` asks 12–24h later how the guidance went | the "did it actually work with your kid" signal, the highest-value implicit outcome data we capture |
| Tester end-of-chat reviews | `conversation_feedback` (testers/admins only; reviewed at `/admin/quality/feedback`) | verdict (pass / needs_work / fail), `failure_tags[]` mapping 1:1 to eval dimensions, expected / actual ground-truth pair, `red_flags[]`, what_worked, suggested_change (see `supabase/migrations/20261113120000_conversation_feedback.sql`) |
| Caretaker feedback intake | `caretaker_feedback_item` + the queue at `/admin/caretaker/feedback` | observation, problem_statement, is_pattern, non_goals, acceptance_criteria, severity; status draft / escalated / accepted / declined / needs_design (see `docs/governance/09-caretaker-change-loop-operator-guide.md`) |
| Eval reviewer feedback | `eval_case_review` via the admin Evals → Review tab; exported by `src/lib/admin/evalFeedbackExport.ts` | Mirra's per-case verdicts (looks_right / suggest_shift) with plain-English notes |
| External, unstructured | David pastes it: a parent's email or DM, an app-store style review, a support thread, a user-interview or feedback-session transcript | verbatim words from a real reporter; capture source, date, and segment at intake |

## 2. Evidence sources for investigation (read-only)

- **Production database**: Supabase project `Satsang`, ref `facgwtempyxekghnpxth`.
  Read-only SELECTs only. Useful reach queries:
  - reaction rates by guidance ref: `assistant_turn_feedback` grouped by `rating`, joined through `guidance_refs`
  - failure clusters: `conversation_feedback` grouped by unnested `failure_tags`
  - duplicate check: `caretaker_feedback_item` and `harness_change_set` for
    pending or prior items touching the same behaviour (also the single-writer
    preflight in `docs/governance/CHANGE-PASS-SPEC.md` Stage 0)
  - eval coverage: `eval_case` tags (`state_slug`, `harness_refs`,
    `principle_refs`, dimension tags) for whether a case already guards the
    behaviour
- **Analytics**: the event catalog is `src/lib/analytics/events.ts`
  (`ANALYTICS_EVENTS`); server events flow through `src/lib/posthog-server.ts`.
  Payloads never contain conversation content, so PostHog answers "how many,
  which funnel step", never "what was said". Quarterly reconciliation script
  and PostHog project id live in `AGENTS.md`.
- **Runtime health**: Vercel MCP tools (`get_runtime_errors`,
  `get_runtime_logs`, `get_deployment_build_logs`) for
  performance / reliability complaints; `src/lib/ai/safety/turnMetrics.ts`
  for latency and token telemetry.
- **Prior art, so demand accumulates instead of fragmenting**: `qa/*.md`
  (dated critiques and sweeps), `qa/feedback/` (briefs this skill wrote),
  `docs/governance/change-pass-*.md` (every harness change already tried),
  `docs/history/qa-findings.md`, open PRs and issues on
  `dmeehan45/satsang-dev`, and the pending change-set queue.
- **The product's own promises** (for expectation-mismatch checks): marketing
  copy resolves through `src/lib/i18n/keys.ts` and the locale catalogs under
  `src/lib/i18n/translations/`; the offer has no single source of truth and
  its mirrors are enumerated in the adversarial-review skill §3 and §8; the
  prerendered claims live in `scripts/prerender-articles.mjs`.

## 3. Surface map — where "parts of the product" live

| Surface a parent names | Source |
|---|---|
| Landing / marketing story | `src/pages/LandingPage.tsx`, `/about`, `/approach`, comparison pages (`HowDifferentFromChatGPTPage`, `HowDifferentFromGoodInsidePage`), copy in `src/lib/i18n/keys.ts` |
| Quiz funnel | `src/pages/quiz/` |
| Onboarding | `OnboardingIntroPage.tsx`, `src/features/onboarding/` |
| Paywall, pricing, upgrade | `src/paywall/` (`config.ts`, `entitlements.ts`), `src/components/satsang/UpgradeSheet.tsx`, `api/billing.ts`, Stripe webhook, `runtime_config` quota/trial values |
| Home | `src/pages/SatsangHomePage.tsx` (follow-up cards, memory snapshot) |
| Talk (the conversation) | `src/pages/TalkPage.tsx`, `src/hooks/useConversationController.ts`, and the AI stack under `src/lib/ai/` (harness, safety, state graph, tools) |
| What the coach actually says | not code: the harness atoms (prompt template, voice profiles, principles, exemplars) governed by the change-pass loop |
| Tools / Calm / Sleep / Meditation | `ToolsPage.tsx`, `MeditationPage.tsx`, `SleepPage.tsx`, `src/features/regulation/`, `src/features/sleep/` |
| Plans | `PlansPage.tsx`, `PlanCreatePage.tsx`, `PlanDetailPage.tsx`, `PlanShareViewPage.tsx` |
| Reflections / You / Profile | `ReflectionsPage.tsx`, `src/pages/you/`, `ProfilePage.tsx` |
| Saved / Library | `SavedPage.tsx`, `SavedSectionPage.tsx`, `src/features/library/` |
| Articles / Moments / Glossary | `ArticlePage.tsx`, `MomentDetailPage.tsx`, `GlossaryPage.tsx`, content pipeline in `scripts/prerender-articles.mjs` |
| Community / Refer | `CommunityPage.tsx`, `ReferAFriendPage.tsx` |
| Emails, community prompts, eval cases | admin records, changed via the Caretaker's Path B queue (`/admin/caretaker/changes`), never edited live by an assistant |

## 4. Category → owner routing table

| Classification | Route | Handoff shape |
|---|---|---|
| `safety_trust` | David, immediately and first, with `docs/safety/trust-and-safety.md` in hand. Never a solo patch. | plain statement of what was reported, what the evidence shows, and the options; any harness fix that follows carries safety acceptance criteria and a fresh-session eval |
| `ai_behavior` | `/change-pass` (then `/eval-changeset`) | a drafted intake packet: observation (concrete moment), problem_statement (parent's POV), suggested non_goals, acceptance_criteria, severity, is_pattern. change-pass owns decomposition; do not pre-decide the ladder rung |
| `defect` | engineering fix in-session under the AGENTS.md contract | repro steps, expected vs actual, the owning file:line, severity (frequency × impact × persistence), smallest diff, verification commands, preview link |
| `ux_confusion` | copy/flow fix via `frontend-polish` + `docs/satsang-design-system.md`; if the confusion is about what the product *is*, escalate to `adversarial-review` | the confused element quoted with file:line (or i18n key), what the parent expected it to mean |
| `content` | `content-rigor` (write or review mode) | the claim or passage, why it failed the reader, sourcing requirement |
| `expectation_mismatch` | fix the promise or the product, David chooses; `adversarial-review` owns the internal-incongruence framing; offer changes must update every mirror in one commit | the promising surface quoted with file:line vs the actual behaviour with its source |
| `missing_capability` | opportunity brief for David's roadmap decision; `needs_design` is an honest answer | restated underlying need (never the requested feature verbatim), demand evidence, Kano lens, options including "don't build" |
| `billing_pricing` | engineering fix for mechanics; David for anything touching price, value framing, or the offer | same as defect, plus the offer-mirror checklist |
| `performance_reliability` | engineering fix informed by Vercel logs and turn metrics | the measured number (latency, error rate), not the adjective |
| `praise` | close the loop; extract what worked; candidate positive exemplar or eval case via `/change-pass` | the working behaviour, named, with its guidance ref if the join exists |
| `noise_unactionable` | record disposition and reason in the brief; no action | one line: why no action, so the next duplicate lands here instead of reopening |

## 5. Hard boundaries this map inherits

- The assistant never writes a live harness atom, a live admin record, or any
  production row. Reads are fine; every write path goes through an owner
  process with a human approval step (`docs/governance/09` — "The Caretaker
  never writes a live surface", and the same discipline holds here).
- One pending harness change-set at a time (single-writer, CHANGE-PASS-SPEC
  Stage 0). Feedback that fans out into several harness edits is sequenced,
  not parallelized.
- Preview-before-merge is non-negotiable for any code fix (`AGENTS.md`).
- Anything that changes auth, schema, build tooling, env behaviour, API
  contracts, or more than three files: stop and ask David first (`AGENTS.md`).
