# Prompt Chain (A/B/C)

The prompts run **after** the measurement pipeline, over its JSON output. They
interpret measurements; they do not produce them. Never ask a prompt to estimate
a value that `aggregate_tokens.py` already measured — that is how a faithful
extraction turns back into a plausible guess.

## Shared conventions

- Feed the generated JSON, not raw HTML or CSS: `measured-raw.json`,
  `tokens.source.json`, `extraction-confidence.json`, `contrast-findings.json`,
  `component-observations.json`, `dark-mode.json`, `fidelity-report.json`,
  `crawl-manifest.json`.
- Attach a few representative screenshots. Do not attach all of them.
- Cite evidence by `page_id` and token name, not prose.
- Confidence scores are inputs, never outputs. A prompt may not invent, adjust,
  or round one.
- Any value not present in the measurements must be labelled a recommendation.

## Prompt A — Evidence Interpretation Report

**Purpose:** turn measurements into weighted, human-readable observations
without making canonical decisions.

**Input:** `measured-raw.json`, `crawl-manifest.json`,
`extraction-confidence.json`, `component-observations.json`, sample screenshots.

**Output:**

1. Weighted observations by template cluster
2. What the site declares about itself — `:root` custom properties, theme-color,
   logo colours, `@media` breakpoints — and where measured usage diverges from
   the declaration
3. Visual observations per category: observed variants, accidental variants,
   measured confidence
4. Verbal/voice candidates: tone, CTA style, messaging hierarchy, vocabulary
   (excluding `typography_only` pages)
5. Component inventory with measured state coverage and gaps
6. Layout and rhythm observations
7. Included/excluded page rationale
8. Weak-evidence zones, taken from the confidence report

**Rules:** extractive only. Do not choose canonical values. Do not restate a
measured number as an estimate. Divergence between what the site declares and
what it renders is a finding — surface it.

```text
You are producing Prompt A (Evidence Interpretation) for a brand-faithful
modernization workflow. Work only from the attached measurement JSON.

The values are already measured. Your job is to interpret and weight them, not
to re-estimate them. Quote measured numbers exactly; never round or adjust a
confidence score.

Return: (1) weighted observations by cluster, (2) declared-vs-rendered
divergence, (3) visual observations with variants and confidence, (4) voice
candidates, (5) component inventory with state coverage, (6) layout and rhythm,
(7) included/excluded page rationale, (8) weak-evidence zones.

Do not choose canonical values. Label every uncertainty.
```

## Prompt B — Brand-Faithful Modernization Synthesis

**Purpose:** turn interpreted evidence into the narrative design system around
the already-emitted token artifacts.

**Input:** Prompt A output, `tokens.source.json`, `tokens.json`,
`component-contracts.json`, `raw-vs-canonical-diff.md`, config.

**Output:** Executive Summary, Source Audit, Brand DNA, token documentation
mirroring `tokens.json`, component library spec, page/template patterns, PNIE
matrix, designer and developer handoff.

**Rules:**

- The emitted tokens are the source of truth. Document them; do not restate them
  with different values. Disagreement with a token means fixing stage 3, not
  writing a different number.
- Preserve brand character; normalize implementation drift; improve
  accessibility.
- Every normalization you describe must already appear in
  `raw-vs-canonical-diff.md`.
- Mark each component state `measured` or `recommended`.
- No exact page-layout reproduction, no protected-asset reuse.
- Label low-confidence decisions using the emitted status values.

```text
You are producing Prompt B (Brand-Faithful Modernization Synthesis).

The token set in tokens.json is already measured and emitted. Document and
explain it — do not regenerate or alter values. If you believe a token is wrong,
say so explicitly as a finding rather than quietly writing a different number.

Requirements:
- Preserve brand character (tone, colour character, typography feel, layout rhythm)
- Normalize implementation drift; every normalization must already be in the diff report
- Integrate accessibility improvements from contrast-findings.json
- Mark every component state as measured or recommended
- Do not reproduce exact layouts or copy protected assets
- Use the emitted confidence status to label uncertain decisions

Return all narrative sections required by output-package.md.
```

## Prompt C — QA Critique and Repair

**Purpose:** critique the synthesis against the measurements and validator
findings, then patch minimally.

**Input:** Prompt B output, Prompt A summary, `validate_output_package.py`
output, `fidelity-report.json`, `contrast-findings.json`,
`extraction-confidence.json`.

**Output:** contradictions and fixes; missing states/anatomy; risky colour pairs
with accessible alternatives; over-literal sections; unsupported certainty
claims; revised sections ready for packaging.

**Rules:** critique first, then patch. Prefer minimal changes. Preserve
brand-faithful intent.

Priority order:

1. Claims that contradict the measurements — the highest-value defect this pass
   catches, and the one most likely to survive into the deliverable
2. Fidelity failures (mean palette ΔE > 0.07)
3. Accessibility failures without a suggested alternative
4. Component states presented as measured that are actually recommended
5. Missing states or anatomy
6. Token inconsistency across JSON / CSS / Tailwind / reports
7. Over-literal copying risk
8. Unsupported certainty claims

```text
You are Prompt C (QA Critique and Repair).

First identify defects. Check every quantitative claim in the synthesis against
the measurement JSON — a number in the prose that does not match the measured
value is the defect to find first.

Then patch, minimally, in this priority order:
1) Claims contradicting the measurements
2) Fidelity failures
3) Accessibility failures lacking an alternative
4) Recommended states presented as measured
5) Missing component states or anatomy
6) Token inconsistency across artifacts
7) Over-literal copying risk
8) Unsupported certainty

Do not alter measured values, confidence scores, or emitted tokens. Report those
as findings for a pipeline re-run instead.
```

## Machine-readable intermediates

- `prompt-a.evidence-report.json`
- `prompt-b.synthesis-draft.json`
- `prompt-c.revisions.json`

These make runs reproducible and let sections be regenerated independently.
Because measurement and synthesis are separate, a prompt can be re-run without
re-crawling — and stages 3–5 can be re-run without touching the prompts.
