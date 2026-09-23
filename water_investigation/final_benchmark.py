"""Run a prespecified benchmark across independently generated ensembles."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from random import Random
from statistics import mean

from .ensemble import build_ensemble
from .evaluation import ROOT, evaluate

DEFAULT_PROTOCOL = ROOT / "benchmark_protocol.json"
DEFAULT_OUTPUT = ROOT / "artifacts" / "final-independent-benchmark.json"


def load_protocol(path: Path = DEFAULT_PROTOCOL) -> dict[str, object]:
    raw = path.read_bytes()
    protocol = json.loads(raw)
    required = {"schema_version", "protocol_id", "reference_policy", "policies",
                "episodes_per_ensemble", "bootstrap_samples", "confidence_level",
                "risk_lambda", "thresholds", "ensembles", "interpretation_limit"}
    missing = required - set(protocol)
    if missing:
        raise ValueError(f"benchmark protocol is missing fields: {sorted(missing)}")
    ensembles = protocol["ensembles"]
    if len(ensembles) < 2 or len({item["generation_seed"] for item in ensembles}) != len(ensembles):
        raise ValueError("protocol requires at least two independently seeded ensembles")
    if not 0 < protocol["confidence_level"] < 1:
        raise ValueError("confidence_level must be between zero and one")
    protocol["sha256"] = hashlib.sha256(raw).hexdigest()
    return protocol


def build_ensembles(protocol: dict[str, object], rebuild: bool = False) -> list[Path]:
    paths = []
    for item in protocol["ensembles"]:
        path = ROOT / item["artifact"]
        if rebuild or not path.exists():
            build_ensemble(item["scenarios_per_class"], item["generation_seed"], path,
                           item["network"], item["sensor_layout"])
        paths.append(path)
    return paths


def _percentile_interval(estimates: list[float], confidence_level: float) -> list[float]:
    estimates.sort()
    tail = (1 - confidence_level) / 2
    lower = min(len(estimates) - 1, int(tail * len(estimates)))
    upper = min(len(estimates) - 1, int((1 - tail) * len(estimates)) - 1)
    return [estimates[lower], estimates[upper]]


def hierarchical_interval(groups: list[list[float]], seed: int, samples: int,
                          confidence_level: float) -> list[float]:
    """Bootstrap ensembles first and episodes second to preserve clustering."""
    if not groups or any(not group for group in groups):
        raise ValueError("hierarchical bootstrap requires non-empty groups")
    rng = Random(seed)
    estimates = []
    for _ in range(samples):
        chosen_groups = rng.choices(groups, k=len(groups))
        values = [value for group in chosen_groups for value in rng.choices(group, k=len(group))]
        estimates.append(mean(values))
    return _percentile_interval(estimates, confidence_level)


def _failure_summary(runs: list[dict[str, object]]) -> dict[str, object]:
    failures = [run for run in runs if not run["correct"]]
    confusions = Counter((run["truth"], run["prediction"]) for run in failures)
    sequences = Counter(tuple(run["actions"]) for run in failures)
    return {
        "count": len(failures),
        "rate": len(failures) / len(runs),
        "confusions": [
            {"truth": truth, "prediction": prediction, "count": count}
            for (truth, prediction), count in confusions.most_common()
        ],
        "most_common_failed_action_sequences": [
            {"actions": list(actions), "count": count}
            for actions, count in sequences.most_common(5)
        ],
    }


def summarize(protocol: dict[str, object], reports: list[dict[str, object]]) -> dict[str, object]:
    policies = protocol["policies"]
    reference = protocol["reference_policy"]
    samples = protocol["bootstrap_samples"]
    confidence = protocol["confidence_level"]
    summary: dict[str, object] = {}
    for policy_index, policy in enumerate(policies):
        run_groups = [report["policies"][policy]["runs"] for report in reports]
        all_runs = [run for group in run_groups for run in group]
        accuracy_groups = [[float(run["correct"]) for run in group] for group in run_groups]
        cost_groups = [[float(run["cost"]) for run in group] for group in run_groups]
        action_groups = [[float(len(run["actions"])) for run in group] for group in run_groups]
        summary[policy] = {
            "accuracy": mean(value for group in accuracy_groups for value in group),
            "accuracy_95_ci": hierarchical_interval(accuracy_groups, 31000 + policy_index,
                                                     samples, confidence),
            "mean_cost": mean(value for group in cost_groups for value in group),
            "mean_cost_95_ci": hierarchical_interval(cost_groups, 32000 + policy_index,
                                                      samples, confidence),
            "mean_actions": mean(value for group in action_groups for value in group),
            "mean_actions_95_ci": hierarchical_interval(action_groups, 33000 + policy_index,
                                                         samples, confidence),
            "failure_summary": _failure_summary(all_runs),
        }
    comparisons = {}
    for policy_index, comparator in enumerate(policy for policy in policies if policy != reference):
        accuracy_groups, cost_groups = [], []
        for report in reports:
            reference_runs = report["policies"][reference]["runs"]
            comparator_runs = report["policies"][comparator]["runs"]
            if [run["scenario_id"] for run in reference_runs] != [run["scenario_id"] for run in comparator_runs]:
                raise ValueError("policies were not evaluated on identical episodes")
            accuracy_groups.append([float(left["correct"]) - float(right["correct"])
                                    for left, right in zip(reference_runs, comparator_runs)])
            cost_groups.append([float(left["cost"]) - float(right["cost"])
                                for left, right in zip(reference_runs, comparator_runs)])
        comparisons[comparator] = {
            "reference_minus_comparator": True,
            "mean_accuracy_difference": mean(value for group in accuracy_groups for value in group),
            "accuracy_difference_95_ci": hierarchical_interval(
                accuracy_groups, 34000 + policy_index, samples, confidence),
            "mean_cost_difference": mean(value for group in cost_groups for value in group),
            "cost_difference_95_ci": hierarchical_interval(
                cost_groups, 35000 + policy_index, samples, confidence),
        }
    return {"absolute_policy_metrics": summary, "paired_comparisons": comparisons}


def run(protocol_path: Path = DEFAULT_PROTOCOL, build: bool = False,
        rebuild: bool = False) -> dict[str, object]:
    protocol = load_protocol(protocol_path)
    paths = build_ensembles(protocol, rebuild) if build or rebuild else [
        ROOT / item["artifact"] for item in protocol["ensembles"]
    ]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing ensemble artifacts; rerun with --build: {missing}")
    thresholds = protocol["thresholds"]
    reports = [evaluate(
        path, protocol["episodes_per_ensemble"], item["evaluation_seed"],
        protocol["risk_lambda"], thresholds["conclusion_posterior"],
        thresholds["max_initial_posterior"], thresholds["min_second_initial_posterior"],
        thresholds["max_actions"],
    ) for item, path in zip(protocol["ensembles"], paths)]
    for item, report in zip(protocol["ensembles"], reports):
        metadata = report["ensemble_metadata"]
        expected = (item["network"], item["sensor_layout"], item["generation_seed"])
        observed = (metadata["network"], metadata["sensor_layout"], metadata["seed"])
        if observed != expected:
            raise ValueError(f"ensemble artifact {item['artifact']} does not match protocol: "
                             f"expected {expected}, observed {observed}")
    result = {
        "schema_version": 1,
        "protocol": {key: value for key, value in protocol.items() if key != "ensembles"},
        "ensembles": [
            {"id": item["id"], "artifact": item["artifact"],
             "network": item["network"], "sensor_layout": item["sensor_layout"],
             "generation_seed": item["generation_seed"],
             "evaluation_seed": item["evaluation_seed"],
             "scenario_count": len(report["ensemble_metadata"]["scenarios"]),
             "training_scenarios": report["training_scenarios"],
             "held_out_scenarios": report["held_out_scenarios"],
             "eligible_held_out_scenarios": report["eligible_held_out_scenarios"],
             "policy_metrics": {name: {key: values[key] for key in
                                ("accuracy", "mean_cost", "mean_actions", "mean_cost_when_correct")}
                                for name, values in report["policies"].items()}}
            for item, report in zip(protocol["ensembles"], reports)
        ],
        "total_evaluated_episodes_per_policy": protocol["episodes_per_ensemble"] * len(reports),
        **summarize(protocol, reports),
        "interpretation_limit": protocol["interpretation_limit"],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    result = run(args.protocol, args.build, args.rebuild)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(args.output)
    for policy, metrics in result["absolute_policy_metrics"].items():
        print(f"{policy}: accuracy={metrics['accuracy']:.3f} "
              f"cost={metrics['mean_cost']:.2f} actions={metrics['mean_actions']:.2f}")


if __name__ == "__main__":
    main()
