"""Run a deterministic uncertainty sensitivity sweep for the first evaluation harness."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ensemble import DEFAULT_OUTPUT
from .evaluation import NOISE_RATES, ROOT, evaluate

DEFAULT_REPORT = ROOT / "artifacts" / "net3-noise-sensitivity.json"
MULTIPLIERS = (0.0, 0.5, 1.0, 1.5, 2.0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate policy robustness across configured noise levels.")
    parser.add_argument("--ensemble", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260912)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    results = []
    for multiplier in MULTIPLIERS:
        try:
            report = evaluate(args.ensemble, args.episodes, args.seed, multiplier)
            results.append({
                "noise_multiplier": multiplier,
                "eligible_held_out_scenarios": report["eligible_held_out_scenarios"],
                "rejected_held_out_scenarios": report["rejected_held_out_scenarios"],
                "policies": {name: {key: values[key] for key in ("accuracy", "mean_cost", "mean_actions")}
                             for name, values in report["policies"].items()},
            })
        except ValueError as error:
            results.append({"noise_multiplier": multiplier, "error": str(error)})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"base_noise_rates": NOISE_RATES, "results": results}, indent=2) + "\n")
    print(args.output)
    for result in results:
        if "error" in result:
            print(f"noise={result['noise_multiplier']:.1f}: {result['error']}")
        else:
            eig = result["policies"]["eig_per_cost"]
            print(f"noise={result['noise_multiplier']:.1f}: eig accuracy={eig['accuracy']:.3f} cost={eig['mean_cost']:.2f}")


if __name__ == "__main__":
    main()
