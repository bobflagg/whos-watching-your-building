# Phase 2 — Core Data Ingestion: Requirements

## Scope

Normalize the three core datasets, derive BBL for registrations, and load nodes and relationships directly into Neo4j Desktop. This feature branch collapses roadmap Phases 2, 3, and 4 into a single deliverable: from raw SODA pulls to a queryable graph.

---

## Datasets

| Dataset | SODA ID | Fetch strategy | BBL source |
|---|---|---|---|
| 311 HPD Complaints | `erm2-nwe9` | Paginated lookback (`LOOKBACK_MONTHS`, `created_date`) | `bbl` field (direct, normalize format) |
| HPD Violations | `wvxf-dwi5` | Windowed lookback (`LOOKBACK_MONTHS`, `inspectiondate`) | `bbl` field (direct, normalize format) |
| HPD Registrations | `tesw-yqqr` | Full pull (no date filter) | Derived: `boroid + block.zfill(5) + lot.zfill(4)` |

---

## Decisions

### BBL as the universal join key
BBL (Borough-Block-Lot) is the primary key for all cross-dataset joins. 311 complaints and violations carry a `bbl` field with ~99.7–99.9% non-null rates. Registrations carry no `bbl` field but have `boroid`, `block`, and `lot` as separate columns; BBL is constructed as a 10-character string: `boroid` (1 digit) + `block` (5 digits, zero-padded) + `lot` (4 digits, zero-padded).

### Direct to Neo4j — no intermediate staging layer
Raw Parquet files from Phase 1 exist in `data/raw/` and can be re-used or re-fetched. Normalized data goes directly into Neo4j; no additional Parquet/SQLite staging layer is introduced.

### 311 complaints must be paginated
Phase 1 discovered that 311 complaints hit the SODA 500k row cap within the 6-month window. The SODA client must be extended to paginate via `$offset` so no records are silently dropped.

### Registrations are always a full pull
Registrations represent current ownership state, not a time-series. They are always fetched in full and refreshed on each run. `LOOKBACK_MONTHS` does not apply.

### Graph schema (minimal, for Phase 2)
Only the nodes and relationships needed to join the three core datasets are loaded:

- `(Building {bbl})` — one node per unique BBL
- `(Complaint {complaint_id, ...}) -[:FILED_AGAINST]-> (Building)`
- `(Violation {violation_id, ...}) -[:FILED_AGAINST]-> (Building)`
- `(Registration {registration_id, ...}) -[:REGISTERED_TO]-> (Building)`

Owner/landlord nodes, neighborhood nodes, and agency nodes are deferred to enrichment phases.

### Code location
New modules live under `src/`:
- `src/ingest/normalize.py` — BBL normalization and derivation
- `src/graph/loader.py` — Neo4j connection and MERGE-based node/relationship loading
- `notebooks/phase2_validation.py` — marimo validation notebook

The existing `src/ingest/soda_client.py` is extended (not replaced) to add pagination.

---

## Out of scope

- DOB violations (Phase 5)
- Embeddings, vector index (Phase 6–7)
- Owner/landlord nodes, neighborhood nodes (Phase 3 refinement or later)
- Any UI or API layer
