"""Colour maths shared by the premium-calm token scripts.

WCAG 2.x relative luminance and contrast, plus the alpha compositing needed to
answer "what is this text actually sitting on" for translucent surfaces.

Standard library only — these scripts must run in a bare checkout.
"""

from __future__ import annotations

import re

Rgb = tuple[int, int, int]
Rgba = tuple[int, int, int, float]

_HEX = re.compile(r"^#?([0-9a-fA-F]{3,8})$")
_RGB_FN = re.compile(r"rgba?\(([^)]+)\)")


def parse_color(value: str) -> Rgba:
    """Parse #rgb, #rrggbb, #rrggbbaa, rgb(), or rgba() into (r, g, b, a)."""
    if not isinstance(value, str):
        raise ValueError(f"not a colour: {value!r}")
    text = value.strip()

    fn = _RGB_FN.match(text)
    if fn:
        parts = [p for p in re.split(r"[,\s/]+", fn.group(1).strip()) if p]
        nums = [float(p.rstrip("%")) for p in parts[:4]]
        if len(nums) < 3:
            raise ValueError(f"not a colour: {value!r}")
        alpha = nums[3] if len(nums) > 3 else 1.0
        if len(parts) > 3 and parts[3].endswith("%"):
            alpha /= 100.0
        return (int(nums[0]), int(nums[1]), int(nums[2]), alpha)

    m = _HEX.match(text)
    if not m:
        raise ValueError(f"not a colour: {value!r}")
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    elif len(h) == 4:
        h = "".join(c * 2 for c in h)
    if len(h) == 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
    if len(h) == 8:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16) / 255.0)
    raise ValueError(f"not a colour: {value!r}")


def to_hex(rgb) -> str:
    r, g, b = rgb[0], rgb[1], rgb[2]
    return "#{:02X}{:02X}{:02X}".format(
        max(0, min(255, round(r))), max(0, min(255, round(g))), max(0, min(255, round(b)))
    )


def composite(fg: Rgba, bg: Rgba) -> Rgba:
    """Source-over: place fg on bg and return the resulting opaque colour."""
    a = fg[3]
    return (
        round(fg[0] * a + bg[0] * (1 - a)),
        round(fg[1] * a + bg[1] * (1 - a)),
        round(fg[2] * a + bg[2] * (1 - a)),
        1.0,
    )


def _channel(c: float) -> float:
    s = c / 255.0
    return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4


def luminance(rgb) -> float:
    return 0.2126 * _channel(rgb[0]) + 0.7152 * _channel(rgb[1]) + 0.0722 * _channel(rgb[2])


def contrast(fg, bg) -> float:
    """WCAG contrast ratio. Translucent fg is composited onto bg first."""
    if len(fg) > 3 and fg[3] < 1.0:
        fg = composite(fg, bg)
    la, lb = luminance(fg), luminance(bg)
    hi, lo = (la, lb) if la > lb else (lb, la)
    return (hi + 0.05) / (lo + 0.05)


def ratio_str(value: float) -> str:
    return f"{value:.2f}:1"


# WCAG 2.2 minimums, by what the pair is used for.
MINIMUMS = {
    "body": 4.5,        # 1.4.3 normal-size text
    "large": 3.0,       # 1.4.3 large text (>=24px, or >=18.66px bold)
    "non-text": 3.0,    # 1.4.11 UI components and meaningful graphics
    "decorative": 1.0,  # no requirement; recorded so the intent is explicit
}
