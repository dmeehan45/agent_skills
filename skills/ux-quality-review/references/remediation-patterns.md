# Remediation Patterns

Use these patterns to convert findings into concrete recommendations.

## Pattern library (issue → fix)
1. **Low contrast text** → Raise contrast tokens; validate on default/hover/focus states.
2. **Meaningful icon has no label** → Add visible text or accessible name.
3. **Input has placeholder-only label** → Add persistent field label and helper text.
4. **Hidden keyboard focus** → Add clear focus ring token across components.
5. **Error-only color cue** → Pair color with icon/text message.
6. **No loading feedback** → Add progress state and disable duplicate submissions.
7. **Dead-end success page** → Add primary next-step CTA and secondary exit path.
8. **Empty state with no action** → Add direct action button plus short instruction.
9. **Confirmation page unclear** → State outcome, what changed, and next action.
10. **Dense settings page** → Group into sections and progressive disclosure panels.
11. **Too many highlight colors** → Reserve accent colors for status and primary actions.
12. **Too many type styles** → Constrain to small type scale with role-based usage.
13. **Primary action as text link** → Convert to button with strong visual affordance.
14. **Tiny tap targets** → Increase touch target size and spacing between actions.
15. **Horizontal scrolling on mobile** → Fix container widths; enable wrapping/reflow.
16. **Sticky footer hides CTA** → Add safe spacing and visibility-aware sticky behavior.
17. **Form keyboard mismatch on mobile** → Use semantic input types for correct keyboard.
18. **Gesture-only interaction** → Provide explicit button/menu fallback path.
19. **Brand color inconsistency** → Map UI states to approved brand tokens only.
20. **Inconsistent spacing rhythm** → Apply spacing scale and component-level constraints.
21. **Competing CTAs** → Keep one primary CTA; demote others to secondary/tertiary.
22. **Destructive action too easy** → Add confirmation modal with consequence copy.

## Do / Don't micro-guidance
- **Do:** Use one dominant primary action per surface.
- **Don't:** Style multiple actions as equally primary.
- **Do:** Keep plain-language, action-first microcopy.
- **Don't:** Use vague labels like “Continue” without context.
- **Do:** Align color and typography to a defined design token system.
- **Don't:** Introduce ad-hoc color or font variants for one-off elements.

## Cognitive-load optimization rules
- Reduce simultaneous decisions per screen.
- Sequence complex workflows into explicit steps.
- Surface only essential information first; defer advanced options.
- Keep interaction patterns predictable across pages.

## Mobile parity rules
- Ensure every desktop critical workflow has a mobile-completable equivalent.
- Prefer button/touch controls over inline text links for primary steps.
- Keep key actions within thumb-reachable zones where possible.
- Ensure recovery paths (errors, permissions, empty states) are available on mobile.

## Recommendation writing format
For each finding, write:
1. User-impact statement in plain language.
2. One primary recommendation (single responsibility).
3. Optional implementation hint (token, component, layout, copy change).
4. Acceptance check phrased as observable pass/fail behavior.
