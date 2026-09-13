from random import Random

from water_investigation.evaluation import (TraceScenario, empirical_actions,
                                            conditional_assay_actions,
                                            empirical_initial_telemetry, is_ambiguous,
                                            run_episode, split_scenarios, _assay_band,
                                            _choose)
from water_investigation.analytic import Action
from water_investigation.benchmark import paired_differences
from water_investigation.ensemble import ScenarioSpec
from water_investigation.measurement import (FIELD_SIGMA_MG_L, PRESSURE_HALF_WIDTH_PSI,
                                             chlorine, pressure_delta)


def _scenario(event_class: str, index: int, outcomes: dict[str, str]) -> TraceScenario:
    return TraceScenario(ScenarioSpec(f"{event_class}-{index:03d}", event_class, index, 0, 1.0), outcomes)


def test_split_is_stratified_and_disjoint() -> None:
    scenarios = [_scenario(kind, index, {}) for kind in ("contamination", "leak", "sensor_fault") for index in range(4)]
    training, held_out = split_scenarios(scenarios)
    assert len(training) == len(held_out) == 6
    assert {item.spec.scenario_id for item in training}.isdisjoint(item.spec.scenario_id for item in held_out)


def test_second_assay_uses_first_assay_band_as_a_condition() -> None:
    outcomes = {
        "field_chlorine_grab": "trace", "lab_chlorine_assay": "trace",
        "portable_pressure_reading": "stable", "wait": "steady",
    }
    training = [
        _scenario("contamination", 0, outcomes),
        _scenario("leak", 0, {**outcomes, "field_chlorine_grab": "below_range", "lab_chlorine_assay": "below_sensitivity"}),
        _scenario("sensor_fault", 0, {**outcomes, "field_chlorine_grab": "below_range", "lab_chlorine_assay": "below_sensitivity", "portable_pressure_reading": "higher"}),
    ]
    conditioned_lab = conditional_assay_actions(training)[("field_chlorine_grab", "trace")]
    assert conditioned_lab.likelihood["contamination"]["trace"] > conditioned_lab.likelihood["contamination"]["below_sensitivity"]


def test_second_assay_replaces_its_marginal_likelihood_after_a_field_result() -> None:
    scenario = _scenario("contamination", 0, {
        "field_chlorine_grab": "trace", "lab_chlorine_assay": "trace",
    })
    telemetry = Action("initial_telemetry", 0.0, 0, {
        event_class: {"unresolved": 1.0}
        for event_class in ("contamination", "leak", "sensor_fault")
    })
    field = Action("field_chlorine_grab", 1.0, 0, {
        "contamination": {"trace": 0.7, "below_range": 0.3},
        "leak": {"trace": 0.3, "below_range": 0.7},
        "sensor_fault": {"trace": 0.3, "below_range": 0.7},
    })
    marginal_lab = Action("lab_chlorine_assay", 5.0, 0, {
        event_class: {"trace": 0.5, "below_sensitivity": 0.5}
        for event_class in ("contamination", "leak", "sensor_fault")
    })
    conditioned_lab = Action("lab_chlorine_assay", 5.0, 0, {
        "contamination": {"trace": 0.9, "below_sensitivity": 0.1},
        "leak": {"trace": 0.1, "below_sensitivity": 0.9},
        "sensor_fault": {"trace": 0.1, "below_sensitivity": 0.9},
    })
    run = run_episode(scenario, (field, marginal_lab), telemetry, "eig_per_cost", 0,
                      assay_followups={("field_chlorine_grab", "trace"): conditioned_lab})
    assert run["actions"] == ["field_chlorine_grab", "lab_chlorine_assay"]


def test_ambiguity_gate_requires_two_plausible_classes() -> None:
    assert is_ambiguous({"contamination": 0.55, "leak": 0.30, "sensor_fault": 0.15})
    assert not is_ambiguous({"contamination": 0.80, "leak": 0.10, "sensor_fault": 0.10})


def test_pressure_measurement_is_seeded_and_respects_the_specification_bound() -> None:
    spec = ScenarioSpec("contamination-000", "contamination", 42, 0, 1.0)
    first = pressure_delta(spec, "portable_pressure_reading", 1.0)
    second = pressure_delta(spec, "portable_pressure_reading", 1.0)
    assert first == second
    assert abs(first.value - 1.0) <= PRESSURE_HALF_WIDTH_PSI


def test_chlorine_measurement_is_seeded_and_uses_the_documented_precision() -> None:
    spec = ScenarioSpec("contamination-000", "contamination", 42, 0, 1.0)
    first = chlorine(spec, "field_chlorine_grab", 1.0, lab=False)
    second = chlorine(spec, "field_chlorine_grab", 1.0, lab=False)
    assert first == second
    assert first.model == "Hach Method 8021 normal approximation"
    assert FIELD_SIGMA_MG_L == 0.05 / 1.96


def test_assay_bands_preserve_detection_limit_and_concentration_order() -> None:
    assert _assay_band(0.019, 0.02, "below_range") == "below_range"
    assert _assay_band(0.02, 0.02, "below_range") == "trace"
    assert _assay_band(0.10, 0.02, "below_range") == "elevated"
    assert _assay_band(0.50, 0.02, "below_range") == "high"


def test_risk_aware_policy_stops_when_no_action_improves_risk_adjusted_accuracy() -> None:
    belief = {"contamination": 0.5, "leak": 0.5}
    uninformative = Action(
        "uninformative", 1.0, 0,
        {"contamination": {"same": 1.0}, "leak": {"same": 1.0}},
    )
    assert _choose("risk_aware", belief, [uninformative], Random(0), risk_lambda=0.05) is None


def test_paired_differences_rejects_different_scenario_sequences() -> None:
    report = {"policies": {
        "eig_per_cost": {"runs": [{"scenario_id": "a", "correct": True, "cost": 1.0}]},
        "random": {"runs": [{"scenario_id": "b", "correct": False, "cost": 2.0}]},
    }}
    try:
        paired_differences(report, "eig_per_cost", "random")
    except ValueError as error:
        assert "different scenarios" in str(error)
    else:
        raise AssertionError("expected paired-sequence validation to fail")
