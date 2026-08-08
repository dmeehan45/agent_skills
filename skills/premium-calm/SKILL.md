---
name: premium-calm
description: >-
  Move an existing interface toward premium calm — composed, trustworthy,
  low-uncertainty UX where emphasis is scarce, state is explicit, and nothing is
  left unresolved. Measures the current state in a real browser (contrast through
  composited backgrounds, target sizes, focus deltas, salience mass, what still
  moves under reduced motion, layout shift), scores it against a weighted
  100-point rubric with an S0–S4 severity gate, then proposes an ordered
  current→target change set with contrast-validated tokens and applies it band by
  band on approval. Use when someone wants a product to feel premium, calm,
  considered, composed, refined, or trustworthy; says an interface feels noisy,
  cluttered, loud, busy, cheap, or anxious; asks for a "calm pass", "premium
  pass", or design-quality pass over a website, web app, or mobile app; or wants
  a design language that holds up under slow networks, large text, payment
  failure, and cancellation rather than only in ideal screenshots. Works for any
  product type — it calibrates what calm means for the archetype instead of
  imposing one aesthetic. Not a general heuristic audit (that is
  ux-quality-review), not brand extraction from a public site (that is
  design-system-extractor).
---

# Premium calm

Premium calm is the disciplined management of attention. It is not minimalism,
muted colour, generous whitespace, or slow animation. It is the property that
makes a product feel composed and trustworthy because every element has an
explicit role, emphasis is scarce, transitions preserve context, language
reduces uncertainty, and the system reacts without visible strain.

```
premium calm = clarity × restraint × responsiveness × continuity × trust
```

Multiplicative. A beautiful screen that hides fees is not calm. A sparse
checkout that responds slowly is not premium. A fluid transition that causes
motion sickness is not refined. An accessible form with vague error language
still produces anxiety.

**The objective is not maximum emptiness. It is minimum unresolved uncertainty
with maximum perceived care.** Minimalism removes elements; premium calm removes
unresolved decisions.

## Two rules the whole skill rests on

**Calibrate before you judge.** Linear, Aesop, Stripe, Calm, and Notion are all
disciplined premium-calm systems and share almost no visual DNA. Calm is a
posture, not a palette. Running this skill without deciding what calm means for
*this* archetype is how a dense professional tool gets turned into a spa
brochure. Phase 1 is not optional.

**Measure, don't assert.** "Contrast is poor" is an opinion and will be argued
with; "13 text nodes fail AA, worst at 2.1:1, here is the file" is a finding.
Composited contrast through translucent ancestors, rendered target rectangles,
which controls have no focus style, and what still animates under
`prefers-reduced-motion` are all invisible to reading CSS. Run the scripts.
Anything not measured is a recommendation and must be labelled as one.

## Phases

Work through these in order. Stop at phase 5 and get approval before touching
code.

### 1. Calibrate — `references/calibration.md`

Name the archetype. Rank journeys by **irreversibility, not traffic** — the
highest-traffic screen is rarely the one that decides trust. Inventory the
signature brand assets and **reassign their roles rather than removing them**
(an accent used everywhere is decoration; the same accent at the moment of
commitment is a signal). Assign each surface a mode: discovery, comparison,
commitment, management, recovery. Record the bar and what must not change.

Produce the calibration block. Everything downstream is judged against it.

### 2. Measure — `references/measurement.md`

```bash
node scripts/measure_surface.mjs --surfaces run-plan.json --accent "#hex" --out pc-evidence
```

Cover the whole journey, not the marketing surface. Per surface and viewport
this yields JSON evidence plus four renders: as-rendered, squint (blurred),
grayscale, and accentless. It focuses controls and reads computed style — it
never clicks, submits, navigates, or types.

When no browser or URL is available, degrade through the tiers in
`measurement.md` and say which tier each finding came from.

### 3. Score — `references/rubric.md`

```bash
python3 scripts/score_rubric.py --template > scores.json   # then fill it in
python3 scripts/score_rubric.py scores.json
```

Ten criteria, fixed weights summing to 100, anchored to the measured evidence so
two reviewers land within a point. Severity S0–S4. The gate blocks on any open
S4, any open S3 on a critical path, accessibility below 4/5, or a critical-path
surface below 85/100. It exits `2` when blocked.

### 4. Propose tokens — `references/design-language.md`

```bash
python3 scripts/check_contrast.py proposed-tokens.json    # must exit 0
python3 scripts/emit_tokens.py  proposed-tokens.json --out tokens/ --preview
```

Encode accessibility into the token layer, not into screens — a palette repaired
screen by screen is not a design system. `emit_tokens.py` refuses to emit while
any declared pair fails. Emits CSS custom properties, Tailwind v3 and v4,
DTCG JSON, Swift, and Android resources from one spec, with the measured ratio
annotated beside each colour. Start from `assets/token-spec.example.json`.

### 5. Compose the change set — `references/change-plan.md`

Every item carries nine fields: ID, surface, criterion, severity, current (with
evidence path), target, why, effort, acceptance check, risk. Order into bands:

```
0  Foundations          tokens, contrast, focus, targets, reduced motion, spacing
1  Critical path        the highest-stakes journey, end to end
2  Comparison & management   templates, IA, status, empty and error states
3  Restraint & rhythm   salience, accent scarcity, nesting, type, imagery
4  Expression           editorial, decorative material, advanced motion
```

**Transactional clarity precedes decorative refinement.** Effort sequences work
*within* a band; it never promotes an item across bands.

### 6. Get approval — the gate

Present calibration, measured state, score, the banded change set, and what is
explicitly **not** changing. Ask which bands to apply. Expect a subset. Band 0
alone is often the right first release: mostly mechanical, lifts several criteria
at once, and makes every later band cheaper.

Do not start editing before this answer.

### 7. Apply, then re-verify

One band at a time. Foundations land as tokens, not per-screen patches. Change
one variable per item. Respect the codebase's existing conventions — a pass that
introduces a second styling system has added debt, not removed it. Run each
item's acceptance check.

```bash
node    scripts/measure_surface.mjs --surfaces run-plan.json --out pc-evidence-after
python3 scripts/score_rubric.py scores-after.json --baseline scores-before.json
```

Report what landed and passed, what landed without moving the number and why,
what was skipped, and whether the gate now passes. **A criterion that did not
move is information.** It usually means the finding was mis-diagnosed or the fix
went in at the wrong layer — re-diagnose rather than stacking more changes on
top.

## Guardrails

- **Never apply before approval.** The change set is the deliverable; applying
  it is a separate, granted step.
- **Preserve the brand.** Reassigning where a signature asset appears is the
  method. Removing it is a rebrand nobody asked for. If a change would improve a
  score but violates "must not change", it is a conversation with the brand
  owner, not a candidate.
- **Never measure a mutating production endpoint.** Use staging, a local build,
  or a seeded fixture for commitment surfaces. With `--storage-state`, use a
  dedicated test account.
- **Label the evidence tier.** A finding from a screenshot is not the same claim
  as one from a measured run. Never assert contrast, target size, focus, motion,
  or performance numbers you did not measure.
- **Report what was not measured** — text over images, INP, and any dynamic or
  authenticated state you could not reach.
- **Lab vitals are not field vitals.** LCP and CLS from a single run catch
  regressions and reserved-dimension bugs. The gate is field p75.
- **Do not import another product's shape.** A product with no discovery mode
  should not be given one.

## Output

Four deliverables, templates in `assets/`:

| Deliverable | Template |
| --- | --- |
| Assessment + banded change plan | `assets/assessment-template.md` |
| Contrast-validated token set | `assets/token-spec.example.json` → `emit_tokens.py` |
| Reusable rubric scorecard and gate | `assets/scorecard-template.md` |
| Rendered visual summary | `assets/artifact-template.html` |

The scorecard is meant to outlive the engagement: re-run it each release so
"premium calm" stays a tracked number with a gate rather than a recurring
opinion.

## Where this sits next to the other skills

- `ux-quality-review` is the general heuristic audit: broad UX domains,
  prioritised findings, no target state. Reach for it when the question is "what
  is wrong here". Reach for **premium calm** when the question is "how do we get
  from this to a specific, higher quality bar", and you want tokens, a score,
  and a gate.
- `design-system-extractor` measures someone else's public site to derive a
  design system. **Premium calm** measures *your* product against a quality bar
  and proposes the move. Use the extractor first if the brand foundation does not
  exist yet.
- `frontend-polish` keeps new UI inside an already-locked design language.
  **Premium calm** is what produces that language when it is missing or
  inconsistent.
- `qa-sweep` finds defects; premium calm finds unresolved decisions. A screen can
  be bug-free and still anxious.

## References

Load as needed:

- `references/calibration.md` — archetypes, stakes ranking, asset reassignment, mode map
- `references/design-language.md` — salience budget, type, colour, spacing, motion, materials, microcopy, accessibility, performance, cross-platform
- `references/component-standards.md` — component specs, state completeness, the commitment state machine
- `references/measurement.md` — pipeline, run plan, gates per reading, limits, degraded runs
- `references/rubric.md` — criteria and weights, evidence anchors, severity, release gate, cadence, checklist
- `references/change-plan.md` — change-item shape, banding, prioritisation, approval, re-verification
- `references/worked-example.md` — a marketplace end to end, and how the method translates to other archetypes
