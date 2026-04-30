# Phase 4 — Graph Loading: Requirements

## Scope

Load the full knowledge graph into Neo4j by correcting the loader bugs identified in Phase 3, running the end-to-end pipeline against live SODA data, and validating the result with a marimo notebook.

---

## What is in scope

- Fix all known bugs in `src/graph/loader.py` before running any load
- Apply uniqueness constraints and indexes (idempotent DDL from Phase 3)
- Run the full pipeline (`src/pipeline.py`) — fetch live from SODA, normalize BBL, load all node and relationship types
- Write a marimo validation notebook that connects to Neo4j and verifies the loaded graph

## What is out of scope

- DOB violations (Phase 5)
- Embeddings or vector index (Phase 6–7)
- Any UI or agent work

---

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Bug fixes | Fix before loading | Phase 3 schema is the canonical reference; loading wrong relationships would require a destructive wipe-and-reload |
| Data source | Live SODA via `pipeline.py` | Validates the full pipeline end-to-end; parquet snapshots are Phase 1 artifacts |
| Validation artifact | Marimo notebook | Consistent with `notebooks/phase2_validation.py` established in Phase 2 |

---

## Known bugs to fix (from Phase 3 schema spec)

1. **Registration label** — currently `Registration`, must be `Registration`
2. **Registration relationship** — currently `REGISTERED_TO`, must be `OWNED_BY`; direction: `(Registration)-[:OWNED_BY]->(Building)`
3. **Violation relationship direction** — currently `(Violation)-[:FILED_AGAINST]->(Building)`, must be `(Building)-[:HAS_VIOLATION]->(Violation)`
4. **Violation field name** — loader references `row.violationtype` (doesn't exist in SODA); correct field is `row.novtype`
5. **Violation node junk fields** — loader sets `lifecyclestage`, `lastmodifieddate`, `ownerfirstname`, `ownerlastname`, `ownertype` which do not exist in the HPD violations dataset; remove them

---

## Context

Phase 3 produced a canonical schema (`specs/2026-04-27-graph-schema-design/schema.md`) and DDL (`constraints_and_indexes.cypher`), but the `loader.py` written in Phase 2 was not updated to match it. Phase 4 reconciles the two so the graph in Neo4j matches the documented schema.
