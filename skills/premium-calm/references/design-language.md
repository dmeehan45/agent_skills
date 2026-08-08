# The premium-calm design language

The rules below are the target state. Calibration (see `calibration.md`) decides
how each one expresses for this product; none of them changes.

## 0. The salience budget

Emphasis is a finite resource. Spend it in tiers, and keep the top tier scarce.

| Tier | Contents | Budget per viewport |
| --- | --- | --- |
| **Primary** | Current task, key value, primary action | One dominant cluster |
| **Secondary** | Supporting choices, filters, navigation, relevant metadata | Two to four groups |
| **Tertiary** | Explanations, labels, supplemental facts, legal detail | As needed — quiet but readable |
| **Latent** | Advanced options, infrequent controls | Progressively disclosed |

**The squint test.** Blur or defocus the screen. The surviving masses should
reveal the intended reading order. If five bright regions survive equally, the
interface is not calm. If nothing survives, it has no hierarchy.
`measure_surface.mjs` renders this automatically (`*.squint.png`) and counts
competing regions.

**The grayscale and accentless tests.** If the reading order disappears without
hue, or if nothing still reads as "selected" or "primary" once the accent is
neutralised, then meaning is carried by colour alone — a WCAG failure and a calm
failure at once. Both renders are produced automatically.

## 1. Typography — expose structure, don't add personality everywhere

| Rule | Target |
| --- | --- |
| Families | One primary sans. An editorial face only for marketing, if at all. |
| Semantic styles | Six to eight, named by role, not by size |
| Body size | 16–18px on web; honour platform text scaling everywhere |
| Line height | ~1.45–1.6 for body |
| Measure | ≤ ~80 characters per line for continuous reading |
| Text spacing | Layout survives increased line, paragraph, letter, and word spacing without clipping or loss of function |

Never reduce price, policy, error, or state information to caption size. Caption
is for supplemental metadata only.

Common failures: too many weights, condensed metadata, extra-light body text,
uppercase runs, one-off sizes where a token exists.

## 2. Colour — scarce and semantic

Neutral surfaces dominate. Saturated colour earns its place.

| The accent is appropriate for | The accent is wrong for |
| --- | --- |
| Primary commitment (the action that spends money, sends, deletes, publishes) | Long paragraphs or ordinary metadata |
| The current selected state | Every navigational icon |
| Keyboard focus, where contrast allows | Large decorative fills behind imagery |
| Availability or positive status, where meaning is *also* carried another way | Multiple competing calls to action |
| Rare brand signature moments | Disabled states |

**Status colours keep distinct meanings.** Success, warning, danger, info, and
pending must not drift into decoration or into each other.

**A bright accent is often unusable as a thin indicator on a light ground.** A
vivid chroma-heavy accent can measure near 1:1 against a warm light canvas. It
can still be a *fill* carrying dark ink at high contrast, but it cannot be a
1px selected-state border, an icon, or small text. When the palette needs an
outline in that role, add a darkened `accent-edge` token and check it at 3:1.
Verify with `check_contrast.py` rather than assuming — this failure is invisible
by eye on a bright display and obvious on a dim one.

**Encode accessibility into the tokens, not the screens.** A palette repaired
screen by screen is not a design system. Every pair the product relies on is
declared in the token spec and validated before the palette is proposed.

## 3. Spacing — rhythm from a small scale

Base 4 or 8; prefer `8, 12, 16, 24, 32, 48, 64, 96`.

| Relationship | Gap |
| --- | --- |
| Within a component | Compact (8) |
| Standard component inset | 16 |
| Spacious card inset | 24 |
| Between sections | 32–48 |
| Between page regions | 64–96 |

**Larger gaps between concepts than within a component.** Arbitrary values, and
containers added to compensate for weak grouping, are the two failures.

## 4. Hierarchy — one clear task per decision region

- One primary action per viewport or modal. Secondary actions must not imitate
  primary styling.
- At most three obvious emphasis tiers on a screen.
- A promotional or decorative element must never outrank the task.
- Radius decreases inward: an inner element never carries a larger radius than
  its parent.

## 5. Materials — depth explains layers

Two or three surface levels, no more. Reach for a subtle border before a shadow,
and a shadow before a blur.

| Level | Use |
| --- | --- |
| Low | Menus, floating controls |
| Medium | Sheets, sticky transactional summaries |
| High | Critical modal interruption only |

Blur and translucency are for temporary overlays, and only where readability
holds. Honour reduced-transparency by swapping to opaque semantic surfaces.
Card-inside-card-inside-sheet is the canonical failure; so is glass over
detailed imagery.

## 6. Motion — explain cause, destination, and state

| Token | Duration | Use |
| --- | --- | --- |
| `motion-instant` | 80–120ms | Press, hover, focus, selected-state acknowledgement |
| `motion-direct` | 120–180ms | Toggle, chip, icon, small disclosure |
| `motion-standard` | 180–260ms | Menu, toast, card-state transition |
| `motion-spatial` | 260–420ms | Sheet, route relationship, media expansion |
| `motion-ambient` | 600ms+ | Rare, non-blocking background atmosphere only |

Four qualities separate calm motion from anxious motion:

| Quality | Calm | Anxious |
| --- | --- | --- |
| Immediacy | Press, selection, and focus appear at once | Button looks dead until the network returns |
| Continuity | The selected object leads to a recognisably related view | The screen resets abruptly |
| Restraint | One coordinated transition | Unrelated fades, springs, and parallax at once |
| Closure | Success, failure, and reversibility are explicit | A spinner vanishes with no interpretable outcome |

**Reduced motion is a mode, not a fallback.** Under `prefers-reduced-motion`,
spatial and decorative movement collapses to an immediate state change, and
nothing essential is communicated by movement alone. Anything still animating
under that preference is a defect; `measure_surface.mjs` counts them.

Haptics follow the same discipline: selection, commit, success, and error only.
Never continuous, never decorative.

## 7. Imagery — images must improve the decision

Fewer and larger beats many and small. Consistent aspect ratios, truthful crops,
reserved dimensions so nothing shifts as they load, responsive sources, and
progressive placeholders whose geometry matches the final content. Meaningful
alternative text where the image carries unique information; decorative images
excluded from the accessibility tree.

Failures: repeated thumbnails, generic lifestyle stock, aggressive overlays,
inconsistent crops, skeletons that do not match what arrives.

## 8. Microcopy — replace uncertainty with concrete language

The grammar: **name the object, describe the state, explain the consequence,
offer the safest next action.** Sentence case, explicit verbs.

| Situation | Avoid | Prefer |
| --- | --- | --- |
| Primary action | "Continue" | "Review booking" |
| Final commitment | "Submit" | "Pay GHS 1,240" |
| Saved state | "Done" | "Saved to Weekend stays" |
| Unavailable | "Not available" | "This room is unavailable for 14–16 August. Try nearby dates." |
| Pending | "Processing…" | "Your mobile-money authorisation is pending. Keep this screen open; you will not be charged twice." |
| Recoverable error | "Something went wrong" | "We could not confirm the payment. Your dates are still held for 8 minutes. Try again." |
| Policy | "View details" | "Free cancellation until 18:00 on 12 August" |
| Empty state | "No items" | "Save stays to compare them here" |
| Destructive action | "Yes" | "Cancel booking" |
| Support | "Contact us" | "Message Avani support" |

Translate the pattern, not the examples: for a deployment tool, "Submit" becomes
"Deploy to production"; "Something went wrong" becomes "The migration stopped at
step 3 of 7. Steps 1–2 are committed. Nothing was dropped. Resume or roll back."

## 9. Accessibility — accommodations are first-class modes

| Requirement | Expectation |
| --- | --- |
| Structure | Native headings, landmarks, lists, buttons, fields, labels |
| Contrast | WCAG 2.2 AA validated for *every* state, not just default |
| Focus | Visible ring, predictable order, focus restored after dismissal |
| Targets | ≥ 44pt Apple, ≥ 48dp Android — floors, not aspirations |
| Text scaling | No clipping, overlap, or hidden function at large text |
| Non-colour cues | Selection, error, availability, and status also carried by text, shape, icon, or pattern |
| Reduced motion | Spatial and decorative effects replaced |
| Reduced transparency | Blur replaced with opaque semantic surfaces |
| Announcements | Loading completion, form errors, save state, transaction state, confirmation |
| Touch alternatives | Nothing essential is hover-only, swipe-only, drag-only, or precision-gesture-only |
| Time limits | Holds and expiry explained; extension offered; data never silently destroyed |

## 10. Interaction patterns that read as quality

| Pattern | Behaviour |
| --- | --- |
| Progressive task entry | Ask for the minimum now; reveal complexity once intent is established |
| Optimistic, reversible save | Reflect the state immediately, offer undo |
| State-preserving navigation | Returning restores scroll, filters, selections, and entered data |
| Contextual transition | Source object and destination feel connected; no full-screen reset |
| Inline validation | Validate after meaningful interaction; put the correction beside the field |
| Stable loading skeleton | Placeholder geometry matches the final content |
| Persistent transaction summary | Total, terms, and material policy stay available during commitment |
| Quiet confirmation | Confirm clearly without hijacking the next task — reference, details, support, and a link onward, not confetti |
| Smart default with visibility | Reduce effort while making the assumption inspectable and editable |
| Graceful network recovery | Preserve input; say whether retry is safe; distinguish pending from failed |
| Focused sheet or modal | One contained decision, obvious dismissal, background state preserved |

## 11. Performance is a premium material

An interface that stutters contradicts the promise no palette can rescue.

| Concern | Guidance |
| --- | --- |
| Hero media | Preload only the likely LCP image; responsive AVIF/WebP at fixed dimensions |
| List images | Lazy-load below the fold; stable aspect-ratio boxes; correctly sized sources |
| Fonts | Subset; preload only critical files; `font-display`; tune fallback metrics to avoid shift |
| JavaScript | Route- and component-level splitting; never load admin or host tooling in a consumer path |
| Input | Acknowledge locally and immediately; debounce the network, never the keystroke |
| Filters | Update selected state locally; cancel superseded requests |
| Skeletons | Match final layout rather than a generic shimmer |
| Animation | Prefer `transform` and `opacity`; avoid layout-triggering properties |
| Third parties | Defer non-essential scripts; never let a tag block a commitment interaction |
| Offline / poor network | Cache what the user already committed to, preserve drafts, expose retry, distinguish stale from unavailable |

Targets are field p75: LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1. Lab numbers from
`measure_surface.mjs` are a single run — useful for catching regressions and
layout shift, not a substitute for field data.

## 12. Cross-platform: share meaning, adapt expression

| Shared across platforms | Adapted per platform |
| --- | --- |
| Meaning of primary, secondary, destructive, success, pending, unavailable | Navigation placement and back behaviour |
| Information architecture of the core objects | Native picker, sheet, menu, keyboard conventions |
| Search, commitment, payment, and cancellation state machines | Haptic vocabulary |
| Typography roles and hierarchy | Exact font rendering and point sizes |
| Colour roles and contrast requirements | System appearance and material implementation |
| Motion intent and duration ranges | Platform transition curves and gestures |
| Microcopy terminology | Concision required by viewport and native pattern |
| Analytics event names | Platform-specific diagnostic detail |

Cross-platform consistency preserves meaning, terminology, hierarchy, and state.
It does not force identical pixels.
