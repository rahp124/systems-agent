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
- In the earlier single-ensemble benchmark, a 600-scenario Net3 ensemble and five fixed episode seeds produced 500 paired episodes. EIG-per-cost exceeded random accuracy by 3.2 percentage points (paired bootstrap 95% CI 1.0–5.8) while reducing mean cost by 2.45 units (CI −2.71 to −2.21). The independent benchmark below supersedes this result for generalization claims.
- A prespecified independent benchmark covers five separately generated ensembles: two Net3 primary-layout seeds, Net3 alternate, L-Town primary, and L-Town alternate. Each ensemble has 60 scenarios per class and contributes 400 paired held-out episode draws, for 2,000 draws per policy. The tracked protocol fixes generation and evaluation seeds, thresholds, policies, risk penalty, and bootstrap settings before the result artifact.
- Across those ensembles, EIG-per-cost achieved 85.9% accuracy (hierarchical bootstrap 95% interval 66.0–98.7%) at mean relative cost 3.59 (1.34–6.48). Random achieved 84.15%; the paired accuracy difference was 1.75 percentage points with interval −0.2 to 3.95, so superiority is not resolved. The cost difference versus random was −1.51 units with interval −2.90 to 0.31, also unresolved at this ensemble count.
- The result exposes strong layout sensitivity: EIG-per-cost accuracy was 93.5% and 89.25% on the two Net3 primary ensembles, 46.75% on Net3 alternate, and 100% on both L-Town layouts. The transparent operator-rule baseline matched EIG-per-cost accuracy overall and differed by only 0.14 mean cost units. These are failure-analysis findings, not evidence of general policy superiority.
- Separate 36-scenario smoke replications now run on Net3 with an alternate sensor layout and L-Town with the primary layout. Their compact report is tracked as `artifacts/multi-network-replication.json`; neither artifact is pooled with the Net3 benchmark or sufficient for cross-network performance claims.

## Integration details found empirically

- EPyT-Flow leak events require flow units compatible with its leakage implementation; the probe uses `EN_CFS`.
- `AbruptLeakage` needs an explicit finite `end_time` in this version; `None` causes an overflow during event initialization.
- Network timing settings must preserve the bundled network's compatible hydraulic/quality cadence. EPyT validates the pair eagerly, so the probe changes duration only.

## Still open

- The observation model now uses published instrument/method performance with explicit distributional assumptions. It still excludes sampling/handling, installation, drift, hydraulic-model, and site-specific error; see `docs/research/measurement-model-sources.md`.
- Initial telemetry gates the benchmark to scenarios with top posterior ≤0.70 and second posterior ≥0.15.
- The expanded result resamples 500 episodes from one fixed 600-scenario synthetic Net3 ensemble. It is not an independent simulator, network-topology, sensor-placement, or real-data replication.
- The new Net3 alternate-layout and L-Town primary-layout artifacts have only 12 scenarios per class. They establish executable replication paths, not stable cross-network or sensor-placement estimates; larger independent ensembles and source-calibrated transport assumptions remain required.
- The expanded independent benchmark replaces the earlier small replication as the strongest cross-layout test, but five ensemble clusters still produce wide hierarchical intervals. Net3 alternate-layout failure requires diagnosis before any cross-layout performance claim; additional networks, layouts, and independently calibrated measurement models remain required.
- The λ=0.02 frontier point and EIG-per-cost result warrant replication across independently generated ensembles, sensor layouts, and source-calibrated sampling/transport assumptions before policy selection.
- The Phase-0 100-scenario parallel timing and frozen-sensor serialized-storage measurements remain to be added. No performance claim is justified yet.
- The analytic runner remains a correctness oracle. The evaluation path is simulator-derived and remains an integration result rather than an operational validation result.
