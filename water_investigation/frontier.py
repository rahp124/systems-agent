"""Sweep the decision-risk cost penalty and report paired bootstrap intervals."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from random import Random
from statistics import mean

from .ensemble import DEFAULT_OUTPUT as DEFAULT_ENSEMBLE
from .evaluation import ROOT, evaluate

DEFAULT_FRONTIER = ROOT / "artifacts" / "net3-risk-frontier.json"
LAMBDAS = (0.0, 0.02, 0.05, 0.10, 0.20)


def _interval(values: list[float], seed: int, samples: int = 1000) -> list[float]:
    rng = Random(seed)
    estimates = sorted(mean(rng.choices(values, k=len(values))) for _ in range(samples))
    return [estimates[25], estimates[975]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a paired risk-aware accuracy-cost frontier.")
    parser.add_argument("--ensemble", type=Path, default=DEFAULT_ENSEMBLE)
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260912)
    parser.add_argument("--output", type=Path, default=DEFAULT_FRONTIER)
    args = parser.parse_args()
    frontier = []
    for risk_lambda in LAMBDAS:
        report = evaluate(args.ensemble, args.episodes, args.seed, risk_lambda)
        runs = report["policies"]["risk_aware"]["runs"]
        frontier.append({"risk_lambda": risk_lambda,
                         "accuracy": mean(run["correct"] for run in runs),
                         "accuracy_95_ci": _interval([float(run["correct"]) for run in runs], args.seed),
                         "mean_cost": mean(run["cost"] for run in runs),
                         "cost_95_ci": _interval([run["cost"] for run in runs], args.seed + 1)})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"episodes": args.episodes, "paired": True, "frontier": frontier}, indent=2) + "\n")
    print(args.output)
    for point in frontier:
        print(f"lambda={point['risk_lambda']:.2f}: accuracy={point['accuracy']:.3f}, cost={point['mean_cost']:.2f}")


if __name__ == "__main__":
    main()
