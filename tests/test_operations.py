import json

import pytest

from water_investigation.operations import (Advisory, InvestigationAction,
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
