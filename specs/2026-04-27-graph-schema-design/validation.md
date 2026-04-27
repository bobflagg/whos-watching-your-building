# Phase 3 — Graph Schema Design: Validation

Phase 3 is complete and ready to merge when all of the following are true.

## Deliverables exist

- [ ] `specs/2026-04-27-graph-schema-design/schema.md` exists and is the canonical schema reference
- [ ] `specs/2026-04-27-graph-schema-design/constraints_and_indexes.cypher` exists

## Schema completeness

- [ ] All 7 node types are defined with a properties table and a named identity key:
  `Building`, `Complaint`, `Violation`, `Landlord`, `Agency`, `Inspection`, `Neighborhood`
- [ ] All 6 relationship types are defined with direction, cardinality, and the identity keys used to resolve each side:
  `FILED_AGAINST`, `HAS_VIOLATION`, `OWNED_BY`, `LOCATED_IN`, `HANDLED_BY`, `INSPECTED_BY`
- [ ] Every property name uses snake_case
- [ ] No relationship type carries properties (all temporal/status data is on nodes)
- [ ] `Landlord` identity key is `registrationid`
- [ ] `Building` identity key is `bbl` (10-digit string, boro + block + lot)

## DDL correctness

- [ ] `constraints_and_indexes.cypher` contains one `CREATE CONSTRAINT` per node type
- [ ] The DDL runs without errors on local Neo4j Desktop (no conflicts, no syntax errors)
- [ ] Running the DDL twice is idempotent (uses `IF NOT EXISTS`)

## Data coverage check

- [ ] The identity key for each node type is confirmed non-null in the Phase 2 ingested data (or null-handling strategy is documented)
- [ ] BBL join logic in the schema matches the BBL construction logic used in Phase 2 ingestion

## Roadmap updated

- [ ] `specs/roadmap.md` marks Phase 3 as ✓ complete
