# Patterns — how strong teams process feedback, and what this skill borrows

Distilled from primary sources (researched 2026-07). Each entry: the pattern,
where it comes from, and how it applies at the app's scale — a two-person team,
low dozens of feedback items a week, one accountable reviewer (the maintainer), and
eval machinery that already exists. The skill's spine encodes these; this file
is the why behind the spine.

## Intake and normalization

**Feedback river → system of record** (Sachin Rekhi,
sachinrekhi.com/designing-your-products-continuous-feedback-loop). Keep one
place where raw feedback flows in, and one deduplicated record you actually
prioritize from. Teams that skip the second step end up prioritizing from
memory. Here: the in-product tables are the river; the briefs in
`qa/feedback/` are the system of record for external items and decisions.

**Small fixed tagging taxonomy** (Intercom,
intercom.com/help/en/articles/6604447). Tag at intake into a stable, small
set: bug, product confusion, feature request, churn risk. "Product confusion"
is deliberately distinct from bugs — it is the blind-spot detector. Here: the
eleven-class taxonomy in the skill, with `ux_confusion` and
`expectation_mismatch` kept separate from `defect` for exactly this reason.
Resist inventing new tags; tag entropy kills searchability.

**Forced disposition, dedupe by attachment** (Linear method,
linear.app/docs/triage). Every triaged item gets one of: accept, duplicate,
decline, snooze — nothing rots unreviewed. Duplicates attach the new
reporter's verbatim to the canonical item, so demand accumulates and counting
is free. Here: every processed item ends with a disposition in its brief, and
a duplicate updates the existing brief's demand ledger instead of opening a
new one.

## Interpretation and investigation

**Extract the problem, not the proposed solution** (Intercom "5 mistakes we
all make with product feedback"; Teresa Torres,
producttalk.org/opportunity-solution-trees). Users report solutions ("add a
simpler form") when the pain is something else (repetition). Torres's test:
if there is more than one way to address it, you are holding a solution, not
the need. Practice: record the verbatim, then restate the underlying need in
one line before anything is prioritized. Both lines go in the brief.

**JTBD and the four forces** (Bob Moesta, jobstobedone.org). For
acquisition, upgrade, and churn feedback, reconstruct the switch: push of the
old way + pull of the new vs anxiety of the new + habit of the old. A parent
saying "I went back to ChatGPT" is a four-forces interview waiting to happen,
not a feature gap statement.

**Five whys to a changeable cause** (Taiichi Ohno via Eric Ries,
startuplessonslearned.com). Chain why from symptom to a process or design
cause you can change; stop at a design cause, never at a person. For a single
feature request the lighter "what problem are you solving" probe suffices.

## Prioritization

**Severity = frequency × impact × persistence** (Nielsen, NN/g,
nngroup.com/articles/how-to-rate-the-severity-of-usability-problems). The
bug-and-friction lane's whole prioritization at our volume. Encoded as the
S0–S4 ladder in the skill.

**Weigh, don't count** (Des Traynor / Intercom; Enterpret's "200 requests =
12 accounts, 9 on free plans" trap). Feedback is noise until segmented: who
said it, on what plan, how engaged, how many distinct reporters. Every
counted item in a brief carries segment metadata. Named failure modes to
check against every time: loudest voice, recency bias, hypothetical feedback
("I'd upgrade if…"), and the builder's own pet hypothesis.

**RICE, sparingly** (Sean McBride, Intercom,
intercom.com/blog/rice-simple-prioritization-for-product-managers). Reach ×
Impact × Confidence ÷ Effort, with Confidence as the bias brake. At low
dozens a week, RICE on individual items is false precision; reserve it for
comparing genuine roadmap-scale bets. Deliberately not this skill's default.

**Kano as a lens, not a survey** (Noriaki Kano, 1984). Basics infuriate by
absence; performance scales linearly; delighters surprise. The sample is far
too small to survey, but the qualitative question "is this a basic, a
performance dimension, or a delighter" catches what RICE is blind to:
feedback silence about a missing basic does not mean "fine".

**Cost of delay** (Reinertsen; blackswanfarming.com/cost-of-delay). Use when
sequencing, not selecting: an urgency claim should survive arithmetic. Mostly
relevant here when a fix blocks trust (safety, billing) rather than revenue.

## Closing the loop

**Inner loop / outer loop** (Bain, Net Promoter System,
bain.com/insights/the-net-promoter-systems-inner-loop). Answer the person
(inner) and fix the pattern (outer); leaders read verbatims, not summaries.
At the app's volume the inner loop is personal: a direct "you told us X, we
changed Y" note from the maintainer to each reporter. Canny and Linear automate this
at scale (canny.io/blog/canny-changelog); we do it by hand because we can,
and because for a parent who flagged an AI-behavior concern it is the
single cheapest trust lever the product owns. The skill drafts the note;
the maintainer sends it or doesn't.

## AI-product practice

**Error analysis first: open coding → taxonomy → counts** (Hamel Husain,
hamel.dev/blog/posts/evals-faq and /field-guide). The highest-ROI activity
in LLM product work is a domain expert reading real traces and annotating
the FIRST failure in each (upstream failures cause downstream ones — the
first-failure rule is also how a "bad answer" complaint gets attributed to
retrieval vs harness vs model vs latency vs UX). Group notes into a failure
taxonomy with counts; build evaluators only for failure modes that persist.
One "benevolent dictator" annotator beats a committee at small scale. Here:
the conversation_feedback failure_tags already map 1:1 to eval dimensions;
this skill's investigation stage applies first-failure reading to any
transcript excerpt the maintainer shares.

**Complaint → eval case → regression suite** (Hamel; LangSmith,
langchain.com/resources/llm-evals). Every confirmed AI-behavior failure
becomes a tagged case in the existing eval set before any fix is authored —
which is exactly CHANGE-PASS-SPEC Stage 2 ("the eval case comes first", and
case-only is a success). This skill never shortcuts that: it hands the
packet to `/change-pass` rather than proposing harness edits itself.

**Don't rely on complaints alone** (Hamel; Chip Huyen, *AI Engineering*).
Explicit thumbs are sparse and biased. Implicit negatives — regeneration,
early exits, "no, I meant…", deletions — plus the outcome follow-ups pick up
what complaints miss. When a complaint arrives, check whether the implicit
signals corroborate it before weighing reach.

**Privacy-preserving pattern mining** (Anthropic Clio,
anthropic.com/research/clio). The reference architecture for reading
patterns without reading people. Below that volume threshold — where we are —
the discipline it encodes still binds: quote the minimum, scrub identities,
never move conversation content into analytics or checked-in docs beyond
what the decision needs.

## Deliberately not adopted at this scale

- RICE as the default ranking key (false precision at low volume)
- Kano surveys (sample too small; keep the lens, skip the instrument)
- Clio-style clustering (below the volume threshold; the eval taxonomy and
  failure_tags serve this role)
- Formal VoC program governance (one accountable owner already exists)
- Feedback-portal tooling à la Productboard/Canny (the briefs + in-product
  tables are the system of record; revisit if volume 10×es)
