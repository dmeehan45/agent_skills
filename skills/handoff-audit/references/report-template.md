# Report template — handoff audit

Write to `docs/production-readiness/handoff-audit-YYYY-MM-DD.md` (real UTC
date). Keep every section, even if a section's honest content is "nothing
found". Findings within a section are ordered by severity/leverage, not by
discovery order.

---

```markdown
# Codebase handoff audit — YYYY-MM-DD

Auditor: Claude (handoff-audit skill vN) · Branch: <branch> · Commit: <sha>
Mode: full | incremental (previous: <path>)

## Executive summary

<Overall health in plain English: what a professional dev team inherits,
the biggest cleanup opportunities by leverage, and the highest-risk
production gaps. 3–6 paragraphs, no tables. State the verdict a hiring
CTO would want: is this a healthy prototype, and what stands between it
and professionally maintained software?>

## Coverage

<Census totals; what was read vs pattern-matched; buckets sampled rather
than swept; analyzers that ran or failed. Per playbook §6 — no silent
sampling.>

<If incremental: table of prior findings → resolved / open / regressed.>

## 1. Safe cleanup candidates

Only Confirmed findings (rubric: ≥2 signal types + survived the trap
table). For each:

### 1.<n> <short title>
- **File path / area**:
- **Finding**:
- **Evidence**: <each signal with its type, e.g. `import-graph: knip
  reports no importers` + `grep-string: basename appears nowhere in
  src/, api/, tests/, docs/, vercel.json, workflows`>
- **Confidence**: Confirmed
- **Risk of removal**: low | medium | high — <blast radius if wrong>
- **Recommended action**:
- **Validation step**: <exact command(s) and expected result after the
  cleanup, e.g. `npm run typecheck && npm test` green + route X still 200>

## 2. Cleanup candidates requiring confirmation

Probable findings and anything gated on product intent. For each:

### 2.<n> <short title>
- **File path / area**:
- **Finding**:
- **Why this cannot be decided automatically**:
- **Confirmation question**: <one specific, answerable question>
- **Recommended default**:

## 3. Documentation cleanup and handoff gaps

<Outdated / misleading / duplicated docs with paths and the specific
inaccuracy; docs to delete, rewrite, merge, or add. Then: what a new dev
team needs on day one that does not exist (setup that actually works,
architecture overview, env-var reference, ops runbook, ownership map).
Remember: dated qa/ and docs/history are records — archive-marker at
most.>

## 4. Architecture simplification opportunities

<Simplifications that reduce maintenance burden without changing product
behavior. For each: the current shape (with paths), the simpler shape,
why behavior is preserved, and the effort/leverage call. No rewrites
unless the current design creates demonstrated risk — name the risk.>

## 5. Build, deployment, and operational readiness gaps

<Gates and their status (typecheck / lint / test / audit /
migration-check); CI blocking vs advisory; scripts hygiene; env-var and
secrets handling; deploy + rollback story; migrations process;
observability and alerting; ownership.>

## 6. Production-grade readiness checklist

- **Must fix before handoff**: <blocks a new team from working safely>
- **Must fix before production launch**: <blocks real users at any scale>
- **Should address before meaningful scale**: <fine today, fails at 10–100×>
- **Can defer until usage justifies it**: <with the signal that triggers it>

## 7. Scalability review for one million users

<Per bottleneck: the mechanism (which query, which cron, which limit,
which cost line), the tier (needed now / before serious launch / when
scale signals appear), the trigger signal to instrument, and the
minimum-professional fix. Include cost drivers (LLM spend, serverless
duration, analytics volume) and operational complexity. Explicitly list
what should be instrumented BEFORE making scale investments.>

## 8. Suggested cleanup sequence

<Ordered phases that minimize breakage; each phase lists its items (by
section number above), its validation gate, and why it precedes the
next. Phase 1 should be zero-behavior-change items only.>

## 9. Open questions for the product or engineering owner

<Only questions that materially change cleanup, readiness, or handoff
quality. Number them; make each answerable in one sentence.>
```

---

## Wrap-up rules (chat reply, after pushing the report)

1. Lead with the executive summary and the report's repo path.
2. Preview URL for the branch per the repo contract (docs-only change —
   say so; the preview exists regardless).
3. Surface the section-9 questions inline so David can answer without
   opening the report.
4. Teaching notes: 1–3 concepts tied to what the audit touched.
5. Stop. No cleanup until specific items are approved; each approved item
   becomes its own small branch/PR using that item's validation step.
