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


@dataclass(frozen=True)
class TraceScenario:
    spec: ScenarioSpec
    outcomes: dict[str, str]


def _outcomes(pressure, flow, quality, baseline) -> dict[str, str]:
    """Extract action results from stored traces; no event label is consulted."""
    baseline_pressure, baseline_flow, baseline_quality = baseline
    quality_peak = float((quality - baseline_quality).max())
    pressure_delta = pressure[:, 0] - baseline_pressure[:, 0]
    flow_change = float(abs(flow - baseline_flow).max())
    return {
        "field_chlorine_grab": "detected" if quality_peak > 1e-6 else "clear",
        "lab_chlorine_assay": "detected" if quality_peak > 1e-7 else "clear",
        "portable_pressure_reading": "higher" if pressure_delta.max() > 0.4 else "lower" if pressure_delta.min() < -0.02 else "stable",
        # At this short horizon, passive waiting is deliberately retained as a
        # low-cost but weak action. It should not dominate an informative sample.
        "wait": "flow_changed" if flow_change > 1.0 else "steady",
    }


def scenarios_from_ensemble(path: Path) -> list[TraceScenario]:
    specs, pressure, flow, quality, baseline = load_ensemble(path)
    return [TraceScenario(spec, _outcomes(pressure[index], flow[index], quality[index], baseline))
            for index, spec in enumerate(specs)]


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
        outcomes = sorted({scenario.outcomes[name] for scenario in training})
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


def _choose(policy: str, belief, available: list[Action], rng: Random) -> Action:
    if policy == "eig_per_cost":
        return max(available, key=lambda action: (score_action(belief, action), action.name))
    if policy == "cheapest_first":
        return min(available, key=lambda action: (action.cost, action.name))
    if policy == "random":
        return rng.choice(available)
    raise ValueError(f"unknown policy: {policy}")


def run_episode(scenario: TraceScenario, actions: tuple[Action, ...], policy: str, seed: int) -> dict[str, object]:
    belief = {hypothesis: 1 / len(HYPOTHESES) for hypothesis in HYPOTHESES}
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
        "posterior": belief,
    }


def evaluate(path: Path = DEFAULT_OUTPUT, episodes: int = 100, seed: int = 20260911) -> dict[str, object]:
    scenarios = scenarios_from_ensemble(path)
    training, held_out = split_scenarios(scenarios)
    if not held_out:
        raise ValueError("ensemble does not contain held-out scenarios")
    actions = empirical_actions(training)
    rng = Random(seed)
    report: dict[str, object] = {
        "ensemble": str(path), "episodes": episodes,
        "training_scenarios": len(training), "held_out_scenarios": len(held_out), "policies": {},
    }
    for policy in ("eig_per_cost", "random", "cheapest_first"):
        runs = [run_episode(rng.choice(held_out), actions, policy, rng.randrange(2**31)) for _ in range(episodes)]
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
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    report = evaluate(args.ensemble, args.episodes, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(args.output)
    for name, metrics in report["policies"].items():
        print(f"{name}: accuracy={metrics['accuracy']:.3f} cost={metrics['mean_cost']:.2f} actions={metrics['mean_actions']:.2f}")


if __name__ == "__main__":
    main()
