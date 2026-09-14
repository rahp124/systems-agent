# Public SDWIS result: PWSID prefix 06

## Source and method

The Water Investigation Agent analyzed EPA's current SDWIS national download, `SDWA_latest_downloads.zip`, retrieved on 2026-09-13. EPA listed the archive as last modified on 2026-07-09. The downloaded archive SHA-256 was:

```text
a18a20f9091c2e0466c91c83d0bac5651473441642331d09504e447a6e2ac7a4
```

The analysis streamed `SDWA_VIOLATIONS_ENFORCEMENT.csv` and selected public-water-system IDs beginning with `06`. The compact, reproducible output is [sdwis-pwsid-06-public-report.json](../artifacts/sdwis-pwsid-06-public-report.json).

## Result

- 5,695 public compliance violation records.
- 132 distinct public water systems with matching records.
- Compliance-period start dates from 1991-01-01 through 2025-11-01.
- The most frequent reported violations were Monitoring, Regular (`03`, 1,280 records), Monitoring, Routine Major (TCR) (`23`, 857), and Failure To Address Deficiency (`45`, 461), using EPA's `SDWA_REF_CODE_VALUES.csv` descriptions.

These are public compliance-record statistics. They are not estimates of real-time water conditions, incident frequency, utility performance, or agent decision quality.

## Reproduction

```bash
.venv/bin/python -m water_investigation.public_data \
  --input .cache/sdwa/SDWA_latest_downloads.zip \
  --pwsid-prefix 06 \
  --source-sha256 a18a20f9091c2e0466c91c83d0bac5651473441642331d09504e447a6e2ac7a4 \
  --source-retrieved-at 2026-09-13T13:45:00Z \
  --output artifacts/sdwis-pwsid-06-public-report.json
```

EPA documents the national SDWIS download and table definitions at [SDWA Data Download Summary](https://echo.epa.gov/tools/data-downloads/sdwa-download-summary).

## Public WQP result: Wisconsin FIPS 55, county FIPS 017, nitrate

The agent downloaded a bounded Water Quality Portal result query on 2026-09-13. The query selected water samples with the exact WQP characteristic `Nitrate`, state FIPS `55`, and county FIPS `017`; it did not request a date range. The compact output is [wqp-wi-017-nitrate-public-report.json](../artifacts/wqp-wi-017-nitrate-public-report.json). Its local CSV is deliberately ignored by Git.

## Result

- 134 historical result records from 39 monitoring locations, dated 1961-02-02 through 2023-06-13.
- Providers recorded 126 results from NWIS and 8 from STORET.
- The report retains separate numeric summaries for five reported units; it does not combine or convert `mg/l as N`, `mg/l asNO3`, and other units.

The recorded query URL and downloaded-file SHA-256 are in the report. These figures describe only the returned public monitoring records. They are not a current condition assessment, a regional prevalence estimate, or a validation of investigation recommendations.

## Reproduction

```bash
.venv/bin/python -m water_investigation.wqp_data \
  --download-to .cache/wqp/wisconsin-017-nitrate.csv \
  --state-fips 55 --county-fips 017 --characteristic Nitrate \
  --output artifacts/wqp-wi-017-nitrate-public-report.json
```

Water Quality Portal documents result-download filters and formats in its [web-service documentation](https://www.waterqualitydata.us/webservices_documentation/).

## Public NORS result: drinking-water outbreak records, 1971–2023

The agent downloaded the CDC NORS records with the exact server-side filter `primary_mode = Water AND water_exposure = Drinking water`, for inclusive years 1971–2023. The compact output is [nors-drinking-water-public-report.json](../artifacts/nors-drinking-water-public-report.json); the raw CSV is ignored by Git.

## Result

- 1,256 reported drinking-water outbreak records from 1971 through 2023.
- Record-level reported outcomes total 586,820 illnesses, 1,978 hospitalizations, and 325 deaths; the report also records missingness for each field.
- The most common reported water types are Community (680 records), Other (339), and Individual/Private (112); the most common etiology is Unknown (355 records).

These are voluntary public-health surveillance records. Rows are not a matched utility incident log and have no PWSID, SCADA measurements, detection time, or intervention data. The values are not unique-incident totals, causal measures of water-system performance, or evidence of agent detection performance.

## Reproduction

```bash
.venv/bin/python -m water_investigation.nors_data \
  --download-to .cache/nors/drinking-water.csv \
  --start-year 1971 --end-year 2023 \
  --output artifacts/nors-drinking-water-public-report.json
```

CDC documents NORS reporting, finality, and its limitations at [NORS Data](https://www.cdc.gov/nors/data/index.html).
