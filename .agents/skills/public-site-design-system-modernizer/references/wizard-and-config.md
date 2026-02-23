# Wizard and Config

Use this checklist to collect inputs and build a normalized config object for reproducible runs.

## 1) Project Intent (fixed mode)

Collect:

- `project_name`
- `source_url` (public URL)
- `output_audience`: `designer` | `developer` | `both`
- `intended_use`: `internal_exploration` | `client_work` | `rebuild_baseline`

Enforce:

- `mode` is always `brand_faithful_modernization`
- Show warning: outputs are site-inspired + normalized, not clones

## 2) Crawl Scope (public web only)

Supported modes:

- `representative_sample` (default, recommended)
- `bounded_full`
- `custom_urls`
- `sitemap`

Collect:

- `max_pages` (int)
- `max_depth` (int)
- `include_subdomains` (bool)
- `exclude_paths` (list; include common defaults)
- `respect_robots_txt` (bool, default true)
- `crawl_delay_ms` (int)
- `requests_per_second` (number)
- `custom_urls` (list; only when mode is `custom_urls`)
- `sitemap_url` (string; only when mode is `sitemap`)

Default exclude suggestions:

- `/legal`
- `/privacy`
- `/terms`
- `/careers`
- `/login`

Representative sample target templates (bias for diversity over count):

- home
- feature/product
- pricing
- docs/help
- blog/article (optional)
- contact/sales
- form/workflow
- public app-like page (if available)

## 3) Public Website Guardrails (explicit confirmations)

Require confirmations:

- `public_access_confirmed` = true
- `non_clone_intent_confirmed` = true
- `asset_rights_warning_confirmed` = true

Never support in v1:

- authenticated crawling
- credential entry/capture
- private route probing
- access-control bypass attempts

## 4) Capture / Extraction Settings

Collect:

- `screenshots.desktop` (required true)
- `screenshots.mobile` (recommended default true)
- `screenshots.tablet` (optional default false)
- `capture.html` (default true)
- `capture.css` (default true)
- `capture.computed_css_samples` (optional if tooling supports)
- `capture.text` (default true)
- `capture.asset_metadata` (default true)
- `capture.component_candidates` (default true)

## 5) Output Package Selection

Defaults:

- Complete handoff package enabled
- `formats.markdown = true`
- `formats.json = true`
- `formats.yaml = false` (optional)

Sections are enumerated in `output-package.md`.

## 6) Quality and Confidence Controls

Collect:

- `canonical_token_confidence_threshold` (default `0.70`)
- `low_confidence_fallback`: `suggest_candidates` | `mark_unknown` | `infer_ranges`
- `require_contrast_checks` (default true)
- `require_anti_pattern_report` (default true)
- `require_pnie_matrix` (default true)

Enforce:

- Label low-confidence claims
- Do not invent exact token values when evidence is weak

## 7) Run Plan Preview (required before execution)

Show:

- Candidate URLs / selected URLs
- Included + excluded path rules
- Crawl mode and limits
- Capture settings
- Output artifacts
- Warnings (JS-heavy pages, sparse styles, third-party embeds)
- Estimated workload class: `fast` | `medium` | `heavy`

Do not execute crawl until this preview is shown.

## Normalized Config Example

```json
{
  "mode": "brand_faithful_modernization",
  "project": {
    "name": "Acme DS Baseline",
    "source_url": "https://example.com",
    "output_audience": "both",
    "intended_use": "rebuild_baseline"
  },
  "scope": {
    "crawl_mode": "representative_sample",
    "max_pages": 20,
    "max_depth": 3,
    "include_subdomains": false,
    "exclude_paths": ["/legal", "/privacy", "/terms", "/careers", "/login"],
    "respect_robots_txt": true,
    "crawl_delay_ms": 500,
    "requests_per_second": 1
  },
  "capture": {
    "screenshots": { "desktop": true, "mobile": true, "tablet": false },
    "html": true,
    "css": true,
    "text": true,
    "asset_metadata": true,
    "component_candidates": true
  },
  "quality": {
    "canonical_token_confidence_threshold": 0.7,
    "low_confidence_fallback": "suggest_candidates",
    "require_contrast_checks": true,
    "require_anti_pattern_report": true,
    "require_pnie_matrix": true
  }
}
```
