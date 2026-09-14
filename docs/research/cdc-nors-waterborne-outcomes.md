# CDC NORS waterborne-outcome data assessment

**Question.** Can a public U.S. dataset add genuine water-related incident or
outcome labels to the agent's public-data work without implying operational
validation?

**Recommendation.** Yes—use the CDC National Outbreak Reporting System (NORS)
download as a *public-health outcome context* adapter. Its `primary_mode =
"Water"` records contain reported outbreak outcomes, and the exact
`water_exposure = "Drinking water"` subset is the appropriate starting scope.
It is suitable for reproducible, aggregate epidemiological summaries and for
testing provenance-aware public-data ingestion. It is **not** suitable for
training, scoring, or validating a utility's real-time investigation decisions.

## Why this is a genuine outcome source

CDC defines a waterborne outbreak as at least two similar illnesses
epidemiologically linked by time, water-exposure location, and illness type,
with evidence implicating water as the probable source. Environmental testing
can strengthen, but does not replace, that epidemiologic link. [CDC,
*About Waterborne Disease Surveillance*](https://www.cdc.gov/healthy-water-data/about/index.html)

The Waterborne Disease and Outbreak Surveillance System (WBDOSS) collects
outbreak-associated illness, hospitalization, and death counts, along with
agents, implicated water types, systems, and settings. Local, state, and
territorial health departments report through NORS; outbreak reports are
voluntary. [CDC, *About Waterborne Disease
Surveillance*](https://www.cdc.gov/healthy-water-data/about/index.html)
CDC describes the public NORS download as a streamlined dataset containing
pathogens, settings, and water sources. [CDC, *NORS
Data*](https://www.cdc.gov/nors/data/index.html)

Thus the labels represent public-health investigation outcomes—not simulated
events, compliance violations, or raw water-quality measurements.

## Access, provenance, and license

| Item | Assessment |
| --- | --- |
| Publisher / collection system | CDC; NORS supports reporting by U.S. local, state, and territorial health departments. [CDC NORS data page](https://www.cdc.gov/nors/data/index.html) |
| Dataset | [`NORS` (Socrata ID `5xkq-dg7x`)](https://data.cdc.gov/Foodborne-Waterborne-and-Related-Diseases/NORS/5xkq-dg7x) |
| Programmatic access | CSV: `https://data.cdc.gov/resource/5xkq-dg7x.csv`; JSON/SoQL: `https://data.cdc.gov/resource/5xkq-dg7x.json`. The official [dataset metadata endpoint](https://data.cdc.gov/api/views/5xkq-dg7x) supplies column definitions, attribution, update metadata, and the dataset license. |
| License | The dataset metadata labels it **Public Domain U.S. Government** and links to [USA.gov government-works terms](https://www.usa.gov/government-works). Keep a retrieval timestamp, URL, and SHA-256 of every downloaded extract because the dataset can change. |
| Reporting/finality | CDC says reports are voluntarily submitted; final data normally appear 12–18 months after a reporting year and reports can later be modified. [CDC NORS data page](https://www.cdc.gov/nors/data/index.html) |

No raw extract needs to be committed: download into the existing ignored cache,
record the canonical query, retrieval timestamp, response checksum, metadata
endpoint, and an aggregate JSON result in version control.

## Available fields and labels

The official metadata defines these directly useful columns:

| Field | Meaning / use |
| --- | --- |
| `year`, `month`, `state` | Earliest illness-onset year/month and exposure state; temporal and state aggregation only. |
| `primary_mode` | Transmission mode. Select the exact value `Water`; do not infer waterborne status from free text. |
| `water_exposure` | Water-exposure category. Select exact `Drinking water` for drinking-water-only aggregation; retain mixed categories separately. |
| `water_type`, `setting` | Reported system/venue/device category and exposure setting; useful descriptive strata, not a utility identifier. |
| `etiology`, `etiology_status` | Identified agent and whether it is confirmed or suspected. |
| `illnesses`, `hospitalizations`, `deaths` | Reported outbreak-impact outcomes. Preserve missingness and the accompanying `info_on_hospitalizations` / `info_on_deaths` denominators. |

The public dataset's documented row schema does **not** include a public-water-
system identifier, distribution-system asset identifier, SCADA tag, sensor
measurements, event detection time, intervention time, or a matched control
population. It therefore cannot join a NORS event to SDWIS or WQP at a specific
utility, nor establish whether an advisory prevented an outcome.

## Reproducible scoped query

Use a bounded server-side query, rather than downloading the full cross-mode
table. The following URL requests only drinking-water, water-mode records and
only the aggregation fields needed for a yearly outcome summary:

```text
https://data.cdc.gov/resource/5xkq-dg7x.csv?$select=year,state,etiology,etiology_status,water_type,setting,illnesses,hospitalizations,deaths,info_on_hospitalizations,info_on_deaths&$where=primary_mode='Water'%20AND%20water_exposure='Drinking%20water'
```

On 2026-09-13, a separate official SoQL aggregation over `primary_mode =
'Water'` returned 3,106 records for 1971–2023; 1,256 had the exact
`Drinking water` exposure value. These counts are retrieval-time context, not a
stable benchmark: the source is dynamic and mixed exposure values must not be
silently folded into the drinking-water-only cohort.

## Feasible, defensible integration

Implement a small read-only adapter that:

1. requires an explicit date range and one of `all-water`,
   `drinking-water-only`, or a documented exact exposure category;
2. constructs and records the canonical SoQL query;
3. downloads only that extract to `.cache/`, checks the expected columns, and
   writes its SHA-256 and retrieval time into a compact aggregate report; and
4. reports counts of outbreak records, illnesses, hospitalizations, deaths,
   unknown outcome fields, and strata by year, state, agent status, and water
   type.

The report must call the values **reported outbreak outcomes**. It may compare
long-run temporal or category distributions with the agent's simulated scenario
classes, but it must not call such a comparison calibration, detection
performance, precision/recall, causal impact, or operational validation.

## Limitations and non-claims

- Reporting is voluntary and outbreaks are likely underreported; reporting
  completeness can differ by transmission mode because health-department
  resources and training differ. [CDC NORS data page](https://www.cdc.gov/nors/data/index.html)
- CDC cautions that only a small proportion of illnesses are identified as
  outbreak-associated, and distributions of reported outbreak settings/sources
  need not represent sporadic illnesses. [CDC NORS data page](https://www.cdc.gov/nors/data/index.html)
- An outbreak record is generally detected and investigated after illnesses;
  it is not a prospective contamination-alert label or a timestamped utility
  operational incident.
- Exposure state and month/year are insufficient to match a particular water
  system. Ecological comparisons to SDWIS or WQP cannot establish linkage or
  causality.
- Drinking-water records may include settings and water types outside a
  municipal distribution system. Keep `water_type` and `setting` in every
  aggregation rather than treating all rows as utility failures.

**Bottom line.** NORS is the strongest readily accessible independent public
outcome source for this scope. It materially improves the agent's ability to
demonstrate careful outcome-data ingestion and descriptive public-health
analysis, while leaving real operational validation contingent on de-identified
historian replay and a read-only partner shadow-mode evaluation.
