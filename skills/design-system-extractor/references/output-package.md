# Output Package and Artifacts

Two kinds of artifact: **generated** (written by the pipeline scripts, never by
hand) and **narrative** (written by the synthesis prompts). Generated artifacts
are the evidence; narrative artifacts interpret them and must not contradict
them.

## Folder structure

```text
/design-system-output/
  reports/
    executive-summary.md                  narrative
    source-audit.md                       narrative
    brand-dna.md                          narrative
    accessibility-audit.md                narrative
    preserve-normalize-improve-exclude.md narrative
    fidelity-check.md                     generated — fidelity_check.mjs
  tokens/
    tokens.json                           generated — DTCG format
    tokens.css                            generated — 3 layers + dark mode
    tailwind.theme.js                     generated — Tailwind v3
    tailwind.theme.css                    generated — Tailwind v4 @theme
    tokens.source.json                    generated — canonical set + change log
    preview.html                          generated — token + component gallery
  components/
    component-library-spec.md             narrative
    component-contracts.json              generated — measured contracts
  patterns/
    page-template-patterns.md             narrative
  evidence/
    crawl-manifest.json                   generated
    measured-raw.json                     generated — every observation, unmodified
    extraction-confidence.json            generated — computed scores
    contrast-findings.json                generated — WCAG + suggested fixes
    component-observations.json           generated — measured state deltas
    dark-mode.json                        generated
    fidelity-report.json                  generated — round-trip verification
    raw-vs-canonical-diff.md              generated — every normalization
    page-weights.json                     narrative — cluster weighting rationale
    pages/<page_id>.json                  generated — per-page measurements
    screenshots/*.png                     generated
    html/<page_id>.html                   generated
```

`init_output_package.py` creates the directories and placeholders for the
narrative files only. It deliberately does **not** stub the generated ones: an
empty placeholder where a measurement should be hides a stage that failed to
run.

## Required report sections

1. **Executive Summary** — brand/design DNA, modernization strategy, key risks,
   the fidelity grade, and explicit non-derivative language.
2. **Source Audit** — template clusters, page weighting, included/excluded pages
   with reasons, capture warnings, coverage gaps.
3. **Brand DNA (Visual + Voice)** — visual summary, voice/tone, messaging and
   CTA guidance. Cite evidence page ids.
4. **Design Tokens** — human-readable tables mirroring `tokens.json`. State the
   source (`declared` vs `measured`) and confidence per token group.
5. **Component Library Spec** — per component: purpose, anatomy, variants,
   states, content guidance, accessibility, implementation. Mark every state
   `measured` or `recommended`.
6. **Page / Template Patterns** — marketing, feature, docs/help, dashboard,
   form-heavy workflow, table-centric.
7. **Designer Handoff** — Figma page structure, token and component naming,
   variant/property strategy, starter component set.
8. **Developer Handoff** — how to consume the three token layers, Tailwind v3 vs
   v4 selection, component style contracts, responsive and state requirements.
9. **Preserve / Normalize / Improve / Exclude Matrix** — decisions and rationale,
   cross-referenced to `raw-vs-canonical-diff.md`.
10. **Evidence + Confidence** — crawl manifest summary, confidence report,
    fidelity grade, warnings.

## Consuming the token layers

`tokens.css` is layered. Consumers alias the **semantic** and **component**
layers; the primitive layer is an implementation detail.

```css
--ds-blue-600: #0b5fff;                                      /* primitive */
--ds-color-action-background: var(--ds-blue-600);            /* semantic   */
--ds-button-primary-bg: var(--ds-color-action-background);   /* component  */
```

Dark mode overrides the semantic layer only, under both
`@media (prefers-color-scheme: dark)` and `[data-theme="dark"]`.

Tailwind: v3 takes `tailwind.theme.js`, v4 takes `tailwind.theme.css`. Both
resolve CSS custom properties rather than literal values, so dark mode and
retheming work without a rebuild. Ship both and let the project pick.

## Generated artifact shapes

### `tokens.json` — DTCG with provenance

```json
{
  "$schema": "https://tr.designtokens.org/format/",
  "color": {
    "primitive": { "blue-600": { "$value": "#0b5fff", "$type": "color" } },
    "semantic": {
      "action-background": {
        "$value": "{color.primitive.blue-600}",
        "$type": "color",
        "$extensions": {
          "psdsm": {
            "resolved": "#0b5fff",
            "confidence": 0.938,
            "status": "canonical",
            "declared_as": "custom-property:--brand-primary",
            "evidence_pages": ["p_00_home", "p_01_pricing"]
          }
        }
      }
    }
  }
}
```

### `extraction-confidence.json`

```json
{
  "schema": "psdsm/extraction-confidence@2",
  "threshold": 0.7,
  "fidelity_mode": "modernized",
  "model": {
    "formula": "0.45*coverage + 0.25*instances + 0.20*area + 0.10*declared - spread_penalty",
    "weights": { "coverage": 0.45, "instances": 0.25, "area": 0.2, "declared": 0.1 }
  },
  "pages_measured": 6,
  "tokens": {
    "color.action.background": {
      "confidence": 0.938,
      "status": "canonical",
      "evidence_refs": ["p_00_home", "p_01_pricing"],
      "declared_as": "custom-property:--brand-primary"
    }
  },
  "components": {
    "button||btn.btn-primary": {
      "measured_states": ["hover", "focus_visible", "active"],
      "unmeasured_states": [],
      "has_visible_focus_indicator": true
    }
  },
  "low_confidence_tokens": ["color.text.accent"],
  "warnings": []
}
```

### `fidelity-report.json`

```json
{
  "schema": "psdsm/fidelity-report@1",
  "summary": {
    "pages_scored": 6,
    "mean_palette_delta_e": 0.0027,
    "mean_pixel_share_covered": 0.953,
    "palette_fidelity": "high",
    "components_compared": 2
  }
}
```

### `crawl-manifest.json`

```json
{
  "schema": "psdsm/crawl-manifest@2",
  "source_url": "https://example.com/",
  "viewports": ["desktop", "mobile"],
  "dark_mode_pass": true,
  "state_probe_pass": true,
  "pages": [
    {
      "page_id": "p_00_home",
      "url": "https://example.com/",
      "template_guess": "home",
      "status": 200,
      "measurement_file": "evidence/pages/p_00_home.json",
      "captures": {
        "desktop_fold_screenshot": "evidence/screenshots/p_00_home.desktop.fold.png",
        "desktop_full_screenshot": "evidence/screenshots/p_00_home.desktop.full.png",
        "desktop_consent": { "dismissed": true, "method": "selector:#onetrust-accept-btn-handler" },
        "html": "evidence/html/p_00_home.html"
      },
      "warnings": []
    }
  ],
  "errors": []
}
```

`page-weights.json` keeps its existing shape: `clusters[]` with `cluster_id`,
`template_guess`, `pages`, `cluster_weight`; and `pages[]` with `page_id`,
`quality_weight`, `reasons`.

## Review and export

Present these sections for review: Executive Summary, Source Audit, Brand DNA,
Design Tokens, Component Library Spec, Page Patterns, Accessibility Audit,
**Fidelity Check**, Preserve/Normalize/Improve/Exclude, Developer Handoff,
Evidence + Confidence.

Offer: open `tokens/preview.html`; export the full package; re-run a single
stage; save settings as a preset.

Selective regeneration is cheap because the stages are separate — changing the
fidelity mode or threshold re-runs stages 3–5 with no re-crawl:

```bash
python3 aggregate_tokens.py $OUT --fidelity-mode verbatim
python3 emit_tokens.py $OUT
node fidelity_check.mjs --out $OUT
```

## Non-derivative language requirement

Include in the final package, explicitly:

- This preserves brand character and tone while normalizing inconsistency and
  improving accessibility. It is a modernized baseline, **not a clone**.
- Source page layouts are not reproduced.
- Protected assets — logos, illustrations, photography, icon sets — require
  reuse rights or replacement. Measured logo *colours* are brand facts and are
  fine to use; the logo artwork itself is not.
- State what is preserved, what is normalized or improved, what must not be
  copied, and how future work stays on-brand without replicating the source.
