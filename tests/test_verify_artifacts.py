from water_investigation.verify_artifacts import verify


def test_tracked_reports_have_required_reproducibility_fields() -> None:
    assert len(verify()) == 4
