"""Evaluate three policies against held-out scenarios from a Net3 trace ensemble."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from random import Random
from statistics import mean

from .analytic import Action, expected_classification_accuracy, posterior_after, score_action
from .ensemble import DEFAULT_OUTPUT, HYPOTHESES, ScenarioSpec, ensemble_metadata, load_ensemble
from .measurement import (FIELD_LOWER_RANGE_MG_L, LAB_SENSITIVITY_MG_L,
                          PRESSURE_HALF_WIDTH_PSI, chlorine, pressure_delta)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "artifacts" / "net3-evaluation.json"
CONCLUSION_THRESHOLD = 0.75
MAX_INITIAL_POSTERIOR = 0.70
MIN_SECOND_INITIAL_POSTERIOR = 0.15
OUTCOME_SPACES = {
    "initial_telemetry": ("pressure_high", "pressure_low", "unresolved"),
    "field_chlorine_grab": ("below_range", "trace", "elevated", "high"),
    "lab_chlorine_assay": ("below_sensitivity", "trace", "elevated", "high"),
    "portable_pressure_reading": ("higher", "lower", "stable"),
    "wait": ("flow_changed", "steady"),
}

# These bands are fixed before fitting likelihoods. They preserve the assay's
# concentration ordering without pretending the source specifications justify
# a continuous density model from only 20 training scenarios per class.
ASSAY_BAND_EDGES_MG_L = (0.10, 0.50)


@dataclass(frozen=True)
class TraceScenario:
    spec: ScenarioSpec
    outcomes: dict[str, str]
    initial_outcome: str = "unresolved"
    measurements: dict[str, float] | None = None


def _assay_band(value: float, lower_limit: float, below_label: str) -> str:
    if value < lower_limit:
        return below_label
    if value < ASSAY_BAND_EDGES_MG_L[0]:
        return "trace"
    if value < ASSAY_BAND_EDGES_MG_L[1]:
        return "elevated"
    return "high"


def _outcomes(spec: ScenarioSpec, pressure, flow, quality, baseline) -> tuple[str, dict[str, str], dict[str, float]]:
    """Extract action results from stored traces; no event label is consulted."""
    baseline_pressure, baseline_flow, baseline_quality = baseline
    quality_peak = float((quality - baseline_quality).max())
    pressure_trace_delta = pressure[:, 0] - baseline_pressure[:, 0]
    flow_change = float(abs(flow - baseline_flow).max())
    # Use the same 12-hour observation window for hourly Net3 and five-minute
    # L-Town traces rather than silently comparing different durations.
    initial_samples = round(12 * (len(pressure) - 1) / 48) + 1
    initial_pressure = pressure[:initial_samples, 0] - baseline_pressure[:initial_samples, 0]
    initial_reading = pressure_delta(spec, "fixed_pressure", float(initial_pressure.max()))
    field_reading = chlorine(spec, "field_chlorine_grab", quality_peak, lab=False)
    lab_reading = chlorine(spec, "lab_chlorine_assay", quality_peak, lab=True)
    pressure_reading = pressure_delta(spec, "portable_pressure_reading", float(pressure_trace_delta.max()))
    initial = "pressure_high" if initial_reading.value > PRESSURE_HALF_WIDTH_PSI else "pressure_low" if initial_reading.value < -PRESSURE_HALF_WIDTH_PSI else "unresolved"
    outcomes = {
        "field_chlorine_grab": _assay_band(field_reading.value, FIELD_LOWER_RANGE_MG_L, "below_range"),
        "lab_chlorine_assay": _assay_band(lab_reading.value, LAB_SENSITIVITY_MG_L, "below_sensitivity"),
        "portable_pressure_reading": "higher" if pressure_reading.value > PRESSURE_HALF_WIDTH_PSI else "lower" if pressure_reading.value < -PRESSURE_HALF_WIDTH_PSI else "stable",
        # At this short horizon, passive waiting is deliberately retained as a
        # low-cost but weak action. It should not dominate an informative sample.
        "wait": "flow_changed" if flow_change > 1.0 else "steady",
    }
    measurements = {
        "fixed_pressure_delta_psi": initial_reading.value,
        "field_chlorine_mg_l": field_reading.value,
        "lab_chlorine_mg_l": lab_reading.value,
        "portable_pressure_delta_psi": pressure_reading.value,
    }
    return initial, outcomes, measurements


def scenarios_from_ensemble(path: Path) -> list[TraceScenario]:
    specs, pressure, flow, quality, baseline = load_ensemble(path)
    scenarios = []
    for index, spec in enumerate(specs):
        initial_outcome, outcomes, measurements = _outcomes(spec, pressure[index], flow[index], quality[index], baseline)
        scenarios.append(TraceScenario(spec, outcomes, initial_outcome, measurements))
    return scenarios


def split_scenarios(scenarios: list[TraceScenario]) -> tuple[list[TraceScenario], list[TraceScenario]]:
    """Deterministic, stratified odd/even split avoids scoring a scenario used for likelihoods."""
    training, held_out = [], []
    for scenario in scenarios:
        index = int(scenario.spec.scenario_id.rsplit("-", 1)[1])
        (held_out if index % 2 else training).append(scenario)
    return training, held_out


def empirical_actions(training: list[TraceScenario]) -> tuple[Action, ...]:
    definitions = (
        ("field_chlorine_grab", 1.0, 1),
        ("lab_chlorine_assay", 5.0, 8),
        ("portable_pressure_reading", 3.0, 2),
        ("wait", 0.5, 1),
    )
    actions = []
    for name, cost, latency in definitions:
        outcomes = OUTCOME_SPACES[name]
        likelihood = {}
        for hypothesis in HYPOTHESES:
            class_scenarios = [scenario for scenario in training if scenario.spec.event_class == hypothesis]
            # Laplace smoothing keeps every observed outcome possible at evaluation time.
            likelihood[hypothesis] = {
                outcome: (1 + sum(scenario.outcomes[name] == outcome for scenario in class_scenarios)) /
                (len(outcomes) + len(class_scenarios))
                for outcome in outcomes
            }
        actions.append(Action(name, cost, latency, likelihood))
    return tuple(actions)


def conditional_assay_actions(training: list[TraceScenario]) -> dict[tuple[str, str], Action]:
    """Estimate the second assay conditional on the first assay's observed band.

    Field and lab samples are separately perturbed readings of the same simulated
    event. Their marginal outcomes are correlated through event magnitude, so a
    second assay must use P(second | class, first), not a second marginal
    likelihood. Laplace smoothing keeps sparse conditional cells usable.
    """
    followups = {}
    pairs = (("field_chlorine_grab", "lab_chlorine_assay"),
             ("lab_chlorine_assay", "field_chlorine_grab"))
    for first_name, second_name in pairs:
        for first_outcome in OUTCOME_SPACES[first_name]:
            likelihood = {}
            for hypothesis in HYPOTHESES:
                matching = [scenario for scenario in training
                            if scenario.spec.event_class == hypothesis
                            and scenario.outcomes[first_name] == first_outcome]
                likelihood[hypothesis] = {
                    outcome: (1 + sum(scenario.outcomes[second_name] == outcome for scenario in matching)) /
                    (len(OUTCOME_SPACES[second_name]) + len(matching))
                    for outcome in OUTCOME_SPACES[second_name]
                }
            definition = next(item for item in (("field_chlorine_grab", 1.0, 1),
                                                 ("lab_chlorine_assay", 5.0, 8))
                              if item[0] == second_name)
            followups[(first_name, first_outcome)] = Action(*definition, likelihood)
    return followups


def empirical_initial_telemetry(training: list[TraceScenario]) -> Action:
    likelihood = {}
    for hypothesis in HYPOTHESES:
        class_scenarios = [scenario for scenario in training if scenario.spec.event_class == hypothesis]
        likelihood[hypothesis] = {
            outcome: (1 + sum(scenario.initial_outcome == outcome for scenario in class_scenarios)) /
            (len(OUTCOME_SPACES["initial_telemetry"]) + len(class_scenarios))
            for outcome in OUTCOME_SPACES["initial_telemetry"]
        }
    return Action("initial_telemetry", 0.0, 0, likelihood)


def initial_posterior(scenario: TraceScenario, telemetry: Action):
    prior = {hypothesis: 1 / len(HYPOTHESES) for hypothesis in HYPOTHESES}
    return posterior_after(prior, telemetry, scenario.initial_outcome)


def is_ambiguous(posterior) -> bool:
    ranked = sorted(posterior.values(), reverse=True)
    return ranked[0] <= MAX_INITIAL_POSTERIOR and ranked[1] >= MIN_SECOND_INITIAL_POSTERIOR


def _risk_adjusted_value(belief, action: Action, risk_lambda: float) -> float:
    return expected_classification_accuracy(belief, action) - max(belief.values()) - risk_lambda * action.cost


def _choose(policy: str, belief, available: list[Action], rng: Random, risk_lambda: float = 0.05) -> Action | None:
    if policy == "eig_per_cost":
        return max(available, key=lambda action: (score_action(belief, action), action.name))
    if policy == "expected_accuracy":
        return max(available, key=lambda action: (expected_classification_accuracy(belief, action), -action.cost, action.name))
    if policy == "risk_aware":
        action = max(available, key=lambda candidate: (_risk_adjusted_value(belief, candidate, risk_lambda), candidate.name))
        return action if _risk_adjusted_value(belief, action, risk_lambda) > 0 else None
    if policy == "cheapest_first":
        return min(available, key=lambda action: (action.cost, action.name))
    if policy == "random":
        return rng.choice(available)
    raise ValueError(f"unknown policy: {policy}")


def run_episode(scenario: TraceScenario, actions: tuple[Action, ...], telemetry: Action, policy: str, seed: int, risk_lambda: float = 0.05, assay_followups: dict[tuple[str, str], Action] | None = None) -> dict[str, object]:
    belief = initial_posterior(scenario, telemetry)
    remaining = list(actions)
    rng = Random(seed)
    total_cost = 0.0
    selected: list[str] = []
    for _ in range(3):
        action = _choose(policy, belief, remaining, rng, risk_lambda)
        if action is None:
            break
        selected.append(action.name)
        total_cost += action.cost
        belief = posterior_after(belief, action, scenario.outcomes[action.name])
        remaining.remove(action)
        if action.name in {"field_chlorine_grab", "lab_chlorine_assay"}:
            # Preserve the second, separately sampled assay, but replace its
            # marginal model with the likelihood conditioned on this result.
            followup = (assay_followups or {}).get((action.name, scenario.outcomes[action.name]))
            if followup:
                remaining = [followup if candidate.name == followup.name else candidate
                             for candidate in remaining]
        if max(belief.values()) >= CONCLUSION_THRESHOLD:
            break
    prediction = max(belief, key=belief.get)
    return {
        "scenario_id": scenario.spec.scenario_id,
        "policy": policy,
        "prediction": prediction,
        "truth": scenario.spec.event_class,
        "correct": prediction == scenario.spec.event_class,
        "cost": total_cost,
        "actions": selected,
        "initial_outcome": scenario.initial_outcome,
        "initial_posterior": initial_posterior(scenario, telemetry),
        "measurements": scenario.measurements,
        "posterior": belief,
    }


def evaluate(path: Path = DEFAULT_OUTPUT, episodes: int = 100, seed: int = 20260911, risk_lambda: float = 0.05) -> dict[str, object]:
    scenarios = scenarios_from_ensemble(path)
    training, held_out = split_scenarios(scenarios)
    if not held_out:
        raise ValueError("ensemble does not contain held-out scenarios")
    actions = empirical_actions(training)
    assay_followups = conditional_assay_actions(training)
    telemetry = empirical_initial_telemetry(training)
    eligible = [scenario for scenario in held_out if is_ambiguous(initial_posterior(scenario, telemetry))]
    if not eligible:
        raise ValueError("no held-out scenarios met the ambiguity gate")
    rng = Random(seed)
    try:
        ensemble_name = str(path.relative_to(ROOT))
    except ValueError:
        ensemble_name = str(path)
    report: dict[str, object] = {
        "ensemble": ensemble_name, "ensemble_metadata": ensemble_metadata(path), "episodes": episodes,
        "training_scenarios": len(training), "held_out_scenarios": len(held_out),
        "eligible_held_out_scenarios": len(eligible), "rejected_held_out_scenarios": len(held_out) - len(eligible),
        "ambiguity_gate": {"max_initial_posterior": MAX_INITIAL_POSTERIOR, "min_second_initial_posterior": MIN_SECOND_INITIAL_POSTERIOR},
        "measurement_model": {
            "pressure_half_width_psi": PRESSURE_HALF_WIDTH_PSI,
            "field_lower_range_mg_l": FIELD_LOWER_RANGE_MG_L,
            "lab_sensitivity_mg_l": LAB_SENSITIVITY_MG_L,
            "assay_band_edges_mg_l": list(ASSAY_BAND_EDGES_MG_L),
        }, "paired_episodes": True, "risk_lambda": risk_lambda, "policies": {},
    }
    # Every policy must face the identical held-out episode sequence. Sampling
    # separately per policy confounds policy quality with scenario mix.
    episode_scenarios = [rng.choice(eligible) for _ in range(episodes)]
    episode_seeds = [rng.randrange(2**31) for _ in range(episodes)]
    for policy in ("eig_per_cost", "risk_aware", "expected_accuracy", "random", "cheapest_first"):
        runs = [run_episode(scenario, actions, telemetry, policy, episode_seed, risk_lambda, assay_followups)
                for scenario, episode_seed in zip(episode_scenarios, episode_seeds)]
        correct = [run for run in runs if run["correct"]]
        report["policies"][policy] = {
            "accuracy": len(correct) / episodes,
            "mean_cost": mean(run["cost"] for run in runs),
            "mean_actions": mean(len(run["actions"]) for run in runs),
            "mean_cost_when_correct": mean(run["cost"] for run in correct) if correct else None,
            "runs": runs,
        }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate policies on a seeded Net3 ensemble.")
    parser.add_argument("--ensemble", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260911)
    parser.add_argument("--risk-lambda", type=float, default=0.05)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    report = evaluate(args.ensemble, args.episodes, args.seed, args.risk_lambda)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(args.output)
    for name, metrics in report["policies"].items():
        print(f"{name}: accuracy={metrics['accuracy']:.3f} cost={metrics['mean_cost']:.2f} actions={metrics['mean_actions']:.2f}")


if __name__ == "__main__":
    main()
