# Offline replay validation protocol

This protocol is frozen before receiving collaborator data. It governs a read-only, de-identified offline replay; it does not authorize a live connection, control action, or operational recommendation.

## Unit of analysis and inclusion

- A telemetry snapshot has a unique ID, ISO-8601 capture time, source attribution, and a complete approved channel map.
- An event group has a reviewer-supplied `event_id`; its resolved label and severity are locked before scoring.
- Include only groups inside the agreed time window with all required channels, a valid chronology, and an independently locked review outcome.
- Report excluded snapshots and event groups with their reason. Do not impute missing telemetry, labels, or dispositions.

## Frozen measures

| Measure | Definition | Availability requirement |
| --- | --- | --- |
| Review and label coverage | Reviewed or resolved-labeled snapshots divided by all replayed snapshots | Always report. |
| Operator-action agreement | Advisory action equals the reviewer-recorded operator action; report Wilson 95% interval | Operator action present. |
| First-advisory time | Seconds from first event-grouped snapshot to first non-wait advisory | `event_id` present. |
| High-consequence recall | Resolved high-consequence groups receiving an agreed qualifying advisory within the frozen window | Severity, resolution, qualifying action, and window present. |
| False-negative rate | High-consequence groups with no qualifying advisory divided by all such groups | Same as recall. |
| Confidence calibration | Reliability by predeclared confidence bins, with event-level outcome | Sufficient locked labels. |

No metric is substituted for one whose required fields are absent. The current implementation reports the first three where its reviewer schema permits; it must not report recall, false-negative rate, or calibration without the corresponding locked data.

## Analysis controls

1. Record export checksum, retrieval date, data dictionary, approved channel map, policy version, and configuration version before replay.
2. Run the replay once against the frozen export; retain append-only advisory records.
3. Reconcile against a separate locked reviewer file. Never use resolution labels as policy inputs.
4. Stratify all reported metrics by event class, severity, data completeness, and source only when each stratum has enough agreed observations; otherwise report counts without a rate.
5. Record failure cases, exclusions, overrides, and disagreement examples. No post-hoc threshold tuning is scored against the same locked set.

## Decision gates

Offline replay can proceed to a utility-approved shadow-mode proposal only when the utility, not this repository, approves the data-quality results, metric definitions, acceptable uncertainty, security review, manual fallback, and escalation process. A missed high-consequence event, material data-quality failure, or unapproved scope change stops the analysis pending joint review.
