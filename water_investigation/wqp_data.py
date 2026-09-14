"""Read-only download and analysis of public Water Quality Portal results."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import ssl
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen

import certifi

WQP_RESULT_ENDPOINT = "https://www.waterqualitydata.us/data/Result/search"
REQUIRED_COLUMNS = frozenset({"MonitoringLocationIdentifier", "ActivityStartDate", "CharacteristicName", "ResultMeasureValue", "ResultMeasure/MeasureUnitCode"})


def build_result_query(state_fips: str, characteristic: str, start_date: date | None = None,
                       end_date: date | None = None, county_fips: str | None = None,
                       providers: tuple[str, ...] = ()) -> str:
    """Build a bounded, reproducible WQP result-download query."""
    if len(state_fips) != 2 or not state_fips.isdigit():
        raise ValueError("state_fips must be a two-digit FIPS code")
    if county_fips and (len(county_fips) != 3 or not county_fips.isdigit()):
        raise ValueError("county_fips must be a three-digit FIPS code")
    if (start_date is None) != (end_date is None):
        raise ValueError("start_date and end_date must be supplied together")
    if start_date and start_date > end_date:
        raise ValueError("start_date must not be after end_date")
    if not county_fips and not start_date:
        raise ValueError("a bounded query requires county_fips or a start_date/end_date window")
    parameters: list[tuple[str, str]] = [
        ("statecode", f"US:{state_fips}"),
        ("characteristicName", characteristic),
        ("sampleMedia", "Water"),
        ("mimeType", "csv"),
        ("zip", "no"),
    ]
    if county_fips:
        parameters.append(("countycode", f"US:{state_fips}:{county_fips}"))
    if start_date:
        parameters.extend((("startDateLo", start_date.strftime("%m-%d-%Y")),
                           ("startDateHi", end_date.strftime("%m-%d-%Y"))))
    parameters.extend(("providers", provider) for provider in providers)
    return f"{WQP_RESULT_ENDPOINT}?{urlencode(parameters)}"


def download_results(query_url: str, destination: Path) -> dict[str, str]:
    """Download one WQP CSV and return provenance without interpreting its contents."""
    parsed = urlparse(query_url)
    if parsed.scheme != "https" or parsed.netloc != "www.waterqualitydata.us" or parsed.path != "/data/Result/search":
        raise ValueError("query_url must be an HTTPS Water Quality Portal result-search URL")
    trusted_context = ssl.create_default_context(cafile=certifi.where())
    with urlopen(query_url, timeout=120, context=trusted_context) as response:
        content = response.read()
    if not content.startswith(b"OrganizationIdentifier,"):
        raise ValueError("Water Quality Portal response was not a results CSV")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return {"query_url": query_url, "sha256": hashlib.sha256(content).hexdigest(),
            "retrieved_at": datetime.now().astimezone().isoformat()}


def _number(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def analyze_results(path: Path, provenance: dict[str, str] | None = None) -> dict[str, object]:
    """Summarize coverage and unit-separated numeric measurements from a WQP CSV."""
    locations: set[str] = set()
    characteristics, providers = Counter(), Counter()
    values_by_unit: defaultdict[str, list[float]] = defaultdict(list)
    result_count = 0
    first_date, last_date = None, None
    with path.open(newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        if not reader.fieldnames or not REQUIRED_COLUMNS <= set(reader.fieldnames):
            raise ValueError("WQP input is missing required result, location, date, or unit columns")
        for row in reader:
            result_count += 1
            locations.add(row["MonitoringLocationIdentifier"])
            characteristics[row["CharacteristicName"]] += 1
            providers[row.get("ProviderName", "")] += 1
            observed_date = datetime.strptime(row["ActivityStartDate"], "%Y-%m-%d").date()
            first_date = min(first_date, observed_date) if first_date else observed_date
            last_date = max(last_date, observed_date) if last_date else observed_date
            if (value := _number(row["ResultMeasureValue"])) is not None:
                values_by_unit[row["ResultMeasure/MeasureUnitCode"]].append(value)
    numeric_by_unit = [{"unit": unit, "count": len(values), "minimum": min(values),
                        "median": statistics.median(values), "maximum": max(values)}
                       for unit, values in sorted(values_by_unit.items())]
    return {"source": "Water Quality Portal public monitoring results", "source_url": WQP_RESULT_ENDPOINT,
            "provenance": provenance or {}, "scope": {"input": str(path)},
            "result_records": result_count, "monitoring_locations": len(locations),
            "date_range": [first_date.isoformat(), last_date.isoformat()] if first_date else None,
            "characteristics": [{"name": name, "count": count} for name, count in characteristics.most_common()],
            "providers": [{"name": name, "count": count} for name, count in providers.most_common() if name],
            "numeric_results_by_unit": numeric_by_unit,
            "interpretation_limit": "Public monitoring results provide historical context, not operational telemetry, incident resolution, or recommendation validation."}


def main() -> None:
    parser = argparse.ArgumentParser(description="Download or analyze public Water Quality Portal result data.")
    parser.add_argument("--input", type=Path, help="Previously downloaded WQP results CSV")
    parser.add_argument("--download-to", type=Path, help="Ignored local path for a new WQP CSV download")
    parser.add_argument("--state-fips", help="Two-digit state FIPS code for a download")
    parser.add_argument("--county-fips", help="Optional three-digit county FIPS code for a download")
    parser.add_argument("--characteristic", help="Exact WQP characteristic name for a download")
    parser.add_argument("--start-date", type=date.fromisoformat, help="Inclusive YYYY-MM-DD download start")
    parser.add_argument("--end-date", type=date.fromisoformat, help="Inclusive YYYY-MM-DD download end")
    parser.add_argument("--provider", action="append", default=[], help="Optional WQP provider; repeatable")
    parser.add_argument("--query-url", help="Exact existing WQP query URL when analyzing --input")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if bool(args.input) == bool(args.download_to):
        parser.error("supply exactly one of --input or --download-to")
    provenance: dict[str, str] = {}
    if args.download_to:
        if not args.state_fips or not args.characteristic:
            parser.error("--download-to requires --state-fips and --characteristic")
        query_url = build_result_query(args.state_fips, args.characteristic, args.start_date, args.end_date,
                                       args.county_fips, tuple(args.provider))
        provenance = download_results(query_url, args.download_to)
        input_path = args.download_to
    else:
        input_path = args.input
        if args.query_url:
            provenance["query_url"] = args.query_url
    report = analyze_results(input_path, provenance)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
