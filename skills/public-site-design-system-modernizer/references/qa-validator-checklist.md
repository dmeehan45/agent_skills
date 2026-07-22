# QA / Validator Checklist

Run validator checks after synthesis and before packaging. Continue on partial failures, but mark degraded confidence.

## 1) Accessibility checks (mandatory)

- Contrast:
  - Flag risky foreground/background pairs
  - Provide accessible alternatives that preserve color character
- Focus states:
  - Visible focus indicators for interactive controls
  - Distinguishable from hover-only styles
- Status communication:
  - Do not rely on color alone
- Touch targets:
  - Minimum target guidance for mobile controls
- Readability:
  - Text sizes/line heights for dense views
- Forms:
  - Labels, helper text, error messages, and validation clarity
- Keyboard:
  - Notes on navigability expectations where inferable
- Motion:
  - Reduced-motion guidance if motion tokens are present

## 2) Token consistency checks

- Canonical token names are consistent across reports/JSON/CSS/Tailwind
- No contradictory values for the same token
- Accidental variants are not elevated to canonical without evidence
- Low-confidence tokens are labeled and handled by fallback policy
- Breakpoints/container widths follow a coherent system (not page-by-page drift)

## 3) Component completeness checks

For each core component in scope, confirm:

- Purpose
- Anatomy
- Variants
- States: `default`, `hover`, `focus`, `active`, `disabled`
- States when applicable: `loading`, `error`, `selected`, `empty`
- Spacing rules
- Content guidance
- Accessibility notes
- Implementation notes

Flag missing state guidance instead of silently omitting it.

## 4) Over-literal copying risk checks (mandatory)

Flag and revise if outputs:

- Mirror exact page layouts from the source
- Encode one-off campaign styles as canonical
- Reuse copyrighted asset content without rights confirmation
- Use exact source copy blocks as reusable component content guidance

Require explicit non-derivative guidance in final outputs:

- what to preserve
- what to normalize/improve
- what not to copy directly

## 5) Confidence checks

- Every weak-evidence area is marked
- Confidence threshold applied to canonical token decisions
- Fallback behavior is consistent (`suggest_candidates`, `mark_unknown`, `infer_ranges`)
- Evidence references exist for material claims

## 6) Failure handling / degraded mode

Handle and report clearly:

- `robots.txt` restrictions
- timeouts / network failures
- JS-heavy pages with incomplete capture
- duplicate/redirect loops
- low-signal pages
- missing CSS / blocked assets
- sparse component evidence

Behavior:

- Continue when partial evidence is sufficient
- Lower confidence and explain blind spots
- Provide fallback outputs instead of fabricating exact values

## QA output recommendations

Generate:

- `reports/accessibility-audit.md`
- `evidence/extraction-confidence.json`
- validator findings summary embedded in Executive Summary and Source Audit
