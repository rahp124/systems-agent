"""Offline replay and reviewer reconciliation for de-identified historian exports."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
from statistics import mean, median

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
    event_id: str | None = None


def load_outcomes(path: Path) -> dict[str, ReviewOutcome]:
    outcomes = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        outcome = ReviewOutcome(item["snapshot_id"], OperatorDisposition(item["disposition"]),
                                InvestigationAction(item["operator_action"])
                                if item.get("operator_action") else None,
                                item.get("event_class"), item.get("event_id"))
        if outcome.snapshot_id in outcomes:
            raise ValueError("review outcomes must have unique snapshot IDs")
        outcomes[outcome.snapshot_id] = outcome
    return outcomes


def load_channel_map(path: Path) -> dict[str, str]:
    mapping = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(mapping, dict) or not all(isinstance(source, str) and isinstance(target, str)
                                                for source, target in mapping.items()):
        raise ValueError("channel map must be a JSON object mapping source columns to output names")
    return mapping


def _wilson_interval(successes: int, total: int, z: float = 1.96) -> list[float] | None:
    if not total:
        return None
    proportion = successes / total
    denominator = 1 + z ** 2 / total
    centre = (proportion + z ** 2 / (2 * total)) / denominator
    half_width = z * ((proportion * (1 - proportion) / total + z ** 2 / (4 * total ** 2)) ** 0.5) / denominator
    return [max(0.0, centre - half_width), min(1.0, centre + half_width)]


def _event_timing(records: tuple[ShadowAuditRecord, ...], outcomes: dict[str, ReviewOutcome]) -> dict[str, object]:
    groups: defaultdict[str, list[ShadowAuditRecord]] = defaultdict(list)
    for record in records:
        outcome = outcomes.get(record.snapshot_id)
        if outcome and outcome.event_id:
            groups[outcome.event_id].append(record)
    latencies = []
    events_without_advisory = 0
    for event_records in groups.values():
        ordered = sorted(event_records, key=lambda record: record.captured_at)
        start = datetime.fromisoformat(ordered[0].captured_at.replace("Z", "+00:00"))
        first = next((record for record in ordered if record.advisory.action != InvestigationAction.WAIT), None)
        if first is None:
            events_without_advisory += 1
            continue
        observed = datetime.fromisoformat(first.captured_at.replace("Z", "+00:00"))
        latencies.append((observed - start).total_seconds())
    return {"labeled_events": len(groups), "events_with_non_wait_advisory": len(latencies),
            "events_without_non_wait_advisory": events_without_advisory,
            "seconds_to_first_non_wait_advisory": {"minimum": min(latencies), "median": median(latencies), "maximum": max(latencies)} if latencies else None}


def reconcile(records: tuple[ShadowAuditRecord, ...], outcomes: dict[str, ReviewOutcome]) -> dict[str, object]:
    record_ids = {record.snapshot_id for record in records}
    if unknown := set(outcomes) - record_ids:
        raise ValueError(f"review outcomes reference unknown snapshots: {sorted(unknown)}")
    reviewed = [record for record in records if record.snapshot_id in outcomes]
    action_reviews = [record for record in reviewed if outcomes[record.snapshot_id].operator_action]
    agreements = [record.advisory.action == outcomes[record.snapshot_id].operator_action
                  for record in action_reviews]
    dispositions = Counter(outcomes[record.snapshot_id].disposition.value for record in reviewed)
    labeled = [record for record in reviewed if outcomes[record.snapshot_id].event_class]
    channels = sorted({channel for record in records for channel in record.telemetry})
    return {"snapshots": len(records), "reviewed_snapshots": len(reviewed),
            "review_coverage": len(reviewed) / len(records) if records else 0.0,
            "dispositions": dict(sorted(dispositions.items())),
            "resolved_event_label_coverage": len(labeled) / len(records) if records else 0.0,
            "action_reviews": len(action_reviews),
            "operator_action_agreement": mean(agreements) if agreements else None,
            "operator_action_agreement_95_interval": _wilson_interval(sum(agreements), len(agreements)),
            "event_timing": _event_timing(records, outcomes),
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
    parser.add_argument("--channel-map", type=Path, help="Optional JSON source-column to canonical-channel map")
    parser.add_argument("--audit-output", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--policy-version", default="replay-threshold-v1")
    parser.add_argument("--configuration-version", default="offline-replay-v1")
    args = parser.parse_args()
    channel_map = load_channel_map(args.channel_map) if args.channel_map else None
    records = ShadowMode(HistorianCsvAdapter(args.telemetry, channel_map), conservative_policy,
                         args.policy_version, args.configuration_version).run()
    JsonlAuditLedger(args.audit_output).append(records)
    print(json.dumps(reconcile(records, load_outcomes(args.reviews)), indent=2))


if __name__ == "__main__":
    main()
