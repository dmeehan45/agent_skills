# Review Checklists

Use these as observable pass/fail checks. Record concrete evidence (screen, state, copy, behavior).

## 1) Accessibility UX standards
1. Page has one clear H1 and logical heading hierarchy (no skipped levels for structure).
2. Text and interactive controls meet contrast expectations across default and hover/focus states.
3. Every form input has an explicit label and clear error/help text association.
4. Keyboard-only users can reach all core actions in a logical tab order.
5. Focus indicator is visible on every interactive element.
6. Main workflows can complete without pointer-only gestures.
7. Images/icons that convey meaning include meaningful alternative text.
8. Status changes (error/success/loading) are announced in a perceivable way.
9. Touch targets are large enough for reliable activation on mobile.
10. Zoom at 200% keeps content readable and workflows functional without clipping.

## 2) User flow simplicity & continuity
1. Every primary screen has one obvious next action.
2. Step transitions preserve context so users know where they are.
3. Back/Cancel behavior is predictable and does not silently lose work.
4. Empty states explain what to do next and offer a direct action.
5. Error states provide recovery actions, not just warnings.
6. Multi-step processes show progress and remaining effort.
7. Confirmation screens clearly state what happened and what users can do next.
8. Navigation labels are consistent with task language.
9. Branching logic never lands users on a page with no valid action.
10. Save/submit actions provide immediate feedback and post-action next steps.

### Dead-end probes (explicit)
1. After completing a task, can the user start the next likely task in one tap/click?
2. In empty states, is there always a visible primary action (not just explanatory text)?
3. After an error, is there at least one actionable recovery path?
4. If permissions block progress, is there a clear alternate route or owner handoff?
5. In optional setup flows, can users skip safely and still complete core workflow?

## 3) Visual cleanliness & cognitive load
1. Color is used purposefully (status, hierarchy, emphasis) rather than decoration.
2. Typography system uses limited, consistent sizes/weights for clear hierarchy.
3. Body text size remains readable across desktop and mobile contexts.
4. Spacing rhythm is consistent and reduces visual noise.
5. Highlight treatments are reserved for high-priority information.
6. Competing callouts are minimized to avoid split attention.
7. Dense content is chunked with headings and scan-friendly grouping.
8. Icons and labels align semantically (no ambiguous symbols without text).
9. Visual affordances distinguish interactive vs static elements.
10. Repetitive or redundant copy is removed to reduce cognitive burden.

## 4) Mobile responsiveness & interaction ergonomics
1. Core workflows are fully completable on narrow viewports (no desktop-only step).
2. Primary actions are buttons or clear touch controls (not tiny inline text links).
3. Key actions remain reachable without precision taps.
4. Layout reflows without horizontal scrolling in standard mobile sizes.
5. Sticky/fixed elements do not obscure required form fields or CTA buttons.
6. Form inputs use mobile-friendly control types and keyboards where applicable.
7. Long flows are split into manageable steps on mobile.
8. Gesture requirements have visible alternatives (button/menu fallback).
9. Orientation changes do not break interaction or hide primary actions.
10. Loading/performance states on mobile keep users informed and prevent double-submit.

## 5) UX + visual best-practice compliance
1. Information hierarchy reflects user goals and task priority.
2. Primary CTA stands out clearly from secondary/tertiary actions.
3. UI patterns are consistent with established platform expectations.
4. Validation is timely, specific, and constructive.
5. Defaults are safe and reduce user effort.
6. Destructive actions require clear confirmation with consequence language.
7. System status is always visible during async operations.
8. Content tone is concise, plain-language, and action-oriented.
9. Visual brand rules are applied consistently across components.
10. Experience supports both novice guidance and efficient repeat usage.
