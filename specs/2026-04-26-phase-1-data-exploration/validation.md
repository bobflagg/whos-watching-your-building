# Phase 1 — Data Exploration: Validation

## Done when:

### Data pull
- [ ] `data/raw/311_hpd_complaints.parquet`, `data/raw/hpd_violations.parquet`, and `data/raw/hpd_registrations.parquet` all exist and are non-empty
- [ ] Each file contains only records within the `LOOKBACK_MONTHS` window (spot-check the min/max date in the relevant date field)
- [ ] `data/` is in `.gitignore` and none of the Parquet files appear in `git status`

### Notebooks
- [ ] Three marimo notebooks exist in `notebooks/` and run top-to-bottom without errors
- [ ] Each notebook reports: record count, column names and dtypes, null rate per column, and at least 5 sample rows

### BBL coverage
- [ ] Each notebook identifies the BBL field name (or notes its absence) and reports its non-null rate

### Findings
- [ ] `specs/2026-04-26-phase-1-data-exploration/findings.md` exists and documents schema observations and any data quality issues relevant to Phase 2
