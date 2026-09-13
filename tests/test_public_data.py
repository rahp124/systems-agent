from water_investigation.public_data import analyze_violations


def test_analyze_violations_summarizes_a_public_export(tmp_path) -> None:
    export = tmp_path / "violations.csv"
    export.write_text("PWSID,PRIMACY_AGENCY_CODE,VIOLATION_CODE,COMPL_PER_BEGIN_DATE\nCA1,CA,A,01/01/2024\nCA2,CA,A,02/01/2024\nNV1,NV,B,03/01/2024\n")
    report = analyze_violations(export, "ca")
    assert report["violation_records"] == 2
    assert report["public_water_systems"] == 2
    assert report["top_violation_codes"] == [{"code": "A", "count": 2}]
