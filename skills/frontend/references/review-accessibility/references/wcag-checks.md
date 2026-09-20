# Focused WCAG 2.2 checks

Use for a web accessibility review after identifying the requested conformance level, critical journeys, and available browser/assistive technology. This reference covers selected frequent mistakes, not all WCAG criteria or legal obligations.

## Measure the right thing

| Check | Evidence and qualification |
| --- | --- |
| Text contrast, SC 1.4.3 AA | Ordinary text needs at least 4.5:1. Large text may use 3:1: at least 18pt normal or 14pt bold, approximately 24 CSS px or 18.67 CSS px. Do not substitute 18px/14px. Account for the criterion's exceptions. |
| Non-text contrast, SC 1.4.11 AA | Required visual information identifying controls/states and meaningful graphics generally needs 3:1 against adjacent colors, subject to the criterion's exceptions. Do not apply a text-size exemption. |
| Reflow, SC 1.4.10 AA | Test at the equivalent of 320 CSS px width for vertically scrolling content; verify no loss of information/function or two-dimensional scrolling except content that requires it, such as certain tables/maps. |
| Target size, SC 2.5.8 AA | Check 24 by 24 CSS px or the allowed spacing/equivalent/inline/user-agent/essential exceptions. A 44px target is useful guidance or a different criterion, not the universal 2.2 AA minimum. |
| Focus not obscured, SC 2.4.11 AA | A keyboard-focused component must not be entirely hidden by author-created content; stronger visibility goals can be recorded separately. |

Use computed foreground/background colors and the actual rendered size/state. Do not round a below-threshold ratio up to a passing value. Test each supported theme and relevant overlay/gradient background, not just token values in isolation.

## Exercise a complete interaction

1. Navigate the primary journey with the keyboard. Observe order, visible focus, native activation, and recovery from errors.
2. Open a modal, confirm sensible initial focus and an accessible name, cycle through its controls, dismiss it, and verify focus returns to a meaningful place. Native `<dialog>` helps when used correctly; the element's presence alone does not prove the whole interaction.
3. Check names/roles/states in an accessibility tree. For important assistive-technology journeys, verify with the supported screen reader when available; a tree snapshot is not a claim that screen-reader testing occurred.
4. Submit an invalid form and verify the error is associated with the field and reachable/announced as appropriate. Avoid duplicate or excessively chatty live announcements.
5. Test zoom/reflow, reduced motion, and touch target interactions in states that matter, including menus, validation, and sticky overlays.

When authentication is part of the journey, include login and any verification
step. For SC 3.3.8 AA, check whether a cognitive-function test has the required
alternative, assistance mechanism, or applicable exception. Test password-manager
support and paste; a segmented one-time-code input should accept the complete
code, not silently keep its first digit. Blocking paste is not automatically a
conformance failure if a qualifying alternative exists, so record the complete
flow and the actual barrier rather than judging one attribute in isolation.

Native buttons already handle keyboard activation. Do not add duplicate Enter/Space handlers merely because a general checklist says interactive elements need them. Custom widgets need the behavior of their selected pattern, not arbitrary ARIA attributes.

Run an available automated checker to find leads, then reproduce and map each finding to the actual criterion and user impact. Report the tested pages/states and any unavailable manual checks. A clean automated result is not a complete audit.

## Primary references

- [W3C: text contrast and large-text units](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- [W3C: non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)
- [W3C: reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html)
- [W3C: target size minimum and exceptions](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
- [W3C: focus not obscured](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html)
- [WAI-ARIA Authoring Practices: modal dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)
- [W3C: accessible authentication, alternatives, and verification-code paste](https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html)
