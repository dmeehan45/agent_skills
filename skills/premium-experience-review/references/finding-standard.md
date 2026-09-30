# The finding standard

The review is read by two people: a product designer who needs to agree or
disagree with each recommendation on the merits, and a coding agent who needs
to open a file and start. A finding that serves only one of them is half a
finding. This document defines the shape every meaningful finding takes, the
vocabulary the linter enforces, and the test that separates a finding from an
opinion.

## The shape

```markdown
### PER-07 — Plan week starts empty and asks the user to configure before showing value

**Altitude** Product · **Priority** Foundational · **Class** Product model · **Effort** L
**Surface** Plan (first arrival, empty state) · **Evidence** Walked — per-evidence/first-arrival/phone/02-plan.png; Source — src/features/plan/PlanWeek.tsx:41

**Observation** A new user lands on an empty seven-column week with a
"Set your preferences to get started" callout and a Settings link. Nothing
edible is visible until diet, household size, and budget are entered on a
separate screen.

**User consequence** The first minute contains configuration instead of value.
The user cannot tell whether the product plans well before doing work for it,
and the empty grid reads as "you have nothing" rather than "we have something
for you".

**Underlying issue** The plan is modelled as user-authored from a blank state.
Preferences are a prerequisite in the data model (`PlanWeek` refuses to render
suggestions when `prefs` is null) rather than a refinement of a default plan.

**Recommended change** Render a complete, sensible default week on first
arrival (the most popular plan for the detected locale), with preferences
offered as inline adjustments on the plan itself ("Fewer meat days", "Feeds 2 →
4"). Move the Settings screen's diet, household, and budget fields into those
inline adjustments and delete the Settings entry for them.

**Premium expression** The user's first sight of the product is a week they
could cook tomorrow. Adjusting one preference visibly re-flows the week in
place, so the product proves it understands them before asking anything.
Nothing has to be filled in to see what the product does.

**Implementation surface** `src/features/plan/PlanWeek.tsx` (render default
plan when `prefs` is null), `src/lib/plan/defaultPlan.ts` (new),
`src/features/settings/DietSection.tsx` (remove; fields move to
`src/features/plan/PlanAdjustments.tsx`), route `/settings/diet` (remove).

**Acceptance** A new account sees at least seven meals within the first
paint of `/plan`; changing any adjustment updates the week without navigation;
`/settings/diet` no longer exists.
```

Every meaningful finding has all of these. The linter rejects a review whose
findings are missing fields, use vocabulary outside the tables below, or
contain the banned phrases.

## Field by field

| Field | Must contain | Not done until |
| --- | --- | --- |
| **Title** | One line: the surface and the problem, stated as a fact | Someone who reads only the ledger understands what is wrong |
| **Altitude** | `Product`, `Experience`, or `Craft` | It matches where the *change* lives, not where the symptom was seen |
| **Priority** | `Foundational`, `Friction`, `Refinement`, or `Exceptional craft` | It reflects the cost to the user, not the effort to fix |
| **Class** | `Local flaw`, `System drift`, or `Product model` | You have read the code and know why it happens |
| **Effort** | `S`, `M`, or `L` | It accounts for the implementation surface as listed |
| **Surface** | The screen or state, and the journey step | A reader can navigate to it |
| **Evidence** | One or more tiers, each with a path: `Walked — <capture>`, `Source — <file:line>`, `Screenshot — <image>`, `Reported — <who/where>` | Every claim in Observation is backed by one of them |
| **Observation** | What currently happens, described as a user would experience it | It contains no judgement words; a defender of the current design would agree it is accurate |
| **User consequence** | Why it matters to the user, in their situation | It names the cost: a decision, a wait, a doubt, a lost thing, a wrong belief |
| **Underlying issue** | The design or product decision producing the problem | It explains the *class*, and would predict other instances |
| **Recommended change** | What should change, specifically enough to disagree with | A coding agent could start without asking a question |
| **Premium expression** | How an exceptional implementation would behave or feel | It describes behaviour, timing, and state, not adjectives |
| **Implementation surface** | Where in the product or code the change belongs | Files, components, routes, tokens, or the layer named |
| **Acceptance** *(encouraged)* | How a reviewer would know it landed | It is checkable by walking the product again |

## The vagueness test

Before filing a finding, ask two questions.

1. **Could a coding agent open the named file and begin?** If the agent would
   have to ask "which element", "how much", "what should it look like", or
   "what do you mean by cleaner", the recommended change is not finished.
2. **Could a product designer disagree with it on the merits?** A finding
   that no one could argue with ("improve the hierarchy") is not making a
   claim. A finding that says "the price should be the largest element on the
   detail screen and the photo carousel should be secondary" can be wrong,
   which means it can be right.

These phrases fail both tests and the linter rejects them in the recommended
change and premium expression fields:

```
improve hierarchy · make this cleaner · add polish · improve the onboarding
make the design more premium · add animations · make it pop · modernise
more intuitive · cleaner look · add micro-interactions · improve UX
enhance the user experience · consider improving · could be better
needs love · feels off · tighten up · elevate the design · more delightful
```

Replace each with the specific decision: which element, which state, which
value, which behaviour, at which moment.

## Altitude — where the change lives

| Altitude | The change is to | Examples |
| --- | --- | --- |
| **Product** | The product model, feature hierarchy, architecture, flows, or fundamental approach | A screen should not exist; onboarding should be replaced by a default; two features should merge; a setting should be inferred |
| **Experience** | Journeys, screens, navigation, information architecture, state management, content, interaction patterns | A step should move earlier; a modal should become inline; context should persist across a transition; an empty state should offer the next action |
| **Craft** | Composition, typography, spacing, responsiveness, transitions, visual hierarchy, micro-interactions, motion, detailed behaviour | A pressed state is missing; a container is nested three deep; a transition explains nothing; a target is 32px on the phone |

Altitude follows the fix. A missing loading state on the pay button is Craft
even though its consequence is severe; the fix is one component's behaviour.

## Priority — what it costs the user

| Priority | Definition | Filed when |
| --- | --- | --- |
| **Foundational** | Undermines usefulness, comprehension, architecture, or the primary jobs | The product model is incoherent; the first minute contains no value; a critical journey dead-ends; a job cannot be completed by keyboard or on the phone; a commitment has no honest state |
| **Friction** | Makes the job harder than necessary | Extra decisions or actions; lost context; premature configuration; avoidable confirmation; unclear state; waiting; remembering what the system knows |
| **Refinement** | Improves coherence, confidence, and quality | Inconsistent patterns; hierarchy carried by containers instead of composition; copy that over-explains; motion that does not explain; incomplete state coverage off the critical path |
| **Exceptional craft** | Elevates a functional experience into a premium one | Signature moments; precision in micro-interactions; editorial typography; object continuity across navigation |

Rules:

- **Visual refinements never outrank Foundational or Friction findings.** If
  you find yourself ranking a spacing inconsistency above an empty first
  minute, the priorities are wrong.
- **Effort orders work within a priority, never across it.** A cheap
  Refinement is done after an expensive Foundational, or bundled into the same
  primitive so it comes free.
- **Priority and altitude are independent.** A Craft finding can be
  Foundational; a Product finding can be Refinement.

## Class — why it happens

| Class | Definition | The fix goes in |
| --- | --- | --- |
| **Local flaw** | One component or screen implemented badly, in a system that is otherwise right | That component |
| **System drift** | A primitive, token, pattern, or convention that is missing, wrong, or bypassed, so the same problem recurs wherever the primitive is not used | The design system or the shared primitive; the local instances then inherit the fix |
| **Product model** | The screen, flow, or feature exists because of a wrong or missing product decision | The product architecture; no amount of component work fixes it |

Class requires reading the code. A finding classed without a `Source` evidence
entry is a guess, and the linter warns.

## Evidence tiers

| Tier | Means | Supports |
| --- | --- | --- |
| **Walked** | Observed in the running product; cite the walker capture or the manual step | Everything |
| **Source** | Established by reading the implementation; cite `file:line` | Behaviour, state coverage, root cause, class |
| **Screenshot** | Inferred from a static image | Composition, hierarchy, copy, density. Not focus, motion, latency, contrast, or target size |
| **Reported** | Told to you by the user, a ticket, or analytics; not verified by you | Nothing on its own; pair it with a walk |

Never assert a state you did not reach. If a finding depends on a state you
could not reach, say so in the finding and list the state in "not reviewed".

## Collapsing into systemic roots

When three or more findings share an underlying issue, they are one finding.
Keep the instances as a list inside the finding and file it once, at the
altitude and class of the root:

```markdown
**Observation** Four surfaces carry their hierarchy with bordered cards nested
inside bordered cards: Plan (`PlanDay` inside `PlanWeek`), Recipe
(`IngredientGroup` inside `RecipeCard`), Shopping (`Aisle` inside `ListCard`),
Settings (`Section` inside `Panel`). Instances: PER-11a–d in the ledger.
```

The "Systemic roots" section of the review then maps each root to the single
change that resolves all its instances. Dozens of local patches where one
primitive change would do is the failure mode this rule exists to prevent.

## Bad → good

**Bad.** "The dashboard feels cluttered. Improve hierarchy and reduce visual
noise; consider a cleaner card layout."

**Good.** "The Home screen presents six modules (streak, today's plan, tips,
community, upgrade, recent) at equal size, weight, and container treatment;
nothing is larger than 24% of the viewport on the phone
(`per-evidence/repeat-use/phone/01-home.png`). The user's job on return is to
see today's plan; it sits third. Make today's plan the only full-width module
at the top, demote streak to a one-line ambient indicator in the header,
collapse tips and community into a single secondary row below the plan, and
move upgrade to the paywall entry points where it has a reason to appear. In
`src/screens/Home.tsx`, replace the `ModuleGrid` with a `TodayPlan` primary
region and a `Secondary` row; delete `HomeModule` variants that no longer
render."

**Bad.** "Add micro-interactions to buttons so the app feels more premium."

**Good.** "The primary button (`src/ui/Button.tsx`) has hover and focus styles
but no pressed state and no loading state; on the phone, tapping Save gives no
feedback for the 300–700ms the request takes (`ackMs` 412 median across
`per-evidence/first-action/phone/journey.json`). Add a pressed state (scale
0.98, 80ms, respecting reduced motion) and a loading state that replaces the
label with a progress indicator while preserving the button's width, and
disable double submission. Because `Button` is the shared primitive, every
commitment surface inherits both states."

**Bad.** "Onboarding is too long; improve the onboarding."

**Good.** "Onboarding asks five questions (goal, experience, schedule,
reminders, name) before showing the product; the answers to three of them
(schedule, reminders, name) are never read by any screen in the first week
(`rg 'onboarding\.schedule' src` returns only the onboarding writer). Cut
onboarding to the one question that changes the first screen (goal) and
collect the rest at the moment each is first needed: schedule when the user
opens the calendar, reminders after the first completed session. Delete
`OnboardingSchedule`, `OnboardingReminders`, and `OnboardingName`; add
contextual prompts in `CalendarEmpty.tsx` and `SessionComplete.tsx`."

## What is not a finding

- **Praise.** Genuinely strong decisions go in "The current experience →
  strongest parts", so they survive the redesign. Do not file them as findings
  and do not pad the review with compliments for ordinary competence.
- **Defects.** A crash, a 500, a broken link belong in a QA report. Note them
  in "not reviewed / defects seen" and move on, unless the defect *is* the
  experience (a commitment that silently fails is a Foundational finding).
- **Preference without consequence.** If you cannot name the user
  consequence, you have a taste, not a finding.
- **Anything against "must not change".** Record it as a conversation for the
  owner in the synthesis, not as a finding.
