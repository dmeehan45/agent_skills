#!/usr/bin/env python3
"""Validate normalized intake config for the public-site design system modernizer skill."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


ALLOWED_AUDIENCES = {"designer", "developer", "both"}
ALLOWED_INTENDED_USE = {"internal_exploration", "client_work", "rebuild_baseline"}
ALLOWED_CRAWL_MODES = {"representative_sample", "bounded_full", "custom_urls", "sitemap"}
ALLOWED_FALLBACKS = {"suggest_candidates", "mark_unknown", "infer_ranges"}
DEFAULT_EXCLUDE_HINTS = {"/legal", "/privacy", "/terms", "/careers", "/login"}


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_http_url(value: Any) -> bool:
    return isinstance(value, str) and (value.startswith("http://") or value.startswith("https://"))


def add_error(errors: list[str], path: str, message: str) -> None:
    errors.append(f"{path}: {message}")


def add_warn(warnings: list[str], path: str, message: str) -> None:
    warnings.append(f"{path}: {message}")


def expect_bool(obj: dict[str, Any], key: str, path: str, errors: list[str]) -> None:
    if key not in obj:
        add_error(errors, f"{path}.{key}", "missing required boolean")
        return
    if not isinstance(obj[key], bool):
        add_error(errors, f"{path}.{key}", "must be boolean")


def expect_number(
    obj: dict[str, Any],
    key: str,
    path: str,
    errors: list[str],
    minimum: float | None = None,
    integer: bool = False,
) -> None:
    if key not in obj:
        add_error(errors, f"{path}.{key}", "missing required number")
        return
    value = obj[key]
    ok_type = isinstance(value, int) and not isinstance(value, bool)
    if not integer:
        ok_type = ok_type or isinstance(value, float)
    if not ok_type:
        add_error(errors, f"{path}.{key}", "must be a number")
        return
    if minimum is not None and value < minimum:
        add_error(errors, f"{path}.{key}", f"must be >= {minimum}")


def validate_project(cfg: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    project = cfg.get("project")
    if not isinstance(project, dict):
        add_error(errors, "project", "missing required object")
        return

    if not isinstance(project.get("name"), str) or not project["name"].strip():
        add_error(errors, "project.name", "must be a non-empty string")
    source_url = project.get("source_url")
    if not is_http_url(source_url):
        add_error(errors, "project.source_url", "must be a public http(s) URL")
    elif "localhost" in source_url or "127.0.0.1" in source_url:
        add_warn(warnings, "project.source_url", "looks local/private; this skill is for public websites only")

    audience = project.get("output_audience")
    if audience not in ALLOWED_AUDIENCES:
        add_error(errors, "project.output_audience", f"must be one of {sorted(ALLOWED_AUDIENCES)}")
    intended = project.get("intended_use")
    if intended not in ALLOWED_INTENDED_USE:
        add_error(errors, "project.intended_use", f"must be one of {sorted(ALLOWED_INTENDED_USE)}")


def validate_scope(cfg: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    scope = cfg.get("scope")
    if not isinstance(scope, dict):
        add_error(errors, "scope", "missing required object")
        return

    crawl_mode = scope.get("crawl_mode")
    if crawl_mode not in ALLOWED_CRAWL_MODES:
        add_error(errors, "scope.crawl_mode", f"must be one of {sorted(ALLOWED_CRAWL_MODES)}")

    expect_number(scope, "max_pages", "scope", errors, minimum=1, integer=True)
    expect_number(scope, "max_depth", "scope", errors, minimum=0, integer=True)
    expect_bool(scope, "include_subdomains", "scope", errors)
    expect_bool(scope, "respect_robots_txt", "scope", errors)
    expect_number(scope, "crawl_delay_ms", "scope", errors, minimum=0, integer=True)
    expect_number(scope, "requests_per_second", "scope", errors, minimum=0.1, integer=False)

    exclude_paths = scope.get("exclude_paths")
    if not isinstance(exclude_paths, list) or not all(isinstance(x, str) for x in exclude_paths):
        add_error(errors, "scope.exclude_paths", "must be a list of strings")
    else:
        if not DEFAULT_EXCLUDE_HINTS.intersection(set(exclude_paths)):
            add_warn(
                warnings,
                "scope.exclude_paths",
                "does not include common low-value paths (/legal,/privacy,/terms,/careers,/login)",
            )

    if crawl_mode == "custom_urls":
        urls = scope.get("custom_urls")
        if not isinstance(urls, list) or not urls:
            add_error(errors, "scope.custom_urls", "required non-empty list when crawl_mode=custom_urls")
        elif not all(is_http_url(u) for u in urls):
            add_error(errors, "scope.custom_urls", "all entries must be http(s) URLs")
    elif "custom_urls" in scope and scope.get("custom_urls"):
        add_warn(warnings, "scope.custom_urls", "ignored unless crawl_mode=custom_urls")

    if crawl_mode == "sitemap":
        sitemap_url = scope.get("sitemap_url")
        if not is_http_url(sitemap_url):
            add_error(errors, "scope.sitemap_url", "required http(s) URL when crawl_mode=sitemap")
    elif "sitemap_url" in scope and scope.get("sitemap_url"):
        add_warn(warnings, "scope.sitemap_url", "ignored unless crawl_mode=sitemap")


def validate_capture(cfg: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    capture = cfg.get("capture")
    if not isinstance(capture, dict):
        add_error(errors, "capture", "missing required object")
        return

    screenshots = capture.get("screenshots")
    if not isinstance(screenshots, dict):
        add_error(errors, "capture.screenshots", "missing required object")
    else:
        for key in ("desktop", "mobile", "tablet"):
            if key in screenshots and not isinstance(screenshots[key], bool):
                add_error(errors, f"capture.screenshots.{key}", "must be boolean")
        if screenshots.get("desktop") is not True:
            add_error(errors, "capture.screenshots.desktop", "must be true (required)")
        if screenshots.get("mobile") is not True:
            add_warn(warnings, "capture.screenshots.mobile", "recommended true for better visual hierarchy coverage")

    for key in ("html", "css", "text", "asset_metadata", "component_candidates"):
        expect_bool(capture, key, "capture", errors)
    if "computed_css_samples" in capture and not isinstance(capture["computed_css_samples"], bool):
        add_error(errors, "capture.computed_css_samples", "must be boolean if provided")

    if capture.get("css") is False:
        add_warn(warnings, "capture.css", "disabling CSS reduces token extraction quality")
    if capture.get("text") is False:
        add_warn(warnings, "capture.text", "disabling text reduces voice DNA extraction quality")


def validate_quality(cfg: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    quality = cfg.get("quality")
    if not isinstance(quality, dict):
        add_error(errors, "quality", "missing required object")
        return

    expect_number(
        quality,
        "canonical_token_confidence_threshold",
        "quality",
        errors,
        minimum=0.0,
        integer=False,
    )
    threshold = quality.get("canonical_token_confidence_threshold")
    if isinstance(threshold, (int, float)) and not isinstance(threshold, bool):
        if threshold > 1:
            add_error(errors, "quality.canonical_token_confidence_threshold", "must be <= 1")
        elif threshold < 0.7:
            add_warn(warnings, "quality.canonical_token_confidence_threshold", "below recommended default 0.70")

    fallback = quality.get("low_confidence_fallback")
    if fallback not in ALLOWED_FALLBACKS:
        add_error(errors, "quality.low_confidence_fallback", f"must be one of {sorted(ALLOWED_FALLBACKS)}")

    for key in ("require_contrast_checks", "require_anti_pattern_report", "require_pnie_matrix"):
        expect_bool(quality, key, "quality", errors)


def validate_guardrails(cfg: dict[str, Any], errors: list[str]) -> None:
    mode = cfg.get("mode")
    if mode != "brand_faithful_modernization":
        add_error(errors, "mode", "must equal 'brand_faithful_modernization'")

    guardrails = cfg.get("guardrails")
    if guardrails is None:
        return
    if not isinstance(guardrails, dict):
        add_error(errors, "guardrails", "must be an object if provided")
        return

    for key in ("public_access_confirmed", "non_clone_intent_confirmed", "asset_rights_warning_confirmed"):
        if key in guardrails and not isinstance(guardrails[key], bool):
            add_error(errors, f"guardrails.{key}", "must be boolean")


def validate_output(cfg: dict[str, Any], warnings: list[str]) -> None:
    output = cfg.get("output")
    if output is None:
        return
    if not isinstance(output, dict):
        add_warn(warnings, "output", "should be an object if provided")
        return
    formats = output.get("formats")
    if formats is not None and isinstance(formats, dict):
        if formats.get("markdown") is False or formats.get("json") is False:
            add_warn(warnings, "output.formats", "markdown and json are required by this skill")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config_json", help="Path to normalized config JSON")
    parser.add_argument(
        "--strict-guardrails",
        action="store_true",
        help="Require explicit guardrails confirmations object/flags before crawl",
    )
    args = parser.parse_args()

    try:
        cfg = load_json(args.config_json)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: failed to read JSON: {exc}")
        return 1

    if not isinstance(cfg, dict):
        print("ERROR: config must be a top-level JSON object")
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    validate_guardrails(cfg, errors)
    validate_project(cfg, errors, warnings)
    validate_scope(cfg, errors, warnings)
    validate_capture(cfg, errors, warnings)
    validate_quality(cfg, errors, warnings)
    validate_output(cfg, warnings)

    if args.strict_guardrails:
        guardrails = cfg.get("guardrails")
        if not isinstance(guardrails, dict):
            add_error(errors, "guardrails", "required when --strict-guardrails is set")
        else:
            for key in ("public_access_confirmed", "non_clone_intent_confirmed", "asset_rights_warning_confirmed"):
                if guardrails.get(key) is not True:
                    add_error(errors, f"guardrails.{key}", "must be true before crawling")

    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        print(f"Config validation failed ({len(errors)} error(s), {len(warnings)} warning(s))")
        return 1

    print(f"Config validation passed ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
