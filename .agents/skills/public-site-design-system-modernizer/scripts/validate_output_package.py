#!/usr/bin/env python3
"""Validate required design-system-output artifacts for this skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_PATHS = [
    "reports/executive-summary.md",
    "reports/source-audit.md",
    "reports/brand-dna.md",
    "reports/accessibility-audit.md",
    "reports/preserve-normalize-improve-exclude.md",
    "tokens/tokens.json",
    "tokens/tokens.css",
    "tokens/tailwind.theme.js",
    "components/component-library-spec.md",
    "components/component-contracts.json",
    "patterns/page-template-patterns.md",
    "evidence/crawl-manifest.json",
    "evidence/page-weights.json",
    "evidence/extraction-confidence.json",
]


def parse_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def require_keys(obj: dict[str, Any], keys: list[str], path: str, errors: list[str]) -> None:
    missing = [k for k in keys if k not in obj]
    if missing:
        errors.append(f"{path}: missing keys {missing}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output_dir",
        nargs="?",
        default="design-system-output",
        help="Root output directory to validate (default: design-system-output)",
    )
    args = parser.parse_args()

    root = Path(args.output_dir)
    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_PATHS:
        p = root / rel
        if not p.exists():
            errors.append(f"Missing required file: {p}")

    if errors:
        for msg in errors:
            print(f"ERROR: {msg}")
        print(f"Validation failed ({len(errors)} missing required files)")
        return 1

    # Basic JSON shape checks
    tokens_json = root / "tokens/tokens.json"
    data, err = parse_json(tokens_json)
    if err:
        errors.append(f"{tokens_json}: invalid JSON ({err})")
    elif isinstance(data, dict):
        expected_top = ["color", "typography", "spacing", "radius", "shadow", "border", "motion", "layout"]
        missing = [k for k in expected_top if k not in data]
        if missing:
            warnings.append(f"{tokens_json}: missing recommended token groups {missing}")
    else:
        errors.append(f"{tokens_json}: expected top-level object")

    manifest_json = root / "evidence/crawl-manifest.json"
    data, err = parse_json(manifest_json)
    if err:
        errors.append(f"{manifest_json}: invalid JSON ({err})")
    elif isinstance(data, dict):
        require_keys(data, ["source_url", "crawl_mode", "pages"], str(manifest_json), errors)
    else:
        errors.append(f"{manifest_json}: expected top-level object")

    page_weights_json = root / "evidence/page-weights.json"
    data, err = parse_json(page_weights_json)
    if err:
        errors.append(f"{page_weights_json}: invalid JSON ({err})")
    elif isinstance(data, dict):
        require_keys(data, ["clusters", "pages"], str(page_weights_json), errors)
    else:
        errors.append(f"{page_weights_json}: expected top-level object")

    confidence_json = root / "evidence/extraction-confidence.json"
    data, err = parse_json(confidence_json)
    if err:
        errors.append(f"{confidence_json}: invalid JSON ({err})")
    elif isinstance(data, dict):
        require_keys(data, ["threshold"], str(confidence_json), errors)
    else:
        errors.append(f"{confidence_json}: expected top-level object")

    # Report content checks
    pnie = (root / "reports/preserve-normalize-improve-exclude.md").read_text(encoding="utf-8")
    expected_terms = ["Preserve", "Normalize", "Improve", "Exclude"]
    for term in expected_terms:
        if term not in pnie:
            warnings.append(f"PNIE report does not mention '{term}'")

    summary = (root / "reports/executive-summary.md").read_text(encoding="utf-8")
    non_derivative_markers = ["not a clone", "brand-faithful", "normalize", "must not be copied"]
    if not any(marker in summary.lower() for marker in [m.lower() for m in non_derivative_markers]):
        warnings.append("Executive summary may be missing explicit non-derivative guardrail language")

    if errors:
        for msg in errors:
            print(f"ERROR: {msg}")
    for msg in warnings:
        print(f"WARN: {msg}")

    if errors:
        print(f"Validation failed ({len(errors)} error(s), {len(warnings)} warning(s))")
        return 1
    print(f"Validation passed with {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
