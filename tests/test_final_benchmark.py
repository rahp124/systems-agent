import json
from pathlib import Path

import pytest

from water_investigation.final_benchmark import (hierarchical_interval,
                                                  load_protocol, summarize)


def _run(scenario: str, correct: bool, cost: float, truth: str = "leak",
         prediction: str = "leak") -> dict[str, object]:
    return {"scenario_id": scenario, "correct": correct, "cost": cost,
            "actions": ["portable_pressure_reading"], "truth": truth,
            "prediction": prediction}


def test_protocol_requires_independent_generation_seeds(tmp_path: Path) -> None:
    protocol = json.loads((Path(__file__).parents[1] / "benchmark_protocol.json").read_text())
    protocol["ensembles"][1]["generation_seed"] = protocol["ensembles"][0]["generation_seed"]
    path = tmp_path / "protocol.json"
    path.write_text(json.dumps(protocol))
    with pytest.raises(ValueError, match="independently seeded"):
        load_protocol(path)


def test_checked_in_protocol_prespecifies_multiple_networks_and_layouts() -> None:
    protocol = load_protocol(Path(__file__).parents[1] / "benchmark_protocol.json")
    combinations = {(item["network"], item["sensor_layout"])
                    for item in protocol["ensembles"]}
    assert {("net3", "primary"), ("net3", "alternate"),
            ("ltown", "primary"), ("ltown", "alternate")} <= combinations
    assert protocol["episodes_per_ensemble"] * len(protocol["ensembles"]) == 2000


def test_hierarchical_interval_is_deterministic_and_contains_group_mean() -> None:
    interval = hierarchical_interval([[0.0, 1.0], [1.0, 1.0]], 42, 1000, 0.95)
    assert interval == hierarchical_interval([[0.0, 1.0], [1.0, 1.0]], 42, 1000, 0.95)
    assert interval[0] <= 0.75 <= interval[1]


def test_summary_reports_absolute_metrics_pairwise_differences_and_failures() -> None:
    protocol = {
        "policies": ["eig_per_cost", "operator_rule"],
        "reference_policy": "eig_per_cost", "bootstrap_samples": 100,
        "confidence_level": 0.95,
    }
    reports = [{"policies": {
        "eig_per_cost": {"runs": [_run("a", True, 1.0), _run("b", True, 2.0)]},
        "operator_rule": {"runs": [_run("a", False, 3.0, prediction="sensor_fault"),
                                     _run("b", True, 2.0)]},
    }}]
    result = summarize(protocol, reports)
    assert result["absolute_policy_metrics"]["eig_per_cost"]["accuracy"] == 1.0
    assert result["absolute_policy_metrics"]["operator_rule"]["failure_summary"]["count"] == 1
    assert result["paired_comparisons"]["operator_rule"]["mean_accuracy_difference"] == 0.5
    assert result["paired_comparisons"]["operator_rule"]["mean_cost_difference"] == -1.0
