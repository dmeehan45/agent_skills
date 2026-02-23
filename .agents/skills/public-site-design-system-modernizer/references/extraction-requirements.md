# Extraction Requirements and Scope Boundaries

Use this file when implementing the extractor/normalizer/synthesizer pipeline. It captures the exhaustive detection targets and v1 acceptance boundaries.

## 1) Visual DNA (extract and normalize)

Detect and normalize:

- color palette:
  - brand
  - neutral
  - semantic
  - background
  - border
- typography:
  - families + fallbacks
  - weights
  - type scale
  - line heights
  - tracking
- spacing scale
- size scale (controls, icons, containers)
- radius scale
- border styles
- shadows / elevation
- motion timing / easing (if detectable)
- breakpoints and container widths
- grid/layout rhythm
- icon style characteristics
- image treatment patterns

For each category return:

- observed variants
- canonical recommendation
- accidental variants to exclude
- confidence score

## 2) Verbal / Brand Voice DNA

Extract and summarize:

- tone attributes
- sentence style
- CTA style
- messaging hierarchy
- vocabulary preferences
- overused phrases / taboo phrases to avoid
- reading-level estimate

## 3) Component Patterns (detect recurring, normalize specs)

Detect recurring components for (when present):

- header / nav
- hero sections
- buttons
- cards
- forms / fields / validation
- tables / data displays
- badges / pills
- alerts / banners
- accordions
- footers
- tabs / pagination / breadcrumbs
- modals / drawers / sidebars
- workflow-oriented UI components

For each component specify:

- purpose
- anatomy
- variants
- states:
  - `default`
  - `hover`
  - `focus`
  - `active`
  - `disabled`
  - `loading` (if applicable)
  - `error` (if applicable)
- spacing rules
- content guidance
- accessibility notes
- implementation notes

## 4) Review and Export UX expectations

Provide review tabs/sections:

- Executive Summary
- Source Audit
- Brand DNA
- Design Tokens
- Component Library Spec
- Page Patterns
- Accessibility Audit
- Preserve / Normalize / Improve / Exclude
- Developer Handoff
- Evidence + Confidence Notes

Provide actions:

- Export full package
- Regenerate specific sections only (`tokens`, `components`, `patterns`, `dev handoff`)
- Save settings as reusable preset

## 5) Success criteria (acceptance requirements)

A successful run:

- produces a coherent canonical token system (not raw style dump)
- preserves recognizable brand identity while modernizing inconsistencies
- includes component specs with anatomy, variants, and states
- includes accessibility improvements and rationale
- shows included/excluded page decisions
- includes confidence/uncertainty reporting
- generates usable designer + developer handoff artifacts without major reinterpretation

A failed run:

- mirrors source too literally
- encodes design debt as canonical
- omits states or spacing logic
- ignores accessibility
- pretends certainty with weak evidence
- outputs only observations without actionable system guidance

## 6) MVP scope (v1 only)

Include:

- public websites only
- representative sample mode (default)
- bounded full crawl mode (optional)
- desktop + mobile screenshots
- HTML/CSS/text/asset metadata capture
- prompt chain A/B/C
- tokens + component specs + page patterns
- CSS vars + Tailwind theme output
- markdown + JSON artifacts
- accessibility + confidence reporting

Exclude:

- authenticated pages
- private portals
- runtime app instrumentation behind login
- Figma API export
- visual diffing across versions
- competitor comparison mode
- direct asset reuse pipelines
