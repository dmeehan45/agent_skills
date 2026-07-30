# Extraction Requirements and Scope Boundaries

What must be extracted, where each signal is measured from, and what is out of
scope. The pipeline in `pipeline.md` does the measuring; this file defines the
coverage it has to achieve.

**Measure, don't infer.** Every category below has a measurement source. If a
category cannot be measured on a given site, report it as a gap — do not fill it
from convention.

## 0) Sources of truth, in priority order

Higher-priority sources override lower ones. The first three are the reason
extraction can be faithful at all, and all three are read by `capture_site.mjs`.

1. **The site's own declared tokens** — `:root` custom properties resolved via
   `getComputedStyle(document.documentElement)`. Modern sites ship their design
   system in the stylesheet. When present you are transcribing, not inferring.
2. **CSSOM declarations** — `@media` breakpoint values, `@font-face` rules,
   `@keyframes` names. Actual breakpoints, not conventional ones.
3. **Brand asset colours** — `<meta name="theme-color">`, web app manifest, and
   `fill`/`stroke`/`stop-color` on the logo SVG. Often the exact brand hex.
4. **Computed styles across the rendered DOM** — area-weighted, role-tagged.
   The fallback for everything not declared, and the only source for how values
   are actually *used*.
5. **Screenshot pixels** — used for fidelity verification, not for deriving
   token values.

Record which source each token came from. `declared` is a component of the
confidence score for exactly this reason.

## 1) Visual DNA

| Category | Measured from | Notes |
| --- | --- | --- |
| Colour palette | computed `color`, `background-color`, `border-color`, weighted by rendered area and tagged by element role | Cluster perceptually (OKLab ΔE ≤ 0.025) before assigning roles |
| Colour roles | role breakdown per cluster | Button background ≠ field background ≠ page surface. A colour may hold several roles |
| Gradients | computed `background-image` containing `gradient` | Keep verbatim; do not decompose into stops |
| Typography families | computed `font-family` ranked by rendered-area share | Also record `@font-face` declarations and which family actually rendered |
| Type scale | computed `font-size` census | Fit the ratio; name it only when close to a known one. Never force a familiar ratio |
| Line height | per-size dominant ratio from element records | Store unitless |
| Weights, tracking, transform | computed values | |
| Spacing scale | `padding`, `margin`, `gap` | Base unit = largest candidate explaining ≥80% of values |
| Size scale | control heights, icon sizes, container widths | Measured from bounding boxes |
| Radius | computed `border-top-left-radius` | Values ≥500px or `%` are pill, not a scale step |
| Borders | width, style, colour | |
| Elevation | computed `box-shadow`, ordered by blur | Produce a ladder, not a set |
| Motion | computed `transition-duration`, `transition-timing-function`, `animation-*` | Directly readable — never report as "not detectable" |
| Breakpoints | `@media` conditions in the CSSOM | Normalise `em`/`rem` to px at 16px |
| Containers | rendered widths of centred / `max-width` elements | |
| Grid rhythm | `grid-template-columns` column counts, `gap` | |
| Z-index | computed `z-index` | Emit as a ladder |
| Icon system | inline SVG vs `<use>` sprite vs icon font; `viewBox`, `stroke-width`, `stroke-linecap`, rendered size | Stroke width and grid size are the fingerprint |
| Image treatment | radius, aspect ratios, filters on media elements | |
| **Dark mode** | full re-measure under `prefers-color-scheme: dark` | Not optional. Report `supported: false` when genuinely absent |

For every category record: **observed variants**, **canonical recommendation**,
**accidental variants excluded**, **confidence**, and **evidence page ids**.

## 2) Verbal / Brand Voice DNA

Extracted from captured headings, CTA labels, and body paragraphs.

- tone attributes, sentence style, reading-level estimate
- CTA verb patterns and label length
- messaging hierarchy (h1 → h2 → body progression)
- vocabulary preferences; overused and taboo phrases

Weight by page role. Legal and policy pages are tagged
`evidence_scope: typography_only` — use them for type and link styling, never
for brand voice.

## 3) Component patterns

Detect when present: header/nav, hero, buttons, cards, forms and fields,
validation, tables, badges, alerts/banners, accordions, tabs, pagination,
breadcrumbs, modals/drawers, footers, workflow UI.

Per component specify purpose, anatomy, variants, spacing, content guidance,
accessibility notes, implementation notes, and states:

`default`, `hover`, `focus`, `focus-visible`, `active`, `disabled`, plus
`loading`, `error`, `selected`, `empty` where applicable.

**States must be measured, and measured states must be distinguishable from
recommended ones.** `capture_site.mjs` probes hover, focus, focus-visible and
active by scripted interaction and reads disabled styling declaratively. Any
state it did not observe goes in `unmeasured_states` and is presented as a
design recommendation. Never present an invented state as an extraction. Schema
in `component-contract-schema.md`.

Form controls deserve specific attention — they drift more than any other
component family and are the most likely to be under-specified.

## 4) Fidelity modes

`aggregate_tokens.py --fidelity-mode`:

- **`verbatim`** — report what the site does. No snapping, no pruning. Use to
  understand the source.
- **`modernized`** (default) — snap off-grid spacing, prune accidental
  variants, cap font families. Use for the deliverable.

Both modes keep the complete measurements in `evidence/measured-raw.json` and
log every change in `evidence/raw-vs-canonical-diff.md`. Never normalize
silently, and never present a normalized value as an observation.

Perceptual colour merging happens in both modes: two values within ΔE 0.025 are
the same colour with two implementations, not two design decisions.

## 5) Success criteria

A successful run:

- grounds every token in measurement, with source and evidence page ids
- preserves recognizable brand identity — verified by the round-trip fidelity
  check, not by assertion
- passes the fidelity gate (mean palette ΔE ≤ 0.07, ideally ≤ 0.03)
- specifies components with anatomy, variants, and **measured** states
- separates measured from recommended everywhere
- shows included/excluded page decisions with reasons
- reports computed confidence and every normalization applied
- emits dark mode when the source has it
- produces artifacts a codebase can consume without reinterpretation

A failed run:

- asserts values it did not measure
- encodes design debt as canonical without recording it in the diff
- presents invented component states as extractions
- omits dark mode on a site that has it
- claims certainty with weak evidence, or reports confidence with no formula
- ships tokens that fail the fidelity check
- mirrors source page layouts, or reuses protected assets without rights

## 6) Scope

Include: public websites; representative-sample and bounded-full crawl modes;
desktop/tablet/mobile measurement; light and dark passes; interaction state
probing; DTCG tokens, CSS, Tailwind v3 and v4; component contracts; page
patterns; accessibility, confidence, and fidelity reporting.

Exclude: authenticated pages, private portals, anything behind a login,
credential entry, access-control bypass, Figma API export, cross-version visual
diffing, competitor comparison mode, and direct asset reuse pipelines.

Do not spoof identity or evade bot protection to widen coverage. Report the
limit and reduce scope instead.
