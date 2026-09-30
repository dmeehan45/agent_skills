#!/usr/bin/env python3
"""
check_review.py — lint a premium experience review before it is handed over.

The review is read by a product designer who must be able to disagree with
each recommendation on the merits, and by a coding agent who must be able to
open a file and start. This script checks the mechanical half of that bar:

  * the required sections are present, in the template's order;
  * every finding (### PER-nn — title) carries the six fields plus altitude,
    priority, class, surface, and evidence;
  * altitude, priority, class, effort, and evidence tiers use the vocabulary
    from references/finding-standard.md;
  * the banned vague phrases do not appear in the recommended change or the
    premium expression;
  * finding IDs are unique, the ledger and the sequence reference them, and
    the implementation sequence does not put cosmetic work ahead of
    structural work.

Usage:
  python3 check_review.py reviews/premium-experience-review-2026-09-30.md
  python3 check_review.py review.md --strict     # warnings fail too
  python3 check_review.py review.md --json       # machine-readable

Exit codes: 0 clean (warnings allowed unless --strict), 1 problems found,
2 could not read the file.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field

REQUIRED_SECTIONS = [
    ("product model", r"product\s+model"),
    ("the current experience", r"current\s+experience"),
    ("hierarchy by surface", r"hierarchy"),
    ("findings", r"^findings\b|\bfindings$"),
    ("systemic roots", r"systemic\s+roots"),
    ("final synthesis", r"synthesis"),
    ("implementation sequence", r"implementation\s+sequence"),
    ("not reviewed", r"not\s+reviewed"),
]

FIELDS = [
    "Altitude",
    "Priority",
    "Class",
    "Effort",
    "Surface",
    "Evidence",
    "Observation",
    "User consequence",
    "Underlying issue",
    "Recommended change",
    "Premium expression",
    "Implementation surface",
    "Acceptance",
]
REQUIRED_FIELDS = [f for f in FIELDS if f not in ("Effort", "Acceptance")]

ALTITUDES = {"Product", "Experience", "Craft"}
PRIORITIES = {"Foundational", "Friction", "Refinement", "Exceptional craft"}
CLASSES = {"Local flaw", "System drift", "Product model"}
EFFORTS = {"S", "M", "L"}
EVIDENCE_TIERS = ("Walked", "Source", "Screenshot", "Reported")

BANNED = [
    "improve hierarchy",
    "improve the hierarchy",
    "make this cleaner",
    "make it cleaner",
    "add polish",
    "improve the onboarding",
    "improve onboarding",
    "make the design more premium",
    "more premium",
    "add animations",
    "add animation",
    "make it pop",
    "modernise",
    "modernize",
    "more intuitive",
    "cleaner look",
    "add micro-interactions",
    "improve ux",
    "improve the ux",
    "enhance the user experience",
    "consider improving",
    "could be better",
    "needs love",
    "feels off",
    "tighten up",
    "elevate the design",
    "more delightful",
]

SYNTHESIS_PARTS = [
    ("what it feels like now", r"feels?\s+like\s+now"),
    ("what it should feel like", r"should\s+feel\s+like"),
    ("the largest gap", r"largest\s+gap"),
    ("governing principles", r"principles?"),
    ("highest-leverage systemic changes", r"systemic\s+changes?"),
    ("signature opportunities", r"signature"),
]

FINDING_HEADING = re.compile(r"^###\s+(PER-\d+[a-z]?)\s*[—–-]\s*(.+?)\s*$", re.M)
FIELD_LABEL = re.compile(r"\*\*(" + "|".join(re.escape(f) for f in FIELDS) + r")\*\*\s*:?\s*")
H2 = re.compile(r"^##\s+(.+?)\s*$", re.M)
PATHISH = re.compile(r"[\w.-]+/[\w./-]+|\.(?:tsx?|jsx?|vue|svelte|swift|kt|dart|css|scss|py|rb|html|json)\b|`[^`]+`|\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b")


@dataclass
class Finding:
    id: str
    title: str
    line: int
    fields: dict = field(default_factory=dict)


@dataclass
class Report:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    findings: list = field(default_factory=list)

    def error(self, msg, line=None):
        self.errors.append({"line": line, "message": msg})

    def warn(self, msg, line=None):
        self.warnings.append({"line": line, "message": msg})


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def parse_sections(text: str):
    """Return [(title, start, end, line)] for every H2."""
    heads = list(H2.finditer(text))
    out = []
    for i, m in enumerate(heads):
        start = m.end()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        out.append((m.group(1), start, end, line_of(text, m.start())))
    return out


def find_section(sections, pattern):
    rx = re.compile(pattern, re.I)
    for title, start, end, line in sections:
        clean = re.sub(r"^\d+[.)]?\s*", "", title).strip()
        if rx.search(clean):
            return (title, start, end, line)
    return None


def parse_findings(text: str, report: Report):
    heads = list(FINDING_HEADING.finditer(text))
    findings = []
    for i, m in enumerate(heads):
        start = m.end()
        # A finding block ends at the next finding heading or the next H2/H3.
        nxt = re.compile(r"^###?\s+", re.M).search(text, start)
        end = nxt.start() if nxt else len(text)
        block = text[start:end]
        f = Finding(id=m.group(1), title=m.group(2), line=line_of(text, m.start()))
        labels = list(FIELD_LABEL.finditer(block))
        for j, lm in enumerate(labels):
            vstart = lm.end()
            vend = labels[j + 1].start() if j + 1 < len(labels) else len(block)
            value = block[vstart:vend]
            value = re.sub(r"\s*[·•|]\s*$", "", value.strip())
            value = value.strip(" ·•|\n")
            name = lm.group(1)
            if name in f.fields:
                report.warn(f"{f.id}: field '{name}' appears twice; using the first", f.line)
                continue
            f.fields[name] = value
        findings.append(f)
    return findings


def check_vocab(f: Finding, report: Report):
    alt = f.fields.get("Altitude", "").strip()
    pri = f.fields.get("Priority", "").strip()
    cls = f.fields.get("Class", "").strip()
    eff = f.fields.get("Effort", "").strip()
    if alt and alt not in ALTITUDES:
        report.error(f"{f.id}: Altitude '{alt}' is not one of {sorted(ALTITUDES)}", f.line)
    if pri and pri not in PRIORITIES:
        report.error(f"{f.id}: Priority '{pri}' is not one of {sorted(PRIORITIES)}", f.line)
    if cls and cls not in CLASSES:
        report.error(f"{f.id}: Class '{cls}' is not one of {sorted(CLASSES)}", f.line)
    if eff and eff not in EFFORTS:
        report.error(f"{f.id}: Effort '{eff}' is not S, M, or L", f.line)
    if alt == "Craft" and pri == "Foundational":
        report.warn(f"{f.id}: Craft-altitude finding marked Foundational; allowed only when it blocks a job, and the user consequence should say so", f.line)
    if alt == "Product" and pri == "Exceptional craft":
        report.warn(f"{f.id}: Product-altitude finding marked Exceptional craft; check whether this is really a product change", f.line)


def check_evidence(f: Finding, report: Report):
    ev = f.fields.get("Evidence", "")
    tiers = [t for t in EVIDENCE_TIERS if re.search(rf"\b{t}\b", ev)]
    if not tiers:
        report.error(f"{f.id}: Evidence names no tier (Walked, Source, Screenshot, Reported) — see finding-standard.md", f.line)
        return
    if tiers == ["Reported"]:
        report.warn(f"{f.id}: Evidence is Reported only; pair it with a walk or a source read before filing", f.line)
    if f.fields.get("Class") and "Source" not in tiers:
        report.warn(f"{f.id}: Class is set but no Source evidence is cited; classification without reading the code is a guess", f.line)
    if "Screenshot" in tiers and len(tiers) == 1:
        lower = (f.fields.get("Observation", "") + f.fields.get("Recommended change", "")).lower()
        if re.search(r"\b(focus|hover|latency|ms\b|contrast|target size|44px|animation|transition|reduced motion)", lower):
            report.warn(f"{f.id}: Screenshot-only evidence but the finding asserts focus, motion, latency, contrast, or target size; those need a walk", f.line)


def banned_in(text: str):
    """Banned phrases present in text, longest first, without double-counting a
    phrase that sits inside a longer matched one."""
    low = text.lower()
    taken = []
    hits = []
    for phrase in sorted(BANNED, key=len, reverse=True):
        start = low.find(phrase)
        while start != -1:
            end = start + len(phrase)
            if not any(s <= start and end <= e for s, e in taken):
                taken.append((start, end))
                if phrase not in hits:
                    hits.append(phrase)
            start = low.find(phrase, end)
    return hits


def check_banned(f: Finding, report: Report):
    for fld in ("Recommended change", "Premium expression"):
        for phrase in banned_in(f.fields.get(fld, "")):
            report.error(f"{f.id}: '{phrase}' in {fld} — say which element, state, value, or behaviour changes", f.line)
    for fld in ("Observation", "User consequence", "Underlying issue"):
        for phrase in banned_in(f.fields.get(fld, "")):
            report.warn(f"{f.id}: '{phrase}' in {fld}", f.line)


def check_substance(f: Finding, report: Report):
    rc = f.fields.get("Recommended change", "")
    if rc and len(rc) < 80:
        report.warn(f"{f.id}: Recommended change is {len(rc)} characters; a coding agent probably cannot start from it", f.line)
    pe = f.fields.get("Premium expression", "")
    if pe and len(pe) < 60:
        report.warn(f"{f.id}: Premium expression is {len(pe)} characters; describe behaviour, timing, and state", f.line)
    imp = f.fields.get("Implementation surface", "")
    if imp and not PATHISH.search(imp):
        report.warn(f"{f.id}: Implementation surface names no file, component, route, or token", f.line)
    if "Acceptance" not in f.fields:
        report.warn(f"{f.id}: no Acceptance; say how a re-walk would show it landed", f.line)
    if "Effort" not in f.fields:
        report.warn(f"{f.id}: no Effort (S/M/L)", f.line)


def check_sequence(text: str, sections, findings, report: Report):
    sec = find_section(sections, r"implementation\s+sequence")
    if not sec:
        return
    body = text[sec[1] : sec[2]]
    by_id = {f.id: f for f in findings}
    order = []
    for m in re.finditer(r"PER-\d+[a-z]?", body):
        if m.group(0) not in order:
            order.append(m.group(0))
    unknown = [i for i in order if i not in by_id]
    if unknown:
        report.warn(f"Implementation sequence references unknown findings: {', '.join(unknown[:8])}", sec[3])
    known = [i for i in order if i in by_id]
    seen_cosmetic = []
    for i in known:
        pri = by_id[i].fields.get("Priority", "")
        if pri in ("Refinement", "Exceptional craft"):
            seen_cosmetic.append(i)
        elif pri == "Foundational" and seen_cosmetic:
            report.warn(
                f"Implementation sequence places {', '.join(seen_cosmetic[:4])} ({'/'.join(sorted({by_id[c].fields.get('Priority','') for c in seen_cosmetic}))}) before Foundational {i}; make the product structurally better before cosmetically better, or bundle them into the same primitive and say so",
                sec[3],
            )
            break
    missing = [f.id for f in findings if f.id not in order]
    if missing:
        report.warn(f"{len(missing)} finding(s) not referenced in the implementation sequence: {', '.join(missing[:10])}", sec[3])


def check_ledger(text: str, sections, findings, report: Report):
    sec = find_section(sections, r"^findings\b|\bfindings$")
    if not sec:
        return
    body = text[sec[1] : sec[2]]
    table_rows = [ln for ln in body.splitlines() if ln.strip().startswith("|")]
    if not any(re.search(r"\|\s*ID\s*\|", ln) for ln in table_rows):
        report.warn("Findings section has no ledger table with an ID column", sec[3])
        return
    ledger_ids = set()
    for ln in table_rows:
        m = re.match(r"\|\s*(PER-\d+[a-z]?)\s*\|", ln.strip())
        if m:
            ledger_ids.add(m.group(1))
    ids = {f.id for f in findings}
    for i in sorted(ids - ledger_ids):
        report.warn(f"{i} is not in the ledger table")
    for i in sorted(ledger_ids - ids):
        report.warn(f"Ledger lists {i} but there is no '### {i} — …' finding")


def check_synthesis(text: str, sections, report: Report):
    sec = find_section(sections, r"synthesis")
    if not sec:
        return
    body = text[sec[1] : sec[2]].lower()
    for name, rx in SYNTHESIS_PARTS:
        if not re.search(rx, body):
            report.warn(f"Final synthesis does not cover '{name}'", sec[3])


def check_product_model(text: str, sections, report: Report):
    sec = find_section(sections, r"product\s+model")
    if not sec:
        return
    body = text[sec[1] : sec[2]].lower()
    if "must not change" not in body:
        report.warn("Product model does not record what must not change", sec[3])
    if not re.search(r"ambigu", body):
        report.warn("Product model has no ambiguities note (write 'none found' if so)", sec[3])
    if not re.search(r"premium\s+means", body):
        report.warn("Product model does not say what premium means for this product", sec[3])


def run(path: str) -> tuple[Report, str]:
    report = Report()
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        report.error(f"cannot read {path}: {e}")
        return report, ""
    sections = parse_sections(text)

    last_pos = -1
    for name, rx in REQUIRED_SECTIONS:
        sec = find_section(sections, rx)
        if not sec:
            report.error(f"missing section: {name}")
            continue
        if sec[1] < last_pos:
            report.warn(f"section '{name}' is out of the template order", sec[3])
        last_pos = sec[1]

    findings = parse_findings(text, report)
    report.findings = findings
    if not findings:
        report.error("no findings found; each needs a heading like '### PER-01 — title'")
    dup = [i for i, n in Counter(f.id for f in findings).items() if n > 1]
    for i in dup:
        report.error(f"duplicate finding id {i}")

    for f in findings:
        for fld in REQUIRED_FIELDS:
            if fld not in f.fields or not f.fields[fld].strip():
                report.error(f"{f.id}: missing {fld}", f.line)
        check_vocab(f, report)
        check_evidence(f, report)
        check_banned(f, report)
        check_substance(f, report)

    check_ledger(text, sections, findings, report)
    check_sequence(text, sections, findings, report)
    check_synthesis(text, sections, report)
    check_product_model(text, sections, report)
    return report, text


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Lint a premium experience review.")
    ap.add_argument("review")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    report, _ = run(args.review)
    if report.errors and any("cannot read" in e["message"] for e in report.errors):
        print(report.errors[0]["message"], file=sys.stderr)
        return 2

    by_priority = Counter(f.fields.get("Priority", "?") for f in report.findings)
    by_altitude = Counter(f.fields.get("Altitude", "?") for f in report.findings)
    by_class = Counter(f.fields.get("Class", "?") for f in report.findings)
    ok = not report.errors and not (args.strict and report.warnings)

    if args.json:
        print(json.dumps({
            "ok": ok,
            "findings": len(report.findings),
            "byPriority": dict(by_priority),
            "byAltitude": dict(by_altitude),
            "byClass": dict(by_class),
            "errors": report.errors,
            "warnings": report.warnings,
        }, indent=2))
        return 0 if ok else 1

    def fmt(item):
        loc = f"  (line {item['line']})" if item.get("line") else ""
        return f"  - {item['message']}{loc}"

    print(f"{args.review}: {len(report.findings)} findings")
    if report.findings:
        print("  priority  " + ", ".join(f"{k} {v}" for k, v in sorted(by_priority.items(), key=lambda kv: -kv[1])))
        print("  altitude  " + ", ".join(f"{k} {v}" for k, v in sorted(by_altitude.items(), key=lambda kv: -kv[1])))
        print("  class     " + ", ".join(f"{k} {v}" for k, v in sorted(by_class.items(), key=lambda kv: -kv[1])))
    if report.errors:
        print(f"\n{len(report.errors)} error(s):")
        for e in report.errors:
            print(fmt(e))
    if report.warnings:
        print(f"\n{len(report.warnings)} warning(s):")
        for w in report.warnings:
            print(fmt(w))
    print("\n" + ("OK" if ok else "NOT OK") + (" (strict)" if args.strict else ""))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
