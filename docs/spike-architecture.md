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

`water_investigation.evaluation` converts held-out traces into categorical results for field chlorine sampling, lab chlorine assay, portable pressure observation, and waiting. It estimates each action's likelihood table from an even-indexed stratified training split using Laplace smoothing, then evaluates only odd-indexed scenarios. Field and lab are separately seeded samples. After either assay returns, the other assay's marginal likelihood is replaced with an empirical conditional likelihood for the observed first band. This keeps the confirmation action available without treating correlated results as conditionally independent.

The current 0.75 conclusion threshold and action outcome thresholds are harness parameters, not domain-calibrated operational policy. The report includes accuracy, mean cost, mean action count, and cost when correct for EIG-per-cost, random, and cheapest-first policies.

## Ambiguous episodes and noisy evidence

The evaluator now extracts an `initial_telemetry` categorical outcome from the first 12 hours of each simulator trace, relative to the stored no-event baseline. It combines early quality and pressure deviations into one of `quality_signal`, `pressure_high`, `pressure_low`, or `unresolved`.

Every channel has a deterministic, scenario-seeded categorical noise rate. Current rates are 0.45 for initial telemetry, 0.10 for field sampling, 0.02 for lab assay, 0.12 for portable pressure readings, and 0 for waiting. The same scenario and channel always produce the same noisy outcome, so training/evaluation remain reproducible.

The likelihood model built from training scenarios updates the initial uniform prior. A held-out scenario is eligible only if its largest initial posterior is at most 0.70 and its second-largest posterior is at least 0.15. The evaluation report records both the eligible and rejected counts, the gate values, and noise rates.

These noise rates are deliberate harness controls, not calibrated sensor-error estimates. The benchmark now tests action selection from ambiguous initial state, but no resume-quality claim is valid until noise and thresholds are estimated or validated against a more realistic measurement model.

## Instrument-level measurement model

`water_investigation.measurement` replaces the former categorical flip-rate model with seeded draws at the observation layer. The model treats the TE M3200 pressure transducer's ±0.25% full-scale accuracy as a bounded uniform interval for a selected 100 psi deployment, yielding a ±0.25 psi pressure measurement bound. It treats the published Hach chlorine-method 95% intervals as explicit normal approximations for field and lab assay draws, while preserving their documented field lower range (0.02 mg/L) and lab sensitivity (0.03 mg/L).

The complete source links and assumptions are in [measurement-model-sources.md](research/measurement-model-sources.md). The sources characterize ideal-condition product/method performance; they do not model collection, transport, hydraulic-model, or site-specific error. The run report stores each seeded numeric draw and its model parameters alongside the categorical result.

The ensemble injection scale is now chosen so contaminant concentrations span the field method's cited 0.02–2.0 mg/L range. Under this model, 40 of 60 held-out scenarios pass the ambiguity gate. EIG-per-cost reduces cost relative to the baselines but has lower accuracy than random in the first 100-episode run, so it is a diagnostic result—not an improvement claim.

## Policy-diagnosis baseline

The evaluator includes an `expected_accuracy` policy that ranks actions by expected post-observation MAP classification accuracy and uses cost only as a tie-breaker. It is deliberately not cost-aware. Its purpose is to distinguish a weak acquisition objective from weak observations: if it improves accuracy but costs more, the action model contains useful information and the cost-aware objective needs refinement.

In the first instrument-level run, EIG-per-cost made most of its errors by choosing the low-cost field assay, receiving a false positive, and classifying a leak as contamination. The expected-accuracy policy instead chooses the lab assay, increasing accuracy from 83% to 88% at mean cost 5.00. Random reached 90% on the same 100 paired episodes. This is an accuracy/cost frontier diagnostic, not evidence that any policy wins.

## Quantitative assay bands and risk-aware frontier

The assay actions no longer collapse every valid concentration into a single `detected` outcome. They use four fixed, ordered outcomes: below the method threshold, trace (<0.10 mg/L), elevated (0.10–0.50 mg/L), and high (≥0.50 mg/L). The empirical likelihood estimator uses Laplace smoothing over these outcomes. This preserves coarse quantitative evidence while avoiding a continuous likelihood fit that the 20-scenario-per-class training split cannot support. The field and lab readings are separate seeded observations but share event magnitude; therefore, a follow-up assay uses an empirical conditional likelihood rather than an independent marginal likelihood. The cited sources establish different reporting thresholds but do not establish a distinct lab precision distribution.

The `risk_aware` policy scores an action as expected increase in MAP classification accuracy minus `λ × action cost`; it stops when no available action has positive value. `water_investigation.frontier` evaluates λ values from 0 through 0.20 on the same episodes and uses 1,000 deterministic bootstrap resamples for 95% intervals.

Conditional lab confirmation creates a nontrivial intermediate frontier point: λ=0.02 reaches 92% accuracy at mean cost 2.15 (bootstrap 95% accuracy interval 86–97%), compared with λ=0 at 88%/5.00 and λ≥0.05 at 83%/1.00. The confidence intervals overlap and the ensemble is small, so this is not evidence that λ=0.02 is generally superior. It is evidence that correlated evidence can be handled without discarding confirmation actions; larger ensembles and a source-calibrated sampling/transport model are the next validation gate.
