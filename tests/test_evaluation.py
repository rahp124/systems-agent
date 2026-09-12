from random import Random

from water_investigation.evaluation import (TraceScenario, empirical_actions,
                                            empirical_initial_telemetry, is_ambiguous,
                                            run_episode, split_scenarios)
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


def test_selecting_field_assay_excludes_correlated_lab_assay() -> None:
    outcomes = {
        "field_chlorine_grab": "detected", "lab_chlorine_assay": "detected",
        "portable_pressure_reading": "stable", "wait": "steady",
    }
    training = [
        _scenario("contamination", 0, outcomes),
        _scenario("leak", 0, {**outcomes, "field_chlorine_grab": "clear", "lab_chlorine_assay": "clear"}),
        _scenario("sensor_fault", 0, {**outcomes, "field_chlorine_grab": "clear", "lab_chlorine_assay": "clear", "portable_pressure_reading": "higher"}),
    ]
    run = run_episode(training[0], empirical_actions(training), empirical_initial_telemetry(training), "eig_per_cost", Random(1).randrange(2**31))
    assert not ({"field_chlorine_grab", "lab_chlorine_assay"} <= set(run["actions"]))


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
