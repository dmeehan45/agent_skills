# Inspecting the implementation

Phase 5. The code explains why the experience is the way it is. Reading it
turns an observation into a root cause, a root cause into a class, and a
dozen local symptoms into one systemic change. Do this before writing any
finding; a finding written before its cause is known lands at the wrong
altitude and recommends the wrong fix.

## What to read, and what it explains

| Read | To learn | Symptoms it usually explains |
| --- | --- | --- |
| **Routing** (routes, navigators, deep links) | The product's real information architecture; what is a screen versus a state | Unnecessary navigation; feature-per-screen; lost context on route change |
| **State management** (stores, contexts, query caches, URL state) | What persists across screens, reloads, and sessions; what is refetched | Duplicated information; remembering what the system knows; loss of drafts on interruption |
| **Component architecture** (primitives, composition, one-offs) | Whether there is a system, and whether the product uses it | Inconsistent interaction patterns; the same control implemented three ways |
| **Design tokens** (colour, type, space, radius, shadow, motion) | Whether the visual vocabulary is decided once or per screen | Equal prominence; accent everywhere; off-scale spacing; nesting |
| **Typography and spacing primitives** | The scale, and whether components respect it | Hierarchy carried by containers; uniform padding; too many type treatments |
| **Responsive logic** (breakpoints, layout components, platform checks) | Whether mobile is designed or derived | Reflowed desktop; fixed-element pile-up; wrong density |
| **Animation implementation** (transition libraries, shared elements, reduced-motion handling) | Whether motion is a system or per-screen decoration | Motion that explains nothing; reduced motion ignored; inconsistent durations |
| **Loading and error handling** (suspense boundaries, query states, error boundaries, retries) | Which states exist, and where they are handled | Blank waits; generic errors; lost work on failure; dead ends |
| **Persistence** (local storage, drafts, offline, sync) | What survives interruption | Interruption and resumption failures; unexpected behaviour on return |
| **Forms** (validation, defaults, autofill, field types) | Where decisions are forced on the user | Premature configuration; missing defaults; wrong keyboards |
| **Accessibility semantics** (roles, names, focus management, live regions) | Whether accessibility is in the primitives or bolted on per screen | Unlabelled controls; focus lost; state changes unannounced |
| **Duplicated components and one-off styling** | Where the system was bypassed | Drift: the same thing, slightly different, everywhere |
| **Analytics and feature flags** | What the team measures and what is half-shipped | Incidental features with full prominence |

Search for the specific evidence a finding needs. Some queries that pay off:

```bash
# Which surfaces read a value the user was asked for?
rg 'onboarding\.(schedule|reminders)' src
# Is reduced motion handled anywhere?
rg -n 'prefers-reduced-motion|useReducedMotion|reduceMotion' src
# How many button implementations exist?
rg -ln '<button|role="button"' src | wc -l ; rg -ln 'from .*ui/Button' src | wc -l
# Where is focus styling reset?
rg -n 'outline:\s*none|outline-none|focus:outline-none' src
# Which routes mount a full-screen spinner?
rg -n 'Spinner|isLoading &&|loading \?' src --type tsx
# Which strings are the vague labels?
rg -n '>(Submit|OK|Continue|Next|Learn more)<' src
# Where do confirmations stand in for undo?
rg -n 'confirm\(|Are you sure' src
```

Adapt to the stack: the same questions apply to SwiftUI, Compose, Flutter,
Vue, or server-rendered templates.

## Classify every finding

For each observed problem, name the decision that produced it and assign one
class.

| Class | Test | Fix lives in |
| --- | --- | --- |
| **Local flaw** | The primitive exists and is right; this instance bypassed it or implemented it badly | The instance. Small, safe, and usually not the review's most important work |
| **System drift** | The primitive is missing, wrong, or not enforced, so the problem recurs wherever a screen made its own decision | The primitive, token, or pattern. Every instance inherits the fix |
| **Product model** | The screen, flow, or feature exists because of a wrong or missing product decision; no component work fixes it | The product architecture: remove, merge, reorder, infer, default |

Three questions settle most cases:

1. **Would fixing this here fix it everywhere?** No → it is not a local flaw.
2. **Would a perfect primitive make this screen right?** No → it is not system
   drift; the screen itself is the problem.
3. **Does the code reveal that the team believes something about the user
   that the product model contradicts?** Yes → product model. The data model
   requiring preferences before rendering a plan is the team believing the
   user wants to configure.

## Collapse into systemic roots

Group findings by underlying issue. When three or more share one, they become
a single finding at the class and altitude of the root, with the instances
listed inside it, and a row in the review's "Systemic roots" table:

| Root | Class | Findings | The one change | Lands in |
| --- | --- | --- | --- | --- |
| No pressed or loading state in the button primitive | System drift | PER-05, PER-09, PER-14 | Add pressed and loading states to `Button`; remove per-screen spinners | `src/ui/Button.tsx` |
| Hierarchy carried by nested bordered cards | System drift | PER-11a–d | Replace `Card` nesting with a `Section` primitive that groups by spacing and a single heading level; reserve `Card` for interactive, self-contained objects | `src/ui/Section.tsx` (new), `src/ui/Card.tsx` |
| Preferences required before value | Product model | PER-01, PER-03, PER-07 | Render a default plan; move preferences to inline adjustments | `src/features/plan/` |

Do not recommend dozens of local patches when one systemic change would solve
them. The review's value is concentrated in this table.

## Bundle into primitives

When writing the implementation sequence, bundle changes that land in the
same primitive so they ship as one change and are verified together:

- **Ship together:** everything that lands in one primitive (all of `Button`'s
  missing states); everything that lands in one token (the accent's new role,
  and the removal of its old uses).
- **Do not ship together:** a structural change and a restyle of the same
  surface (you will not know which one moved the experience); two Product
  findings that change the same journey (walk it between them).

Foundations land as primitives, not as per-screen patches. If a fix is
applied in three components, it belonged in the primitive.

## Respect the codebase

- Recommend changes in the product's own conventions. A review that proposes
  a second styling system, a new animation library, or a parallel component
  set has added debt, not removed it.
- When a primitive exists and is right, the recommendation is "use it", with
  the list of places that do not.
- When the design system itself is the problem, say so once, in the systemic
  roots, and point at `premium-calm` for producing a validated token layer
  rather than proposing hex values in a review.
- Name files, components, routes, and tokens by their real names. The
  implementation surface is where a coding agent starts; it must resolve.
