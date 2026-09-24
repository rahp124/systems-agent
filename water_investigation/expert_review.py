"""Build and analyze a blinded expert review of next-observation choices."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

from .evaluation import ROOT, evaluate
from .final_benchmark import DEFAULT_PROTOCOL, load_protocol

STUDY_DIR = ROOT / "studies" / "expert-review"
DEFAULT_CASEBOOK = STUDY_DIR / "casebook.json"
DEFAULT_ANSWER_KEY = STUDY_DIR / "coordinator-answer-key.json"
ACTION_DETAILS = {
    "field_chlorine_grab": {
        "label": "Field chlorine grab",
        "description": "Collect a rapid field chlorine measurement.",
        "relative_cost": 1.0,
        "turnaround_steps": 1,
    },
    "lab_chlorine_assay": {
        "label": "Lab chlorine assay",
        "description": "Send a chlorine sample for laboratory analysis.",
        "relative_cost": 5.0,
        "turnaround_steps": 8,
    },
    "portable_pressure_reading": {
        "label": "Portable pressure reading",
        "description": "Take an independent portable pressure measurement.",
        "relative_cost": 3.0,
        "turnaround_steps": 2,
    },
    "wait": {
        "label": "Wait for telemetry",
        "description": "Wait for the next scheduled telemetry update.",
        "relative_cost": 0.5,
        "turnaround_steps": 1,
    },
}


def _select_cases(runs: list[dict[str, object]], per_truth: int = 3) -> list[dict[str, object]]:
    unique = {run["scenario_id"]: run for run in runs}
    selected = []
    # Sensor-fault episodes do not pass the frozen ambiguity gate in the final
    # benchmark. Keep that as a documented scope limit rather than weakening the
    # gate after seeing the benchmark results.
    for truth in ("contamination", "leak"):
        candidates = [run for run in unique.values() if run["truth"] == truth]
        candidates.sort(key=lambda run: (bool(run["correct"]), run["scenario_id"]))
        if len(candidates) < per_truth:
            raise ValueError(f"not enough unique {truth} cases for expert review")
        selected.extend(candidates[:per_truth])
    return selected


def build_casebook(protocol_path: Path = DEFAULT_PROTOCOL) -> tuple[dict[str, object], dict[str, object]]:
    protocol = load_protocol(protocol_path)
    thresholds = protocol["thresholds"]
    public_cases, answers = [], []
    for ensemble in protocol["ensembles"]:
        path = ROOT / ensemble["artifact"]
        if not path.exists():
            raise FileNotFoundError(f"missing {path}; build the frozen benchmark ensembles first")
        report = evaluate(
            path, protocol["episodes_per_ensemble"], ensemble["evaluation_seed"],
            protocol["risk_lambda"], thresholds["conclusion_posterior"],
            thresholds["max_initial_posterior"], thresholds["min_second_initial_posterior"],
            thresholds["max_actions"],
        )
        for run in _select_cases(report["policies"]["eig_per_cost"]["runs"]):
            case_id = f"{ensemble['id']}--{run['scenario_id']}"
            recommendation = run["actions"][0]
            public_cases.append({
                "case_id": case_id,
                "network": ensemble["network"],
                "sensor_layout": ensemble["sensor_layout"],
                "scenario_statement": "Pressure, flow, and water-quality evidence do not yet establish a cause.",
                "initial_telemetry": {
                    "category": run["initial_outcome"],
                    "fixed_pressure_delta_psi": run["measurements"]["fixed_pressure_delta_psi"],
                    "other_channels": "unresolved",
                },
                "initial_model_beliefs": run["initial_posterior"],
                "belief_note": "Model estimates derived from the initial synthetic telemetry; not field measurements or calibrated probabilities.",
                "competing_explanations": ["contamination", "leak", "sensor_fault"],
                "available_actions": ACTION_DETAILS,
                "phase_1_instruction": "Choose the next observation before opening phase_2.",
                "phase_2": {
                    "agent_recommendation": recommendation,
                    "agent_recommendation_label": ACTION_DETAILS[recommendation]["label"],
                    "rationale": "Highest expected uncertainty reduction per relative cost under the frozen policy.",
                },
            })
            answers.append({
                "case_id": case_id,
                "synthetic_ground_truth": run["truth"],
                "agent_prediction": run["prediction"],
                "agent_correct": run["correct"],
                "agent_action_sequence": run["actions"],
                "final_posterior": run["posterior"],
            })
    public = {
        "schema_version": 1,
        "study": "expert-next-observation-review",
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": protocol["sha256"],
        "case_count": len(public_cases),
        "blinding": "Ground truth and final prediction are excluded. Record phase 1 before revealing phase 2.",
        "sampling_note": "Three contamination and three leak cases were selected from each ensemble. Sensor fault remains an available explanation, but no sensor-fault episode passed the frozen ambiguity gate.",
        "cases": public_cases,
    }
    key = {
        "schema_version": 1,
        "study": "expert-next-observation-review-coordinator-key",
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": protocol["sha256"],
        "case_count": len(answers),
        "answers": answers,
    }
    return public, key


def write_casebook(protocol_path: Path = DEFAULT_PROTOCOL,
                   casebook_path: Path = DEFAULT_CASEBOOK,
                   answer_key_path: Path = DEFAULT_ANSWER_KEY) -> None:
    casebook, answer_key = build_casebook(protocol_path)
    casebook_path.parent.mkdir(parents=True, exist_ok=True)
    casebook_path.write_text(json.dumps(casebook, indent=2) + "\n")
    answer_key_path.write_text(json.dumps(answer_key, indent=2) + "\n")


def analyze_responses(response_path: Path, casebook_path: Path = DEFAULT_CASEBOOK) -> dict[str, object]:
    casebook = json.loads(casebook_path.read_text())
    cases = {case["case_id"]: case for case in casebook["cases"]}
    rows = list(csv.DictReader(response_path.open(newline="", encoding="utf-8")))
    if not rows:
        raise ValueError("response file is empty")
    required = {"reviewer_id", "case_id", "reviewer_action", "confidence_1_5",
                "recommendation_reasonable_1_5", "advisory_safety"}
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"response file is missing columns: {sorted(missing)}")
    normalized = []
    seen = set()
    for row in rows:
        if row["case_id"] not in cases:
            raise ValueError(f"unknown case_id: {row['case_id']}")
        if row["reviewer_action"] not in ACTION_DETAILS:
            raise ValueError(f"unknown reviewer_action: {row['reviewer_action']}")
        response_key = (row["reviewer_id"], row["case_id"])
        if response_key in seen:
            raise ValueError(f"duplicate reviewer-case response: {response_key}")
        seen.add(response_key)
        confidence = int(row["confidence_1_5"])
        reasonable = int(row["recommendation_reasonable_1_5"])
        if confidence not in range(1, 6) or reasonable not in range(1, 6):
            raise ValueError("ratings must be integers from 1 through 5")
        safety = row["advisory_safety"].strip().lower()
        if safety not in {"safe", "uncertain", "unsafe"}:
            raise ValueError("advisory_safety must be safe, uncertain, or unsafe")
        normalized.append({**row, "confidence": confidence, "reasonable": reasonable,
                           "safety": safety,
                           "agent_action": cases[row["case_id"]]["phase_2"]["agent_recommendation"]})
    agreements = [row["reviewer_action"] == row["agent_action"] for row in normalized]
    by_case: dict[str, list[str]] = defaultdict(list)
    for row in normalized:
        by_case[row["case_id"]].append(row["reviewer_action"])
    pairwise = []
    for actions in by_case.values():
        for left in range(len(actions)):
            for right in range(left + 1, len(actions)):
                pairwise.append(actions[left] == actions[right])
    safety = Counter(row["safety"] for row in normalized)
    return {
        "schema_version": 1,
        "response_count": len(normalized),
        "reviewer_count": len({row["reviewer_id"] for row in normalized}),
        "case_count": len(by_case),
        "exact_agent_agreement": mean(agreements),
        "mean_reviewer_confidence": mean(row["confidence"] for row in normalized),
        "mean_recommendation_reasonableness": mean(row["reasonable"] for row in normalized),
        "median_recommendation_reasonableness": median(row["reasonable"] for row in normalized),
        "advisory_safety": dict(safety),
        "unsafe_rate": safety["unsafe"] / len(normalized),
        "pairwise_inter_reviewer_agreement": mean(pairwise) if pairwise else None,
        "interpretation_limit": "Agreement measures expert judgment of recommendation plausibility, not diagnostic correctness or field performance.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    build.add_argument("--casebook", type=Path, default=DEFAULT_CASEBOOK)
    build.add_argument("--answer-key", type=Path, default=DEFAULT_ANSWER_KEY)
    analyze = subparsers.add_parser("analyze")
    analyze.add_argument("responses", type=Path)
    analyze.add_argument("--casebook", type=Path, default=DEFAULT_CASEBOOK)
    analyze.add_argument("--output", type=Path, default=STUDY_DIR / "results.json")
    args = parser.parse_args()
    if args.command == "build":
        write_casebook(args.protocol, args.casebook, args.answer_key)
        print(args.casebook)
        print(args.answer_key)
    else:
        result = analyze_responses(args.responses, args.casebook)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(args.output)


if __name__ == "__main__":
    main()
