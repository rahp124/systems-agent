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
- The most frequent reported violation codes were `03` (1,280 records), `23` (857), and `45` (461).

These are public compliance-record statistics. The report intentionally retains the EPA codes rather than assigning meanings without applying the corresponding official reference-table mapping. They are not estimates of real-time water conditions, incident frequency, utility performance, or agent decision quality.

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
