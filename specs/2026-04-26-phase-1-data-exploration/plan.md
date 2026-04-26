# Phase 1 — Data Exploration: Plan

## Group 1 — Project Structure

1. Create `data/raw/` directory (gitignored) for saved samples
2. Create `notebooks/` directory for marimo exploration notebooks
3. Add `data/` to `.gitignore`

## Group 2 — SODA Client Setup

1. Create `src/ingest/soda_client.py` — wraps `sodapy.Socrata`, reads `NYC_OPEN_DATA_APP_TOKEN` and `LOOKBACK_MONTHS` from env, exposes a `fetch_recent(dataset_id, date_field, **filters)` helper that applies the lookback window and returns a DataFrame

## Group 3 — Pull and Persist Each Dataset

1. Identify the correct date filter field for each dataset:
   - 311 Service Requests (`erm2-nwe9`): `created_date`, filter `agency='HPD'`
   - HPD Violations (`wvxf-dwi5`): confirm date field during exploration
   - HPD Registrations (`tesw-yqqr`): confirm date field during exploration
2. Pull each dataset via `fetch_recent()` and save to `data/raw/` as Parquet:
   - `data/raw/311_hpd_complaints.parquet`
   - `data/raw/hpd_violations.parquet`
   - `data/raw/hpd_registrations.parquet`

## Group 4 — Schema Exploration (one marimo notebook per dataset)

1. `notebooks/explore_311_complaints.py` — field names, dtypes, null rates, sample values, record count
2. `notebooks/explore_violations.py` — same
3. `notebooks/explore_registrations.py` — same
4. For each notebook, document BBL field name and non-null coverage rate

## Group 5 — Findings Summary

1. Add a `specs/2026-04-26-phase-1-data-exploration/findings.md` summarizing:
   - Field names and types for each dataset
   - BBL field name and coverage rate per dataset
   - Any data quality issues or surprises relevant to Phase 2 join logic
