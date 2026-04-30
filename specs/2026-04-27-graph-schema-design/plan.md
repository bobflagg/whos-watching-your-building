# Phase 3 — Graph Schema Design: Plan

## Task Group 1 — Field inventory

1.1 For each source dataset, list all available fields from the Phase 2 ingestion output.
1.2 Map each field to a target node and property name (snake_case), flagging fields that are dropped.
1.3 Identify the identity key field(s) for each node type (used in MERGE statements).

## Task Group 2 — Node schema definitions

2.1 Write the node property table for each of the 7 node types:
    - `Building`, `Complaint`, `Violation`, `Registration`, `Agency`, `Inspection`, `Neighborhood`
    - Columns: property name, Neo4j type, source field, nullable, notes
2.2 Confirm `bbl` construction logic (boro + block + lot zero-padded to 10 chars) matches Phase 2 join logic.
2.3 Define the `Inspection` composite identity (since it has no natural surrogate key in the source data).

## Task Group 3 — Relationship schema definitions

3.1 For each of the 6 relationship types, document:
    - Start node label, end node label, relationship type name
    - Cardinality (one-to-one, one-to-many, many-to-one, many-to-many)
    - Which identity keys on each side are used to resolve the MERGE
3.2 Flag any relationships where the foreign key may be missing/null in source data (e.g., BBL nulls).

## Task Group 4 — Constraints and indexes

4.1 Write `CREATE CONSTRAINT` statements for the identity key on each node type (uniqueness constraints).
4.2 Write `CREATE INDEX` statements for high-cardinality properties that will be queried often
    (e.g., `Building.address`, `Complaint.status`, `Violation.novdescription`).
4.3 Save all DDL to `constraints_and_indexes.cypher`.
4.4 Run the DDL against local Neo4j Desktop and confirm it executes cleanly.

## Task Group 5 — Schema reference document

5.1 Write `schema.md` in this directory as the canonical human-readable schema reference.
    - One section per node type (properties table + identity key callout)
    - One section for relationships (full table + cardinality notes)
    - One section for constraints and indexes
5.2 Cross-check `schema.md` against `constraints_and_indexes.cypher` for consistency.

## Task Group 6 — Review and sign-off

6.1 Walk through each node type and relationship against the Phase 2 data to confirm every identity key actually exists and is populated in the ingested data.
6.2 Confirm the schema covers the query patterns needed for Phase 9 (query router) and Phase 10 (Cypher generator).
6.3 Mark Phase 3 complete in `specs/roadmap.md`.
