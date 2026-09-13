"""Offline replay and reviewer reconciliation for de-identified historian exports."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from statistics import mean

from .operations import (Advisory, HistorianCsvAdapter, InvestigationAction,
                         JsonlAuditLedger, ShadowAuditRecord, ShadowMode,
                         TelemetrySnapshot)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT = ROOT / "artifacts" / "offline-replay.jsonl"


class OperatorDisposition(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    NO_ACTION = "no_action"


@dataclass(frozen=True)
class ReviewOutcome:
    snapshot_id: str
    disposition: OperatorDisposition
    operator_action: InvestigationAction | None = None
    event_class: str | None = None


def load_outcomes(path: Path) -> dict[str, ReviewOutcome]:
    outcomes = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        outcome = ReviewOutcome(item["snapshot_id"], OperatorDisposition(item["disposition"]),
                                InvestigationAction(item["operator_action"])
                                if item.get("operator_action") else None,
                                item.get("event_class"))
        if outcome.snapshot_id in outcomes:
            raise ValueError("review outcomes must have unique snapshot IDs")
        outcomes[outcome.snapshot_id] = outcome
    return outcomes


def reconcile(records: tuple[ShadowAuditRecord, ...], outcomes: dict[str, ReviewOutcome]) -> dict[str, object]:
    record_ids = {record.snapshot_id for record in records}
    if unknown := set(outcomes) - record_ids:
        raise ValueError(f"review outcomes reference unknown snapshots: {sorted(unknown)}")
    reviewed = [record for record in records if record.snapshot_id in outcomes]
    action_reviews = [record for record in reviewed if outcomes[record.snapshot_id].operator_action]
    agreements = [record.advisory.action == outcomes[record.snapshot_id].operator_action
                  for record in action_reviews]
    channels = sorted({channel for record in records for channel in record.telemetry})
    return {"snapshots": len(records), "reviewed_snapshots": len(reviewed),
            "review_coverage": len(reviewed) / len(records) if records else 0.0,
            "action_reviews": len(action_reviews),
            "operator_action_agreement": mean(agreements) if agreements else None,
            "data_quality": {"timestamp_ordered": True, "telemetry_channels": channels,
                             "sources": sorted({record.source for record in records})},
            "versions": sorted({(record.policy_version, record.configuration_version)
                                for record in records}),
            "resolved_event_classes": sorted({outcomes[record.snapshot_id].event_class
                                                for record in reviewed
                                                if outcomes[record.snapshot_id].event_class})}


def conservative_policy(snapshot: TelemetrySnapshot) -> Advisory:
    if snapshot.values.get("quality_delta_mg_l", 0.0) >= 0.02:
        return Advisory(InvestigationAction.FIELD_CHLORINE, 0.70, "quality delta exceeds field range")
    if abs(snapshot.values.get("pressure_delta_psi", 0.0)) >= 0.25:
        return Advisory(InvestigationAction.PORTABLE_PRESSURE, 0.65, "pressure delta exceeds bound")
    return Advisory(InvestigationAction.WAIT, 0.50, "no replay threshold exceeded")


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay a de-identified historian export in shadow mode.")
    parser.add_argument("--telemetry", type=Path, required=True)
    parser.add_argument("--reviews", type=Path, required=True)
    parser.add_argument("--audit-output", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--policy-version", default="replay-threshold-v1")
    parser.add_argument("--configuration-version", default="offline-replay-v1")
    args = parser.parse_args()
    records = ShadowMode(HistorianCsvAdapter(args.telemetry), conservative_policy,
                         args.policy_version, args.configuration_version).run()
    JsonlAuditLedger(args.audit_output).append(records)
    print(json.dumps(reconcile(records, load_outcomes(args.reviews)), indent=2))


if __name__ == "__main__":
    main()
