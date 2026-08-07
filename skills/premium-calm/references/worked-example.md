# Worked example — a guest-house marketplace

The case the method was written against: Avani, a guest-house marketplace for
African travellers and hosts, with verified accommodation, local and
mobile-money payments, reviews, nearby discovery, real-time availability,
wishlists, and host tools.

**Provenance warning, and the reason it is stated first.** The original
assessment was inferred from public app screenshots — not a measured run, not a
moderated usability study. Every observation below is therefore a *hypothesis to
verify*, and that is exactly the distinction `measurement.md` insists on. When
running this skill for real, measure first. Do not import these conclusions.

## Calibration

```
Archetype:        Transactional marketplace, mobile-first, emerging-market payments
Calm means:       Cost and consequence are known before commitment, and payment
                  state is never ambiguous
Highest stakes:   Mobile-money authorisation — irreversible, money moves, may
                  leave the app and complete asynchronously
Journey order:    1 search → results → detail → availability   (is it useful and credible)
                  2 booking → payment → confirmation            (money, error, abandonment risk)
                  3 confirmation → trip management → support    (calm after money moves)
                  4 save → wishlist → return                    (considered decisions, no pressure)
                  5 host onboarding and listing management       (inherits a stabilised guest system)
Modes:            home=discovery  results=comparison  detail=comparison
                  checkout=commitment  my-stays=management  support=recovery
Bar:              85 release / 90 flagship · zero S4 · a11y ≥ 4/5 · AA · 44pt/48dp
                  LCP ≤2.5s, INP ≤200ms, CLS ≤0.1 at field p75
Must not change:  the lime as brand signature, five-destination navigation,
                  local payment methods, African hospitality positioning
```

## Signature asset reassignment

The whole point: the assets stay, their jobs change.

| Asset | Was doing | Becomes | Now forbidden from |
| --- | --- | --- | --- |
| Fluorescent lime | Logo, chips, links, nav, banners, and CTAs simultaneously | Commitment, selection, focus, key availability, rare brand moments | Long text, ordinary metadata, every nav icon, decorative fills, competing CTAs, disabled states |
| Near-black shell | Every surface | Cinematic discovery and media | Comparison and checkout, which move to quieter light or warm-neutral ground |
| Rounded cards | Wrapping everything, nested | Grouping that spacing and type cannot express | Card inside card inside sheet |
| Property imagery | Many small repeated thumbnails | Fewer, larger, decision-relevant images, consistent crops, progressive loading | Inconsistent ratios, aggressive overlays |
| Compact typography | Dense metadata at caption size | Larger body, higher line height, stronger metadata contrast, 6–8 roles | Price, policy, or error at caption size |
| Persistent navigation | Stable, but styled identically per platform | Stable destinations with platform-native labels, state, badges, and back behaviour | Identical pixels across web, iOS, Android |
| Local-market positioning | A marketing claim | Visible trust architecture: mobile-money support, verified hosts, fee clarity, cancellation policy, human support | Claims the interface never substantiates |

The diagnosis that drives all of it: **lime, dark panels, and similarly weighted
cards recur often enough that selected navigation, promotional content,
transactional actions, and ordinary metadata compete for attention.** Consistent,
and functionally undifferentiated.

## What the measurement pass would look for

Run the pipeline before accepting any of the above:

```bash
node scripts/measure_surface.mjs --surfaces avani-run-plan.json \
  --accent "#C6FF1A" --out pc-evidence
```

The readings that would confirm or refute the hypothesis:

| Hypothesis | Confirmed by |
| --- | --- |
| The accent is doing too many jobs | `accentCoveragePct` well above single digits; `accentUses` spanning nav, chips, promos, and CTAs |
| Promotions outrank the task | `competingSalienceRegions` > 1; the squint render showing promo masses dominating the search control |
| Selection depends on colour alone | The accentless render showing selected and unselected chips as indistinguishable |
| Metadata is too quiet | `contrastFailures` concentrated on `.meta` and price nodes |
| Cards are over-nested | `maxCardNestDepth` ≥ 3 |
| Type is doing too much | `typeTreatments` well above 8 |

## Two change items in full

```
ID            PC-01
Surface       checkout (commitment mode)
Criterion     microcopy-trust, interaction-feedback
Severity      S4
Current       Mobile-money authorisation leaves the app. On timeout the state is
              ambiguous and the form is cleared, so the user's recovery instinct
              is to retry — risking a duplicate charge.
Target        An explicit transaction state machine: ready, awaiting
              authorisation, pending confirmation, succeeded, failed-before-
              charge, uncertain/timed-out, refunded. Entered data survives every
              recoverable failure. Duplicate attempts are structurally blocked
              while state is unknown. Copy: "Your mobile-money authorisation is
              pending. Keep this screen open; you will not be charged twice."
Why           The single highest-consequence ambiguity in the product. Money
              moves, the confirmation is asynchronous, and the failure mode is
              charging a customer twice.
Effort        L — state machine, idempotency key, copy, three new screens
Acceptance    All seven states reachable in review; timeout retains the booking
              and distinguishes pending from failed; a second commitment attempt
              is refused while state is unknown; no entered data lost.
Risk          Requires payment-provider webhook reliability; needs a
              reconciliation path for states the provider never resolves.
```

```
ID            PC-04
Surface       results (comparison mode)
Criterion     task-clarity, color-contrast, accessibility
Severity      S3
Current       Selected filter chips are distinguished by lime fill alone.
              Evidence: the accentless render shows selected and unselected
              chips as identical.
Target        Selection carried by fill *and* a text or icon cue and a border,
              with the chip individually removable in place. Selected filters
              remain visible and removable without reopening the filter panel.
Why           WCAG requires meaning not to depend on colour alone, and a filter
              set the user cannot read is a comparison failure as well as an
              accessibility one.
Effort        S — chip component, selected-state markup
Acceptance    Accentless render still distinguishes selected chips; screen
              reader announces selected state; each chip is individually
              removable; target ≥44pt.
```

## Priority order

| Opportunity | User impact | Business impact | Effort | Priority |
| --- | --- | --- | --- | --- |
| Search module and persistent trip criteria | Very high | Very high | M | Critical |
| Property-detail information architecture | Very high | Very high | L | Critical |
| Transparent quote and payment-state model | Very high | Very high | L | Critical |
| Confirmation and trip hub | High | High | M | High |
| Results-card standardisation | High | High | M | High |
| Error, empty, and offline states | High | High | M | High |
| Wishlist collections and comparison | Medium | Medium | M | High |
| Profile information architecture | Medium | Medium | S | Medium |
| Editorial destination storytelling | Medium | Medium | L | Medium |
| Decorative material and advanced motion | Low | Medium | M | Later |

## The palette finding worth generalising

`assets/token-spec.example.json` carries this product's proposed palette. Two
results from running `check_contrast.py` against it are worth keeping:

- **The lime accent measures 1.08:1 against the warm light canvas.** It is
  perfectly usable as a *fill* with dark ink (15.05:1) but cannot be a thin
  selected-state border, an icon, or small text on light ground. The palette
  needed a separate darkened `accent-edge` token to fill that role.
- **`accent-quiet` needs an ink token that flips with the mode.** A near-black
  ink on a pale tint passes in light mode and fails on the dark-mode tint.

Neither is visible by eye on a bright display. Both would have shipped.

## Translating the method to other archetypes

The mechanism is identical; only the stakes and the vocabulary change.

| | Marketplace | Deployment tool | Clinical records |
| --- | --- | --- | --- |
| Highest-stakes moment | Payment authorisation | Promote to production | Submit or amend a record |
| Irreversible thing | Money moves twice | A bad build reaches users | An incorrect entry enters the audit trail |
| The ambiguous-state trap | Pending vs failed payment | Deploying vs deployed vs rolled back | Saved locally vs submitted vs countersigned |
| "Name the amount" becomes | "Pay GHS 1,240" | "Deploy 3 services to production" | "Submit and lock this record" |
| Confirmation must persist | Booking reference, policy, support | Deployment ID, diff, rollback command | Record ID, timestamp, amendment path |
| Accent belongs on | The commitment action | The destructive/irreversible action | The submit action, and nothing else |
| Discovery mode | Inspiration and imagery | Not present — this product has no browse mode | Not present |

A product with no discovery mode should not be given one. Calibration exists to
prevent importing another product's shape along with its principles.
