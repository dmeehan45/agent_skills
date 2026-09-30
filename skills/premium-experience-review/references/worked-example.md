# Worked example — Ladle, a weekly dinner planner

A condensed review of a fictional consumer product, at the bar this skill
expects. Ladle is a web and mobile-web app that plans a week of dinners,
builds the shopping list, and tells the user what to cook tonight. The
product, the paths, and the numbers are invented; the *shape* is the point.
Every finding below passes `scripts/check_review.py`.

**Provenance.** This review was walked on a local build with `--interact`
against seeded fixtures, at phone and laptop sizes, with the codebase open.
Where a state was not reached it says so.

---

## 1. Product model

| | |
| --- | --- |
| Primary user | A person who cooks most weeknights for a household and is tired of deciding what |
| Situation | Sunday evening, or 5pm on a weekday with nothing defrosted |
| Functional job | Get seven dinners decided and the ingredients into the house with the least deciding |
| Emotional job | Stop feeling that dinner is a daily small failure |
| First minute | Should see a week they could cook tomorrow. Currently sees an empty grid and a link to Settings |
| Shortest path to value | Today: 9 steps (signup, 3 preference screens, plan, add ×4). Could be 1: open the app |
| Primary loop | Evening: open → see tonight → cook. Weekly: Sunday → adjust the week → shop |
| Return trigger | Tonight's dinner is already decided and the ingredients are in the fridge |
| Unusually good | "It just knew what we'd eat, and the list was right" |
| Central | Plan week, Tonight, Shopping list, Swap |
| Incidental | Discover feed, Saved tab, Community, Streak, Settings → Diet |
| Premium means, here | Value before configuration; defaults that are right; editing in place; the product remembers so the user need not |
| Must not change | The warm terracotta accent, the hand-drawn recipe illustrations, the one-week horizon (deliberately not a calendar), no accounts required to browse |

**Ambiguities.** The Home surface cannot say whether Ladle is a tonight
product or a weekly product; it gives Tonight, Plan, and Discover equal
weight (PER-02). The Discover feed reads as a content product grafted onto a
utility; nothing in the loop uses it.

---

## 2. The current experience

**As a user lives it.** On the phone, a new user taps Get started, answers
diet, household size, and budget on three screens, and lands on an empty
seven-column week with "Set your preferences to get started" (the preferences
they just set) and a Settings link. Adding a meal opens a full-screen search.
After four additions the week is half full and the shopping list, on another
tab, has regenerated from scratch each time, unchecking what was checked. On
Tuesday evening, returning to Home shows Tonight third, below a streak badge
and a Discover carousel. Removing Wednesday's meal asks "Are you sure?" There
is no undo.

**Strongest parts.** The Swap sheet is the best decision in the product:
three alternatives, each with a one-line reason ("uses the same chicken"),
one tap to commit. The one-week horizon is right; a calendar would invite
planning as a hobby. The recipe page is calm: one column, ingredients first,
method second, nothing else. The illustrations carry the brand without
shouting. Preserve all four.

**Weakest moments.**

1. The first minute contains configuration and an empty grid (PER-01).
2. Home does not know what it is for (PER-02).
3. Every change is either confirmed or unrecoverable (PER-04, PER-09).
4. Tapping Save or Swap on the phone does nothing visible for half a second (PER-06).
5. The shopping list forgets what was checked (PER-05).

**Journey ledger**

| Journey | Reached | Sizes | Evidence | Verdict |
| --- | --- | --- | --- | --- |
| First arrival | yes | phone, laptop | per-evidence/first-arrival/ | Configuration before value; empty grid |
| First meaningful action | yes | phone, laptop | per-evidence/first-action/ | Full-screen search for one meal; no feedback on tap |
| First successful outcome | yes | phone | per-evidence/first-outcome/ | List is right, but silent about being generated |
| Repeat use | yes | phone | per-evidence/repeat-use/ | Tonight is third on Home |
| Returning after time away | partial (fixture) | phone | per-evidence/returning-after-time-away/ | Streak-lost banner over a stale week |
| Changing or undoing | yes | phone, laptop | per-evidence/undo/ | Confirm dialog; no undo |
| Missing information | yes | phone | per-evidence/first-arrival/ | Sends the user to Settings |
| Error | yes (fixture) | phone | per-evidence/error/ | "Something went wrong"; swap lost |
| Empty state | yes (fixture) | phone, laptop | per-evidence/empty-state/ | Illustration and a sentence; no action |
| Interruption and resumption | partial | phone | manual | Draft swap lost on tab switch |
| Mobile | yes | phone | all of the above | Designed for the phone; the tablet is a stretched phone |

---

## 3. Hierarchy by surface

| Surface | User is trying to | Should be primary | Is primary today | Secondary | Ambient | Disclosed | Remove |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Home | Know what to cook tonight | Tonight, full width | Nothing; three equal modules | Rest of the week | Streak (one line) | Discover | Community, Upgrade banner |
| Plan | See and adjust the week | The week, filled | An empty grid and a callout | Swap | Nutrition totals | Preferences (inline) | Settings link |
| Shop | Buy what is missing | The unchecked items, by aisle | The whole list, flat | Checked items (collapsed) | Item count | Add item | Regenerate button |
| Recipe | Cook | Ingredients then method | Correct today | Swap | Servings | Nutrition | — |

**Centre of gravity.** Home and Plan differ from "should" because the product
model treats configuration and discovery as first-class (PER-01, PER-02).
Shop differs because the list is regenerated rather than maintained (PER-05).

---

## 4. Findings

### Ledger

| ID | Altitude | Priority | Class | Surface | Finding | Effort |
| --- | --- | --- | --- | --- | --- | --- |
| PER-01 | Product | Foundational | Product model | Plan, onboarding | Plan starts empty and asks for preferences before showing value | L |
| PER-02 | Product | Foundational | Product model | Home | Home gives Tonight, Plan, and Discover equal weight; the loop has no centre | M |
| PER-06 | Craft | Foundational | System drift | Button primitive | No pressed or loading state; double submission creates duplicate meals | S |
| PER-04 | Experience | Friction | System drift | Plan, Shop | Confirmation dialogs stand in for undo on every mutation | M |
| PER-05 | Experience | Friction | System drift | Shop | Shopping list regenerates from scratch, discarding checked items | M |
| PER-09 | Experience | Friction | System drift | Plan (error) | Failed save shows "Something went wrong" and discards the swap | S |
| PER-03 | Experience | Friction | Product model | Saved, Swap | Saved recipes are a destination instead of the swap sheet's first source | M |
| PER-07 | Craft | Refinement | System drift | Plan, Recipe, Shop, Settings | Hierarchy carried by bordered cards nested inside bordered cards | M |
| PER-08 | Craft | Refinement | System drift | All routes | Reduced motion ignored; 450ms fade on a 60ms route change | S |
| PER-10 | Craft | Exceptional craft | System drift | Swap | The swap could be the signature interaction: the chosen recipe travels into the day | M |

### Product-level

### PER-01 — Plan starts empty and asks for preferences before showing value

**Altitude** Product · **Priority** Foundational · **Class** Product model · **Effort** L
**Surface** Plan (first arrival, empty state); onboarding screens 2–4 · **Evidence** Walked — per-evidence/first-arrival/phone/03-plan.png; Source — src/features/plan/PlanWeek.tsx:41, src/features/onboarding/steps.ts:8

**Observation** After three preference screens the new user lands on an empty
seven-column week with a "Set your preferences to get started" callout and a
Settings link. `PlanWeek` returns the empty grid when `prefs.complete` is
false, and `prefs.complete` is only set by the Settings → Diet form, not by
onboarding.

**User consequence** The first minute is configuration followed by an empty
grid that contradicts what they just did. The user cannot tell whether Ladle
plans well before working for it, and the emptiness reads as "you have
nothing" rather than "we have something for you".

**Underlying issue** The plan is modelled as user-authored from a blank state,
with preferences as a prerequisite in the data model rather than a refinement
of a default. Onboarding and Settings write different fields for the same
concept.

**Recommended change** Render a complete default week on first arrival (the
most-cooked plan for the detected locale and a two-person household), with
preferences as inline adjustments on the plan itself: "Fewer meat days",
"Feeds 2 → 4", "Under £60". Delete onboarding screens 2–4 and the Settings →
Diet screen; their fields become those adjustments.

**Premium expression** The first thing a new user sees is a week they could
cook tomorrow, with the illustrations doing the welcoming. Tapping "Feeds 4"
re-flows the week in place over 200ms; the product proves it understands
before it asks anything. Nothing has to be filled in to see what Ladle does.

**Implementation surface** `src/features/plan/PlanWeek.tsx` (render
`defaultPlan()` when `prefs` is incomplete), `src/lib/plan/defaultPlan.ts`
(new), `src/features/plan/PlanAdjustments.tsx` (new, absorbs the fields from
`src/features/settings/DietSection.tsx`, which is removed), `src/features/onboarding/steps.ts` (keep only the goal step), route `/settings/diet` (remove).

**Acceptance** A new account sees at least seven meals in the first paint of
`/plan`; changing any adjustment updates the week without navigation;
`/settings/diet` no longer exists; onboarding is one screen.

### PER-02 — Home gives Tonight, Plan, and Discover equal weight; the loop has no centre

**Altitude** Product · **Priority** Foundational · **Class** Product model · **Effort** M
**Surface** Home (returning user) · **Evidence** Walked — per-evidence/repeat-use/phone/01-home-returning.png (three modules at 31% viewport height each; Tonight third); Source — src/screens/Home.tsx:22 (`ModuleGrid` renders `modules` in config order)

**Observation** On a weekday evening Home shows a streak badge, a Discover
carousel, then Tonight, each in an identical card. The primary action
"Cook tonight" is below the fold on the phone.

**User consequence** The user opens the app to answer one question and has
to find the answer. Every visit, they re-establish the hierarchy the product
should hold for them.

**Underlying issue** Home is a module grid configured from a list, so every
module has equal prominence by construction. The product has not decided
whether it is a tonight product or a weekly product, and the grid expresses
that indecision.

**Recommended change** Make Tonight the only full-width region at the top of
Home: the illustration, the dish, the time to cook, and one action. Below it,
the rest of the week as a single quiet row. Move streak to a one-line ambient
indicator in the header. Move Discover behind Swap (see PER-03) and remove it
from Home. Remove the Community and Upgrade modules from Home; Upgrade lives at
the paywall entry points.

**Premium expression** Opening Ladle at 5pm answers the question before the
user asks it. The rest of the week is glanceable but not competing. The
surface has one centre of gravity, and it is dinner.

**Implementation surface** `src/screens/Home.tsx` (replace `ModuleGrid` with
`TonightHero` and `WeekRow`), `src/screens/home/modules.ts` (remove Discover,
Community, Upgrade entries), `src/components/StreakBadge.tsx` (becomes a
header indicator).

**Acceptance** On the phone, "Cook tonight" is in the first viewport; no other
region exceeds 20% of the viewport height; the Home route renders at most
three regions.

### Experience-level

### PER-04 — Confirmation dialogs stand in for undo on every mutation

**Altitude** Experience · **Priority** Friction · **Class** System drift · **Effort** M
**Surface** Plan (remove, swap), Shop (clear, remove item) · **Evidence** Walked — per-evidence/undo/phone/02-removed.png (native `confirm()` dialog); Source — src/lib/api/useMutation.ts:14 (no rollback), `rg 'Are you sure' src` → 6 call sites

**Observation** Removing a meal, swapping, clearing the list, and removing an
item each open "Are you sure?" Confirming is final; there is no undo anywhere
in the product.

**User consequence** Every small change carries the weight of a big one. The
user hesitates before trying things, which is the opposite of what a planner
should invite, and a mis-tap is unrecoverable.

**Underlying issue** The mutation wrapper is fire-and-forget: it has no
optimistic update and no rollback, so the six call sites each added a
confirmation to compensate. Undo was never possible at the primitive level.

**Recommended change** Give `useMutation` an optimistic update with a stored
inverse, and surface a single, quiet, inline undo affordance for eight seconds
after any reversible mutation ("Wednesday removed · Undo"). Remove all six
confirmation dialogs. Keep a deliberate confirmation only for clearing the
whole week, and phrase it as the consequence: "Remove all 7 dinners? The
shopping list will empty too."

**Premium expression** Changes happen the moment they are asked for, and can
be taken back the moment they are regretted. The product feels safe to touch.

**Implementation surface** `src/lib/api/useMutation.ts` (optimistic update,
inverse, `undo()`), `src/components/UndoBar.tsx` (new, inline, not a toast),
call sites listed by `rg 'Are you sure' src`.

**Acceptance** No `confirm(` or "Are you sure" remains except the clear-week
path; removing a meal shows the undo affordance within 100ms and undo restores
the meal and the list.

### PER-05 — Shopping list regenerates from scratch, discarding checked items

**Altitude** Experience · **Priority** Friction · **Class** System drift · **Effort** M
**Surface** Shop, after any plan change · **Evidence** Walked — per-evidence/first-outcome/phone/02-first-item-checked.png then per-evidence/first-action/phone/03-swapped.png (item unchecked after swap); Source — src/features/shop/buildList.ts:5 (`return aggregate(plan)` with no reconcile against the existing list)

**Observation** Checking off "onions" then swapping Thursday's meal rebuilds
the list; onions are unchecked and the list order changes.

**User consequence** In the shop, the list lies. The user re-checks items or
stops trusting the list and buys from memory, which is the job the product
exists to remove.

**Underlying issue** The list is derived state recomputed on every plan
change instead of a maintained object reconciled with the plan. The same
mutation wrapper (PER-04) has no notion of merging.

**Recommended change** Make the list a persisted object keyed by ingredient;
on plan change, diff the new aggregate against it, preserving `checked` and
user-added items, and show the delta inline ("+3 items for Thursday") rather
than rebuilding. Remove the Regenerate button.

**Premium expression** The list quietly keeps up with the week. What the user
checked stays checked; what the swap added arrives with a two-word note; the
order is stable so the shop is walked the same way every time.

**Implementation surface** `src/features/shop/buildList.ts` (becomes
`reconcileList(existing, plan)`), `src/features/shop/ShopList.tsx` (delta
note, remove Regenerate), `src/lib/store/list.ts` (persist checked state).

**Acceptance** Check an item, swap a meal: the item stays checked, the list
order is unchanged, and a delta note appears for the new items.

### PER-09 — Failed save shows "Something went wrong" and discards the swap

**Altitude** Experience · **Priority** Friction · **Class** System drift · **Effort** S
**Surface** Plan (save fails) · **Evidence** Walked — per-evidence/error/phone/03-save-failed.png; Source — src/features/plan/PlanWeek.tsx:88 (`onError: () => toast('Something went wrong')`), src/lib/api/client.ts:31 (error body with `retryable` is available and unused)

**Observation** When the save fails, a toast says "Something went wrong", the
sheet closes, and the previous meal is back. The API response includes a
reason and whether a retry is safe; neither is shown.

**User consequence** The user does not know whether their choice was kept,
whether to try again, or whether the list changed. They redo the swap or give
up on it.

**Underlying issue** The mutation wrapper has no error state of its own, so
each screen handles failure ad hoc, and the cheapest handling is a generic
toast.

**Recommended change** In `useMutation`, keep the optimistic state on failure
and expose `error` with the API's reason and `retryable`; on the Plan, hold
the chosen meal in place with an inline "Couldn't save · Retry" affordance
where the undo bar sits, and only revert if the user dismisses it.

**Premium expression** The product keeps the user's choice and tells them
exactly what happened, next to the thing it happened to. One tap retries.
Nothing the user did is lost.

**Implementation surface** `src/lib/api/useMutation.ts` (error state, retry),
`src/components/UndoBar.tsx` (error variant), `src/features/plan/PlanWeek.tsx`
(replace the toast).

**Acceptance** With the `save-fails` fixture, the chosen meal stays visible,
the inline affordance names the failure, and Retry succeeds when the fixture
is cleared.

### PER-03 — Saved recipes are a destination instead of the swap sheet's first source

**Altitude** Experience · **Priority** Friction · **Class** Product model · **Effort** M
**Surface** Saved tab; Swap sheet · **Evidence** Walked — per-evidence/first-action/phone/02-swap-sheet.png (three suggestions, no saved items); Source — src/routes.tsx:19 (`/saved` route), src/features/plan/SwapSheet.tsx:30 (`suggest(plan, day)` reads recommendations only)

**Observation** Recipes the user hearts are collected on a Saved tab. The
Swap sheet suggests three recipes from the recommendation service and never
shows a saved one. To cook a saved recipe the user goes to Saved, opens it,
and taps "Add to plan", then picks a day.

**User consequence** The user's own stated preferences are the hardest thing
to act on. The loop (swap) ignores the signal (saved), so saving feels
pointless.

**Underlying issue** Saved was built as a feature with a screen rather than as
an input to the loop. The navigation exposes the product's storage, not the
user's job.

**Recommended change** Make saved recipes the first row of the Swap sheet
("Your saved · 4"), then the three suggestions. Remove the Saved tab from
navigation; keep `/saved` reachable from the profile as a list.

**Premium expression** Hearting a recipe changes what the product offers next
time, visibly, in the place where the offer is made. The user never has to
carry a recipe across the product.

**Implementation surface** `src/features/plan/SwapSheet.tsx` (prepend saved
row), `src/features/plan/suggest.ts` (accept saved as a source), `src/routes.tsx`
and `src/components/TabBar.tsx` (remove the Saved tab).

**Acceptance** With one saved recipe, the Swap sheet shows it first on every
day; the tab bar has four items.

### Craft-level

### PER-06 — No pressed or loading state; double submission creates duplicate meals

**Altitude** Craft · **Priority** Foundational · **Class** System drift · **Effort** S
**Surface** Button primitive, felt on Save, Swap, Add · **Evidence** Walked — per-evidence/first-action/phone/journey.json (`ackMs` 412 and 688 on the two clicks; duplicate Thursday entry after a double tap); Source — src/ui/Button.tsx:12 (variants: default, hover, focus, disabled; no active or loading), src/features/plan/SwapSheet.tsx:52 (no in-flight guard)

**Observation** Tapping Swap on the phone changes nothing on screen for
400–700ms. Tapping again submits again; the fixture produced two Thursday
meals and six extra list items.

**User consequence** Foundational rather than Refinement because it sits on
the primary loop and corrupts the plan and the list: the user's central action
feels broken, and a natural second tap creates work they must then undo (and
cannot, see PER-04).

**Underlying issue** The shared button has no pressed and no loading state,
and the mutation wrapper exposes no in-flight flag, so every commitment
surface is silent while it works.

**Recommended change** Add a pressed state to `Button` (scale 0.98 over 80ms,
respecting reduced motion) and a loading state that replaces the label with a
progress indicator while holding the button's width, driven by `useMutation`'s
`isPending`; ignore activation while pending. Every commitment surface
inherits both.

**Premium expression** The tap is felt the instant it lands. The button says
it is working without moving anything around it, and the result arrives into
the same place. A second tap does nothing because there is nothing to do.

**Implementation surface** `src/ui/Button.tsx` (`:active`, `loading` prop),
`src/lib/api/useMutation.ts` (`isPending`), `src/features/plan/SwapSheet.tsx`
and the other call sites (pass `loading`).

**Acceptance** `ackMs` under 100 on every click in the plan; a double tap on
Swap produces one meal; the button's width does not change while pending.

### PER-07 — Hierarchy carried by bordered cards nested inside bordered cards

**Altitude** Craft · **Priority** Refinement · **Class** System drift · **Effort** M
**Surface** Plan, Recipe, Shop, Settings · **Evidence** Walked — per-evidence/summary.md (`bordered` 38 and `maxNestDepth` 3 on Plan; 22 and 3 on Shop); Source — src/ui/Card.tsx used 41 times, `rg -l 'Card>' src/features` → 17 files; no `Section` primitive exists

**Observation** Four surfaces express grouping as a bordered, shadowed card
inside another: Plan (`PlanDay` inside `PlanWeek`), Recipe
(`IngredientGroup` inside `RecipeCard`), Shop (`Aisle` inside `ListCard`),
Settings (`Section` inside `Panel`). Instances PER-07a–d.

**User consequence** Every boundary competes with the content it contains.
The eye reads frames before food, and on the phone the nested padding costs a
third of the width.

**Underlying issue** `Card` is the only grouping primitive, so it is used for
every level of structure. Hierarchy that spacing and one heading level would
carry is carried by borders and shadows.

**Recommended change** Add a `Section` primitive that groups by a 24px gap
and a single small-caps heading, with no border or background. Reserve `Card`
for interactive, self-contained objects (a meal in the week, a recipe in the
Swap sheet). Replace the outer container on the four surfaces with `Section`
and remove the inner card's border where it sits inside a card.

**Premium expression** The week reads as seven dishes on a calm ground, not
seven boxes in a box. Structure is felt through rhythm; the illustrations and
dish names are the loudest things on the page.

**Implementation surface** `src/ui/Section.tsx` (new), `src/ui/Card.tsx`
(document the interactive-object rule), `src/features/plan/PlanWeek.tsx`,
`src/features/recipe/RecipeCard.tsx`, `src/features/shop/ShopList.tsx`,
`src/features/settings/Panel.tsx`.

**Acceptance** `maxNestDepth` is 1 on every walked surface; `bordered` on
Plan falls below 10; nothing that is not tappable has a border.

### PER-08 — Reduced motion ignored; 450ms fade on a 60ms route change

**Altitude** Craft · **Priority** Refinement · **Class** System drift · **Effort** S
**Surface** Every route transition; the streak flame; the loading shimmer · **Evidence** Walked — per-evidence/summary.md (`movesUnderReducedMotion` 6 on Home; `longTransitions` 14 on Plan); Source — src/app/Router.tsx:40 (`<Fade duration={450}>` around every route), `rg 'prefers-reduced-motion' src` → no results

**Observation** Every navigation fades the old screen out and the new one in
over 450ms; the route resolves in about 60ms. With reduced motion enabled the
fade, the flame, and the shimmer all still run.

**User consequence** Navigation feels slower than it is, and the motion
explains nothing about where the user went. Users who asked for less motion
get all of it.

**Underlying issue** Motion is a route-level decoration applied uniformly
rather than a system with a purpose per transition, and there is no
reduced-motion handling at the token or primitive level.

**Recommended change** Remove the route fade. Add a `motion` token set
(durations 80/160/240ms, one easing) and a `useReducedMotion` hook honoured by
`Button`, `UndoBar`, and the flame; under reduced motion, cross-fades become
cuts and the flame becomes a static icon. Reserve longer motion for the swap
(PER-10).

**Premium expression** Navigation is instant. The only things that move are
the things that changed, and they move for a reason. Reduced motion is
respected everywhere without looking broken.

**Implementation surface** `src/app/Router.tsx` (remove `Fade`),
`src/styles/tokens.css` (motion tokens), `src/lib/useReducedMotion.ts` (new),
`src/components/StreakFlame.tsx`, `src/ui/Skeleton.tsx`.

**Acceptance** `movesUnderReducedMotion` is 0 on every walked surface;
`longTransitions` is 0 outside the swap; route change shows the new screen
within one frame.

### PER-10 — The swap could be the signature interaction: the chosen recipe travels into the day

**Altitude** Craft · **Priority** Exceptional craft · **Class** System drift · **Effort** M
**Surface** Swap sheet → Plan → Shop · **Evidence** Walked — per-evidence/first-action/phone/03-swapped.png (sheet closes, day re-renders, list unchanged until refresh); Source — src/features/plan/SwapSheet.tsx:60 (`close(); refetch()`), no shared-element transition primitive in `src/ui`

**Observation** Choosing a recipe closes the sheet; the day slot re-renders
with the new dish; the shopping list updates only on next visit. Three
disconnected changes for one decision.

**User consequence** The user's most frequent decision produces no sense of
cause and effect. The product does not feel like one object.

**Underlying issue** Transitions are per-route fades (PER-08), so nothing
moves from where it was to where it went, and the list is rebuilt elsewhere
(PER-05) rather than updated in view.

**Recommended change** On choose, animate the recipe card from its position in
the sheet into the day slot (240ms, the sheet dismissing beneath it), let the
week re-flow in place, and show a two-word delta on the Shop tab badge
("+3 items"). Under reduced motion, cut to the final state and keep the badge
delta.

**Premium expression** Swapping a dinner feels like moving a plate onto the
table. The week accepts it, the list notices, and nothing else stirs. This is
the moment users would describe to a friend.

**Implementation surface** `src/ui/SharedElement.tsx` (new, on the View
Transitions API with a fallback), `src/features/plan/SwapSheet.tsx`,
`src/features/plan/PlanDay.tsx`, `src/components/TabBar.tsx` (badge delta).
Depends on PER-05 and PER-08.

**Acceptance** The chosen card is continuously visible from sheet to slot at
the phone size; the Shop badge shows the delta within 300ms; under reduced
motion the final state appears within one frame.

---

## 5. Systemic roots

| Root | Class | Findings | The one change | Lands in |
| --- | --- | --- | --- | --- |
| Configuration modelled as a prerequisite to value | Product model | PER-01, PER-03 | Default plan; preferences and saved recipes as inputs to the loop, not destinations | `src/features/plan/`, `src/routes.tsx` |
| Home is a module grid with no opinion | Product model | PER-02 | Tonight as the centre of gravity | `src/screens/Home.tsx` |
| Mutations are fire-and-forget: no optimistic state, no undo, no error recovery, no in-flight flag | System drift | PER-04, PER-05, PER-06, PER-09 | One `useMutation` with optimistic update, inverse, `isPending`, and `error`; one inline `UndoBar` | `src/lib/api/useMutation.ts`, `src/components/UndoBar.tsx` |
| One grouping primitive for every level of structure | System drift | PER-07a–d | `Section` for structure; `Card` for objects | `src/ui/Section.tsx`, `src/ui/Card.tsx` |
| Motion is uniform route decoration with no reduced-motion handling | System drift | PER-08, PER-10 | Motion tokens and a reduced-motion hook; one shared-element primitive for the swap | `src/styles/tokens.css`, `src/ui/SharedElement.tsx` |

---

## 6. Final synthesis

**What it feels like now.** A capable planner hidden behind a setup wizard,
a Home page that cannot decide what it is, and a set of interactions that
either ask permission or cannot be taken back. The bones are good; the product
does not yet trust itself.

**What it should feel like.** Opening Ladle is being told what is for dinner
by someone who knows you. The week is already there; changing it is a touch;
the list keeps up. Nothing is asked that the product could have known.

**The largest gap.** Value arrives after configuration instead of before it.
Every other weakness (the empty grid, the Settings detour, the equal-weight
Home) follows from a data model that will not render until it has been told
who the user is. Closing that gap changes the first minute, the return visit,
and the meaning of every preference control.

**Principles that should govern future decisions.**

1. Show a good default before asking a question; a preference is an
   adjustment to something visible, never a prerequisite.
2. Every change is immediate and reversible; confirmation is reserved for the
   one irreversible act.
3. Home has one centre of gravity, and it is tonight.
4. Structure is expressed by spacing and sequence; a border means "you can
   tap this".
5. Motion explains a change or does not happen.

**Highest-leverage systemic changes.**

1. The mutation primitive (PER-04, PER-05, PER-06, PER-09): four findings,
   one file, and it makes every future feature safe by default.
2. The default plan with inline adjustments (PER-01, PER-03): rewrites the
   first minute and deletes four screens.
3. `Section` and the motion tokens (PER-07, PER-08): quiet, cheap, and they
   make the signature swap possible.

**Signature opportunities.** The swap (PER-10): a recipe travelling from the
sheet into the day, the week re-flowing, the list noticing. Secondarily, the
first paint of a filled week for a user who has done nothing (PER-01) — the
illustrations arriving one by one over 400ms would be worth the exception to
principle 5.

---

## 7. Implementation sequence

| Step | Change | Resolves | Lands in | Acceptance |
| --- | --- | --- | --- | --- |
| 1 | Default plan on first arrival; preferences become inline adjustments; onboarding to one screen | PER-01 | `src/features/plan/`, `src/features/onboarding/` | Seven meals in the first paint of `/plan` for a new account |
| 2 | Home: Tonight full width, week row, streak to header, Discover/Community/Upgrade removed | PER-02 | `src/screens/Home.tsx` | "Cook tonight" in the first phone viewport |
| 3 | Mutation primitive: optimistic update, inverse, `isPending`, `error`; inline `UndoBar`; remove six confirmations | PER-04, PER-09, PER-05 | `src/lib/api/useMutation.ts`, `src/components/UndoBar.tsx`, `src/features/shop/buildList.ts` | Undo restores; failed save keeps the choice; checked items survive a swap |
| 4 | Button pressed and loading states driven by `isPending` | PER-06 | `src/ui/Button.tsx` | `ackMs` < 100; double tap produces one meal |
| 5 | Saved recipes as the first row of Swap; Saved tab removed | PER-03 | `src/features/plan/SwapSheet.tsx`, `src/routes.tsx` | Saved recipe appears first on every day |
| 6 | `Section` primitive; four surfaces de-nested | PER-07 | `src/ui/Section.tsx` | `maxNestDepth` 1 everywhere |
| 7 | Motion tokens, reduced-motion hook, route fade removed | PER-08 | `src/styles/tokens.css`, `src/app/Router.tsx` | `movesUnderReducedMotion` 0 |
| 8 | Shared-element swap with Shop badge delta | PER-10 | `src/ui/SharedElement.tsx` | Card continuous from sheet to slot |

**Bundles.** Steps 3 and 4 ship together (both depend on `isPending`). Step 1
and step 2 ship separately and are each walked before the next, because both
change the first-arrival journey and the review needs to know which one moved
it. Step 8 waits for 3 and 7.

---

## 8. Not reviewed

Tablet and large-desktop sizes (the product's traffic is 91% phone; the
tablet was spot-checked and is a stretched phone, which is a finding for a
later pass). The paywall and subscription cancellation (no fixture). Push
notification copy (device only). Field performance (no RUM access; `ackMs`
and `cls` are single lab runs). Contrast through the illustration overlays
(text over images is not measured by the walker; run `premium-calm`'s
measurement if it becomes a question). Defects seen and handed to QA: the
Saved tab's heart toggles twice on a fast double tap.
