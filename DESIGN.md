# Design System: Water Investigation Agent

## North star

The interface is a **calm decision console**. It helps a first-time visitor understand the problem, run an investigation, and interpret a recommendation without confronting them with a dashboard of unexplained numbers.

The experience follows one narrative: conflicting signals → useful next observation → returned evidence → changed belief → next step. Conclusions stay visible; technical calculations are progressively disclosed.

## Visual language

- Public Sans is the interface typeface. Large headings use weight, line-height, and spacing—not condensed display type—to create hierarchy.
- Deep teal communicates trustworthy analysis. Signal orange is reserved for the primary action, active recommendation, and meaningful change.
- The page uses a pale mineral canvas, white reading surfaces, soft teal explanation surfaces, generous whitespace, and restrained rounded geometry.
- Shadows appear only on the hero situation and primary investigation workspace. Supporting content remains flat.
- Borders group related information; they do not form a page-wide ruled grid.

## Information hierarchy

1. Explain the uncertain water-event problem in plain language.
2. Name the product's job: choose what evidence to collect next.
3. Explain the three-step mechanism without formulas.
4. Let the visitor run the real synthetic agent.
5. Keep recommendation, evidence, interpretation, and changed belief in one stable result surface.
6. Place rankings and calculations in one clearly labeled disclosure.
7. Separate proof, limitations, and evaluator-specific documents below the task.

## Components

The header is quiet and sticky on desktop. A single low-emphasis “Synthetic demo” marker establishes the global context; repeat warnings only where provenance changes interpretation. Primary buttons are signal orange; secondary buttons are white with a neutral border. All controls keep visible focus and at least 44px target height.

The investigation workspace is the dominant application surface. A narrow context rail holds starting assumptions and descriptive observation history. The result canvas updates in place and presents the recommendation, why it was selected, returned evidence, plain-language interpretation, belief changes, and the next action together.

Model estimates, synthetic evidence, public context, and operational boundaries are explicitly labeled in text. Color never carries provenance or uncertainty by itself. Content required to understand a recommendation stays open; only rankings and calculation details are collapsed.

## Responsive and motion rules

- Preserve the same conclusion, evidence, and next action at narrow widths.
- Tables may scroll inside a labeled region; the page itself must not scroll horizontally.
- State changes update in place and use the existing polite live region.
- Motion is limited to short control feedback and a small loading trace. Reduced-motion preferences remove both.

## Boundaries

Never imply a live utility connection, field validation, deployment, or operational authority. The interface is advisory-only and cannot control infrastructure.
