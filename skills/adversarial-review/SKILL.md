---
name: adversarial-review
description: >-
  Adversarial review of a Satsang surface from the perspective of the toughest
  parent, investor, designer, and clinician. Use when pressure-testing or
  hardening a surface: a marketing page (home, about, approach, a comparison
  page, the quiz funnel, refer-a-friend), or a product surface (onboarding, the
  paywall and upgrade sheet, Talk, Tools, Plans, Reflections). It finds the
  prioritized reasons the surface fails a sharp reader, traces each to a root
  cause, weighs candidate fixes, picks one, and closes the gap in the source. It
  attacks positioning, proof, persuasion, and duty of care, the strategic
  failures the other skills do not catch. Defers voice to
  satsang-writing-style-guide.md and content-rigor, UI to
  satsang-design-system.md and frontend-polish, claim truth to content-rigor,
  and the AI's live conversational behavior to the harness and evals
  (change-pass, eval-changeset, docs/governance, docs/safety). Not for the
  model's turn-by-turn output; review that with the eval loop.
---

# Adversarial review (Satsang)

This skill runs a hostile but fair review of a surface and then closes the gaps
it finds. It plays the four readers who decide whether the product wins: the
parent who has to trust it in a hard moment, the investor who has to believe the
value lasts, the designer who has to be convinced the surface works, and the
clinician who has to find it responsible. Each attacks a different surface.
Together they answer the only question that matters: would this survive the
sharpest version of the person it is written for.

The repo already holds reviews at the caliber this skill is meant to produce.
Read one before you start: `qa/landing-design-critique-2026-04-27.md` (the
AI-tell inventory plus bold directions), `qa/pro-ux-craft-audit-2026-05-28.md`
(what a designer with an opinion would add), and `qa/marketing-ux-pro-pass-2026-05-28.md`
(recommendations with a shipped-status table). Note their shape: a verdict up
front, each finding grounded in a heuristic or the site's own standard rather
than taste, the cheapest high-leverage fixes named first. Those docs are strong
on craft. This skill extends the same discipline to the layers they leave out,
positioning, proof, persuasion, and duty of care, and it ships the fix.

The output is not a critique for its own sake. It is a prioritized set of
findings, each mapped to a chosen solution, applied to the source, verified, and
handed over on a preview. Review, then remediate.

A note on the name. The repo is `satsang-dev` and code identifiers say
"satsang", but the live user-facing brand is currently "Avani" (admin
configurable via the branding row), and the docs still say "Sage". That drift is
itself a reviewable finding (section 2). Throughout this skill, "the product"
means the app whatever it is currently branded.

## 0. Scope. What this reviews, and what it defers

Use this on any surface that has to win or keep a parent. Two families:

- **Acquisition and story surfaces.** `/` (LandingPage), `/about`, `/approach`,
  the comparison pages (`/how-different-from-chatgpt`,
  `/how-different-from-good-inside`), the quiz funnel (`src/pages/quiz/`),
  `/refer`, `/privacy`, `/security`, and the editorial content (`/articles/:slug`,
  `/moments/:slug`).
- **Product and experience surfaces.** Onboarding (`OnboardingIntroPage`,
  `src/features/onboarding/`), the paywall and upgrade sheet
  (`src/paywall/`, `src/components/satsang/UpgradeSheet.tsx`), Home and Talk
  (`SatsangHomePage`, `TalkPage`), Tools, Plans, Reflections, and the shared
  chrome. It reviews a whole surface as an argument or an experience aimed at a
  parent, not a paragraph in isolation.

It owns the strategic layer the other skills do not: is the value proposition
clear and differentiated against the alternatives the parent already holds
(ChatGPT, a parenting book or membership like Good Inside, a friend, a therapist,
or doing nothing); is every claim proven; does the surface earn trust before it
asks for the first message; does the investor see something that lasts once
intelligence is cheap; does a parent in an acute state know in five seconds what
this is and whether it is safe for their family; is the surface responsible.

It defers the layers the other skills and standards already own, and routes
fixes to them rather than restating their rules.

- Voice, punctuation, and the AI-tell bans: `docs/satsang-writing-style-guide.md`
  (marketing, articles, long-form) and Section 2 of `docs/satsang-design-system.md`
  (in-product microcopy). This skill flags that a line does not make the case; the
  writing guide governs whether the line is on-voice.
- Whether a claim is true and traceable: the `content-rigor` skill. This skill
  flags that a claim is unproven to the reader; content-rigor governs whether it
  is sourced at all.
- Visual design language, layout, motion, imagery, the conversation UI:
  `docs/satsang-design-system.md` and the `frontend-polish` skill.
- Functional, interaction, responsive, and mobile behavior: the Playwright
  suites (`npm run test:mobile`) and the mobile QA notes in `qa/mobile-*.md`.
- **The AI's live conversational behavior**, what the assistant actually says
  turn by turn, its persona, pacing, and safety at runtime: the behavior harness
  and the eval loop, not this skill. That is `change-pass`, `eval-changeset`,
  `docs/governance/`, the safety stack in `src/lib/ai/safety/`, and
  `docs/safety/trust-and-safety.md`. This skill reviews the surface and the
  promises it makes about the AI; it does not grade a transcript.

If a finding is really a voice, UI, functional, sourcing, or model-behavior
defect, name it, then hand the fix to the owner. This skill catches the failure
those owners, run in isolation, miss: a surface that is clean, accessible,
on-brand, sourced, and functional, and still does not make the case, or makes a
case it has no right to make.

## 1. The method, and the one rule under it

The method is red-team tradecraft pointed at a surface. Assume it has already
failed, enumerate the competing reasons why, attack the strongest version rather
than a weak one, and rank the reasons by what disconfirms them. Then map each
surviving reason to a fix and close it.

The one rule under all of it: **a finding that is not falsifiable is not a
finding.** Generic critique ("this could be stronger", "the messaging feels off",
"consider adding social proof") is the failure mode of every persona review and
of every model asked to role-play a critic. It sounds like work and points at
nothing. Every finding this skill emits names the exact element, makes a claim
that could be wrong, and carries a test that would settle it. If it cannot, cut
it. And if a surface is genuinely strong on a lens, say so and move on. Finding
nothing real beats inventing something plausible.

## 2. The two anchors that keep the review honest

These are the anti-slop core. Skip them and the review degenerates into fluent,
confident, unfalsifiable role-play.

**Anchor one: hold the surface to two references at once.** Outside best practice
(the frameworks in the Sources section) and the product's own written standards.
The second is the sharper blade. When a surface breaks a rule the product itself
preaches, that is not opinion, it is the product failing its own bar. The writing
guide bans the em dash and the dramatic-reveal colon app-wide, so either on a
page is a finding. The design system fixes the palette and type, so an off-token
accent is a finding. And the product's own copy sets internal facts that must
agree with each other. Real examples of internal incongruence found in this repo:
the landing copy says "no card to start" while the Stripe upgrade sheet takes a
card up front; the README says "Sage" while the app renders "Avani"; the quiz
calls itself "science-backed" with no study behind it. Internal incongruence is
the most defensible critique you can make, because the standard is already agreed.

**Anchor two: every finding is a falsifiable claim tied to a quoted element and a
test.** Before a finding ships it passes four checks.

1. **It quotes the exact element.** The headline text, the CTA label, the claim,
   the section, with its `file:line`. Marketing copy often lives in
   `src/lib/i18n/keys.ts` (the English source of truth) rather than the TSX, so
   quote the key and its value. Not "the hero", not "the messaging".
2. **It makes a claim that could be false.** "This headline would sit unchanged on
   a generic wellness app" is testable. "This headline is weak" is not. "No number
   or named source proves the science-backed claim" is testable. "The proof feels
   thin" is not.
3. **It names the test that settles it.** The five-second test, "name the one
   proof point that earns this line", "name the alternative this surface beats and
   why", a specific Nielsen heuristic, the duty-of-care check, or the pre-mortem.
4. **It is attributable to one persona's specific stake.** If any of the four
   personas could have said it, it is generic. Reject it and find the version only
   the parent, or only the investor, or only the designer, or only the clinician
   would raise.

## 3. Assemble the ground truth first

You cannot attack a value proposition you have not pinned down. Before the first
critique, read enough to state, in your own words, what this surface claims, who
it is for, and what it wants the reader to do. Read:

- The surface component in `src/pages/` (or `src/features/`) and the copy it
  pulls from. Most user-facing strings resolve through `src/lib/i18n/keys.ts`;
  read the keys, not just the JSX.
- The offer, which has **no single source of truth** and is spread across at
  least: the price strings in `src/lib/i18n/keys.ts` and the nine locale catalogs
  under `src/lib/i18n/translations/`, the JSON-LD price in `src/lib/seo.ts`, the
  quota and trial length in Supabase `runtime_config` (surfaced via
  `/api/billing?action=paywall-config`), the gating in `src/paywall/config.ts`
  and `entitlements.ts`, and the referral discount in `ReferAFriendPage.tsx`. Any
  disagreement among these is a finding on its own.
- The positioning spine: `README.md`, `docs/brand-name-research.md` (the naming
  and positioning decisions), and the "architecture" section of `ApproachPage`
  (the governed-harness and eval claims).
- The competitive frame: the two comparison pages name the alternatives the buyer
  is weighing (ChatGPT, Good Inside / Dr. Becky). Read them so you know what the
  product claims to beat.
- The route's SEO title and description (`src/lib/seo.ts`, `SeoHead`): they are
  the promise a searcher clicks, and they should match what the surface delivers.

Write the one-sentence version of what the surface does before you tear into it.
If you cannot, that is the first and largest finding, and it belongs to the parent.

## 4. The four lenses

Each persona attacks a different surface with a different question bank and a
different kill criterion. Run them one at a time so each stays in character and
the coverage stays broad. Do not blend them into a single voice.

### 4a. The parent. Would I trust this, in the state I am actually in

Stake: the ICP is a parent in an acute, emotionally loaded moment, reading at
9:47pm after a hard hour, defensive, low on patience, and holding a standing set
of doubts. They are the buyer and the user at once. They run every line through
"so what" and "prove it", and they are looking for a reason to close the tab.

Question bank.
- Five-second test, under stress. From the hero alone, can a first-time parent
  say what this is, who it is for, and why it is for them right now. The
  activation chips ("I yelled", "My child is melting down") exist for exactly this
  reader; do they lower the activation energy or add a step (Fletch, StoryBrand
  grunt test).
- The struggling moment. Does the surface open on the parent's real push, the
  moment their current way stopped working, in their words, not ours. Is the cost
  of the hard hour made visible without shaming them (Jobs to Be Done, four
  forces).
- Trust before the ask. This product asks a parent to type "the moments with your
  kids you would never put in a public chatbot". Does the surface earn that trust,
  privacy, a real person behind it, safety, before it asks for the first message,
  or does it ask first and reassure later. Privacy is load-bearing to the whole
  pitch, so a privacy promise buried below the composer is a finding.
- So what. Does every capability tie to a value the parent recognizes, or does the
  surface stop at what we do. "We remember across sessions" is a feature; "you
  never have to re-explain your kid at the worst moment" is the value (Dunford,
  Fletch capability versus benefit).
- Prove it. Does every value claim have a proof point at the point of the claim, a
  named therapist, a real mechanism, a specific before-and-after. An unproven
  claim adds doubt, it does not add value (Dunford, MECLABS credibility).
- The alternative. Does the surface imply what the parent would use instead, and
  why this beats it: the free ChatGPT on their phone, a parenting book or a Good
  Inside membership, a friend, a therapist, or nothing. A surface that names no
  alternative cannot establish that it is different (Dunford, the comparison
  pages).
- The objections. Are the standing ones defused: too expensive ($24.99/month, is
  the value tied to it), won't work for my kid or my situation, I don't trust AI
  with my family, is this safe, what happens to my data, not now. Which does the
  surface answer, and which does it dodge.

Kill criterion. The parent stays, and types the first message, when the surface
names their moment, earns trust before the ask, ties every claim to a proof they
can check, implies the alternative it beats, and answers the objection they walked
in with. Short of that, they close the tab.

### 4b. The investor. Does the value last, and is it big enough

Stake: would a sharp, skeptical investor back a company that sells this. They
read for durable advantage and grade claims by evidence, not excitement. This is a
consumer AI subscription, so the questions bite hard.

Question bank.
- In one plain sentence, with zero marketing-speak, what does this do and for
  whom. A grandiose or decode-me sentence is the tell (Graham).
- Once intelligence is cheap and a general model can role-play a warm coach, what
  does this own that is scarce. The product's own answer is the governed harness,
  Mirra's clinical method, a 100-plus-case eval suite, cross-session memory, and a
  trusted brand. Does the surface show that as hard-won specificity, or assert it
  as generic optimism (the product's own thesis on `ApproachPage`).
- Why now. What shift makes this the moment, and why do parents adopt an AI coach
  now when they would not have before. A surface with no "why now" reads as
  timeless, which reads as untethered (Sequoia, a16z, the idea maze).
- Retention and the acute-need trap. A tool a parent reaches for only in crisis
  gets used rarely and churns. Does the surface show a reason to return between
  crises (reflections, plans, memory, the wider arc of family life), or is it a
  fire extinguisher with a monthly bill (engagement and cohort logic, Ulwick
  outcome metrics).
- Feature or company. Could an incumbent (a general model with a parenting mode, a
  Good Inside with an AI bolt-on) copy the visible part in a quarter. What survives
  that, and does the surface show it (Andreessen on moats, vaporware skepticism).
- Where is the proof of durable value. A retention curve, a real outcome, a
  clinician who stands behind the method, or is it assertion (Gurley on
  unsubstantiated size, grade by evidence).
- Unit economics. A $24.99 subscription against per-conversation model cost and a
  7-day trial: does the surface's promise (unlimited, always-on, ZDR-tier
  inference) square with a business that makes money, or does it promise a cost
  structure that does not close.

Kill criterion. The investor leans in when the surface names one scarce,
defensible thing the company owns, shows a reason parents stay and return, and
proves durable value with something a reader can check. Short of that, they pass.

### 4c. The designer. Does the surface work and communicate

Stake: an exacting designer judging whether the surface communicates and
converts, not whether it is pretty. This is a mobile-first product, so the
judgment is a phone judgment. Ground every comment in a heuristic, a stated
objective, or evidence, so a defect is separable from a preference. "I do not like
it" is not a finding; a violated heuristic is (Nielsen, and the crit discipline
from Discussing Design). Route pixel-level and token-level fixes to
`frontend-polish` and `docs/satsang-design-system.md`, and functional defects to
the mobile QA suite; this lens owns whether the surface's structure makes the
argument land.

Question bank.
- Hierarchy, on a phone. Does the eye land on the one claim and the one action
  first, or does the surface compete with itself. One primary action per view
  (Nielsen 8, aesthetic and minimalist; the design system's surface language).
- The five-second read, visual version. Squint. Do the headline, the proof, and
  the primary action survive, or does the message drown in equal-weight blocks.
- Match to the reader's world. Is the language the parent's, not ours. Does a label
  or an abstraction make them translate (Nielsen 2).
- The cognitive walkthrough of the primary path (land, understand, act, and for a
  product surface, the first-run and the empty state). At each step: will the
  parent try the right action, see it is available, connect it to what they want,
  and get feedback that they progressed.
- The AI-tells and the missing craft. The repo has a running audit of the
  calm-therapeutic-AI uniform (`qa/ai-tells-audit-2026-05-28.md`) and a craft-signal
  pass (`qa/pro-ux-craft-audit-2026-05-28.md`). Does this surface carry the tells
  (templated eyebrow over every section, identical cards, an icon in a tinted
  square, motion with no job) or the craft (one strong gesture per scroll,
  typography set on purpose). Route the fixes to `frontend-polish`, but name them
  here when they cost the argument.
- Consistency. One CTA label per intent across the surface, one accent, one voice.
  Two labels for the same action is a defect (Nielsen 4).
- Trust through craft. Do the proof elements (the founder, the before-and-after
  stories, the privacy section) read as real and specific, or as decoration a
  skeptic discounts.

Kill criterion. The designer signs off when a distracted parent, on a phone, in
one squint, gets what it is and what to do, the primary path walks cleanly
including its empty and error states, and the proof reads as real. Short of that,
the craft is undercutting the claim.

### 4d. The clinician. Is this responsible, and honest about what it is

Stake: a licensed family clinician judging whether the surface is safe and honest
for a vulnerable reader. This is the lens the other three miss, and for a
parenting and wellbeing product touching mental health, partners, and children, it
is the one with the most exposure. It owns the surface's promises and framing, not
the model's runtime behavior (that is the safety stack and the eval loop). But a
promise the product cannot keep, or a boundary the surface blurs, is this lens's
finding.

Question bank.
- Overclaim. Does the surface claim or imply therapy, diagnosis, treatment, or a
  guaranteed outcome. The product's own position is that it "does not lecture or
  diagnose" and routes out to human professionals for anything clinical; a surface
  that promises more than coaching breaks that boundary and invites both distrust
  and liability.
- Honest proof. Are the credential and popularity claims true, current, and
  consistent across surfaces: "a licensed therapist with 15 years", "over 100,000
  parents follow her work", "a 100-plus-case evaluation set", "more robust and
  reliable than AI companions", "science-backed". Anonymous "Mom of two"
  testimonials and a follower count are not evidence of efficacy; does the surface
  present them as vibe or as proof (content-rigor owns the sourcing; this lens owns
  whether the framing is honest to a vulnerable reader).
- Duty of care at the moment of distress. If a parent lands here in crisis, is
  there a visible, appropriate path (the crisis resources card, the route-out),
  or does the surface only sell. Crisis copy aligns to SAMHSA and WHO safe
  messaging (`docs/safety/trust-and-safety.md`); a surface that could be a
  vulnerable parent's entry point should not dead-end them.
- Privacy honesty. The privacy promise is a clinical-trust promise here. Does the
  surface's claim ("we never sell your family's story", "nothing you share trains
  an AI", ZDR) match the actual data posture (`docs/subprocessors.md`, the safety
  doc). A privacy overclaim is both a trust and a legal failure.
- Respect for the reader's state. Does the surface speak to a parent in shame
  without adding to it (the product's "compassion, shame-free" pillar), or does it
  imply they are failing. Fear-based conversion copy on a mental-health-adjacent
  product is a duty-of-care finding, not a growth tactic.
- Children as subjects, not users. The product's posture is COPPA-aligned:
  children are subjects of conversation, not users. Does any surface blur that
  (implying it is for the child, collecting a child's data as a user).

Kill criterion. The clinician signs off when the surface promises only what the
product can stand behind, presents proof honestly to a vulnerable reader, keeps
the not-therapy boundary and the crisis path visible, and speaks to a struggling
parent without shaming them. Short of that, the surface is a responsibility risk,
whatever it does for conversion.

## 5. Run the review

1. **Pre-mortem first.** Before any lens, fix the failure in place. "It is ninety
   days out. This surface shipped and failed. The parent left in five seconds, the
   investor passed after one read, nobody upgraded, and one vulnerable parent had a
   bad experience. Write the reasons." Imagining the failure as already certain
   surfaces materially more concrete causes than asking what might go wrong (Klein,
   HBR). List them before you judge them.
2. **Run each lens in character.** Parent, then investor, then designer, then
   clinician. For each, walk the question bank against the real surface and
   generate findings. Stay in one voice at a time.
3. **Steelman before you attack.** For each candidate finding, first state the
   strongest version of what the surface is doing right there. If the strong
   version holds, drop the finding. Attack only what survives its own best case.
4. **Write each finding in the format below.** Then rank them (section 6) and map
   them to fixes (section 7).

Finding format. Every finding carries these, or it is not done.

- **Lens and severity.** Which reader raised it, and High, Medium, or Low
  (section 6).
- **The element.** The quoted text or the specific component, with `file:line`
  (and the i18n key, if the copy lives there).
- **The objection.** What this reader concludes and why, in their voice, as a claim
  that could be false.
- **The test.** How to confirm the defect is real. One of the tests from the lens.
- **Root cause.** The changeable design cause, via section 7.
- **The fix.** The chosen solution and how we will know it worked.

## 6. Prioritize

A flat list is not a review. Rank so the output is a fix order.

Severity, by what the finding costs.

- **High, blocking.** Costs the conversion, fails the diligence, or is a
  responsibility risk. Examples: a hero that does not say what this is and for
  whom, a load-bearing claim with no proof, positioning that would sit unchanged on
  a generic wellness app, the primary objection unanswered, the offer contradicting
  itself across the mirrors, a clinical or privacy overclaim, a crisis dead-end, a
  broken primary path. Do not ship to prod with one open.
- **Medium, should fix.** Weakens the surface but a motivated parent gets past it.
  A capability with no "so what", a soft comparative where a real proof exists, a
  missing alternative, a second-order objection unanswered, a hierarchy or
  heuristic violation that adds friction, a retention story left implicit.
- **Low, polish.** Costs a little trust or momentum. A slightly generic line, an
  overused eyebrow, a minor motion or spacing nit that undercuts the claim.

Then order the fix work by impact over effort, so cheap high-leverage fixes go
first (RICE or ICE if you want the number). A High-severity finding that is a
one-line headline rewrite outranks a Medium that needs a new section. Keep
severity (how bad) separate from fix order (what to do first).

Emit a scorecard.

| # | Finding | Lens | Severity | Direction of fix |
|---|---------|------|----------|------------------|

## 7. Map to a root cause, then choose the best fix

Do not jump from symptom to the first fix that comes to mind. That is how a
surface gets a band-aid on a broken value proposition.

1. **Trace to a changeable root cause (5 Whys).** Chain "why" from the symptom to a
   cause you can change in the source. "Nobody upgrades, because the parent never
   reaches the upgrade sheet, because they bounce in the hero, because the headline
   states a feeling not a moment, because we led with aspiration over the job."
   Stop at a design cause ("we led with aspiration"), never at a person. If the
   chain branches, note both.
2. **Generate at least two candidate fixes, each steelmanned.** State the strongest
   case for each before comparing. Do not anchor on the first.
3. **Score the candidates and pick.** Weigh each on impact on the objection, effort,
   fit with the house voice and design system, and reversibility. Prefer the fix
   that closes the objection at the lowest cost and lowest risk. Say why the winner
   won.
4. **State how you will know it worked.** Re-run the lens that raised the finding.
   The fix is done when that reader's kill criterion is met, not when the words
   changed.

## 8. Close the gap

Apply the chosen fix to the source, then verify. This is where the review becomes
an improvement.

- **Route the edit to the owner.** Copy follows `docs/satsang-writing-style-guide.md`
  (and design-system Section 2 for in-product microcopy); run the voice pre-flight
  on every line you rewrite. A UI or layout change follows
  `docs/satsang-design-system.md` and `frontend-polish`. A functional change is
  checked against the mobile QA suite. A new or reworded claim has to clear
  `content-rigor` before it ships; do not fix a "prove it" finding by inventing a
  number, a study, or a clinical claim. A safety or crisis or medical-boundary
  change follows `docs/safety/trust-and-safety.md`. If the fix changes anything
  the AI actually says at runtime, that is not a source edit here, it is a change
  to the behavior harness (`change-pass`, then `eval-changeset`); route it there.
- **Keep the offer in sync.** Because there is no single offer file, an offer or
  price change must update every mirror in the same commit: the price strings in
  `src/lib/i18n/keys.ts` and all nine locale catalogs, the JSON-LD in
  `src/lib/seo.ts`, the hardcoded copy in `scripts/prerender-articles.mjs`, and
  the docs, plus the `runtime_config` quota and trial values and the Stripe price
  where relevant. A resolution that leaves them disagreeing is a new bug.
- **Checkpoint before large or positioning-level edits.** A headline rewrite, a new
  value proposition, a change to what the company claims to be, a change to a
  clinical or privacy claim, or anything that restates positioning is David's call.
  Present the findings and the recommended fixes, get direction on which to close,
  then edit. Do not silently rewrite the positioning of a live surface. Mechanical
  and Low-severity fixes can be applied directly and shown in the diff.
- **Verify.** `npm run typecheck` and `npm run build` are green (the build runs the
  prerender step; it no-ops cleanly without Supabase env). The voice scan is clean
  on changed copy: the em dash is banned app-wide, so
  `rg -n "—|–" src/lib/i18n public/content` should return no hits on lines you
  touched, and run the AI-tell pass from the writing guide. `npm test` is green if
  you touched anything a contract test covers. Walk the surface at 360px if you
  touched layout. The lens that raised each closed finding now passes its kill
  criterion.
- **Preview, then approval.** Push to the feature branch, confirm the Vercel
  preview reaches READY, share the URL, and let David QA before anything reaches
  `main`. Never self-merge. This is the house workflow and it holds here.

## 9. The review report

Deliver the review in a shape that reads as a judgment, not a list, matching the
`qa/` critique docs.

1. **Verdict up front.** One line: **ship**, **harden**, or **rebuild**, plus the
   count of High-severity findings. "Harden. Three blocking, five should-fix."
2. **The short version.** A paragraph on the single biggest reason the surface does
   or does not make its case, named plainly.
3. **The scorecard** (section 6 table).
4. **The findings**, grouped by severity, each in the finding format, each
   steelmanned before it is attacked.
5. **What I would change first.** The cheap, high-leverage fixes, ordered. This is
   the section that turns a critique into a plan.
6. **What is already strong.** Name what survived all four lenses. Credit is not
   padding; a review that only finds fault reads as a model performing critique, and
   it hides where the real leverage is.
7. **The standards and methods the review leans on**, so each finding traces back to
   a rule or a framework, not to taste.

Offer to save a substantial review to `qa/<surface>-adversarial-review-YYYY-MM-DD.md`,
matching the `qa/` naming, when it is worth keeping as a record.

## 10. Anti-slop guardrails for the reviewer itself

The reviewer is a model asked to role-play four critics, and that is exactly the
setup that produces fluent, sycophantic, unfalsifiable output. Hold yourself to
these or the whole skill becomes theater.

- **Every finding passes the four checks in section 2.** Quoted element with
  `file:line`, falsifiable claim, named test, one persona's specific stake. No
  exceptions.
- **Reward finding nothing.** If a lens finds no real defect, say so. Never
  manufacture a finding to look thorough. An invented problem wastes a real fix
  cycle and erodes trust in the next review.
- **Steelman at full strength before every attack.** A finding that only beats a
  weak reading of the surface is not a finding.
- **At most one sharp contrast per lens.** Make the positive case for the fix. Do
  not build the review out of "unlike a weaker app" framing.
- **Do not fabricate the ammunition.** No invented competitor line, benchmark,
  study, statistic, or user quote to make a finding land. This matters double on
  the clinician lens: do not invent a clinical fact to argue a clinical finding. If
  the evidence would need to be real, go find it or mark the finding as needing it
  (the content-rigor bar).
- **Separate defect from taste.** If a finding is really "I would have done it
  differently", cut it. Keep it only if it ties to a heuristic, a stated objective,
  or the product's own standard.
- **Keep the personas distinct.** If two lenses raise the same finding, it is either
  genuinely cross-cutting (say so once) or one of them is generic (cut it).
- **Practice the voice you review.** Write the review itself without em dashes or
  dramatic-reveal colons. A review that breaks the house voice rules while enforcing
  them has no standing.

## 11. Pre-flight before a review is done

- [ ] Ground truth stated: the surface's one-sentence claim, its parent, its wanted
      action, written down before critiquing.
- [ ] Pre-mortem run before the lenses.
- [ ] All four lenses run in character, each against its full question bank.
- [ ] Every finding passes the four checks: quoted element with `file:line` (and
      i18n key where relevant), a falsifiable claim, a named test, one persona's
      specific stake.
- [ ] Every finding was steelmanned before it was attacked.
- [ ] Findings held to the product's own standards, not only outside best practice.
      Internal incongruence findings cite the rule or the mirror they break.
- [ ] Each finding is severity-rated, and the fix work is ordered by impact over
      effort.
- [ ] Each finding traces to a changeable root cause, with at least two candidate
      fixes weighed and one chosen for a stated reason.
- [ ] Each chosen fix names how the lens will confirm it worked.
- [ ] Applied fixes routed to the owning skill or standard; any runtime-behavior fix
      routed to the harness (change-pass, eval-changeset), not applied as copy; offer
      changes mirrored across every price and quota source.
- [ ] Positioning-level, clinical, and privacy edits checkpointed with David, not
      applied silently.
- [ ] What is already strong is named.
- [ ] Verified: typecheck and build green, `npm test` green if touched, voice scan
      clean on changed copy, kill criteria met.
- [ ] Shipped to a preview and handed over before `main`.

## 12. How this fits the other skills and the workflow

- `frontend-polish` and `docs/satsang-design-system.md` build and guard the UI a
  surface sits in. `content-rigor` guards whether its claims are true and sourced.
  The behavior harness (`change-pass`, `eval-changeset`, `docs/governance/`,
  `docs/safety/`) governs what the AI actually says. This skill sits above them and
  asks a different question: does the surface win and keep a parent, survive the
  investor, and stay responsible. A hard finding usually routes its fix down into
  one of those owners.
- The `qa/` critiques (`landing-design-critique`, `pro-ux-craft-audit`,
  `marketing-ux-pro-pass`, `ai-tells-audit`) are the design-and-craft ancestors of
  this skill. Read them for caliber and continuity, and continue their numbering
  and voice when you save a review.
- Run this skill after a surface is built and before it is called done, and again
  when a surface has been live a while and the sell or the trust has gone stale. It
  is a hardening pass, not a first draft. For the AI's conversational quality, use
  the eval loop, not this skill.
- The house workflow is unchanged. Preview before prod, David approves the
  promotion to `main`. A review that ends in a merged change without a preview has
  skipped the gate.

## Sources. The methods this skill adapts

Established frameworks, held here as the outside reference the review
triangulates with the product's own standards. The internal standard is usually
the sharper blade; these keep the review anchored to practice beyond our own
walls.

- Red-team tradecraft. Richards Heuer, *Analysis of Competing Hypotheses* and
  *Psychology of Intelligence Analysis* (rank explanations by what disconfirms
  them); the CIA *Tradecraft Primer* Key Assumptions Check and "What If?" analysis;
  Rapoport and Dennett on steelmanning; devil's advocacy against groupthink
  (Janis). Modern practice: red and blue teaming, and AI red-teaming at Anthropic,
  OpenAI, and NIST (attack the worst case, turn each finding into a repeatable
  check, keep the judge independent of the builder).
- Pre-mortem. Gary Klein, "Performing a Project Premortem", *HBR* (2007), and the
  prospective-hindsight result behind it (Mitchell, Russo, Pennington, 1989).
- Investor lens. Sequoia's "Writing a Business Plan" and "Elements of Enduring
  Companies"; the idea maze (Srinivasan, Dixon); Andreessen on market and
  product-market fit and moats; Graham on plain description and the domain-expert
  test; Gurley on unsubstantiated size; cohort-retention and engagement logic for a
  consumer subscription.
- Parent (buyer and user) lens. April Dunford's positioning built from competitive
  alternatives up; Jobs to Be Done and the four forces (Christensen, Moesta) plus
  Ulwick's outcome metrics; Fletch PMM's homepage test and capability-versus-benefit
  distinction; the StoryBrand grunt test; MECLABS's value-proposition model and
  conversion heuristic.
- Designer lens. Jakob Nielsen's ten usability heuristics, his severity scale, and
  the cognitive walkthrough; the crit discipline from Connor and Irizarry's
  *Discussing Design* (tie every comment to an objective, separate defect from
  taste); the repo's own craft and AI-tell audits in `qa/`.
- Clinician and duty-of-care lens. The product's own safety posture in
  `docs/safety/trust-and-safety.md`; SAMHSA and WHO safe-messaging guidance for
  crisis content; the professional-ethics norm that coaching is not therapy and must
  not diagnose or treat; honest-advertising and testimonial-substantiation norms
  (do not present anecdote or popularity as clinical efficacy); COPPA (children as
  subjects, not users).
- Prioritization and fixes. Nielsen severity for defects; RICE (Intercom), ICE, and
  the impact-effort matrix for fix order; severity versus priority from bug triage;
  5 Whys and the fishbone for root cause; a weighted decision matrix for choosing
  among steelmanned fixes.
- The in-repo models this skill generalizes: `qa/landing-design-critique-2026-04-27.md`,
  `qa/pro-ux-craft-audit-2026-05-28.md`, `qa/marketing-ux-pro-pass-2026-05-28.md`,
  and `qa/ai-tells-audit-2026-05-28.md`.
