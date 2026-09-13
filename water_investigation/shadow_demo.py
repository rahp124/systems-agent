"""Exercise the read-only shadow-mode workflow with synthetic SCADA snapshots."""
from __future__ import annotations

import argparse
from pathlib import Path

from .operations import (Advisory, InvestigationAction, JsonlAuditLedger,
                         ShadowMode, SyntheticScadaAdapter, TelemetrySnapshot)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "shadow-demo.jsonl"


def _advisory(snapshot: TelemetrySnapshot) -> Advisory:
    """A synthetic-only policy used to demonstrate the operational contract."""
    if snapshot.values.get("quality_delta_mg_l", 0.0) >= 0.02:
        return Advisory(InvestigationAction.FIELD_CHLORINE, 0.70,
                        "quality delta exceeds the field-method lower range")
    if abs(snapshot.values.get("pressure_delta_psi", 0.0)) >= 0.25:
        return Advisory(InvestigationAction.PORTABLE_PRESSURE, 0.65,
                        "pressure delta exceeds the modeled transducer bound")
    return Advisory(InvestigationAction.WAIT, 0.50, "no synthetic threshold exceeded")


def main() -> None:
    parser = argparse.ArgumentParser(description="Write synthetic, advisory-only shadow records.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    snapshots = (
        TelemetrySnapshot("synthetic-001", "2026-09-13T12:00:00Z", "synthetic-scada",
                          {"quality_delta_mg_l": 0.04, "pressure_delta_psi": 0.01}),
        TelemetrySnapshot("synthetic-002", "2026-09-13T12:05:00Z", "synthetic-scada",
                          {"quality_delta_mg_l": 0.00, "pressure_delta_psi": 0.31}),
    )
    records = ShadowMode(SyntheticScadaAdapter(snapshots), _advisory).run()
    JsonlAuditLedger(args.output).append(records)
    print(f"{args.output} ({len(records)} advisory-only shadow records)")


if __name__ == "__main__":
    main()
