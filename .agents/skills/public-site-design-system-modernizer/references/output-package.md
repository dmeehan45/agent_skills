# Output Package and Artifacts

Return all sections below. Markdown + JSON are required.

## Required report sections

1. Executive Summary
- Extracted brand/design DNA summary
- Modernization strategy
- Key risks (inconsistency, accessibility, weak evidence)

2. Source Audit
- Page groups/template clusters
- Page weighting summary
- Included/excluded pages and rationale
- Confidence notes

3. Brand DNA (Visual + Voice)
- Visual DNA summary
- Voice/tone summary
- Messaging and CTA guidance

4. Design Tokens
- Human-readable token tables
- `tokens.json` canonical object
- Include: color, typography, spacing, radius, shadow, border, motion, layout

5. Component Library Spec
- For each core component: name, purpose, anatomy, variants, states, usage/content guidance, accessibility notes, implementation notes

6. Page / Template Patterns
- Marketing page
- Feature page
- Docs/help page
- Dashboard/data view page
- Form-heavy workflow page
- Table-centric page

7. Designer Handoff
- Figma page structure recommendation
- Token naming conventions
- Component naming conventions
- Variant/property strategy
- Starter component set

8. Developer Handoff
- CSS variables (`:root`)
- Tailwind theme extension object
- Component style contracts
- Responsive behavior guidance
- State styling requirements

9. Preserve / Normalize / Improve / Exclude Matrix
- Explicit decisions and rationale

10. Evidence + Confidence Artifacts
- Crawl manifest
- Page weights
- Confidence report
- Warnings/errors summary

## Required folder structure

Use this structure (or equivalent with same content):

```text
/design-system-output/
  reports/
    executive-summary.md
    source-audit.md
    brand-dna.md
    accessibility-audit.md
    preserve-normalize-improve-exclude.md
  tokens/
    tokens.json
    tokens.css
    tailwind.theme.js
  components/
    component-library-spec.md
    component-contracts.json
  patterns/
    page-template-patterns.md
  evidence/
    crawl-manifest.json
    page-weights.json
    extraction-confidence.json
```

## Minimal machine-readable artifact shapes

Use stable IDs so reports can cite evidence consistently.

### `crawl-manifest.json` (example shape)

```json
{
  "run_id": "2026-02-23T12-00-00Z_example",
  "source_url": "https://example.com",
  "crawl_mode": "representative_sample",
  "respect_robots_txt": true,
  "pages": [
    {
      "page_id": "p_home",
      "url": "https://example.com/",
      "cluster_id": "c_home",
      "status": 200,
      "captures": {
        "desktop_screenshot": "evidence/screenshots/p_home.desktop.png",
        "mobile_screenshot": "evidence/screenshots/p_home.mobile.png",
        "html": "evidence/html/p_home.html",
        "css_refs": ["evidence/css/p_home.css"]
      },
      "warnings": []
    }
  ],
  "errors": []
}
```

### `page-weights.json` (example shape)

```json
{
  "clusters": [
    {
      "cluster_id": "c_pricing",
      "template_guess": "pricing",
      "pages": ["p_pricing", "p_pricing_alt"],
      "cluster_weight": 0.86
    }
  ],
  "pages": [
    {
      "page_id": "p_pricing",
      "quality_weight": 0.9,
      "reasons": ["high style signal", "core business template", "low third-party noise"]
    }
  ]
}
```

### `extraction-confidence.json` (example shape)

```json
{
  "threshold": 0.7,
  "tokens": {
    "color.brand.primary": {
      "confidence": 0.92,
      "evidence_refs": ["p_home", "p_pricing", "c_marketing"]
    },
    "radius.card.md": {
      "confidence": 0.46,
      "status": "low_confidence_candidate",
      "fallback": "suggest_candidates"
    }
  },
  "components": {
    "button": {
      "confidence": 0.9,
      "missing_states": ["loading"]
    }
  },
  "warnings": ["JS-heavy docs pages limited computed style capture"]
}
```

## Non-derivative language requirement (include in final package)

Include an explicit note stating:

- This package preserves brand character and tone while normalizing inconsistency and improving accessibility/usability.
- It is intended as a modernized baseline, not a clone of the source website.
- Protected assets (logos, illustrations, images) require reuse rights or replacement.
