# Public-data analysis track

The Water Investigation Agent can analyze official public water data without a utility partnership. This track is for public compliance and monitoring context, not for operational recommendation validation.

## SDWIS compliance export

EPA's Safe Drinking Water Information System (SDWIS) includes public-water-system characteristics, drinking-water violations, and enforcement information. EPA publishes a national SDWA dataset and documents its tables and fields at [SDWA Data Download Summary](https://echo.epa.gov/tools/data-downloads/sdwa-download-summary). The dataset is refreshed quarterly according to EPA.

Download the official SDWIS data through EPA, retain the source date and file checksum locally, then run:

```bash
.venv/bin/python -m water_investigation.public_data \
  --input path/to/SDWA_VIOLATIONS.csv \
  --pwsid-prefix 06 \
  --source-sha256 <downloaded-file-sha256> \
  --source-retrieved-at 2026-09-13T13:45:00Z \
  --output artifacts/sdwis-public-report.json
```

The adapter accepts the violations CSV directly or a ZIP containing either `SDWA_VIOLATIONS.csv` or the current `SDWA_VIOLATIONS_ENFORCEMENT.csv`. For official archives it joins the EPA `SDWA_REF_CODE_VALUES.csv` reference table, so the report includes the documented meaning of each common violation code. It streams the input and reports record count, public-water-system count, covered date range, and common violations for the selected PWSID prefix. The tracked example is a schema fixture, not official data.

## Interpretation boundary

SDWIS compliance records are not high-frequency SCADA telemetry, incident tickets, laboratory turnaround records, or operator actions. They can support real-world context and reproducible public-data statistics, but they cannot establish that the agent improves investigation decisions. That claim requires resolved historical investigations from a partner or another dataset that contains the necessary operational outcomes.

Water Quality Portal data is a complementary public source for monitoring results; EPA describes it as a cooperative EPA/USGS/National Water Quality Monitoring Council service with results from many public providers. [EPA Water Quality Data](https://www.epa.gov/waterdata/water-quality-data-download)

## Water Quality Portal monitoring results

The read-only WQP adapter builds one explicit, bounded query and writes its CSV only to a local ignored path. It records the exact query URL, retrieval timestamp, and SHA-256 in the compact report. WQP's result-search documentation defines state and county filters using FIPS codes, and its date filters use `MM-DD-YYYY`; the adapter accepts ISO dates and performs that conversion. [WQP web-service documentation](https://www.waterqualitydata.us/webservices_documentation/)

```bash
.venv/bin/python -m water_investigation.wqp_data \
  --download-to .cache/wqp/wisconsin-017-nitrate.csv \
  --state-fips 55 --county-fips 017 --characteristic Nitrate \
  --output artifacts/wqp-public-report.json
```

Every download must include either `--county-fips` or both `--start-date` and `--end-date`; `--provider` can be repeated to limit it to named WQP providers. The report counts results and monitoring locations, records date coverage, and reports numeric minimum/median/maximum only within the same reported unit. Nondetect or nonnumeric result strings are counted in coverage but excluded from numeric summaries.

As with SDWIS, WQP data does not include the contemporaneous telemetry, incident resolution, action trace, or local calibration needed to measure investigation quality. It must not be used as evidence that a recommendation is operationally correct.

## CDC NORS drinking-water outbreak outcomes

CDC's National Outbreak Reporting System (NORS) publishes public-health outbreak records, including reported illnesses, hospitalizations, deaths, etiology, and water type. The adapter requires an explicit inclusive year range and selects the exact NORS values `primary_mode = Water` and `water_exposure = Drinking water` server-side. [CDC NORS data documentation](https://www.cdc.gov/nors/data/index.html)

```bash
.venv/bin/python -m water_investigation.nors_data \
  --download-to .cache/nors/drinking-water.csv \
  --start-year 1971 --end-year 2023 \
  --output artifacts/nors-drinking-water-public-report.json
```

The raw extract remains ignored under `.cache/`; the tracked report records its query, timestamp, checksum, record count, outcome-field missingness, and aggregate strata. Reported outcome totals are record-level values, not estimates of unique incidents or a utility's impact. NORS is voluntarily reported surveillance and has no public-water-system identifier, operational telemetry, detection timestamp, or intervention trace. It cannot be joined to SDWIS or WQP at utility level and cannot validate the agent. The source assessment is [cdc-nors-waterborne-outcomes.md](research/cdc-nors-waterborne-outcomes.md).
