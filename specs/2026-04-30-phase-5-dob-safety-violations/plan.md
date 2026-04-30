# Phase 5 — DOB Safety Violations: Plan

> **Status note:** `src/graph/loader.py` and `src/pipeline.py` already contain DOB violation stubs written during Phase 4. This plan verifies, finalizes, and validates that work rather than writing it from scratch.

---

## Task Group 1 — Verify existing implementation

Files: `src/graph/loader.py`, `src/pipeline.py`

1.1 Confirm `ensure_constraints()` includes `DOBViolation` / `violation_number` — already present, no change needed  
1.2 Confirm `load_dob_safety_violations()` field mapping matches the live SODA schema from `notebooks/explore_dob_safety_violations.py`  
1.3 Confirm `pipeline.py` includes DOB BBLs in `all_bbls` so Building nodes are created before the relationship step — already present  
1.4 Fix any field name mismatches found in 1.2 (e.g. if a SODA column name differs from what the loader expects)

---

## Task Group 2 — Run the pipeline

2.1 Run `uv run python -m src.pipeline` against the local Neo4j instance  
2.2 Monitor stdout for DOB fetch count, BBL drop count, node/relationship counts  
2.3 If the DOB fetch returns 0 rows, debug the `fetch_all_paginated` call against `855j-jady`  
2.4 If a constraint or field error surfaces, fix and re-run (wipe only DOBViolation nodes if a clean retry is needed: `MATCH (d:DOBViolation) DETACH DELETE d`)

---

## Task Group 3 — Write validation notebook

File to create: `notebooks/phase5_validation.py`

3.1 Connect to Neo4j using env vars  
3.2 Add cells for:
  - `DOBViolation` node count (must be > 0)
  - `HAS_DOB_VIOLATION` relationship count (must be > 0)
  - BBL match rate: % of `DOBViolation` nodes with an inbound `HAS_DOB_VIOLATION` from a Building (must be ≥ 50%)
  - Device type distribution (value counts from Neo4j)
  - Violation status distribution
  - Sample traversal: given a BBL, show HPD violations + DOB violations together
  - Cross-dataset check: count Buildings that have both `HAS_VIOLATION` (HPD) and `HAS_DOB_VIOLATION` (DOB) relationships

---

## Task Group 4 — Update docs and merge

4.1 Mark Phase 5 complete in `specs/roadmap.md`  
4.2 Confirm all validation checks in `specs/2026-04-30-phase-5-dob-safety-violations/validation.md` pass  
4.3 Commit, open PR to main, merge
