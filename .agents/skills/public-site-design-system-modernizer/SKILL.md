---
name: public-site-design-system-modernizer
description: Generate a brand-faithful modernized design system from a public website (public pages only) by crawling a bounded representative sample, extracting visual/voice/component evidence, and producing normalized designer/developer handoff artifacts with accessibility and confidence reporting. Use when Codex needs to analyze a public site and create a site-inspired (not cloned) design system, tokens, component specs, and page patterns.
---

# Public Site Design System Modernizer

Create a brand-faithful modernization package for a **public website**. Preserve recognizable brand character while normalizing inconsistency, improving accessibility, and avoiding exact duplication.

## Product principle (enforce explicitly)

Preserve:

- brand character
- tone of voice
- color character
- typography feel
- layout rhythm
- icon/image style cues (when detectable)

Modernize:

- inconsistent spacing and sizing
- outdated interaction patterns
- inaccessible contrast combinations
- unclear focus states
- component drift across templates
- one-off page anomalies

Do not:

- reproduce exact page layouts by default
- treat every page as equal truth
- encode legacy inconsistencies as canonical tokens
- claim certainty when evidence is weak

## Use this skill correctly

- Restrict scope to **publicly accessible pages** only.
- Refuse authenticated crawling, credential entry, private route probing, or bypass attempts.
- Treat mode as fixed: **Brand-Faithful Modernization**.
- Produce **site-inspired, normalized outputs**, not source clones.
- Respect `robots.txt` by default (required unless the user explicitly disables and platform policy permits).
- Exclude direct reuse of copyrighted logos/illustrations/images unless the user confirms rights.

## Required workflow (follow in order)

1. Validate intake and public-site guardrails.
2. Build and show a **run plan preview** before crawling.
3. Crawl/capture a bounded page set (representative sample by default).
4. Normalize sources (template clustering + page weighting).
5. Extract evidence (visual DNA, voice DNA, component patterns).
6. Run multi-prompt synthesis pipeline (Prompts A/B/C).
7. Validate accessibility + consistency + anti-patterns.
8. Package exports in the required folder structure.

Do not start crawling before the run plan preview is shown.

## Default operating profile (v1)

- Mode: Brand-Faithful Modernization
- Scope: Representative sample (recommended)
- Screenshots: Desktop + mobile (default on)
- Capture: HTML + CSS + text + screenshots + asset metadata
- Respect robots.txt: On
- Contrast checks: On
- Anti-pattern report: On
- Preserve/Normalize/Improve/Exclude matrix: On
- Canonical token confidence threshold: `0.70`
- Low-confidence fallback: Suggest candidates; do not assert exact values

## Wizard flow (required fields)

Collect and enforce the following (see `references/wizard-and-config.md` for exact checklist and config schema):

1. Project Intent
- Project name
- Public source URL
- Output audience (`designer`, `developer`, `both`)
- Intended use (`internal exploration`, `client work`, `rebuild baseline`)
- Show warning: outputs are inspired + normalized, not clones

2. Crawl Scope (public web only)
- Crawl mode: `representative_sample` (default), `bounded_full`, `custom_urls`, `sitemap`
- `max_pages`, `max_depth`, `include_subdomains`
- `exclude_paths`
- `respect_robots_txt`
- Rate limiting / crawl delay
- Prefer template diversity over page count

3. Public Website Guardrails (explicit confirmations)
- Publicly accessible source
- User understands non-clone workflow
- User understands asset reuse may require rights/replacement

4. Capture / Extraction settings
- Desktop screenshots required
- Mobile screenshots recommended (default on)
- Tablet optional
- HTML/DOM, CSS, text, asset metadata, component candidates

5. Output package selection
- Default to full handoff package
- Markdown + JSON required, YAML optional

6. Quality / confidence controls
- Token confidence threshold
- Low-confidence fallback behavior
- Contrast checks / anti-pattern report / PNIE matrix toggles (default on)

7. Run plan preview (required)
- URLs, inclusions/exclusions, limits, capture settings, outputs, warnings, workload class

## Crawler and capture guidance

- Prefer representative template coverage over scraping every page.
- Include likely template types when available: home, feature/product, pricing, docs/help, blog/article, contact/sales, form/workflow, publicly accessible app-like page.
- Skip obvious low-value or noisy routes unless explicitly requested (`/legal`, `/privacy`, `/terms`, `/login`, campaign one-offs, redirects, duplicate query-param variants).
- Log redirects, failures, timeouts, blocked assets, JS-heavy capture gaps.
- Capture screenshots because DOM/CSS alone is insufficient for hierarchy/rhythm.

If browser automation is needed, use the local `playwright` skill when available.

## Pipeline modules (required responsibilities)

Implement or simulate a modular pipeline with these stages:

1. Intake / Config
- Validate public URL and guardrails
- Parse wizard inputs
- Resolve crawl mode and store normalized config

2. Crawler / Capture (public only)
- Respect bounds, robots, exclusions
- Collect screenshots + HTML/CSS/text + asset metadata
- Dedupe and avoid loops

3. Normalizer
- Cluster by template
- Weight pages by signal quality
- Separate core brand pages from one-offs/noise
- Dedupe repeated component instances

4. Extractor
- Produce token/voice/component/layout candidates + confidence scores
- Keep raw variants and accidental variants separate

5. Synthesizer (LLM)
- Convert evidence into a **brand-faithful modernized design system**
- Preserve brand signals; remove design debt
- Generate designer + developer handoff artifacts

6. QA / Validator
- Contrast checks, focus-state requirements, token consistency
- Component anatomy/state completeness
- Over-literal copying risk checks
- Confidence threshold enforcement + fallback policy

7. Packager
- Write markdown reports, JSON artifacts, CSS vars, Tailwind theme
- Emit required output folder structure

## Prompt chain (mandatory: use at least 3 prompts)

Do not use a single giant prompt.

- Prompt A: Evidence Extraction Report (extractive, grounded, cites evidence)
- Prompt B: Brand-Faithful Modernization Synthesis (prescriptive outputs)
- Prompt C: QA Critique and Repair Pass (critique first, then patch)

Use the prompt templates and I/O contracts in `references/prompt-chain.md`.

## Extraction requirements (must cover)

Cover all categories in `references/extraction-requirements.md`:

- Visual DNA: colors, typography, spacing, sizing, radius, borders, shadows, motion, breakpoints, containers, grid/rhythm, icon style, image treatments
- Verbal DNA: tone, sentence style, CTA style, messaging hierarchy, vocabulary, taboo/overused phrases, reading level
- Component patterns: recurring components with anatomy, variants, states, spacing/content/accessibility/implementation notes

For each visual category, keep:

- observed variants
- canonical recommendation
- accidental variants to exclude
- confidence score

## Brand-faithful modernization rules (must enforce)

Explicitly separate findings into:

- `Preserve`: core brand signals that should remain recognizable
- `Preserve but Normalize`: brand-consistent but inconsistent implementations
- `Improve`: accessibility/usability upgrades that keep brand intent
- `Exclude`: noisy/legacy/third-party/low-signal patterns not fit for canon

Never encode legacy inconsistency as canonical tokens.
Never claim certainty when evidence is weak.
Never reproduce exact page layouts by default.

## Accessibility requirements (mandatory)

Integrate accessibility into the modernized system (not as optional notes):

- Contrast risk detection + accessible alternatives
- Visible focus states
- Non-color-only status communication
- Minimum touch targets
- Readable dense text sizing
- Form label/helper/error clarity
- Keyboard navigability notes (when inferable)
- Motion reduction considerations (if motion tokens exist)

Use the checklist in `references/qa-validator-checklist.md`.

## Required outputs

Return all required sections and files listed in `references/output-package.md`.

Minimum deliverables:

- Executive Summary
- Source Audit
- Brand DNA (Visual + Voice)
- Design Tokens (human-readable + `tokens.json`)
- Component Library Spec
- Page / Template Patterns
- Designer Handoff
- Developer Handoff (`tokens.css`, `tailwind.theme.js`, component contracts)
- Preserve / Normalize / Improve / Exclude Matrix
- Evidence + Confidence artifacts

## Confidence and evidence policy

- Label low-confidence claims explicitly.
- Cite the page clusters and evidence used for conclusions.
- Provide fallback outputs when evidence is sparse (ranges, candidate sets, unknown markers).
- Continue on partial capture when sufficient data exists; document degradation.
- Do not fabricate missing evidence.

## Execution progress and review UX requirements

During execution, present stage-based progress (with page count, warnings/errors, partial previews, and confidence summary):

1. Crawl and capture
2. Template grouping and page weighting
3. Visual/verbal/component extraction
4. Design system synthesis
5. QA validation (accessibility + consistency)
6. Packaging and export

After execution, provide review/export sections and actions described in `references/output-package.md` (including selective regeneration and preset saving).

## Non-derivative guardrail language (include in outputs)

State explicitly:

- what is preserved as brand character
- what is normalized/improved
- what must not be copied directly
- how future work stays on-brand without replicating source layouts/assets

## Implementation notes for Codex

- Keep runs reproducible: save normalized config + crawl manifest + page weights + confidence artifacts.
- Prefer compact, machine-readable intermediates (JSON) between modules.
- When evidence is weak, bias toward design-system ranges and rules, not exact clones of observed values.
- If the source is JS-heavy and capture is incomplete, lower confidence and report likely blind spots.

## References (load only as needed)

- `references/wizard-and-config.md`: wizard checklist, config object, run-plan preview structure
- `references/prompt-chain.md`: Prompt A/B/C templates and expected outputs
- `references/qa-validator-checklist.md`: validator checks and failure handling
- `references/extraction-requirements.md`: exhaustive extraction targets and component/state coverage
- `references/output-package.md`: required sections, file structure, and artifact schemas

## Bundled scripts (use when helpful)

- `scripts/init_output_package.py`: scaffold the required `/design-system-output` directory tree and placeholder files for a run
- `scripts/render_run_plan.py`: generate a run-plan preview markdown from normalized config + selected URLs
- `scripts/validate_output_package.py`: validate required artifacts/files and basic JSON/report expectations before handoff
- `scripts/validate_intake_config.py`: validate normalized intake config (schema-style checks) before crawl execution

Prefer these scripts over re-writing scaffolding/validation code during each run.
