# Phase 2 — Core Data Ingestion: Plan

## Task Group 1 — Extend SODA client with pagination

Fix the 500k row cap on 311 complaints by adding offset-based pagination to `src/ingest/soda_client.py`.

- Add `fetch_recent_paginated(dataset_id, date_field, page_size=50_000, **filters)` that loops with `$offset` until a page returns fewer rows than `page_size`
- Existing `fetch_recent` and `fetch_all` are unchanged
- Update the 311 fetch call in the ingestion pipeline to use the paginated variant

---

## Task Group 2 — BBL normalization module

Create `src/ingest/normalize.py` with functions to produce a consistent 10-character BBL string across all three datasets.

- `normalize_bbl(series: pd.Series) -> pd.Series` — strips whitespace, zero-pads to 10 chars, drops rows where BBL is null or malformed after normalization
- `derive_bbl(df: pd.DataFrame) -> pd.Series` — for registrations only: constructs BBL from `boroid`, `block`, `lot` columns using `boroid.str.zfill(1) + block.str.zfill(5) + lot.str.zfill(4)`
- Both functions return a clean `bbl` Series; callers assign it as `df['bbl']`

---

## Task Group 3 — Graph schema and Neo4j loader

Create `src/graph/loader.py` implementing MERGE-based upserts for all node and relationship types.

- `get_driver()` — returns a Neo4j driver from `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` env vars
- `ensure_constraints(driver)` — creates uniqueness constraints on `Building.bbl`, `Complaint.complaint_id`, `Violation.violation_id`, `Registration.registration_id` (idempotent)
- `load_buildings(driver, bbls: list[str])` — MERGE one `Building` node per unique BBL across all three datasets
- `load_complaints(driver, df: pd.DataFrame)` — MERGE `Complaint` nodes and `[:FILED_AGAINST]` relationships to `Building`
- `load_violations(driver, df: pd.DataFrame)` — MERGE `Violation` nodes and `[:FILED_AGAINST]` relationships to `Building`
- `load_registrations(driver, df: pd.DataFrame)` — MERGE `Registration` nodes and `[:REGISTERED_TO]` relationships to `Building`
- All loaders use batched writes (batch size 1000) via `UNWIND`

---

## Task Group 4 — Ingestion pipeline script

Wire together fetch → normalize → load in a single runnable script.

- Create `src/pipeline.py` (or extend `main.py`) with a `run()` function that:
  1. Fetches 311 complaints (paginated), violations (windowed), registrations (full pull)
  2. Normalizes BBL for all three
  3. Calls `ensure_constraints`, then all four loaders
  4. Prints a brief summary: rows fetched, BBL nulls dropped, nodes/relationships written
- Runnable via `uv run python -m src.pipeline`

---

## Task Group 5 — Validation notebook

Create `notebooks/phase2_validation.py` as a marimo notebook that confirms the ingestion succeeded and quantifies join coverage.

- Row counts at each stage: raw SODA → after BBL normalization → loaded into Neo4j
- BBL null/drop rates per dataset
- Join coverage: how many distinct BBLs appear in all three datasets vs. only one or two
- Neo4j node counts by label and relationship counts by type (via Cypher)
- Flag any BBLs in complaints or violations that have no matching registration
