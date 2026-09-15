# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

The shared public experience serves two primary audiences:

- Utility evaluators assessing whether the advisory approach is understandable, safe, and suitable for a governed offline or shadow-mode evaluation.
- Water-systems researchers assessing the decision method, reproducibility, evidence provenance, and validation limits.

The interactive demonstration must remain understandable to a first-time visitor without hiding technical depth from specialists.

## Product Purpose

The Water Investigation Agent is an auditable decision-support system for uncertain water-distribution events. It maintains competing explanations, evaluates the expected information and operational cost of available observations, and recommends what to investigate next.

Success means a visitor can understand the mechanism, inspect measured evidence and limitations, and run the real synthetic investigation harness without mistaking it for operationally validated software.

## Positioning

The defining mechanism is an inspectable investigation trail: competing hypotheses lead to scored observation choices, returned evidence changes explicit probabilities, and every recommendation remains reviewable. The system is not an LLM wrapper and does not claim novelty for Bayesian inference or expected information gain.

## Operating Context

The public experience is a source of truth and an executable demonstration. Researchers can follow evidence into architecture, measurement assumptions, reports, and reproducibility instructions. Utility evaluators can follow safety, governance, data-handling, and offline-validation material. The current live experience uses synthetic scenarios and exposes no control interface.

## Capabilities and Constraints

- The browser lab calls the repository's actual Bayesian investigation harness.
- Demonstrations use synthetic scenarios and may classify a scenario incorrectly.
- Public SDWIS, Water Quality Portal, and NORS data provide context, not matched operational validation.
- The interface is read-only and advisory-only; it cannot control pumps, valves, dosing, flushing, or other actuators.
- Real operational claims require approved de-identified historian replay, locked outcomes, security review, governance, and external validation.
- The implementation remains dependency-light HTML, CSS, JavaScript, and Python.

## Brand Commitments

Use the name “Water Investigation Agent.” The voice is precise, calm, evidence-led, and candid about uncertainty. Avoid hype, anthropomorphic claims, invented customers, implied deployment, or decorative AI conventions.

The unified experience will use an investigation-instrument concept: a shared plain-language opening leads into clearly marked utility and researcher paths. The complete redesign includes navigation, evidence, the interactive lab, results, responsive behavior, and accessibility.

## Evidence on Hand

- `artifacts/net3-multiseed-benchmark.json` contains the tracked synthetic policy benchmark.
- `artifacts/sdwis-pwsid-06-public-report.json` contains public compliance context.
- `artifacts/wqp-wi-017-nitrate-public-report.json` contains public monitoring context.
- `artifacts/nors-drinking-water-public-report.json` contains public outbreak-outcome context.
- `docs/agent-architecture.md`, `docs/research/measurement-model-sources.md`, and `FINDINGS.md` document the method and limitations.
- `docs/validation-protocol.md`, `docs/data-handling-security.md`, and `docs/operational-readiness.md` document the external-validation boundary.

No utility deployment, live SCADA result, customer testimonial, or matched real-world outcome result is available and none may be fabricated.

## Product Principles

- Make the next-investigation decision visible before the final classification.
- Prove claims with inspectable evidence and label synthetic demonstrations at the point of use.
- Provide one understandable opening, then let utility and researcher needs diverge without duplication.
- Treat incorrect results as informative evidence, not something to conceal.
- Keep every operational boundary explicit and every interaction read-only.

## Accessibility & Inclusion

The primary flow must work with keyboard and assistive technology, preserve visible focus, announce asynchronous state changes, avoid color-only meaning, support reduced motion, and remain usable on narrow screens and at browser zoom.
