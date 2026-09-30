---
name: premium-experience-review
description: >-
  Review a working consumer web or mobile product the way a master product
  designer would, against the bar of the best premium consumer software:
  considered, restrained, intuitive, coherent, emotionally appropriate, and
  polished to the interaction level. Starts from the product model and the
  user's jobs (never from visual polish), walks the real journeys in a browser
  at phone, tablet, laptop, and desktop sizes with a read-only journey walker,
  inspects interaction states, hierarchy, motion, copy, trust, accessibility,
  and perceived performance, then reads the codebase to root-cause every
  problem as a local flaw, design-system drift, or a product-model problem.
  Produces findings at three altitudes (product, experience, craft) in a
  six-field shape a coding agent can start on without asking a question,
  prioritised Foundational → Friction → Refinement → Exceptional craft, plus a
  final synthesis and a structural-before-cosmetic implementation sequence.
  Use whenever someone asks for a premium review, a product experience review,
  a design review of a running app, "does this feel premium", "review this like
  a world-class product designer", "what would make this feel like Linear /
  Apple / Stripe / Airbnb", "this feels generic, templated, or AI-generated",
  "critique the UX end to end", or wants a product designer's honest read before
  a launch, a redesign, or a fundraise — even when they only say "review the
  app" or "give me feedback on the product". Review only: it does not apply
  changes. Not the heuristic checklist audit (ux-quality-review), not the
  measured calm-score-and-tokens pass (premium-calm), not positioning and proof
  (adversarial-review), not defect triage (qa-sweep).
---

# Premium experience review

Premium is not a style. It is the feeling that every decision in the product was
made on the user's behalf before they arrived: the right capability, at the
right moment, with the right amount of interface, behaving exactly as expected,
with enough exceptional craft that the product feels unmistakably considered.
The best premium consumer products share almost no visual DNA. What they share
is intentionality.

```
premium = right capability × right moment × right amount of interface
          × expected behaviour × visible care
```

Multiplicative. A beautifully typeset screen that asks the user to configure
things the system already knows is not premium. A frictionless flow whose
success state is a generic toast is not premium. A fluid transition on a screen
that should not exist is decoration on a mistake.

This skill reviews a working product against that bar. It progresses from
product fundamentals down to interaction-level craft, and it refuses to start
with visual polish, because polish applied to the wrong product model is the
most expensive kind of waste. You have the running product **and** the
implementation. Treat the running product as the primary artifact and read the
code to learn why the experience is the way it is.

## Three rules the whole skill rests on

**Product model before pixels.** Before judging a single screen, decide who the
product is for, what situation makes them reach for it, what functional and
emotional jobs they are hiring it to do, what the shortest path to meaningful
value is, and what the recurring loop is. Every later judgement is made against
that model. Do not assume the current architecture is correct simply because it
exists; a strong review may conclude that a screen, step, setting, modal,
navigation item, or whole workflow should disappear.

**Walk it, don't imagine it.** A review written from screenshots reviews the
happy path at one viewport. Walk the journeys in a real browser at phone and
laptop sizes at least, reach the empty, error, partial, loading, and returning
states, and record what you saw. Every finding carries an evidence tier
(`Walked`, `Source`, `Screenshot`, `Reported`) so a reader knows which claims
were observed and which were inferred. Never assert a state you did not reach.

**Findings a coding agent can start on.** "Improve hierarchy", "make this
cleaner", "add polish", "improve the onboarding", "make it more premium", and
"add animations" are not findings. Every meaningful recommendation carries six
fields (observation, user consequence, underlying issue, recommended change,
premium expression, implementation surface) plus an altitude, a priority, a
root-cause class, and evidence. `scripts/check_review.py` rejects a review that
does not meet this bar.

## Phases

Work through these in order. Phases 1 to 5 gather; phase 6 writes. Do not
write findings before phase 5, because a finding written before its root cause
is known is almost always filed at the wrong altitude.

### 0. Scope and set up

Establish what is reviewable and record it in the report header:

- **Running product** — a URL, a local build, a staging environment, or a
  device build. Prefer a local or staging build for anything that commits,
  pays, deletes, or sends.
- **Implementation** — the repository, and which parts of it render the
  surfaces in scope.
- **Scope** — whole product (default), one journey, or one surface. A
  whole-product review is the standard deliverable; a narrower scope still
  runs phase 1, because a surface cannot be judged without the model.
- **Platform sizes** — phone, tablet, laptop, and large desktop where the
  product serves them. Mobile is reviewed as its own product, not as a
  compressed desktop.

Write the journey plan (`assets/journey-plan.example.json`) now. The journeys
in `references/journeys.md` are the minimum; add the product's own.

### 1. Establish the product model — `references/product-model.md`

Infer, from the product, code, copy, information architecture, and flows: the
primary user; the situation that makes them reach for it; the functional job;
the emotional job; what should be understood in the first minute; the shortest
path to meaningful value; the primary recurring loop; what would bring someone
back; what would make someone call it unusually good; which parts are central
versus incidental. Then decide what premium means for *this* product and what
must not change (brand, signature interactions, deliberate constraints).

Call out every place the product itself gives no coherent answer. Ambiguity in
the product model is a Foundational finding, not a footnote.

### 2. Walk the journeys — `references/journeys.md`

```bash
node scripts/walk_journeys.mjs --plan journeys.json --out per-evidence            # read-only sweep
node scripts/walk_journeys.mjs --plan journeys.json --out per-evidence --interact # staging or local only
```

The walker follows the plan at each viewport, captures a screenshot at every
named step, and records what a screenshot cannot show: which controls have no
visible focus or hover style, what still animates under reduced motion,
cumulative layout shift, how long the interface took to acknowledge each
action, horizontal overflow, targets under 44px on the phone, how much of the
phone viewport fixed elements occupy, unlabelled fields, the container and copy
inventory, and console and network errors. In read-only mode it stops each
journey at the first click, fill, or key press; `--interact` is for staging or
a local build with a test account, never production.

Walk at minimum: first arrival, first meaningful action, first successful
outcome, repeat use, returning after time away, changing or undoing something,
missing information, an error, an empty state, interruption and resumption, and
mobile use. For each, log friction using the taxonomy in `journeys.md`: number
of decisions, number of actions, cognitive load, unnecessary navigation, loss of
context, duplicated information, premature configuration, avoidable
confirmation, unclear state, waiting, unexpected behaviour, dead ends,
unnecessary mode switching, and places the user must remember what the system
already knows. **Fewer clicks is not the objective. Lower cognitive effort and
stronger continuity are.**

### 3. Judge surfaces and hierarchy — `references/product-model.md`, second half

For every major screen and state ask, "What is the user trying to accomplish at
this exact moment?" Then decide whether the screen is necessary, whether it
appears at the right moment, whether the most important thing carries the most
emphasis, whether anything forces the user to understand the product's internal
structure, what could be removed, combined, deferred, automated, or inferred,
whether the interface exposes features instead of facilitating the job, whether
the next action is obvious without instructional text, and whether context and
momentum survive.

Then assign every element on the surface to one of five roles: primary,
secondary, ambient, progressively disclosed, or removed. A premium surface has
one centre of gravity. Products where every feature gradually received equal
prominence fail here first, and the fix is opinion, not styling.

### 4. Apply the lenses — `references/lenses.md`

Nine lenses, each with its own checks and its own tells:

| Lens | Question |
| --- | --- |
| Interaction states | Does every control acknowledge intent immediately and proportionately, across hover, focus, pressed, selected, disabled, loading, saved, completed, destructive, error, empty, partial, asynchronous, optimistic, and interrupted states? |
| Premium craft | Is hierarchy carried by composition, spacing, typography, sequence, and interaction, or by cards, borders, pills, callouts, icons, labels, helper text, shadows, and nested containers? |
| Motion | Does motion explain where something came from, where it went, what changed, what is connected, what is waiting, what completed, and what deserves attention? Is reduced motion respected? |
| Responsive and mobile | Is mobile designed, or merely not broken? Information priority, thumb reach, navigation model, keyboard, viewport changes, fixed elements, gestures, density. |
| Language | Does copy tell users what they already know, over-explain, leak internal terminology, or paper over a layout problem with a heading? |
| Trust and control | At every point the user must trust the system: what it is doing, why, whether it is reversible, whether generated or inferred content is distinguishable from user-authored content, what persists, what is private. |
| Accessibility | Semantic structure, keyboard, focus management, target sizes, contrast, zoom, reduced motion, labelling, error identification, as interaction quality, not compliance. |
| Perceived performance | Blocking operations, layout shift, slow acknowledgement, blank waits, unnecessary spinners, missing skeletons, transitions that make fast operations feel slow, work that could be optimistic or prefetched. |
| Signature opportunities | After the weaknesses: where could this product do extraordinarily well what competitors treat as ordinary? A few moments, not decorative uniqueness everywhere. |

Use the walker's evidence for the measurable parts and your own walk for the
rest. Look especially for moments that feel generic, templated,
framework-default, dashboard-like, or assembled from familiar component-library
patterns; name the tell, not the vibe.

### 5. Inspect the implementation and root-cause — `references/implementation.md`

For every observed problem, find the decision that produced it. Read component
architecture, routing, state management, responsive logic, design tokens,
typography and spacing primitives, animation implementation, loading and error
handling, persistence, forms, accessibility semantics, duplicated components,
one-off styling, and design-system drift.

Classify each problem:

| Class | Meaning | Fix lives in |
| --- | --- | --- |
| **Local flaw** | One component or screen implemented badly | That component |
| **System drift** | A primitive, token, pattern, or convention that is missing, wrong, or bypassed, so the same problem recurs | The design system or shared primitive |
| **Product model** | The screen, flow, or feature exists because of a wrong or missing product decision | The product architecture |

Then **collapse**. Three findings with the same underlying issue are one
finding with three instances. Do not recommend dozens of local patches when one
systemic change would solve them.

### 6. Write the review — `assets/review-template.md`, `references/finding-standard.md`

```bash
python3 scripts/check_review.py reviews/premium-experience-review-<date>.md
```

Preserve the template's section order: product model, the current experience
as a user lives it (strongest parts included, so they are preserved), hierarchy
by surface, findings by altitude, systemic roots, final synthesis, and the
implementation sequence. The linter checks every finding for the six fields,
the classification, the evidence tier, and the banned vague phrases, and warns
when the sequence puts cosmetic work ahead of structural work.

## Prioritisation

Every finding gets exactly one priority:

| Priority | Meaning |
| --- | --- |
| **Foundational** | Undermines the product's usefulness, comprehension, architecture, or primary jobs. Includes an incoherent product model, a missing or wrong primary loop, a critical journey that dead-ends, and accessibility failures that block a job. |
| **Friction** | Makes accomplishing the job harder than necessary: extra decisions, lost context, premature configuration, unclear state, avoidable confirmation, waiting. |
| **Refinement** | Improves coherence, confidence, and quality: consistency, hierarchy, copy, state completeness, motion that explains. |
| **Exceptional craft** | Could elevate an already-functional experience into a genuinely premium one: signature moments, precision in micro-interactions, editorial typography. |

**Visual refinements never outrank fundamental product or usability problems.**
Effort orders work *within* a priority; it never promotes an item across
priorities. A cheap cosmetic change is still done after an expensive
Foundational one, or bundled into the same primitive so it comes for free.

Altitude (Product, Experience, Craft) says where the change lives. Priority
says what it costs the user. They are independent: a Craft-altitude finding can
be Foundational (a commitment button with no pressed or loading state on a
payment flow), and a Product-altitude finding can be Refinement (a secondary
feature that should be demoted, not removed).

## Standard of critique

Be demanding. Do not assume an existing decision deserves to survive, and do
not compliment ordinary competence. Do name genuinely strong decisions, in the
"strongest parts" section, so they are preserved through the redesign.

- Do not confuse visual novelty with product quality.
- Do not redesign established patterns without a reason grounded in the job.
- Do not optimise screenshots at the expense of interaction.
- Do not make everything animated, everything minimal, or everything a card.
- Do not solve uncertainty by adding explanatory copy. Prefer concise copy
  supported by better interface design; explain only when explanation is
  intrinsically necessary (consequences, cost, irreversibility).
- Do not recommend a trend because premium products currently use it.
- Do not recommend motion to make the product "feel polished". Motion earns its
  place by explaining something.
- Do not import another product's shape. A product with no discovery mode
  should not be given one because a marketplace has one.

The goal is an experience that feels inevitable.

## Guardrails

- **Review only.** The deliverable is the review and its implementation
  sequence. Applying changes is a separate, granted step; if asked to
  implement, take the sequence in order, structural before cosmetic, and
  re-walk after each step.
- **Never walk a mutating production flow.** The walker is read-only by
  default and stops at the first interaction. `--interact` is for staging, a
  local build, or a seeded fixture with a dedicated test account. Never a real
  customer's session.
- **Label the evidence tier on every finding.** A screenshot supports
  hierarchy and composition claims; it does not support claims about focus,
  motion, latency, contrast, or target size. Say what you did not reach.
- **Preserve what must not change.** Record the brand, signature interactions,
  and deliberate constraints in the product model, and do not file findings
  against them. If a change would improve the experience but violates one, it is
  a conversation with the owner, not a finding.
- **Respect robots, rate limits, and consent** on anything you do not own.
- **Report what was not reviewed** — states not reachable, platforms not
  tested, authenticated areas without access, field performance not measured.

## Output

One deliverable, from `assets/review-template.md`, written to `reviews/` (or
wherever the repository keeps design and QA documents), dated:

```
reviews/premium-experience-review-<YYYY-MM-DD>.md
per-evidence/                      # walker captures and JSON, referenced by path
```

The review opens with the product model, narrates the current experience as a
user lives it, ranks findings by priority within three altitudes, maps them to
their systemic roots, closes with the synthesis (what it feels like now, what
it should feel like, the largest gap, the few principles that should govern
future decisions, the highest-leverage systemic changes, the most promising
signature opportunities), and ends with an implementation sequence that makes
the product structurally better before it makes it cosmetically better,
bundling changes into shared primitives wherever three findings share a root.

## Where this sits next to the other skills

- **`ux-quality-review`** is the heuristic checklist audit: five domains, a 0–5
  score, prioritised fixes. Reach for it when the question is "what is wrong
  against baseline standards". Reach for **premium experience review** when
  the question is "what would make this exceptional", and the answer may
  include changing the product, not just the UI.
- **`premium-calm`** measures a product against a calm-design bar, scores it
  out of 100 with a gate, and emits contrast-validated tokens, then applies
  the change set on approval. It is the natural next step when this review's
  systemic roots point at the token layer or the salience budget. This review
  decides *what the product should be*; premium-calm is one way to *build the
  design language it needs*.
- **`adversarial-review`** attacks positioning, proof, persuasion, and duty of
  care. This review attacks the experience. They share the strategic
  question of whether the product earns trust; they answer it from different
  sides.
- **`frontend-polish`** keeps new UI inside an already-locked design language.
  Findings classed as *System drift* here often become rules there.
- **`qa-sweep`** files defects. A screen can be bug-free and still fail this
  review; a screen can fail QA and be beautifully designed.

## References

Load as needed:

- `references/product-model.md` — inferring the model and the jobs; deciding what premium means here; judging surfaces by intent; the five hierarchy roles
- `references/journeys.md` — the minimum journeys, the friction taxonomy, the journey plan, reading the walker's evidence, degraded modes when no browser or URL is available
- `references/lenses.md` — the nine lenses with their checks and tells: interaction states, premium craft, motion, responsive and mobile, language, trust and control, accessibility, perceived performance, signature opportunities
- `references/implementation.md` — the codebase inspection playbook, root-cause classification, collapsing findings into systemic roots, bundling into primitives
- `references/finding-standard.md` — the finding shape, the vagueness test, altitude and priority, evidence tiers, bad→good examples
- `references/worked-example.md` — a condensed review of a consumer product end to end, at the bar this skill expects
