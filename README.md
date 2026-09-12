# Cost-aware water-network investigation

This repository starts with a deliberately small **feasibility spike** for a future investigation system for simulated water-distribution events. The intended system will maintain competing explanations, select the next observation based on expected information and operational cost, update its belief when evidence returns, and evaluate the decision policy against baselines.

This is not an LLM wrapper, and it does not claim that Bayesian inference or expected information gain is novel. The project framing, prior-art constraints, and planned milestones are in [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), [RESEARCH-REPORT.md](RESEARCH-REPORT.md), and [VERIFICATION-REPORT.md](VERIFICATION-REPORT.md).

## What works today

The current milestone proves two foundations independently:

1. An exact, discrete Bayesian harness validates posterior updates, entropy, expected information gain (EIG), action scoring, seeded replay, and delayed evidence handling.
2. An EPyT-Flow probe runs Net3 and L-Town water-network simulations and normalizes pressure, flow, and quality output shapes for contamination, leak, and sensor-fault scenarios.

The analytic harness is the correctness oracle. The simulator probe is intentionally separate: it has not yet produced the seeded scenario ensemble or calibrated likelihood model needed for simulator-derived policy decisions.

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

The report compares four policies: EIG-per-cost, expected post-action classification accuracy, random, and cheapest-first. The expected-accuracy policy is intentionally a cost-insensitive diagnostic baseline; it exposes the accuracy/cost tradeoff rather than replacing the cost-aware policy.

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

The spike deliberately excludes persistent workflow state, a UI, LLM processing, human approval gates, interventions such as hydrant flushes, scenario-ensemble storage, and benchmark claims. Do not report policy quality, cost savings, or calibration results from the current code.

The evaluation now admits only held-out episodes whose instrument-perturbed, simulator-derived initial telemetry leaves at least two plausible classes. The next technical gate is a policy improvement: EIG-per-cost currently saves cost but trails random on accuracy under the new model. See [FINDINGS.md](FINDINGS.md) for the current evidence and blockers.
