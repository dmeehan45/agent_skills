#!/usr/bin/env python3
"""check_contrast.py — prove a proposed palette before recommending it.

A premium-calm proposal that ships a colour it never checked is exactly the
failure the design language warns about: accessibility repaired screen by screen
instead of encoded into the tokens. This validates every declared pair, in every
mode, and exits non-zero if any of them misses.

Usage:
  python3 check_contrast.py token-spec.json
  python3 check_contrast.py token-spec.json --json
  python3 check_contrast.py --pair "#171814 on #F6F4EF" --pair "#FFF on #C6FF1A"
  python3 check_contrast.py token-spec.json --mode dark --quiet
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.color import MINIMUMS, contrast, parse_color, ratio_str  # noqa: E402


def resolve(token: str, palette: dict) -> str:
    """A pair side is either a token name in the palette or a literal colour."""
    if token in palette:
        return palette[token]
    return token


def check_spec(spec: dict, only_mode: str | None = None) -> list[dict]:
    modes = spec.get("color", {})
    pairs = spec.get("pairs", [])
    results: list[dict] = []

    for mode_name, palette in modes.items():
        if only_mode and mode_name != only_mode:
            continue
        for pair in pairs:
            fg_token, bg_token = pair["fg"], pair["bg"]
            use = pair.get("use", "body")
            minimum = pair.get("min", MINIMUMS.get(use, 4.5))

            fg_raw, bg_raw = resolve(fg_token, palette), resolve(bg_token, palette)
            unknown = [
                name
                for name, raw in ((fg_token, fg_raw), (bg_token, bg_raw))
                if name not in palette and not _looks_like_color(raw)
            ]
            if unknown:
                results.append({
                    "mode": mode_name, "fg": fg_token, "bg": bg_token, "use": use,
                    "role": pair.get("role", ""), "ratio": None, "min": minimum,
                    "pass": False,
                    "error": f"not in the {mode_name} palette: {', '.join(unknown)}",
                })
                continue

            try:
                ratio = contrast(parse_color(fg_raw), parse_color(bg_raw))
            except ValueError as exc:
                results.append({
                    "mode": mode_name, "fg": fg_token, "bg": bg_token, "use": use,
                    "role": pair.get("role", ""), "ratio": None, "min": minimum,
                    "pass": False, "error": str(exc),
                })
                continue

            results.append({
                "mode": mode_name,
                "fg": fg_token, "fgValue": fg_raw,
                "bg": bg_token, "bgValue": bg_raw,
                "use": use, "role": pair.get("role", ""),
                "ratio": round(ratio, 2), "min": minimum,
                "pass": ratio >= minimum, "error": None,
            })
    return results


def _looks_like_color(value: str) -> bool:
    return bool(re.match(r"^#|^rgba?\(", str(value).strip()))


def check_adhoc(pairs: list[str]) -> list[dict]:
    results = []
    for raw in pairs:
        parts = re.split(r"\s+on\s+|\s*/\s*|\s*,\s*", raw.strip(), maxsplit=1)
        if len(parts) != 2:
            results.append({"mode": "adhoc", "fg": raw, "bg": "", "ratio": None,
                            "min": 4.5, "pass": False, "use": "body", "role": "",
                            "error": 'expected "<fg> on <bg>"'})
            continue
        fg, bg = parts
        try:
            ratio = contrast(parse_color(fg), parse_color(bg))
        except ValueError as exc:
            results.append({"mode": "adhoc", "fg": fg, "bg": bg, "ratio": None, "min": 4.5,
                            "pass": False, "use": "body", "role": "", "error": str(exc)})
            continue
        results.append({"mode": "adhoc", "fg": fg, "fgValue": fg, "bg": bg, "bgValue": bg,
                        "use": "body", "role": "", "ratio": round(ratio, 2), "min": 4.5,
                        "pass": ratio >= 4.5, "error": None})
    return results


def render_table(results: list[dict], quiet: bool) -> str:
    lines: list[str] = []
    by_mode: dict[str, list[dict]] = {}
    for r in results:
        by_mode.setdefault(r["mode"], []).append(r)

    for mode, rows in by_mode.items():
        failures = [r for r in rows if not r["pass"]]
        if quiet and not failures:
            lines.append(f"{mode}: {len(rows)} pairs, all pass")
            continue
        lines.append(f"\n{mode}  ({len(rows) - len(failures)}/{len(rows)} pass)")
        lines.append(f"  {'':2} {'ratio':>9}  {'min':>5}  pair")
        for r in rows:
            if quiet and r["pass"]:
                continue
            mark = "ok" if r["pass"] else "!!"
            ratio = ratio_str(r["ratio"]) if r["ratio"] is not None else (r.get("error") or "error")
            pair = f"{r['fg']} on {r['bg']}"
            role = f"   — {r['role']}" if r.get("role") else ""
            lines.append(f"  {mark} {ratio:>9}  {r['min']:>5}  {pair}{role}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate premium-calm token contrast.")
    ap.add_argument("spec", nargs="?", help="token spec JSON")
    ap.add_argument("--pair", action="append", default=[], help='ad-hoc check, e.g. "#171814 on #F6F4EF"')
    ap.add_argument("--mode", help="check only this colour mode (light, dark, ...)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--quiet", action="store_true", help="show failures only")
    args = ap.parse_args()

    results: list[dict] = []
    if args.pair:
        results += check_adhoc(args.pair)
    if args.spec:
        spec = json.loads(Path(args.spec).read_text())
        results += check_spec(spec, args.mode)
    if not results:
        ap.error("pass a token spec, --pair, or both")

    failures = [r for r in results if not r["pass"]]

    if args.json:
        print(json.dumps({
            "checked": len(results),
            "passed": len(results) - len(failures),
            "failed": len(failures),
            "results": results,
        }, indent=2))
    else:
        print(render_table(results, args.quiet))
        print(f"\n{len(results) - len(failures)}/{len(results)} pairs pass.")
        if failures:
            print("\nEvery failing pair is a token-level defect. Fix the token, not the screen —")
            print("a palette that needs per-screen repair is not a design system.")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
