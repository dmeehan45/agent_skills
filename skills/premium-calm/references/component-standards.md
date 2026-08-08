# Component standards and state completeness

## Component specifications

| Component | Premium-calm specification |
| --- | --- |
| **Primary button** | One per decision region. Verb and object in the label. Amount included when it commits money. Pressed state appears immediately. Loading retains label width so the control does not jump. |
| **Secondary button** | Border or low-emphasis fill. Must not visually imitate the primary. |
| **Quiet button** | Text or icon treatment for reversible, low-risk actions. Focus ring and target size stay full-size. |
| **Search / primary input** | ~52–56px tall. Persistent label or unambiguous placeholder. Entered values remain inspectable and editable at every later step. |
| **Form field** | Persistent label, never a placeholder as the label. Helper and error occupy stable space so nothing reflows. Input is never erased on failure. |
| **Filter chip** | Text label. Selected state removable in place. Selection carried by more than colour. Horizontal scrolling only where discoverability survives. |
| **List / result card** | One template. Consistent image ratio. Carries the facts needed to compare without opening it. Whole card is the target, with the save or secondary control separately reachable. |
| **Media gallery** | Responsive sources, stable aspect ratio, progressive placeholder, meaningful alt text where the image carries unique information. |
| **Price / cost summary** | Line items, currency, taxes, fees, total, refundability. Sticky but collapsible on constrained screens. |
| **Bottom / primary navigation** | Three to five stable destinations. Labels when icons are ambiguous. Selected state carried by more than colour. |
| **Sheet** | One focused task. Obvious title, dismissal, and safe back behaviour. Keyboard containment on web. Selections preserved on dismiss. |
| **Alert** | Critical, unusual, or destructive decisions only. Never for routine success. |
| **Toast / snackbar** | Non-critical confirmation, at most one undo action. Never covers navigation or the primary action. |
| **Progress indicator** | Appears before the delay reads as failure. Says what is happening. Deterministic where the work is measurable. |
| **Empty state** | Names the absent content, says why it matters, offers one primary next step. |
| **Error state** | Names what failed, what was preserved, whether money or data changed, and how to recover. |
| **Haptic** | Selection, commit, success, and error only. Never continuous, never decorative. |

## State completeness

**A component is not production-ready when only its ideal state has been
designed.** Every component ships with these states designed *and* tested.

| Family | Required states |
| --- | --- |
| **Interaction** | Default, hover (where applicable), focus-visible, pressed, selected, disabled |
| **Data** | Empty, partial, complete, stale, unavailable |
| **Network** | Idle, loading, slow, offline, retrying, timed out |
| **Transaction** | Ready, pending, succeeded, failed, reversed, refunded |
| **Permission** | Unknown, requested, granted, denied, limited |
| **Accessibility** | Large text, increased contrast, reduced motion, reduced transparency, screen-reader focus |
| **Localisation** | Long labels, currency variation, pluralisation, right-to-left where supported |

## The commitment state machine

Any operation that moves money, publishes, deletes, or is otherwise
irreversible needs explicit state semantics — especially when authorisation
leaves the app or completes asynchronously. Ambiguity here is the single most
expensive calm failure, because the user's recovery instinct is to retry, and
retrying an unknown state is how duplicates happen.

| State | Required interface |
| --- | --- |
| **Ready** | Amount or scope, method or target, identifier, and the action |
| **Awaiting authorisation** | Non-destructive progress, the expected next step, safe exit guidance |
| **Pending confirmation** | Reference, what is being held and for how long, refresh or notification behaviour |
| **Succeeded** | Receipt, what happened, where it now lives, support route |
| **Failed before commit** | Explicit "nothing was charged / nothing changed", and retry |
| **Uncertain or timed out** | "We are checking" — and duplicate attempts prohibited until resolved |
| **Reversed / refunded** | Amount, method, expected settlement window, escalation path |

Rules that hold across all of them:

- **Never destroy entered data on a recoverable failure.** Retry resumes with
  the previous state.
- **Distinguish pending from failed.** They demand opposite user behaviour.
- **Make duplicate commitment structurally impossible** while state is unknown,
  rather than asking the user not to.
- **Name the hold.** If inventory, a price, or a slot is reserved, say for how
  long and what happens at expiry.

## The confirmation surface is a durable hub, not an endpoint

After a commitment succeeds, the confirmation becomes the place the user returns
to. It carries the reference, the timing, the contact or support route, the
payment or completion status, the policy that now applies, the receipt, and any
action still required of them. A celebratory screen that discards this
information forces a support contact later.

## Acceptance criteria for any new or changed component

- [ ] Every state in the families above is designed, built, and reachable in review
- [ ] One primary action per decision region; secondary actions are visibly subordinate
- [ ] Contrast validated in every state, not just default, at the token level
- [ ] Target ≥ 44pt Apple / 48dp Android on the minor axis
- [ ] Visible focus, logical order, focus restored after dismissal
- [ ] Selection, error, and status carried by more than colour
- [ ] Text scales without clipping, overlap, or loss of function
- [ ] Motion respects reduced motion; nothing essential is movement-only
- [ ] Input is acknowledged in ~100ms regardless of network
- [ ] Entered data survives a recoverable failure
- [ ] Copy names the object, the state, the consequence, and the safest next action
- [ ] Long labels, currency variation, pluralisation, and RTL do not break layout
