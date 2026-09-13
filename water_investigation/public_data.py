"""Read-only analysis of public EPA SDWIS violation exports."""
from __future__ import annotations

import argparse
import csv
import json
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path

EPA_SDWIS_DOWNLOAD = "https://echo.epa.gov/tools/data-downloads/sdwa-download-summary"
REQUIRED_COLUMNS = frozenset({"PWSID", "VIOLATION_CODE", "COMPL_PER_BEGIN_DATE"})


def _rows(path: Path):
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist()
                     if Path(name).name.upper() in {"SDWA_VIOLATIONS.CSV", "SDWA_VIOLATIONS_ENFORCEMENT.CSV"}]
            if len(names) != 1:
                raise ValueError("SDWIS archive must contain exactly one violations CSV file")
            with archive.open(names[0]) as input_file:
                yield from csv.DictReader((line.decode("utf-8-sig") for line in input_file))
    else:
        with path.open(newline="", encoding="utf-8-sig") as input_file:
            yield from csv.DictReader(input_file)


def analyze_violations(path: Path, pwsid_prefix: str | None = None,
                       provenance: dict[str, str] | None = None) -> dict[str, object]:
    record_count = 0
    systems, codes = set(), Counter()
    first_date, last_date = None, None
    header_checked = False
    for row in _rows(path):
        if not header_checked:
            if not REQUIRED_COLUMNS <= set(row):
                raise ValueError("SDWIS violations input requires PWSID, VIOLATION_CODE, and COMPL_PER_BEGIN_DATE")
            header_checked = True
        if pwsid_prefix and not row["PWSID"].startswith(pwsid_prefix):
            continue
        record_count += 1
        if row["PWSID"]:
            systems.add(row["PWSID"])
        if row["VIOLATION_CODE"]:
            codes[row["VIOLATION_CODE"]] += 1
        if date := row["COMPL_PER_BEGIN_DATE"]:
            parsed_date = datetime.strptime(date, "%m/%d/%Y").date()
            first_date = min(first_date, parsed_date) if first_date else parsed_date
            last_date = max(last_date, parsed_date) if last_date else parsed_date
    if not header_checked:
        raise ValueError("SDWIS violations input requires PWSID, VIOLATION_CODE, and COMPL_PER_BEGIN_DATE")
    return {"source": "EPA SDWIS public compliance export", "source_url": EPA_SDWIS_DOWNLOAD,
            "provenance": provenance or {},
            "scope": {"pwsid_prefix": pwsid_prefix or "all", "input": str(path)},
            "violation_records": record_count, "public_water_systems": len(systems),
            "date_range": [first_date.isoformat(), last_date.isoformat()] if first_date else None,
            "top_violation_codes": [{"code": code, "count": count}
                                    for code, count in codes.most_common(10)],
            "interpretation_limit": "Compliance records are public context, not SCADA telemetry, incident resolution, or recommendation validation."}


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a public EPA SDWIS violations export.")
    parser.add_argument("--input", type=Path, required=True, help="CSV or ZIP from the EPA SDWIS download")
    parser.add_argument("--pwsid-prefix", help="Optional public-water-system ID prefix")
    parser.add_argument("--source-sha256", help="SHA-256 of the downloaded source archive")
    parser.add_argument("--source-retrieved-at", help="ISO-8601 retrieval timestamp")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    provenance = {key: value for key, value in {
        "sha256": args.source_sha256, "retrieved_at": args.source_retrieved_at,
    }.items() if value}
    report = analyze_violations(args.input, args.pwsid_prefix, provenance)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
