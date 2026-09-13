import json

import pytest

from water_investigation.operations import Advisory, InvestigationAction, ShadowAuditRecord
from water_investigation.replay import OperatorDisposition, ReviewOutcome, reconcile


def _record(snapshot_id: str, action: InvestigationAction) -> ShadowAuditRecord:
    return ShadowAuditRecord(snapshot_id, "2026-09-13T12:00:00Z", "historian", {},
                             Advisory(action, 0.7, "test"))


def test_reconcile_reports_operator_action_agreement() -> None:
    records = (_record("one", InvestigationAction.FIELD_CHLORINE),
               _record("two", InvestigationAction.WAIT))
    outcomes = {"one": ReviewOutcome("one", OperatorDisposition.ACCEPTED,
                                      InvestigationAction.FIELD_CHLORINE, "contamination")}
    report = reconcile(records, outcomes)
    assert report["review_coverage"] == 0.5
    assert report["operator_action_agreement"] == 1.0


def test_reconcile_rejects_reviews_without_matching_snapshots() -> None:
    with pytest.raises(ValueError, match="unknown snapshots"):
        reconcile((_record("one", InvestigationAction.WAIT),),
                  {"missing": ReviewOutcome("missing", OperatorDisposition.NO_ACTION)})
