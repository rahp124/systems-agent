# Operational readiness package

## Scope and safety posture

This repository currently contains a synthetic, read-only decision-support agent. It must not issue pump, valve, dosing, flushing, or other control commands. Its first operational use case is narrower: rank investigative observations for a trained operator during a suspected distribution-system event. The operator remains responsible for decisions and incident-response actions.

The production seam is `TelemetryReader` in `water_investigation.operations`. Its interface reads immutable, source-attributed telemetry snapshots after an optional cursor. `SyntheticScadaAdapter` is the current adapter; a utility-owned historian adapter may replace it only when it meets the same read-only, stable-order, source-attribution, and access-control requirements. `ShadowMode` turns snapshots and an advisory policy into `ShadowAuditRecord` values. `JsonlAuditLedger` persists supplied records but does not transmit commands or connect to operational technology.

This design gives callers a small interface while containing cursor handling, serialization, and audit shape in one deep module. A later utility adapter is a replacement at the telemetry seam, not a reason to spread SCADA-specific logic through policy code.

Run `.venv/bin/python -m water_investigation.shadow_demo` to exercise the contract. It writes two synthetic, advisory-only JSONL records. The output is intentionally Git-ignored because it is regenerated demonstration output.

`HistorianCsvAdapter` is the second adapter at the telemetry seam. It reads a de-identified CSV with required `snapshot_id`, `captured_at`, and `source` columns; all remaining columns are numeric telemetry values. `water_investigation.replay` joins its advisory records with separate JSONL reviewer outcomes and reports review coverage and operator-action agreement. The examples in `docs/examples/` are synthetic schema examples, not utility data or evidence of decision quality.

## Shadow-mode protocol

1. A utility names an operational owner, security owner, incident commander, and technical product owner; they approve the intended use, data sources, retention, and escalation path.
2. The deployed adapter receives least-privilege, read-only access to a historian replica or export. It has no credentials or network route to actuators.
3. The system records each telemetry snapshot, advisory action, confidence, rationale, policy/model version, and operator disposition in an append-only audit store. The current `ShadowAuditRecord` supplies the telemetry and advisory core; utility deployment must add version and disposition fields before pilot use.
4. Operators follow normal procedures. Recommendations are shown only as shadow output and are never used to delay, replace, or authorize response actions.
5. A reviewer reconciles every alert against incident tickets, laboratory results, maintenance records, and eventual resolution. Unknown outcomes remain unknown; they are not relabeled to improve metrics.
6. The pilot ends with a written go/no-go decision against the acceptance gates below.

EPA's [distribution-system contamination incident checklist](https://www.epa.gov/waterutilityresponse/incident-action-checklists-water-utilities) is a useful reference for fitting this workflow into existing response procedures. EPA also provides water-sector [cybersecurity planning resources](https://www.epa.gov/cyberwater/cybersecurity-planning); utility security requirements take precedence over this agent's assumptions.

## Acceptance gates

Before a limited operator-facing pilot, define these values with the utility and freeze them for the shadow period:

| Gate | Required evidence |
| --- | --- |
| Safety | Read-only access verified; no actuator path; documented manual fallback and incident escalation. |
| Data quality | Completeness, latency, clock skew, missing-channel behavior, and source provenance measured on the actual feed. |
| Decision quality | Locked historical and prospective labels; false-negative rate for high-consequence events, calibration, time-to-triage, operator agreement, and cost measured with uncertainty. |
| Security | Threat model, access review, audit retention, dependency review, and incident-response ownership approved. |
| Human factors | Explanations, confidence, evidence provenance, override/disposition capture, and training reviewed with operators. |
| Change control | Versioned policy/configuration, rollback procedure, monitoring, drift thresholds, and revalidation trigger defined. |

Use a utility-specific risk register to prioritize the gates. NIST's AI Risk Management Framework frames this work as continuous governance, context mapping, measurement, and management, including documented testing and monitoring before and during operation. [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)

## Validation roadmap

1. **Offline replay:** run against de-identified historian exports and locked incident labels; compare with actual operator investigations.
2. **Shadow mode:** run prospectively without affecting operations; collect audit records and operator dispositions.
3. **Limited pilot:** expose recommendations to trained operators with explicit human approval and defined rollback.
4. **Ongoing validation:** monitor data drift, missing telemetry, calibration, false negatives, latency, cybersecurity events, and operator overrides; revalidate after model, configuration, network, or sensor changes.

No step automatically authorizes the next. The utility's documented go/no-go decision, legal obligations, and applicable jurisdictional requirements control progression.
