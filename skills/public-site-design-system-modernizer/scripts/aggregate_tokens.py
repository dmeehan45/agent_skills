#!/usr/bin/env python3
"""Aggregate measured page data into raw + canonical token candidates.

Consumes the output of `capture_site.mjs` and produces deterministic token
candidates. Colour clustering is perceptual (OKLab), spacing/type scales are
fitted from observed values, and every token carries a computed confidence
score rather than an asserted one.

Nothing here is an LLM judgement call: the same measurements always produce the
same tokens. The synthesis prompts consume this output, they do not replace it.

Usage:
  python3 aggregate_tokens.py design-system-output
  python3 aggregate_tokens.py design-system-output --fidelity-mode verbatim
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

# ---------------------------------------------------------------- colour math

_RGB_RE = re.compile(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.%]+))?\s*\)")
_HEX_RE = re.compile(r"^#([0-9a-fA-F]{3,8})$")

NAMED_COLORS = {
    "white": (255, 255, 255, 1.0),
    "black": (0, 0, 0, 1.0),
    "transparent": (0, 0, 0, 0.0),
    "red": (255, 0, 0, 1.0),
    "currentcolor": None,
}


def parse_color(value: str) -> tuple[float, float, float, float] | None:
    """Parse a CSS colour into (r, g, b, alpha) with r/g/b in 0-255."""
    if not isinstance(value, str):
        return None
    text = value.strip().lower()
    if text in NAMED_COLORS:
        return NAMED_COLORS[text]
    match = _HEX_RE.match(text)
    if match:
        digits = match.group(1)
        if len(digits) == 3:
            digits = "".join(c * 2 for c in digits)
        elif len(digits) == 4:
            digits = "".join(c * 2 for c in digits)
        if len(digits) == 6:
            return (int(digits[0:2], 16), int(digits[2:4], 16), int(digits[4:6], 16), 1.0)
        if len(digits) == 8:
            return (
                int(digits[0:2], 16),
                int(digits[2:4], 16),
                int(digits[4:6], 16),
                int(digits[6:8], 16) / 255.0,
            )
        return None
    match = _RGB_RE.search(text)
    if match:
        alpha_raw = match.group(4)
        if alpha_raw is None:
            alpha = 1.0
        elif alpha_raw.endswith("%"):
            alpha = float(alpha_raw[:-1]) / 100.0
        else:
            alpha = float(alpha_raw)
        return (float(match.group(1)), float(match.group(2)), float(match.group(3)), alpha)
    return None


def to_hex(rgb: tuple[float, float, float, float]) -> str:
    r, g, b, a = rgb
    base = "#%02x%02x%02x" % (round(max(0, min(255, r))), round(max(0, min(255, g))), round(max(0, min(255, b))))
    if a < 0.999:
        return base + "%02x" % round(max(0.0, min(1.0, a)) * 255)
    return base


def _srgb_to_linear(channel: float) -> float:
    c = channel / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def to_oklab(rgb: tuple[float, float, float, float]) -> tuple[float, float, float]:
    r, g, b = (_srgb_to_linear(c) for c in rgb[:3])
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (v ** (1 / 3) if v > 0 else -((-v) ** (1 / 3)) for v in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def to_oklch(rgb: tuple[float, float, float, float]) -> tuple[float, float, float]:
    L, a, b = to_oklab(rgb)
    return (L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360.0)


def oklch_to_rgb(L: float, C: float, H: float) -> tuple[float, float, float, float]:
    h = math.radians(H)
    a, b = C * math.cos(h), C * math.sin(h)
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_**3, m_**3, s_**3
    lr = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    lg = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    lb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    def encode(c: float) -> float:
        c = max(0.0, min(1.0, c))
        v = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
        return max(0.0, min(255.0, v * 255.0))

    return (encode(lr), encode(lg), encode(lb), 1.0)


def delta_e_ok(c1: tuple[float, float, float, float], c2: tuple[float, float, float, float]) -> float:
    l1, a1, b1 = to_oklab(c1)
    l2, a2, b2 = to_oklab(c2)
    return math.sqrt((l1 - l2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)


def relative_luminance(rgb: tuple[float, float, float, float]) -> float:
    r, g, b = (_srgb_to_linear(c) for c in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def composite_over(fg: tuple[float, float, float, float], bg: tuple[float, float, float, float]):
    """Flatten a translucent colour onto an opaque backdrop before measuring."""
    a = fg[3]
    if a >= 0.999:
        return fg
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3)) + (1.0,)


def contrast_ratio(fg: tuple, bg: tuple) -> float:
    fg_flat = composite_over(fg, bg)
    l1, l2 = relative_luminance(fg_flat), relative_luminance(bg)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def wcag_requirement(font_px: float, weight: int) -> float:
    """3.0 for large text (>=24px, or >=18.66px bold), else 4.5."""
    if font_px >= 24 or (font_px >= 18.66 and weight >= 700):
        return 3.0
    return 4.5


def suggest_accessible(fg: tuple, bg: tuple, target: float) -> dict[str, Any] | None:
    """Shift lightness in OKLCH until contrast passes, holding hue and chroma.

    Keeping H and C fixed is what preserves brand colour character; only L moves.
    """
    L, C, H = to_oklch(composite_over(fg, bg))
    bg_lum = relative_luminance(bg)
    directions = [-1, 1] if bg_lum > 0.5 else [1, -1]
    best: dict[str, Any] | None = None
    original = composite_over(fg, bg)
    for direction in directions:
        # Contrast rises monotonically as L moves away from the backdrop, so
        # binary-search for the L closest to the original that still passes.
        lo, hi = L, (0.0 if direction < 0 else 1.0)
        if contrast_ratio(oklch_to_rgb(hi, C, H), bg) < target:
            continue
        best_l = hi
        for _ in range(30):
            mid = (lo + hi) / 2
            if contrast_ratio(oklch_to_rgb(mid, C, H), bg) >= target:
                best_l, hi = mid, mid
            else:
                lo = mid
            if abs(hi - lo) < 0.0005:
                break
        trial = oklch_to_rgb(best_l, C, H)
        entry = {
            "hex": to_hex(trial),
            "oklch": {"l": round(best_l, 4), "c": round(C, 4), "h": round(H, 2)},
            "contrast": round(contrast_ratio(trial, bg), 2),
            "perceptual_shift": round(delta_e_ok(trial, original), 4),
            "hue_preserved": True,
            "direction": "darker" if direction < 0 else "lighter",
        }
        if best is None or entry["perceptual_shift"] < best["perceptual_shift"]:
            best = entry
    return best


# ------------------------------------------------------------ generic helpers


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def px_value(text: Any) -> float | None:
    if isinstance(text, (int, float)):
        return float(text)
    if not isinstance(text, str):
        return None
    match = re.match(r"^(-?[\d.]+)px$", text.strip())
    if match:
        return float(match.group(1))
    try:
        return float(text)
    except ValueError:
        return None


def round_nice(value: float) -> float:
    return round(value, 2) if abs(value - round(value)) > 0.01 else float(round(value))


# -------------------------------------------------------- measurement loading


class Measurements:
    """Flattened view over every captured page."""

    def __init__(self, pages: list[dict[str, Any]]):
        self.pages = pages
        self.page_count = len(pages)

    def desktop_probes(self) -> Iterable[tuple[str, dict[str, Any]]]:
        for page in self.pages:
            probe = page.get("measurements", {}).get("desktop")
            if probe:
                yield page["page_id"], probe

    def dark_probes(self) -> Iterable[tuple[str, dict[str, Any]]]:
        for page in self.pages:
            probe = page.get("measurements", {}).get("dark")
            if probe:
                yield page["page_id"], probe

    def all_probes(self) -> Iterable[tuple[str, str, dict[str, Any]]]:
        for page in self.pages:
            for viewport, probe in page.get("measurements", {}).items():
                if isinstance(probe, dict) and "census" in probe:
                    yield page["page_id"], viewport, probe

    def census(self, group: str, viewports: tuple[str, ...] = ("desktop",)) -> dict[str, dict[str, Any]]:
        """Merge one census group across pages, tracking page coverage."""
        merged: dict[str, dict[str, Any]] = {}
        for page_id, viewport, probe in self.all_probes():
            if viewport not in viewports:
                continue
            for value, stats in (probe.get("census", {}).get(group) or {}).items():
                slot = merged.setdefault(value, {"count": 0, "area": 0, "roles": defaultdict(int), "pages": set()})
                slot["count"] += stats.get("count", 0)
                slot["area"] += stats.get("area", 0)
                slot["pages"].add(page_id)
                for role, n in (stats.get("roles") or {}).items():
                    slot["roles"][role] += n
        return merged

    def declared_values(self) -> dict[str, str]:
        """Every :root custom property the site itself declares."""
        out: dict[str, str] = {}
        for _, probe in self.desktop_probes():
            for name, value in (probe.get("resolved_custom_properties") or {}).items():
                out.setdefault(name, value)
        return out

    def brand_signals(self) -> dict[str, Any]:
        theme_colors, logo_colors = [], []
        for _, probe in self.desktop_probes():
            brand = probe.get("brand") or {}
            if brand.get("theme_color"):
                theme_colors.append(brand["theme_color"])
            for logo in brand.get("logo_candidates") or []:
                logo_colors.extend(logo.get("colors") or [])
        return {"theme_colors": theme_colors, "logo_colors": logo_colors}


# ------------------------------------------------------------- confidence model

CONFIDENCE_WEIGHTS = {"coverage": 0.45, "instances": 0.25, "area": 0.20, "declared": 0.10}


def compute_confidence(
    pages_seen: int,
    pages_total: int,
    instances: int,
    area_share: float,
    declared: bool,
    spread: float = 0.0,
) -> dict[str, Any]:
    """Confidence is measured, not asserted. See references/confidence-model.md.

    coverage  — fraction of captured pages the value appears on
    instances — log-scaled occurrence count, saturating at ~12 instances
    area      — share of measured rendered area, saturating at 2%
    declared  — the site declares this value as its own token / brand signal
    spread    — intra-cluster perceptual spread, applied as a penalty
    """
    coverage = clamp01(pages_seen / pages_total) if pages_total else 0.0
    instance_score = clamp01(math.log1p(max(0, instances)) / math.log1p(12))
    area_score = clamp01(area_share / 0.02)
    declared_score = 1.0 if declared else 0.0
    raw = (
        CONFIDENCE_WEIGHTS["coverage"] * coverage
        + CONFIDENCE_WEIGHTS["instances"] * instance_score
        + CONFIDENCE_WEIGHTS["area"] * area_score
        + CONFIDENCE_WEIGHTS["declared"] * declared_score
    )
    penalty = clamp01(spread * 4.0) * 0.15
    return {
        "confidence": round(clamp01(raw - penalty), 3),
        "components": {
            "coverage": round(coverage, 3),
            "instances": round(instance_score, 3),
            "area": round(area_score, 3),
            "declared": declared_score,
            "spread_penalty": round(penalty, 3),
        },
    }


# ------------------------------------------------------------- colour pipeline

COLOR_MERGE_THRESHOLD = 0.025  # OKLab ΔE; below this two colours read as the same


def cluster_colors(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Greedy perceptual clustering, heaviest colour first.

    Hex-string equality misses `#1a73e8` vs `#1b74e9`; those are one brand colour
    with two implementations, and they must merge before role assignment.
    """
    ordered = sorted(entries, key=lambda e: (-e["area"], -e["count"]))
    clusters: list[dict[str, Any]] = []
    for entry in ordered:
        placed = False
        for cluster in clusters:
            if delta_e_ok(entry["rgb"], cluster["rgb"]) <= COLOR_MERGE_THRESHOLD:
                cluster["members"].append(entry)
                cluster["count"] += entry["count"]
                cluster["area"] += entry["area"]
                cluster["pages"] |= entry["pages"]
                for role, n in entry["roles"].items():
                    cluster["roles"][role] = cluster["roles"].get(role, 0) + n
                placed = True
                break
        if not placed:
            clusters.append(
                {
                    "rgb": entry["rgb"],
                    "hex": to_hex(entry["rgb"]),
                    "members": [entry],
                    "count": entry["count"],
                    "area": entry["area"],
                    "pages": set(entry["pages"]),
                    "roles": dict(entry["roles"]),
                }
            )
    for cluster in clusters:
        spreads = [delta_e_ok(m["rgb"], cluster["rgb"]) for m in cluster["members"]]
        cluster["spread"] = round(max(spreads) if spreads else 0.0, 4)
        cluster["observed_values"] = sorted({m["raw"] for m in cluster["members"]})
    return clusters


def collect_color_entries(measurements: Measurements, group: str) -> list[dict[str, Any]]:
    entries = []
    for raw, stats in measurements.census(group).items():
        rgb = parse_color(raw)
        if rgb is None or rgb[3] < 0.05:
            continue
        entries.append(
            {
                "raw": raw,
                "rgb": rgb,
                "count": stats["count"],
                "area": stats["area"],
                "pages": set(stats["pages"]),
                "roles": dict(stats["roles"]),
            }
        )
    return entries


def declared_color_index(measurements: Measurements) -> dict[str, str]:
    """Map hex -> declaring source, for the `declared` confidence component."""
    index: dict[str, str] = {}
    for name, value in measurements.declared_values().items():
        rgb = parse_color(value)
        if rgb:
            index.setdefault(to_hex(rgb), f"custom-property:{name}")
    signals = measurements.brand_signals()
    for value in signals["theme_colors"]:
        rgb = parse_color(value)
        if rgb:
            index.setdefault(to_hex(rgb), "meta:theme-color")
    for value in signals["logo_colors"]:
        rgb = parse_color(value)
        if rgb:
            index.setdefault(to_hex(rgb), "logo-svg")
    return index


def role_profile(roles: dict[str, int]) -> dict[str, float]:
    total = sum(roles.values()) or 1
    profile: dict[str, float] = defaultdict(float)
    for role, n in roles.items():
        head = role.split(".")[0]
        profile[head] += n / total
    return dict(profile)


ROLE_SHARE_THRESHOLD = 0.30

BUTTON_ROLES = ("control.button", "role.button")
FIELD_ROLES = ("control.input", "control.select", "control.textarea")


def share_of(roles: dict[str, int], prefixes: tuple[str, ...]) -> float:
    """Share of instances whose full role name starts with one of `prefixes`.

    `role_profile` collapses to the head segment, which cannot tell a button
    background from a text-input background — a distinction that decides whether
    a colour is the action colour or the field surface.
    """
    total = sum(roles.values()) or 1
    hits = sum(n for role, n in roles.items() if role.startswith(prefixes))
    return hits / total


def assign_color_roles(cluster: dict[str, Any], group: str, surface_lum: float) -> list[str]:
    """Infer semantic roles from where the colour is actually painted.

    Frequency alone misleads: a colour on 40 buttons is the action colour even
    though a page background covers a thousand times more area. A colour can
    legitimately serve several roles (body text and link text are often the same
    ink), so this returns every role whose share clears the threshold rather than
    forcing a single winner.
    """
    profile = role_profile(cluster["roles"])
    control = profile.get("control", 0.0)
    region = profile.get("region", 0.0) + profile.get("box", 0.0)
    body = profile.get("text", 0.0)
    heading = profile.get("heading", 0.0)
    link = profile.get("nav", 0.0) + profile.get("link", 0.0)
    lum = relative_luminance(cluster["rgb"])
    chroma = to_oklch(cluster["rgb"])[1]
    roles: list[str] = []

    if group == "background_color":
        if share_of(cluster["roles"], BUTTON_ROLES) >= ROLE_SHARE_THRESHOLD:
            roles.append("action.background")
        if share_of(cluster["roles"], FIELD_ROLES) >= ROLE_SHARE_THRESHOLD:
            roles.append("surface.field")
        if region >= ROLE_SHARE_THRESHOLD or not roles:
            if abs(lum - surface_lum) < 0.02:
                roles.append("surface.base")
            elif lum < 0.2:
                roles.append("surface.inverse")
            elif chroma > 0.06:
                roles.append("surface.accent")
            elif lum > 0.75:
                roles.append("surface.subtle")
            else:
                roles.append("surface.raised")
    elif group == "text_color":
        if heading >= ROLE_SHARE_THRESHOLD:
            roles.append("text.heading")
        if link >= ROLE_SHARE_THRESHOLD:
            roles.append("text.link")
        if body >= ROLE_SHARE_THRESHOLD:
            roles.append("text.body")
        if share_of(cluster["roles"], BUTTON_ROLES) >= ROLE_SHARE_THRESHOLD:
            roles.append("text.on-action")
        if not roles:
            # Saturated leftovers are accents (badges, tags); desaturated ones
            # sitting between body ink and the surface are muted text.
            roles.append("text.accent" if chroma > 0.06 else "text.muted")
    elif group == "border_color":
        if control >= ROLE_SHARE_THRESHOLD:
            roles.append("border.control")
        if region >= ROLE_SHARE_THRESHOLD or not roles:
            roles.append("border.default")

    return roles or ["unassigned"]


def build_color_tokens(measurements: Measurements) -> dict[str, Any]:
    declared = declared_color_index(measurements)
    pages_total = max(1, measurements.page_count)

    bg_entries = collect_color_entries(measurements, "background_color")
    surface_lum = 1.0
    if bg_entries:
        dominant = max(bg_entries, key=lambda e: e["area"])
        surface_lum = relative_luminance(dominant["rgb"])

    result: dict[str, Any] = {"groups": {}, "declared_sources": declared, "merge_threshold_delta_e": COLOR_MERGE_THRESHOLD}
    for group in ("background_color", "text_color", "border_color"):
        entries = collect_color_entries(measurements, group)
        total_area = sum(e["area"] for e in entries) or 1
        clusters = cluster_colors(entries)
        out = []
        for cluster in clusters:
            hex_value = cluster["hex"]
            declared_hit = declared.get(hex_value)
            if not declared_hit:
                for candidate_hex, source in declared.items():
                    candidate_rgb = parse_color(candidate_hex)
                    if candidate_rgb and delta_e_ok(candidate_rgb, cluster["rgb"]) <= COLOR_MERGE_THRESHOLD:
                        declared_hit = source
                        break
            conf = compute_confidence(
                pages_seen=len(cluster["pages"]),
                pages_total=pages_total,
                instances=cluster["count"],
                area_share=cluster["area"] / total_area,
                declared=bool(declared_hit),
                spread=cluster["spread"],
            )
            L, C, H = to_oklch(cluster["rgb"])
            out.append(
                {
                    "hex": hex_value,
                    "oklch": {"l": round(L, 4), "c": round(C, 4), "h": round(H, 2)},
                    "roles": assign_color_roles(cluster, group, surface_lum),
                    "instances": cluster["count"],
                    "area": cluster["area"],
                    "area_share": round(cluster["area"] / total_area, 4),
                    "pages": sorted(cluster["pages"]),
                    "top_roles": sorted(cluster["roles"].items(), key=lambda kv: -kv[1])[:5],
                    "observed_values": cluster["observed_values"],
                    "variant_count": len(cluster["members"]),
                    "perceptual_spread": cluster["spread"],
                    "declared_as": declared_hit,
                    **conf,
                }
            )
        out.sort(key=lambda c: -c["confidence"])
        result["groups"][group] = out
    return result


# ------------------------------------------------------------- scale fitting


def fit_spacing_scale(values: dict[float, int]) -> dict[str, Any]:
    """Find the base grid unit by testing conformance across candidate bases."""
    if not values:
        return {"base_unit": None, "conformance": 0.0, "scale": [], "off_grid": []}
    total = sum(values.values())

    def conformance_of(base: int) -> float:
        return sum(n for v, n in values.items() if v > 0 and abs(v % base) < 0.51) / total

    # Pick the *largest* base that still explains most of the spacing. Scoring on
    # conformance alone always collapses to 2px, which describes nothing: every
    # even number conforms to a 2px grid.
    candidates = [(base, conformance_of(base)) for base in (2, 4, 5, 6, 8, 10, 12, 16)]
    qualified = [(base, score) for base, score in candidates if score >= 0.80]
    if qualified:
        best_base = max(qualified, key=lambda kv: kv[0])[0]
    else:
        best_base = max(candidates, key=lambda kv: (kv[1], kv[0]))[0]
    conformance = conformance_of(best_base)
    ranked = sorted(values.items(), key=lambda kv: -kv[1])
    scale = sorted({round(v) for v, n in ranked if v > 0 and n >= max(2, total * 0.01)})
    off_grid = sorted(
        {round(v, 2) for v, n in values.items() if v > 0 and abs(v % best_base) >= 0.51},
    )
    return {
        "base_unit": best_base,
        "conformance": round(conformance, 3),
        "scale": scale[:16],
        "off_grid": off_grid[:24],
        "distinct_values_observed": len(values),
    }


def fit_type_scale(sizes: dict[float, dict[str, Any]]) -> dict[str, Any]:
    """Fit a ratio to the observed size ladder without forcing a familiar one."""
    if not sizes:
        return {"ratio": None, "steps": [], "note": "no text measured"}
    significant = sorted(v for v, s in sizes.items() if s["count"] >= 1)
    if len(significant) < 2:
        return {"ratio": None, "steps": significant, "note": "insufficient distinct sizes"}
    ratios = [
        significant[i + 1] / significant[i]
        for i in range(len(significant) - 1)
        if significant[i] > 0 and significant[i + 1] / significant[i] > 1.01
    ]
    ratios.sort()
    median = ratios[len(ratios) // 2] if ratios else None
    named = None
    if median:
        reference = {
            "minor second (1.067)": 1.067, "major second (1.125)": 1.125,
            "minor third (1.200)": 1.200, "major third (1.250)": 1.250,
            "perfect fourth (1.333)": 1.333, "golden (1.618)": 1.618,
        }
        name, distance = min(((k, abs(v - median)) for k, v in reference.items()), key=lambda kv: kv[1])
        named = name if distance < 0.045 else None
    return {
        "ratio": round(median, 4) if median else None,
        "nearest_named_ratio": named,
        "is_modular": bool(median and len(ratios) >= 3 and (max(ratios) - min(ratios)) < 0.35),
        "steps": [
            {
                "px": size,
                "instances": stats["count"],
                "area": stats["area"],
                "roles": sorted(stats["roles"].items(), key=lambda kv: -kv[1])[:3],
            }
            for size, stats in sorted(sizes.items())
        ],
    }


def build_typography(measurements: Measurements) -> dict[str, Any]:
    pages_total = max(1, measurements.page_count)

    families: dict[str, dict[str, Any]] = {}
    for raw, stats in measurements.census("font_family").items():
        families[raw] = {
            "stack": raw,
            "primary": raw.split(",")[0].strip().strip("\"'"),
            "instances": stats["count"],
            "area": stats["area"],
            "pages": sorted(stats["pages"]),
            "top_roles": sorted(stats["roles"].items(), key=lambda kv: -kv[1])[:4],
        }
    family_list = sorted(families.values(), key=lambda f: -f["area"])
    total_family_area = sum(f["area"] for f in family_list) or 1
    for family in family_list:
        family.update(
            compute_confidence(
                pages_seen=len(family["pages"]),
                pages_total=pages_total,
                instances=family["instances"],
                area_share=family["area"] / total_family_area,
                declared=False,
            )
        )
        family["area_share"] = round(family["area"] / total_family_area, 4)

    sizes: dict[float, dict[str, Any]] = {}
    for raw, stats in measurements.census("font_size").items():
        value = px_value(raw)
        if value is None:
            continue
        slot = sizes.setdefault(value, {"count": 0, "area": 0, "roles": defaultdict(int)})
        slot["count"] += stats["count"]
        slot["area"] += stats["area"]
        for role, n in stats["roles"].items():
            slot["roles"][role] += n

    weights = {
        raw: {"instances": stats["count"], "area": stats["area"], "roles": sorted(stats["roles"].items(), key=lambda kv: -kv[1])[:3]}
        for raw, stats in measurements.census("font_weight").items()
    }
    line_heights: dict[str, Any] = {}
    for raw, stats in measurements.census("line_height").items():
        line_heights[raw] = {"instances": stats["count"], "area": stats["area"]}
    tracking = {
        raw: {"instances": stats["count"]} for raw, stats in measurements.census("letter_spacing").items()
    }

    # Pair each size with its dominant line-height, from element records.
    pairs: dict[float, dict[float, int]] = defaultdict(lambda: defaultdict(int))
    role_sizes: dict[str, dict[float, int]] = defaultdict(lambda: defaultdict(int))
    for _, probe in measurements.desktop_probes():
        for element in probe.get("elements", []):
            size, lh, role = element.get("font_size"), element.get("line_height"), element.get("role")
            if size:
                if lh:
                    pairs[size][round(lh / size, 3)] += 1
                if role:
                    role_sizes[role][size] += 1

    size_line_height = {
        str(size): max(options.items(), key=lambda kv: kv[1])[0] for size, options in pairs.items() if options
    }

    return {
        "families": family_list,
        "font_faces": [
            face
            for _, probe in measurements.desktop_probes()
            for face in (probe.get("cssom", {}).get("font_faces") or [])
        ],
        "scale": fit_type_scale(sizes),
        "weights": weights,
        "line_heights": line_heights,
        "line_height_by_size": size_line_height,
        "letter_spacing": tracking,
        "role_sizes": {
            role: sorted(sizes.items(), key=lambda kv: -kv[1])[:3] for role, sizes in role_sizes.items()
        },
    }


def build_spacing(measurements: Measurements) -> dict[str, Any]:
    padding: dict[float, int] = defaultdict(int)
    margin: dict[float, int] = defaultdict(int)
    gap: dict[float, int] = defaultdict(int)
    for group, sink in (("padding", padding), ("margin", margin), ("gap", gap)):
        for raw, stats in measurements.census(group).items():
            for part in str(raw).split():
                value = px_value(part)
                if value is not None and value > 0:
                    sink[round(value, 1)] += stats["count"]
    combined: dict[float, int] = defaultdict(int)
    for sink in (padding, margin, gap):
        for value, n in sink.items():
            combined[value] += n
    return {
        "combined": fit_spacing_scale(dict(combined)),
        "padding": fit_spacing_scale(dict(padding)),
        "margin": fit_spacing_scale(dict(margin)),
        "gap": fit_spacing_scale(dict(gap)),
    }


def build_radius(measurements: Measurements) -> dict[str, Any]:
    values: dict[float, dict[str, Any]] = {}
    pill = 0
    for raw, stats in measurements.census("radius").items():
        value = px_value(str(raw).split()[0]) if raw else None
        if value is None:
            if "%" in str(raw):
                pill += stats["count"]
            continue
        if value >= 500:
            pill += stats["count"]
            continue
        slot = values.setdefault(value, {"count": 0, "area": 0, "roles": defaultdict(int)})
        slot["count"] += stats["count"]
        slot["area"] += stats["area"]
        for role, n in stats["roles"].items():
            slot["roles"][role] += n
    ladder = sorted(values.items())
    return {
        "scale": [
            {"px": value, "instances": stats["count"], "roles": sorted(stats["roles"].items(), key=lambda kv: -kv[1])[:3]}
            for value, stats in ladder
        ],
        "pill_instances": pill,
        "distinct_values": len(values),
    }


SHADOW_LAYER_RE = re.compile(r"(-?[\d.]+)px\s+(-?[\d.]+)px\s+(-?[\d.]+)px(?:\s+(-?[\d.]+)px)?")


def build_elevation(measurements: Measurements) -> dict[str, Any]:
    entries = []
    for raw, stats in measurements.census("shadow").items():
        match = SHADOW_LAYER_RE.search(raw)
        blur = float(match.group(3)) if match else 0.0
        y = float(match.group(2)) if match else 0.0
        entries.append(
            {
                "value": raw,
                "blur": blur,
                "offset_y": y,
                "instances": stats["count"],
                "area": stats["area"],
                "roles": sorted(stats["roles"].items(), key=lambda kv: -kv[1])[:3],
            }
        )
    entries.sort(key=lambda e: (e["blur"], e["offset_y"]))
    for index, entry in enumerate(entries):
        entry["ladder_step"] = index
    return {"ladder": entries, "distinct_values": len(entries)}


def split_top_level(text: str) -> list[str]:
    """Split a CSS list on commas outside parentheses.

    A naive split shreds `cubic-bezier(0.4, 0, 0.2, 1)` into four useless
    fragments, which is how an easing curve turns into the token `0`.
    """
    parts: list[str] = []
    depth = 0
    current: list[str] = []
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        if char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return [p for p in parts if p]


def build_motion(measurements: Measurements) -> dict[str, Any]:
    durations: dict[str, int] = defaultdict(int)
    for raw, stats in measurements.census("transition_duration").items():
        for part in split_top_level(str(raw)):
            if part != "0s":
                durations[part] += stats["count"]
    timings: dict[str, int] = defaultdict(int)
    for raw, stats in measurements.census("transition_timing").items():
        for part in split_top_level(str(raw)):
            timings[part] += stats["count"]

    def to_ms(text: str) -> float | None:
        match = re.match(r"^([\d.]+)(ms|s)$", text)
        if not match:
            return None
        value = float(match.group(1))
        return value if match.group(2) == "ms" else value * 1000

    duration_list = sorted(
        ({"value": k, "ms": to_ms(k), "instances": v} for k, v in durations.items()),
        key=lambda d: (d["ms"] if d["ms"] is not None else 1e9),
    )
    keyframes = sorted({
        name
        for _, probe in measurements.desktop_probes()
        for name in (probe.get("cssom", {}).get("keyframes") or [])
    })
    return {
        "durations": duration_list,
        "easings": sorted(({"value": k, "instances": v} for k, v in timings.items()), key=lambda e: -e["instances"]),
        "keyframes": keyframes,
        "has_motion_system": bool(duration_list),
    }


def build_layout(measurements: Measurements) -> dict[str, Any]:
    breakpoints: dict[float, dict[str, Any]] = {}
    for _, probe in measurements.desktop_probes():
        for query in probe.get("cssom", {}).get("media_queries", []):
            for width in query.get("widths", []):
                unit, value = width.get("unit"), width.get("value")
                if value is None:
                    continue
                px = value * 16 if unit in ("em", "rem") else value
                slot = breakpoints.setdefault(px, {"px": px, "bounds": set(), "rule_count": 0, "conditions": []})
                slot["bounds"].add(width.get("bound"))
                slot["rule_count"] += query.get("rule_count", 0)
                if len(slot["conditions"]) < 4 and query["condition"] not in slot["conditions"]:
                    slot["conditions"].append(query["condition"])
    breakpoint_list = [
        {"px": k, "bounds": sorted(v["bounds"]), "rule_count": v["rule_count"], "sample_conditions": v["conditions"]}
        for k, v in sorted(breakpoints.items())
    ]

    containers: dict[int, int] = defaultdict(int)
    for _, probe in measurements.desktop_probes():
        for width, n in (probe.get("container_widths") or {}).items():
            containers[int(width)] += n
    for raw, stats in measurements.census("max_width").items():
        value = px_value(raw)
        if value and 320 <= value <= 2200:
            containers[int(value)] += stats["count"]

    grid_columns = {raw: stats["count"] for raw, stats in measurements.census("grid_columns").items()}
    z_ladder: dict[int, int] = defaultdict(int)
    for _, probe in measurements.desktop_probes():
        for z, n in (probe.get("z_indexes") or {}).items():
            z_ladder[int(z)] += n

    return {
        "breakpoints": breakpoint_list,
        "containers": sorted(
            ({"px": k, "instances": v} for k, v in containers.items() if v >= 1), key=lambda c: -c["instances"]
        )[:12],
        "grid_columns": grid_columns,
        "z_index_ladder": sorted(({"z": k, "instances": v} for k, v in z_ladder.items()), key=lambda e: e["z"]),
    }


def build_icons(measurements: Measurements) -> dict[str, Any]:
    merged = {
        "inline_svg_count": 0, "sprite_use_count": 0, "icon_font_candidates": [],
        "view_boxes": defaultdict(int), "stroke_widths": defaultdict(int),
        "stroke_linecaps": defaultdict(int), "fill_vs_stroke": {"fill": 0, "stroke": 0}, "sizes": defaultdict(int),
    }
    for _, probe in measurements.desktop_probes():
        icons = probe.get("icon_system") or {}
        merged["inline_svg_count"] += icons.get("inline_svg_count", 0)
        merged["sprite_use_count"] += icons.get("sprite_use_count", 0)
        for family in icons.get("icon_font_candidates", []):
            if family not in merged["icon_font_candidates"]:
                merged["icon_font_candidates"].append(family)
        for key in ("view_boxes", "stroke_widths", "stroke_linecaps", "sizes"):
            for k, v in (icons.get(key) or {}).items():
                merged[key][k] += v
        for k in ("fill", "stroke"):
            merged["fill_vs_stroke"][k] += (icons.get("fill_vs_stroke") or {}).get(k, 0)
    fill, stroke = merged["fill_vs_stroke"]["fill"], merged["fill_vs_stroke"]["stroke"]
    return {
        "delivery": "sprite" if merged["sprite_use_count"] > merged["inline_svg_count"] / 2 else "inline_svg",
        "style": "stroke" if stroke > fill else "fill" if fill else "unknown",
        "dominant_stroke_width": max(merged["stroke_widths"].items(), key=lambda kv: kv[1])[0] if merged["stroke_widths"] else None,
        "dominant_linecap": max(merged["stroke_linecaps"].items(), key=lambda kv: kv[1])[0] if merged["stroke_linecaps"] else None,
        "dominant_view_box": max(merged["view_boxes"].items(), key=lambda kv: kv[1])[0] if merged["view_boxes"] else None,
        "common_sizes": sorted(({"px": int(k), "instances": v} for k, v in merged["sizes"].items()), key=lambda s: -s["instances"])[:6],
        "icon_font_candidates": merged["icon_font_candidates"],
        "counts": {"inline_svg": merged["inline_svg_count"], "sprite_use": merged["sprite_use_count"], "fill": fill, "stroke": stroke},
    }


# ------------------------------------------------- states, contrast, dark mode


def build_component_states(measurements: Measurements) -> dict[str, Any]:
    """Consolidate measured hover/focus/active deltas into component evidence."""
    by_signature: dict[str, dict[str, Any]] = {}
    for page in measurements.pages:
        states = page.get("measurements", {}).get("interaction_states") or {}
        for probe in states.get("probes", []):
            if probe.get("error"):
                continue
            signature = probe["signature"]
            slot = by_signature.setdefault(
                signature,
                {
                    "signature": signature,
                    "selector": probe.get("selector"),
                    "role": probe.get("role"),
                    "pages": [],
                    "base": probe.get("base"),
                    "states": probe.get("states"),
                    "instances": 0,
                    "has_visible_focus_indicator": probe.get("has_visible_focus_indicator", False),
                },
            )
            slot["pages"].append(page["page_id"])
            slot["instances"] += probe.get("instances", 1)
            slot["has_visible_focus_indicator"] = slot["has_visible_focus_indicator"] or probe.get(
                "has_visible_focus_indicator", False
            )

    disabled = [
        sample
        for page in measurements.pages
        for sample in (page.get("measurements", {}).get("interaction_states") or {}).get("disabled_samples", [])
    ]

    observed, missing = [], []
    for entry in by_signature.values():
        states = entry.get("states") or {}
        measured = [name for name, delta in states.items() if delta]
        absent = [name for name in ("hover", "focus_visible", "active") if not states.get(name)]
        entry["measured_states"] = measured
        entry["unmeasured_states"] = absent
        observed.append(entry)
        if absent:
            missing.append({"signature": entry["signature"], "missing": absent})
    observed.sort(key=lambda e: -e["instances"])
    return {
        "components": observed,
        "disabled_samples": disabled,
        "gaps": missing,
        "note": (
            "States are measured by scripted hover/focus/active interaction. "
            "Any state listed in `unmeasured_states` was not observed and must be "
            "marked as a design recommendation, not an extraction."
        ),
    }


def build_contrast_findings(measurements: Measurements) -> dict[str, Any]:
    aggregated: dict[str, dict[str, Any]] = {}
    for page_id, probe in measurements.desktop_probes():
        for pair in probe.get("contrast_pairs", []):
            key = f"{pair['fg']}|{pair['bg']}"
            slot = aggregated.setdefault(
                key,
                {
                    "fg": pair["fg"], "bg": pair["bg"], "count": 0, "area": 0,
                    "roles": defaultdict(int), "min_font_px": 9999, "max_weight": 0, "pages": set(),
                },
            )
            slot["count"] += pair["count"]
            slot["area"] += pair["area"]
            slot["pages"].add(page_id)
            slot["min_font_px"] = min(slot["min_font_px"], pair.get("min_font_px", 16))
            slot["max_weight"] = max(slot["max_weight"], pair.get("max_weight", 400))
            for role, n in (pair.get("roles") or {}).items():
                slot["roles"][role] += n

    findings = []
    for slot in aggregated.values():
        fg, bg = parse_color(slot["fg"]), parse_color(slot["bg"])
        if not fg or not bg:
            continue
        ratio = contrast_ratio(fg, bg)
        required = wcag_requirement(slot["min_font_px"], slot["max_weight"])
        passes = ratio >= required
        entry = {
            "foreground": to_hex(fg),
            "background": to_hex(bg),
            "contrast_ratio": round(ratio, 2),
            "required_ratio": required,
            "wcag_aa": passes,
            "wcag_aaa": ratio >= (4.5 if required == 3.0 else 7.0),
            "min_font_px": slot["min_font_px"],
            "max_font_weight": slot["max_weight"],
            "instances": slot["count"],
            "area": slot["area"],
            "pages": sorted(slot["pages"]),
            "top_roles": sorted(slot["roles"].items(), key=lambda kv: -kv[1])[:4],
        }
        if not passes:
            entry["accessible_alternative"] = suggest_accessible(fg, bg, required)
        findings.append(entry)
    findings.sort(key=lambda f: (f["wcag_aa"], -f["area"]))
    failures = [f for f in findings if not f["wcag_aa"]]
    return {
        "pairs": findings,
        "summary": {
            "total_pairs": len(findings),
            "failing_pairs": len(failures),
            "failing_area_share": round(
                sum(f["area"] for f in failures) / max(1, sum(f["area"] for f in findings)), 4
            ),
        },
    }


def build_dark_mode(measurements: Measurements) -> dict[str, Any]:
    dark_pages = list(measurements.dark_probes())
    if not dark_pages:
        return {"supported": False, "reason": "no dark-mode capture pass in this run"}

    def dominant_bg(probe: dict[str, Any]) -> str | None:
        census = probe.get("census", {}).get("background_color") or {}
        if not census:
            return None
        return max(census.items(), key=lambda kv: kv[1].get("area", 0))[0]

    comparisons = []
    supported = False
    for page in measurements.pages:
        light = page.get("measurements", {}).get("desktop")
        dark = page.get("measurements", {}).get("dark")
        if not light or not dark:
            continue
        light_bg, dark_bg = dominant_bg(light), dominant_bg(dark)
        lrgb, drgb = parse_color(light_bg or ""), parse_color(dark_bg or "")
        differs = bool(lrgb and drgb and delta_e_ok(lrgb, drgb) > 0.08)
        supported = supported or differs
        comparisons.append(
            {
                "page_id": page["page_id"],
                "light_dominant_background": to_hex(lrgb) if lrgb else None,
                "dark_dominant_background": to_hex(drgb) if drgb else None,
                "differs": differs,
            }
        )

    dark_tokens = {}
    if supported:
        dark_measurements = Measurements(
            [
                {"page_id": p["page_id"], "measurements": {"desktop": p["measurements"]["dark"]}}
                for p in measurements.pages
                if p.get("measurements", {}).get("dark")
            ]
        )
        dark_tokens = build_color_tokens(dark_measurements)

    return {
        "supported": supported,
        "declared_media_query": any(
            "prefers-color-scheme" in q.get("condition", "")
            for _, probe in measurements.desktop_probes()
            for q in probe.get("cssom", {}).get("media_queries", [])
        ),
        "page_comparisons": comparisons,
        "color_tokens": dark_tokens,
    }


# -------------------------------------------------------- canonical selection


def canonicalize(raw: dict[str, Any], threshold: float, fidelity_mode: str) -> dict[str, Any]:
    """Promote measured candidates to a canonical set, recording every change.

    In `verbatim` mode nothing is snapped or dropped — the observed values are
    passed straight through so you can see exactly what the site does.
    """
    changes: list[dict[str, Any]] = []
    canonical: dict[str, Any] = {"color": {}, "typography": {}, "spacing": {}, "radius": {}, "shadow": {}, "motion": {}, "layout": {}}
    normalize = fidelity_mode != "verbatim"

    # --- colour: one token per inferred role, best-confidence wins ---------
    role_best: dict[str, dict[str, Any]] = {}
    role_alternates: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for clusters in raw["color"]["groups"].values():
        for cluster in clusters:
            for role in cluster["roles"]:
                if role == "unassigned":
                    continue
                role_alternates[role].append(cluster)
                incumbent = role_best.get(role)
                if incumbent is None or cluster["confidence"] > incumbent["confidence"]:
                    role_best[role] = cluster
    for role, cluster in sorted(role_best.items()):
        alternates = [
            {"hex": c["hex"], "confidence": c["confidence"], "instances": c["instances"]}
            for c in sorted(role_alternates[role], key=lambda c: -c["confidence"])[1:4]
        ]
        canonical["color"][role] = {
            "value": cluster["hex"],
            "oklch": cluster["oklch"],
            "confidence": cluster["confidence"],
            "evidence": {"pages": cluster["pages"], "instances": cluster["instances"], "declared_as": cluster["declared_as"]},
            "status": "canonical" if cluster["confidence"] >= threshold else "low_confidence_candidate",
            "alternates": alternates,
        }
        if cluster["variant_count"] > 1:
            changes.append(
                {
                    "type": "color_merge",
                    "token": f"color.{role}",
                    "canonical": cluster["hex"],
                    "observed": cluster["observed_values"],
                    "rationale": (
                        f"{cluster['variant_count']} near-identical values merged "
                        f"(max ΔE {cluster['perceptual_spread']} ≤ {COLOR_MERGE_THRESHOLD})"
                    ),
                    "applied": True,
                }
            )

    # --- typography ---------------------------------------------------------
    families = raw["typography"]["families"]
    if families:
        canonical["typography"]["font_family_primary"] = {
            "value": families[0]["stack"],
            "confidence": families[0]["confidence"],
            "status": "canonical" if families[0]["confidence"] >= threshold else "low_confidence_candidate",
        }
        if len(families) > 1:
            canonical["typography"]["font_family_secondary"] = {
                "value": families[1]["stack"],
                "confidence": families[1]["confidence"],
                "status": "canonical" if families[1]["confidence"] >= threshold else "low_confidence_candidate",
            }
        if len(families) > 2:
            changes.append(
                {
                    "type": "font_family_reduction",
                    "token": "typography.font_family",
                    "canonical": [f["stack"] for f in families[:2]],
                    "observed": [f["stack"] for f in families],
                    "rationale": f"{len(families)} families observed; kept the two with the highest rendered-area share",
                    "applied": normalize,
                }
            )

    steps = raw["typography"]["scale"]["steps"]
    total_text_area = sum(s["area"] for s in steps) or 1

    def keep_size(step: dict[str, Any]) -> bool:
        """A display size appears once per page but defines the brand.

        Pruning on instance count alone deletes the h1, which is usually the
        single largest block of text on the site. Area share and heading role
        both rescue it.
        """
        if step["instances"] >= 2:
            return True
        if step["area"] / total_text_area >= 0.02:
            return True
        return any(role.startswith("heading") for role, _ in step.get("roles", []))

    kept_sizes = [s["px"] for s in steps if keep_size(s)] or [s["px"] for s in steps]
    canonical["typography"]["size_scale"] = sorted(kept_sizes)
    dropped = sorted({s["px"] for s in steps} - set(kept_sizes))
    if dropped:
        changes.append(
            {
                "type": "type_size_pruning",
                "token": "typography.size_scale",
                "canonical": sorted(kept_sizes),
                "observed": sorted({s["px"] for s in steps}),
                "rationale": (
                    f"dropped {len(dropped)} size(s) with a single instance, under 2% of text area, "
                    f"and no heading role: {dropped}"
                ),
                "applied": normalize,
            }
        )
    if fidelity_mode == "verbatim":
        canonical["typography"]["size_scale"] = sorted({s["px"] for s in steps})
    canonical["typography"]["line_height_by_size"] = raw["typography"]["line_height_by_size"]
    canonical["typography"]["weights"] = sorted(
        {int(w) for w in raw["typography"]["weights"] if str(w).isdigit()}
    )
    canonical["typography"]["scale_ratio"] = raw["typography"]["scale"].get("ratio")

    # --- spacing ------------------------------------------------------------
    spacing = raw["spacing"]["combined"]
    canonical["spacing"]["base_unit"] = spacing["base_unit"]
    canonical["spacing"]["grid_conformance"] = spacing["conformance"]
    if normalize and spacing["base_unit"]:
        base = spacing["base_unit"]
        snapped = sorted({int(round(v / base) * base) for v in spacing["scale"] if v > 0})
        canonical["spacing"]["scale"] = snapped
        if spacing["off_grid"]:
            changes.append(
                {
                    "type": "spacing_snap",
                    "token": "spacing.scale",
                    "canonical": snapped,
                    "observed": spacing["scale"],
                    "off_grid_values": spacing["off_grid"],
                    "rationale": (
                        f"{len(spacing['off_grid'])} off-grid value(s) snapped to the {base}px base unit "
                        f"(observed grid conformance {spacing['conformance']:.0%})"
                    ),
                    "applied": True,
                }
            )
    else:
        canonical["spacing"]["scale"] = spacing["scale"]

    # --- radius / shadow / motion / layout ----------------------------------
    radius_scale = [r["px"] for r in raw["radius"]["scale"] if r["instances"] >= 2] or [
        r["px"] for r in raw["radius"]["scale"]
    ]
    canonical["radius"]["scale"] = sorted(set(radius_scale))
    canonical["radius"]["pill"] = raw["radius"]["pill_instances"] > 0
    if fidelity_mode == "verbatim":
        canonical["radius"]["scale"] = sorted({r["px"] for r in raw["radius"]["scale"]})
    elif len(raw["radius"]["scale"]) > len(radius_scale):
        changes.append(
            {
                "type": "radius_pruning",
                "token": "radius.scale",
                "canonical": sorted(set(radius_scale)),
                "observed": sorted({r["px"] for r in raw["radius"]["scale"]}),
                "rationale": "dropped single-instance radii as accidental variants",
                "applied": True,
            }
        )

    canonical["shadow"]["ladder"] = [
        {"step": s["ladder_step"], "value": s["value"], "instances": s["instances"]}
        for s in raw["elevation"]["ladder"]
    ]
    canonical["motion"] = {
        "durations": raw["motion"]["durations"],
        "easings": raw["motion"]["easings"][:3],
        "has_motion_system": raw["motion"]["has_motion_system"],
    }
    canonical["layout"] = {
        "breakpoints": [b["px"] for b in raw["layout"]["breakpoints"]],
        "containers": [c["px"] for c in raw["layout"]["containers"][:4]],
        "z_index_ladder": [z["z"] for z in raw["layout"]["z_index_ladder"]],
    }

    return {"tokens": canonical, "changes": changes}


def render_diff_markdown(raw: dict[str, Any], canonical: dict[str, Any], changes: list[dict[str, Any]], mode: str) -> str:
    lines = [
        "# Raw vs Canonical Diff",
        "",
        f"Fidelity mode: `{mode}`",
        "",
        "Every normalization applied to the measured values is listed here. Nothing",
        "is changed silently — if a value in the token set differs from what the site",
        "actually renders, the change appears below with its rationale.",
        "",
    ]
    if not changes:
        lines += ["No normalizations were applied. Canonical tokens equal measured values.", ""]
    else:
        lines += ["| Token | Canonical | Observed | Applied | Rationale |", "| --- | --- | --- | --- | --- |"]
        for change in changes:
            observed = change.get("observed")
            observed_text = ", ".join(str(v) for v in observed) if isinstance(observed, list) else str(observed)
            if len(observed_text) > 90:
                observed_text = observed_text[:87] + "…"
            canonical_value = change.get("canonical")
            canonical_text = ", ".join(str(v) for v in canonical_value) if isinstance(canonical_value, list) else str(canonical_value)
            if len(canonical_text) > 60:
                canonical_text = canonical_text[:57] + "…"
            lines.append(
                f"| `{change['token']}` | {canonical_text} | {observed_text} | "
                f"{'yes' if change.get('applied') else 'no (verbatim mode)'} | {change['rationale']} |"
            )
        lines.append("")

    lines += ["## Measured values retained in full", "", "The unmodified measurements are in `evidence/measured-raw.json`:", ""]
    lines += [
        f"- {len(raw['color']['groups']['background_color'])} background colour clusters, "
        f"{len(raw['color']['groups']['text_color'])} text colour clusters, "
        f"{len(raw['color']['groups']['border_color'])} border colour clusters",
        f"- {len(raw['typography']['scale']['steps'])} distinct font sizes, {len(raw['typography']['families'])} families",
        f"- spacing base unit {raw['spacing']['combined']['base_unit']}px at "
        f"{raw['spacing']['combined']['conformance']:.0%} conformance across "
        f"{raw['spacing']['combined']['distinct_values_observed']} distinct values",
        f"- {raw['elevation']['distinct_values']} distinct shadows, {raw['radius']['distinct_values']} distinct radii",
        "",
    ]
    return "\n".join(lines)


# ------------------------------------------------------------------- entry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output_dir", nargs="?", default="design-system-output")
    parser.add_argument(
        "--fidelity-mode",
        choices=["modernized", "verbatim"],
        default="modernized",
        help="verbatim keeps every measured value; modernized snaps and prunes (default)",
    )
    parser.add_argument("--threshold", type=float, default=0.70, help="canonical token confidence threshold")
    args = parser.parse_args()

    root = Path(args.output_dir)
    pages_dir = root / "evidence" / "pages"
    if not pages_dir.exists():
        print(f"ERROR: no measurements at {pages_dir}. Run capture_site.mjs first.")
        return 1

    pages = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(pages_dir.glob("*.json"))]
    if not pages:
        print(f"ERROR: {pages_dir} is empty. Run capture_site.mjs first.")
        return 1
    measurements = Measurements(pages)

    raw = {
        "schema": "psdsm/measured-raw@1",
        "pages_measured": measurements.page_count,
        "color": build_color_tokens(measurements),
        "typography": build_typography(measurements),
        "spacing": build_spacing(measurements),
        "radius": build_radius(measurements),
        "elevation": build_elevation(measurements),
        "motion": build_motion(measurements),
        "layout": build_layout(measurements),
        "icons": build_icons(measurements),
        "declared_custom_properties": measurements.declared_values(),
        "brand_signals": measurements.brand_signals(),
        "framework_fingerprint": [
            {"page_id": pid, **(probe.get("framework") or {})} for pid, probe in measurements.desktop_probes()
        ],
    }

    contrast = build_contrast_findings(measurements)
    states = build_component_states(measurements)
    dark = build_dark_mode(measurements)

    result = canonicalize(raw, args.threshold, args.fidelity_mode)
    canonical, changes = result["tokens"], result["changes"]

    confidence_report = {
        "schema": "psdsm/extraction-confidence@2",
        "threshold": args.threshold,
        "fidelity_mode": args.fidelity_mode,
        "model": {
            "formula": "0.45*coverage + 0.25*instances + 0.20*area + 0.10*declared - spread_penalty",
            "weights": CONFIDENCE_WEIGHTS,
            "notes": "See references/confidence-model.md for the definition of each component.",
        },
        "pages_measured": measurements.page_count,
        "tokens": {
            f"color.{role}": {
                "confidence": entry["confidence"],
                "status": entry["status"],
                "evidence_refs": entry["evidence"]["pages"],
                "declared_as": entry["evidence"]["declared_as"],
            }
            for role, entry in canonical["color"].items()
        },
        "components": {
            entry["signature"]: {
                "measured_states": entry["measured_states"],
                "unmeasured_states": entry["unmeasured_states"],
                "has_visible_focus_indicator": entry["has_visible_focus_indicator"],
            }
            for entry in states["components"]
        },
        "warnings": sorted({w for page in pages for w in page.get("warnings", [])}),
        "low_confidence_tokens": [
            f"color.{role}" for role, entry in canonical["color"].items() if entry["status"] != "canonical"
        ],
    }

    evidence = root / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    tokens_dir = root / "tokens"
    tokens_dir.mkdir(parents=True, exist_ok=True)

    (evidence / "measured-raw.json").write_text(json.dumps(raw, indent=2, default=str), encoding="utf-8")
    (evidence / "contrast-findings.json").write_text(json.dumps(contrast, indent=2), encoding="utf-8")
    (evidence / "component-observations.json").write_text(json.dumps(states, indent=2), encoding="utf-8")
    (evidence / "dark-mode.json").write_text(json.dumps(dark, indent=2, default=str), encoding="utf-8")
    (evidence / "extraction-confidence.json").write_text(json.dumps(confidence_report, indent=2), encoding="utf-8")
    (evidence / "raw-vs-canonical-diff.md").write_text(
        render_diff_markdown(raw, canonical, changes, args.fidelity_mode), encoding="utf-8"
    )
    (tokens_dir / "tokens.source.json").write_text(
        json.dumps(
            {
                "schema": "psdsm/tokens-source@1",
                "fidelity_mode": args.fidelity_mode,
                "threshold": args.threshold,
                "canonical": canonical,
                "dark": dark.get("color_tokens", {}),
                "icons": raw["icons"],
                "changes": changes,
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print(f"Aggregated {measurements.page_count} page(s) in `{args.fidelity_mode}` mode")
    print(f"  colour roles:        {len(canonical['color'])}")
    print(f"  type sizes:          {len(canonical['typography'].get('size_scale', []))}")
    print(f"  spacing base unit:   {canonical['spacing']['base_unit']}px "
          f"({canonical['spacing']['grid_conformance']:.0%} conformance)")
    print(f"  breakpoints:         {canonical['layout']['breakpoints']}")
    print(f"  contrast failures:   {contrast['summary']['failing_pairs']}/{contrast['summary']['total_pairs']}")
    print(f"  components w/ states:{len(states['components'])}")
    print(f"  dark mode supported: {dark['supported']}")
    print(f"  normalizations:      {len(changes)} (see evidence/raw-vs-canonical-diff.md)")
    if confidence_report["low_confidence_tokens"]:
        print(f"  low confidence:      {confidence_report['low_confidence_tokens']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
