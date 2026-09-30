# Product model, surfaces, and hierarchy

Phases 1 and 3 of the review. Phase 1 builds the model every later judgement
is made against; phase 3 uses it to decide what each surface is for and what
should dominate it.

## Why this comes first

A review that begins with the screens inherits the product's own assumptions:
that this screen should exist, that this step belongs here, that this feature
deserves the space it has. Premium products are opinionated about what matters,
and you cannot judge an opinion without holding one. Building the model first
lets you notice that the most polished screen in the product is one the user
should never have to see.

## Step 1 — infer the model

Answer every row from the product itself: its copy, its information
architecture, its flows, its data model, its onboarding, its pricing, its
empty states, its notifications. Read the code where the product is ambiguous;
the data model often reveals what the team believes the product is.

| Question | Where the answer usually hides | What a coherent answer looks like |
| --- | --- | --- |
| Who is the primary user? | Onboarding questions, pricing tiers, empty-state copy, the vocabulary of labels | One person, in one sentence, not a segment list |
| What situation makes them reach for it? | Notification copy, the first screen after launch, deep-link entry points | A moment, not a demographic: "Sunday evening, deciding what to cook this week" |
| What is the functional job? | The primary action on the home surface, the object the data model centres on | A verb and an object: "get a week of dinners onto the table" |
| What is the emotional job? | Tone of success states, what the product celebrates, what it never mentions | A feeling to reach or escape: "stop feeling like dinner is a daily failure" |
| What should be understood within the first minute? | The first screen, the first action's result | What this is, what it will do for me, what I do next |
| What is the shortest path to meaningful value? | Count the screens from launch to the first thing the user would keep | Steps today versus steps it could take if the system used what it knows |
| What is the primary recurring loop? | The home surface on a return visit, notification triggers, what accumulates | A cycle with a trigger, an action, and a reward the product can see |
| What would make someone return? | Streaks, saved state, scheduled content, social pull, accumulated value | Something the product has that the user cannot get by starting over |
| What would make someone call it unusually good? | Reviews, marketing claims, the team's own pride | A specific moment, not "it's easy to use" |
| Which parts are central versus incidental? | Navigation weight, code size, route count, analytics events | Central parts carry a job; incidental parts exist because they were buildable |

Write each answer as one sentence. Where the product gives two answers, write
both and mark the row ambiguous. Where it gives none, mark it missing.

**Ambiguity is a finding.** A product that cannot say who it is for, or whose
home surface serves three different loops equally, has a Foundational,
Product-altitude, Product-model-class problem, and every downstream finding
inherits it. File it first.

## Step 2 — decide what premium means here

Premium expresses differently by archetype. A dense professional tool made
airy is worse, not better; a consumer wellbeing product made dense is
frightening. Pick the closest archetype, blend two if necessary, and write one
sentence.

| Archetype | Premium reads as | The moment that decides trust | Self-inflicted risk |
| --- | --- | --- | --- |
| Consumer habit / wellbeing | Low-pressure language; the product remembers so the user need not; celebration proportionate to effort | Missing a day; cancelling | Gamification that shames; calm visuals over a coercive paywall |
| Consumer utility (planning, lists, money, home) | Value before configuration; defaults that are right; editing in place | The first time it is wrong | Settings as a substitute for good defaults |
| Content and media | Editorial pacing; typography carries hierarchy; nothing competes with the content | Subscription, cancellation, discovery of the next thing | Chrome that outshouts the content |
| Marketplace / commerce | Cost, terms, and timing known before commitment; every transaction state named | Payment, cancellation, refund | Promotion outranking the task |
| Social / messaging | Presence and state without noise; reversibility; who can see what is always clear | Sending something you cannot take back | Engagement mechanics over composure |
| Creative tool | Direct manipulation; the canvas is the interface; undo is total | Losing work | Feature exposure over facilitation |
| AI-assisted anything | What the system is doing and why is visible; generated is distinguishable from authored; autonomy has a leash | The first time the system acts without being asked | Magic that cannot be inspected or reversed |

Then write: *"For this product, premium means ___, and the moment that most
decides whether the user feels considered is ___."*

## Step 3 — record what must not change

The brand's signature assets, the interactions users already love, the
deliberate constraints (offline-first, no accounts, one-handed use), and any
locked decisions the owner has stated. The review does not file findings
against these. If a change would improve the experience but violates one, it
goes in the synthesis as a conversation for the owner.

Reassign before you remove. An accent used everywhere is decoration; the same
accent reserved for the moment of commitment is a signal. A signature
illustration on every screen is wallpaper; on the success screen it is a
reward.

## Step 4 — judge each surface by intent

Phase 3. For every major screen and state, in journey order, ask one question
first:

> **What is the user trying to accomplish at this exact moment?**

Write the answer in the hierarchy table before looking at the screen's
contents. Then evaluate the screen against it:

| Ask | The premium answer | The tell that it fails |
| --- | --- | --- |
| Is this screen necessary? | Yes, because the job cannot be done without a decision made here | It exists to hold a feature, a setting, or a step the system could infer |
| Does it appear at the right moment? | It appears when the user has the information and the motivation to act | Configuration before value; confirmation before understanding; a paywall before the first success |
| Does the most important thing carry the most emphasis? | One element is unmistakably first; everything else steps back | Several regions at equal weight; the primary action below secondary content |
| Does anything force the user to understand the product's internal structure? | The user never needs to know how the product is organised | Labels named after data models, tabs named after teams, a flow that mirrors the database |
| What could be removed, combined, deferred, automated, or inferred? | Every element survives that question | Fields the system could fill; choices with one sensible answer; steps that exist to confirm the previous step |
| Is the interface exposing features or facilitating the job? | The job's next step is the interface | A menu of capabilities where an action should be |
| Is the next action obvious without instructional text? | Yes; the layout tells the user | A sentence explaining what to click |
| Does the product preserve context and momentum? | The user arrives already oriented, and leaves with their state intact | A transition that resets scroll, selection, filters, or drafts; a modal that hides what the user was looking at |

Be willing to conclude that the screen, the step, the setting, the modal, the
navigation item, or the whole workflow should disappear. That is a Product
finding, and it is usually worth more than every Craft finding on the same
screen combined.

## Step 5 — assign the five roles

On each surface, every element gets exactly one role:

| Role | Definition | Treatment |
| --- | --- | --- |
| **Primary** | The one thing the surface exists for | The most space, the most contrast, first in reading and tab order; one per surface |
| **Secondary** | Supports the primary or is the likely next job | Present, clearly subordinate, never competing in size or colour |
| **Ambient** | Useful to glance at, never to act on here | Small, quiet, peripheral; a number in a header, a status dot |
| **Progressively disclosed** | Needed by some users some of the time | Behind a deliberate, discoverable gesture: expand, long-press, a "more" that names what it holds |
| **Removed** | Does not serve the job at this moment | Gone from this surface; possibly gone from the product |

Then compare with what the surface does today. The common failure is
**equal prominence**: every feature received a card, a heading, an icon, and a
colour, so the user establishes the hierarchy themselves on every visit. The
fix is a decision, not a restyle. Name the centre of gravity, and let
composition, spacing, typography, sequence, and interaction express it before
reaching for containers.

A calmer surface with one clear centre of gravity is almost always the result
of removing roles from elements, not of adding treatment to the primary.

## Output of these phases

Section 1 of the review (the model table, the premium sentence, "must not
change", and the ambiguities) and section 3 (the hierarchy table with
"should" and "is", and the centre-of-gravity notes). Both are written before
any finding, and every finding is judged against them.
