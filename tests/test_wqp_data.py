from datetime import date

import pytest

from water_investigation.wqp_data import analyze_results, build_result_query


def test_build_result_query_uses_fips_dates_and_repeated_providers() -> None:
    query = build_result_query("55", "Nitrate", date(2024, 1, 1), date(2024, 1, 31), "017", ("NWIS", "STORET"))
    assert "statecode=US%3A55" in query
    assert "countycode=US%3A55%3A017" in query
    assert "startDateLo=01-01-2024" in query
    assert query.count("providers=") == 2


def test_build_result_query_requires_a_bounded_scope() -> None:
    with pytest.raises(ValueError, match="bounded query"):
        build_result_query("55", "Nitrate")


def test_analyze_results_separates_measurement_units(tmp_path) -> None:
    results = tmp_path / "results.csv"
    results.write_text(
        "MonitoringLocationIdentifier,ActivityStartDate,CharacteristicName,ResultMeasureValue,ResultMeasure/MeasureUnitCode,ProviderName\n"
        "site-a,2024-01-01,Nitrate,1.0,mg/L,NWIS\n"
        "site-a,2024-01-01,Nitrate,0,mg/L,NWIS\n"
        "site-a,2024-01-02,Nitrate,3.0,mg/L,NWIS\n"
        "site-b,2024-01-03,Nitrate,,mg/L,STORET\n"
        "site-b,2024-01-03,Nitrate,20,ug/L,STORET\n")
    report = analyze_results(results, {"query_url": "https://example.test"})
    assert report["result_records"] == 5
    assert report["monitoring_locations"] == 2
    assert report["numeric_results_by_unit"] == [
        {"unit": "mg/L", "count": 3, "minimum": 0.0, "median": 1.0, "maximum": 3.0},
        {"unit": "ug/L", "count": 1, "minimum": 20.0, "median": 20.0, "maximum": 20.0},
    ]
