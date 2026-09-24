import csv
from pathlib import Path

import pytest

from water_investigation.expert_review import ACTION_DETAILS, _select_cases, analyze_responses


def _casebook(path: Path) -> None:
    path.write_text('''{
      "cases": [{
        "case_id": "case-1",
        "phase_2": {"agent_recommendation": "portable_pressure_reading"}
      }]
    }''')


def test_analyze_responses_reports_agreement_ratings_and_safety(tmp_path: Path) -> None:
    casebook = tmp_path / "casebook.json"
    responses = tmp_path / "responses.csv"
    _casebook(casebook)
    with responses.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "reviewer_id", "case_id", "reviewer_action", "confidence_1_5",
            "recommendation_reasonable_1_5", "advisory_safety",
        ])
        writer.writeheader()
        writer.writerow({"reviewer_id": "r1", "case_id": "case-1",
                         "reviewer_action": "portable_pressure_reading",
                         "confidence_1_5": "4", "recommendation_reasonable_1_5": "5",
                         "advisory_safety": "safe"})
        writer.writerow({"reviewer_id": "r2", "case_id": "case-1",
                         "reviewer_action": "field_chlorine_grab",
                         "confidence_1_5": "3", "recommendation_reasonable_1_5": "2",
                         "advisory_safety": "uncertain"})
    result = analyze_responses(responses, casebook)
    assert result["reviewer_count"] == 2
    assert result["exact_agent_agreement"] == 0.5
    assert result["mean_recommendation_reasonableness"] == 3.5
    assert result["pairwise_inter_reviewer_agreement"] == 0.0


def test_analyze_responses_rejects_unknown_actions(tmp_path: Path) -> None:
    casebook = tmp_path / "casebook.json"
    responses = tmp_path / "responses.csv"
    _casebook(casebook)
    responses.write_text("reviewer_id,case_id,reviewer_action,confidence_1_5,recommendation_reasonable_1_5,advisory_safety\nr1,case-1,guess,3,3,safe\n")
    with pytest.raises(ValueError, match="unknown reviewer_action"):
        analyze_responses(responses, casebook)


def test_analyze_responses_rejects_duplicate_reviewer_case_rows(tmp_path: Path) -> None:
    casebook = tmp_path / "casebook.json"
    responses = tmp_path / "responses.csv"
    _casebook(casebook)
    header = "reviewer_id,case_id,reviewer_action,confidence_1_5,recommendation_reasonable_1_5,advisory_safety\n"
    row = "r1,case-1,wait,3,3,safe\n"
    responses.write_text(header + row + row)
    with pytest.raises(ValueError, match="duplicate reviewer-case"):
        analyze_responses(responses, casebook)


def test_action_vocabulary_covers_the_four_review_choices() -> None:
    assert set(ACTION_DETAILS) == {"field_chlorine_grab", "lab_chlorine_assay",
                                   "portable_pressure_reading", "wait"}


def test_case_selection_is_balanced_without_weakening_the_frozen_gate() -> None:
    runs = [
        {"scenario_id": f"{truth}-{index}", "truth": truth, "correct": index > 0}
        for truth in ("contamination", "leak")
        for index in range(4)
    ]
    selected = _select_cases(runs)
    assert [run["truth"] for run in selected].count("contamination") == 3
    assert [run["truth"] for run in selected].count("leak") == 3
    assert selected[0]["correct"] is False
