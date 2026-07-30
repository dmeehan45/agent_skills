# Component Contract Schema

`components/component-contracts.json` is the machine-readable half of the
component library. `emit_tokens.py` writes it from measured interaction data;
the synthesis prompts may add narrative fields but must not overwrite measured
ones.

The load-bearing rule: **every state carries a `source`** that says whether it
was observed on the live site or designed by the pipeline. A contract that
cannot distinguish the two is a contract you cannot trust, and
`validate_output_package.py` fails the package if any state is untagged.

## Top level

```jsonc
{
  "schema": "psdsm/component-contracts@1",
  "fidelity_mode": "modernized",
  "note": "...",
  "components": [ /* Component */ ]
}
```

## Component

```jsonc
{
  "name": "button.primary",              // <family>.<variant>
  "evidence": {
    "signatures": ["button||btn.btn-primary"],  // capture-time selector signatures
    "pages": ["p_00_home", "p_01_pricing"],     // page_ids it was measured on
    "instances": 24                              // total occurrences observed
  },

  // Computed style of the resting element, measured — not reconstructed.
  "base": {
    "color": "rgb(255, 255, 255)",
    "background_color": "rgb(11, 95, 255)",
    "border_color": "rgba(0, 0, 0, 0)",
    "border_width": "1px",
    "border_radius": "10px",
    "box_shadow": null,
    "outline": null,
    "outline_offset": "0px",
    "opacity": "1",
    "transform": null,
    "text_decoration": "none",
    "cursor": "pointer",
    "transition": "background-color 0.18s cubic-bezier(0.4, 0, 0.2, 1)",
    "padding": "12px 24px 12px 24px",
    "min_height": "auto",
    "height": "46px",
    "width": "168px",
    "font_size": "16px",
    "font_weight": "600"
  },

  // Only properties that CHANGED from base. Absent state = never observed.
  "states": {
    "hover": {
      "source": "measured",
      "changes": {
        "background_color": { "from": "rgb(11, 95, 255)", "to": "rgb(8, 70, 196)" },
        "box_shadow":       { "from": null, "to": "rgba(11, 95, 255, 0.28) 0px 4px 12px 0px" }
      }
    },
    "focus_visible": {
      "source": "measured",
      "changes": {
        "outline": { "from": null, "to": "3px solid rgb(122, 167, 255)" },
        "outline_offset": { "from": "0px", "to": "2px" }
      }
    },
    "active":   { "source": "measured", "changes": { /* ... */ } },
    "disabled": { "source": "measured", "samples": [ { "opacity": "0.45", "cursor": "not-allowed" } ] },
    "loading":  { "source": "recommended", "rationale": "no loading state exists on the source site" }
  },

  // States that were probed but produced no delta, or could not be probed.
  // These are design work, not extractions. Never present them as findings.
  "unmeasured_states": ["loading", "error"],

  "accessibility": {
    "has_visible_focus_indicator": true,
    "measured_height_px": 46.0,
    "meets_44px_touch_target": true
  }
}
```

## `source` values

| Value | Meaning |
| --- | --- |
| `measured` | Observed by scripted interaction or read declaratively from the live DOM. Trustworthy as extraction. |
| `recommended` | Designed by the pipeline because the source has no such state. Must be labelled as a recommendation everywhere it surfaces. |

## Naming

`<family>.<variant>`, families being `button`, `link`, `field`, `card`, `badge`,
`alert`, `nav`, `table`, `modal`. `emit_tokens.py` derives these from the tag
and class signature — `button` + a class containing `secondary`, `ghost`, or
`outline` becomes `button.secondary`, everything else `button.primary`. Rename
in the narrative spec if the site's own vocabulary differs, but keep the
`evidence` block attached so provenance survives.

## Reading the `states` diffs

Three things routinely surprise people:

- **`active` includes hover changes.** Pressing an element requires hovering it,
  so the active delta contains both. Diff active against hover, not base, when
  you want the press-only change.
- **`focus` vs `focus_visible`.** Both are captured. `focus` is programmatic;
  `focus_visible` is reached via Tab and is what a keyboard user actually sees.
  Build focus rings from `focus_visible`.
- **A UA default is a real measurement.** `outline: 1px auto` means the site
  never styled its focus ring. That is a genuine finding and an accessibility
  improvement opportunity — not missing data.

## Extending in the narrative spec

The synthesis prompts should add `purpose`, `anatomy`, `variants`, `content`,
and `implementation` alongside the measured fields, and mirror the result into
`components/component-library-spec.md`. Do not delete or rewrite `base`,
`states[].changes`, `evidence`, or `unmeasured_states` — downstream validation
and the fidelity check read them.
