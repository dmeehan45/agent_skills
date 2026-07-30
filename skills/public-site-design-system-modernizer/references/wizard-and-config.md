# Wizard and Config

Collect these inputs, build a normalized config, validate it with
`scripts/validate_intake_config.py`, and show the run plan before crawling.

Most fields have a working default. Ask for the source URL and the fidelity
mode; infer the rest and show them in the run plan for correction rather than
interrogating the user field by field.

## 1) Project intent

- `project_name`
- `source_url` — public http(s) URL
- `output_audience`: `designer` | `developer` | `both`
- `intended_use`: `internal_exploration` | `client_work` | `rebuild_baseline`

`mode` is always `brand_faithful_modernization`. Warn that outputs are
site-inspired and normalized, not clones.

## 2) Crawl scope

Modes: `representative_sample` (default), `bounded_full`, `custom_urls`,
`sitemap`.

- `max_pages`, `max_depth`, `include_subdomains`
- `exclude_paths`, `typography_only_paths`
- `respect_robots_txt` (default true)
- `crawl_delay_ms`, `requests_per_second`
- `custom_urls` / `sitemap_url` when the mode requires them

`discover_urls.py` implements this: it reads robots.txt, follows declared
sitemaps, classifies templates, and round-robins across template buckets so
coverage beats depth.

**Default excludes:** `/careers`, `/login`, plus auth, cart/checkout, feeds, and
binary assets (built into the discovery script).

**Typography-only paths:** `/legal`, `/privacy`, `/terms`, `/cookie`,
`/accessibility`. Excluded by default; add `--include-typography-only` to
capture them. They hold the site's cleanest long-form body copy and link styling
with no marketing noise — good typography evidence, bad brand-voice evidence.
Never let them influence tone extraction.

**Target templates**, in priority order: home, pricing, feature/product, docs,
contact/form, article, case study, catalog, help, about.

## 3) Public-site guardrails

Require:

- `public_access_confirmed`
- `non_clone_intent_confirmed`
- `asset_rights_warning_confirmed`

Never support: authenticated crawling, credential entry, private route probing,
access-control bypass, or spoofing identity to evade bot protection. If a site
blocks the crawler, report it and reduce scope.

## 4) Capture settings

Screenshots: `desktop` (required), `mobile` (default true), `tablet` (default
false).

Content capture: `html`, `css`, `text`, `asset_metadata`,
`component_candidates` — all default true.

**Measurement passes** — these are what make the run an extraction rather than
an inference:

| Field | Default | Effect when disabled |
| --- | --- | --- |
| `computed_styles` | `true` (enforced) | Every token becomes inferred. The validator rejects `false` |
| `interaction_states` | `true` | Hover/focus/active unobservable; component states become recommendations |
| `dark_mode` | `true` | Token set is light-only |
| `consent_dismissal` | `true` | Cookie banners obscure components and skew pixel measurements |

## 5) Output package

Full handoff package by default. `formats.markdown` and `formats.json` are
required; `formats.yaml` optional.

Token emission always produces DTCG JSON, layered CSS, Tailwind v3 **and** v4,
and `preview.html`. Emit both Tailwind formats — v3 and v4 configure themes in
completely different places, and shipping one guesses the consumer's version.

## 6) Quality and confidence

- `fidelity_mode`: `modernized` (default) | `verbatim` — see
  `extraction-requirements.md` §4
- `canonical_token_confidence_threshold` (default `0.70`) — see
  `confidence-model.md`
- `low_confidence_fallback`: `suggest_candidates` | `mark_unknown` |
  `infer_ranges`
- `require_contrast_checks`, `require_anti_pattern_report`,
  `require_pnie_matrix` (default true)
- `require_fidelity_check` (default true) — the round-trip verification; without
  it nothing confirms the tokens match the source
- `require_raw_vs_canonical_diff` (default true)

Confidence is computed, not asserted. Do not hand-edit scores.

## 7) Run plan preview (required before crawling)

Show: selected URLs with template guesses, exclusions and why, crawl mode and
limits, capture settings including which measurement passes are on, fidelity
mode, output artifacts, warnings (JS-heavy pages, blocked stylesheets,
third-party embeds, missing high-signal templates), and estimated workload
(`fast` | `medium` | `heavy`).

`render_run_plan.py` renders this from the config plus `crawl-plan.json`. Do not
start capture until it has been shown.

## Normalized config example

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
    "max_pages": 14,
    "max_depth": 3,
    "include_subdomains": false,
    "exclude_paths": ["/careers", "/login"],
    "typography_only_paths": ["/legal", "/privacy", "/terms"],
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
    "component_candidates": true,
    "computed_styles": true,
    "interaction_states": true,
    "dark_mode": true,
    "consent_dismissal": true
  },
  "quality": {
    "fidelity_mode": "modernized",
    "canonical_token_confidence_threshold": 0.7,
    "low_confidence_fallback": "suggest_candidates",
    "require_contrast_checks": true,
    "require_anti_pattern_report": true,
    "require_pnie_matrix": true,
    "require_fidelity_check": true,
    "require_raw_vs_canonical_diff": true
  },
  "guardrails": {
    "public_access_confirmed": true,
    "non_clone_intent_confirmed": true,
    "asset_rights_warning_confirmed": true
  }
}
```
