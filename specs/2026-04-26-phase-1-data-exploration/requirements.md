# Phase 1 — Data Exploration: Requirements

## Scope

Pull a recent sample of each core dataset, persist it to disk, and explore schemas and BBL coverage in marimo notebooks — producing enough understanding to design the ingestion and join logic in Phase 2.

**In scope:**
- Fetching the last `LOOKBACK_MONTHS` months from each of the three core datasets via SODA
- Saving each sample as Parquet to `data/raw/` for Phase 2 to reuse
- Marimo notebooks documenting field names, dtypes, null rates, and BBL coverage per dataset
- A written findings summary capturing data quality observations and join readiness

**Out of scope:**
- Cross-dataset joins (deferred to Phase 2)
- Data normalization or transformation
- Loading anything into Neo4j
- Full historical pulls (Phase 2 will decide the final ingestion window)

## Decisions

**Marimo notebooks for exploration.**
One notebook per dataset. Notebooks are stored in `notebooks/` and committed. They serve as living documentation of what the data looks like.

**Parquet for raw storage.**
`data/raw/` is gitignored. Parquet preserves dtypes better than CSV and loads faster for Phase 2. File names are fixed (not date-stamped) so Phase 2 can reference them by a known path.

**BBL coverage is basic only.**
Phase 1 checks whether the BBL field exists and reports its non-null rate per dataset. Cross-dataset join coverage analysis is Phase 2's job.

**`LOOKBACK_MONTHS` controls the sample window.**
Read from the environment, defaulting to 6. All three datasets use the same window for consistency. The correct date field for each dataset is confirmed during exploration (Group 3).

## Context

The original roadmap used the HPD Complaints dataset (`uwyv-629c`), which is not publicly accessible. It has been replaced by 311 Service Requests (`erm2-nwe9`) filtered to `agency='HPD'`, which covers the same housing complaint traffic. This dataset is already in the roadmap as a Phase 5 enrichment source — that entry has been updated to remove it since it now enters the graph in Phase 2.
