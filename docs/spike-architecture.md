# Feasibility spike architecture

## Purpose

The spike answers two narrow questions before application work begins:

1. Are the Bayesian update and expected-information-gain calculations correct?
2. Can the chosen simulator express contamination, leaks, and sensor faults through a common observation interface?

It does not yet answer whether an information-theoretic policy outperforms a baseline. That requires a simulator-derived ensemble and held-out evaluation episodes.

## Analytic decision path

`water_investigation.analytic` models a finite hypothesis set `H`, a belief distribution `p(H)`, and an action-specific observation model `p(o | H, a)`.

For an observed outcome `o`, the posterior is:

```text
p(h | o, a) = p(o | h, a) p(h) / Σh' p(o | h', a) p(h')
```

Entropy is measured in bits:

```text
H(p) = -Σh p(h) log2 p(h)
```

For each possible action, EIG is the prior entropy minus expected posterior entropy:

```text
EIG(a) = H(p) - Σo p(o | a) H(p(H | o, a))
```

The spike chooses the affordable action with the highest score:

```text
score(a) = EIG(a) / (cost(a) + 0.25 × latency_steps(a))
```

The `0.25` latency penalty is only a transparent harness parameter. It is not a final operational-cost model and must be replaced with a documented, evaluated objective before any project claim.

## Episode state and timing

An `Episode` contains evaluator-only ground truth, the current belief, a budget, simulated clock, pending actions, and materialized evidence. Scheduling an action immediately charges its cost but returns evidence only at `clock + latency_steps`. Each `advance()` call materializes all due evidence and applies one Bayes update per item.

All random behavior is seeded. Replaying an episode with the same seed and action sequence must yield the same hidden class, outcomes, evidence sequence, and posterior.

## Simulator probe contract

The probe uses EPyT-Flow 0.17.2 and EPANET-PLUS. It:

- downloads the requested Net3 or L-Town input only when it is absent from `.cache/networks/`;
- sets four pressure sensors, one flow sensor, and two quality sensors;
- runs a 48-hour simulation while preserving the network's bundled compatible hydraulic/quality cadence;
- models contamination as a chemical mass source, a leak as a finite abrupt node leakage, and a sensor fault as a retained hydraulic trace plus a post-processed pressure shift;
- writes either a compact summary or a captured exception for every requested class.

The report schema is:

```json
{
  "network": "net3",
  "results": [
    {
      "event_class": "leak",
      "runtime_seconds": 0.0,
      "pressure_shape": [49, 4],
      "flow_shape": [49, 1],
      "quality_shape": [49, 2],
      "pressure_mean": 0.0,
      "flow_mean": 0.0,
      "quality_max": 0.0
    }
  ],
  "failures": []
}
```

`failures` retains the event class, exception representation, and traceback. A caller must inspect this field before treating a run as successful.

## Important constraints

- `AbruptLeakage` in the pinned EPyT-Flow version requires a finite `end_time`; an open-ended event overflows during initialization.
- Leakage simulation requires a compatible flow unit. The probe sets `EN_CFS`.
- The probe does not alter the bundled network's hydraulic/quality cadence because EPyT validates the two settings eagerly.
- Probe summaries are observability data, not likelihoods. Means and maxima alone are insufficient for Bayesian inference.

## Required next interface

The next increment should introduce a versioned scenario record with: scenario ID and seed, event class and parameters, fixed sensor configuration, full or selected trace storage, convergence status, and action-conditioned observation extraction. A likelihood-estimation layer can then consume that record without accessing hidden evaluation ground truth.

## First trace-backed evaluation

`water_investigation.ensemble` now creates 40 seeded scenarios per event class by default and writes compressed pressure, flow, and quality tensors plus scenario metadata to `artifacts/net3-ensemble.npz`. A no-event baseline trace is stored alongside them so action extraction measures event deviations rather than confusing chemical concentration with Net3's default water-age channel.

`water_investigation.evaluation` converts held-out traces into categorical results for field chlorine sampling, lab chlorine assay, portable pressure observation, and waiting. It estimates each action's likelihood table from an even-indexed stratified training split using Laplace smoothing, then evaluates only odd-indexed scenarios. Field and lab assays are mutually exclusive because, in this first harness, they inspect the same physical sample; treating them as independent would double-count evidence.

The current 0.75 conclusion threshold and action outcome thresholds are harness parameters, not domain-calibrated operational policy. The report includes accuracy, mean cost, mean action count, and cost when correct for EIG-per-cost, random, and cheapest-first policies.

## Ambiguous episodes and noisy evidence

The evaluator now extracts an `initial_telemetry` categorical outcome from the first 12 hours of each simulator trace, relative to the stored no-event baseline. It combines early quality and pressure deviations into one of `quality_signal`, `pressure_high`, `pressure_low`, or `unresolved`.

Every channel has a deterministic, scenario-seeded categorical noise rate. Current rates are 0.45 for initial telemetry, 0.10 for field sampling, 0.02 for lab assay, 0.12 for portable pressure readings, and 0 for waiting. The same scenario and channel always produce the same noisy outcome, so training/evaluation remain reproducible.

The likelihood model built from training scenarios updates the initial uniform prior. A held-out scenario is eligible only if its largest initial posterior is at most 0.70 and its second-largest posterior is at least 0.15. The evaluation report records both the eligible and rejected counts, the gate values, and noise rates.

These noise rates are deliberate harness controls, not calibrated sensor-error estimates. The benchmark now tests action selection from ambiguous initial state, but no resume-quality claim is valid until noise and thresholds are estimated or validated against a more realistic measurement model.
