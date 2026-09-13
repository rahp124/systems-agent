"""Read-only analysis of public EPA SDWIS violation exports."""
from __future__ import annotations

import argparse
import csv
import json
import zipfile
from collections import Counter
from pathlib import Path

EPA_SDWIS_DOWNLOAD = "https://echo.epa.gov/tools/data-downloads/sdwa-download-summary"
REQUIRED_COLUMNS = frozenset({"PWSID", "VIOLATION_CODE", "COMPL_PER_BEGIN_DATE"})


def _rows(path: Path):
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist()
                     if name.upper().endswith("SDWA_VIOLATIONS.CSV")]
            if len(names) != 1:
                raise ValueError("SDWIS archive must contain exactly one SDWA_VIOLATIONS.csv file")
            with archive.open(names[0]) as input_file:
                yield from csv.DictReader((line.decode("utf-8-sig") for line in input_file))
    else:
        with path.open(newline="", encoding="utf-8-sig") as input_file:
            yield from csv.DictReader(input_file)


def analyze_violations(path: Path, state: str | None = None) -> dict[str, object]:
    rows = list(_rows(path))
    if not rows or not REQUIRED_COLUMNS <= set(rows[0]):
        raise ValueError("SDWIS violations input requires PWSID, VIOLATION_CODE, and COMPL_PER_BEGIN_DATE")
    if state:
        rows = [row for row in rows if row.get("PRIMACY_AGENCY_CODE") == state.upper()]
    codes = Counter(row["VIOLATION_CODE"] for row in rows if row["VIOLATION_CODE"])
    systems = {row["PWSID"] for row in rows if row["PWSID"]}
    dates = sorted(row["COMPL_PER_BEGIN_DATE"] for row in rows if row["COMPL_PER_BEGIN_DATE"])
    return {"source": "EPA SDWIS public compliance export", "source_url": EPA_SDWIS_DOWNLOAD,
            "scope": {"primacy_agency": state.upper() if state else "all", "input": str(path)},
            "violation_records": len(rows), "public_water_systems": len(systems),
            "date_range": [dates[0], dates[-1]] if dates else None,
            "top_violation_codes": [{"code": code, "count": count}
                                    for code, count in codes.most_common(10)],
            "interpretation_limit": "Compliance records are public context, not SCADA telemetry, incident resolution, or recommendation validation."}


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a public EPA SDWIS violations export.")
    parser.add_argument("--input", type=Path, required=True, help="CSV or ZIP from the EPA SDWIS download")
    parser.add_argument("--state", help="Optional two-letter primacy agency code")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = analyze_violations(args.input, args.state)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
