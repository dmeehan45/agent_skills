# Confidence Model

Confidence is **computed from the measurements**, not asserted by a model. A
threshold is only meaningful if the number it gates is reproducible, so the
formula is fixed and implemented in `scripts/aggregate_tokens.py`.

## Formula

```
confidence = clamp01(
    0.45 * coverage
  + 0.25 * instances
  + 0.20 * area
  + 0.10 * declared
  - spread_penalty
)
```

| Component | Definition | Why it is weighted this way |
| --- | --- | --- |
| `coverage` | `pages_seen / pages_captured` | Highest weight. A value on one page is a page style; a value on every page is a system token. This is the strongest available signal that something is systematic. |
| `instances` | `log1p(count) / log1p(12)`, capped at 1 | Log-scaled and saturating at ~12 occurrences. Beyond that, more repetition adds no information — and raw counts would let a nav with 40 links outvote a design decision. |
| `area` | `area_share / 0.02`, capped at 1 | Share of measured rendered area within its census group, saturating at 2%. Rescues values that appear rarely but dominate the screen, like an h1. |
| `declared` | 1 if the value matches a `:root` custom property, `<meta name="theme-color">`, or a logo SVG fill; else 0 | The site publishing a value as its own token is direct evidence, not inference. Deliberately capped at 0.10 so a declared-but-unused variable cannot alone clear the threshold. |
| `spread_penalty` | `clamp01(max_intra_cluster_ΔE * 4) * 0.15` | Colours only. A cluster spanning visibly different values is a weaker claim than a tight one. |

Matching for `declared` is perceptual, not string equality: a measured colour
within ΔE 0.025 of a declared custom property counts as declared.

## Threshold

Default `0.70`, configurable via `--threshold`.

- `confidence >= threshold` → `status: canonical`
- `confidence < threshold` → `status: low_confidence_candidate`

Low-confidence tokens are still emitted — with the status recorded in
`tokens.json` under `$extensions.psdsm`, flagged inline in `tokens.css`, and
listed in `extraction-confidence.json.low_confidence_tokens`. They are marked,
never silently dropped and never silently promoted.

## What the score does and does not mean

It measures **how well-evidenced the measurement is**. It says nothing about
whether the resulting token set looks like the brand — that is what
`fidelity_check.mjs` measures, and the two are independent. A run can be
confident and unfaithful: consistently measuring the wrong thing (a cookie
banner on every page) scores high on coverage and instances.

Always read the confidence report and the fidelity report together.

## Reading a low score

| Pattern | Likely cause | Response |
| --- | --- | --- |
| Everything low | Too few pages captured | Capture more pages; coverage is 45% of the score |
| One role low, rest high | Genuinely rare — a badge or alert colour seen once | Correct. Leave it labelled |
| Low with high `declared` | Declared as a custom property but barely rendered | Probably a token for a component you did not capture |
| High `spread_penalty` | Many near-but-not-identical values | Real implementation drift; the diff report lists the merged variants |

## Worked example

The brand blue on a six-page capture: seen on 6/6 pages, 24 button instances,
1.4% of measured background area, declared as `--brand-primary`, cluster spread
ΔE 0.004.

```
coverage  = 6/6                      = 1.000  → 0.45 × 1.000 = 0.450
instances = log1p(24)/log1p(12)      = 1.000  → 0.25 × 1.000 = 0.250   (capped)
area      = 0.014/0.02               = 0.700  → 0.20 × 0.700 = 0.140
declared  = 1                                 → 0.10 × 1.000 = 0.100
spread    = clamp01(0.004×4) × 0.15           = 0.002
                                                ---------------------
                                                confidence     = 0.938
```

Canonical.
