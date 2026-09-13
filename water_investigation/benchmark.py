"""Run paired policy comparisons over fixed episode seeds."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from random import Random
from statistics import mean

from .ensemble import DEFAULT_OUTPUT as DEFAULT_ENSEMBLE
from .evaluation import ROOT, evaluate

DEFAULT_BENCHMARK = ROOT / "artifacts" / "net3-multiseed-benchmark.json"
DEFAULT_SEEDS = (20260911, 20260912, 20260913, 20260914, 20260915)
REFERENCE_POLICY = "eig_per_cost"


def bootstrap_interval(values: list[float], seed: int, samples: int = 1000) -> list[float]:
    """Return a deterministic percentile bootstrap interval for a paired mean."""
    if not values:
        raise ValueError("cannot bootstrap an empty sample")
    rng = Random(seed)
    estimates = sorted(mean(rng.choices(values, k=len(values))) for _ in range(samples))
    return [estimates[25], estimates[975]]


def paired_differences(report: dict[str, object], reference: str, comparator: str) -> tuple[list[float], list[float]]:
    """Return reference-minus-comparator accuracy and cost for identical episodes."""
    policies = report["policies"]
    reference_runs = policies[reference]["runs"]
    comparator_runs = policies[comparator]["runs"]
    if len(reference_runs) != len(comparator_runs):
        raise ValueError("paired policies have different episode counts")
    if any(left["scenario_id"] != right["scenario_id"]
           for left, right in zip(reference_runs, comparator_runs)):
        raise ValueError("paired policies were evaluated on different scenarios")
    return ([float(left["correct"]) - float(right["correct"])
             for left, right in zip(reference_runs, comparator_runs)],
            [float(left["cost"]) - float(right["cost"])
             for left, right in zip(reference_runs, comparator_runs)])


def benchmark(path: Path = DEFAULT_ENSEMBLE, episodes: int = 100,
              seeds: tuple[int, ...] = DEFAULT_SEEDS) -> dict[str, object]:
    if not seeds:
        raise ValueError("at least one episode seed is required")
    reports = [evaluate(path, episodes, seed, risk_lambda=0.02) for seed in seeds]
    policy_names = tuple(reports[0]["policies"])
    comparisons = {}
    for comparator in policy_names:
        if comparator == REFERENCE_POLICY:
            continue
        accuracy_deltas, cost_deltas = [], []
        for index, report in enumerate(reports):
            accuracy, cost = paired_differences(report, REFERENCE_POLICY, comparator)
            accuracy_deltas.extend(accuracy)
            cost_deltas.extend(cost)
        comparisons[comparator] = {
            "reference_minus_comparator": True,
            "mean_accuracy_difference": mean(accuracy_deltas),
            "accuracy_difference_95_ci": bootstrap_interval(accuracy_deltas, seeds[0] + len(comparator)),
            "mean_cost_difference": mean(cost_deltas),
            "cost_difference_95_ci": bootstrap_interval(cost_deltas, seeds[-1] + len(comparator)),
        }
    return {
        "ensemble": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "episodes_per_seed": episodes,
        "episode_seeds": list(seeds),
        "total_paired_episodes": episodes * len(seeds),
        "reference_policy": REFERENCE_POLICY,
        "risk_lambda": 0.02,
        "comparisons": comparisons,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark paired policy differences over multiple seeds.")
    parser.add_argument("--ensemble", type=Path, default=DEFAULT_ENSEMBLE)
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--seeds", default=",".join(map(str, DEFAULT_SEEDS)))
    parser.add_argument("--output", type=Path, default=DEFAULT_BENCHMARK)
    args = parser.parse_args()
    seeds = tuple(int(seed) for seed in args.seeds.split(",") if seed)
    result = benchmark(args.ensemble, args.episodes, seeds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(args.output)
    for policy, comparison in result["comparisons"].items():
        print(f"{REFERENCE_POLICY} - {policy}: "
              f"accuracy={comparison['mean_accuracy_difference']:.3f} "
              f"cost={comparison['mean_cost_difference']:.2f}")


if __name__ == "__main__":
    main()
