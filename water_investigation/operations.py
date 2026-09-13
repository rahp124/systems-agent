"""Read-only telemetry and auditable shadow-mode primitives for utility pilots.

This module deliberately exposes no control-operation interface. Its seam is a
telemetry reader: a synthetic adapter exercises it now, while a utility-owned,
read-only historian adapter can replace it during a shadow pilot.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Callable, Protocol


class InvestigationAction(StrEnum):
    FIELD_CHLORINE = "field_chlorine_grab"
    LAB_CHLORINE = "lab_chlorine_assay"
    PORTABLE_PRESSURE = "portable_pressure_reading"
    WAIT = "wait_for_next_telemetry"


@dataclass(frozen=True)
class TelemetrySnapshot:
    """One immutable, source-attributed read from a read-only telemetry feed."""

    snapshot_id: str
    captured_at: str
    source: str
    values: dict[str, float]


class TelemetryReader(Protocol):
    """Read snapshots strictly after an optional cursor, in stable order."""

    def read(self, cursor: str | None = None) -> tuple[TelemetrySnapshot, ...]: ...


class SyntheticScadaAdapter:
    """In-memory read-only adapter for exercising shadow-mode workflows."""

    def __init__(self, snapshots: tuple[TelemetrySnapshot, ...]) -> None:
        if len({snapshot.snapshot_id for snapshot in snapshots}) != len(snapshots):
            raise ValueError("telemetry snapshot IDs must be unique")
        self._snapshots = snapshots

    def read(self, cursor: str | None = None) -> tuple[TelemetrySnapshot, ...]:
        if cursor is None:
            return self._snapshots
        for index, snapshot in enumerate(self._snapshots):
            if snapshot.snapshot_id == cursor:
                return self._snapshots[index + 1:]
        raise ValueError(f"unknown telemetry cursor: {cursor}")


@dataclass(frozen=True)
class Advisory:
    action: InvestigationAction
    confidence: float
    rationale: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("advisory confidence must be between zero and one")


@dataclass(frozen=True)
class ShadowAuditRecord:
    """An auditable advisory record; it contains no control command or side effect."""

    snapshot_id: str
    captured_at: str
    source: str
    telemetry: dict[str, float]
    advisory: Advisory
    mode: str = "shadow"

    def as_dict(self) -> dict[str, object]:
        record = asdict(self)
        record["advisory"]["action"] = self.advisory.action.value
        return record


class ShadowMode:
    """Create audit records from any read-only telemetry adapter and advisory policy."""

    def __init__(self, reader: TelemetryReader,
                 policy: Callable[[TelemetrySnapshot], Advisory]) -> None:
        self._reader = reader
        self._policy = policy

    def run(self, cursor: str | None = None) -> tuple[ShadowAuditRecord, ...]:
        return tuple(
            ShadowAuditRecord(snapshot.snapshot_id, snapshot.captured_at, snapshot.source,
                              snapshot.values, self._policy(snapshot))
            for snapshot in self._reader.read(cursor)
        )


class JsonlAuditLedger:
    """Append-only JSONL persistence for shadow records supplied by the caller."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def append(self, records: tuple[ShadowAuditRecord, ...]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as output:
            for record in records:
                output.write(json.dumps(record.as_dict(), sort_keys=True) + "\n")
