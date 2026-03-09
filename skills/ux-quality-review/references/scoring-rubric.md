# Scoring Rubric

## Category scoring scale (0–5)
Apply this anchor set to each category.
- **0**: Broken or absent; core workflow blocked.
- **1**: Severe systemic issues; completion unlikely without assistance.
- **2**: Major gaps; completion possible with high friction.
- **3**: Baseline acceptable; notable quality gaps remain.
- **4**: Strong and consistent; only minor issues.
- **5**: Exemplary execution; no meaningful gaps observed.

## Category anchors

## 1) Accessibility UX standards
- **0** No keyboard path and inaccessible critical content.
- **1** Multiple critical barriers across controls/forms/feedback.
- **2** Frequent barriers with partial workarounds.
- **3** Core path accessible; secondary paths need fixes.
- **4** Broad compliance with minor edge gaps.
- **5** Robust inclusive experience across core and edge flows.

## 2) User flow simplicity & continuity
- **0** Users frequently get stuck with no next action.
- **1** Core flow fragmented; dead ends common.
- **2** Flow works but confusion and backtracking are frequent.
- **3** Most transitions clear; occasional ambiguity.
- **4** Flow is clear, resilient, and easy to recover.
- **5** Seamless progression with excellent guidance and continuity.

## 3) Visual cleanliness & cognitive load
- **0** Visual chaos prevents efficient comprehension.
- **1** Heavy inconsistency and competing emphasis.
- **2** Noticeable clutter and hierarchy breakdown.
- **3** Readable baseline with some noise.
- **4** Clean, purposeful hierarchy with low cognitive burden.
- **5** Highly legible, focused, and consistently intentional design.

## 4) Mobile responsiveness & interaction ergonomics
- **0** Core task cannot be completed on mobile.
- **1** Mobile path exists but frequently fails.
- **2** Mobile completion possible with major friction.
- **3** Mobile works with some ergonomic issues.
- **4** Reliable mobile completion with strong ergonomics.
- **5** Mobile-first quality with excellent touch usability.

## 5) UX / visual best-practice compliance
- **0** Fundamental best practices absent.
- **1** Repeated anti-patterns across critical surfaces.
- **2** Mixed quality with substantial best-practice gaps.
- **3** Generally aligned but inconsistent in edge cases.
- **4** Strong alignment with only minor deviations.
- **5** Consistent, high-quality adherence throughout.

## Overall status mapping
- **0.0–1.9**: Failing
- **2.0–2.9**: Needs major improvement
- **3.0–3.9**: Acceptable with gaps
- **4.0–5.0**: Strong

## Severity definitions
- **Critical:** Blocks task completion, causes major accessibility barriers, or breaks core workflows.
- **High:** Serious friction, likely abandonment/confusion, or strong standards violations.
- **Medium:** Noticeable UX quality degradation but task still completable.
- **Low:** Polish or consistency issue with minor impact.

## Issue-type to severity mapping examples
1. Primary checkout button unreachable by keyboard → **Critical**.
2. Mandatory field has no visible label → **High**.
3. Success screen provides no next action → **High**.
4. 320px viewport cuts off submit button → **Critical**.
5. Error message appears without recovery action → **High**.
6. Body text is slightly small on mobile but readable → **Medium**.
7. Excessive font-style variation causing scan friction → **Medium**.
8. Overuse of accent colors without clear meaning → **Medium**.
9. Secondary action visually competes with primary CTA → **Medium**.
10. Minor inconsistent spacing in non-critical card layout → **Low**.
11. Empty state lacks example content but has CTA → **Low**.
12. Hover state color is inconsistent with brand palette → **Low**.

## Tie-break and confidence rules
- If evidence conflicts, choose the lower score and note what evidence is missing.
- If only partial flows are reviewed, label confidence as `Low` and avoid `5` scores.
- Use `Medium` confidence when core paths are reviewed but edge states are not.
- Use `High` confidence only when core + failure + mobile states are verified.
