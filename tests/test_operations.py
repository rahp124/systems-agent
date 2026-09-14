import json

import pytest

from water_investigation.operations import (Advisory, HistorianCsvAdapter, InvestigationAction,
                                            JsonlAuditLedger, ShadowMode,
                                            SyntheticScadaAdapter,
                                            TelemetrySnapshot)


def _snapshot(snapshot_id: str) -> TelemetrySnapshot:
    return TelemetrySnapshot(snapshot_id, "2026-09-13T12:00:00Z", "synthetic-scada",
                             {"pressure_delta_psi": 0.1})


def _advisory(_: TelemetrySnapshot) -> Advisory:
    return Advisory(InvestigationAction.PORTABLE_PRESSURE, 0.7, "pressure deviation")


def test_synthetic_scada_adapter_is_cursor_based_and_read_only() -> None:
    adapter = SyntheticScadaAdapter((_snapshot("one"), _snapshot("two")))
    assert [snapshot.snapshot_id for snapshot in adapter.read("one")] == ["two"]
    with pytest.raises(ValueError, match="unknown telemetry cursor"):
        adapter.read("missing")


def test_shadow_mode_emits_advisory_only_audit_records() -> None:
    records = ShadowMode(SyntheticScadaAdapter((_snapshot("one"),)), _advisory).run()
    assert records[0].mode == "shadow"
    assert records[0].as_dict()["advisory"]["action"] == "portable_pressure_reading"
    assert "control" not in records[0].as_dict()


def test_jsonl_ledger_appends_serialized_shadow_records(tmp_path) -> None:
    records = ShadowMode(SyntheticScadaAdapter((_snapshot("one"),)), _advisory).run()
    ledger_path = tmp_path / "shadow.jsonl"
    JsonlAuditLedger(ledger_path).append(records)
    assert json.loads(ledger_path.read_text())["mode"] == "shadow"


def test_historian_csv_adapter_requires_and_reads_deidentified_telemetry(tmp_path) -> None:
    export = tmp_path / "telemetry.csv"
    export.write_text("snapshot_id,captured_at,source,pressure_delta_psi\na,2026-09-13T12:00:00Z,historian,0.2\n")
    assert HistorianCsvAdapter(export).read()[0].values == {"pressure_delta_psi": 0.2}


def test_historian_csv_adapter_rejects_unordered_timestamps(tmp_path) -> None:
    export = tmp_path / "telemetry.csv"
    export.write_text("snapshot_id,captured_at,source,pressure_delta_psi\na,2026-09-13T12:01:00Z,historian,0.2\nb,2026-09-13T12:00:00Z,historian,0.3\n")
    with pytest.raises(ValueError, match="strictly increasing"):
        HistorianCsvAdapter(export)


def test_historian_csv_adapter_maps_complete_source_channels(tmp_path) -> None:
    export = tmp_path / "telemetry.csv"
    export.write_text("snapshot_id,captured_at,source,p_delta,q_delta\na,2026-09-13T12:00:00Z,historian,0.2,0.01\n")
    adapter = HistorianCsvAdapter(export, {"p_delta": "pressure_delta_psi", "q_delta": "quality_delta_mg_l"})
    assert adapter.read()[0].values == {"pressure_delta_psi": 0.2, "quality_delta_mg_l": 0.01}
