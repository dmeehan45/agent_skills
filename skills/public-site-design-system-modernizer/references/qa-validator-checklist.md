# QA / Validator Checklist

Run after synthesis, before handoff. Much of this is automated by
`scripts/validate_output_package.py` — run it, then work the items it cannot
check. Continue on partial failures but mark degraded confidence.

## 0) Measurement integrity (blocking)

Before anything else, confirm the package is measured rather than inferred.
`validate_output_package.py` fails if any of these is missing:

- `evidence/crawl-manifest.json`, `evidence/measured-raw.json`
- `evidence/extraction-confidence.json` with a `model.formula`
- `evidence/contrast-findings.json`, `evidence/component-observations.json`
- `evidence/raw-vs-canonical-diff.md`
- `tokens/tokens.source.json`, `tokens.json`, `tokens.css`, both Tailwind files,
  `preview.html`
- `components/component-contracts.json`

A missing artifact means a stage did not run. Re-run it — do not backfill by
hand, and do not use `--allow-unmeasured` for a handoff package.

Also check: `pages_measured >= 1`; every page has screenshots; consent was
dismissed where a banner exists (`captures.<viewport>_consent.dismissed`).

## 1) Fidelity (blocking)

From `evidence/fidelity-report.json`:

- Mean palette ΔE **≤ 0.03** high, **≤ 0.07** moderate, **> 0.07 fails**.
- Dominant pixel share covered ≥ 75%; below that, a surface colour is probably
  missing or imagery dominates the page.
- Component comparisons: dominant ΔE near zero for the primary button and input.
  A large delta means the component token layer is not resolving to what the
  site renders.

If fidelity is low, the fault is usually colour role assignment, not the
palette. Check `evidence/measured-raw.json` role breakdowns before touching
anything else.

Confidence and fidelity are independent. A run can be confident and unfaithful —
consistently measuring a cookie banner scores high on coverage. Read both.

## 2) Accessibility

- **Contrast** — every failing pair in `contrast-findings.json` has an
  `accessible_alternative`. Alternatives move OKLCH lightness only, holding hue
  and chroma, so brand character survives. Verify thresholds used the real font
  size and weight (3.0 for large text, 4.5 otherwise).
- **Focus** — `has_visible_focus_indicator` true for every interactive contract.
  A measured UA default (`outline: 1px auto`) means the site never styled its
  ring: a real finding and an improvement opportunity, not missing data. Build
  rings from `focus_visible`, not `focus`.
- **Touch targets** — `meets_44px_touch_target` on interactive contracts; flag
  and recommend where measured height falls short.
- **Status communication** — never colour alone.
- **Readability** — text sizes and line heights for dense views.
- **Forms** — labels, helper text, error messages, validation clarity.
- **Keyboard** — navigability notes where inferable.
- **Motion** — reduced-motion guidance whenever motion tokens exist. Durations
  are measured, so "no motion system" must mean the census found none.

## 3) Token consistency

- Names match across `tokens.json`, `tokens.css`, both Tailwind files, and the
  reports.
- No contradictory values for one token.
- The three layers are intact: primitives are raw, semantics alias primitives,
  component tokens alias semantics. No component token holding a literal.
- Dark mode overrides the semantic layer only. If the source has dark mode,
  `dark-mode.json.supported` must be true and `tokens.css` must carry both the
  media query and the `[data-theme="dark"]` block.
- Low-confidence tokens are labelled in all three places (JSON status, CSS
  comment, confidence report) — never silently promoted or dropped.
- Breakpoints came from the site's own `@media` rules, not convention.

## 4) Component completeness

Per `component-contract-schema.md`:

- Purpose, anatomy, variants, spacing, content guidance, accessibility,
  implementation notes.
- States `default`, `hover`, `focus-visible`, `active`, `disabled`; plus
  `loading`, `error`, `selected`, `empty` where applicable.
- **Every state carries `source: measured | recommended`.** Untagged states fail
  validation. Anything in `unmeasured_states` is design work and must be
  presented that way in the narrative spec too.
- The narrative spec did not overwrite `base`, `states[].changes`, `evidence`,
  or `unmeasured_states`.

Flag missing state guidance; never silently omit it.

## 5) Normalization honesty

- `raw-vs-canonical-diff.md` exists, names the fidelity mode, and lists every
  change with a rationale.
- No normalization happened that is absent from the diff.
- `measured-raw.json` still holds the complete unmodified observations.
- The PNIE matrix cross-references the diff.
- No normalized value is presented anywhere as an observation.

## 6) Over-literal copying (blocking)

Flag and revise if outputs:

- mirror exact source page layouts
- encode one-off campaign styling as canonical
- reuse copyrighted assets without rights confirmation — measured logo
  *colours* are brand facts and fine; the logo *artwork* is not
- reuse source copy blocks as reusable component content guidance

Require explicit non-derivative language: what to preserve, what to
normalize/improve, what not to copy.

## 7) Confidence

- Every weak-evidence area marked.
- Threshold applied consistently; fallback behaviour consistent.
- Evidence page ids exist for material claims.
- No hand-edited confidence scores — they are computed from
  `confidence-model.md`.

## 8) Degraded runs

Handle and report, do not paper over: robots restrictions, timeouts,
cross-origin stylesheets (`cssom.sheets_blocked`), JS-heavy pages with thin
capture, redirect loops, low-signal pages, blocked assets, sparse component
evidence, bot protection.

Continue when partial evidence suffices, lower confidence, name the blind spots,
and provide fallbacks. Never fabricate a value to fill a gap.

## Outputs

- `reports/accessibility-audit.md`
- `reports/fidelity-check.md` (generated)
- `evidence/extraction-confidence.json` (generated)
- Validator findings summarised in the Executive Summary and Source Audit
