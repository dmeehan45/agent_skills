---
name: i18n-propagate
description: >-
  Propagate user-facing copy changes across all ten locale catalogs and audit
  key parity. Use whenever a change adds, edits, or removes a string in
  src/lib/i18n/keys.ts or any file under src/lib/i18n/translations/; whenever
  new user-facing copy is written on a translated surface (the landing page,
  marketing pages, the quiz funnel — anything rendered through
  useTranslation); when asked to audit, complete, or fix translations; or when
  adding a new locale. The nine non-English catalogs are typed
  Partial<Catalog>, so a missing key does NOT fail typecheck and does NOT fail
  any test — the string silently renders in English in production. This skill
  is the only guard. It fans the change out (real translations, not
  placeholder English), runs the parity audit, and verifies nothing was
  dropped. Not for harness/prompt copy (that is the change-pass loop), not for
  articles or moment scripts (content-rigor), and not for copy quality in
  English (docs/satsang-writing-style-guide.md owns voice; this skill owns
  completeness and propagation). Repo: dmeehan45/satsang-dev.
---

# i18n propagation (Satsang / Avani)

Every translatable string lives in one English catalog and nine translated
mirrors. The English side is guarded by the type system; the translated side is
guarded by **nothing**. This skill is the missing guard: when copy changes, it
carries the change into every locale and proves parity before the push.

**When to invoke.** Any diff that touches `src/lib/i18n/keys.ts` or
`src/lib/i18n/translations/*.ts`; any new user-facing string on a translated
surface; "audit the translations"; "add <language>"; resolving a review comment
about a string showing in English on a non-English locale.

## 1. The mental model: one source of truth, nine silent mirrors

- **`src/lib/i18n/keys.ts`** exports `EN`, a flat `'dot.path': 'string'` object
  (~577 keys at the time of writing). It is the source of truth twice over: it
  defines the key set (`TranslationKey` / `Catalog` types) *and* the English
  fallback copy. `translations/en.ts` just re-exports it.
- **`src/lib/i18n/translations/{zh,hi,es,ar,fr,bn,pt,ru,id}.ts`** are the nine
  translated catalogs, each typed `Partial<Catalog>`.
- **`src/lib/i18n/translations.ts`** assembles `TRANSLATIONS`; the runtime falls
  back to English for any key a locale omits.
- **`src/lib/i18n/locales.ts`** defines the ten locales (native names, `rtl`
  flag — Arabic is the RTL one), `DEFAULT_LOCALE`, and browser detection.

The trap, spelled out: because non-English catalogs are `Partial`, a key you
forget to translate compiles clean, passes `npm test`, ships, and renders
English to a Hindi-speaking parent. And a key you *drop* while editing does the
same. There is no parity test in `tests/` and no sync script in `scripts/`.
(Proof this bites: when this skill was written, all nine locales were missing
the same 52 keys — 42 of them live keys rendering English on every non-English
locale in production, unflagged by anything; the other 10 were dead keys
(`demoFork.*` etc.) that only a manual QA sweep had caught as a P3. Grep a
missing key's usage in `src/` before translating it: dead keys get deleted,
not translated.)

## 2. The parity audit (run first, and run last)

This is the skill's instrument. Run it before editing (to know the starting
state — do not blame your diff for pre-existing gaps) and after (to prove your
change landed everywhere):

```bash
node -e "
const fs=require('fs');
const keyRe=/^\s*'([^']+)':/;
const keys=f=>fs.readFileSync(f,'utf8').split('\n').map(l=>l.match(keyRe)).filter(Boolean).map(m=>m[1]);
const en=new Set(keys('src/lib/i18n/keys.ts'));
console.log('EN keys:',en.size);
for(const loc of ['zh','hi','es','ar','fr','bn','pt','ru','id']){
  const k=new Set(keys('src/lib/i18n/translations/'+loc+'.ts'));
  const missing=[...en].filter(x=>!k.has(x));
  const orphan=[...k].filter(x=>!en.has(x));
  console.log(loc.padEnd(3),'missing:',String(missing.length).padStart(3),'orphans:',orphan.length,missing.slice(0,5).join(', '));
}"
```

Success is `missing: 0, orphans: 0` for all nine locales — or a gap David has
explicitly accepted, named in your reply. Never report parity you did not run.
(Note the regex reads keys line-by-line; it assumes the house one-key-per-line
format. If a catalog was reformatted, eyeball-verify before trusting a zero.)

## 3. Adding or editing a string: the fan-out

1. **English first.** Add or edit the key in `keys.ts`, inside the right
   `// — Section —` comment group (the file is grouped by surface, not
   alphabetical — match that). English copy follows
   `docs/satsang-writing-style-guide.md`; the em-dash ban and voice rules apply
   to the **English** catalog. Keep any price or offer strings in sync with
   their mirrors (`src/lib/seo.ts`, `scripts/prerender-articles.mjs`, the
   docs) — `tests/offer-consistency.contract.test.mjs` guards some of this,
   your eyes guard the rest.
2. **Then all nine locales, in the same PR.** For each of `zh hi es ar fr bn
   pt ru id`, add the key with a **real translation into that language** —
   never English text as a placeholder, never a machine-transliterated stub.
   Match each catalog's existing register and typographic conventions (the
   catalogs already establish them: Russian uses «…» and the typographic
   dash, Chinese uses full-width punctuation, Arabic reads RTL — do not
   "fix" those to English conventions, and do not apply the English em-dash
   ban to languages whose typography requires one). Keep untranslatables
   untranslated: the product name **Avani**, the price **$24.99**, person
   names.
3. **Editing an existing English string?** Decide per key whether the meaning
   changed. A meaning change means all nine translations must be re-rendered,
   not left stale — a stale translation is worse than a fallback, because
   nothing ever flags it. A pure English style tweak (same meaning) can leave
   translations alone; say which case you're in.
4. **Removing a key?** Remove it from `keys.ts` **and** all nine catalogs.
   Typecheck will not catch a leftover in a `Partial` catalog if the key still
   exists; the parity audit's `orphans` count is what catches a key that
   outlived its English source.
5. **Renaming a key** is a remove plus an add across all ten files. Grep for
   the old key's usages in `src/` first.

These files were AI-draft translated at launch ("pending native review" per the
file headers). Keep that header comment intact; if David has had a locale
natively reviewed, do not churn its existing strings without being asked.

## 4. Verify

- Parity audit (section 2): 0 missing / 0 orphans, or named accepted gaps.
- `npm run typecheck` — catches a key in a locale file that doesn't exist in
  `Catalog`, and a malformed catalog.
- `npm test` — the contract suite; copy-adjacent tests
  (`start-page-copy`, `ui-copy`, `offer-consistency`) touch these files.
- Spot-render at least one changed locale and the RTL one if you touched
  shared layout copy: `npm run dev`, switch locale via the globe control
  (persisted under localStorage key `satsang_locale`), and look at the
  changed surface. For Arabic confirm direction still renders correctly.
- Bundle sanity: all nine catalogs are **eagerly imported** at boot via
  `translations.ts` → `I18nProvider` (a known P1 in the 2026-06-05 QA sweep).
  Adding keys is fine; adding anything *large* (long-form content, per-locale
  assets) to catalogs is not — flag it instead of growing the boot chunk.

## 5. Guardrails

- Never ship a key present in `keys.ts` but absent from a locale without
  saying so — silence is the failure mode this skill exists to kill.
- Never paste English into a non-English catalog to "make parity green".
  A wrong-language string in production is worse than the English fallback.
- Never drop or reorder existing translated strings while merging or editing;
  the parity audit catches drops, only diff review catches rewrites.
- Never translate brand names, prices, or `{placeholders}` / interpolation
  tokens if a string contains them — carry them through verbatim.
- Do not add a translation-completeness test to `tests/` as a side effect;
  that is a real improvement but it changes CI behavior — propose it to David
  separately.

## 6. Preflight before you hand back

- [ ] Parity audit run before and after; after-state is 0/0 or gaps named.
- [ ] Every new/changed key present in `keys.ts` + all nine catalogs, in the
      right comment group, really translated.
- [ ] Meaning-changed English strings had their translations re-rendered;
      style-only tweaks stated as such.
- [ ] Removed/renamed keys purged from all ten files; old-key grep clean.
- [ ] `npm run typecheck` and `npm test` green, honestly reported.
- [ ] One locale (plus RTL if layout-adjacent) spot-rendered.
- [ ] Price/brand/placeholder tokens verbatim in every locale.
