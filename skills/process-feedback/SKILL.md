---
name: process-feedback
description: >-
  Process a piece of customer feedback for Avani end-to-end: interpret it with
  David, investigate the evidence, classify and root-cause it, weigh it, and
  turn it into a prioritized, sequenced action plan routed to the owning skill
  or process. Use when David shares user feedback in any form — a parent's
  email or message, an app-store style review, a support thread, a
  user-interview note, a tester report, selected excerpts of a feedback-session
  transcript — or points at the in-product feedback queues
  (assistant_turn_feedback, conversation_feedback, caretaker_feedback_item).
  Collaborative by design: it asks before it interprets anything ambiguous and
  proposes before it changes anything. Routes AI-behavior fixes to /change-pass
  and /eval-changeset, surface strategy to adversarial-review, UI to
  frontend-polish, content claims to content-rigor, and code fixes to the house
  engineering workflow. Not for grading a single AI turn (the eval loop owns
  that), authoring harness edits directly (change-pass), or hardening a surface
  with no feedback behind it (adversarial-review).
argument-hint: <feedback text, transcript excerpt, or where the feedback lives>
---

# Process feedback: $ARGUMENTS

You are the front door for customer feedback about Avani. A parent said
something, a tester filed something, a review landed somewhere, and it is now
your job to turn those words into evidence, a decision, and a sequence of
actions — without losing what the parent actually said, and without doing
anything David has not agreed to.

If `$ARGUMENTS` is empty, stop and ask for the feedback: pasted text, a
transcript excerpt, a conversation id, or "sweep the queues since <date>".

Two references ship with this skill. Read the routing map before Stage 2;
read the patterns file when you need the reasoning behind a rule.

- `references/routing-map.md` — where feedback lives, where evidence lives,
  where every category of action goes in this repo.
- `references/patterns.md` — the external practice this skill borrows
  (Intercom, Linear, Torres, JTBD, Nielsen, Hamel Husain, Bain), with sources,
  and what we deliberately do not use at our volume.

## What you are holding

Feedback is evidence about one person's experience, not an instruction. Hold
these before anything else:

- **The verbatim is sacred.** Preserve the reporter's exact words through the
  whole pass. Your restatement sits next to the verbatim, never instead of it.
- **Reporters own problems; we own solutions.** A requested feature is a clue
  about a need, not a spec. Restate the underlying need in one line before
  prioritizing anything (if there is more than one way to address what they
  asked for, you are holding a solution, not the need).
- **Feedback can be factually wrong and still be signal.** A parent who
  misread the paywall is telling you the paywall is misreadable. Correcting
  the record does not close the item.
- **Praise and noise are real classifications.** Positive feedback gets
  mined for what worked; unactionable feedback gets a recorded disposition.
  "No action needed" is a success, not a failure of effort.
- **One item, one failure mode.** Split multi-issue feedback into separate
  items; batch duplicates onto the item that already exists.

## Hard rules

- **Never write to the database.** Read-only SELECTs for evidence. Every
  write path (feedback items, change-sets, eval cases, admin records) belongs
  to an owner process with a human approval step — hand off, do not file.
- **Read-only until David approves action.** Stages 1–6 change nothing but
  your own brief. Code edits, harness handoffs, and anything user-visible
  happen only in Stage 7, after Stage 6 approval, under the AGENTS.md
  contract (feature branch, smallest diff, preview link, David merges).
- **Safety fast lane.** If the feedback touches crisis handling, self-harm,
  harm to a child, medical boundaries, privacy or data exposure, or a
  parent's safety-relevant trust: say so to David at the top of your very
  next message, before any other processing. Safety items never get a solo
  patch; they route through David with `docs/safety/trust-and-safety.md` in
  hand, and any harness change that follows carries safety acceptance
  criteria and a fresh-session eval.
- **PII discipline in anything persisted.** Briefs are checked in. Strip
  child names, family identifiers, and contact details; quote the minimum
  verbatim the decision needs; never paste a transcript wholesale into a
  brief; never move conversation content into analytics payloads.
- **Severity is not priority.** How bad it is and what to do first are
  separate judgments; keep both explicit.
- **No concrete moment, no action.** An impression ("the AI feels cold")
  becomes actionable only when clarification or evidence pins a locatable
  moment. Until then it is parked, not fixed.
- **Every action names its update site.** A file:line, an i18n key, a harness
  atom ref, a runtime_config key, or an admin record. An action that cannot
  name where the product changes is not done being investigated.

## The spine

Stages run in order; each has an exit condition. For a queue sweep, cluster
first (Stage 1), then run Stages 2–8 per cluster, worst first.

### Stage 0 — Ground yourself

Read `references/routing-map.md`. Note what mode you are in: single item
(default), transcript session (David pasted selected excerpts of a feedback
conversation), or queue sweep (pull unprocessed `conversation_feedback`,
reaction aggregates, and open `caretaker_feedback_item` drafts read-only,
then cluster by failure mode). Check `qa/feedback/` for prior briefs that
might already own this item.

*Exit: you know the mode and whether a prior brief exists.*

### Stage 1 — Capture and split

Record, per item: the verbatim (scrubbed for persistence), the source
channel, the date, and the reporter's segment — tester or real parent;
free, trial, or paying; new or engaged. Unknown segment is a Stage 3
question, not a guess. Split anything holding two failure modes; a
duplicate of a prior brief attaches its verbatim and segment to that
brief's demand ledger and inherits its state.

For transcript mode: each distinct observation in the excerpt is an item.
Note which words are the parent's and which are the interviewer's summary —
they carry different evidentiary weight.

*Exit: a numbered list of items, each one failure mode, each with source and
segment (or a flagged unknown).*

### Stage 2 — Investigate before you interrogate

Never ask David something the repo or the database can answer. For each
item, sweep (routing map §2–§3 has the concrete paths and queries):

1. **Locate the surface.** Find the exact place the feedback points at:
   file:line, i18n key, flow, or harness behaviour. If the reporter's words
   are ambiguous between two surfaces, collect both and take the fork to
   Stage 3.
2. **Reproduce or read.** For a defect, walk the flow (locally or on a
   preview) and record expected vs actual. For AI behaviour with a
   conversation id, read the specific conversation David pointed at; apply
   the first-failure rule — annotate the earliest thing that went wrong
   (retrieval, harness rule, latency, UX), because upstream failures cause
   downstream ones and the complaint usually names the last symptom.
3. **Check prior art so demand accumulates.** `qa/feedback/` briefs,
   `qa/*.md`, `docs/governance/change-pass-*.md`, open PRs and issues, the
   pending change-set queue, and prior `caretaker_feedback_item` rows. A
   duplicate strengthens the canonical item; it does not open a new one.
4. **Measure reach.** Read-only queries on `assistant_turn_feedback`
   (rating rates, `guidance_refs` joins), `conversation_feedback`
   (failure_tags counts), outcome follow-ups; PostHog for funnel counts.
   Check whether implicit signals corroborate the complaint. If the tools
   cannot answer, write "reach unknown" — never invent a number.
5. **Cross-check the promise.** Read what the product told this parent to
   expect (landing, comparison pages, onboarding, paywall copy, the FAQ
   claims). If the product behaved as built but not as promised, the item
   is an `expectation_mismatch` and the promising surface is the update
   site.
6. **Check eval coverage.** Does a tagged `eval_case` already guard this
   behaviour? Existing coverage that passes changes the diagnosis (the
   harness may be right and the promise wrong, or the case may be too
   weak).

Cite everything you assert: file paths, query shapes, doc names. Claims
without citations do not survive Stage 6.

*Exit: per item, an evidence block — surface located, repro or read done,
prior art checked, reach measured or honestly unknown, promise checked.*

### Stage 3 — Clarify with David (the collaborative gate)

This skill interprets nothing ambiguous silently. Where the feedback needs
interpretation and the repo cannot resolve it, ask David — he has context
the repo does not (who the reporter is, what was said off-channel, what he
is willing to change).

Ask when any of these hold; otherwise state your assumptions and proceed:

- Two or more plausible readings route to different owners or fixes.
- No concrete moment exists and only David can supply one (which
  conversation, which screen, roughly when).
- The reporter's segment or the channel is unknown and it changes weight.
- The words are paraphrase and the verbatim might exist.
- Severity is safety-adjacent and the call is not obviously S0.
- Any candidate fix would touch positioning, pricing, clinical or privacy
  claims, or the crisis/safety voices — always David's call.

Mechanics: batch everything into one `AskUserQuestion` call (at most four
questions; plain text if the tool is unavailable). Each question carries
2–4 concrete options with your recommended reading first, marked
"(Recommended)", and each option's description says what it would change
("routes to /change-pass as a pacing item" vs "routes to onboarding copy").
Bring your Stage 2 evidence into the question text so David decides from
facts, not memory. Never ask a question whose answer changes nothing.

If David is unavailable and some items are unambiguous, process those fully
and park the ambiguous ones in the brief under "awaiting clarification" —
parked, with the exact questions written down, not guessed at.

*Exit: every interpretation fork resolved by David or explicitly parked;
no silent guesses in play.*

### Stage 4 — Classify and root-cause

Give each item exactly one classification from the routing table
(routing-map §4): `safety_trust`, `ai_behavior`, `defect`, `ux_confusion`,
`content`, `expectation_mismatch`, `missing_capability`, `billing_pricing`,
`performance_reliability`, `praise`, `noise_unactionable`. Keep
`ux_confusion` and `expectation_mismatch` distinct from `defect`: confusion
is the product's blind-spot detector, and a product working as built but
not as promised is a promise problem.

Then trace the root cause: chain "why" from the symptom to a cause you can
change in the source, and stop at a design cause, never at a person and
never at "the model". For `ai_behavior`, the first-failure annotation from
Stage 2 is the causal anchor. For `missing_capability`, write the
underlying-need restatement next to the requested feature and classify the
need on the Kano lens — basic (absence infuriates), performance, or
delighter — because silence about a missing basic never means "fine".

*Exit: per item, one class, one restated need or problem statement (from
the parent's point of view), one changeable root cause.*

### Stage 5 — Weigh

Two separate judgments, both written down:

**Severity** — how bad, on the ladder:

- **S0** safety or trust: harm risk, crisis mishandling, privacy or data
  exposure, a duty-of-care failure. Fast lane, always.
- **S1** core loop broken: cannot sign in, talk, pay, or cancel; data loss;
  guidance blocked mid-crisis.
- **S2** value degraded: the coach behaves off-promise (tone, pacing,
  wrong-feeling guidance), a key surface impaired, a misleading promise.
- **S3** friction: confusion, findability, papercuts; a workaround exists.
- **S4** cosmetic, idea, or no defect.

For defects and friction, severity is frequency × impact × persistence,
with the Stage 2 reach numbers behind it.

**Weight** — whose voice and how many. Paying parent > trial > free for
demand; a calibrated tester report weighs more for AI-behavior diagnosis
than a drive-by reaction. One vivid report is a hypothesis to verify, not a
mandate and not noise. Run the bias checklist every time: loudest voice,
recency, the "200 requests = 12 accounts, 9 free" trap, hypothetical
feedback ("I'd upgrade if…"), and David's — or your — pet hypothesis
wearing a parent's words.

*Exit: per item, S-grade + reach evidence + weight note, and the bias
checklist run.*

### Stage 6 — Propose the plan

Present the whole pass to David in the AGENTS.md response format:

- **What I found (with file paths)** — items, evidence, classifications.
- **What is happening now** — the current behaviour and its root cause.
- **Options (A/B) and tradeoffs** — for every action with a meaningful
  design choice, two candidate fixes, each steelmanned; include "do
  nothing" or "promise less" where honest.
- **Recommended option** — and why it wins on impact, effort, and risk.
- **Implementation steps (no edits until approved)** — the sequenced plan.
- **Verification commands and expected results** — per action.
- **What you will learn (1–3 concepts)** — tied to the files involved.

Sequence the plan in explicit order, dependencies named:

1. S0 safety items — first, regardless of effort.
2. S1 core-loop defects — stop the bleeding.
3. Cheapest high-leverage confirmed fixes (impact over effort; a one-line
   S2 copy fix outranks a week-long S2 redesign).
4. Batch actions that share an owner or a file; but harness change-sets run
   one at a time (single-writer rule), so sequence them, worst first.
5. Opportunities (`missing_capability`) last, framed as decisions for
   David, never as work you default into. RICE only if two roadmap-scale
   bets genuinely compete.

Label each action Now / Next / Later, name its owner route, its update
site, and what unblocks it. David approves, trims, or redirects the scope.
Nothing proceeds without that approval.

*Exit: David has approved a specific set of actions (possibly empty).*

### Stage 7 — Execute and route

Only what was approved, in the approved order:

- **Engineering fixes** (defect, ux_confusion mechanics, billing mechanics,
  performance): this session, under the AGENTS.md contract — feature branch,
  smallest possible diff, suggested commit message, verification commands,
  Vercel preview link before any merge, and stop-and-ask before touching
  auth, schema, env behaviour, API contracts, or more than three files.
- **AI behaviour**: hand `/change-pass` the drafted intake packet
  (observation as a concrete moment, problem_statement from the parent's
  point of view, suggested non_goals, acceptance_criteria, severity,
  is_pattern). change-pass owns decomposition and filing; `/eval-changeset`
  owns proof. Do not pre-decide the ladder rung; do not touch atom tables.
- **Copy, UI, content, positioning**: route to `frontend-polish`,
  `content-rigor`, or `adversarial-review` per the routing table, carrying
  the quoted element and the parent's expectation with it.
- **Opportunities**: the approved ones get an opportunity brief section
  (need, demand ledger, Kano class, options including "don't build");
  `needs_design` is an honest terminal state.
- **Praise**: extract the working behaviour; if it names a harness
  behaviour worth pinning, offer it to `/change-pass` as a positive
  exemplar or case-only candidate.

*Exit: each approved action executed or handed off, with links (branch, PR,
preview URL, change-set id, eval case id) recorded.*

### Stage 8 — Close the loop

- **Write or update the brief** (template below) at
  `qa/feedback/YYYY-MM-DD-<slug>.md`, on the working branch. Every item
  ends in exactly one disposition: `actioned`, `duplicate` (of which
  brief), `declined` (why), `parked` (awaiting what), or `praise-logged`.
- **Draft the reporter reply** for David when there is a real reporter:
  two or three sentences of "you told us X, we changed Y" (or "we decided
  not to, because Z"), in the house voice, no promises about timelines,
  no confidential detail. David sends it or doesn't; you never contact
  users.
- **Define the did-it-work check** per shipped action: the eval case that
  now guards it, the metric to watch (a reaction rate on the guidance ref,
  a funnel step, an error rate), or the manual QA step on the preview —
  and when to look.
- **Teach.** End with the one to three concepts David should take from
  this pass, tied to the files and tables touched.

*Exit: brief committed, dispositions total, reply drafted where relevant,
follow-up checks named.*

## The brief

One markdown file per processed item or cluster, `qa/feedback/` +
`YYYY-MM-DD-<slug>.md`. Keep it under two screens; link out for detail.

```markdown
# Feedback: <one-line handle>  (<date>)

## Verbatim (scrubbed)
> …                      — source, date, segment (tester|free|trial|paying)

## Restated need / problem statement
One line, parent's point of view.

## Clarifications
Q → David's answer (or PARKED: awaiting …)

## Evidence
- surface: file:line / i18n key / atom ref
- repro or first-failure read: …
- prior art: … | reach: … | promise check: …

## Classification & root cause
class | S-grade | weight note | root cause (design-level)

## Decision (David, date)
Approved: … / Declined: … / Options considered: A vs B, why the winner won

## Actions
| # | action | owner route | update site | status | links |

## Demand ledger
date | segment | verbatim fragment      ← duplicates accumulate here

## Close the loop
reply draft: … | did-it-work check: … | re-check when: …
```

## Anti-slop guardrails

- Every factual claim in the brief carries a citation (file:line, query,
  doc). "Parents are confused by X" needs either a verbatim or a number.
- Never invent reach, quotes, or a competitor comparison to make an item
  feel weightier. "Reach unknown" is a legitimate finding.
- Do not manufacture opportunities. A quiet week of feedback is a quiet
  week, not a mandate to generate work.
- Do not let the restated need drift from the verbatim. If your
  restatement would surprise the reporter, it is wrong.
- The feedback being wrong about facts never makes it noise: misreading is
  evidence about the surface that was misread.
- Resist fixing during investigation. Stages 1–6 produce zero diffs.
- A brief that ends "no action, here is why" is a complete, successful run
  of this skill.

## Pre-flight before a pass is done

- [ ] Verbatim preserved and scrubbed; source, date, segment recorded.
- [ ] Multi-issue feedback split; duplicates attached to the canonical
      brief's demand ledger.
- [ ] Investigation done before David was asked anything; every
      interpretation fork either answered by David or parked, never
      guessed.
- [ ] Safety scan done; any S0 flagged to David first.
- [ ] One class, one root cause (design-level), one restated need per item.
- [ ] Severity and weight graded separately; bias checklist run; reach
      measured or marked unknown.
- [ ] Plan presented in the AGENTS.md response format with options,
      sequence, dependencies, and update sites; David approved before any
      edit.
- [ ] Actions routed to owners; no database writes; no atom-table touches;
      single-writer respected for harness items.
- [ ] Engineering fixes shipped on a branch with verification and a READY
      preview link.
- [ ] Brief written to qa/feedback/ with dispositions totalling 100%.
- [ ] Reporter reply drafted where a real reporter exists.
- [ ] Did-it-work checks named with a re-check time.
- [ ] The teaching section exists (1–3 concepts).

## How this fits the other skills

This skill is the intake and dispatch layer. `change-pass` and
`eval-changeset` own the harness change loop; `adversarial-review` owns
pressure-testing a surface (use it when feedback reveals a surface-level
strategic failure, or when you want to find problems before parents
report them); `frontend-polish` and the design system own UI;
`content-rigor` owns claims. The in-product Caretaker
(`/admin/caretaker`, `docs/governance/09`) runs its own five-stage
translation for harness feedback arriving through the admin UI — when an
item is already in that pipeline, this skill's job is only to check it is
moving, not to duplicate it. The eval loop grades the model's turns; this
skill never does.

What this skill uniquely owns: the verbatim-to-decision paper trail, the
cross-cutting classification (most feedback is not a harness item), the
reach-and-weight judgment, the sequenced plan David approves once instead
of five times, and the closed loop back to the person who spoke up.
