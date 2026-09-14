"""Compact, provenance-preserving summaries across independent ensembles."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluation import evaluate

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "multi-network-replication.json"


def summarize(ensembles: list[Path], episodes: int, seed: int) -> dict[str, object]:
    """Evaluate each ensemble separately; never pool their scenarios or results."""
    reports = [evaluate(path, episodes, seed + index) for index, path in enumerate(ensembles)]
    return {"episodes_per_replication": episodes, "replications": [
        {"ensemble": report["ensemble"], "ensemble_metadata": {
            key: report["ensemble_metadata"][key]
            for key in ("schema_version", "network", "sensor_layout", "seed")},
         "scenario_count": len(report["ensemble_metadata"]["scenarios"]),
         "training_scenarios": report["training_scenarios"],
         "held_out_scenarios": report["held_out_scenarios"],
         "eligible_held_out_scenarios": report["eligible_held_out_scenarios"],
         "policies": {name: {key: values[key] for key in ("accuracy", "mean_cost", "mean_actions")}
                      for name, values in report["policies"].items()}}
        for report in reports],
        "interpretation_limit": "Each network/layout is evaluated separately on synthetic traces. This report does not pool results, estimate cross-network generalization, or establish operational performance."}


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize separate synthetic network/layout replications.")
    parser.add_argument("--ensemble", type=Path, action="append", required=True)
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = summarize(args.ensemble, args.episodes, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
