# Water Investigation Agent context

## Mission

The Water Investigation Agent is a cost-aware, auditable decision-support system for suspected water-distribution events. It maintains competing explanations, selects the next observation by expected information and operational cost, updates its belief from returned evidence, and records the recommendation path for review.

The active event classes are contamination, leak, and sensor fault. The agent is read-only and advisory: operators retain authority over incident-response actions. `docs/operational-readiness.md` defines the path from synthetic evaluation to utility shadow mode.

## Current implementation

- An exact categorical Bayesian harness verifies belief updates, information gain, expected classification accuracy, and policy scoring.
- A seeded Net3 simulation ensemble supplies contamination, leak, and sensor-fault traces.
- Instrument-derived pressure and chlorine observation models yield four ordered assay bands.
- Field and delayed lab confirmation are modeled as correlated evidence; the second assay uses a conditional likelihood rather than double-counting a marginal likelihood.
- Paired evaluation compares EIG-per-cost, risk-aware, expected-accuracy, random, and cheapest-first policies.
- A 600-scenario Net3 ensemble and five fixed episode seeds provide a tracked synthetic benchmark report.
- A read-only telemetry seam, synthetic SCADA adapter, de-identified historian CSV adapter with timestamp validation, versioned shadow records, and JSONL audit ledger support offline and shadow-mode integration work.

## Evidence discipline

The agent does not claim that Bayesian updates or expected-information selection are novel. It reports only measured outcomes with their scope and uncertainty. The current benchmark is synthetic Net3 evidence; it is not a utility deployment, real-world cost-savings result, or independent topology replication.

Read [PRIOR_ART_REPORT.md](PRIOR_ART_REPORT.md) before changing the decision model or making external claims. Read [docs/operational-readiness.md](docs/operational-readiness.md) before changing telemetry, audit, shadow-mode, or integration behavior.
Use [docs/utility-pilot-brief.md](docs/utility-pilot-brief.md) for partner outreach and keep it aligned with the operational-readiness documentation.
Use [docs/partner-outreach.md](docs/partner-outreach.md) to prepare outreach; do not send messages or request external data without explicit user direction.

## Development sequence

1. Preserve analytic correctness and reproducibility.
2. Extend the simulator-derived evidence model or action model only with documented assumptions.
3. Evaluate policies on paired held-out episodes and record uncertainty.
4. Replicate across independent ensembles, sensor layouts, and eventually de-identified historian replay.
5. Use utility-approved shadow mode before any operator-facing pilot.

## Non-negotiable boundaries

- Keep simulator ground truth unavailable to the investigation policy.
- Keep telemetry integration read-only and recommendations advisory until a utility-approved validation gate authorizes a broader scope.
- Do not fabricate operational, calibration, or economic claims.
- Keep every material belief and recommendation explainable from recorded evidence, likelihoods, and policy configuration.
