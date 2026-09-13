# Cost-aware water-network investigation

This repository starts with a deliberately small **feasibility spike** for a future investigation system for simulated water-distribution events. The intended system will maintain competing explanations, select the next observation based on expected information and operational cost, update its belief when evidence returns, and evaluate the decision policy against baselines.

This is not an LLM wrapper, and it does not claim that Bayesian inference or expected information gain is novel. The project framing, prior-art constraints, and planned milestones are in [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), [RESEARCH-REPORT.md](RESEARCH-REPORT.md), and [VERIFICATION-REPORT.md](VERIFICATION-REPORT.md).

## What works today

The current milestone proves two foundations independently:

1. An exact, discrete Bayesian harness validates posterior updates, entropy, expected information gain (EIG), action scoring, seeded replay, and delayed evidence handling.
2. An EPyT-Flow probe runs Net3 and L-Town water-network simulations and normalizes pressure, flow, and quality output shapes for contamination, leak, and sensor-fault scenarios.

The analytic harness remains the correctness oracle. The simulator path now produces a seeded Net3 ensemble and empirical held-out policy evaluation, but it remains a synthetic integration benchmark rather than a deployment claim.

## Prerequisites

- Python 3.12 or later
- A working C/C++ runtime compatible with EPANET-PLUS for your platform
- Network access on the first probe run, so EPyT-Flow can download bundled network inputs into `.cache/networks/`

## Setup

Create a virtual environment and install the declared runtime and test dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'
```

The project pins EPyT-Flow to `0.17.2`. The local `.venv/` and downloaded network cache are ignored by Git.

## Run and verify

Run the correctness suite:

```bash
.venv/bin/python -m pytest -q
```

Run a deterministic, analytic investigation episode:

```bash
.venv/bin/python -m water_investigation.demo --seed 7
```

The output lists candidate actions with their EIG and EIG-per-cost score, the selected action, delayed evidence arrival, and the posterior after each update. The hidden hypothesis is selected from the seed but is not printed.

Run the real Net3 integration probe:

```bash
.venv/bin/python -m water_investigation.probe --network net3
```

Run an L-Town timing smoke check:

```bash
.venv/bin/python -m water_investigation.probe --network ltown --classes sensor_fault
```

Build the first reproducible Net3 ensemble and evaluate it:

```bash
.venv/bin/python -m water_investigation.ensemble --per-class 40 --seed 20260911
.venv/bin/python -m water_investigation.evaluation --episodes 100 --seed 20260911
```

The ensemble command stores local compressed traces in `artifacts/net3-ensemble.npz`; the evaluation command trains empirical action likelihoods on an even-indexed stratified subset and evaluates policies on odd-indexed held-out scenarios. Its report is written to `artifacts/net3-evaluation.json`.

The evaluation now uses a seeded instrument-level measurement model rather than categorical outcome-flip rates. Its assumptions, bounds, source links, and limitations are documented in [measurement-model-sources.md](docs/research/measurement-model-sources.md).

The report compares five policies: EIG-per-cost, risk-aware expected classification accuracy, cost-insensitive expected classification accuracy, random, and cheapest-first. The expected-accuracy policy is intentionally a diagnostic baseline; it exposes the accuracy/cost tradeoff rather than replacing the cost-aware policy.

Chemical observations retain four pre-specified concentration bands rather than only a binary detection: below the method limit, trace (below 0.10 mg/L), elevated (0.10–0.50 mg/L), and high (at least 0.50 mg/L). The same bands are used when estimating discrete likelihoods from the small training split; this is intentionally more defensible than fitting an unsupported continuous density. The field and lab methods retain their distinct documented detection/sensitivity limits, but the available source material does not support claiming a more precise lab error distribution.

Field and delayed lab assays are modeled as separate seeded readings. If one is observed first, the evaluator replaces the other action's marginal likelihood with an empirical conditional likelihood for that observed concentration band. This prevents the policy from treating correlated assays as independent while retaining the value of a confirmation sample.

Generate the paired risk-aware frontier with bootstrap intervals:

```bash
.venv/bin/python -m water_investigation.frontier --episodes 100 --seed 20260912
```

This writes `artifacts/net3-risk-frontier.json`. It sweeps the cost penalty in expected reduction of classification risk; it does not tune a penalty against the held-out result.

Run the larger paired benchmark used for the current finding:

```bash
.venv/bin/python -m water_investigation.ensemble --per-class 200 --seed 20260911 --output artifacts/net3-benchmark-ensemble.npz
.venv/bin/python -m water_investigation.benchmark --ensemble artifacts/net3-benchmark-ensemble.npz --episodes 100 --seeds 20260911,20260912,20260913,20260914,20260915
```

The benchmark stores a compact, tracked report at `artifacts/net3-multiseed-benchmark.json`. It compares EIG-per-cost with each policy on identical episodes and reports deterministic bootstrap intervals for paired accuracy and cost differences. The five seeds resample episodes from one fixed, 600-scenario Net3 ensemble; they are not independent simulator-network replications.

The operational-readiness foundation adds a read-only telemetry seam, synthetic SCADA adapter, shadow-mode advisory records, and append-only JSONL audit ledger. It deliberately exposes no actuator/control interface. See [operational-readiness.md](docs/operational-readiness.md) for the utility shadow-mode protocol, acceptance gates, and validation roadmap.

Exercise the synthetic, advisory-only workflow locally:

```bash
.venv/bin/python -m water_investigation.shadow_demo
```

This appends two synthetic records to `artifacts/shadow-demo.jsonl`, which is ignored by Git. It is a contract demonstration, not a SCADA connection or operational recommendation.

Each probe writes a structured report to `artifacts/<network>-probe.json`. A report contains successful scenario summaries and failures separately; simulator failures are evidence to investigate, not silently discarded output.

## Architecture

```text
Analytic categorical world                 EPyT-Flow probe
──────────────────────────                 ───────────────
known likelihood tables                    hidden simulator event
          │                                           │
          ▼                                           ▼
Bayes update / entropy / EIG                 normalized SCADA summaries
          │                                           │
          ▼                                           ▼
cost-and-latency action score               JSON feasibility findings
          │
          ▼
seeded delayed-evidence episode
```

The two paths must stay distinct until the simulator path can estimate likelihoods from a reproducible scenario ensemble. More detail is in [docs/spike-architecture.md](docs/spike-architecture.md).

## Repository map

- `water_investigation/analytic.py` — exact categorical posterior, entropy, EIG, and score functions.
- `water_investigation/world.py` — seeded delayed-evidence episode model and analytic action likelihoods.
- `water_investigation/demo.py` — command-line presentation of a deterministic analytic episode.
- `water_investigation/probe.py` — EPyT-Flow Net3/L-Town simulator feasibility probe.
- `tests/` — analytic correctness and replay tests.
- `FINDINGS.md` — measured environment results and open risks.
- `docs/` — operational and architectural documentation.

## Current boundaries

The spike deliberately excludes persistent workflow state, a UI, LLM processing, human approval gates, interventions such as hydrant flushes, field-data calibration, and independent network replications. It stores reproducible local scenario ensembles and a synthetic benchmark report, but does not support deployment, safety, or real-world cost-savings claims.

The evaluation admits only held-out episodes whose instrument-perturbed, simulator-derived initial telemetry leaves at least two plausible classes. The next technical gate is external validity: repeat the benchmark across independently generated ensembles, sensor layouts, and source-calibrated sampling/transport assumptions. See [FINDINGS.md](FINDINGS.md) for the current evidence and blockers.
