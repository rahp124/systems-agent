# Feasibility spike findings

## Environment

- Python 3.12.0
- EPyT-Flow 0.17.2
- EPANET-PLUS 0.3.1 / EPANET 2.3.06

## Confirmed

- The analytic harness has exact Bayesian-update and EIG tests; `pytest` passes six tests.
- Net3 can run 48-hour contamination, leak, and sensor-fault scenarios through a common pressure/flow/quality observation shape (`49 × 4`, `49 × 1`, and `49 × 2`) using its bundled hourly cadence.
- A seeded categorical episode keeps its hidden class evaluator-only, schedules delayed evidence, and replays deterministically.
- L-Town can run a 48-hour sensor-fault smoke scenario with the current four-pressure/one-flow/two-quality sensor configuration in about 0.9 seconds on this machine (`577` observations, using its bundled five-minute cadence).
- A 120-scenario Net3 ensemble (40 per class) can be generated reproducibly. On 100 paired held-out episodes with four-band chemical observations, EIG-per-cost achieved 85% accuracy at mean cost 3.46, risk-aware achieved 85%/1.00, expected-accuracy achieved 88%/5.56, random 88%/5.28, and cheapest-first 85%/3.81.
- Forty of 60 held-out scenarios pass the ambiguity gate under the instrument-level model; 20 are rejected as too certain at the initial telemetry stage.
- The paired risk-aware frontier remains abrupt after adding four-band chemical observations: λ=0 matches the expected-accuracy policy (88% accuracy, cost 5.00), while λ≥0.02 selects the field assay (83%, cost 1.00). More outcome granularity alone does not provide a smooth cost/accuracy frontier.

## Integration details found empirically

- EPyT-Flow leak events require flow units compatible with its leakage implementation; the probe uses `EN_CFS`.
- `AbruptLeakage` needs an explicit finite `end_time` in this version; `None` causes an overflow during event initialization.
- Network timing settings must preserve the bundled network's compatible hydraulic/quality cadence. EPyT validates the pair eagerly, so the probe changes duration only.

## Still open

- The observation model now uses published instrument/method performance with explicit distributional assumptions. It still excludes sampling/handling, installation, drift, hydraulic-model, and site-specific error; see `docs/research/measurement-model-sources.md`.
- Initial telemetry gates the benchmark to scenarios with top posterior ≤0.70 and second posterior ≥0.15.
- EIG-per-cost currently loses seven percentage points of accuracy to random despite lower cost. The expected-accuracy diagnostic reduces this gap but costs more, showing that acquisition—not just observation quality—is the next policy-design problem.
- Further λ tuning is not useful with the current action model. Four-band quantitative assay evidence raised EIG-per-cost accuracy from 83% to 85% on the standard paired run, but did not change the positive-λ frontier. The next valid improvement is conditionally distinct evidence, such as a separately sampled and source-calibrated delayed lab action.
- The Phase-0 100-scenario parallel timing and frozen-sensor serialized-storage measurements remain to be added. No performance claim is justified yet.
- The analytic runner remains a correctness oracle. The new evaluation path is simulator-derived, but is an integration result rather than a resume-quality benchmark.
