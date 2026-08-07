# Premium-calm scorecard — <product>

A standing gate, not a one-off opinion. Re-run it each release and keep the
history: the trend matters more than any single number.

**Release** <name> · **Assessed** <date> · **Assessor** <who> · **Evidence**
<path>

## Score

```
python3 scripts/score_rubric.py scores.json --baseline last-release.json
```

| Surface | Path | Critical? | Score | Band | Δ vs last |
| --- | --- | --- | --- | --- | --- |
| | | | /100 | | |

**Overall** <n>/100 — <band>

## Criterion detail

| Criterion | Weight | Score /5 | Weighted | Evidence |
| --- | --- | --- | --- | --- |
| Task clarity and hierarchy | 15 | | | |
| Interaction predictability and feedback | 15 | | | |
| Typography and readability | 10 | | | |
| Colour and contrast | 10 | | | |
| Spacing and density | 10 | | | |
| Accessibility | 10 | | | |
| Motion and haptics | 8 | | | |
| Imagery and materials | 8 | | | |
| Microcopy and trust | 8 | | | |
| Performance and cross-platform behaviour | 6 | | | |
| **Total** | **100** | | | |

Every score cites evidence. A score without a path beside it is an opinion
wearing a number.

## Release gate

| Condition | Required | Actual | |
| --- | --- | --- | --- |
| Open S4 findings | 0 | | |
| Open S3 on a critical path | 0 | | |
| Accessibility, every surface | ≥ 4/5 | | |
| Critical-path surfaces | ≥ 85/100 | | |

**Verdict:** <pass / blocked>

Blockers, if any — each with an owner and a target date:

| ID | Severity | Path | Summary | Owner | Target |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

## Measured readings

| Reading | Gate | Actual | |
| --- | --- | --- | --- |
| Contrast failures | 0 | | |
| Targets under 44pt / 48dp | 0 | | |
| Controls without focus style | 0 | | |
| Moves under reduced motion | 0 | | |
| CLS (field p75) | ≤ 0.1 | | |
| LCP (field p75) | ≤ 2.5s | | |
| INP (field p75) | ≤ 200ms | | |

## Scores file

Kept beside this document so the next assessment can diff against it.

```json
{
  "project": "<product>",
  "assessedAt": "<date>",
  "release": "<name>",
  "criticalPaths": ["<path>", "<path>"],
  "surfaces": [
    {
      "id": "<surface>",
      "path": "<journey>",
      "critical": true,
      "evidence": "pc-evidence/evidence/<surface>.mobile.json",
      "scores": {
        "task-clarity": 0,
        "interaction-feedback": 0,
        "typography": 0,
        "color-contrast": 0,
        "spacing-density": 0,
        "accessibility": 0,
        "motion-haptics": 0,
        "imagery-materials": 0,
        "microcopy-trust": 0,
        "performance": 0
      }
    }
  ],
  "findings": [
    {
      "id": "PC-01",
      "severity": "S3",
      "path": "<journey>",
      "surface": "<surface>",
      "summary": "<one line>",
      "status": "open"
    }
  ]
}
```

Generate a blank one with `python3 scripts/score_rubric.py --template`.
