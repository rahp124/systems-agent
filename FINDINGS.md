# Water Investigation Agent findings

## Environment

- Python 3.12.0
- EPyT-Flow 0.17.2
- EPANET-PLUS 0.3.1 / EPANET 2.3.06

## Confirmed

- The public-data path processed EPA's July 2026 SDWIS export for PWSID prefix `06`: 5,695 compliance violation records across 132 systems, with compliance-period starts from 1991 through 2025. This is public compliance context, not operational telemetry or an agent-performance result; provenance and limitations are in `docs/public-data-results.md`.
- A bounded Water Quality Portal nitrate query for Wisconsin FIPS `55`, county FIPS `017` returned 134 historical public records from 39 monitoring locations (1961–2023). The report retains query/checksum provenance and separates reported measurement units; it is public monitoring context, not current telemetry or agent-performance evidence. See `docs/public-data-results.md`.
- A bounded CDC NORS drinking-water query returned 1,256 reported public-health outbreak records (1971–2023), with record-level reported illness, hospitalization, and death fields. It is an independent historical outcome source but has no PWSID, telemetry, or detection/intervention trace; it cannot validate the agent. See `docs/public-data-results.md` and `docs/research/cdc-nors-waterborne-outcomes.md`.
- The offline replay reconciler now reports review and label coverage, dispositions, action-agreement uncertainty, and event-grouped first-advisory timing when review records supply event IDs. These are schema-tested capabilities only; no real historian export or locked outcome set has been analyzed.
- The analytic harness has exact Bayesian-update and EIG tests; the full suite has 29 passing tests.
- Net3 can run 48-hour contamination, leak, and sensor-fault scenarios through a common pressure/flow/quality observation shape (`49 × 4`, `49 × 1`, and `49 × 2`) using its bundled hourly cadence.
- A seeded categorical episode keeps its hidden class evaluator-only, schedules delayed evidence, and replays deterministically.
- L-Town can run a 48-hour sensor-fault smoke scenario with the current four-pressure/one-flow/two-quality sensor configuration in about 0.9 seconds on this machine (`577` observations, using its bundled five-minute cadence).
- A 120-scenario Net3 ensemble (40 per class) can be generated reproducibly. On 100 paired held-out episodes with four-band chemical observations and conditional assay confirmation, EIG-per-cost achieved 94% accuracy at mean cost 3.98, risk-aware achieved 85%/1.00, expected-accuracy achieved 88%/5.24, random 90%/5.54, and cheapest-first 85%/3.81.
- Forty of 60 held-out scenarios pass the ambiguity gate under the instrument-level model; 20 are rejected as too certain at the initial telemetry stage.
- The paired risk-aware frontier gains an intermediate point once delayed lab confirmation is conditioned on the field band: λ=0.02 reaches 92% accuracy at mean cost 2.15 (bootstrap 95% accuracy interval 86–97%), between λ=0 at 88%/5.00 and λ≥0.05 at 83%/1.00. These intervals overlap; this is a decision-frontier signal, not a policy-superiority claim.
- On a larger 600-scenario Net3 ensemble, five fixed episode seeds produce 500 paired episodes. EIG-per-cost exceeds random accuracy by 3.2 percentage points (paired bootstrap 95% CI 1.0–5.8) while reducing mean cost by 2.45 units (CI −2.71 to −2.21). It exceeds cheapest-first accuracy by 7.0 points (CI 3.4–10.2) with no resolved cost difference (0.01, CI −0.06 to 0.10).

## Integration details found empirically

- EPyT-Flow leak events require flow units compatible with its leakage implementation; the probe uses `EN_CFS`.
- `AbruptLeakage` needs an explicit finite `end_time` in this version; `None` causes an overflow during event initialization.
- Network timing settings must preserve the bundled network's compatible hydraulic/quality cadence. EPyT validates the pair eagerly, so the probe changes duration only.

## Still open

- The observation model now uses published instrument/method performance with explicit distributional assumptions. It still excludes sampling/handling, installation, drift, hydraulic-model, and site-specific error; see `docs/research/measurement-model-sources.md`.
- Initial telemetry gates the benchmark to scenarios with top posterior ≤0.70 and second posterior ≥0.15.
- The expanded result resamples 500 episodes from one fixed 600-scenario synthetic Net3 ensemble. It is not an independent simulator, network-topology, sensor-placement, or real-data replication.
- The λ=0.02 frontier point and EIG-per-cost result warrant replication across independently generated ensembles, sensor layouts, and source-calibrated sampling/transport assumptions before policy selection.
- The Phase-0 100-scenario parallel timing and frozen-sensor serialized-storage measurements remain to be added. No performance claim is justified yet.
- The analytic runner remains a correctness oracle. The evaluation path is simulator-derived and remains an integration result rather than an operational validation result.
