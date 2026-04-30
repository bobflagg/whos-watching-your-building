# Phase 5 — DOB Safety Violations: Requirements

## Scope

Ingest DOB Safety Violations (`855j-jady`) from NYC Open Data, integrate them into the existing Neo4j graph as a distinct `DOBViolation` node type, and validate the result with a marimo notebook.

---

## What is in scope

- Verify and finalize the `load_dob_safety_violations()` function in `src/graph/loader.py` (stub already exists)
- Verify and finalize the DOB fetch + load steps in `src/pipeline.py` (already wired)
- Confirm `DOBViolation` uniqueness constraint in `ensure_constraints()` (already present)
- Write `notebooks/phase5_validation.py` covering node counts, relationship counts, BBL match rate, and sample traversal
- Run `src/pipeline.py` end-to-end and confirm DOB nodes land in Neo4j
- Update `specs/roadmap.md` to mark Phase 5 complete

## What is out of scope

- ACRIS ownership ingestion (Phase 6)
- Embeddings or vector index (Phase 7–8)
- Any UI or agent work

---

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Node label | `DOBViolation` (separate from `Violation`) | HPD and DOB violations have different schemas, agency semantics, and lifecycle stages; mixing them would blur accountability attribution |
| Relationship type | `(Building)-[:HAS_DOB_VIOLATION]->(DOBViolation)` | Mirrors the HPD pattern `HAS_VIOLATION` and keeps traversals symmetric |
| Primary key | `violation_number` | Stable, dataset-assigned identifier; present on all records |
| Data window | Full pull (`fetch_all_paginated`, no date filter) | DOB NOW violations cover structural/safety equipment (boilers, elevators, facades) where historical completeness matters more than a rolling window; the dataset is append-only so a full pull is safe to re-run |

> **Note on data window:** When scoping this phase the default expectation was to use `LOOKBACK_MONTHS` (consistent with HPD data). The existing pipeline implementation instead does a full pull. This is documented here as a deliberate decision; revisit in Phase 6 if dataset size becomes a concern.

---

## Dataset fields mapped to graph properties

| SODA field | DOBViolation property | Notes |
|---|---|---|
| `violation_number` | `violation_number` | Primary key |
| `violation_type` | `violation_type` | |
| `violation_status` | `violation_status` | e.g. `ACTIVE`, `RESOLVED` |
| `violation_issue_date` | `violation_issue_date` | |
| `violation_remarks` | `violation_remarks` | Free-text description |
| `device_type` | `device_type` | e.g. `BOILER`, `ELEVATOR`, `FACADE` |
| `bin` | `bin` | Building Identification Number |
| `bbl` | `bbl` | Join key to Building node |

---

## Context

Phases 0–4 loaded HPD Complaints, HPD Violations, Registrations, and their relationships into Neo4j. DOB Safety Violations add a second enforcement lens — agency-issued safety equipment violations — that can be co-traversed with HPD data to reveal buildings with overlapping accountability failures. The loader and pipeline stubs were written during Phase 4 development but not validated or merged as part of that phase.
