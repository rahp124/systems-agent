"""Read-only analysis of CDC NORS drinking-water outbreak records."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import ssl
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen

import certifi

NORS_ENDPOINT = "https://data.cdc.gov/resource/5xkq-dg7x.csv"
REQUIRED_COLUMNS = frozenset({"year", "state", "primary_mode", "etiology", "illnesses", "hospitalizations", "deaths", "water_exposure", "water_type"})


def build_drinking_water_query(start_year: int | None = None, end_year: int | None = None,
                               state: str | None = None) -> str:
    """Build an exact NORS query for reported drinking-water outbreak records."""
    if (start_year is None) != (end_year is None):
        raise ValueError("start_year and end_year must be supplied together")
    if start_year is None:
        raise ValueError("a bounded query requires an explicit start_year and end_year")
    if start_year and (start_year < 1971 or end_year < start_year):
        raise ValueError("years must be ordered and no earlier than 1971")
    where = ["primary_mode = 'Water'", "water_exposure = 'Drinking water'"]
    if start_year:
        where.append(f"year between {start_year} and {end_year}")
    if state:
        where.append("state = '" + state.replace("'", "''") + "'")
    return f"{NORS_ENDPOINT}?{urlencode({'$where': ' AND '.join(where), '$order': 'year, month', '$limit': '50000'})}"


def download_records(query_url: str, destination: Path) -> dict[str, str]:
    """Download a NORS CSV using verified TLS and return immutable provenance."""
    parsed = urlparse(query_url)
    if parsed.scheme != "https" or parsed.netloc != "data.cdc.gov" or parsed.path != "/resource/5xkq-dg7x.csv":
        raise ValueError("query_url must be an HTTPS CDC NORS resource URL")
    context = ssl.create_default_context(cafile=certifi.where())
    with urlopen(query_url, timeout=120, context=context) as response:
        content = response.read()
    if not content.startswith(b'"year",'):
        raise ValueError("CDC response was not the expected NORS CSV")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return {"query_url": query_url, "sha256": hashlib.sha256(content).hexdigest(),
            "retrieved_at": datetime.now().astimezone().isoformat()}


def _integer(value: str | None) -> int:
    return int(value) if value else 0


def analyze_records(path: Path, provenance: dict[str, str] | None = None) -> dict[str, object]:
    """Summarize record-level NORS health outcomes without inferring water-system causality."""
    states, etiologies, water_types = Counter(), Counter(), Counter()
    record_count = illnesses = hospitalizations = deaths = 0
    outcome_present = Counter()
    first_year, last_year = None, None
    with path.open(newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        if not reader.fieldnames or not REQUIRED_COLUMNS <= set(reader.fieldnames):
            raise ValueError("NORS input is missing required outbreak, outcome, or water-exposure columns")
        for row in reader:
            if row["primary_mode"] != "Water" or row["water_exposure"] != "Drinking water":
                raise ValueError("NORS input must be filtered to Water / Drinking water records")
            record_count += 1
            year = int(row["year"])
            first_year = min(first_year, year) if first_year else year
            last_year = max(last_year, year) if last_year else year
            states[row["state"]] += 1
            etiologies[row["etiology"]] += 1
            water_types[row["water_type"]] += 1
            for field in ("illnesses", "hospitalizations", "deaths"):
                if row[field]:
                    outcome_present[field] += 1
            illnesses += _integer(row["illnesses"])
            hospitalizations += _integer(row["hospitalizations"])
            deaths += _integer(row["deaths"])
    most_common = lambda values: [{"name": name, "records": count}
                                  for name, count in values.most_common(10) if name]
    return {"source": "CDC National Outbreak Reporting System (NORS)", "source_url": NORS_ENDPOINT,
            "provenance": provenance or {}, "scope": {"input": str(path), "primary_mode": "Water", "water_exposure": "Drinking water"},
            "outbreak_records": record_count, "year_range": [first_year, last_year] if first_year else None,
            "record_reported_outcomes": {"illnesses": illnesses, "hospitalizations": hospitalizations, "deaths": deaths},
            "outcome_field_coverage": {field: {"reported": outcome_present[field], "missing": record_count - outcome_present[field]}
                                       for field in ("illnesses", "hospitalizations", "deaths")},
            "states": most_common(states), "etiologies": most_common(etiologies), "water_types": most_common(water_types),
            "interpretation_limit": "NORS is voluntarily reported public-health surveillance. Rows are not linked to utility telemetry or a unique water system, and record-level outcome totals must not be interpreted as agent performance, incident detection coverage, or water-system causality."}


def main() -> None:
    parser = argparse.ArgumentParser(description="Download or analyze CDC NORS drinking-water outbreak records.")
    parser.add_argument("--input", type=Path, help="Previously downloaded NORS CSV")
    parser.add_argument("--download-to", type=Path, help="Ignored local path for a new NORS CSV download")
    parser.add_argument("--start-year", type=int, help="Inclusive start year for a download")
    parser.add_argument("--end-year", type=int, help="Inclusive end year for a download")
    parser.add_argument("--state", help="Optional exact state name for a download")
    parser.add_argument("--query-url", help="Exact existing NORS query URL when analyzing --input")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if bool(args.input) == bool(args.download_to):
        parser.error("supply exactly one of --input or --download-to")
    provenance: dict[str, str] = {}
    if args.download_to:
        query_url = build_drinking_water_query(args.start_year, args.end_year, args.state)
        provenance = download_records(query_url, args.download_to)
        input_path = args.download_to
    else:
        input_path = args.input
        if args.query_url:
            provenance["query_url"] = args.query_url
    report = analyze_records(input_path, provenance)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
