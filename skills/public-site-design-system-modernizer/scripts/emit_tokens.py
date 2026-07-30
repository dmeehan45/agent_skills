#!/usr/bin/env python3
"""Emit consumable design-system artifacts from aggregated token candidates.

Reads `tokens/tokens.source.json` (written by aggregate_tokens.py) and writes:

  tokens/tokens.json          W3C DTCG format ($value/$type) — imports into
                              Style Dictionary, Tokens Studio, Figma
  tokens/tokens.css           three-layer CSS custom properties + dark mode
  tokens/tailwind.theme.js    Tailwind v3 config fragment
  tokens/tailwind.theme.css   Tailwind v4 @theme block
  tokens/preview.html         self-contained token + component gallery
  components/component-contracts.json
                              measured component contracts (see
                              references/component-contract-schema.md)

The token set is layered primitive -> semantic -> component. A flat dump cannot
be rethemed: every consumer ends up hardcoding primitives.

Usage:
  python3 emit_tokens.py design-system-output
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

# Reuse the colour maths from the aggregator so both stages agree exactly.
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aggregate_tokens import (  # noqa: E402
    contrast_ratio,
    parse_color,
    to_hex,
    to_oklch,
)

# ------------------------------------------------------------ primitive names

HUE_FAMILIES = [
    (15, "red"), (45, "orange"), (70, "amber"), (100, "yellow"), (135, "lime"),
    (165, "green"), (195, "teal"), (225, "cyan"), (265, "blue"), (295, "indigo"),
    (320, "violet"), (345, "pink"), (360, "red"),
]

LIGHTNESS_STEPS = [
    (0.97, "50"), (0.93, "100"), (0.87, "200"), (0.79, "300"), (0.70, "400"),
    (0.60, "500"), (0.50, "600"), (0.41, "700"), (0.32, "800"), (0.22, "900"), (0.0, "950"),
]


def hue_family(hue: float) -> str:
    for bound, name in HUE_FAMILIES:
        if hue <= bound:
            return name
    return "red"


def lightness_step(lightness: float) -> str:
    for bound, name in LIGHTNESS_STEPS:
        if lightness >= bound:
            return name
    return "950"


# Below this OKLCH chroma a colour reads as a (possibly hue-tinted) neutral.
# Brand greys are rarely pure: 0.02 is too strict and names slate inks "blue".
NEUTRAL_CHROMA_MAX = 0.045


def primitive_name(hex_value: str) -> str:
    """Derive a stable primitive name from the colour itself."""
    rgb = parse_color(hex_value)
    if not rgb:
        return "color-unknown"
    L, C, H = to_oklch(rgb)
    if C < NEUTRAL_CHROMA_MAX:
        if L >= 0.99:
            return "white"
        if L <= 0.02:
            return "black"
        return f"neutral-{lightness_step(L)}"
    return f"{hue_family(H)}-{lightness_step(L)}"


def dedupe_primitives(values: list[str]) -> dict[str, str]:
    """hex -> primitive name, disambiguating collisions with a numeric suffix."""
    used: dict[str, str] = {}
    taken: set[str] = set()
    for hex_value in values:
        if hex_value in used:
            continue
        base = primitive_name(hex_value)
        name = base
        suffix = 1
        while name in taken:
            suffix += 1
            name = f"{base}-{suffix}"
        taken.add(name)
        used[hex_value] = name
    return used


def scale_step_names(values: list[float], prefix: str) -> dict[float, str]:
    """Name a numeric scale by index so it stays stable as values shift."""
    return {value: f"{prefix}-{index}" for index, value in enumerate(sorted(values))}


# --------------------------------------------------------------- token model


class TokenSet:
    def __init__(self, source: dict[str, Any], observations: dict[str, Any] | None):
        self.source = source
        self.canonical = source.get("canonical", {})
        self.dark = source.get("dark", {})
        self.icons = source.get("icons", {})
        self.observations = observations or {}
        self.fidelity_mode = source.get("fidelity_mode", "modernized")

        colors = self.canonical.get("color", {})
        self.semantic_colors = {role: entry["value"] for role, entry in colors.items()}
        self.color_meta = colors
        self.color_primitives = dedupe_primitives(
            sorted(set(self.semantic_colors.values()), key=lambda h: (to_oklch(parse_color(h) or (0, 0, 0, 1))[0]))
        )

        self.spacing = self.canonical.get("spacing", {}).get("scale", []) or []
        self.spacing_names = scale_step_names([float(v) for v in self.spacing], "space")
        self.type_sizes = [float(v) for v in self.canonical.get("typography", {}).get("size_scale", [])]
        self.type_names = scale_step_names(self.type_sizes, "font-size")
        self.radii = [float(v) for v in self.canonical.get("radius", {}).get("scale", [])]
        self.radius_names = scale_step_names(self.radii, "radius")
        self.shadows = self.canonical.get("shadow", {}).get("ladder", [])
        self.motion = self.canonical.get("motion", {})
        self.layout = self.canonical.get("layout", {})
        self.typography = self.canonical.get("typography", {})

    # -- dark mode -----------------------------------------------------------

    def dark_semantic_colors(self) -> dict[str, str]:
        groups = (self.dark or {}).get("groups") or {}
        best: dict[str, tuple[float, str]] = {}
        for clusters in groups.values():
            for cluster in clusters:
                for role in cluster.get("roles", []):
                    if role == "unassigned":
                        continue
                    incumbent = best.get(role)
                    if incumbent is None or cluster["confidence"] > incumbent[0]:
                        best[role] = (cluster["confidence"], cluster["hex"])
        return {role: value for role, (_, value) in best.items()}

    # -- component layer -----------------------------------------------------

    def component_tokens(self) -> dict[str, dict[str, str]]:
        """Component tokens alias semantic ones, with measured state overrides."""
        out: dict[str, dict[str, str]] = {}
        button_radius = self.radii[len(self.radii) // 2] if self.radii else 0
        out["button-primary"] = {
            "bg": "var(--ds-color-action-background)" if "action.background" in self.semantic_colors else "var(--ds-color-text-heading)",
            "fg": "var(--ds-color-text-on-action)" if "text.on-action" in self.semantic_colors else "#ffffff",
            "radius": f"var(--ds-{self.radius_names.get(button_radius, 'radius-0')})" if self.radii else "0",
            "border-color": "transparent",
        }
        out["surface-card"] = {
            "bg": "var(--ds-color-surface-base)" if "surface.base" in self.semantic_colors else "#ffffff",
            "border-color": "var(--ds-color-border-default)" if "border.default" in self.semantic_colors else "transparent",
            "radius": f"var(--ds-{self.radius_names.get(self.radii[-1], 'radius-0')})" if self.radii else "0",
            "shadow": "var(--ds-shadow-0)" if self.shadows else "none",
        }
        out["field"] = {
            "bg": "var(--ds-color-surface-field)" if "surface.field" in self.semantic_colors else "var(--ds-color-surface-base)",
            "fg": "var(--ds-color-text-heading)" if "text.heading" in self.semantic_colors else "inherit",
            "border-color": "var(--ds-color-border-control)" if "border.control" in self.semantic_colors else "var(--ds-color-border-default)",
            "radius": f"var(--ds-{self.radius_names.get(self.radii[0], 'radius-0')})" if self.radii else "0",
        }

        # Fold in measured state values where they exist.
        for component in self.observations.get("components", []):
            states = component.get("states") or {}
            hover = states.get("hover") or {}
            if component.get("role") == "button" or "btn" in (component.get("signature") or ""):
                if "background_color" in hover:
                    rgb = parse_color(hover["background_color"]["to"])
                    if rgb and rgb[3] > 0.05:
                        out["button-primary"]["bg-hover"] = to_hex(rgb)
                active = states.get("active") or {}
                if "background_color" in active:
                    rgb = parse_color(active["background_color"]["to"])
                    if rgb and rgb[3] > 0.05:
                        out["button-primary"]["bg-active"] = to_hex(rgb)
            focus = states.get("focus_visible") or states.get("focus") or {}
            if "outline" in focus and focus["outline"]["to"]:
                out.setdefault("focus", {})["ring"] = focus["outline"]["to"]
                if "outline_offset" in focus:
                    out["focus"]["ring-offset"] = focus["outline_offset"]["to"]
        return out


# ------------------------------------------------------------------- emitters


def css_var_name(role: str) -> str:
    return "--ds-color-" + role.replace(".", "-")


def emit_dtcg(tokens: TokenSet) -> dict[str, Any]:
    """W3C Design Token Community Group format."""

    def group(description: str, items: dict[str, Any]) -> dict[str, Any]:
        return {"$description": description, **items}

    color_primitives = {
        name: {"$value": hex_value, "$type": "color", "$description": f"Measured on the source site as {hex_value}"}
        for hex_value, name in tokens.color_primitives.items()
    }
    color_semantic = {}
    for role, hex_value in tokens.semantic_colors.items():
        meta = tokens.color_meta.get(role, {})
        color_semantic[role.replace(".", "-")] = {
            "$value": f"{{color.primitive.{tokens.color_primitives[hex_value]}}}",
            "$type": "color",
            "$description": f"role: {role}",
            "$extensions": {
                "psdsm": {
                    "resolved": hex_value,
                    "confidence": meta.get("confidence"),
                    "status": meta.get("status"),
                    "declared_as": (meta.get("evidence") or {}).get("declared_as"),
                    "evidence_pages": (meta.get("evidence") or {}).get("pages", []),
                }
            },
        }

    dark = tokens.dark_semantic_colors()
    if dark:
        dark_primitives = dedupe_primitives(sorted(set(dark.values())))
        for hex_value, name in dark_primitives.items():
            color_primitives.setdefault(
                f"dark-{name}", {"$value": hex_value, "$type": "color", "$description": "measured in dark mode"}
            )

    document: dict[str, Any] = {
        "$schema": "https://tr.designtokens.org/format/",
        "$description": (
            f"Extracted from a public website in `{tokens.fidelity_mode}` mode. "
            "Values carry measurement provenance under $extensions.psdsm."
        ),
        "color": {
            "primitive": group("Raw measured colours, named by hue and lightness", color_primitives),
            **{k: v for k, v in [("semantic", group("Role-assigned colours; alias these, not primitives", color_semantic))]},
        },
        "dimension": {
            "space": group(
                f"Spacing scale on a {tokens.canonical.get('spacing', {}).get('base_unit')}px base unit",
                {
                    name: {"$value": f"{value:g}px", "$type": "dimension"}
                    for value, name in tokens.spacing_names.items()
                },
            ),
            "radius": group(
                "Corner radii",
                {name: {"$value": f"{value:g}px", "$type": "dimension"} for value, name in tokens.radius_names.items()},
            ),
        },
        "typography": {
            "family": group(
                "Font stacks ranked by rendered-area share",
                {
                    "primary": {
                        "$value": tokens.typography.get("font_family_primary", {}).get("value", "system-ui, sans-serif"),
                        "$type": "fontFamily",
                    },
                    **(
                        {"secondary": {"$value": tokens.typography["font_family_secondary"]["value"], "$type": "fontFamily"}}
                        if tokens.typography.get("font_family_secondary")
                        else {}
                    ),
                },
            ),
            "size": group(
                f"Type scale (fitted ratio {tokens.typography.get('scale_ratio')})",
                {name: {"$value": f"{value:g}px", "$type": "dimension"} for value, name in tokens.type_names.items()},
            ),
            "weight": group(
                "Observed weights",
                {
                    f"w{weight}": {"$value": weight, "$type": "fontWeight"}
                    for weight in tokens.typography.get("weights", [])
                },
            ),
            "lineHeight": group(
                "Dominant line-height per size, as a unitless multiplier",
                {
                    f"size-{size}": {"$value": ratio, "$type": "number"}
                    for size, ratio in (tokens.typography.get("line_height_by_size") or {}).items()
                },
            ),
        },
        "shadow": group(
            "Elevation ladder, ordered by blur radius",
            {
                f"elevation-{entry['step']}": {"$value": entry["value"], "$type": "shadow"}
                for entry in tokens.shadows
            },
        ),
        "duration": group(
            "Transition durations measured from computed styles",
            {
                f"d{index}": {"$value": entry["value"], "$type": "duration"}
                for index, entry in enumerate(tokens.motion.get("durations", []))
            },
        ),
        "cubicBezier": group(
            "Easings measured from computed styles",
            {
                f"ease-{index}": {"$value": entry["value"], "$type": "cubicBezier"}
                for index, entry in enumerate(tokens.motion.get("easings", []))
            },
        ),
        "breakpoint": group(
            "Breakpoints harvested from the site's own @media rules",
            {f"bp-{int(value)}": {"$value": f"{int(value)}px", "$type": "dimension"} for value in tokens.layout.get("breakpoints", [])},
        ),
        "container": group(
            "Container widths measured from rendered bounding boxes",
            {f"container-{int(value)}": {"$value": f"{int(value)}px", "$type": "dimension"} for value in tokens.layout.get("containers", [])},
        ),
    }
    if dark:
        document["color"]["semanticDark"] = group(
            "Dark-mode role colours measured under prefers-color-scheme: dark",
            {
                role.replace(".", "-"): {"$value": hex_value, "$type": "color"}
                for role, hex_value in dark.items()
            },
        )
    return document


def emit_css(tokens: TokenSet) -> str:
    lines = [
        "/* Design tokens extracted from a public website.",
        f"   Fidelity mode: {tokens.fidelity_mode}",
        "",
        "   Layered primitive -> semantic -> component. Consume the semantic and",
        "   component layers; retheming means overriding those, never primitives. */",
        "",
        ":root {",
        "  /* ---- layer 1: primitives (measured values) ---- */",
    ]
    for hex_value, name in tokens.color_primitives.items():
        lines.append(f"  --ds-{name}: {hex_value};")
    lines.append("")
    for value, name in sorted(tokens.spacing_names.items()):
        lines.append(f"  --ds-{name}: {value:g}px;")
    lines.append("")
    for value, name in sorted(tokens.type_names.items()):
        lines.append(f"  --ds-{name}: {value:g}px;")
    lines.append("")
    for value, name in sorted(tokens.radius_names.items()):
        lines.append(f"  --ds-{name}: {value:g}px;")
    if tokens.canonical.get("radius", {}).get("pill"):
        lines.append("  --ds-radius-pill: 9999px;")
    lines.append("")
    for entry in tokens.shadows:
        lines.append(f"  --ds-shadow-{entry['step']}: {entry['value']};")
    lines.append("")
    for index, entry in enumerate(tokens.motion.get("durations", [])):
        lines.append(f"  --ds-duration-{index}: {entry['value']};")
    for index, entry in enumerate(tokens.motion.get("easings", [])):
        lines.append(f"  --ds-ease-{index}: {entry['value']};")
    lines.append("")
    primary = tokens.typography.get("font_family_primary", {}).get("value")
    if primary:
        lines.append(f"  --ds-font-family-primary: {primary};")
    secondary = tokens.typography.get("font_family_secondary", {}).get("value")
    if secondary:
        lines.append(f"  --ds-font-family-secondary: {secondary};")
    for weight in tokens.typography.get("weights", []):
        lines.append(f"  --ds-font-weight-{weight}: {weight};")
    for size, ratio in (tokens.typography.get("line_height_by_size") or {}).items():
        lines.append(f"  --ds-line-height-{str(size).replace('.', '_')}: {ratio};")
    lines.append("")
    for value in tokens.layout.get("containers", []):
        lines.append(f"  --ds-container-{int(value)}: {int(value)}px;")
    for index, value in enumerate(tokens.layout.get("z_index_ladder", [])):
        lines.append(f"  --ds-z-{index}: {value};")

    lines += ["", "  /* ---- layer 2: semantic roles (alias these) ---- */"]
    for role, hex_value in sorted(tokens.semantic_colors.items()):
        meta = tokens.color_meta.get(role, {})
        marker = "" if meta.get("status") == "canonical" else "  /* low confidence — verify before use */"
        lines.append(f"  {css_var_name(role)}: var(--ds-{tokens.color_primitives[hex_value]});{marker}")

    component = tokens.component_tokens()
    lines += ["", "  /* ---- layer 3: component tokens ---- */"]
    for name, props in sorted(component.items()):
        for prop, value in props.items():
            lines.append(f"  --ds-{name}-{prop}: {value};")
    lines.append("}")

    dark = tokens.dark_semantic_colors()
    if dark:
        body = [
            f"    {css_var_name(role)}: {hex_value};"
            for role, hex_value in sorted(dark.items())
        ]
        lines += [
            "",
            "/* Dark mode overrides the semantic layer only. Measured under",
            "   prefers-color-scheme: dark on the source site. */",
            "@media (prefers-color-scheme: dark) {",
            "  :root {",
            *body,
            "  }",
            "}",
            "",
            '[data-theme="dark"] {',
            *[line[2:] for line in body],
            "}",
        ]
    else:
        lines += [
            "",
            "/* No dark mode detected on the source site. Add a @media",
            "   (prefers-color-scheme: dark) block overriding the semantic layer. */",
        ]
    return "\n".join(lines) + "\n"


def emit_tailwind_v3(tokens: TokenSet) -> str:
    colors = {role.replace(".", "-"): f"var({css_var_name(role)})" for role in tokens.semantic_colors}
    spacing = {name.replace("space-", ""): f"var(--ds-{name})" for _, name in sorted(tokens.spacing_names.items())}
    font_size = {name.replace("font-size-", "s"): f"var(--ds-{name})" for _, name in sorted(tokens.type_names.items())}
    radius = {name.replace("radius-", ""): f"var(--ds-{name})" for _, name in sorted(tokens.radius_names.items())}
    if tokens.canonical.get("radius", {}).get("pill"):
        radius["pill"] = "var(--ds-radius-pill)"
    shadow = {str(entry["step"]): f"var(--ds-shadow-{entry['step']})" for entry in tokens.shadows}
    screens = {f"bp{int(value)}": f"{int(value)}px" for value in tokens.layout.get("breakpoints", [])}
    max_width = {f"container-{int(value)}": f"var(--ds-container-{int(value)})" for value in tokens.layout.get("containers", [])}
    families = {}
    if tokens.typography.get("font_family_primary"):
        families["sans"] = "var(--ds-font-family-primary)"
    if tokens.typography.get("font_family_secondary"):
        families["display"] = "var(--ds-font-family-secondary)"
    duration = {str(i): e["value"] for i, e in enumerate(tokens.motion.get("durations", []))}
    timing = {str(i): e["value"] for i, e in enumerate(tokens.motion.get("easings", []))}

    theme = {
        "extend": {
            "colors": colors,
            "spacing": spacing,
            "fontSize": font_size,
            "fontFamily": families,
            "borderRadius": radius,
            "boxShadow": shadow,
            "screens": screens,
            "maxWidth": max_width,
            "transitionDuration": duration,
            "transitionTimingFunction": timing,
        }
    }
    return (
        "// Tailwind CSS v3 theme fragment.\n"
        "// Import tokens.css first — every value here resolves a CSS custom property,\n"
        "// so dark mode and retheming work without rebuilding Tailwind.\n"
        "//\n"
        "//   const { theme } = require('./tailwind.theme.js')\n"
        "//   module.exports = { content: [...], theme }\n"
        "//\n"
        "// On Tailwind v4, use tailwind.theme.css instead.\n"
        f"module.exports = {json.dumps({'theme': theme}, indent=2)};\n"
    )


def emit_tailwind_v4(tokens: TokenSet) -> str:
    lines = [
        "/* Tailwind CSS v4 theme. Import after tokens.css:",
        "     @import './tokens.css';",
        "     @import './tailwind.theme.css';",
        "   v4 reads theme values from CSS, so there is no JS config to keep in sync. */",
        "",
        "@theme {",
    ]
    for role in sorted(tokens.semantic_colors):
        lines.append(f"  --color-{role.replace('.', '-')}: var({css_var_name(role)});")
    for value, name in sorted(tokens.spacing_names.items()):
        lines.append(f"  --spacing-{name.replace('space-', '')}: var(--ds-{name});")
    for value, name in sorted(tokens.type_names.items()):
        lines.append(f"  --text-s{name.replace('font-size-', '')}: var(--ds-{name});")
    for value, name in sorted(tokens.radius_names.items()):
        lines.append(f"  --radius-{name.replace('radius-', '')}: var(--ds-{name});")
    if tokens.canonical.get("radius", {}).get("pill"):
        lines.append("  --radius-pill: var(--ds-radius-pill);")
    for entry in tokens.shadows:
        lines.append(f"  --shadow-{entry['step']}: var(--ds-shadow-{entry['step']});")
    for value in tokens.layout.get("breakpoints", []):
        lines.append(f"  --breakpoint-bp{int(value)}: {int(value)}px;")
    for value in tokens.layout.get("containers", []):
        lines.append(f"  --container-c{int(value)}: {int(value)}px;")
    if tokens.typography.get("font_family_primary"):
        lines.append("  --font-sans: var(--ds-font-family-primary);")
    if tokens.typography.get("font_family_secondary"):
        lines.append("  --font-display: var(--ds-font-family-secondary);")
    for index, entry in enumerate(tokens.motion.get("easings", [])):
        lines.append(f"  --ease-e{index}: {entry['value']};")
    lines.append("}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- preview page


def emit_preview(tokens: TokenSet, contrast: dict[str, Any]) -> str:
    swatches = []
    surface = tokens.semantic_colors.get("surface.base", "#ffffff")
    surface_rgb = parse_color(surface) or (255, 255, 255, 1.0)
    for role, hex_value in sorted(tokens.semantic_colors.items()):
        meta = tokens.color_meta.get(role, {})
        rgb = parse_color(hex_value)
        ratio = contrast_ratio(rgb, surface_rgb) if rgb else 0
        status = meta.get("status", "")
        declared = (meta.get("evidence") or {}).get("declared_as") or "measured from rendered pixels"
        swatches.append(
            f'''<figure class="swatch">
      <div class="chip" style="background:{hex_value}"></div>
      <figcaption>
        <code>{role}</code>
        <span class="hex">{hex_value}</span>
        <span class="meta">conf {meta.get("confidence", "—")} · {ratio:.1f}:1 vs surface</span>
        <span class="meta src">{declared}</span>
        {'<span class="warn">low confidence</span>' if status != "canonical" else ''}
      </figcaption>
    </figure>'''
        )

    type_rows = []
    for value, name in sorted(tokens.type_names.items(), reverse=True):
        ratio = (tokens.typography.get("line_height_by_size") or {}).get(str(value), "")
        type_rows.append(
            f'<div class="type-row"><span class="label"><code>{name}</code> {value:g}px'
            f'{f" / lh {ratio}" if ratio else ""}</span>'
            f'<span style="font-size:{value:g}px;line-height:{ratio or 1.3}">Grumpy wizards make toxic brew</span></div>'
        )

    space_rows = [
        f'<div class="space-row"><code>{name}</code>'
        f'<span class="bar" style="width:{value:g}px"></span><span class="v">{value:g}px</span></div>'
        for value, name in sorted(tokens.spacing_names.items())
    ]
    radius_cells = [
        f'<div class="radius-cell"><div class="box" style="border-radius:{value:g}px"></div>'
        f'<code>{name}</code><span>{value:g}px</span></div>'
        for value, name in sorted(tokens.radius_names.items())
    ]
    shadow_cells = [
        f'<div class="shadow-cell"><div class="box" style="box-shadow:{entry["value"]}"></div>'
        f'<code>elevation-{entry["step"]}</code></div>'
        for entry in tokens.shadows
    ]
    motion_cells = [
        f'<div class="motion-cell"><code>{e["value"]}</code><span>{e["instances"]} uses</span></div>'
        for e in tokens.motion.get("durations", [])
    ] or ["<p class='empty'>No transition durations measured on the source site.</p>"]

    failures = [p for p in contrast.get("pairs", []) if not p.get("wcag_aa")]
    contrast_rows = "".join(
        f'<tr><td><span class="dot" style="background:{p["foreground"]}"></span><code>{p["foreground"]}</code></td>'
        f'<td><span class="dot" style="background:{p["background"]}"></span><code>{p["background"]}</code></td>'
        f'<td>{p["contrast_ratio"]}:1</td><td>{p["required_ratio"]}:1</td>'
        f'<td>{p.get("accessible_alternative", {}).get("hex", "—") if p.get("accessible_alternative") else "—"}</td>'
        f'<td>{p["instances"]}</td></tr>'
        for p in failures[:20]
    ) or '<tr><td colspan="6">No AA failures in the measured colour pairs.</td></tr>'

    components = tokens.component_tokens()
    focus_ring = components.get("focus", {}).get("ring", "2px solid var(--ds-color-action-background, #000)")
    btn = components.get("button-primary", {})
    card = components.get("surface-card", {})
    field = components.get("field", {})

    unmeasured = []
    for component in tokens.observations.get("components", [])[:8]:
        if component.get("unmeasured_states"):
            unmeasured.append(
                f'<li><code>{component["signature"]}</code> — not observed: '
                f'{", ".join(component["unmeasured_states"])}</li>'
            )
    unmeasured_block = (
        f'<ul class="gaps">{"".join(unmeasured)}</ul>'
        if unmeasured
        else '<p class="empty">Every probed component had hover, focus-visible and active measured.</p>'
    )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Extracted design system — preview</title>
<link rel="stylesheet" href="./tokens.css">
<style>
  body {{ margin:0; font-family: var(--ds-font-family-primary, system-ui, sans-serif);
         background: var(--ds-color-surface-base, #fff); color: var(--ds-color-text-heading, #111); }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 40px 24px 96px; }}
  h1 {{ font-size: 28px; margin: 0 0 6px; }}
  h2 {{ font-size: 18px; margin: 48px 0 4px; padding-top: 20px; border-top: 1px solid var(--ds-color-border-default, #e5e5e5); }}
  .sub {{ color: var(--ds-color-text-body, #555); font-size: 14px; margin: 0 0 20px; max-width: 62ch; line-height:1.5; }}
  .grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(210px,1fr)); gap:14px; margin-top:16px; }}
  .swatch {{ margin:0; border:1px solid var(--ds-color-border-default,#e5e5e5); border-radius:8px; overflow:hidden; }}
  .chip {{ height:60px; }}
  figcaption {{ padding:10px; display:flex; flex-direction:column; gap:2px; font-size:12px; }}
  figcaption code {{ font-size:12px; font-weight:600; }}
  .hex {{ font-family: ui-monospace, monospace; color: var(--ds-color-text-body,#555); }}
  .meta {{ color: var(--ds-color-text-body,#666); font-size:11px; }}
  .src {{ opacity:.75; }}
  .warn {{ color:#b3261e; font-weight:600; font-size:11px; }}
  .type-row {{ display:flex; gap:20px; align-items:baseline; padding:8px 0;
               border-bottom:1px dashed var(--ds-color-border-default,#eee); }}
  .type-row .label {{ flex:0 0 190px; font-size:12px; color:var(--ds-color-text-body,#666); }}
  .space-row {{ display:flex; align-items:center; gap:12px; padding:3px 0; font-size:12px; }}
  .space-row code {{ flex:0 0 90px; }}
  .space-row .bar {{ height:14px; background: var(--ds-color-action-background, #333); border-radius:2px; }}
  .radius-cell, .shadow-cell, .motion-cell {{ display:flex; flex-direction:column; gap:6px; align-items:center;
      font-size:11px; padding:14px; }}
  .radius-cell .box, .shadow-cell .box {{ width:72px; height:52px;
      background: var(--ds-color-surface-base,#fff); border:1px solid var(--ds-color-border-default,#ddd); }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; margin-top:12px; }}
  th, td {{ text-align:left; padding:7px 10px; border-bottom:1px solid var(--ds-color-border-default,#eee); }}
  .dot {{ display:inline-block; width:12px; height:12px; border-radius:3px; margin-right:6px;
          vertical-align:-2px; border:1px solid rgba(0,0,0,.15); }}
  .demo {{ display:flex; gap:14px; flex-wrap:wrap; align-items:center; margin-top:16px; }}
  .empty {{ color: var(--ds-color-text-body,#777); font-size:13px; font-style:italic; }}
  .gaps {{ font-size:13px; color: var(--ds-color-text-body,#555); line-height:1.7; }}

  /* Components built purely from the emitted tokens — this is the proof. */
  .btn {{ font: inherit; font-weight:600; cursor:pointer; border:1px solid {btn.get('border-color','transparent')};
      background: {btn.get('bg','#000')}; color: {btn.get('fg','#fff')}; border-radius: {btn.get('radius','4px')};
      padding: var(--ds-space-2, 10px) var(--ds-space-4, 20px);
      transition: background-color var(--ds-duration-0, 150ms) var(--ds-ease-0, ease); }}
  .btn:hover {{ background: {btn.get('bg-hover', btn.get('bg','#000'))}; }}
  .btn:active {{ background: {btn.get('bg-active', btn.get('bg','#000'))}; }}
  .btn:focus-visible {{ outline: {focus_ring}; outline-offset: {components.get('focus',{}).get('ring-offset','2px')}; }}
  .btn[disabled] {{ opacity:.45; cursor:not-allowed; }}
  .card {{ background: {card.get('bg','#fff')}; border:1px solid {card.get('border-color','#e5e5e5')};
      border-radius: {card.get('radius','8px')}; box-shadow: {card.get('shadow','none')};
      padding: var(--ds-space-4, 20px); max-width: 300px; }}
  .field {{ font: inherit; background: {field.get('bg','#fff')}; color: {field.get('fg','inherit')};
      border:1px solid {field.get('border-color','#ccc')}; border-radius: {field.get('radius','4px')};
      padding: var(--ds-space-2, 9px) var(--ds-space-3, 12px); width:260px; }}
  .field:focus-visible {{ outline: {focus_ring}; outline-offset: 1px; }}
</style></head>
<body><div class="wrap">
<h1>Extracted design system — preview</h1>
<p class="sub">Every value below was measured from the source site's rendered pages, then emitted as tokens.
Fidelity mode: <code>{tokens.fidelity_mode}</code>. The components at the bottom are built only from these tokens —
if they look like the brand, the extraction held.</p>

<h2>Semantic colours</h2>
<p class="sub">Contrast is measured against <code>surface.base</code>. "conf" is the computed confidence score.</p>
<div class="grid">{"".join(swatches)}</div>

<h2>Type scale</h2>
<p class="sub">Fitted ratio: <code>{tokens.typography.get('scale_ratio') or 'not modular'}</code>.
Primary family: <code>{tokens.typography.get('font_family_primary',{}).get('value','—')}</code></p>
{"".join(type_rows)}

<h2>Spacing</h2>
<p class="sub">Base unit <code>{tokens.canonical.get('spacing',{}).get('base_unit')}px</code>,
observed grid conformance {tokens.canonical.get('spacing',{}).get('grid_conformance', 0):.0%}.</p>
{"".join(space_rows)}

<h2>Radius</h2><div class="grid">{"".join(radius_cells) or "<p class='empty'>No radii measured.</p>"}</div>
<h2>Elevation</h2><div class="grid">{"".join(shadow_cells) or "<p class='empty'>No shadows measured.</p>"}</div>
<h2>Motion</h2><div class="grid">{"".join(motion_cells)}</div>

<h2>Contrast failures</h2>
<p class="sub">Measured foreground/background pairs failing WCAG AA, with a suggested replacement that holds
hue and chroma and moves lightness only.</p>
<table><thead><tr><th>Foreground</th><th>Background</th><th>Ratio</th><th>Required</th><th>Suggested</th><th>Uses</th></tr></thead>
<tbody>{contrast_rows}</tbody></table>

<h2>Components built from these tokens</h2>
<p class="sub">Hover, focus (press Tab) and active states use measured deltas, not invented ones.</p>
<div class="demo">
  <button class="btn" id="fx-button-primary">Primary action</button>
  <button class="btn" disabled>Disabled</button>
  <input class="field" id="fx-field" placeholder="you@company.com">
</div>
<div class="demo">
  <div class="card" id="fx-card"><strong>Card</strong>
  <p style="color:var(--ds-color-text-body,#555);font-size:14px;line-height:1.5;margin:6px 0 0">
  Surface, border, radius and elevation all resolve from the emitted token layer.</p></div>
</div>

<h2>Unmeasured states</h2>
<p class="sub">These were not observable during capture. Treat them as design recommendations, not extractions.</p>
{unmeasured_block}
</div></body></html>
"""


# ------------------------------------------------------- component contracts


def contract_name(signature: str, role: str) -> str:
    tag = signature.split("|")[0]
    classes = signature.split("|")[-1].lower()
    if tag == "button" or "btn" in classes or role == "button":
        if "secondary" in classes or "ghost" in classes or "outline" in classes:
            return "button.secondary"
        return "button.primary"
    if tag == "a":
        return "link.nav" if "nav" in classes else "link.inline"
    if tag == "input":
        return "field.input"
    if tag in ("select", "textarea"):
        return f"field.{tag}"
    return f"{tag}.default"


def emit_component_contracts(tokens: TokenSet) -> dict[str, Any]:
    contracts: dict[str, Any] = {}
    for component in tokens.observations.get("components", []):
        name = contract_name(component["signature"], component.get("role", ""))
        entry = contracts.setdefault(
            name,
            {
                "name": name,
                "evidence": {"signatures": [], "pages": [], "instances": 0},
                "base": component.get("base"),
                "states": {},
                "unmeasured_states": [],
                "accessibility": {},
            },
        )
        entry["evidence"]["signatures"].append(component["signature"])
        entry["evidence"]["pages"] = sorted(set(entry["evidence"]["pages"]) | set(component.get("pages", [])))
        entry["evidence"]["instances"] += component.get("instances", 0)
        for state, delta in (component.get("states") or {}).items():
            if delta and state not in entry["states"]:
                entry["states"][state] = {
                    "source": "measured",
                    "changes": delta,
                }
        for state in component.get("unmeasured_states", []):
            if state not in entry["states"] and state not in entry["unmeasured_states"]:
                entry["unmeasured_states"].append(state)
        entry["accessibility"]["has_visible_focus_indicator"] = (
            entry["accessibility"].get("has_visible_focus_indicator", False)
            or component.get("has_visible_focus_indicator", False)
        )
        base = component.get("base") or {}
        height = base.get("height", "0px")
        try:
            entry["accessibility"]["measured_height_px"] = float(str(height).replace("px", ""))
            entry["accessibility"]["meets_44px_touch_target"] = entry["accessibility"]["measured_height_px"] >= 44
        except ValueError:
            pass

    disabled = tokens.observations.get("disabled_samples") or []
    if disabled:
        for entry in contracts.values():
            if entry["name"].startswith("button") or entry["name"].startswith("field"):
                entry["states"].setdefault(
                    "disabled", {"source": "measured", "samples": disabled[:2]}
                )
                if "disabled" in entry["unmeasured_states"]:
                    entry["unmeasured_states"].remove("disabled")

    return {
        "schema": "psdsm/component-contracts@1",
        "fidelity_mode": tokens.fidelity_mode,
        "note": (
            "`states.*.source == 'measured'` means the delta was observed by scripted "
            "interaction on the live site. Anything in `unmeasured_states` was never "
            "observed and must be designed, not claimed as extracted."
        ),
        "components": list(contracts.values()),
    }


# -------------------------------------------------------------------- entry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output_dir", nargs="?", default="design-system-output")
    args = parser.parse_args()

    root = Path(args.output_dir)
    source_path = root / "tokens" / "tokens.source.json"
    if not source_path.exists():
        print(f"ERROR: {source_path} not found. Run aggregate_tokens.py first.")
        return 1
    source = json.loads(source_path.read_text(encoding="utf-8"))

    observations_path = root / "evidence" / "component-observations.json"
    observations = json.loads(observations_path.read_text(encoding="utf-8")) if observations_path.exists() else {}
    contrast_path = root / "evidence" / "contrast-findings.json"
    contrast = json.loads(contrast_path.read_text(encoding="utf-8")) if contrast_path.exists() else {}

    tokens = TokenSet(source, observations)

    tokens_dir = root / "tokens"
    components_dir = root / "components"
    tokens_dir.mkdir(parents=True, exist_ok=True)
    components_dir.mkdir(parents=True, exist_ok=True)

    (tokens_dir / "tokens.json").write_text(json.dumps(emit_dtcg(tokens), indent=2), encoding="utf-8")
    (tokens_dir / "tokens.css").write_text(emit_css(tokens), encoding="utf-8")
    (tokens_dir / "tailwind.theme.js").write_text(emit_tailwind_v3(tokens), encoding="utf-8")
    (tokens_dir / "tailwind.theme.css").write_text(emit_tailwind_v4(tokens), encoding="utf-8")
    (tokens_dir / "preview.html").write_text(emit_preview(tokens, contrast), encoding="utf-8")
    (components_dir / "component-contracts.json").write_text(
        json.dumps(emit_component_contracts(tokens), indent=2), encoding="utf-8"
    )

    dark = tokens.dark_semantic_colors()
    print("Emitted design-system artifacts:")
    print(f"  tokens/tokens.json         DTCG, {len(tokens.semantic_colors)} semantic colours")
    print(f"  tokens/tokens.css          3 layers{', + dark mode' if dark else ', no dark mode detected'}")
    print("  tokens/tailwind.theme.js   Tailwind v3")
    print("  tokens/tailwind.theme.css  Tailwind v4 @theme")
    print("  tokens/preview.html        open this to eyeball the extraction")
    print(f"  components/component-contracts.json  {len(emit_component_contracts(tokens)['components'])} components")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
