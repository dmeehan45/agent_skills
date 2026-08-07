# Measurement — evidence before opinion

A premium-calm assessment that asserts "contrast is poor" or "targets are too
small" without a number is an opinion, and it will be argued with. Measure
first, then score, then propose.

**Run the scripts. Do not re-derive their work by reading CSS or eyeballing a
screenshot.** Contrast composited through translucent ancestors, rendered target
rectangles, and what still animates under reduced motion are all invisible to
static reading.

## Pipeline

```bash
SKILL=skills/premium-calm/scripts

# 1. measure the current state
node $SKILL/measure_surface.mjs --surfaces run-plan.json --out pc-evidence

# 2. validate the proposed palette before proposing it
python3 $SKILL/check_contrast.py proposed-tokens.json

# 3. emit the token files the codebase will consume
python3 $SKILL/emit_tokens.py proposed-tokens.json --out tokens/ --preview

# 4. score, and apply the release gate
python3 $SKILL/score_rubric.py scores.json

# 5. after applying changes, re-measure and re-score against the baseline
node $SKILL/measure_surface.mjs --surfaces run-plan.json --out pc-evidence-after
python3 $SKILL/score_rubric.py scores-after.json --baseline scores-before.json
```

## Run plan

```json
{
  "project": "Example",
  "accents": ["#C6FF1A"],
  "spaceScale": [4, 8, 12, 16, 24, 32, 48, 64, 96],
  "viewports": ["mobile", "desktop"],
  "surfaces": [
    { "id": "home",     "url": "https://example.com/",            "mode": "discovery" },
    { "id": "results",  "url": "https://example.com/search?q=x",  "mode": "comparison" },
    { "id": "detail",   "url": "https://example.com/item/1",      "mode": "comparison" },
    { "id": "checkout", "url": "http://localhost:3000/checkout",  "mode": "commitment" },
    { "id": "trips",    "url": "http://localhost:3000/trips",     "mode": "management" }
  ]
}
```

`mode` comes from calibration and travels with the evidence, so a commitment
surface is never judged by discovery standards.

Useful flags: `--accent` (track accent coverage), `--viewport mobile`,
`--storage-state auth.json` (authenticated surfaces — checkout and account are
usually where calm matters most), `--wait-for <selector>`, `--no-renders`,
`--space-scale`.

**Cover the whole journey, not the marketing surface.** A run plan containing
only the home page measures the easiest screen in the product.

## What it measures, and the gate for each

| Reading | Gate | Reads on |
| --- | --- | --- |
| `contrastFailures` | 0 | Colour and contrast, accessibility |
| `targetsUnder44` / `targetsUnder48` | 0 | Accessibility |
| `controlsWithoutFocusStyle` | 0 | Accessibility, interaction feedback |
| `movesUnderReducedMotion` | 0 | Motion, accessibility |
| `cls` | ≤ 0.1 | Performance, imagery |
| `lcpMs` | ≤ 2500 (confirm in field) | Performance |
| `competingSalienceRegions` | 1 dominant | Task clarity |
| `primaryLikeActions` | 1 per viewport | Task clarity, hierarchy |
| `accentCoveragePct` | Low single digits outside brand moments | Colour restraint |
| `typeTreatments` | 6–8 | Typography |
| `linesOver85Chars` | 0 for continuous reading | Typography |
| `maxCardNestDepth` | ≤ 2 | Materials, spacing |
| `offScaleSpacingValues` | 0 | Spacing rhythm |
| `infiniteAnimations` | 0 outside rare ambient | Motion |
| `slowTransitions` | 0 above 420ms | Motion |
| `imagesMissingDimensions` | 0 | Performance, imagery |
| `distinctImageRatios` | 1–2 per template | Imagery |
| `vagueActionLabels` | 0 | Microcopy and trust |

## Reading the renders

Four PNGs per surface per viewport:

| Render | Question it answers |
| --- | --- |
| `*.png` | What the surface actually looks like right now |
| `*.squint.png` | Does the blurred mass reveal the intended reading order, or do several regions compete equally? |
| `*.grayscale.png` | Does hierarchy survive without hue? |
| `*.accentless.png` | With the accent neutralised, does anything still read as selected or primary? |

The accentless render is the fastest way to prove colour-only meaning. If the
selected filter and the unselected ones become indistinguishable, that is an
accessibility failure and a calm failure in one image — and it is far more
persuasive in a review than a citation.

## Limits, and how to stay honest about them

**Anything not measured is a recommendation, and must be labelled as one.**

- **Text over images is not scored.** Reported as
  `contrastUnmeasuredOverImage`. Composited contrast against photography needs a
  per-pixel check; treat these as manual review items, not passes.
- **LCP and CLS are single lab runs.** Good for regression and for catching
  reserved-dimension bugs. Field p75 is the real gate.
- **INP is not measured.** The script never clicks, so it cannot observe
  interaction latency. Take INP from field data (RUM), and treat the ~100ms
  acknowledgement rule as a code-review item.
- **Focus probing only reads computed style.** A focus ring drawn on a pseudo-
  element or a parent may read as missing. Confirm flagged controls by hand
  before filing them.
- **The accent matcher uses an RGB distance threshold.** Accents close to a
  neutral, or gradient fills, may under-count. Check `accentUses` against the
  plain render.
- **Only the first viewport counts for salience and accent coverage**, because
  that is where the "one dominant cluster" rule applies.
- **Dynamic and authenticated states need setup.** An error state, a pending
  transaction, or an empty list will not appear from a URL alone. Reach them
  with `--storage-state`, a seeded fixture, or a static capture, and say in the
  assessment which states were measured live versus reviewed by hand.
- **Element caps.** 4000 elements, 600 interactive, 120 focus probes per page.
  Very large pages are sampled, not exhausted.

## When the browser cannot run

Playwright or a reachable URL is not always available. Degrade in this order,
and record which tier the evidence came from — a finding sourced from tier 3 is
not the same claim as one from tier 1.

1. **Live measurement.** The full pipeline. Preferred.
2. **Local build or static capture.** Point the run plan at `localhost` or saved
   HTML. Nearly as good; performance numbers are not comparable to production.
3. **Token and source analysis only.** `check_contrast.py` still validates the
   palette from the stylesheet or theme file with no browser at all. Read
   component source for state coverage, focus handling, and motion durations.
   Label everything as "reviewed, not measured".
4. **Screenshots only.** Salience, layout, and hierarchy findings are legitimate
   from an image. Contrast, target size, focus, motion, and performance findings
   are not — do not assert numbers you did not measure.

## Interaction guardrails

The script **focuses controls and reads computed style. It never clicks,
submits, navigates, or types.** That is deliberate: a measurement pass over a
checkout must not create an order.

- Do not point it at a production endpoint that mutates on load.
- Prefer a staging environment or a local build for commitment surfaces.
- With `--storage-state`, use a dedicated test account, never a real customer's.
- Respect `robots.txt` and rate limits when measuring anything you do not own.
