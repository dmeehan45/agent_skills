# Walking the journeys

Phase 2. The running product is the primary artifact, and a journey is the
unit of review: not a screen, but a person with an intent moving through
screens, states, and time. This document lists the journeys every review
walks, the friction to look for, the plan the walker reads, and what to do
when the browser cannot run.

## The minimum journeys

Walk every one of these that the product can support. Add the product's own
(the loop, the commitment, the share, the export). A review that walked only
first arrival reviewed the easiest ten minutes of the product.

| Journey | Start | What you are looking for |
| --- | --- | --- |
| **First arrival** | Launch, cold, no account | Is what-this-is and what-to-do-next understood in the first minute, without instructional text? |
| **First meaningful action** | The first thing the user does that is not setup | Does the product respond with something the user would keep? |
| **First successful outcome** | The first time the job is done | Is success proportionate, specific, and followed by the obvious next thing? |
| **Repeat use** | Second session, same day or next | Does the product remember; is the loop the first thing on screen? |
| **Returning after time away** | Two weeks later, or after a notification | Is the user re-oriented, or punished, or shown a stale state? |
| **Changing or undoing** | Edit a thing; reverse a thing | Is editing in place; is undo total; does the product say what changed? |
| **Missing information** | The system does not have what it needs | Does it ask for exactly that, at that moment, or send the user to Settings? |
| **Error** | A failed request, a rejected input, a conflict | Is the error stated as a consequence with a recovery, and is the user's work intact? |
| **Empty state** | No data yet, or all data gone | Does the empty state offer the next action, or only explain the emptiness? |
| **Interruption and resumption** | Background the app mid-task; switch tabs; lose the network; rotate | Is the draft, scroll, selection, and step preserved? |
| **Mobile** | Every journey above, on the phone | Is this a designed phone product, or a desktop that reflows? |

For each journey record: reached (yes, partial, no), the sizes walked, the
evidence path, and a one-line verdict. That table is section 2 of the review.

## The friction taxonomy

Log friction as you walk, using these names so findings are comparable across
journeys and reviews. Each row is a *symptom*; the root cause comes in phase 5.

| Friction | You see it when | Usually caused by |
| --- | --- | --- |
| Number of decisions | The user must choose between options at a step where one answer is right for almost everyone | Missing default; configuration modelled as a choice |
| Number of actions | The same intent takes more taps than the information requires | Confirmation steps; navigation between what should be one surface |
| Cognitive load | The user must hold information from one screen to use on another | Lost context; data the system has but does not show |
| Unnecessary navigation | The user leaves the surface to do something that belongs on it | Feature-per-screen architecture |
| Loss of context | Scroll, selection, filter, draft, or step resets on transition | Route-level state; modals over the working surface |
| Duplicated information | The same fact appears twice at once, or the user re-enters what they already gave | Screens built independently; no shared state |
| Premature configuration | Setup before value | Data model that requires preferences before rendering |
| Avoidable confirmation | "Are you sure?" on a reversible action | Undo not implemented, so confirmation stands in for it |
| Unclear state | The user cannot tell whether the last action worked, or what the system is doing | Missing loading, saved, or partial states |
| Waiting | Blank or spinner with nothing to read or do | Blocking fetch; no skeleton; no optimistic update |
| Unexpected behaviour | The interface does something the user did not ask for | Autonomy without visibility; side effects on navigation |
| Dead end | A screen with no valid next action | Success and error states without a next step |
| Unnecessary mode switching | Editing, viewing, and selecting are separate modes | Toolbar-driven design where direct manipulation would do |
| Remembering what the system knows | The user is asked for something already entered or inferable | No shared profile; forms that do not read state |

**Do not equate fewer clicks with better UX.** A three-tap flow with no
decisions beats a one-tap flow that requires the user to already know what
will happen. Optimise for lower cognitive effort and stronger continuity.

## The journey plan

The walker reads a JSON plan. Start from `assets/journey-plan.example.json`.

```json
{
  "project": "Example",
  "baseUrl": "http://localhost:3000",
  "viewports": ["phone", "laptop"],
  "journeys": [
    {
      "id": "first-arrival",
      "intent": "A new visitor understands what this is and what to do first",
      "steps": [
        { "goto": "/", "capture": "landing" },
        { "scroll": "bottom", "capture": "landing-end" },
        { "click": "text=Get started", "capture": "signup" },
        { "fill": { "selector": "input[name=email]", "value": "reviewer@example.com" } },
        { "press": "Enter", "waitFor": "text=Check your inbox", "capture": "sent" }
      ]
    }
  ]
}
```

| Step key | Does | Read-only mode |
| --- | --- | --- |
| `goto` | Navigate to a path or URL | Allowed |
| `scroll` | `"bottom"`, `"top"`, or a pixel count | Allowed |
| `hover` | Hover a selector | Allowed |
| `wait` | Pause for N ms | Allowed |
| `waitFor` | Wait for a selector (property on any step) | Allowed |
| `capture` | Name this moment; screenshot and probe (property on any step, or its own step) | Allowed |
| `click` | Click a selector | Stops the journey |
| `fill` | Type into a selector | Stops the journey |
| `press` | Press a key | Stops the journey |
| `select` | Choose an option | Stops the journey |

Selectors are Playwright selectors (`text=`, `role=`, CSS, `data-testid`).

Viewports: `phone` (390×844), `tablet` (820×1180), `laptop` (1280×800),
`desktop` (1728×1117). Default is phone and laptop. Pass `--viewport all` when
the product serves all four; tablet is where "responsive but not designed" is
most visible.

```bash
node scripts/walk_journeys.mjs --plan journeys.json --out per-evidence
node scripts/walk_journeys.mjs --plan journeys.json --out per-evidence --interact --storage-state auth.json --viewport all
```

`--interact` is for a staging environment, a local build, or a seeded fixture,
with a dedicated test account. Never point it at production for anything that
commits, pays, deletes, sends, or shares.

## What the walker records

Per capture, per viewport, alongside the screenshot:

| Reading | What it tells you | Lens |
| --- | --- | --- |
| `ackMs` | Milliseconds from the previous action to the first DOM change (or navigation); the interface's acknowledgement latency, waited for up to `--ack-wait` ms | Perceived performance |
| `settleMs` | Approximate milliseconds after the action until the network went quiet; how long the user waited for the result | Perceived performance |
| `cls` | Cumulative layout shift since the last navigation | Perceived performance |
| `controlsWithoutFocusStyle` | Interactive elements with no visible change on keyboard focus | Accessibility, interaction states |
| `controlsWithoutHoverStyle` | Interactive elements with no visible change on hover (laptop and desktop only) | Interaction states |
| `movesUnderReducedMotion` | Animations and transitions still running with `prefers-reduced-motion: reduce` | Motion, accessibility |
| `longTransitions` / `infiniteAnimations` | Transitions over 400ms; animations that never end | Motion |
| `horizontalOverflow` | Page wider than the viewport | Responsive |
| `targetsUnder44` | Interactive elements with a rendered box under 44px on the phone | Accessibility, mobile |
| `fixedCoveragePct` | Share of the phone viewport occupied by fixed or sticky elements | Mobile, thumb reach |
| `primaryLikeActions` / `primaryAboveFold` | Filled, high-contrast actions on the surface, and whether one is in the first viewport | Hierarchy |
| `containers` | Counts of bordered, shadowed, and pill-shaped elements, icons, headings, and the deepest container nesting | Premium craft |
| `copy` | Headings, action labels, helper text, placeholders, live-region text, and vague labels (Submit, OK, Continue, Learn more) | Language |
| `unlabelledFields` | Inputs with no label, `aria-label`, or `aria-labelledby` | Accessibility |
| `imagesMissingAlt` / `imagesMissingDimensions` | Images without alternative text; images without reserved size | Accessibility, performance |
| `headingOrderSkips` / `landmarks` | Skipped heading levels; presence of `main` and `nav` | Accessibility |
| `waitingIndicators` | Spinners, skeletons, and `aria-busy` regions still present at capture | Perceived performance |
| `actionableCount` | Visible actionable elements; zero is a dead end | Journeys |
| `consoleErrors` / `failedRequests` | Errors the user may or may not see | Trust |

`summary.json` indexes every capture; `summary.md` is a table you can paste
into the review. Read the screenshots too. The readings tell you where to
look; they do not tell you what the surface is for.

## What the walker does not do

- It does not judge. `primaryLikeActions` is a proxy; confirm against the
  screenshot before filing.
- It does not measure contrast through composited backgrounds or accent
  coverage. `premium-calm`'s `measure_surface.mjs` does, and you can run it on
  the same URLs when a finding needs those numbers.
- Hover probing reads computed style on the element; a hover treatment drawn
  on a child or a pseudo-element may read as missing. Confirm by hand before
  filing.
- Native mobile apps are out of its reach. Walk them on a device or simulator
  and file with `Screenshot` evidence, saying so.

## When the browser cannot run

Degrade in this order and record the tier on every finding:

1. **Walked, live or local.** The full plan, with `--interact` on a safe
   environment. Preferred.
2. **Walked, read-only.** Entry surfaces at each viewport, with the probe
   readings. Interaction-dependent states come from source.
3. **Source only.** Read routes, components, and state for what each journey
   would do. Every finding is `Source`, and the review says that no journey was
   walked.
4. **Screenshots only.** Composition, hierarchy, and copy findings are
   legitimate. Focus, motion, latency, contrast, and target-size findings are
   not; do not assert them.
