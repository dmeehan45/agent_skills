---
name: ux-quality-review
description: Standardized UX and visual-quality assessment workflow for product interfaces. Use when Codex must review or critique UI/UX for accessibility UX standards, user-flow simplicity and continuity (including dead-end detection), visual cleanliness and cognitive-load reduction, mobile responsiveness and workflow completion parity, and overall visual design / UX best-practice compliance, then produce prioritized, actionable recommendations.
---

# UX Quality Review

## Overview
Execute a consistent UX review that produces evidence-based findings, severity, category scores, and a prioritized remediation plan. Keep recommendations concrete, implementation-oriented, and mapped to user impact.

## Workflow
1. **Set scope and context**
   - Capture product area, target users, primary workflows, platforms (web/mobile), and known brand constraints.
2. **Run category checklists**
   - Use `references/review-checklists.md` to inspect all required domains and collect observable evidence.
3. **Score and classify severity**
   - Use `references/scoring-rubric.md` for 0–5 scoring per category and severity calibration.
4. **Write recommendations**
   - Use `references/remediation-patterns.md` to convert each issue into a clear fix with implementation hints.
5. **Generate final report**
   - Use `assets/review-output-template.md` and preserve required section/field order.

## Output requirements
Always use this report structure and order:
1. `Scope & Context`
2. `Findings by Category`
3. `Severity Summary`
4. `Priority Fix Plan (Now / Next / Later)`
5. `Acceptance Checks`

For each finding, include fields in this exact order:
- `ID`
- `Category`
- `Severity`
- `Evidence`
- `User Impact`
- `Recommendation`
- `Implementation Hint`

## Required references
- **Checklist source:** `references/review-checklists.md`
- **Scoring + severity source:** `references/scoring-rubric.md`
- **Fix-pattern source:** `references/remediation-patterns.md`

## Optional execution aid
If coordinating multiple agents, use `assets/agent-brief-template.md` to assign category ownership with non-overlapping files and unified reporting format.
