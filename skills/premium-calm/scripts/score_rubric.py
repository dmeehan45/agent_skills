#!/usr/bin/env python3
"""score_rubric.py — score a surface against the premium-calm rubric and apply the gate.

Turns "does this feel premium?" into a weighted number with an explicit release
verdict, so the same question asked next release gets a comparable answer.

Usage:
  python3 score_rubric.py scores.json
  python3 score_rubric.py scores.json --baseline last-release.json
  python3 score_rubric.py scores.json --json
  python3 score_rubric.py --template > scores.json

Input shape: see --template, or assets/scorecard-template.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Criterion weights sum to 100. Changing them changes what the product optimises
# for, so treat edits as a deliberate act, not a tuning knob.
CRITERIA = [
    ("task-clarity", 15, "Task clarity and hierarchy",
     "Purpose, state, and next action are immediately evident",
     "User cannot determine what to do"),
    ("interaction-feedback", 15, "Interaction predictability and feedback",
     "Controls behave consistently; state and progress are explicit",
     "Actions appear unresponsive or produce unexplained outcomes"),
    ("typography", 10, "Typography and readability",
     "Strong hierarchy, comfortable measure, scalable text, readable metadata",
     "Text is cramped, clipped, or visually undifferentiated"),
    ("color-contrast", 10, "Colour and contrast",
     "Accent is scarce and semantic; all states meet contrast requirements",
     "Meaning depends on low contrast or colour alone"),
    ("spacing-density", 10, "Spacing and density",
     "Grouping follows a stable rhythm; neither crowded nor wasteful",
     "Arbitrary gaps and container clutter obscure structure"),
    ("accessibility", 10, "Accessibility",
     "Core tasks work with scaling, keyboard, screen readers, and accommodations",
     "Users are excluded from essential actions"),
    ("motion-haptics", 8, "Motion and haptics",
     "Motion preserves context and respects preferences",
     "Motion delays work, distracts, or causes discomfort"),
    ("imagery-materials", 8, "Imagery and materials",
     "Images aid decisions; material clarifies hierarchy",
     "Imagery is generic, inconsistent, or competes with content"),
    ("microcopy-trust", 8, "Microcopy and trust",
     "Prices, policies, states, and recovery are concrete",
     "Copy is vague, coercive, or conceals consequences"),
    ("performance", 6, "Performance and cross-platform behaviour",
     "Responsive at the 75th percentile and appropriately native",
     "Delays, layout shifts, or platform inconsistencies impair tasks"),
]
WEIGHTS = {key: weight for key, weight, *_ in CRITERIA}

BANDS = [
    (90, "Distinctive premium calm", "Flagship quality; refine through measured use"),
    (80, "Strong but uneven", "Release only when critical paths score at least 85"),
    (70, "Functional, visibly inconsistent", "Targeted redesign required"),
    (60, "Noisy or friction-heavy", "Do not position as premium"),
    (0, "Systemic failure", "Rework information architecture and foundations"),
]

SEVERITY = {
    "S0": "Not a usability problem — no action",
    "S1": "Cosmetic inconsistency — fix during routine polish",
    "S2": "Minor friction — schedule in the current design cycle",
    "S3": "Major problem — fix before release of the affected path",
    "S4": "Critical failure — block release immediately",
}

RELEASE_MIN = 85
FLAGSHIP_MIN = 90
ACCESSIBILITY_MIN_SCORE = 4


def template() -> str:
    return json.dumps({
        "project": "Product name",
        "assessedAt": "2026-01-01",
        "release": "v1.0 premium-calm pass",
        "criticalPaths": ["search", "booking", "payment", "cancellation", "support"],
        "surfaces": [
            {
                "id": "checkout",
                "path": "payment",
                "critical": True,
                "scores": {key: 0 for key, *_ in CRITERIA},
                "evidence": "premium-calm-evidence/evidence/checkout.mobile.json",
            }
        ],
        "findings": [
            {
                "id": "F-01",
                "severity": "S3",
                "path": "payment",
                "surface": "checkout",
                "summary": "Total is shown only after the payment method is chosen",
                "status": "open",
            }
        ],
    }, indent=2)


def score_surface(surface: dict) -> dict:
    scores = surface.get("scores", {})
    unknown = [k for k in scores if k not in WEIGHTS]
    missing = [k for k in WEIGHTS if k not in scores]
    total = 0.0
    breakdown = []
    for key, weight, label, *_ in CRITERIA:
        raw = scores.get(key)
        if raw is None:
            breakdown.append({"key": key, "label": label, "weight": weight,
                              "score": None, "weighted": 0.0})
            continue
        raw = float(raw)
        weighted = weight * raw / 5.0
        total += weighted
        breakdown.append({"key": key, "label": label, "weight": weight,
                          "score": raw, "weighted": round(weighted, 2)})
    return {
        "id": surface.get("id", "surface"),
        "path": surface.get("path"),
        "critical": bool(surface.get("critical")),
        "total": round(total, 1),
        "band": band_for(total),
        "breakdown": breakdown,
        "missing": missing,
        "unknown": unknown,
        "evidence": surface.get("evidence"),
    }


def band_for(total: float) -> dict:
    for threshold, name, implication in BANDS:
        if total >= threshold:
            return {"threshold": threshold, "name": name, "implication": implication}
    return {"threshold": 0, "name": BANDS[-1][1], "implication": BANDS[-1][2]}


def evaluate_gate(doc: dict, scored: list[dict]) -> dict:
    critical_paths = {p.lower() for p in doc.get("criticalPaths", [])}
    findings = doc.get("findings", [])
    open_findings = [f for f in findings if str(f.get("status", "open")).lower() not in ("resolved", "closed", "fixed", "wontfix-accepted")]

    s4 = [f for f in open_findings if f.get("severity") == "S4"]
    s3_critical = [
        f for f in open_findings
        if f.get("severity") == "S3" and str(f.get("path", "")).lower() in critical_paths
    ]

    a11y_short = []
    for s in scored:
        raw = next((b["score"] for b in s["breakdown"] if b["key"] == "accessibility"), None)
        if raw is not None and raw < ACCESSIBILITY_MIN_SCORE:
            a11y_short.append({"surface": s["id"], "score": raw})

    below_release = [s for s in scored if s["total"] < RELEASE_MIN]
    critical_below = [s for s in scored if s["critical"] and s["total"] < RELEASE_MIN]

    blockers = []
    if s4:
        blockers.append(f"{len(s4)} open S4 (critical failure) finding(s)")
    if s3_critical:
        blockers.append(f"{len(s3_critical)} open S3 finding(s) on a critical path")
    if a11y_short:
        blockers.append(
            f"{len(a11y_short)} surface(s) score below {ACCESSIBILITY_MIN_SCORE}/5 on accessibility"
        )
    if critical_below:
        blockers.append(
            f"{len(critical_below)} critical-path surface(s) below {RELEASE_MIN}/100"
        )

    return {
        "pass": not blockers,
        "blockers": blockers,
        "s4": s4,
        "s3Critical": s3_critical,
        "accessibilityShortfall": a11y_short,
        "belowRelease": [s["id"] for s in below_release],
        "criticalBelowRelease": [s["id"] for s in critical_below],
        "openFindings": len(open_findings),
        "severityCounts": {
            sev: len([f for f in open_findings if f.get("severity") == sev]) for sev in SEVERITY
        },
    }


def render(doc: dict, scored: list[dict], gate: dict, overall: float, baseline: dict | None) -> str:
    lines: list[str] = []
    title = doc.get("project", "Premium-calm assessment")
    lines.append(f"{title} — premium-calm rubric")
    if doc.get("release"):
        lines.append(f"  {doc['release']}  ·  assessed {doc.get('assessedAt', 'undated')}")
    lines.append("")

    base_totals = {}
    if baseline:
        base_totals = {s.get("id"): score_surface(s)["total"] for s in baseline.get("surfaces", [])}

    for s in scored:
        delta = ""
        if s["id"] in base_totals:
            d = s["total"] - base_totals[s["id"]]
            delta = f"   ({d:+.1f} vs baseline)"
        flag = " [critical path]" if s["critical"] else ""
        lines.append(f"  {s['id']}{flag}: {s['total']}/100 — {s['band']['name']}{delta}")
        for b in s["breakdown"]:
            score = "—" if b["score"] is None else f"{b['score']:.0f}/5"
            bar_len = 0 if b["score"] is None else int(round(b["score"] * 4))
            bar = "█" * bar_len + "·" * (20 - bar_len)
            mark = "  "
            if b["key"] == "accessibility" and b["score"] is not None and b["score"] < ACCESSIBILITY_MIN_SCORE:
                mark = "!!"
            lines.append(f"    {mark} {bar} {score:>4}  ×{b['weight']:<3} = {b['weighted']:>5}  {b['label']}")
        if s["missing"]:
            lines.append(f"       unscored: {', '.join(s['missing'])}")
        if s["unknown"]:
            lines.append(f"       not a rubric criterion, ignored: {', '.join(s['unknown'])}")
        lines.append("")

    overall_band = band_for(overall)
    delta = ""
    if baseline and base_totals:
        prev = sum(base_totals.values()) / len(base_totals)
        delta = f"   ({overall - prev:+.1f} vs baseline)"
    lines.append(f"  Overall: {overall:.1f}/100 — {overall_band['name']}{delta}")
    lines.append(f"           {overall_band['implication']}")
    lines.append("")

    counts = gate["severityCounts"]
    lines.append(f"  Open findings by severity: " + ", ".join(
        f"{sev} {counts[sev]}" for sev in ("S4", "S3", "S2", "S1", "S0")
    ))
    lines.append("")

    if gate["pass"]:
        lines.append("  RELEASE GATE: pass")
        if overall >= FLAGSHIP_MIN:
            lines.append(f"  At or above {FLAGSHIP_MIN} — flagship quality. Refine through measured use.")
    else:
        lines.append("  RELEASE GATE: BLOCKED")
        for b in gate["blockers"]:
            lines.append(f"    · {b}")
        lines.append("")
        for f in gate["s4"]:
            lines.append(f"    S4  {f.get('id', '')} [{f.get('path', '?')}] {f.get('summary', '')}")
        for f in gate["s3Critical"]:
            lines.append(f"    S3  {f.get('id', '')} [{f.get('path', '?')}] {f.get('summary', '')}")
        for a in gate["accessibilityShortfall"]:
            lines.append(f"    A11y {a['surface']}: {a['score']:.0f}/5, needs {ACCESSIBILITY_MIN_SCORE}/5")

    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Score a surface against the premium-calm rubric.")
    ap.add_argument("scores", nargs="?", help="scores JSON")
    ap.add_argument("--baseline", help="previous scores JSON, to show movement")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--template", action="store_true", help="print a blank scores file and exit")
    args = ap.parse_args()

    if args.template:
        print(template())
        return 0
    if not args.scores:
        ap.error("pass a scores JSON, or --template to generate one")

    doc = json.loads(Path(args.scores).read_text())
    surfaces = doc.get("surfaces")
    if not surfaces:
        if "scores" not in doc:
            ap.error('scores file needs either "surfaces": [...] or a top-level "scores": {...}')
        surfaces = [{"id": doc.get("project", "surface"), "scores": doc["scores"], "critical": True}]

    scored = [score_surface(s) for s in surfaces]
    overall = sum(s["total"] for s in scored) / len(scored) if scored else 0.0
    gate = evaluate_gate(doc, scored)
    baseline = json.loads(Path(args.baseline).read_text()) if args.baseline else None

    if args.json:
        print(json.dumps({
            "project": doc.get("project"),
            "assessedAt": doc.get("assessedAt"),
            "overall": round(overall, 1),
            "band": band_for(overall),
            "surfaces": scored,
            "gate": gate,
        }, indent=2))
    else:
        print(render(doc, scored, gate, overall, baseline))

    return 0 if gate["pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
