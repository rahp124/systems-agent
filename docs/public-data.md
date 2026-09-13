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

The adapter accepts the violations CSV directly or a ZIP containing either `SDWA_VIOLATIONS.csv` or the current `SDWA_VIOLATIONS_ENFORCEMENT.csv`. It streams the input, reports record count, public-water-system count, covered date range, and the most common violation codes for the selected PWSID prefix. The tracked example is a schema fixture, not official data.

## Interpretation boundary

SDWIS compliance records are not high-frequency SCADA telemetry, incident tickets, laboratory turnaround records, or operator actions. They can support real-world context and reproducible public-data statistics, but they cannot establish that the agent improves investigation decisions. That claim requires resolved historical investigations from a partner or another dataset that contains the necessary operational outcomes.

Water Quality Portal data is a complementary public source for monitoring results; EPA describes it as a cooperative EPA/USGS/National Water Quality Monitoring Council service with results from many public providers. [EPA Water Quality Data](https://www.epa.gov/waterdata/water-quality-data-download)
