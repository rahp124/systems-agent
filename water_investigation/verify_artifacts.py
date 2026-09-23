"""Verify the schema-critical fields of tracked reproducibility reports."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "artifacts/sdwis-pwsid-06-public-report.json": ("source", "provenance", "violation_records"),
    "artifacts/wqp-wi-017-nitrate-public-report.json": ("source", "provenance", "result_records"),
    "artifacts/nors-drinking-water-public-report.json": ("source", "provenance", "outbreak_records"),
    "artifacts/multi-network-replication.json": ("episodes_per_replication", "replications", "interpretation_limit"),
    "artifacts/final-independent-benchmark.json": (
        "protocol", "ensembles", "total_evaluated_episodes_per_policy",
        "absolute_policy_metrics", "paired_comparisons", "interpretation_limit",
    ),
}


def verify() -> list[str]:
    """Return checked report paths or raise when a tracked report is incomplete."""
    checked = []
    for relative_path, fields in REQUIRED.items():
        path = ROOT / relative_path
        report = json.loads(path.read_text(encoding="utf-8"))
        missing = [field for field in fields if field not in report]
        if missing:
            raise ValueError(f"{relative_path} is missing required fields: {missing}")
        if "provenance" in report and not {"sha256", "retrieved_at"} <= set(report["provenance"]):
            raise ValueError(f"{relative_path} lacks source checksum or retrieval time")
        checked.append(relative_path)
    return checked


def main() -> None:
    for path in verify():
        print(path)


if __name__ == "__main__":
    main()
