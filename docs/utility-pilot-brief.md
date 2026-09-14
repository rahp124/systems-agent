# Water Investigation Agent: offline replay pilot

## Purpose

The Water Investigation Agent is a read-only decision-support agent for investigating suspected distribution-system events. Given time-stamped telemetry, it maintains competing explanations and recommends the next investigative observation—such as a field chlorine sample, delayed lab assay, portable pressure reading, or waiting for telemetry—while recording the evidence and rationale.

This proposed pilot is an **offline replay**. It does not connect to live SCADA, issue operational commands, control pumps or valves, change treatment, or replace utility procedures. Its purpose is to determine whether the agent produces useful, auditable recommendations when replayed against resolved historical investigations.

## Requested collaboration

Provide a de-identified export covering approximately 6–24 months and, where available, 10–50 resolved investigations involving leaks, water-quality anomalies, sensor faults, or comparable operational events.

The minimum telemetry export is CSV with:

- `snapshot_id`, `captured_at`, and a source identifier;
- numeric sensor values or deviations, with sensor type and location metadata supplied separately or pseudonymized;
- strictly ordered timestamps; and
- no customer information, credentials, control paths, or sensitive infrastructure fields that the utility does not approve for sharing.

For resolved events, a separate review file can contain an investigation/ticket reference, operator disposition, action taken, resolution class, and relevant laboratory or maintenance outcome. The utility retains ownership of all data and approves the transfer, retention, access, and deletion terms before any exchange.

## What the utility receives

1. A reproducible offline replay using the supplied export; no production integration.
2. An append-only advisory audit record for each replayed telemetry snapshot, including evidence, recommended action, confidence, rationale, and policy/configuration version.
3. A validation report covering data quality, review coverage, resolved-label coverage, reviewer dispositions, operator-action agreement with uncertainty, event-grouped first-advisory timing where event IDs are supplied, known failure cases, and metrics agreed before analysis.
4. A closeout discussion and written recommendation: stop, refine offline evaluation, or consider a limited read-only shadow pilot.

## Safety and security posture

- The agent is advisory-only and read-only. It has no interface for actuator, treatment, or operational control.
- Data should be transferred only through utility-approved channels. Access is least-privilege and limited to the agreed replay scope.
- Results are reviewed with utility staff; an agent recommendation never authorizes or delays an operational response.
- The pilot has a documented owner, security contact, incident-response contact, retention period, and deletion procedure.

## Pre-agreed evaluation gates

Before data analysis begins, the utility and team define:

| Area | Example evidence |
| --- | --- |
| Data quality | Completeness, latency, timestamp order, missing channels, provenance, and export coverage. |
| Decision quality | Recall for known high-consequence events, false-negative rate, calibration, time-to-triage, and operator-action agreement. Current code reports only metrics supported by supplied reviewer fields; unavailable labels remain unavailable. |
| Safety | Read-only access confirmation, manual fallback, escalation path, and no-control verification. |
| Security | Approved transfer method, access review, audit retention, dependency review, and data-deletion procedure. |
| Go/no-go | Written criteria for ending offline replay, refining the model, or proposing shadow mode. |

No success metric is assumed in advance. Current results are from synthetic water-network simulation and will not be represented as utility performance.

## Suggested sequence

1. 30-minute scoping call: intended use, data availability, approvals, and success criteria.
2. Utility-approved de-identified export and data dictionary.
3. Offline replay and joint review of audit records, metrics, and failure cases.
4. Written closeout decision. Only if both parties agree and gates are met, scope a time-limited, read-only shadow pilot.

## Current technical readiness

The repository includes a read-only historian CSV adapter, a synthetic SCADA adapter, versioned advisory records, append-only JSONL audit storage, data-quality checks, and replay reconciliation. The current benchmark uses a synthetic Net3 water-network ensemble; real utility data has not yet been analyzed.

Technical details and the shadow-mode protocol are available in [operational-readiness.md](operational-readiness.md).
