"""Read-only telemetry and auditable shadow-mode primitives for utility pilots.

This module deliberately exposes no control-operation interface. Its seam is a
telemetry reader: a synthetic adapter exercises it now, while a utility-owned,
read-only historian adapter can replace it during a shadow pilot.
"""
from __future__ import annotations

import json
import csv
from datetime import datetime
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


class HistorianCsvAdapter(SyntheticScadaAdapter):
    """Read a de-identified historian export through the telemetry seam.

    Required columns are ``snapshot_id``, ``captured_at``, and ``source``;
    every remaining column must be a numeric telemetry value. The adapter never
    writes to the export or opens a network connection.
    """

    REQUIRED_COLUMNS = frozenset({"snapshot_id", "captured_at", "source"})

    def __init__(self, path: Path, channel_map: dict[str, str] | None = None) -> None:
        with path.open(newline="", encoding="utf-8") as input_file:
            reader = csv.DictReader(input_file)
            if reader.fieldnames is None or not self.REQUIRED_COLUMNS <= set(reader.fieldnames):
                raise ValueError("historian CSV requires snapshot_id, captured_at, and source columns")
            source_columns = [column for column in reader.fieldnames if column not in self.REQUIRED_COLUMNS]
            channel_map = channel_map or {column: column for column in source_columns}
            if set(channel_map) != set(source_columns) or len(set(channel_map.values())) != len(channel_map):
                raise ValueError("channel map must cover each telemetry column exactly once with unique output names")
            value_columns = list(channel_map)
            if not value_columns:
                raise ValueError("historian CSV requires at least one numeric telemetry column")
            snapshots = []
            previous_time = None
            for row in reader:
                try:
                    values = {channel_map[column]: float(row[column]) for column in value_columns}
                    captured_at = datetime.fromisoformat(row["captured_at"].replace("Z", "+00:00"))
                except (TypeError, ValueError) as error:
                    raise ValueError("historian rows require nonmissing numeric values and ISO-8601 timestamps") from error
                if previous_time and captured_at <= previous_time:
                    raise ValueError("historian timestamps must be strictly increasing")
                previous_time = captured_at
                snapshots.append(TelemetrySnapshot(row["snapshot_id"], row["captured_at"],
                                                   row["source"], values))
        super().__init__(tuple(snapshots))


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
    policy_version: str = "unversioned"
    configuration_version: str = "unversioned"
    mode: str = "shadow"

    def as_dict(self) -> dict[str, object]:
        record = asdict(self)
        record["advisory"]["action"] = self.advisory.action.value
        return record


class ShadowMode:
    """Create audit records from any read-only telemetry adapter and advisory policy."""

    def __init__(self, reader: TelemetryReader,
                 policy: Callable[[TelemetrySnapshot], Advisory],
                 policy_version: str = "unversioned",
                 configuration_version: str = "unversioned") -> None:
        self._reader = reader
        self._policy = policy
        self._policy_version = policy_version
        self._configuration_version = configuration_version

    def run(self, cursor: str | None = None) -> tuple[ShadowAuditRecord, ...]:
        return tuple(
            ShadowAuditRecord(snapshot.snapshot_id, snapshot.captured_at, snapshot.source,
                              snapshot.values, self._policy(snapshot), self._policy_version,
                              self._configuration_version)
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
