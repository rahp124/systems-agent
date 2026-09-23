# Water Investigation Agent

The unified utility/research experience first explains what the agent is for, then lets visitors run a seeded synthetic investigation through a guided workspace. Every observation is presented in human order—recommended check, reason, returned evidence, interpretation, and before/after belief—while full EIG, cost, score, and ranking details remain available for audit. Utility and research tabs separate evaluation readiness from reproducibility material without hiding the shared safety boundaries. Synthetic output and public context are never presented as field validation. Start it with `make app`, then open `http://127.0.0.1:8000`. The browser lab calls the repository's actual Bayesian harness; it is not a prerecorded mock result.

### Hosting split

GitHub Pages can host the static `showcase/` experience, but it cannot execute the Python investigation endpoint. The browser reads `showcase/config.js`; leave `WATER_AGENT_API_BASE` empty for local same-origin mode, or set it to the deployed API origin for Pages. The Python service accepts `HOST` and `PORT`, exposes `GET /health`, and only permits cross-origin requests from `WATER_AGENT_ALLOWED_ORIGIN` (set this to the exact Pages origin, including `https://`).

Render is the initial free-hosting target for the API. Its free web services sleep after inactivity and have ephemeral filesystems, so this service remains stateless by design. The repository includes [`render.yaml`](render.yaml): create a Render Blueprint from it, set `WATER_AGENT_ALLOWED_ORIGIN` to the eventual Pages origin, and let Render provide `PORT`; the service defaults `HOST` to `127.0.0.1` locally but Render should set `HOST=0.0.0.0`. After Render supplies the service URL, place that origin in `showcase/config.js` before publishing Pages.

The GitHub Pages workflow assembles the showcase at the site root, copies only the documented public reports and pages, and deploys on pushes to `main`. Add a repository variable named `RENDER_API_BASE_URL` containing the Render origin (for example, `https://water-investigation-agent.onrender.com`) before the first Pages deployment. In Render, set `WATER_AGENT_ALLOWED_ORIGIN` to the resulting Pages origin (for a project site, usually `https://<account>.github.io/<repository>`). Keep both values origin-only: no trailing `/api` path and no credentials.

For the no-card PythonAnywhere deployment, use [`water_investigation/wsgi.py`](water_investigation/wsgi.py) as the WSGI entry point. Set the web app's source directory to the repository root, add the repository parent directory to `sys.path` in the WSGI configuration, and set `WATER_AGENT_ALLOWED_ORIGIN` to the GitHub Pages origin. The WSGI adapter exposes the same `/health` and `/api/investigate` endpoints as the local server; it does not add persistence or operational-system access.

The Water Investigation Agent is a cost-aware, auditable decision-support system for simulated water-distribution events. It maintains competing explanations, selects the next observation based on expected information and operational cost, updates its belief when evidence returns, and evaluates its decision policy against baselines.

This is not an LLM wrapper, and it does not claim that Bayesian inference or expected information gain is novel. Its scope, prior-art constraints, and validation record are in [AGENT_CONTEXT.md](AGENT_CONTEXT.md), [PRIOR_ART_REPORT.md](PRIOR_ART_REPORT.md), and [VERIFICATION-REPORT.md](VERIFICATION-REPORT.md).

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

The agent pins EPyT-Flow to `0.17.2`. The local `.venv/` and downloaded network cache are ignored by Git.

## Run and verify

Run the correctness suite:

```bash
.venv/bin/python -m pytest -q
```

Run the complete synthetic, fail-closed operational demonstration with one command:

```bash
make demo
```

Run the complete browser experience:

```bash
make app
```

### Verify tracked evidence

Verify that every tracked public-data or replication report retains its required provenance and schema fields:

```bash
.venv/bin/python -m water_investigation.verify_artifacts
```

The final synthetic benchmark is prespecified in [`benchmark_protocol.json`](benchmark_protocol.json). To build any missing independent Net3/L-Town ensembles and regenerate its summary:

```bash
.venv/bin/python -m water_investigation.final_benchmark --build
```

The tracked summary reports absolute metrics, hierarchical confidence intervals, paired baseline comparisons, and failure modes. Generated `.npz` traces remain local because they are reproducible from the frozen seeds.

GitHub Actions runs both checks on every push and pull request, including strict third-party dependency auditing from [`requirements-audit.txt`](requirements-audit.txt). The local editable package is intentionally excluded because it is not published to PyPI. Public-source reports are reproducible from their documented queries and checksums; the raw downloads remain local and ignored.

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

The same ensemble/evaluation path can make network topology and sensor layout explicit:

```bash
.venv/bin/python -m water_investigation.ensemble --network net3 --sensor-layout alternate --per-class 40 --seed 20260914
.venv/bin/python -m water_investigation.ensemble --network ltown --sensor-layout primary --per-class 40 --seed 20260915
```

Each ensemble records its network and sensor layout in metadata, and evaluation carries that metadata into its report. Network cadence is derived from returned traces for sensor-fault timing. These runs are separate synthetic replications, not a pooled benchmark or a claim of cross-network policy generalization.

Create a compact, non-pooled summary after generating separate artifacts:

```bash
.venv/bin/python -m water_investigation.replication \
  --ensemble artifacts/net3-alternate-replication.npz \
  --ensemble artifacts/ltown-primary-replication.npz \
  --episodes 100 --seed 20260915
```

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

Replay a de-identified historian export with separate reviewer outcomes:

```bash
.venv/bin/python -m water_investigation.replay \
  --telemetry docs/examples/historian-replay.csv \
  --reviews docs/examples/historian-reviews.jsonl \
  --channel-map docs/examples/historian-channel-map.json
```

The replay writes advisory-only audit records to `artifacts/offline-replay.jsonl` and reports review coverage, dispositions, resolved-label coverage, operator-action agreement with a Wilson interval, and event-grouped time to first non-wait advisory when reviewers provide an optional `event_id`. It does not treat missing reviews as negative evidence or establish operational performance.

Run the local synthetic operational-pilot safety gate:

```bash
.venv/bin/python -m water_investigation.synthetic_pilot \
  --telemetry docs/examples/historian-replay.csv \
  --channel-map docs/examples/historian-channel-map.json \
  --required-channel pressure_delta_psi --required-channel quality_delta_mg_l
```

It fails closed when required channels are absent or telemetry gaps exceed the configured limit. It is strictly a local readiness check, not a live SCADA connector or shadow-mode authorization.

For utilities, laboratories, and research partners, [utility-pilot-brief.md](docs/utility-pilot-brief.md) defines the requested de-identified data, read-only safety posture, deliverables, and offline-replay evaluation gates.

Before accepting any collaborator export, use the frozen [offline replay validation protocol](docs/validation-protocol.md) and [data-handling and security review](docs/data-handling-security.md).

The reusable contact template, qualification checklist, and scoping-call agenda are in [partner-outreach.md](docs/partner-outreach.md). It supports outreach preparation only; no external contact is made from this repository.

Analyze an official EPA SDWIS public compliance export locally:

```bash
.venv/bin/python -m water_investigation.public_data \
  --input docs/examples/sdwis-violations.csv \
  --pwsid-prefix CA \
  --output artifacts/sdwis-public-report.json
```

The command accepts the SDWIS violations CSV or ZIP download and reports public compliance context. It does not infer operational incidents or validate agent recommendations; see [public-data.md](docs/public-data.md).

The first sourced public-data result is recorded in [public-data-results.md](docs/public-data-results.md).

Download a bounded Water Quality Portal monitoring-results query and create a compact report:

```bash
.venv/bin/python -m water_investigation.wqp_data \
  --download-to .cache/wqp/wisconsin-017-nitrate.csv \
  --state-fips 55 --county-fips 017 --characteristic Nitrate \
  --output artifacts/wqp-public-report.json
```

The CSV stays local under `.cache/`; the report preserves the exact query URL and checksum. WQP results are historical public monitoring context, not operational telemetry or validation of agent recommendations. See [public-data.md](docs/public-data.md).

Download a bounded CDC NORS drinking-water outbreak extract and summarize its reported public-health outcomes:

```bash
.venv/bin/python -m water_investigation.nors_data \
  --download-to .cache/nors/drinking-water.csv \
  --start-year 1971 --end-year 2023 \
  --output artifacts/nors-drinking-water-public-report.json
```

NORS records are reported outbreak context with illnesses, hospitalizations, and deaths—not utility telemetry, a matched water-system event log, or evidence of agent performance. See [public-data.md](docs/public-data.md).

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

The two paths must stay distinct until the simulator path can estimate likelihoods from a reproducible scenario ensemble. More detail is in [docs/agent-architecture.md](docs/agent-architecture.md).

## Repository map

- `water_investigation/analytic.py` — exact categorical posterior, entropy, EIG, and score functions.
- `water_investigation/world.py` — seeded delayed-evidence episode model and analytic action likelihoods.
- `water_investigation/demo.py` — command-line presentation of a deterministic analytic episode.
- `water_investigation/probe.py` — EPyT-Flow Net3/L-Town simulator feasibility probe.
- `tests/` — analytic correctness and replay tests.
- `FINDINGS.md` — measured environment results and open risks.
- `docs/` — operational and architectural documentation.

## Current boundaries

The current agent includes a local browser investigation UI, synthetic scenario ensembles, separate small network/layout replications, read-only historian replay, and an append-only advisory audit seam. It excludes live SCADA connectivity, persistent multi-user workflow state, LLM processing, implemented human-approval workflow, interventions such as hydrant flushes, and field-data calibration. It does not support deployment, safety, or real-world cost-savings claims.

The evaluation admits only held-out episodes whose instrument-perturbed, simulator-derived initial telemetry leaves at least two plausible classes. The next technical gate is external validity: repeat the benchmark across independently generated ensembles, sensor layouts, and source-calibrated sampling/transport assumptions. See [FINDINGS.md](FINDINGS.md) for the current evidence and blockers.
