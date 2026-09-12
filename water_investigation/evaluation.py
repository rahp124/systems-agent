"""Evaluate three policies against held-out scenarios from a Net3 trace ensemble."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from random import Random
from statistics import mean

from .analytic import Action, expected_information_gain, posterior_after, score_action
from .ensemble import DEFAULT_OUTPUT, HYPOTHESES, ScenarioSpec, load_ensemble

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "artifacts" / "net3-evaluation.json"
CONCLUSION_THRESHOLD = 0.75
MAX_INITIAL_POSTERIOR = 0.70
MIN_SECOND_INITIAL_POSTERIOR = 0.15
OUTCOME_SPACES = {
    "initial_telemetry": ("quality_signal", "pressure_high", "pressure_low", "unresolved"),
    "field_chlorine_grab": ("detected", "clear"),
    "lab_chlorine_assay": ("detected", "clear"),
    "portable_pressure_reading": ("higher", "lower", "stable"),
    "wait": ("flow_changed", "steady"),
}
NOISE_RATES = {
    "initial_telemetry": 0.45,
    "field_chlorine_grab": 0.10,
    "lab_chlorine_assay": 0.02,
    "portable_pressure_reading": 0.12,
    "wait": 0.00,
}


@dataclass(frozen=True)
class TraceScenario:
    spec: ScenarioSpec
    outcomes: dict[str, str]
    initial_outcome: str = "unresolved"


def _noisy_outcome(spec: ScenarioSpec, channel: str, outcome: str, noise_multiplier: float) -> str:
    """Apply reproducible, channel-specific categorical measurement noise."""
    rng = Random(f"{spec.seed}:{channel}")
    if rng.random() >= NOISE_RATES[channel] * noise_multiplier:
        return outcome
    alternatives = [candidate for candidate in OUTCOME_SPACES[channel] if candidate != outcome]
    return rng.choice(alternatives)


def _outcomes(spec: ScenarioSpec, pressure, flow, quality, baseline, noise_multiplier: float) -> tuple[str, dict[str, str]]:
    """Extract action results from stored traces; no event label is consulted."""
    baseline_pressure, baseline_flow, baseline_quality = baseline
    quality_peak = float((quality - baseline_quality).max())
    pressure_delta = pressure[:, 0] - baseline_pressure[:, 0]
    flow_change = float(abs(flow - baseline_flow).max())
    initial_pressure = pressure[:13, 0] - baseline_pressure[:13, 0]
    initial_quality = float((quality[:13] - baseline_quality[:13]).max())
    initial = "quality_signal" if initial_quality > 1e-6 else "pressure_high" if initial_pressure.max() > 0.4 else "pressure_low" if initial_pressure.min() < -0.02 else "unresolved"
    outcomes = {
        "field_chlorine_grab": "detected" if quality_peak > 1e-6 else "clear",
        "lab_chlorine_assay": "detected" if quality_peak > 1e-7 else "clear",
        "portable_pressure_reading": "higher" if pressure_delta.max() > 0.4 else "lower" if pressure_delta.min() < -0.02 else "stable",
        # At this short horizon, passive waiting is deliberately retained as a
        # low-cost but weak action. It should not dominate an informative sample.
        "wait": "flow_changed" if flow_change > 1.0 else "steady",
    }
    return (_noisy_outcome(spec, "initial_telemetry", initial, noise_multiplier),
            {channel: _noisy_outcome(spec, channel, outcome, noise_multiplier) for channel, outcome in outcomes.items()})


def scenarios_from_ensemble(path: Path, noise_multiplier: float = 1.0) -> list[TraceScenario]:
    if not 0 <= noise_multiplier <= 2:
        raise ValueError("noise_multiplier must be between zero and two")
    specs, pressure, flow, quality, baseline = load_ensemble(path)
    scenarios = []
    for index, spec in enumerate(specs):
        initial_outcome, outcomes = _outcomes(spec, pressure[index], flow[index], quality[index], baseline, noise_multiplier)
        scenarios.append(TraceScenario(spec, outcomes, initial_outcome))
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


def _choose(policy: str, belief, available: list[Action], rng: Random) -> Action:
    if policy == "eig_per_cost":
        return max(available, key=lambda action: (score_action(belief, action), action.name))
    if policy == "cheapest_first":
        return min(available, key=lambda action: (action.cost, action.name))
    if policy == "random":
        return rng.choice(available)
    raise ValueError(f"unknown policy: {policy}")


def run_episode(scenario: TraceScenario, actions: tuple[Action, ...], telemetry: Action, policy: str, seed: int) -> dict[str, object]:
    belief = initial_posterior(scenario, telemetry)
    remaining = list(actions)
    rng = Random(seed)
    total_cost = 0.0
    selected: list[str] = []
    for _ in range(3):
        action = _choose(policy, belief, remaining, rng)
        selected.append(action.name)
        total_cost += action.cost
        belief = posterior_after(belief, action, scenario.outcomes[action.name])
        remaining.remove(action)
        # Field and lab assays observe the same physical sample in this first
        # harness. Treating their outcomes as conditionally independent would
        # double-count evidence, so selecting either excludes the other.
        if action.name in {"field_chlorine_grab", "lab_chlorine_assay"}:
            remaining = [candidate for candidate in remaining
                         if candidate.name not in {"field_chlorine_grab", "lab_chlorine_assay"}]
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
        "posterior": belief,
    }


def evaluate(path: Path = DEFAULT_OUTPUT, episodes: int = 100, seed: int = 20260911, noise_multiplier: float = 1.0) -> dict[str, object]:
    scenarios = scenarios_from_ensemble(path, noise_multiplier)
    training, held_out = split_scenarios(scenarios)
    if not held_out:
        raise ValueError("ensemble does not contain held-out scenarios")
    actions = empirical_actions(training)
    telemetry = empirical_initial_telemetry(training)
    eligible = [scenario for scenario in held_out if is_ambiguous(initial_posterior(scenario, telemetry))]
    if not eligible:
        raise ValueError("no held-out scenarios met the ambiguity gate")
    rng = Random(seed)
    report: dict[str, object] = {
        "ensemble": str(path), "episodes": episodes,
        "training_scenarios": len(training), "held_out_scenarios": len(held_out),
        "eligible_held_out_scenarios": len(eligible), "rejected_held_out_scenarios": len(held_out) - len(eligible),
        "ambiguity_gate": {"max_initial_posterior": MAX_INITIAL_POSTERIOR, "min_second_initial_posterior": MIN_SECOND_INITIAL_POSTERIOR},
        "noise_rates": NOISE_RATES, "noise_multiplier": noise_multiplier, "policies": {},
    }
    for policy in ("eig_per_cost", "random", "cheapest_first"):
        runs = [run_episode(rng.choice(eligible), actions, telemetry, policy, rng.randrange(2**31)) for _ in range(episodes)]
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
    parser.add_argument("--noise-multiplier", type=float, default=1.0)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    report = evaluate(args.ensemble, args.episodes, args.seed, args.noise_multiplier)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(args.output)
    for name, metrics in report["policies"].items():
        print(f"{name}: accuracy={metrics['accuracy']:.3f} cost={metrics['mean_cost']:.2f} actions={metrics['mean_actions']:.2f}")


if __name__ == "__main__":
    main()
