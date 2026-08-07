# Composing the current → target change set

The deliverable is not a critique. It is an ordered set of changes, each one
traceable to measured evidence and checkable when it lands.

## The shape of a change item

Every item carries all nine fields. An item missing evidence is an opinion; one
missing an acceptance check cannot be verified; one missing an effort estimate
cannot be sequenced.

```
ID            PC-07
Surface       checkout (commitment mode)
Criterion     microcopy-trust, task-clarity
Severity      S3
Current       Total and fees appear only after a payment method is selected.
              Evidence: pc-evidence/evidence/checkout.mobile.json — the price
              summary node is absent above the fold; vagueActionLabels includes
              "Submit".
Target        A persistent line-item quote — nightly rate, taxes, fees, total,
              refundability — visible from entry, and a commitment action that
              names the amount: "Pay GHS 1,240".
Why           Trust. The user cannot evaluate the commitment before making it,
              which is the largest abandonment and support-contact risk on the
              highest-stakes path.
Effort        M — new summary component, reuse existing quote endpoint
Acceptance    Total, currency, fees, and cancellation terms are visible without
              scrolling on a 390px viewport; the action label contains the
              amount; `vagueActionLabels` is 0 for this surface.
Risk          Sticky summary reduces content height on small screens; verify the
              form remains usable at 320px and at largest text setting.
```

## Sequence: foundations, then the riskiest path, then the rest

Order the plan in bands. Within a band, order by the stakes ranking from
calibration.

| Band | Contains | Why here |
| --- | --- | --- |
| **0 — Foundations** | Token layer, contrast fixes, focus treatment, target sizes, reduced-motion handling, spacing scale | Everything downstream inherits these. Fixing them first removes whole classes of finding at once, and prevents rework. |
| **1 — Critical path** | The highest-stakes journey end to end: entry, commitment, confirmation, recovery | Where trust and money concentrate. A calm visual language is not credible until this path is predictable. |
| **2 — Comparison and management** | Result templates, detail information architecture, status surfaces, empty and error states | Determines whether the product feels useful and whether it stays calm after commitment. |
| **3 — Restraint and rhythm** | Salience reduction, accent scarcity, nesting removal, type consolidation, imagery consistency | Real improvements, but they land better on a stable structure. |
| **4 — Expression** | Editorial storytelling, decorative material, advanced motion | Last. Deliberately. |

**Transactional clarity precedes decorative refinement.** Reversing this order
is the most common way a premium-calm pass produces a beautiful product that
people still do not trust.

## Prioritisation

Score each opportunity, then place it:

| Priority | Rule |
| --- | --- |
| **Critical** | Very high user *and* business impact, on a critical path, or any S4 |
| **High** | High impact on a critical path, or an S3 anywhere |
| **Medium** | Real improvement off the critical path |
| **Later** | Decorative or expressive work with no trust or comprehension effect |

Effort (S / M / L) sequences work *within* a priority band. It never promotes or
demotes an item across bands — "it's cheap" is not a reason to do a decorative
change before a payment-state fix.

## The before/after table

For the assessment's summary section, one row per surface:

| Surface | Current | Target | Measurable heuristic |
| --- | --- | --- | --- |
| Home / discovery | Promotional region and several similarly weighted cards | Lead with the primary task control; inspiration below the active task; fewer, larger recommendations | Task control identified within two seconds; one primary action above the fold |
| Results | Image-heavy cards with compact metadata | One card template with consistent ratio, the facts needed to compare, and a policy cue | Essential comparison facts visible without opening every item |
| Detail | Media-led surface with a bright commitment control | Gallery, concise trust row, summary, context, visible total and policy beside a sticky action | Cost, terms, and constraints visible before commitment |
| Commitment | Dense panel with a high-emphasis final action | Comprehensible stages, persistent line-item quote, explicit state and recovery | No hidden mandatory cost; no data loss after recoverable failure |
| Management | Repeated cards with similar emphasis | Grouped by status, leading with the next required action | Next action identifiable in under two seconds |
| Empty / error | Generic or sparse | State-specific explanation, preserved context, one safe next step | No dead end; errors state whether data or money was affected |

Replace the rows with the product's actual surfaces. The pattern to keep is
**current → target → how we will know**.

## The approval gate

Never apply changes straight from the assessment. Present:

1. The calibration block, so the target state is explicit and arguable.
2. The measured current state, with the gate table.
3. The rubric score and band, per surface.
4. The change set, in bands, with effort and acceptance checks.
5. What is explicitly **not** changing, and why — especially the signature
   assets that were reassigned rather than removed.

Then ask which bands to apply. Expect the answer to be a subset. Band 0 alone is
often the right first release: it is mostly mechanical, it lifts several
criteria at once, and it makes the later bands cheaper.

## Applying

- **One band at a time**, and re-measure after each. A single large diff makes
  it impossible to attribute a regression.
- **Foundations land as tokens**, not as per-screen patches. If a fix is applied
  in three components, it belonged in the token layer.
- **Preserve the reassigned signature assets.** Removing the brand accent is not
  the same as restricting where it appears; the first is a rebrand nobody asked
  for.
- **Change one variable per item.** Restructuring the information architecture
  and restyling in the same commit hides which one caused the movement.
- **Respect the codebase's existing conventions.** A premium-calm pass that
  introduces a second styling system has added debt, not removed it.
- **Every applied item gets its acceptance check run**, not just a visual
  once-over.

## Re-verification

After each band:

```bash
node    scripts/measure_surface.mjs --surfaces run-plan.json --out pc-evidence-after
python3 scripts/score_rubric.py scores-after.json --baseline scores-before.json
```

Report movement per criterion and per surface, then state plainly:

- which items landed and passed their acceptance checks,
- which landed but did not move the number, and the likely reason,
- which were skipped, and why,
- whether the release gate now passes.

**A criterion that did not move is information, not an embarrassment.** It
usually means the finding was mis-diagnosed, or the fix was applied at the
wrong layer. Say so, and re-diagnose rather than adding more changes on top.
