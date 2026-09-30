# The nine lenses

Phase 4. Each lens has a question, the checks that answer it, and the tells
that mark a generic or unconsidered implementation. Apply every lens to every
journey; file what you find at the altitude of the fix, not the altitude of
the symptom.

Contents: 1 Interaction states · 2 Premium craft · 3 Motion · 4 Responsive
and mobile · 5 Language · 6 Trust and control · 7 Accessibility · 8 Perceived
performance · 9 Signature opportunities

---

## 1. Interaction states

**Question.** Does every control acknowledge the user's intent immediately and
proportionately, in every state it can be in?

Review by component class, not by screen. A `Button` primitive with a missing
pressed state is missing it on every surface; file it once, as `System drift`,
and list the surfaces where it hurts most.

| State | Must | Common failure |
| --- | --- | --- |
| Hover | Signal interactivity without shouting; consistent across the class | Missing on links styled as text; a colour jump with no transition |
| Focus | Visible, high-contrast, on every interactive element, without a mouse | Reset by a CSS reset; drawn only on `:focus` so mouse clicks show it too |
| Pressed | Instant (under 100ms) physical acknowledgement | Absent; the user taps twice |
| Selected | Distinguishable without colour alone | Colour-only tint; identical to hover |
| Disabled | Explains, or is not shown | Greyed control with no reason; disabled primary action on a form with no indication of what is missing |
| Loading | Acknowledges within 100ms, preserves layout, prevents duplicate submission | Spinner replaces the whole surface; button changes width; double submit possible |
| Saved | Confirms proportionately, near the thing that was saved | A toast for every keystroke; no confirmation at all |
| Completed | Names what happened and offers the next thing | Generic "Success!"; dead end |
| Destructive | Names the consequence; is reversible or requires deliberate confirmation | Confirmation for the reversible; none for the irreversible |
| Error | States what happened, what it means, and how to recover; keeps the user's work | Red text with a code; the form clears |
| Empty | Offers the first action; shows what the surface will look like with content | Illustration and a sentence |
| Partial | Shows what has loaded and what is still coming | Blank until everything arrives |
| Asynchronous | Says what is happening in the background, and where the result will appear | Silence, then a surprise |
| Optimistic | Updates immediately, reconciles quietly, reverses honestly | Waits for the server when it could act; or lies and never reconciles |
| Interrupted | Preserves draft, scroll, step, and selection across background, tab switch, network loss, rotation | Returns to the start |

**Look for.** Unnecessary toasts; modals used where inline would preserve
context; sudden layout changes on state transitions; ambiguous click targets
(is this row clickable?); hidden state changes (something changed and nothing
moved); controls without visible affordances; the same interaction implemented
two ways; excessive confirmation; insufficient confirmation for the
destructive; interactions that make the implementation model visible ("Sync
now", "Refresh", "Reload to see changes").

**Prefer.** Direct manipulation and continuity. The interface should feel
responsive to the user's intent rather than like a sequence of commands sent
to software.

---

## 2. Premium craft

**Question.** Does the experience feel intentional, or assembled?

Premium does not mean luxurious styling, gradients, excessive animation,
glassmorphism, or decorative complexity. Premium means intentionality:
restraint, confidence, excellent typography, disciplined spacing, strong
hierarchy, careful alignment, coherent geometry, consistent interaction
patterns, considered density, sophisticated use of whitespace, appropriate
visual rhythm, high-quality assets, graceful transitions, precision in
micro-interactions, absence of unnecessary UI, excellent defaults, thoughtful
empty states, excellent edge-state behaviour.

**The generic tells.** Name the tell in the finding, never the vibe.

| Tell | Reads as | Ask instead |
| --- | --- | --- |
| Everything in a card | Dashboard, template | Would spacing and a heading group this as well? |
| Borders on everything | Framework default | Which of these boundaries does the eye need? |
| Pills and badges for ordinary metadata | Component library | Is this a status, or just a word in a box? |
| An icon beside every label | Assembled | Does the icon add meaning the word lacks? |
| Helper text under every field | Unconfident | Would a better label or a better default remove the need? |
| Shadows and elevation on static content | Decorative | What is this raised above, and why? |
| Nested containers (card in panel in card) | Structure exposed | Which level is the real grouping? |
| A section heading above every block | Layout insufficient | Would the content's own shape carry it? |
| The same accent on nav, links, chips, buttons, and banners | Nothing is emphasised | Where is the one moment the accent should mean something? |
| Uniform 16px padding everywhere | Framework spacing | Where should density change to express hierarchy? |
| Stock illustration in empty states | Placeholder | What would show the user what this surface becomes? |
| Gradient hero, glass panels, glow | Trend | What job does this do for the user? |

**Ask whether hierarchy could be communicated through composition, spacing,
typography, sequence, and interaction instead.** A premium product often
contains less visible interface because the underlying decisions were made
more carefully.

**Check.** The walker's `containers` reading per surface: bordered, shadowed,
pills, icons, headings, nesting depth. Numbers are not findings, but a surface
with forty bordered elements and nesting three deep is where to look. Then
read the type scale (how many sizes and weights are in use; is there a body
size and a clear scale above it), the spacing (is there a scale, and is it
used), alignment (do edges line up across regions), and assets (are images
consistent in crop, ratio, and quality).

---

## 3. Motion

**Question.** Does motion explain, or decorate?

Motion earns its place by answering one of these:

| Motion explains | Example |
| --- | --- |
| Where something came from | A detail view grows from the row that was tapped |
| Where something went | A saved item slides toward the tab that holds it |
| What changed | The one edited value re-flows; the rest holds still |
| What is connected | A filter and the list it filters move together |
| What is waiting | A determinate progress that matches the real work |
| What completed | A brief, proportionate settle, not a celebration |
| What deserves attention | One thing moves; nothing else does |

**Review.** Transitions between product states; expansion and collapse; object
continuity; reordering; loading; completion; navigation; overlays; gesture
responses.

**Flag.** Motion that adds latency (a 400ms transition on a 40ms operation);
spectacle; distraction; visual fatigue (everything moves on every screen);
motion that ignores `prefers-reduced-motion`; motion that resets rather than
continues (a fade-out fade-in where a shared element would preserve identity).

**Check.** The walker's `movesUnderReducedMotion`, `longTransitions`, and
`infiniteAnimations`. Then watch the transitions by hand at the phone size.

**Do not recommend animation to make the product feel polished.** Identify a
small number of opportunities for *signature* motion, where continuity or
acknowledgement would materially improve the character of the product, and
put them in lens 9.

---

## 4. Responsive and mobile

**Question.** Is mobile designed, or merely not broken?

Do not treat mobile as a compressed desktop. Walk the product at phone,
tablet, laptop, and large desktop, and review the phone as its own product.

| Reconsider on the phone | The premium answer |
| --- | --- |
| Information priority | The first viewport holds the job, not the header, the hero, and the nav |
| Thumb reach | The primary action and the navigation live in the bottom half; destructive actions do not |
| Navigation model | A model designed for one hand, not a hamburger hiding the desktop nav |
| Input behaviour | The right keyboard for each field; autofill honoured; no zoom on focus (16px inputs) |
| Keyboard interaction | The keyboard does not cover the field being edited or the action that submits it |
| Viewport changes | Rotation and keyboard appearance preserve scroll and focus |
| Fixed elements | Together they cover a small share of the viewport; nothing important hides under them |
| Scrolling | One axis; no nested scroll traps; no horizontal overflow |
| Gestures | Every gesture has a visible alternative; system gestures are not hijacked |
| Content density | Designed for the phone, not desktop density squeezed |
| Progressive disclosure | More is available, but the first screen is complete |
| Interruption and resumption | Backgrounding, a call, a notification: state survives |

**Check.** `horizontalOverflow`, `targetsUnder44`, `fixedCoveragePct`,
`primaryAboveFold` on the phone captures. Then look at the tablet captures:
a two-column desktop layout stretched to a single column with desktop-sized
type and full-width buttons is the signature of responsive CSS that prevents
breakage without producing a designed experience.

---

## 5. Language

**Question.** Does the copy reduce uncertainty, or fill space?

Read every important piece of interface copy in the journeys: headings, action
labels, empty states, errors, confirmations, helper text, notifications, and
the paywall.

| Ask | Tell |
| --- | --- |
| Does it tell users things they already know? | "Welcome to your dashboard"; "Here you can see your items" |
| Does it over-explain obvious actions? | A sentence above a single button |
| Does it use internal terminology? | "Sync", "entity", "workspace" where the user says "my stuff" |
| Does it rely on headings because layout is insufficient? | A heading on every block, so the eye has to read to find anything |
| Does it sound robotic or generic? | "An error occurred"; "Success!"; "Are you sure?" |
| Does it present uncertainty clearly? | Estimates shown as facts; "about" missing where it belongs |
| Does it set accurate expectations? | "Takes 2 minutes" on a ten-step flow |
| Does it help users understand consequences before important actions? | "Delete" with no mention of what is lost or whether it can be recovered |

**Prefer** concise copy supported by good interface design. Do not solve a
confusing screen by adding an instructional paragraph unless explanation is
intrinsically necessary: cost, irreversibility, privacy, and consequences are
worth a sentence; where to click is not.

**Check.** The walker's `copy` reading lists headings, labels, helper text,
placeholders, and vague action labels per surface.

---

## 6. Trust and control

**Question.** At every point the user must trust the system, does the product
earn it?

This lens is decisive for AI-powered experiences and anything that acts on the
user's behalf. Identify every place the user must trust the system, then check:

| Check | Premium |
| --- | --- |
| What the system is doing | Visible while it happens, in the user's vocabulary |
| Why it is doing it | Available on demand, not forced |
| Whether actions are reversible | Undo where possible; where not, the consequence is stated before, not after |
| Generated or inferred versus user-authored | Distinguishable at a glance, and editable |
| Persistence | The user knows what is saved, where, and whether it will be there tomorrow |
| Privacy-sensitive behaviour | Clear before it happens: what is shared, with whom, what is stored |
| Uncertainty | Represented honestly: confidence, ranges, "we think" |
| Autonomy | The system never acts without sufficient visibility; the user can see what it did and stop it |

The product should communicate enough system state to create confidence
without exposing implementation details. "Syncing 3 of 12 records" exposes the
implementation; "Your changes will be on your phone in a moment" communicates
state.

---

## 7. Accessibility

**Question.** Is the product usable by everyone who reaches it, as a property of
interaction quality rather than a compliance appendix?

| Check | Look at |
| --- | --- |
| Semantic structure | One `h1`; no skipped levels; `main` and `nav` landmarks; lists as lists; buttons as buttons |
| Keyboard navigation | Every job completable without a pointer; logical tab order; no traps |
| Focus management | Focus moves to what opened, and returns to what opened it; focus is never lost on route change |
| Target sizes | 44px minimum on touch; spacing between adjacent targets |
| Contrast | Text and controls in every state, including placeholder, disabled, and on imagery |
| Readable typography | Body size at least 16px on the phone; line length under about 80 characters; line height for the size |
| Zoom | 200% text zoom keeps the job completable; no clipping, no horizontal scroll |
| Screen-reader implications | Names on icons and controls; live regions for state changes; hidden decorative content |
| Reduced motion | Respected; essential motion reduced, not just removed |
| Form labelling | Visible labels, associated; placeholder is not the label |
| Error identification | Errors named, associated with the field, announced |

**Check.** `controlsWithoutFocusStyle`, `targetsUnder44`, `unlabelledFields`,
`imagesMissingAlt`, `headingOrderSkips`, `landmarks`, `movesUnderReducedMotion`.
For contrast numbers through composited backgrounds, run `premium-calm`'s
measurement on the same URLs.

A job that cannot be completed by keyboard or on the phone is Foundational,
whatever else is true of the product.

---

## 8. Perceived performance

**Question.** Does the product preserve the user's momentum?

Evaluate both actual and perceived responsiveness.

| Look for | Premium |
| --- | --- |
| Blocking operations | Nothing blocks the interface that could run beside it |
| Layout shift | Content arrives into reserved space; nothing jumps after paint |
| Slow interaction acknowledgement | Every tap acknowledged within 100ms, before the work is done |
| Blank waiting states | The shape of the coming content is shown; something is readable |
| Unnecessary spinners | A spinner for under 300ms is worse than nothing; for a known duration, progress |
| Missing skeleton states | Skeletons match the layout they precede |
| Transitions that make fast operations feel slow | Transition duration under the operation's duration; none on instant operations |
| Operations that could be optimistic | Local, reversible actions update immediately |
| Prefetching and progressive rendering | The likely next screen is ready; the first paint is useful |

**Check.** `ackMs` per action, `cls` per capture, `waitingIndicators` at
capture, and the step timings in each `journey.json`. Lab numbers from a
single run catch regressions and reserved-dimension bugs; the gate is field
p75 (LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1). Say which you have.

---

## 9. Signature opportunities

**Question.** After the weaknesses are corrected, where could this product
become distinctly memorable?

> *What could this product do extraordinarily well that competitors would
> normally treat as ordinary?*

Find the moments where interaction, motion, personalisation, sequencing,
content, or visual treatment could become characteristic of the product. The
best candidates are usually:

- the moment of first value (what the user sees before doing any work);
- the completion of the primary loop (how success feels);
- the transition that the user makes most often (object continuity here
  defines the product's physicality);
- the one input the product is built around (how it feels to give the product
  what it needs);
- recovery (how the product behaves when the user or the system gets it wrong).

**Do not manufacture novelty.** A signature interaction improves the job *and*
expresses the character of the product. Aim for a few exceptional moments, not
decorative uniqueness everywhere. Tie each opportunity to a finding or a
primitive it depends on, and file them as `Exceptional craft`.
