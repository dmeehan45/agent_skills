---
name: content-rigor
description: >-
  Research, sourcing, and evidence guardrails for authored user-facing content
  on Satsang: articles and moment scripts, marketing and comparison-page copy,
  the glossary, quiz copy, emails, image alt text, and meta descriptions. Use
  when drafting, editing, or reviewing a piece for whether its claims are true,
  traceable, and earned, not just well written. Matters double here because the
  product makes developmental, neuroscience, clinical, competitive, and privacy
  claims to vulnerable parents, and the repo has no separate research standard
  yet, so this skill carries the sourcing bar. Runs in two modes, write and
  review. Anchors voice to docs/satsang-writing-style-guide.md. NOT for the AI's
  live conversational output (that is the behavior harness and evals) and not
  for UI (docs/satsang-design-system.md and frontend-polish).
---

# Content rigor (Satsang)

This skill is the workflow for holding every piece of authored content to a
research and rigor bar: how to research and draft a piece so it clears the bar,
and how to review a piece against the bar and report what fails.

The spine is one rule. Traceability. Every non-obvious claim resolves to
something the reader can check: a named primary source, a real number with its
units, a worked example, or a clearly marked statement of how confident we are.
A piece can be clean prose and still fail this. That failure is what the skill
exists to catch.

**Read this next, because it changes how you use the skill.** In the codebase
this skill was ported from, the sourcing standard lived in a separate document
and this skill only operationalized it. Satsang has no such document. It has a
strong voice standard (`docs/satsang-writing-style-guide.md`) but no
research-standards, source-tier, or citation document, and the clinical-review
gate that would enforce sourcing on authored content exists only as an admin
stub that is "a future gate and is not currently enforced". Meanwhile the live
content actively asserts brain science ("the prefrontal cortex comes back
online"), attachment research ("the research is unambiguous"), competitor facts
("ChatGPT may train on your conversations"), privacy contracts ("our provider
agreed in writing not to train"), and "science-backed" claims, mostly with no
traceable source. So until a `docs/research-standards.md` exists, **this skill is
the sourcing bar, not just its workflow.** Section 1 is written to be that bar.
See section 7 for the recommendation to promote it into a doc and wire the
clinical-review gate.

This is an internal note, so the house voice rules do not strictly bind it, but
it is written to pass them anyway (no em dashes, no dramatic-reveal colons),
because it enforces them.

## 0. What this owns, and what it defers

This is the seam that keeps the skill honest. Get it wrong and you either miss
the content that needs rigor or waste effort auditing content another system
already governs.

**This skill owns authored, static, or batch-generated content:**
- Articles. Authored as JSON in `public/content/articles/*.json`, seeded into the
  Supabase `article` and `article_version` tables (the DB is the runtime source of
  truth; the JSON is the fallback), and prerendered to SEO HTML. Includes the
  "brain science" callouts (`callout` blocks, `variant: "brain"`).
- Moment scripts, the "Find Your Words" library on `/tools`. DB-backed
  (`moment`, `moment_example` for the "Say This" exact words, and
  `do_not_say_rule` scoped `script` for the "Easy to Slip Up" section). Both the
  "Say This" phrasing and the "what not to say" rules are content claims.
- The glossary (`src/pages/GlossaryPage.tsx`), including the `DefinedTerm`
  JSON-LD it emits.
- Marketing and comparison copy: the landing, about, approach, and comparison
  pages, and the quiz funnel. Most strings resolve through `src/lib/i18n/keys.ts`
  and the locale catalogs; some are inline in the TSX.
- Emails, meta descriptions and titles (`src/lib/seo.ts`, `SeoHead`), and image
  alt text.

**This skill defers:**
- Voice, punctuation, and the AI-tell bans, to `docs/satsang-writing-style-guide.md`
  (marketing, articles, long-form) and Section 2 of `docs/satsang-design-system.md`
  (in-product UI microcopy). This skill governs whether a claim is true and
  sourced; the writing guide governs whether the line is on-voice. A piece usually
  needs both.
- The AI's live conversational output, what the assistant says turn by turn, its
  plans, summaries, and presented content, to the behavior harness and the eval
  loop (`change-pass`, `eval-changeset`, `docs/governance/`, and the safety stack
  in `src/lib/ai/safety/`). Do not audit a chat transcript with this skill; that
  content is generated against a governed prompt and graded by evals. This skill
  governs the human-authored and batch-authored words around the AI, not the
  model's turns.
- Runtime safety, crisis handling, blocked topics, and medical-boundary
  enforcement, to `docs/safety/trust-and-safety.md` and the safety-policy console.
  This skill flags when authored content crosses a safety line; the safety stack
  owns runtime.
- UI, layout, and imagery, to `docs/satsang-design-system.md` and `frontend-polish`.

## 1. The one test, the source tiers, and the claim classes that bite here

Two questions gate every factual claim in a piece.

1. Can the reader trace it, to a named primary source, a real number with units,
   a worked example, or a clearly marked opinion. If not, cut it or go earn it.
2. Could it be false. "Keeps getting better", "built for trust", "wires the
   relationship safe" cannot, so they prove nothing. Replace the soft claim with
   the mechanism, the number, or the named thing.

Source quality is tiered. Anchor to the highest tier reachable, and never let a
lower one stand in for a higher one that exists.

- **Tier 1, primary.** The only tier strong enough for a load-bearing claim.
  Peer-reviewed developmental and clinical psychology, meta-analyses and
  systematic reviews (for example Cochrane), the primary texts of the frameworks
  the product actually draws on (attachment theory: Bowlby, Ainsworth; "name it to
  tame it" and whole-brain: Siegel and Bryson; polyvagal and nervous-system work:
  Porges, where honestly applicable; couples work: Gottman), and official bodies
  (the American Academy of Pediatrics, WHO, SAMHSA). For product claims, our own
  logged eval results and data.
- **Tier 2, support.** A named clinician or researcher writing first hand, a
  reputable practitioner book (check it against the primary it rests on), or an
  established institution's explainer that names its own primary source. Use to
  support, and link through to the primary.
- **Tier 3, never the basis of a claim.** Parenting blogs, content-mill and SEO
  listicles, "studies show" with no study, competitor marketing pages, a single
  anecdote or testimonial offered as proof of efficacy.

Because this is a parenting and wellbeing product, some claim classes carry more
risk than a marketing line usually would. Treat each as load-bearing:

- **Developmental and neuroscience claims.** "The prefrontal cortex comes back
  online", "children learn to soothe themselves only after thousands of moments of
  being soothed", "repair wires the relationship safe". These need a Tier 1 source
  or they must be softened to a marked observation or argument and attributed. "The
  research is unambiguous" with nothing cited is a blocking finding, not a flourish.
- **Attribution claims.** "A phrase coined by Dr. Dan Siegel". Attribute correctly
  and verify the attribution; a misattributed coinage is a credibility hole a
  skeptic will find.
- **Competitive claims.** "ChatGPT consumer accounts may use your conversations to
  train", "Good Inside is a parenting book in digital form". Must be true, current,
  fair, and dated, because a competitor's policy or product can change under you.
  Name the date or the version you checked.
- **Privacy and contractual claims.** "We never sell your family's story", "nothing
  you share trains an AI, ever", "our provider agreed in writing not to train or
  retain", zero-data-retention. These must match the actual data posture in
  `docs/subprocessors.md` and `docs/safety/trust-and-safety.md`. A privacy overclaim
  is both a trust failure and a legal exposure; hold it to the contract, not the
  aspiration.
- **Product and efficacy claims.** "A 100-plus-case evaluation set", "more robust
  and reliable than AI companions", "science-backed parenting quiz". Tie each to the
  real eval-harness numbers or the real study, or soften it. "Science-backed" with
  no study named is a Tier 3 dressed as Tier 1.
- **Credential claims.** "A licensed therapist with 15 years", "over 100,000
  parents follow her work". Verify, and keep them consistent across every surface
  that repeats them; a credential that drifts between pages reads as marketing.
- **Safety-boundary claims.** No diagnosis, no treatment, no guaranteed outcome, no
  language that positions the product as therapy. Crisis content aligns to SAMHSA
  and WHO safe messaging. This skill flags an authored line that crosses the
  boundary; the safety stack owns enforcement at runtime.

## 2. Pick the mode, and scale to the piece

**Write mode** when the input is a topic, a brief, or a rough draft to bring up to
standard. **Review mode** when the input is a finished or near-finished piece to
audit. If the input is ambiguous, ask which, or infer: a topic means write, a
drafted piece means review.

Scale the rigor to the piece. A full article gets the whole treatment: every
load-bearing claim traced to a live primary source, the "brain science" callouts
sourced or softened, confidence marked, an internal-consistency check against what
other pieces already say. A glossary term, a marketing headline, or a quiz result
gets the two questions in section 1 plus the voice pre-flight; any factual claim it
makes still needs a Tier 1 or Tier 2 source behind it, even if the source is not
printed on the surface. A moment script gets the two questions plus the script
guardrail (its "Say This" and its "Easy to Slip Up" pairing, section 4). Do not
impose a literature review on a button, and do not let a headline smuggle in an
unsourced clinical claim because it is short.

## 3. Write mode

1. **Name the load-bearing claims before drafting.** Write down the factual
   assertions the piece will rest on, especially any in the claim classes in
   section 1. These are what you research. Everything else is voice and arrangement.
2. **Do the research the bar requires.** Re-verify every source live today, because
   competitor policies, guidance, and even links move. Prefer Tier 1. Triangulate
   any load-bearing developmental or clinical claim across independent primary
   sources. For a product or efficacy claim, look at the real eval data or the real
   study first. When a piece needs broad new research, the `deep-research` skill can
   run the fan-out and fact-check; this skill governs the bar its output must clear.
3. **Choose the structure.** An article uses the block schema already in
   `public/content/articles/*.json` (`hero`, `prose`, `keyTakeaway`, `callout`,
   `accordion`, `checklist`, `pullQuote` with `attribution`, `tryThis`,
   `reflection`). A moment script uses the "Say This" plus "Easy to Slip Up" shape.
   Marketing copy follows the writing guide. One idea per piece.
4. **Draft in the house voice.** No em dashes, no dramatic-reveal colons, no AI
   tells, concrete nouns (bedtime, meltdown, sibling fight, script) over abstraction,
   verbs that show work (remember, surface, draft, replay), say it once, show the
   behavior instead of asserting the quality, lead with what the parent gets. The
   full list is in `docs/satsang-writing-style-guide.md`.
5. **Cite and attribute as you write.** Attach each load-bearing claim to its
   source at the claim, with the date or edition you checked. Attribute ideas and
   coinages by name (and verify the attribution). For an article, put the sourcing
   where the piece or its editorial record can carry it; do not ship a "brain
   science" callout whose source you cannot name.
6. **Mark confidence and limits.** Tag each claim as observed, argued, or
   speculative, and match the hedge to the evidence. Name the limitation and the
   tradeoff in the same piece that makes the claim. "This helps many kids" is honest;
   "this works" is usually not.
7. **Self-review before handing over.** Run the pre-flight in section 6 on your own
   draft. Fix what fails. Then hand it over with the preview, never before.

## 4. Review mode

1. **Get the piece.** For an article, the JSON in `public/content/articles/` or,
   if it has been edited in the admin, the live `article_version` row (admin edits
   win over the JSON). For a moment script, the `moment` and its `moment_example`
   and `do_not_say_rule` rows via the loader. For marketing, the i18n keys in
   `src/lib/i18n/keys.ts` or the inline TSX. Or the current branch diff against
   `main` (`git diff main -- <paths>`).
2. **Extract the load-bearing claims.** List the factual assertions a sharp parent,
   a skeptic, or a clinician could dispute. Flag every claim that falls in a
   section 1 claim class. Ignore plain navigation and offer description; those only
   need the voice pre-flight.
3. **Grade each claim.** For every one: is it traceable, and to which tier; is the
   source still live and current; is it specific enough to be false; are the units,
   the sample, and the date or edition present; if it is our opinion or a soft
   observation, is it marked as ours. Each "no" is a finding.
4. **Scan the red flags** in section 5. Each hit is a finding.
5. **Run the mechanical checks.** The em-dash scan on changed copy
   (`rg -n "—|–" src/lib/i18n public/content src/pages`, expecting no hits) and the
   AI-tell pass from the writing guide. For a moment script, confirm the do-not-say
   guardrail: `node scripts/audit-script-do-not-say.mjs` must pass, meaning every
   active script surfaced to users has at least one approved, active "Easy to Slip
   Up" rule to match its "Say This". For an article or moment, `npm run build` runs
   the prerender so the SEO HTML regenerates. `npm run typecheck` if you touched
   typed content.
6. **Report**, using the format in the next section. Offer to apply the fixes, or
   apply them if asked. Do not silently rewrite a finished piece, and never fix a
   sourcing finding by inventing a source.

## 5. The review report, and the red flags

Open with a one-line verdict: **ship**, **revise**, or **not ready**, plus the
count of blocking findings. Then list findings grouped by severity, each as a
quote or location, the rule it breaks, and the concrete fix. Close with the
pre-flight result.

Three severities.

- **Blocking.** An untraceable or unfalsifiable factual claim, a developmental or
  clinical claim asserted as fact with no primary source, a number with no source,
  a Tier 3 source carrying a load-bearing claim, a privacy or contractual overclaim
  that does not match the actual posture, a misattributed coinage, a moment script
  with no matching do-not-say rule, banned punctuation in copy, or a build failure.
  The piece does not ship with any of these.
- **Should fix.** A Tier 2 or Tier 3 source where a reachable Tier 1 exists, a
  missing unit, date, edition, or model version, an unmarked opinion, a competitor
  claim with no date, a credential that disagrees with another surface, a restated
  idea a prior piece already made better.
- **Polish.** A soft comparative that could be a number, an adjective where a
  behavior would land harder, a sentence that is not a claim, proof, or a next step.

Worked example of a single finding:

> **Blocking.** `what-is-co-regulation.json`, the "brain science" callout: "a
> regulated adult's calm voice and slow breath signal safety, which lets the
> prefrontal cortex come back online. That's it." Asserted as settled neuroscience
> with no source, and as written the "That's it" makes it unfalsifiable. Fix: cite a
> Tier 1 source for the stress-response and co-regulation claim (for example Siegel
> and Bryson, or a review of the stress-physiology literature), soften the mechanism
> to what the source actually supports, and mark it as an explanatory model rather
> than a proven one-liner. Do not invent a citation; if none is reachable, cut the
> mechanism and keep the behavior ("your calm helps your child settle").

The red flags. Any one is a finding.

- "Studies show", "the research is unambiguous", or "science-backed" with nothing
  named.
- A number with no source, no date, no units ("3 to 10 minutes", "thousands of
  moments").
- A developmental, neuroscience, or attachment claim stated as fact with no primary
  source.
- A coinage or idea attributed to a named person without the attribution verified.
- A competitor claim with no date or version, or one that is no longer true.
- A privacy, retention, or training claim that outruns the actual contract and data
  posture.
- A credential or popularity claim that disagrees with another surface, or that is
  presented as proof of clinical efficacy.
- A secondary explainer or a blog cited where a primary was reachable.
- A load-bearing claim on one source, or on a marketing page.
- An adjective standing in for a measurement: "dramatically", "more robust",
  "personalized" with no inputs named.
- A claim that cannot be false: "keeps getting better", "built for trust", "wires
  the relationship safe".
- The good number shown and the caveat, the control, or the limit hidden.
- A moment script that gives a "Say This" with no "Easy to Slip Up" to match it.
- Our opinion dressed as established fact, or aspiration dressed as contract.

## 6. Pre-flight before a piece is done

Tick every box that applies, and if one fails honestly, it is not done.

- [ ] Every load-bearing claim traces to a named primary source, a real number with
      units, a worked example, or a clearly marked opinion.
- [ ] Every source is the highest tier reachable, and was re-verified live today.
- [ ] Every developmental, neuroscience, or clinical claim rests on a Tier 1 source,
      or is softened and marked as a model, not asserted as fact.
- [ ] Every competitive claim carries the date or version checked; every privacy or
      contractual claim matches the actual posture in `docs/subprocessors.md` and the
      safety doc.
- [ ] Every credential and efficacy claim is verified and consistent across surfaces,
      and no anecdote or follower count is presented as clinical proof.
- [ ] Every number carries its unit, sample, and date or edition.
- [ ] Every claim is specific enough to be false.
- [ ] The limitation, the tradeoff, and what was not tested are named in the piece.
- [ ] Each sentence sits at the right confidence tier; our opinion is marked as ours.
- [ ] The piece adds something the others do not; it does not restate what a prior
      piece already said.
- [ ] For a moment script, every "Say This" has a matching "Easy to Slip Up"; the
      do-not-say audit passes (`node scripts/audit-script-do-not-say.mjs`).
- [ ] Voice pre-flight passes: no em dashes (`rg -n "—|–"` clean on changed copy),
      no dramatic-reveal colons, no AI tells from the writing guide.
- [ ] `npm run typecheck` passes, and `npm run build` (which reruns the prerender)
      passes, before pushing to preview.

## 7. How this fits the other skills and the workflow

- `docs/satsang-writing-style-guide.md` governs voice; this skill governs the words
  and their sourcing. A piece usually wants both, and the two are complementary: the
  guide makes the line sound right, this skill makes it true.
- `frontend-polish` and `docs/satsang-design-system.md` govern the UI a piece sits
  in.
- The behavior harness and the eval loop (`change-pass`, `eval-changeset`,
  `docs/governance/`, the safety stack) govern the AI's live output. If a "fix" would
  change what the assistant says at runtime, it is not a content edit here, it is a
  harness change; route it there.
- `deep-research` is the engine for broad new research. This skill is the bar that
  engine's output must clear before it becomes copy.
- `adversarial-review` sits above this skill and flags that a claim is unproven to
  the reader; it routes the sourcing fix here.
- **Recommendation, worth raising with David.** Because the sourcing bar currently
  lives only in this skill, two follow-ups would harden it: promote section 1 into a
  standing `docs/research-standards.md` that this skill and `CLAUDE.md` both point at,
  and wire the admin clinical-review gate (`src/pages/admin/guidance/ReviewsPage.tsx`,
  `DoNotSayPage.tsx`) from a stub into an enforced publish gate for articles, moments,
  and glossary terms. Until then, this skill is the only place the bar is written down,
  so run it.
- Ship to a Vercel preview and hand over the URL before anything goes to `main`, the
  same as every other change.
