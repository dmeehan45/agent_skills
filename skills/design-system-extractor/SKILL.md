---
name: design-system-extractor
description: Extract a brand-faithful design system from a public website by measuring its rendered pages in a real browser — computed styles, the site's own CSS custom properties, interaction states, dark mode — then emitting DTCG tokens, layered CSS, Tailwind v3/v4 themes, and component contracts, verified by a round-trip fidelity check against the source pixels. Use when someone wants to extract, capture, or reverse-engineer the design system, tokens, brand palette, typography, or component styles of a public site, or build a site-inspired (not cloned) modernized baseline for a rebuild or redesign.
---

# Public Site Design System Modernizer

Extract a design system from a **public website** by measuring it, then emit
artifacts a codebase can consume. Preserve recognizable brand character,
normalize inconsistency, improve accessibility, and never clone.

## Measure, don't infer

The fidelity of the output depends entirely on this. A model looking at
screenshots and HTML produces a *plausible* design system: hex values drift a
few points, type scales snap to a familiar ratio, spacing rounds to a 4px grid
whether or not the site uses one, and component states get invented outright.

So the pipeline measures instead:

- computed styles across every visible element, weighted by rendered area and
  tagged by element role
- the site's own `:root` custom properties — most modern sites ship their design
  tokens in the stylesheet, and reading them is transcription, not inference
- real `@media` breakpoints, `@font-face` rules, theme-color, logo SVG fills
- hover / focus-visible / active deltas by scripted interaction, because states
  are invisible to static analysis
- a dark-mode pass under `prefers-color-scheme: dark`

Then it verifies: `fidelity_check.mjs` decodes the source screenshots and
measures how close the emitted palette gets to the pixels the site actually
renders. That number, not a self-reported confidence score, is what says the
extraction held.

**Run the scripts.** Do not re-derive their work by reading HTML or eyeballing
screenshots, and do not hand-write values into the generated artifacts.

## Pipeline

Full command reference, flags, and troubleshooting: `references/pipeline.md`.

```bash
SKILL=skills/design-system-extractor/scripts
OUT=design-system-output

python3 $SKILL/discover_urls.py https://example.com --out crawl-plan.json --max-pages 14
#   → show the run plan preview and get approval before capturing
node    $SKILL/capture_site.mjs   --urls crawl-plan.json --out $OUT
python3 $SKILL/aggregate_tokens.py $OUT --fidelity-mode modernized
python3 $SKILL/emit_tokens.py      $OUT
node    $SKILL/fidelity_check.mjs  --out $OUT
#   → write the narrative reports with Prompts A/B/C, then
python3 $SKILL/validate_output_package.py $OUT
```

| Stage | Does | Key output |
| --- | --- | --- |
| `discover_urls.py` | robots.txt, sitemap, template classification, sample selection | `crawl-plan.json` |
| `capture_site.mjs` | renders and measures each page across viewports, light + dark, with state probes | `evidence/pages/*.json`, screenshots |
| `aggregate_tokens.py` | perceptual colour clustering, scale fitting, contrast, computed confidence | `tokens.source.json`, `measured-raw.json` |
| `emit_tokens.py` | DTCG tokens, layered CSS, Tailwind v3 + v4, preview, contracts | `tokens/*`, `component-contracts.json` |
| `fidelity_check.mjs` | round-trips the tokens against source pixels | `fidelity-report.json` |

Stages 3–5 re-run without re-crawling, so changing the fidelity mode or
threshold is cheap.

Also available: `validate_intake_config.py` (validate config before crawling),
`render_run_plan.py` (render the preview), `init_output_package.py` (scaffold
the tree).

## Guardrails

- **Public pages only.** Refuse authenticated crawling, credential entry,
  private route probing, and access-control bypass.
- **Respect `robots.txt`** unless the user explicitly disables it and policy
  permits. Never spoof identity to evade bot protection — report the limit and
  reduce scope.
- **Show the run plan before capturing.** No crawling until it is reviewed.
- **Site-inspired, not cloned.** Do not reproduce source page layouts.
- **Assets need rights.** Measured logo *colours* are brand facts and are fine
  to use. Logo *artwork*, illustrations, and photography are not.

## What to preserve, and what to fix

Preserve brand character, tone of voice, colour character, typography feel,
layout rhythm, and icon/image style cues.

Normalize inconsistent spacing and sizing, outdated interaction patterns,
inaccessible contrast, unclear focus states, component drift, and one-off page
anomalies.

Sort every finding into `Preserve`, `Preserve but Normalize`, `Improve`, or
`Exclude`, and record the rationale in the PNIE matrix.

## Fidelity modes

`aggregate_tokens.py --fidelity-mode`:

- **`verbatim`** — report exactly what the site does. No snapping, no pruning.
- **`modernized`** (default) — snap off-grid spacing, prune accidental variants.

Both keep the complete measurements in `evidence/measured-raw.json` and log
every change in `evidence/raw-vs-canonical-diff.md`. **Never normalize
silently, and never present a normalized value as an observation.** Run
`verbatim` first when the goal is to understand the source.

## Confidence and honesty

Confidence is computed from coverage, instance count, rendered area, and whether
the site declares the value itself — formula in `references/confidence-model.md`.
It is never asserted or hand-edited.

- Label low-confidence claims; never silently promote or drop them.
- Cite evidence by `page_id`.
- Continue on partial capture; document the degradation and the blind spots.
- Do not fabricate a value to fill a gap.
- Confidence and fidelity are independent. A run can be confident and
  unfaithful — consistently measuring a cookie banner scores high on coverage.
  Read both reports.

**Anything not measured is a recommendation, and must be labelled as one.** This
applies especially to component states: `component-contracts.json` tags every
state `measured` or `recommended`, and the narrative spec must preserve that
distinction.

## Output

Layered **primitive → semantic → component** tokens. A flat dump cannot be
rethemed — every consumer ends up hardcoding primitives. Dark mode overrides the
semantic layer only.

Emit both Tailwind v3 (`tailwind.theme.js`) and v4 (`tailwind.theme.css`): the
two configure themes in completely different places, and shipping one guesses
the consumer's version. Both resolve CSS custom properties rather than literals,
so retheming works without a rebuild.

Open `tokens/preview.html` to eyeball the result — every token plus components
built only from those tokens. If it looks like the brand, the extraction held.

Required sections, artifact shapes, and folder structure:
`references/output-package.md`.

## Progress reporting

Report per stage: pages captured, warnings and errors, confidence summary, and —
once stage 5 runs — the fidelity grade. Surface capture failures immediately
rather than at the end; a page that failed to load silently degrades every token
downstream.

## References

Load as needed:

- `references/pipeline.md` — commands, stage detail, environment, degraded runs
- `references/confidence-model.md` — the confidence formula and how to read it
- `references/extraction-requirements.md` — coverage targets and measurement sources
- `references/component-contract-schema.md` — `component-contracts.json` schema
- `references/output-package.md` — required sections, artifacts, folder structure
- `references/wizard-and-config.md` — intake checklist and config schema
- `references/qa-validator-checklist.md` — validation gates before handoff
- `references/prompt-chain.md` — Prompts A/B/C, which run over measured JSON
