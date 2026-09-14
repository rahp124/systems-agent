"""Run a local, read-only synthetic operational-pilot readiness check."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .operations import HistorianCsvAdapter, assess_telemetry
from .replay import conservative_policy, load_channel_map


def run(telemetry: Path, channel_map: Path | None, required_channels: frozenset[str], maximum_gap_seconds: float) -> dict[str, object]:
    snapshots = HistorianCsvAdapter(telemetry, load_channel_map(channel_map) if channel_map else None).read()
    assessment = assess_telemetry(snapshots, required_channels, maximum_gap_seconds)
    advisories = [] if not assessment.safe_to_advise else [
        {"snapshot_id": snapshot.snapshot_id, "action": conservative_policy(snapshot).action.value,
         "confidence": conservative_policy(snapshot).confidence} for snapshot in snapshots]
    return {"mode": "synthetic_offline_pilot", "safety_assessment": {
        "safe_to_advise": assessment.safe_to_advise, "reasons": list(assessment.reasons),
        "snapshot_count": assessment.snapshot_count, "maximum_gap_seconds": assessment.maximum_gap_seconds},
        "advisories": advisories,
        "interpretation_limit": "Local synthetic readiness check only; it is not a SCADA connection, shadow-mode authorization, or operational validation."}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a read-only synthetic operational-pilot check.")
    parser.add_argument("--telemetry", type=Path, required=True)
    parser.add_argument("--channel-map", type=Path)
    parser.add_argument("--required-channel", action="append", required=True)
    parser.add_argument("--maximum-gap-seconds", type=float, default=900)
    args = parser.parse_args()
    print(json.dumps(run(args.telemetry, args.channel_map, frozenset(args.required_channel), args.maximum_gap_seconds), indent=2))


if __name__ == "__main__":
    main()
