# Phase 3 — Graph Schema Design: Requirements

## Scope

Design and document the complete Neo4j graph schema before any data is loaded (Phase 4). Output is a canonical `schema.md` and the corresponding Cypher DDL (`constraints_and_indexes.cypher`). No data is loaded in this phase.

### Node types in scope (all defined upfront)

| Node label | Primary source dataset | Identity key |
|---|---|---|
| `Building` | BBL join key across all three datasets | `bbl` (10-digit string: boro + block + lot) |
| `Complaint` | 311 Service Requests (`erm2-nwe9`, HPD filter) | `unique_key` |
| `Violation` | HPD Violations (`wvxf-dwi5`) | `violationid` |
| `Landlord` | HPD Registrations (`tesw-yqqr`) | `registrationid` |
| `Agency` | Derived from Complaint records | `agency_code` (e.g., `"HPD"`) |
| `Inspection` | Derived from Violation records | composite: `violationid` + `inspectiondate` |
| `Neighborhood` | NTA codes on Building/Complaint records | `ntacode` |

### Relationship types in scope

| Relationship | Direction | Cardinality |
|---|---|---|
| `FILED_AGAINST` | `(Complaint)->(Building)` | Many-to-one |
| `HAS_VIOLATION` | `(Building)->(Violation)` | One-to-many |
| `OWNED_BY` | `(Building)->(Landlord)` | Many-to-one (per registration) |
| `LOCATED_IN` | `(Building)->(Neighborhood)` | Many-to-one |
| `HANDLED_BY` | `(Complaint)->(Agency)` | Many-to-one |
| `INSPECTED_BY` | `(Violation)->(Inspection)` | One-to-one |

## Key decisions

**All node types defined upfront.** Enrichment nodes (Agency, Inspection, Neighborhood) are first-class nodes with defined properties and identity keys — not stubs. Phase 4 loading targets this complete schema.

**Landlord identity = `registrationid`.** One `Landlord` node per HPD registration record, keyed by `registrationid`. Name-based deduplication (fuzzy or exact) is deferred to a future enrichment phase. This is lossless and keeps loading logic simple.

**Relationships carry no properties.** All temporal data (dates, statuses) lives on the nodes they naturally belong to. This simplifies querying and indexing and avoids the complexity of relationship-property indexes in Neo4j.

## Context

Phase 3 is documentation and DDL only. The deliverables feed directly into Phase 4 (graph loading), which will use MERGE statements keyed on the identity fields defined here. The schema must be stable before any loading begins.

DOB Violations (`3h2n-5cm9`) are out of scope for this phase; they are ingested in Phase 5 and may extend the schema at that point.
