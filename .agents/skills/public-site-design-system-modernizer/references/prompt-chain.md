# Prompt Chain (A/B/C)

Use at least these three prompts. Keep inputs structured and include evidence references (page IDs, cluster IDs, screenshot IDs, CSS frequency tables).

## Shared conventions

- Provide `config`, `clusters`, `page_weights`, `capture_manifest`, and validator findings as JSON when possible.
- Attach only representative screenshots; do not overload prompts.
- Use confidence scores in `[0,1]`.
- Cite evidence by IDs, not long prose.

## Prompt A: Evidence Extraction Report (Grounded, Extractive)

Purpose:

- Produce weighted observations and candidate signals without making final canonical design decisions.

Input:

- Structured crawl data
- Screenshot samples
- CSS frequency tables / computed style samples (if available)
- Text samples
- Template clusters + page weights

Required output:

- Weighted observations by cluster
- Visual token candidates + confidence
- Verbal tone candidates + confidence
- Component inventory candidates
- Layout/rhythm observations
- Included/excluded page rationale
- Evidence references used for each claim

Rules:

- Be extractive, not prescriptive
- Do not define final canonical tokens
- Mark weak evidence zones explicitly

Suggested prompt skeleton:

```text
You are producing Prompt A (Evidence Extraction Report) for a brand-faithful modernization workflow.
Use only the provided crawl evidence. Be extractive, not prescriptive.

Return:
1) Weighted observations
2) Visual token candidates (observed variants, accidental variants, confidence)
3) Verbal/voice candidates (tone, CTA style, messaging hierarchy, vocabulary)
4) Component inventory candidates (with recurrence estimates)
5) Layout/rhythm observations
6) Included/excluded page rationale
7) Evidence references per claim

Do not choose final canonical values. Label uncertainty.
```

## Prompt B: Brand-Faithful Modernization Synthesis

Purpose:

- Convert Prompt A evidence into a normalized design system and handoff package.

Input:

- Prompt A output
- User config/settings
- Quality thresholds

Required output:

- Executive summary
- Source audit summary
- Visual + voice DNA
- Canonical token system
- Component library specs (anatomy, variants, states)
- Page/template patterns
- Preserve / Normalize / Improve / Exclude matrix
- Developer handoff artifacts

Rules:

- Preserve recognizable brand signals
- Normalize inconsistency
- Improve accessibility/usability
- Optimize for scalability and developer ergonomics
- Avoid exact cloning / derivative replication
- Mark ambiguity when evidence is weak

Suggested prompt skeleton:

```text
You are producing Prompt B (Brand-Faithful Modernization Synthesis).
Transform the evidence into a site-inspired, normalized design system.

Requirements:
- Preserve brand character (tone, color character, typography feel, layout rhythm)
- Normalize implementation drift and one-offs
- Integrate accessibility improvements
- Do not reproduce exact layouts or copy protected assets
- Label low-confidence decisions

Return all sections required for packaging, including tokens, components, patterns, and dev handoff.
```

## Prompt C: QA Critique and Repair Pass

Purpose:

- Critique Prompt B outputs using evidence + validator findings, then minimally patch issues.

Input:

- Prompt B output
- Prompt A evidence summary
- Validator findings (contrast, completeness, conflicts, copying-risk flags)

Required output:

- Contradictions and fixes
- Missing component states/anatomy fixes
- Risky color pairs + accessible alternatives
- Over-literal sections and revisions
- Revised sections ready for packaging

Rules:

- Critique first, then patch
- Prefer minimal changes that improve quality
- Preserve brand-faithful modernization intent

Suggested prompt skeleton:

```text
You are Prompt C (QA Critique and Repair).
First identify defects and risks in the synthesized design system.
Then provide targeted revisions only where needed.

Prioritize:
1) Accessibility failures
2) Missing component states/anatomy
3) Token inconsistency/conflicts
4) Over-literal copying risk
5) Unsupported certainty claims
```

## Recommended machine-readable intermediates

- `prompt-a.evidence-report.json`
- `prompt-b.synthesis-draft.json`
- `prompt-c.revisions.json`

These improve reproducibility and allow selective regeneration (tokens/components/patterns/dev handoff).
