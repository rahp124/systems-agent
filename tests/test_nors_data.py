from water_investigation.nors_data import analyze_records, build_drinking_water_query


def test_build_drinking_water_query_filters_to_drinking_water() -> None:
    query = build_drinking_water_query(2020, 2023, "Wisconsin")
    assert "primary_mode+%3D+%27Water%27" in query
    assert "water_exposure+%3D+%27Drinking+water%27" in query
    assert "year+between+2020+and+2023" in query


def test_analyze_records_reports_outcomes_and_missingness(tmp_path) -> None:
    records = tmp_path / "nors.csv"
    records.write_text(
        '"year","month","state","primary_mode","etiology","illnesses","hospitalizations","deaths","water_exposure","water_type"\n'
        '"2020","1","Wisconsin","Water","Legionella","10","2","1","Drinking water","Community"\n'
        '"2021","2","Wisconsin","Water","Unknown","","","","Drinking water","Other"\n')
    report = analyze_records(records)
    assert report["outbreak_records"] == 2
    assert report["record_reported_outcomes"] == {"illnesses": 10, "hospitalizations": 2, "deaths": 1}
    assert report["outcome_field_coverage"]["illnesses"] == {"reported": 1, "missing": 1}
    assert report["etiologies"] == [{"name": "Legionella", "records": 1}, {"name": "Unknown", "records": 1}]
