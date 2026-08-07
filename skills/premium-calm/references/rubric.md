# The rubric, the severity model, and the release gate

Scored with `scripts/score_rubric.py`. Weights sum to 100 and do not change per
project — calibration changes what a 5 looks like, not what matters.

```
weighted score = criterion weight × score ÷ 5
```

## Criteria and weights

| Criterion | Weight | A five means | A zero means |
| --- | --- | --- | --- |
| `task-clarity` | 15 | Purpose, state, and next action are immediately evident | The user cannot determine what to do |
| `interaction-feedback` | 15 | Controls behave consistently; state and progress are explicit | Actions appear unresponsive or produce unexplained outcomes |
| `typography` | 10 | Strong hierarchy, comfortable measure, scalable text, readable metadata | Text is cramped, clipped, or undifferentiated |
| `color-contrast` | 10 | Accent is scarce and semantic; all states meet contrast requirements | Meaning depends on low contrast or colour alone |
| `spacing-density` | 10 | Grouping follows a stable rhythm; neither crowded nor wasteful | Arbitrary gaps and container clutter obscure structure |
| `accessibility` | 10 | Core tasks work with scaling, keyboard, screen readers, and accommodations | Users are excluded from essential actions |
| `motion-haptics` | 8 | Motion preserves context and respects preferences | Motion delays work, distracts, or causes discomfort |
| `imagery-materials` | 8 | Images aid decisions; material clarifies hierarchy | Imagery is generic, inconsistent, or competes with content |
| `microcopy-trust` | 8 | Prices, policies, states, and recovery are concrete | Copy is vague, coercive, or conceals consequences |
| `performance` | 6 | Responsive at p75 and appropriately native | Delays, layout shifts, or platform inconsistencies impair tasks |

## Anchoring scores to measured evidence

Score from the evidence, not from impression. These anchors keep two reviewers
within a point of each other; they are guidance, not arithmetic — a single
catastrophic failure can cap a criterion regardless of the other readings.

| Criterion | 5 | 3 | 1 |
| --- | --- | --- | --- |
| `task-clarity` | One dominant salience region, one primary-like action per viewport, squint reveals the intended order | 2–3 competing regions; the task is findable but not dominant | 4+ competing regions, or promotion outranks the task |
| `interaction-feedback` | Every control acknowledges in ~100ms; all transaction states named; no dead ends | Feedback exists but some states are implicit | Actions look unresponsive; pending and failed are indistinguishable |
| `typography` | 6–8 treatments, body ≥16px, measure ≤80 chars, scales cleanly | ~10 treatments, some tight metadata | Critical information at caption size; clipping at large text |
| `color-contrast` | Zero measured failures; accent scarce and semantic; no colour-only meaning | A few non-critical failures; accent slightly over-used | Failures on primary content, or selection carried by colour alone |
| `spacing-density` | On-scale throughout; nesting ≤2; grouping reads without containers | Mostly on-scale; some container compensation | Arbitrary gaps everywhere; card-in-card-in-sheet |
| `accessibility` | Zero contrast/target/focus failures; reduced motion honoured; non-colour cues throughout | Isolated failures on secondary paths | Essential actions unreachable by keyboard or assistive tech |
| `motion-haptics` | All durations within tokens; nothing moves under reduced motion; every animation justified | Some long transitions; motion mostly purposeful | Looping decoration; essential state shown only by movement |
| `imagery-materials` | Consistent ratios, reserved dimensions, ≤3 surface levels | Some ratio drift or an extra surface level | Layout shifts as media loads; glass over detail; generic stock |
| `microcopy-trust` | Cost, policy, state, and recovery concrete everywhere | Mostly clear; some generic labels | "Continue"/"Something went wrong"; fees revealed after commitment |
| `performance` | Field p75 within budget; no shift; input never blocked | Budget missed on one metric | Interaction latency causes repeat actions |

Record the evidence path for each score. A score with no evidence is an opinion
wearing a number.

## Interpretation bands

| Score | Meaning | Release implication |
| --- | --- | --- |
| 90–100 | Distinctive premium calm | Flagship quality; refine through measured use |
| 80–89 | Strong but uneven | Release only when critical paths score at least 85 |
| 70–79 | Functional, visibly inconsistent | Targeted redesign required |
| 60–69 | Noisy or friction-heavy | Do not position as premium |
| Below 60 | Systemic failure | Rework information architecture and foundations |

## Severity model

| Severity | Definition | Example | Required response |
| --- | --- | --- | --- |
| **S0** | Not a usability problem | Personal preference, no task impact | No action |
| **S1** | Cosmetic inconsistency | Radius differs slightly on a low-use card | Fix during routine polish |
| **S2** | Minor friction | Filter selection is harder to scan but usable | Schedule in the current cycle |
| **S3** | Major problem | User cannot tell whether a price is nightly or total | Fix before release of the affected path |
| **S4** | Critical failure | Duplicate-payment risk, inaccessible commitment control, lost data | Block release immediately |

Severity is about frequency, impact, and persistence — not about how ugly it is.
A quiet defect on the payment path outranks a loud one on a settings screen.

## The release gate

`score_rubric.py` exits `2` when any of these is unmet:

- Zero open **S4** findings.
- Zero open **S3** findings on a critical path (from calibration).
- Every surface scores **≥ 4/5 on accessibility**.
- Every critical-path surface scores **≥ 85/100**.

Flagship flows target 90+. The gate is checked per surface, not on the average —
an average hides the one screen where money moves.

## Review cadence

| Stage | Required review |
| --- | --- |
| Concept | Task hierarchy, information architecture, trust model |
| Component design | Tokens, states, accessibility, content rules |
| Prototype | Navigation continuity, motion, error recovery, large text |
| Development | Semantic implementation, platform behaviour, performance budgets |
| Pre-release | Full rubric, severity triage, assistive-technology test, slow-network test |
| Post-release | Field metrics, support themes, session evidence, experiment guardrails |

## Review checklist

| Question | Passing evidence | Failure |
| --- | --- | --- |
| Can a first-time user identify the screen's purpose and next action in two seconds? | One dominant task cluster, clear title | Promotion visually outranks the task |
| Is there one unmistakable primary action per decision region? | Secondary actions visibly subordinate | Two or three filled accent buttons compete |
| Does hierarchy survive squinting, grayscale, and reduced contrast? | Reading order apparent without the accent | Only the accent distinguishes selection |
| Is text readable and scalable without clipping? | Platform scaling and browser zoom hold | Price or policy truncates at large text |
| Do all meaningful states meet contrast requirements? | Token- and component-level checks pass | Disabled and secondary text illegible |
| Are targets ≥44pt / ≥48dp? | Automated and manual audit | Small save control needs precision tapping |
| Does motion explain change and respect reduced motion? | Alternative transition preserves meaning | Essential state shown only through movement |
| Does every action acknowledge input immediately? | Pressed or selected state within ~100ms | No response until the network returns |
| Are cost, terms, and consequences clear before commitment? | Final amount and terms sit beside the action | Fees appear only after commitment starts |
| Are entered data and selections preserved after errors? | Retry resumes with previous state | Timeout empties the form |
| Is every error recoverable and specific? | States explain effect and next step | "Something went wrong" dead end |
| Does keyboard and screen-reader order follow the visual task? | Logical focus, descriptive labels, announcements | Focus jumps behind an open sheet |
| Do images have stable geometry and sensible loading? | Reserved dimensions, responsive sources, relevant alt | Layout shifts as the gallery loads |
| Does each platform feel native without changing meaning? | Native navigation, shared terminology | One platform imitating another's back behaviour |
| Are edge states in the acceptance criteria? | Empty, loading, offline, timeout, reversal tested | Only happy-path mockups exist |
| Are field metrics collected for core interactions? | Performance, abandonment, recovery, conversion observable | The team relies on subjective polish reviews |

## Measuring the outcome, not just the artefact

Heuristic review finds consistency and standards problems efficiently. It does
not reveal mental-model or comprehension failures — those need usability
testing. Pair the rubric with:

| Dimension | Metric |
| --- | --- |
| Discovery clarity | Time to first meaningful interaction |
| Comparison quality | Detail-view rate, backtracking, repeated opens |
| Comprehension | Can users state the total, the terms, and what happens next? |
| Commitment efficiency | Completion rate, time, step abandonment, validation-error rate |
| Commitment trust | Retry rate, duplicate-attempt prevention, pending-resolution time |
| Post-commitment confidence | Support contact rate before the event, detail-retrieval success |
| Accessibility | Automated violations plus manual keyboard, screen-reader, scaling, contrast |
| Performance | Field p75 vitals; mobile launch, scroll, image, and interaction traces |
| Perceived calm | Post-task rating for clarity, confidence, effort, composure |
| System integrity | Token exceptions, one-off component count, state coverage |

Ask concrete questions, not abstract ones:

| Avoid | Ask instead |
| --- | --- |
| "Does this feel premium?" | "What makes this screen feel considered, or unfinished?" |
| "Is this calm?" | "Where did you feel uncertain, rushed, or overloaded?" |
| "Do you like the colour?" | "Which element did you believe was most important, and why?" |
| "Was checkout easy?" | "Before paying, what amount and terms did you expect?" |
| "Did the animation work?" | "Did anything move in a way that delayed or clarified your next action?" |
