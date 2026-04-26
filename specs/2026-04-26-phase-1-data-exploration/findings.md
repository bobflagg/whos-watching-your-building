# Phase 1 — Data Exploration: Findings

Pulled last 6 months (`LOOKBACK_MONTHS=6`, cutoff ~2025-10-28).

---

## Dataset Summaries

| Dataset | File | Rows | Cols | Date field used |
|---|---|---|---|---|
| 311 HPD Complaints | `311_hpd_complaints.parquet` | 500,000 | 35 | `created_date` |
| HPD Violations | `hpd_violations.parquet` | 453,355 | 41 | `inspectiondate` |
| HPD Registrations | `hpd_registrations.parquet` | 30,404 | 16 | `lastregistrationdate` |

---

## BBL Coverage

| Dataset | BBL field | Non-null rate | Notes |
|---|---|---|---|
| 311 HPD Complaints | `bbl` | 99.7% | Excellent — safe to use as join key |
| HPD Violations | `bbl` | 99.9% | Excellent — safe to use as join key |
| HPD Registrations | none | — | Has `boroid`, `block`, `lot` — must construct BBL in Phase 2 |

**BBL construction for registrations:**
`bbl = boroid.zfill(1) + block.zfill(5) + lot.zfill(4)` (10-character string).
Phase 2 should add this as a derived column before joining.

---

## Data Quality Notes

### 311 HPD Complaints
- **Row cap hit:** 500,000 rows returned — this is the SODA `limit` ceiling. The full 6-month window likely contains more records. Phase 2 should paginate using `$offset` or narrow the window to get complete data.
- High-null columns: `cross_street_1`, `cross_street_2`, `intersection_street_1`, `intersection_street_2`, `landmark` — these are optional address fields, expected to be sparse. Not relevant to join logic.

### HPD Violations
- High-null columns: `certifieddate`, `newcertifybydate`, `newcorrectbydate` — these are only populated for violations that have been certified or had deadlines extended. Nulls are meaningful, not missing data.
- `inspectiondate` confirmed as the right filter field.

### HPD Registrations
- No high-null columns — clean dataset.
- **No direct `bbl` column** — requires construction from components (see above).
- 30,404 rows for 6 months reflects this is a slow-moving dataset (property registrations don't change frequently). Phase 2 may want to pull a longer window or consider pulling the full dataset for registrations.

---

## Phase 2 Recommendations

1. **Paginate 311 complaints** — use `$offset` to retrieve all records within the lookback window, not just the first 500k.
2. **Construct BBL on registrations** — derive a `bbl` column from `boroid` + `block` + `lot` before joining.
3. **Consider full pull for registrations** — 30k rows for 6 months is small; a full pull may be more useful since registrations represent current ownership state, not a time-series of events.
4. **Lookback window for violations** — 453k rows in 6 months is substantial; verify the window is right for the use case before widening it.
