# Premium-calm assessment — <product>

> Preserve this section order. Each section answers a question the next one
> depends on: what are we aiming at, where are we, how bad is it, what changes,
> and how will we know it worked.

**Assessed** <date> · **Scope** <surfaces and platforms> · **Evidence tier**
<measured live / local build / source-only / screenshots — see measurement.md>

---

## 1. Calibration

| | |
| --- | --- |
| Archetype | <e.g. transactional marketplace, mobile-first> |
| Calm means, here | <one sentence> |
| Highest-stakes moment | <the irreversible one, and why> |
| Journey priority | 1 <…> 2 <…> 3 <…> |
| Modes | <surface=mode, …> |
| Bar | <rubric target · severity gates · a11y floor · WCAG level · target sizes · vitals> |
| Must not change | <signature assets, constraints, locked decisions> |

**Signature asset reassignment**

| Asset | Was doing | Becomes | Now forbidden from |
| --- | --- | --- | --- |
| | | | |

---

## 2. Measured current state

Command(s) run, and the evidence path:

```
node scripts/measure_surface.mjs --surfaces run-plan.json --accent "<hex>" --out pc-evidence
```

| Reading | Gate | <surface> | <surface> | <surface> |
| --- | --- | --- | --- | --- |
| Contrast failures | 0 | | | |
| Targets under 44pt | 0 | | | |
| Controls without focus style | 0 | | | |
| Moves under reduced motion | 0 | | | |
| CLS | ≤0.1 | | | |
| LCP (lab) | ≤2500ms | | | |
| Competing salience regions | 1 | | | |
| Primary-looking actions | 1 | | | |
| Accent coverage | low | | | |
| Type treatments | 6–8 | | | |
| Max card nesting | ≤2 | | | |
| Off-scale spacing values | 0 | | | |
| Vague action labels | 0 | | | |

**What the renders show** — one line each for the squint, grayscale, and
accentless renders per critical surface. Name what survives and what does not.

**Not measured** — text over images, INP, dynamic and authenticated states not
reachable from a URL, and anything else reviewed by hand rather than measured.
List it. An unlabelled inference reads as a measurement.

---

## 3. Rubric score

```
python3 scripts/score_rubric.py scores.json
```

| Surface | Score | Band | Weakest criteria |
| --- | --- | --- | --- |
| | /100 | | |

**Overall** <n>/100 — <band>. **Release gate:** <pass / blocked, with blockers>.

---

## 4. Findings

Severity-ordered, worst first. Every finding cites evidence.

| ID | Severity | Surface | Criterion | Finding | Evidence |
| --- | --- | --- | --- | --- | --- |
| PC-01 | S4 | | | | |

---

## 5. Change plan

Banded. Within a band, ordered by the journey priority from calibration.

### Band 0 — Foundations
*Token layer, contrast, focus, targets, reduced motion, spacing scale. Everything
downstream inherits these.*

| ID | Change | Effort | Acceptance check |
| --- | --- | --- | --- |
| | | S/M/L | |

### Band 1 — Critical path: <name>
### Band 2 — Comparison and management
### Band 3 — Restraint and rhythm
### Band 4 — Expression

**Full item detail** for every Critical and High item, in the nine-field shape
from `change-plan.md`: ID, Surface, Criterion, Severity, Current (with
evidence), Target, Why, Effort, Acceptance, Risk.

### Before and after by surface

| Surface | Current | Target | Measurable heuristic |
| --- | --- | --- | --- |
| | | | |

---

## 6. Proposed tokens

Validated before proposal — a palette that has not been checked is not a
proposal.

```
python3 scripts/check_contrast.py proposed-tokens.json     # must exit 0
python3 scripts/emit_tokens.py  proposed-tokens.json --out tokens/ --preview
```

| | |
| --- | --- |
| Pairs checked | <n>, all passing |
| Notable constraints found | <e.g. the accent cannot carry a thin indicator on light ground> |
| Emitted | tokens.css, tailwind.theme.{js,css}, tokens.json, Tokens.swift, android/ |

---

## 7. Not changing, and why

The signature assets that were **reassigned rather than removed**, the
constraints respected, and any finding deliberately accepted. A premium-calm
pass that quietly erases the brand has failed even with a perfect score.

---

## 8. Approval

Which bands to apply. Band 0 alone is often the right first release: mostly
mechanical, lifts several criteria at once, makes later bands cheaper.

- [ ] Band 0 — Foundations
- [ ] Band 1 — Critical path
- [ ] Band 2 — Comparison and management
- [ ] Band 3 — Restraint and rhythm
- [ ] Band 4 — Expression

---

## 9. Re-verification *(after applying)*

```
node    scripts/measure_surface.mjs --surfaces run-plan.json --out pc-evidence-after
python3 scripts/score_rubric.py scores-after.json --baseline scores-before.json
```

| Surface | Before | After | Δ | Gate |
| --- | --- | --- | --- | --- |
| | | | | |

- **Landed and verified** — items whose acceptance checks pass.
- **Landed, no movement** — and the likely reason. Re-diagnose rather than
  stacking more changes on top.
- **Skipped** — and why.
- **Release gate** — passes / still blocked by <…>.
