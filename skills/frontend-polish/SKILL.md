---
name: frontend-polish
description: >-
  Anti-slop design guardrails for building and editing user-facing UI:
  marketing surfaces (landing, about, approach, comparison pages, the quiz
  funnel) and consumer product surfaces (Home, Talk, Tools, Calm, Sleep, Plans,
  You, onboarding, the paywall). Keeps new work inside the locked "Quiet
  Authority" design language in docs/design-system.md and off the usual
  AI-generated tells, in both the morning and evening themes. The design system
  doc is the authority; this skill is the workflow that keeps you inside it.
  Copy and voice defer to docs/writing-style-guide.md and Section 2 of the
  design system; claim truth defers to content-rigor; the conversation UI spec
  and the AI's live behavior defer to design-system Section 9 and the harness.
  Universal token, anti-artifact, motion, and accessibility discipline applies
  to all UI including admin; the marketing-layout rules apply to expressive
  surfaces only.
---

# Frontend polish

This is a project-specific version of the open-source "taste-skill" anti-slop
design rules. The original is a generic, multi-client tool that reads an
arbitrary brief and picks an aesthetic and a design system. We do not do that.
The app has one brand, one stack, and one locked visual language, "Quiet
Authority", documented in full in `docs/design-system.md`. That document
is the source of truth. This skill is the workflow that keeps new UI consistent
with it and free of the patterns that make generated pages look generated.

> Written against a reference implementation — a TypeScript React/Vite SPA using Tailwind v3 with a locked design system and dual light/dark ("morning"/"evening") theming driven by CSS custom properties. The design tokens, class names, file paths, and sibling-doc references below are examples from that implementation — map them to the equivalents in your own codebase.

Read the design system's philosophy and its "Avoiding AI Artifacts" section
first (Section 1), then pull only the rules that fit what you are building. None
of this fires automatically.

The whole system reduces to one test, from the design system. For any element,
ask: **"does this feel like a quiet room you want to sit in?"** If it feels busy,
loud, clever, or demanding, the fix is usually a removal, not an addition. The
user is a tired parent, often at low resources; every choice should make that
person feel held.

## 0. Scope

Two layers, and they have different reach.

**Universal discipline, applies to every user-facing surface including admin and
settings.** Sections 1 (tokens), 2 (stack reality), 3 (anti-artifacts), 4 (dual
theme), 6 (motion), 7 (icons and imagery), and 8 (accessibility). A raw hex
value, an emoji in a heading, a violet gradient, an untokenized color that breaks
dark mode, or a missing focus ring is a defect anywhere in the app.

**Marketing-layout rules, apply to expressive surfaces only.** Section 5 (hero,
eyebrow restraint, section rhythm, one CTA label). These are for the landing,
about, approach, comparison, quiz, and refer surfaces. For in-product surfaces,
follow the design system's Page Template Patterns (Section 8) and content
max-widths by page type (Section 12). For admin and dense internal UI, follow the
design system's Component Catalog (Section 7) and the admin QA notes
(`qa/admin-visual-qa-*.md`, `scripts/admin-visual-sweep.mjs`); the marketing
layout rules do not apply there, but the universal discipline still does.

**Defer, do not restate:**
- Copy and voice, to `docs/writing-style-guide.md` (marketing and
  long-form) and Section 2 of the design system (in-product microcopy). Section 9
  of this skill routes there.
- Whether a claim is true and sourced, to the `content-rigor` skill.
- The conversation UI (the Talk and Calm chat surface, streaming reveal, bubbles,
  the orb), to the design system's Conversation UI Spec (Section 9). It has its
  own layout and motion; do not reinvent it here.
- What the AI actually says, to the behavior harness and evals (`change-pass`,
  `eval-changeset`, `docs/governance/`, `docs/safety/`).
- Whether the surface makes its case and survives a sharp reader, to
  `adversarial-review`.

## 1. The brand is locked. Match it, do not reinvent it

The original taste-skill spends most of its length helping the model choose a
palette, a typeface, and a design system per project. None of that applies.
The app already made those choices, in `docs/design-system.md`, backed by
`tailwind.config.js`, `src/index.css`, and `src/lib/theme.ts`. Your job is to
extend the existing system, not to reach past it. The single most common failure
mode for new work is introducing a token, color, or font that is not already in
the system. When the design system and anything below disagree, the design system
wins. Read the relevant sections before adding a surface.

**Type (design system Section 4).** Three families, all in the Tailwind config.
- `font-display` is Newsreader, a variable serif with an optical-size (`opsz`) and
  an italic axis. It carries the voice: display, hero, page, and section
  headings. Serif as the display face is a deliberate brand decision here, not a
  tell. Lean on the italic axis with lighter weights (400 to 500) for warm
  register (greetings, journal prompts, encouragements) and upright medium to
  semibold (500 to 600) for serious content (resources, settings, safety,
  errors). Register, not size, sets the tone.
- `font-body` is Instrument Sans. Everything functional: body, labels, UI,
  captions, forms.
- `font-mono` is JetBrains Mono, only for timestamps and data readouts.
- Use the type recipes in Section 4 (for example a hero page title is
  `font-display text-3xl text-ink`) and the Tailwind `text-*` scale. Do not
  hand-roll one-off `text-[2.3rem]` sizes when a token fits. Never use Inter or a
  system sans for display; a voiceless typeface contradicts a product whose value
  is voice.

**Color (design system Section 3).** The entire palette is CSS custom properties
switched by `data-theme`, not Tailwind's default scales. Use the named tokens,
never raw hex, and never a Tailwind default like `stone-500` or `slate-700`.
- Neutrals: `bg-ground`, `bg-surface`, `bg-surface-raised`, `bg-surface-sunken`,
  the `--border-default` and `--border-subtle` borders, and text `text-ink`,
  `text-dusk`, `text-clay`, `text-mist`.
- Accents, budgeted to under 5% of any screen: `warmth` (terra cotta, the primary
  brand accent, for CTAs, active states, trust signals), `sage` (growth, success,
  completion), `sky` (informational, links), `amber` (warning, time-sensitive),
  `rose` (error, destructive). Earn every accent. Adding `warmth` somewhere new
  means asking whether that element genuinely needs emphasis.
- Gradients are the faint radial washes in `.bg-app-morning`,
  `.bg-app-evening`, and `.bg-calm-gradient` only. They are felt, not seen.
  Never a solid decorative gradient, never violet or electric blue.

**Shape and rhythm (design system Sections 5 and 6).** Reuse the locked scales:
the 4px spacing scale (`gap-1` through `gap-8`, `py-12` for a section, `py-16` for
hero breathing room), the shadow system (`shadow-soft`, `shadow-elevated`,
`shadow-modal`), and the radius vocabulary (`rounded-full` for pills, chips, and
buttons; `rounded-3xl` for sheets and modals; `rounded-2xl` for cards;
`rounded-xl` for inputs and inner cards; `rounded-lg` for small inner elements).
Radius decreases as you move inward; an inner element never uses a larger radius
than its parent. Use the exact card class strings in Section 6 (standard,
elevated, inset, interactive tile, status-tinted, danger, conversation
container) rather than assembling your own.

If you genuinely need a value the system does not have, add it to the tokens (a
CSS variable in `src/index.css` and, if needed, the Tailwind config) as a named
token with a comment, the way the existing tokens are defined. Do not scatter
arbitrary values through components.

## 2. Stack reality (what you can actually use)

- Vite + React 18 + React Router + TypeScript + **Tailwind v3**. There is no
  Next.js and no React Server Components. Ignore any RSC, `"use client"`,
  `next/font`, or `next/image` guidance from the original skill. It does not
  apply.
- **No Motion, Framer Motion, or GSAP is installed** (checked in `package.json`).
  Do not import `motion/react`, `framer-motion`, or `gsap`. Animation here is
  Tailwind keyframes plus CSS transitions. There is a large native keyframe set in
  `src/index.css` (the `app-*` keyframes: `app-enter`, `app-breathe`,
  and the conversation and sheet animations) exposed as utilities like
  `animate-enter` and `animate-breathe`, plus the motion tokens (`duration-fast`,
  `duration-base`, `duration-slow`, the `ease-calm` timing function). Reach for
  those first.
- Scroll-triggered reveals use the existing landing components,
  `src/components/landing/SectionReveal.tsx` and `BubbleReveal.tsx`. Use them for
  "appears on scroll". Do not add raw `window.addEventListener('scroll', ...)` or
  scroll-position React state. If a new motion need cannot be met by the existing
  keyframes plus these components, raise it before pulling in a library.
- The app is a SPA. Article and moment pages are prerendered to static SEO HTML by
  the `postbuild` scripts (`scripts/prerender-articles.mjs`,
  `prerender-moments.mjs`), which read the database and no-op cleanly without env.
  The theme is applied on boot in `src/main.tsx` (`applyTheme(resolveTheme())`).
  If a component branches on the theme or on `prefers-reduced-motion`, read it in
  an effect after mount, not during render, so first paint is stable.
- Before importing any third-party package, check `package.json`. If it is
  missing, surface the install command and the reason instead of assuming it is
  there.

## 3. Anti-AI-artifact discipline

The design system already owns the canonical list. **Section 1, "Avoiding AI
Artifacts", is the authority: its visual-tells table and its six-step pre-ship
checklist.** Do not restate a generic anti-slop list here and do not contradict
it; run every surface against that section. The tells it bans, in short: floating
gradient blobs and blurred orbs as decoration, violet or electric-blue gradients,
three-card feature grids with an icon in a rounded square, emoji as decoration or
in headings, everything centered and symmetric, over-rounding every surface,
decorative motion (parallax, bounce, float, shimmer), default typefaces for
display, glassmorphism as ambient decoration, and identical evenly-weighted
sections down a page. The design system's line is worth memorizing: a list of five
reads more human than a grid of three.

**The single hardest rule, repeated because it is violated most often: no em
dashes.** No `—`, no en dash used as a sentence break, no double-hyphen substitute,
no `&mdash;` or `&ndash;` entities, anywhere user-facing, including JSX text,
string literals, page titles, meta descriptions, placeholders, error copy,
onboarding, and safety copy. The only carveouts are code comments and LLM system
prompts. En dashes are allowed only inside numeric ranges (`1–3`, `$30–$80`). The
design system's pre-ship checklist starts by grepping the diff for these.

## 4. Dual theme: morning and evening

The app ships a light theme (morning) and a dark theme (evening), resolved from
system preference and time of day and switched by the `data-theme` attribute
(design system Section 15). This is not an afterthought; it is why the token
discipline in Section 1 is strict.

- **Every surface must work in both themes.** Because all color is CSS variables
  that resolve off `data-theme`, using the tokens is what makes theming work
  automatically. A raw hex value or a Tailwind default color does not switch, so it
  silently breaks in the other theme. This is the real reason "no raw hex" is a
  hard rule, not a stylistic one.
- **Dark mode is 2am mode.** Test every evening-theme surface with screen
  brightness around 20% in a dark room (design system Section 14). Text stays
  legible without squinting, accents feel warm rather than glaring, and surfaces
  keep clear boundaries without stark contrast. If it glares, it fails.
- **Native form controls** (`<select>`, `<input type="date">`, and similar) need
  the `.app-native-control` class so their `color-scheme` follows the theme.
- Do not read the theme during render to pick a color. Use the tokens and let the
  cascade do it. Read the resolved theme in an effect only when you must branch
  behavior (not color) on it.

## 5. Layout rules for marketing and expressive surfaces

Durable rules, re-anchored to our system. These apply to the marketing surfaces;
for product surfaces defer to design-system Sections 8 and 12.

- **Mobile-first, always.** The app is for a parent holding a phone in one hand;
  desktop is a bonus, not the target (design system Section 12). Design and check
  the phone layout first.
- **Hero fits the first viewport.** Headline at most two lines on desktop, a short
  supporting line, primary action visible without scrolling. A four-line hero
  headline is a font-size problem: scale the type with the `text-*` tokens rather
  than letting it overflow.
- **Hero stack is small.** At most an optional eyebrow, the headline, one
  supporting line, and one primary plus at most one secondary action. Trust strips
  and logo walls go in their own section below, not inside the hero.
- **Eyebrow restraint.** The small uppercase label above a heading is one of the
  most overused tells; the design system flags the templated eyebrow directly. At
  most one per three sections, hero included. Most sections need only the heading.
- **No section-layout repetition, and no three-card grid reflex.** A layout family
  appears at most once per page; a long page uses several. When you reach for three
  symmetric cards with an icon in a rounded square, stop: vary the count, break the
  symmetry, prefer a list or an asymmetric layout (design system Section 1 and 6).
- **No split-header.** Do not put a big headline on the left and a small floating
  explainer on the right. Stack heading then body at a reading width. Use a
  two-column header only when the second column carries a real visual or
  interactive element.
- **One CTA label per intent.** Two labels for the same action on one page is a
  defect. Pick one and use it everywhere.
- **Navigation is one line on desktop.** Mobile collapse is explicit per
  multi-column section, not assumed. Prefer CSS Grid over flex percentage math, and
  `min-h-[100dvh]` over `h-screen` for full-height sections.

## 6. Motion

- **Motion is breath, not bounce** (design system Principle 6). The app's rhythm
  matches calm breathing: roughly 4-second cycles, ease-in-out (`ease-calm`), small
  amplitudes. Nothing feels urgent except an actual alert.
- **Every animation earns its place.** It communicates hierarchy, sequences a
  reveal, gives feedback, or shows a state change. "It looked polished" is not a
  reason; the design system bans decorative motion outright. Cut anything you
  cannot justify in a sentence.
- **Use the existing system.** The `app-*` keyframes, `animate-enter`,
  `animate-breathe`, the duration and easing tokens, and `SectionReveal` /
  `BubbleReveal` cover the real needs. Reach for those before inventing anything.
- **Reduced motion is mandatory.** `src/index.css` has a global
  `prefers-reduced-motion` override that neutralizes animation and transition
  durations, and the reveal components honor it. Any new infinite loop, parallax,
  or marquee must still collapse to static under it.
- **The conversation UI has its own motion** (streaming sentence reveal, bubble
  settle, the breathing orb) specified in design-system Section 9. Route there;
  do not reinvent it on the marketing side.
- If you claim motion on a surface, ship working motion. A static section that
  pretends to animate, or a half-built reveal that cuts off, is worse than a clean
  static one.

## 7. Icons, images, and assets

- **Icons: Lucide React only** (design system Section 13), stroke width `1.5`
  (lighter than Lucide's default 2), color always inherited from the parent, never
  hardcoded. Use the common icon vocabulary in Section 13 so the same action reads
  the same everywhere.
- **No emoji in any user-facing surface**, as decoration or in headings. It reads
  as generated marketing instantly (design system Section 1).
- **No tell-version fake visuals.** No product screenshots assembled from `<div>`
  rectangles, no fake terminals or dashboards, no decorative version footers
  (`v1.4.2`, `last sync 4s ago`), no decorative status dots, no "Scroll" cues, no
  locale or weather strips. Use a real screenshot, a real component, a real brand
  asset, or editorial imagery.
- **Real assets.** Brand marks and shared imagery live in `/public` (design system
  Section 16; for example `meditation-bg.webp` and the app icons). The logo
  filename lags the ongoing rebrand, so check `/public` for the live asset rather
  than hardcoding a name. Do not leave broken image links. For a placeholder, use a
  descriptive one rather than a generic gray box.

## 8. Accessibility

- **WCAG 2.1 AA** (design system Section 14). Body text 4.5:1, large text 3:1, UI
  components 3:1. The token pairs are built to pass; verify after any color
  customization, in both themes.
- **Focus rings.** The standard is
  `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-warmth focus-visible:ring-offset-2`,
  and a global `.app-focus-ring` treatment exists in `src/index.css`. Do not
  regress it; a component with its own focus style must stay at least as visible.
- **Touch targets** at least 44px by 44px on every interactive element. The
  codebase has `h-10` (40px), `h-11` (44px), and `h-12` (48px); prefer `h-11` or
  `h-12` for new work.
- **ARIA patterns** from Section 14: `role="dialog" aria-modal="true"` for modals,
  `role="switch" aria-checked` for toggles, `aria-label` on icon-only buttons, and
  the bookmark and segmented-control patterns. `Escape` closes modals and sheets,
  `Enter` submits, tab order follows visual order.
- **Form fields** pass AA against their surface in both themes. Label above input,
  error below, never a placeholder as the label. Native controls carry
  `.app-native-control`.
- The mobile CI (`npm run test:mobile`) runs an axe-core accessibility pass
  (`@axe-core/playwright`), so a regression here fails a gate, not just a review.

## 9. Copy and voice (defer)

Do not restate copy rules here, and do not let any wording from the original
taste-skill override the house rules. Every visible string follows:

- `docs/writing-style-guide.md` for marketing, articles, and long-form:
  the 15 AI-tell bans, the app-wide em-dash ban, the colon-drama ban, and the
  required behaviors. Run its checks on any copy you write.
- Section 2 of the design system for in-product UI microcopy: greetings, guidance,
  companion lines, errors, empty states, and safety microcopy, in the warm,
  second-person, present-tense register.
- The `content-rigor` skill for whether any factual claim in the copy is true and
  sourced.

Run the dash scan on changed copy: `rg -n "—|–" src public`, expecting no hits
outside numeric ranges. If this skill and the writing guide or design system ever
seem to conflict on copy, they win.

## 10. Pre-flight before you call a UI change done

Tick every box that applies. If one fails honestly, it is not done.

- [ ] Only locked tokens used (colors, type, spacing, radius, shadows). No raw hex,
      no Tailwind default color scales, no one-off font sizes where a token fits, no
      fourth font family.
- [ ] Accents earned; `warmth` is the primary accent; accent coverage stays under
      about 5% of the screen. Gradients are the faint washes only, never violet or a
      solid decorative gradient.
- [ ] Works in **both** themes. Evening tested at ~20% brightness in a dark room:
      legible, warm not glaring, surfaces bounded. Native controls carry
      `.app-native-control`.
- [ ] No Motion, Framer, or GSAP import. Animation uses the `app-*` keyframes,
      `animate-enter` / `animate-breathe`, the motion tokens, and the reveal
      components. Reduced motion respected. No raw scroll listeners.
- [ ] Theme and `prefers-reduced-motion` read in an effect, not during render.
- [ ] Marketing surfaces: hero fits the viewport with type scaled by tokens; hero
      stack small; eyebrow count at most one per three sections; no layout-family
      repeat; no three-card icon grid; no split-header; one CTA label per intent;
      nav one line; `min-h-[100dvh]` not `h-screen`.
- [ ] Lucide icons only, stroke 1.5, color inherited. No emoji. No div-based fake
      screenshots, decorative dots, version footers, or scroll cues.
- [ ] WCAG AA contrast on every text and control in both themes. Global focus
      treatment intact. Touch targets at least 44px. ARIA patterns applied.
- [ ] The design system's "Avoiding AI Artifacts" pre-ship checklist (Section 1)
      run: dashes grepped, strings read aloud, triads cut, colons checked, layout
      scanned, Voice Test applied.
- [ ] Copy passes `docs/writing-style-guide.md` and design-system Section 2;
      dash scan clean (`rg -n "—|–" src public`).
- [ ] `npm run typecheck` and `npm run build` pass. `npm run test:mobile` (including
      the axe-core pass) is green if the change shipped user-facing UI.

## 11. How this fits the other skills and the workflow

- `docs/design-system.md` is the authority; this skill operationalizes it
  and adds the anti-slop workflow. When in doubt, open the doc.
- `docs/writing-style-guide.md` and `content-rigor` govern the words and
  their truth. `adversarial-review` governs whether the surface makes its case. The
  behavior harness and evals govern what the AI says. This skill governs whether the
  UI is inside the design language and off the tells.
- The `qa/` craft tradition is the running record of this work:
  `qa/landing-design-critique-2026-04-27.md`,
  `qa/ai-tells-audit-2026-05-28.md`, `qa/pro-ux-craft-audit-2026-05-28.md`, the
  mobile and admin visual QA notes, and the `scripts/visual-sweep.mjs` and
  `scripts/admin-visual-sweep.mjs` sweeps. Read them for continuity.
- The house workflow is unchanged. Push to the feature branch, confirm the Vercel
  preview reaches READY, share the URL, and let the maintainer QA before anything reaches
  `main`. Never self-merge.

## Attribution

Rebuilt for this repo from the open-source taste-skill
(github.com/Leonxlnx/taste-skill, MIT). This is a derivative tailored to the
app's "Quiet Authority" design system and brand. It is not a verbatim copy: the
design-system-selection map, the palette rotation, and the Next.js, RSC, and GSAP
material from the original were dropped as not applicable, and several of the
original's hard bans (serif for display, and loading fonts from Google Fonts) are
intentionally reversed because Newsreader as the display voice and the Google
Fonts `@import` are deliberate decisions here (design system Section 4). The
durable layout, motion, imagery, and anti-tell rules were kept and re-anchored to
our tokens, our dual-theme system, and the design system doc, which is the
authority this skill serves.
