# Premium experience review — <product>

> Preserve this section order. Each section answers a question the next one
> depends on: what is this product for, how does it feel to use today, what
> should dominate each surface, what is wrong and why, what single changes
> resolve many findings, what it should feel like, and in what order to get
> there.

**Reviewed** <date> · **Build** <commit / version / environment> ·
**Scope** <whole product / journey / surface> · **Sizes** <phone, tablet, laptop, desktop> ·
**Evidence** <walked live / walked local build / source / screenshots — see finding-standard.md>

---

## 1. Product model

| | |
| --- | --- |
| Primary user | <who, in one sentence> |
| Situation | <what makes them reach for it> |
| Functional job | <what they are trying to get done> |
| Emotional job | <how they want to feel, or stop feeling> |
| First minute | <what must be understood, and whether it currently is> |
| Shortest path to value | <steps today → steps it should take> |
| Primary loop | <the recurring behaviour the product lives on> |
| Return trigger | <what would make someone come back> |
| Unusually good | <what someone would tell a friend> |
| Central | <the parts that carry the jobs> |
| Incidental | <the parts that exist but do not carry a job> |
| Premium means, here | <one sentence: what considered looks like for this archetype> |
| Must not change | <brand, signature interactions, deliberate constraints> |

**Ambiguities.** Where the product gives no coherent answer to the questions
above. Each of these is a candidate Foundational finding.

---

## 2. The current experience

**As a user lives it.** A narrative walk through the primary loop and the
first-arrival journey, in the user's situation, at the size they actually use.
What they see, what they decide, what they wait for, what they doubt.

**Strongest parts.** The decisions that are genuinely right and must be
preserved through everything below. Specific: which surface, which decision,
why it works.

**Weakest moments.** The three to five moments that most damage the feeling of
being considered, in order.

**Journey ledger**

| Journey | Reached | Sizes | Evidence | Verdict |
| --- | --- | --- | --- | --- |
| First arrival | yes / partial / no | phone, laptop | per-evidence/… | <one line> |
| First meaningful action | | | | |
| First successful outcome | | | | |
| Repeat use | | | | |
| Returning after time away | | | | |
| Changing or undoing | | | | |
| Missing information | | | | |
| Error | | | | |
| Empty state | | | | |
| Interruption and resumption | | | | |
| Mobile | | | | |
| <product's own journeys> | | | | |

---

## 3. Hierarchy by surface

One row per major surface. "Should" is your opinion; "is" is what the surface
does today.

| Surface | User is trying to | Should be primary | Is primary today | Secondary | Ambient | Disclosed | Remove |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |

**Centre of gravity.** For each surface where "should" and "is" differ, the
one-line reason, and the finding ID that resolves it.

---

## 4. Findings

### Ledger

| ID | Altitude | Priority | Class | Surface | Finding | Effort |
| --- | --- | --- | --- | --- | --- | --- |
| PER-01 | Product | Foundational | Product model | | | L |

Ordered by priority, then altitude (Product before Experience before Craft).

### Product-level

Changes to the product model, feature hierarchy, architecture, flows, or
fundamental approach. Full shape from `finding-standard.md` for every item.

### PER-01 — <title>

**Altitude** Product · **Priority** Foundational · **Class** Product model · **Effort** L
**Surface** <screen or state> · **Evidence** Walked — <capture>; Source — <file:line>

**Observation** …

**User consequence** …

**Underlying issue** …

**Recommended change** …

**Premium expression** …

**Implementation surface** …

**Acceptance** …

### Experience-level

Changes to journeys, screens, navigation, information architecture, state
management, content, and interaction patterns.

### Craft-level

Changes to composition, typography, spacing, responsiveness, transitions,
visual hierarchy, micro-interactions, motion, and detailed behaviour.

---

## 5. Systemic roots

Every underlying issue that produced more than one finding, and the single
change that resolves all of its instances.

| Root | Class | Findings | The one change | Lands in |
| --- | --- | --- | --- | --- |
| | System drift | PER-04, PER-09, PER-12 | | <primitive / token / pattern> |

---

## 6. Final synthesis

**What it feels like now.** <two or three sentences, honest>

**What it should feel like.** <two or three sentences, specific to this
product's jobs and archetype>

**The largest gap.** <one paragraph: the single distance that matters most>

**Principles that should govern future decisions.** Three to five, each one
sentence, each falsifiable.

1. …
2. …
3. …

**Highest-leverage systemic changes.** The two to four changes from section 5
that resolve the most findings per unit of work, in order.

**Signature opportunities.** The few moments where this product could do
extraordinarily well what competitors treat as ordinary, each tied to a
finding or a primitive, none manufactured.

---

## 7. Implementation sequence

Structurally better before cosmetically better. Each step names the findings
it resolves, the primitive it lands in where one exists, and how to know it
worked. Steps are ordered so that later steps inherit earlier ones.

| Step | Change | Resolves | Lands in | Acceptance |
| --- | --- | --- | --- | --- |
| 1 | | PER-01 | | |
| 2 | | | | |

**Bundles.** Changes that should ship together because they touch the same
primitive, and changes that must not ship together because they would hide
which one moved the experience.

---

## 8. Not reviewed

States not reachable, platforms not tested, authenticated areas without
access, field performance not measured, defects seen and handed to QA. An
unlabelled gap reads as a pass.
