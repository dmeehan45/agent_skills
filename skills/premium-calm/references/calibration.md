# Calibration — deciding what calm means for *this* product

Run this before measuring anything. Every later phase depends on it: the rubric
weights stay fixed, but what counts as a 5 does not.

Skipping calibration is how a premium-calm pass turns a dense professional tool
into a spa brochure. Linear, Aesop, Stripe, Calm, and Notion are all disciplined
premium-calm systems and they share almost no visual DNA. What they share is a
posture: emphasis is scarce, state is explicit, and nothing is left unresolved.

## The model

```
premium calm = clarity × restraint × responsiveness × continuity × trust
```

Multiplicative, not additive. A near-zero in any factor collapses the product.

| Factor | Holds when | Collapses when |
| --- | --- | --- |
| **Clarity** | Purpose, current state, and the next reasonable action are readable without inspecting every element | The user has to decode the screen before acting |
| **Restraint** | Emphasis is treated as a finite budget | Everything is emphasised, so nothing is |
| **Responsiveness** | Intent is acknowledged immediately; work completes predictably | The interface looks frozen while it thinks |
| **Continuity** | Objects, selections, scroll, and entered data survive transitions | Returning means starting over |
| **Trust** | Cost, policy, identity, security, and recovery surface before the user wonders | The user finds out after committing |

A beautiful screen that hides fees is not calm. A sparse screen that responds
slowly is not premium. A fluid transition that causes motion sickness is not
refined. An accessible form with vague error language still produces anxiety.

**Premium calm removes unresolved decisions, not visible elements.** Minimalism
deletes; calm resolves. A dense screen can be calm when information is grouped,
sequenced, and progressively disclosed. A nearly empty screen is not calm when
the primary action is ambiguous, the empty state offers no next step, or the
user cannot tell whether their last action worked.

## Step 1 — name the archetype

Calm expresses differently by product type. Pick the closest, or blend two and
say so.

| Archetype | Stakes concentrate at | Calm reads as | Biggest self-inflicted risk |
| --- | --- | --- | --- |
| **Transactional marketplace / commerce** | Payment, cancellation, refund | Total cost and policy visible before commitment; every transaction state named | Promotional surfaces outranking the task |
| **Professional / dense tool** | Destructive or irreversible operations, bulk edits | High information density with low visual noise; instant response; keyboard-first | Consumer-media polish that hurts scanning |
| **Financial / fintech** | Moving money, changing limits, identity | Predictable colour and form behaviour; explicit amounts and timing | Abstract brand visuals competing with financial clarity |
| **Health / regulated** | Recording, dosing, submitting, consent | Slow-and-certain over fast-and-clever; reversibility stated | Gamification that trivialises a serious act |
| **Content & media** | Subscription, cancellation, discovery | Editorial pacing; typography carries the hierarchy | Storytelling obscuring comparison and price |
| **Consumer wellbeing / habit** | Subscription, streak loss, personal data | Emotional tone set before task entry; low-pressure language | Calm visuals with a coercive cancellation flow |
| **Marketing / acquisition** | Signup, contact, purchase intent | One idea per section; one action per intent | Every section shouting equally |
| **Developer tool** | Deploy, delete, rotate credentials, migrate | Precision, honest progress, undo where possible | Decorative motion in a workflow measured in seconds |

Then write one sentence: *"For this product, calm means ___, and the moment
that most determines whether the user trusts us is ___."*

## Step 2 — map the stakes, and let them set priority

**Rank journeys by irreversibility, not by traffic.** The highest-traffic screen
is rarely the one that decides trust. Score each journey:

| Dimension | Ask |
| --- | --- |
| Irreversibility | Can the user undo this in one step, or not at all? |
| Money | Does value move? Can it move twice? |
| Data loss | Can entered work vanish on failure? |
| Identity and privacy | Is something exposed, shared, or verified here? |
| Consequence delay | Does the damage show up later, when recovery is harder? |
| Recovery cost | If it fails, is self-service repair possible? |

The journey scoring highest is the first redesign investment, whatever its
traffic. In the worked example it was booking → payment → confirmation. In a
deployment tool it is promote-to-production → rollback. In a records system it
is submit → amend → audit trail.

Produce an ordered list with a one-line reason each. That order drives the whole
change plan.

## Step 3 — inventory the signature assets, then reassign their roles

This is the move that keeps a premium-calm pass from erasing the brand. **The
assets usually stay; what changes is the job each one is allowed to do.** A
signature asset used everywhere is decoration; the same asset used at the moment
of commitment is a signal.

For each asset, fill in the reassignment:

| Signature asset | Currently used for | Reassign to | Now forbidden from |
| --- | --- | --- | --- |
| Accent colour | *(e.g. logo, chips, links, nav, banners, CTAs, all at once)* | Commitment, selection, focus, key availability, rare brand moments | Long text, ordinary metadata, every nav icon, decorative fills, multiple competing CTAs, disabled states |
| Dominant surface treatment | *(e.g. dark everywhere)* | The one mode it genuinely serves (usually immersive discovery or media) | Transactional and comparison surfaces, which need quieter ground |
| Container / card style | Wrapping everything | Grouping that spacing and typography cannot express alone | Nesting inside another container of the same kind |
| Imagery | Many small repeated thumbnails | Fewer, larger, decision-relevant images with consistent crops | Generic stock, aggressive overlays, inconsistent ratios |
| Type treatment | Many simultaneous styles | Six to eight semantic roles | Condensed metadata, extra-light body, uppercase runs |
| Navigation | Stable destinations | Stable destinations with platform-native state and back behaviour | Identical pixels across platforms |
| Market or positioning claim | Marketing copy only | Visible trust architecture in the product (verification, fees, policy, support) | Claims the interface never substantiates |

Record what must **not** change. A premium-calm pass that loses recognisability
has failed even if every score improves.

## Step 4 — differentiate the modes

Using one treatment everywhere makes a product visually consistent and
functionally undifferentiated. Assign each surface a mode, and let the mode set
the treatment:

| Mode | Posture | Treatment |
| --- | --- | --- |
| **Discovery** | Invite | May be immersive and image-led |
| **Comparison** | Inform | Structured, information-led, stable card templates |
| **Commitment** | Confirm | Quiet, explicit, operational; the accent appears here |
| **Management** | Orient | Status-led; the next required action leads |
| **Recovery / support** | Reassure | Plain language, preserved context, one safe next step |

Consistency lives in the token layer and the state machine, not in making every
mode look alike.

## Step 5 — set the bar and the constraints

Record before measuring, so the gate is not negotiated after the results arrive:

- **Rubric target.** Default: 85/100 before broad release, 90+ for flagship
  flows, zero S4, zero unresolved S3 on a critical path, accessibility ≥ 4/5.
- **Accessibility floor.** WCAG 2.2 AA; targets ≥ 44pt Apple / 48dp Android;
  reduced motion and reduced transparency honoured.
- **Performance budget.** Field p75: LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1.
- **Immediacy.** Visible acknowledgement of direct manipulation in ~100ms.
- **Platforms in scope**, and which are shared versus adapted.
- **Locked constraints**: brand assets that cannot change, framework and design
  system in use, release window, who approves.

## Output of this phase

A short calibration block at the top of the assessment:

```
Archetype:        Transactional marketplace, mobile-first
Calm means:       Cost and consequence are known before commitment
Highest stakes:   Payment authorisation (irreversible, money moves, async)
Journey order:    1 search→results→detail  2 booking→payment→confirm  3 trip management
                  4 save→return            5 host onboarding
Signature assets: accent lime → commitment/selection/focus only
                  dark shell → discovery and media only
Modes:            home=discovery  results=comparison  checkout=commitment
                  trips=management  support=recovery
Bar:              85 release / 90 flagship · zero S4 · a11y ≥ 4/5 · AA · 44pt/48dp
Must not change:  lime as the brand signature, five-destination nav, local payment methods
```

Every finding and every proposed change is judged against this block. If a
change improves a score but violates "must not change", it is not a candidate —
it is a separate conversation with the brand owner.
