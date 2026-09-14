import json

import pytest

from water_investigation.operations import Advisory, InvestigationAction, ShadowAuditRecord
from water_investigation.replay import OperatorDisposition, ReviewOutcome, reconcile


def _record(snapshot_id: str, action: InvestigationAction) -> ShadowAuditRecord:
    return ShadowAuditRecord(snapshot_id, "2026-09-13T12:00:00Z", "historian", {},
                             Advisory(action, 0.7, "test"))


def test_reconcile_reports_operator_action_agreement() -> None:
    records = (_record("one", InvestigationAction.FIELD_CHLORINE),
               ShadowAuditRecord("two", "2026-09-13T12:05:00Z", "historian", {},
                                 Advisory(InvestigationAction.WAIT, 0.7, "test")))
    outcomes = {"one": ReviewOutcome("one", OperatorDisposition.ACCEPTED,
                                      InvestigationAction.FIELD_CHLORINE, "contamination", "event-one")}
    report = reconcile(records, outcomes)
    assert report["review_coverage"] == 0.5
    assert report["operator_action_agreement"] == 1.0
    assert report["operator_action_agreement_95_interval"] is not None
    assert report["event_timing"]["seconds_to_first_non_wait_advisory"]["median"] == 0.0
    assert report["data_quality"]["timestamp_ordered"] is True


def test_reconcile_rejects_reviews_without_matching_snapshots() -> None:
    with pytest.raises(ValueError, match="unknown snapshots"):
        reconcile((_record("one", InvestigationAction.WAIT),),
                  {"missing": ReviewOutcome("missing", OperatorDisposition.NO_ACTION)})


def test_reconcile_leaves_timing_unavailable_without_event_ids() -> None:
    report = reconcile((_record("one", InvestigationAction.WAIT),),
                       {"one": ReviewOutcome("one", OperatorDisposition.NO_ACTION)})
    assert report["event_timing"]["labeled_events"] == 0
