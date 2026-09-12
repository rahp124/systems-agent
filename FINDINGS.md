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
- A 120-scenario Net3 ensemble (40 per class) can be generated reproducibly. With seeded noisy observations and an ambiguity gate, 100 held-out episodes produced 76% accuracy at mean cost 2.95 for EIG-per-cost, versus 76%/4.47 for random and 73%/3.24 for cheapest-first.

## Integration details found empirically

- EPyT-Flow leak events require flow units compatible with its leakage implementation; the probe uses `EN_CFS`.
- `AbruptLeakage` needs an explicit finite `end_time` in this version; `None` causes an overflow during event initialization.
- Network timing settings must preserve the bundled network's compatible hydraulic/quality cadence. EPyT validates the pair eagerly, so the probe changes duration only.

## Still open

- The first trace-backed likelihood model uses categorical thresholds and Laplace-smoothed empirical frequencies. It is not calibrated and its threshold choices are harness parameters.
- Initial telemetry now gates the benchmark to scenarios with top posterior ≤0.70 and second posterior ≥0.15. Its categorical noise rates are configured harness parameters, not calibrated field-error estimates.
- The Phase-0 100-scenario parallel timing and frozen-sensor serialized-storage measurements remain to be added. No performance claim is justified yet.
- The analytic runner remains a correctness oracle. The new evaluation path is simulator-derived, but is an integration result rather than a resume-quality benchmark.
