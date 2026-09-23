from water_investigation.verify_artifacts import verify


def test_tracked_reports_have_required_reproducibility_fields() -> None:
    checked = verify()
    assert len(checked) == 5
    assert "artifacts/final-independent-benchmark.json" in checked
