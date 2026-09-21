# Modern UI guidance for a read-only water investigation / decision-support site

Research date: 2026-09-20

This note translates first-party design-system and accessibility guidance into implications for a water-quality investigation interface. “Recommendation” below means a design implication inferred from the cited source, not a claim that the source specifically studied water investigations.

## Evidence interpretation and progressive disclosure

- **Put the key facts in a compact, scannable summary.** GOV.UK’s [summary list](https://design-system.service.gov.uk/components/summary-list/) is intended for “key facts” and metadata, and explicitly distinguishes key/value facts from tables and ordinary lists. Use this for sample date, site, analyte, result, unit, threshold, source, and last-updated metadata; use a table for repeated measurements.
- **Use disclosure only when it helps users choose what to inspect.** GOV.UK says accordions should be used only where research shows value in seeing an overview, revealing relevant sections, or comparing information; content everyone needs should remain visible. [USWDS accordion guidance](https://designsystem.digital.gov/components/accordion/) similarly warns that accordions add cognitive and interaction cost, and recommends them for a small space containing a lot of content. Therefore: keep the “what happened / why it matters / what to do” summary open; place methods, provenance, assumptions, and calculation details behind clearly labeled “Show evidence” sections.
- **Make the disclosure affordance explicit and keyboard accessible.** GOV.UK’s [accordion implementation](https://design-system.service.gov.uk/components/accordion/) uses a whole heading button, an accessible show/hide label, and a no-JavaScript fallback that exposes all content. USWDS requires buttons, `aria-expanded`, `aria-controls`, unique IDs, and enough target space. Avoid nested accordions; offer “show all” when users need comparison.
- **Do not hide the evidence needed to challenge a recommendation.** This is an application of the above guidance: every recommendation card should expose its evidence summary, threshold/standard, data date, uncertainty/quality flag, and a link to underlying records without forcing users through many nested controls.

## Uncertainty and scientific/technical visualization

- **Treat the chart as one view, not the data itself.** USWDS [Data visualizations](https://designsystem.digital.gov/components/data-visualizations/) says visualizations need an underlying-data alternative, and that a data table alone does not provide the equivalent narrative. Provide a readable table/download plus a short text interpretation (“3 of 8 samples exceeded…”, trend direction, and relevant range).
- **Describe the statistical message in plain text.** USWDS recommends adding trends or a statistical summary in screen-reader-only text. For this project, encode uncertainty as text and structure—not color alone: e.g., “Estimated 12 µg/L; interval 9–16; confidence/coverage method; low confidence because n=1.” Include units, detection limits, missingness, sample count, and comparison baseline next to the mark.
- **Use visual channels that survive low vision and monochrome use.** WCAG 2.2 [1.4.1 Use of Color](https://www.w3.org/TR/WCAG22/#use-of-color) prohibits color as the sole means of conveying information; [1.4.3 Contrast](https://www.w3.org/TR/WCAG22/#contrast-minimum) and [1.4.11 Non-text Contrast](https://www.w3.org/TR/WCAG22/#non-text-contrast) establish contrast requirements. Represent status with a label/icon/pattern plus color (for example, “Above guideline” and a shape), and give chart lines/points distinct labels or styles.
- **Make hover and focus inspection optional and persistent.** WCAG [1.4.13 Content on Hover or Focus](https://www.w3.org/TR/WCAG22/#content-on-hover-or-focus) requires content revealed on hover/focus to be dismissible, hoverable, and persistent. Tooltips should not be the only route to exact values: provide focusable points or a nearby table/details panel.
- **Keep axes, units, thresholds, and provenance visible.** This is a project-specific inference from WCAG’s non-text-content and information/relationships requirements ([1.1.1](https://www.w3.org/TR/WCAG22/#non-text-content), [1.3.1](https://www.w3.org/TR/WCAG22/#info-and-relationships)): a chart should name the measured quantity, unit, date/time basis, scale, guideline line, and source in adjacent text.

## Recommendation and action explanation

- **Explain the recommendation as a chain of evidence.** A useful structure is: finding → comparison/threshold → confidence/limitations → recommended next step. Keep the conclusion visible, then let users expand “Evidence,” “How calculated,” and “What would change this.” This is an application of GOV.UK’s summary/disclosure guidance and USWDS’s alert guidance.
- **Make important state changes perceivable without interrupting.** WCAG [4.1.3 Status Messages](https://www.w3.org/TR/WCAG22/#status-messages) requires status updates to be programmatically determinable without moving focus; WAI’s [status-message guidance](https://www.w3.org/WAI/WCAG22/Understanding/status-messages) identifies `role="status"`/polite live regions as a sufficient technique in common cases. Use this for filter results, “showing 18 of 42 samples,” loading completion, and changed comparison settings. Do not use assertive alerts for routine updates.
- **Use alerts sparingly and include next steps.** USWDS [Alert](https://designsystem.digital.gov/components/alert/) guidance says to consider next steps, educate the user, avoid overuse, allow dismissal where appropriate, and understand context. A water warning should state what is known, what is uncertain, the scope/date, and a concrete safe action or escalation path.

## Accessibility, responsive behavior, and motion

- **Target WCAG 2.2 AA behaviorally, not just visually.** The [WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/) covers text alternatives, keyboard operation, focus order/visibility, contrast, reflow, target size, and status messages. Charts, maps, badges, and icons need accessible names or equivalent text; all controls must work by keyboard.
- **Design for reflow and narrow screens.** WCAG [1.4.10 Reflow](https://www.w3.org/TR/WCAG22/#reflow) requires content to work at 320 CSS pixels without two-dimensional scrolling except for content whose layout inherently needs it. On mobile, stack summary cards, let tables provide a deliberate horizontal-scroll region with an accessible caption, and move secondary evidence below the primary finding. Preserve reading order in the DOM; do not use CSS ordering to make a visual layout that changes meaning.
- **Make touch targets and focus states obvious.** WCAG [2.5.8 Target Size (Minimum)](https://www.w3.org/TR/WCAG22/#target-size-minimum) and [2.4.7/2.4.11 focus criteria](https://www.w3.org/TR/WCAG22/#focus-visible) support generous controls, visible focus, and no obscured focused elements. Use full-row/header hit areas for disclosure, but keep adjacent controls separated to prevent accidental activation.
- **Respect reduced motion.** WCAG [2.3.3 Animation from Interactions](https://www.w3.org/TR/WCAG22/#animation-from-interactions) says interaction-triggered motion must be disableable unless essential; WAI explains vestibular risks and recommends avoiding unnecessary motion, offering a control, and honoring the operating-system reduced-motion setting ([Understanding Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions)). Use short opacity/color transitions for feedback, avoid chart re-layout or map “fly-to” motion, and provide an instant state change under `prefers-reduced-motion`.
- **Avoid auto-advancing or flashing information.** WCAG [2.2.2 Pause, Stop, Hide](https://www.w3.org/TR/WCAG22/#pause-stop-hide) and [2.3.1 Three Flashes](https://www.w3.org/TR/WCAG22/#three-flashes-or-below-threshold) rule out uncontrolled moving/flashing status. A read-only investigation should be stable by default; updates should be user-triggered or politely announced.

## Suggested interaction model for this project

1. **Investigation header:** title, location/time scope, last updated, data-quality badge, and a one-sentence finding.
2. **Decision summary:** 2–4 key measures in summary-list/card form, with explicit units and comparison labels (“within guideline,” “above guideline,” “insufficient evidence”).
3. **Evidence view:** chart plus synchronized table; visible threshold/reference; exact values, intervals, sample count, and source links.
4. **Explanation disclosure:** “Why this conclusion,” “Methods and assumptions,” and “What could change it,” using shallow, independently expandable sections.
5. **Next action:** plain-language recommended action with scope, urgency, responsible party if known, and uncertainty caveat; use a polite status region for filter/query changes.
6. **Responsive/accessibility parity:** the same conclusion and evidence remain available at narrow widths, keyboard-only, screen-reader, high-contrast/forced-colors, and reduced-motion settings.

## Source index

- [WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/)
- [WAI: Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions)
- [WAI: Status Messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages)
- [GOV.UK Summary list](https://design-system.service.gov.uk/components/summary-list/)
- [GOV.UK Accordion](https://design-system.service.gov.uk/components/accordion/)
- [USWDS Accordion](https://designsystem.digital.gov/components/accordion/)
- [USWDS Data visualizations](https://designsystem.digital.gov/components/data-visualizations/)
- [USWDS Alert](https://designsystem.digital.gov/components/alert/)

