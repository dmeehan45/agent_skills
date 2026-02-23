#!/usr/bin/env python3
"""Render a run-plan preview markdown from normalized config and selected URLs."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def workload_class(config: dict[str, Any], url_count: int) -> str:
    max_pages = int(config.get("scope", {}).get("max_pages", url_count or 0) or 0)
    screenshots = config.get("capture", {}).get("screenshots", {})
    screenshot_modes = sum(1 for v in screenshots.values() if v)
    score = max(max_pages, url_count)
    score += 5 if screenshot_modes >= 2 else 0
    score += 5 if config.get("scope", {}).get("crawl_mode") == "bounded_full" else 0
    if score <= 15:
        return "fast"
    if score <= 50:
        return "medium"
    return "heavy"


def normalize_urls(url_data: Any) -> list[str]:
    if url_data is None:
        return []
    if isinstance(url_data, list):
        return [str(u) for u in url_data]
    if isinstance(url_data, dict):
        if isinstance(url_data.get("urls"), list):
            return [str(u) for u in url_data["urls"]]
        if isinstance(url_data.get("pages"), list):
            return [str(p.get("url")) for p in url_data["pages"] if isinstance(p, dict) and p.get("url")]
    raise ValueError("URL input must be a list or an object with 'urls' or 'pages'")


def render(config: dict[str, Any], urls: list[str]) -> str:
    project = config.get("project", {})
    scope = config.get("scope", {})
    capture = config.get("capture", {})
    quality = config.get("quality", {})
    output = config.get("output", {})
    warnings = []

    if not scope.get("respect_robots_txt", True):
        warnings.append("robots.txt respect is disabled; confirm policy allows this.")
    if not capture.get("css", True):
        warnings.append("CSS capture disabled; visual token confidence may degrade.")
    if not capture.get("text", True):
        warnings.append("Text capture disabled; voice DNA extraction may degrade.")
    if not capture.get("screenshots", {}).get("desktop", False):
        warnings.append("Desktop screenshots disabled; this violates the recommended/default profile.")
    if len(urls) == 0:
        warnings.append("No URLs selected yet; crawl plan is incomplete.")

    selected_urls = urls[: int(scope.get("max_pages", len(urls) or 0) or len(urls))]
    excluded = scope.get("exclude_paths", [])
    outputs = output.get("artifacts") or [
        "reports/*",
        "tokens/tokens.json",
        "tokens/tokens.css",
        "tokens/tailwind.theme.js",
        "components/*",
        "patterns/*",
        "evidence/*",
    ]

    lines: list[str] = []
    lines.append(f"# Run Plan Preview: {project.get('name', 'Untitled Project')}")
    lines.append("")
    lines.append("## Project Intent")
    lines.append(f"- Mode: `{config.get('mode', 'brand_faithful_modernization')}`")
    lines.append(f"- Source URL: `{project.get('source_url', '')}`")
    lines.append(f"- Audience: `{project.get('output_audience', 'both')}`")
    lines.append(f"- Intended use: `{project.get('intended_use', 'rebuild_baseline')}`")
    lines.append("- Warning: Outputs are brand-faithful, normalized, and non-clone by design.")
    lines.append("")
    lines.append("## Crawl Scope")
    lines.append(f"- Crawl mode: `{scope.get('crawl_mode', 'representative_sample')}`")
    lines.append(f"- Max pages: `{scope.get('max_pages', 'n/a')}`")
    lines.append(f"- Max depth: `{scope.get('max_depth', 'n/a')}`")
    lines.append(f"- Include subdomains: `{bool(scope.get('include_subdomains', False))}`")
    lines.append(f"- Respect robots.txt: `{bool(scope.get('respect_robots_txt', True))}`")
    lines.append(f"- Crawl delay (ms): `{scope.get('crawl_delay_ms', 'n/a')}`")
    lines.append(f"- Requests/sec: `{scope.get('requests_per_second', 'n/a')}`")
    lines.append("")
    lines.append("## Included / Excluded Paths")
    if excluded:
        for item in excluded:
            lines.append(f"- Exclude: `{item}`")
    else:
        lines.append("- No explicit excluded paths configured")
    lines.append("")
    lines.append("## Selected URLs")
    if selected_urls:
        for i, url in enumerate(selected_urls, start=1):
            lines.append(f"{i}. `{url}`")
        if len(urls) > len(selected_urls):
            lines.append(f"- Truncated to `max_pages`; {len(urls) - len(selected_urls)} additional URLs not shown")
    else:
        lines.append("- No URLs selected")
    lines.append("")
    lines.append("## Capture Settings")
    screenshots = capture.get("screenshots", {})
    lines.append(f"- Screenshots: desktop={bool(screenshots.get('desktop', False))}, mobile={bool(screenshots.get('mobile', False))}, tablet={bool(screenshots.get('tablet', False))}")
    lines.append(f"- HTML capture: `{bool(capture.get('html', True))}`")
    lines.append(f"- CSS capture: `{bool(capture.get('css', True))}`")
    lines.append(f"- Text capture: `{bool(capture.get('text', True))}`")
    lines.append(f"- Asset metadata: `{bool(capture.get('asset_metadata', True))}`")
    lines.append(f"- Component candidates: `{bool(capture.get('component_candidates', True))}`")
    lines.append("")
    lines.append("## Quality Controls")
    lines.append(f"- Canonical token confidence threshold: `{quality.get('canonical_token_confidence_threshold', 0.7)}`")
    lines.append(f"- Low-confidence fallback: `{quality.get('low_confidence_fallback', 'suggest_candidates')}`")
    lines.append(f"- Contrast checks: `{bool(quality.get('require_contrast_checks', True))}`")
    lines.append(f"- Anti-pattern report: `{bool(quality.get('require_anti_pattern_report', True))}`")
    lines.append(f"- PNIE matrix: `{bool(quality.get('require_pnie_matrix', True))}`")
    lines.append("")
    lines.append("## Output Artifacts")
    for artifact in outputs:
        lines.append(f"- `{artifact}`")
    lines.append("")
    lines.append("## Warnings")
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- None detected from configuration")
    lines.append("")
    lines.append("## Estimated Workload")
    lines.append(f"- Class: `{workload_class(config, len(selected_urls))}`")
    lines.append("")
    lines.append("_Do not begin crawling until this run plan is reviewed._")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config_json", help="Path to normalized config JSON")
    parser.add_argument(
        "--urls-json",
        help="Path to JSON list of URLs or object containing `urls` or `pages`",
    )
    parser.add_argument(
        "--output",
        help="Write markdown to a file instead of stdout",
    )
    args = parser.parse_args()

    config = load_json(args.config_json)
    urls = normalize_urls(load_json(args.urls_json)) if args.urls_json else []
    markdown = render(config, urls)

    if args.output:
        Path(args.output).write_text(markdown, encoding="utf-8")
    else:
        sys.stdout.write(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
