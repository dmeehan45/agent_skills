# Measurement Pipeline

Five scripts, run in order. Each writes machine-readable artifacts the next one
reads. Run them — do not re-derive their work by reading HTML or eyeballing
screenshots. Measurement is what makes the extraction faithful; inference is
what produces plausible-but-wrong tokens.

```bash
SKILL=skills/design-system-extractor/scripts
OUT=design-system-output

# 1. discover — robots.txt, sitemap, template classification, sample selection
python3 $SKILL/discover_urls.py https://example.com --out crawl-plan.json --max-pages 14

# ---- show the run plan preview and get approval before step 2 ----

# 2. capture — render every page and measure it
node $SKILL/capture_site.mjs --urls crawl-plan.json --out $OUT

# 3. aggregate — cluster, fit scales, score confidence (deterministic)
python3 $SKILL/aggregate_tokens.py $OUT --fidelity-mode modernized

# 4. emit — DTCG tokens, layered CSS, Tailwind v3 + v4, preview, contracts
python3 $SKILL/emit_tokens.py $OUT

# 5. verify — round-trip the tokens against the source pixels
node $SKILL/fidelity_check.mjs --out $OUT

# ---- write the narrative reports (Prompts A/B/C), then ----
python3 $SKILL/validate_output_package.py $OUT
```

## Environment

`capture_site.mjs` and `fidelity_check.mjs` need Playwright and a Chromium
build. They resolve Playwright from local `node_modules`, then
`PLAYWRIGHT_MODULE_PATH`, then the global npm root. They never download a
browser. If resolution fails:

```bash
export PLAYWRIGHT_MODULE_PATH=$(npm root -g)/playwright
# or, when only NODE_PATH is set up:
NODE_PATH=$(npm root -g) node $SKILL/capture_site.mjs ...
```

The Python scripts use the standard library only.

---

## Stage 1 — `discover_urls.py`

Fetches `robots.txt`, follows declared sitemaps (including sitemap indexes),
falls back to a shallow static link crawl when the sitemap is thin, classifies
each URL into a template type, and selects a diverse sample using round-robin
across template buckets so coverage beats depth.

**Writes:** `crawl-plan.json` — pages with `page_id`, `template_guess`,
`selection_reason`, `evidence_scope`, plus `excluded[]` with reasons,
`template_coverage`, and `coverage_gaps`.

Key flags: `--max-pages`, `--per-template`, `--no-robots` (needs explicit user
authorisation), `--include-typography-only`.

**On legal pages:** `/legal`, `/privacy`, `/terms` are excluded by default but
tagged `evidence_scope: typography_only` when included. They carry the site's
cleanest long-form body copy and link styling with no marketing noise — good
typography evidence, bad brand-voice evidence. Never let them influence tone
extraction.

Static link discovery misses JS-rendered navigation. `capture_site.mjs` records
the links it sees in a real browser under `measurements.desktop.links`; feed
those back for a second discovery pass on SPA sites.

## Stage 2 — `capture_site.mjs`

The measurement layer. Per page, per viewport (desktop 1440×900, tablet
834×1112, mobile 390×844):

- dismisses cookie/consent overlays (vendor selectors, then button text, then
  hides large fixed overlays whose text reads like a consent notice)
- scrolls the full page to trigger lazy-loading, then returns to top
- freezes animations and transitions so screenshots are deterministic
- runs an in-page census: every visible element's computed styles, weighted by
  rendered area and tagged with an inferred role (`control.button`,
  `heading.h1`, `nav.link`, `region.footer`, …)
- harvests the CSSOM: `:root` custom properties, `@media` breakpoint values,
  `@font-face` rules, `@keyframes` names
- resolves text/background contrast pairs against the nearest painted ancestor
- fingerprints the icon system, framework, brand assets, and logo SVG colours
- probes interaction states by scripted hover, keyboard focus, and mouse-down

**Writes:** `evidence/pages/<page_id>.json` per page,
`evidence/crawl-manifest.json`, `evidence/screenshots/*.png` (fold + full page,
per viewport, plus a dark-mode fold), `evidence/html/<page_id>.html`.

Key flags: `--viewports desktop,tablet,mobile`, `--no-dark`, `--no-states`,
`--no-consent`, `--max-elements`, `--settle-ms`, `--user-agent`.

### Why each pass matters

| Pass | Without it |
| --- | --- |
| Computed-style census | Every token is guessed from markup; hex values drift |
| `:root` custom properties | You re-derive tokens the site already publishes |
| CSSOM `@media` harvest | Breakpoints are invented from convention |
| Interaction state probe | Component states are fabricated — they are unobservable in static HTML |
| Dark-mode pass | The token set is light-only |
| Consent dismissal | Screenshots and colour measurements capture the banner |
| Animation freeze | Screenshots are non-deterministic; fidelity scores wobble |

### Interaction state probing

Runs on desktop, before animations are frozen so transitions are real. For each
distinct interactive signature (tag + type + first three classes) it reads the
base computed style, then diffs against hover, keyboard focus, `:focus-visible`
(reached via Tab so it is distinguishable from plain `:focus`), and active.

Note that `active` implies hover, so the active delta normally contains the
hover changes too. Disabled styling is read declaratively from
`[disabled]`/`[aria-disabled="true"]` elements rather than synthesised.

## Stage 3 — `aggregate_tokens.py`

Deterministic. The same measurements always produce the same tokens — no model
judgement enters here.

- **Colour:** perceptual clustering in OKLab (ΔE ≤ 0.025). Hex equality misses
  `#1a73e8` vs `#1b74e9`; those are one brand colour with two implementations
  and must merge before roles are assigned. Roles come from *where the colour is
  painted*, not how often — button backgrounds are distinguished from field
  backgrounds, headings from body from links. A colour serving two roles is
  emitted under both.
- **Typography:** families ranked by rendered-area share; type scale fitted to
  the observed ladder and matched against named ratios only when it is close.
  Sizes are retained if they have ≥2 instances, ≥2% of text area, or a heading
  role — the h1 usually appears once per page but is the most brand-defining
  size on the site.
- **Spacing:** the base unit is the *largest* candidate explaining ≥80% of
  observed values. Scoring on conformance alone always collapses to 2px, which
  describes nothing.
- **Radius, elevation, motion, breakpoints, containers, z-index, icons:** ladders
  built from measured values with instance counts retained.
- **Contrast:** WCAG ratio per measured pair, using the real font size and
  weight to pick the 3.0 or 4.5 threshold. Failures get an alternative found by
  moving OKLCH lightness only, holding hue and chroma — that is what preserves
  brand colour character.
- **Dark mode:** the dark-pass measurements go through the same colour pipeline.

**Writes:** `evidence/measured-raw.json` (everything observed, nothing
normalized), `tokens/tokens.source.json` (canonical set + change log),
`evidence/extraction-confidence.json`, `evidence/contrast-findings.json`,
`evidence/component-observations.json`, `evidence/dark-mode.json`,
`evidence/raw-vs-canonical-diff.md`.

Key flags: `--fidelity-mode {modernized,verbatim}`, `--threshold`.

See `confidence-model.md` for how confidence is computed.

## Stage 4 — `emit_tokens.py`

Turns candidates into artifacts a codebase can consume.

Tokens are layered **primitive → semantic → component**:

```css
--ds-blue-600: #0b5fff;                            /* primitive: measured */
--ds-color-action-background: var(--ds-blue-600);  /* semantic: alias this */
--ds-button-primary-bg: var(--ds-color-action-background);  /* component */
```

A flat dump cannot be rethemed — every consumer ends up hardcoding primitives.
Dark mode overrides the **semantic layer only**, via both
`@media (prefers-color-scheme: dark)` and `[data-theme="dark"]`.

**Writes:** `tokens/tokens.json` (DTCG `$value`/`$type`, with measurement
provenance under `$extensions.psdsm`), `tokens/tokens.css`,
`tokens/tailwind.theme.js` (v3), `tokens/tailwind.theme.css` (v4 `@theme`),
`tokens/preview.html`, `components/component-contracts.json`.

Both Tailwind outputs resolve CSS custom properties rather than literals, so
dark mode and retheming work without a rebuild. Emit both and let the consuming
project pick; v3 and v4 configure themes in completely different places.

## Stage 5 — `fidelity_check.mjs`

Confidence says how sure the measurement was. It cannot say whether the result
looks like the brand. This measures that.

1. **Palette fidelity** — decodes each source screenshot in Chromium (the
   browser is the image decoder, so there is no image library to install),
   quantises to dominant colours by pixel share, and finds the nearest emitted
   token for each in OKLab.
2. **Component fidelity** — screenshots the real element on the live site and
   the token-built equivalent from `preview.html`, then compares dominant
   colour and box metrics. Applies the same consent dismissal and animation
   freeze as capture, or it would measure the cookie banner.

**Writes:** `evidence/fidelity-report.json`, `reports/fidelity-check.md`.

Grading on pixel-share-weighted mean OKLab ΔE:

| Mean ΔE | Grade | Meaning |
| --- | --- | --- |
| ≤ 0.03 | high | The palette reproduces what the site renders |
| ≤ 0.07 | moderate | Spot-check `preview.html` before relying on it |
| > 0.07 | low | **Blocking.** Re-check colour role assignment and capture coverage |

`validate_output_package.py` fails the package on a `low` grade.

Colours in the report with no close token are usually photography, gradients, or
third-party embeds. Confirm before adding them — imagery is not a design token.

Flags: `--no-live` (skip live element comparison), `--min-share`.

---

## Fidelity modes

`--fidelity-mode` on stage 3 controls how much normalization is applied.

| | `modernized` (default) | `verbatim` |
| --- | --- | --- |
| Off-grid spacing | snapped to the base unit | kept as measured |
| Single-instance type sizes | pruned unless heading or ≥2% area | all kept |
| Single-instance radii | pruned | all kept |
| Third+ font families | dropped from canonical | all kept |
| Near-identical colours | merged (ΔE ≤ 0.025) | merged (always — they are the same colour) |

Both modes write `evidence/raw-vs-canonical-diff.md` listing every change with
its rationale, and both keep the complete unmodified measurements in
`evidence/measured-raw.json`. Nothing is ever changed silently.

Use `verbatim` first when the goal is to understand what the site actually
does, then re-run in `modernized` for the deliverable. Stage 3 is cheap to
re-run — it does not re-crawl.

## Degraded runs

Continue and report; do not fabricate.

| Situation | Handling |
| --- | --- |
| Cross-origin stylesheets | Counted in `cssom.sheets_blocked`; computed styles still measured, so tokens survive — declared custom properties may be incomplete |
| JS-heavy / SPA pages | Increase `--settle-ms`; feed browser-observed links back into discovery |
| Bot protection / 403 | Recorded in `crawl-manifest.errors`. Do not spoof identity to evade it — report it and reduce scope |
| robots.txt disallows most paths | Respect it. Report reduced coverage and lower confidence |
| Consent banner not dismissed | Check `captures.<viewport>_consent.dismissed`; if false, screenshots and pixel fidelity are suspect |
| Few pages captured | Coverage is 45% of the confidence score, so tokens land below threshold and get labelled — this is correct behaviour, not a bug to override |
